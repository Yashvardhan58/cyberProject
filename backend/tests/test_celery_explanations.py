"""
Unit and Integration Tests for Asynchronous Celery LLM Explanations.
Runs isolated in-memory using config.settings.test without Redis running.
"""

import os
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from celery import current_app

from apps.users.models import UserProfile
from apps.alerts.models import RiskScore, Alert, SHAPValue
from apps.explanations.models import Explanation
from apps.explanations.tasks import generate_alert_explanation_task
from apps.explanations.evidence_builder import EvidenceBuilder


class CeleryExplanationTests(TestCase):
    """
    Test suite for Phase 8 Acceptance Criteria & Celery Async Pipeline:
    1. Success: row reaches COMPLETED with text.
    2. Transient failure then success: attempts > 1, final status is COMPLETED.
    3. Retries exhausted: final status is FAILED.
    4. Permanent error (auth): FAILED with exactly 1 attempt, no retry.
    5. Double POST: only one row and only one call_claude invocation.
    6. Broker Downtime: returns 503 instead of false 202 when Redis is down.
    7. Stuck-Row Recovery: stale PROCESSING rows (> 10 min) recover on new POST.
    """

    def setUp(self):
        self.client = APIClient()

        # Create baseline test fixture
        self.user = UserProfile.objects.create(
            employee_id="USR9999",
            name="Test Analyst Subject",
            email="test.subject@enterprise.local",
            role="Software Engineer",
            department="Engineering",
            current_risk_score=85.5,
            current_severity="CRITICAL",
        )

        self.risk_score = RiskScore.objects.create(
            user=self.user,
            date=date(2026, 1, 15),
            xgb_score=0.92,
            if_score=0.88,
            peer_score=0.75,
            user_score=0.80,
            drift_score=0.65,
            final_risk=85.5,
            severity="CRITICAL",
            component_breakdown={"primary": "file_copy_to_usb"},
        )

        self.alert = Alert.objects.create(
            user=self.user,
            risk_score=self.risk_score,
            severity="CRITICAL",
            status="OPEN",
            title="Suspicious After-Hours USB File Copy",
            description="User copied 4.2GB of encrypted archives to removable drive at 02:14 AM.",
        )

        SHAPValue.objects.create(
            alert=self.alert,
            feature_name="usb_bytes_transferred_24h",
            shap_value=0.42,
            actual_value=4294967296.0,
            rank=1,
            direction="INCREASES_RISK",
        )

    @patch("apps.explanations.tasks.call_claude")
    def test_1_success_reaches_completed(self, mock_claude):
        """1. Success: the row reaches COMPLETED with text."""
        mock_claude.return_value = {
            "text": "The user exhibited abnormal after-hours file transfer behavior consistent with insider data staging.",
            "faithfulness_score": 0.98,
            "model_name": "claude-3-5-sonnet",
        }

        explanation = Explanation.objects.create(
            alert=self.alert,
            evidence_hash="test_hash_1",
            status="PENDING",
            evidence_object={"alert_id": self.alert.id},
        )

        res = generate_alert_explanation_task(explanation.id)
        self.assertEqual(res["status"], "success")

        explanation.refresh_from_db()
        self.assertEqual(explanation.status, "COMPLETED")
        self.assertIn("abnormal after-hours", explanation.text)
        self.assertEqual(explanation.attempts, 1)
        self.assertIsNotNone(explanation.finished_at)

    @patch("apps.explanations.tasks.call_claude")
    def test_2_transient_failure_then_success(self, mock_claude):
        """2. Transient failure then success: attempts > 1 and final status is COMPLETED."""
        mock_claude.side_effect = [
            Exception("Connection reset by peer: 502 Bad Gateway"),
            {
                "text": "Recovered on retry attempt: user initiated large USB data transfer after hours.",
                "faithfulness_score": 0.95,
                "model_name": "claude-3-5-sonnet",
            },
        ]

        explanation = Explanation.objects.create(
            alert=self.alert,
            evidence_hash="test_hash_2",
            status="PENDING",
            attempts=0,
            evidence_object={"alert_id": self.alert.id},
        )

        # 1st invocation: fails with transient network error (502) and triggers self.retry
        try:
            generate_alert_explanation_task(explanation.id)
        except Exception:
            pass

        # 2nd invocation (Celery executing the scheduled retry): recovers successfully
        res = generate_alert_explanation_task(explanation.id)
        self.assertEqual(res["status"], "success")

        explanation.refresh_from_db()
        self.assertEqual(explanation.status, "COMPLETED")
        self.assertEqual(explanation.attempts, 2)
        self.assertIn("Recovered on retry attempt", explanation.text)

    @patch("apps.explanations.tasks.call_claude")
    def test_3_retries_exhausted_reaches_failed(self, mock_claude):
        """3. Retries exhausted: final status is FAILED with error message."""
        mock_claude.side_effect = Exception("Rate limit 429: quota exhausted")

        explanation = Explanation.objects.create(
            alert=self.alert,
            evidence_hash="test_hash_3",
            status="PENDING",
            attempts=3,
            evidence_object={"alert_id": self.alert.id},
        )

        # Set Celery task request context with retries at max using push_request
        generate_alert_explanation_task.push_request(retries=3)
        try:
            res = generate_alert_explanation_task(explanation.id)
        finally:
            generate_alert_explanation_task.pop_request()

        explanation.refresh_from_db()
        self.assertEqual(explanation.status, "FAILED")
        self.assertIn("Retries exhausted", explanation.error)
        self.assertIsNotNone(explanation.finished_at)

    @patch("apps.explanations.tasks.call_claude")
    def test_4_permanent_error_auth_no_retry(self, mock_claude):
        """4. Permanent error (auth): FAILED with exactly 1 attempt, no retry."""
        mock_claude.side_effect = Exception("401 Unauthorized: Invalid Anthropic API key provided")

        explanation = Explanation.objects.create(
            alert=self.alert,
            evidence_hash="test_hash_4",
            status="PENDING",
            evidence_object={"alert_id": self.alert.id},
        )

        res = generate_alert_explanation_task(explanation.id)
        self.assertEqual(res["status"], "failed")

        explanation.refresh_from_db()
        self.assertEqual(explanation.status, "FAILED")
        self.assertEqual(explanation.attempts, 1)
        self.assertIn("Permanent failure", explanation.error)

    @patch("apps.explanations.tasks.call_claude")
    def test_5_double_post_only_one_row_and_one_call(self, mock_claude):
        """5. Double POST / Token Quota Defense Test: only one row and one Claude call."""
        mock_claude.return_value = {
            "text": "Debounced response for duplicate alert generation.",
            "faithfulness_score": 0.97,
            "model_name": "claude-3-5-sonnet",
        }

        with self.captureOnCommitCallbacks(execute=True):
            res1 = self.client.post(
                "/api/v1/explanations/",
                data={"alert_id": self.alert.id},
                format="json",
            )
            res2 = self.client.post(
                "/api/v1/explanations/",
                data={"alert_id": self.alert.id},
                format="json",
            )

        self.assertIn(res1.status_code, [status.HTTP_202_ACCEPTED, status.HTTP_200_OK])
        self.assertIn(res2.status_code, [status.HTTP_202_ACCEPTED, status.HTTP_200_OK])

        count = Explanation.objects.filter(alert=self.alert).count()
        self.assertEqual(count, 1)

        # Assert Claude API was invoked exactly once (preserving free token quota)
        mock_claude.assert_called_once()

    @patch("celery.Celery.connection_for_write")
    def test_6_broker_failure_returns_503(self, mock_conn):
        """6. Broker Downtime Test: returns 503 Service Unavailable when broker is down."""
        # Force connection_for_write to raise an exception simulating Redis downtime
        mock_conn.side_effect = Exception("Connection refused: 127.0.0.1:6379")

        # Temporarily enable task_always_eager = False to trigger broker check
        with self.settings(CELERY_TASK_ALWAYS_EAGER=False):
            response = self.client.post(
                "/api/v1/explanations/",
                data={"alert_id": self.alert.id},
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("Task queue unavailable", response.data["error"])

    @patch("apps.explanations.tasks.call_claude")
    def test_7_stale_processing_row_recovers_and_reenqueues(self, mock_claude):
        """7. Stuck-Row Recovery: row trapped in PROCESSING > 10 min gets re-enqueued on POST."""
        mock_claude.return_value = {
            "text": "Recovered from abandoned worker state.",
            "faithfulness_score": 0.96,
            "model_name": "claude-3-5-sonnet",
        }

        # Build exact structured evidence matching EvidenceBuilder
        evidence = EvidenceBuilder.build_alert_evidence(self.alert)

        # Simulate row abandoned 20 minutes ago with matching evidence hash
        stale_exp = Explanation.objects.create(
            alert=self.alert,
            evidence_hash=Explanation.compute_evidence_hash(evidence),
            status="PROCESSING",
            evidence_object=evidence,
        )
        Explanation.objects.filter(pk=stale_exp.id).update(
            created_at=timezone.now() - timedelta(minutes=20)
        )

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                "/api/v1/explanations/",
                data={"alert_id": self.alert.id},
                format="json",
            )

        self.assertIn(response.status_code, [status.HTTP_202_ACCEPTED, status.HTTP_200_OK])
        stale_exp.refresh_from_db()
        self.assertEqual(stale_exp.status, "COMPLETED")
        self.assertIn("Recovered from abandoned worker", stale_exp.text)
