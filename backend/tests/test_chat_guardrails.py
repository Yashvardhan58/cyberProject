"""
Unit and Integration Tests for Centralized Chat Guardrails & Conversational Policy.

Verifies:
1. Greeting → immediate response (0 LLM tokens).
2. Simple system question → immediate response (0 LLM tokens).
3. User-context question → immediate response when information exists.
4. No hallucinated user information when context is absent.
5. UEBA alert question → analysis pipeline.
6. UEBA follow-up question → analysis pipeline / context preservation.
7. Unrelated movie question → early scope response (0 LLM tokens).
8. Unrelated general questions (weather, poems, sports) → early scope response.
9. Ambiguous question → concise clarification.
10. Existing alert-analysis behavior remains unchanged.
"""

from datetime import date
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.users.models import UserProfile
from apps.alerts.models import RiskScore, Alert, SHAPValue
from apps.explanations.models import ChatSession
from apps.explanations.chat_guardrails import (
    evaluate_chat_guardrails,
    ResponseCategory,
    SCOPE_RESPONSE_TEXT,
    SYSTEM_IDENTITY_RESPONSE,
    SYSTEM_WORK_RESPONSE,
    GREETING_RESPONSE,
    STATUS_RESPONSE,
    CLARIFICATION_RESPONSE,
)


class ChatGuardrailsUnitTest(TestCase):
    """
    Focused unit tests for conversational classification and early-return policy.
    """

    def setUp(self):
        self.sample_alert_context = {
            "alert_id": 101,
            "alert_title": "Critical Data Staging Anomaly",
            "employee_context": {
                "employee_id": "USR1001",
                "name": "Alex Mercer",
                "role": "Financial Analyst",
                "department": "Finance",
            },
            "risk_evaluation": {
                "composite_risk_score": 88.5,
                "severity_tier": "CRITICAL",
                "components": {
                    "xgboost_malicious_probability": 0.94,
                    "isolation_forest_anomaly_score": 0.89,
                },
            },
            "top_contributing_features_shap": [
                {
                    "rank": 1,
                    "feature": "file_copy_to_usb_bytes",
                    "shap_impact": 0.44,
                    "direction": "positive",
                },
                {
                    "rank": 2,
                    "feature": "logon_count_after_hours",
                    "shap_impact": 0.38,
                    "direction": "positive",
                },
            ],
            "seven_day_trend": {
                "summary": "Significant escalation from 25.0 to 88.5 over recent days."
            },
        }

    # 1. Greeting → immediate response
    def test_greeting_immediate_response(self):
        for greeting in ["Hi", "Hello", "Hey", "good morning", "Hey there"]:
            decision = evaluate_chat_guardrails(greeting)
            self.assertEqual(decision.category, ResponseCategory.IMMEDIATE_GENERAL)
            self.assertFalse(decision.should_invoke_llm)
            self.assertEqual(decision.response_text, GREETING_RESPONSE)

    # 2. Simple system question → immediate response
    def test_simple_system_question_immediate_response(self):
        # Who are you
        d1 = evaluate_chat_guardrails("Who are you?")
        self.assertEqual(d1.category, ResponseCategory.IMMEDIATE_GENERAL)
        self.assertFalse(d1.should_invoke_llm)
        self.assertEqual(d1.response_text, SYSTEM_IDENTITY_RESPONSE)

        # What is this system
        d2 = evaluate_chat_guardrails("What is this system?")
        self.assertEqual(d2.category, ResponseCategory.IMMEDIATE_GENERAL)
        self.assertFalse(d2.should_invoke_llm)
        self.assertEqual(d2.response_text, SYSTEM_IDENTITY_RESPONSE)

        # What was your work
        d3 = evaluate_chat_guardrails("What was your work?")
        self.assertEqual(d3.category, ResponseCategory.IMMEDIATE_GENERAL)
        self.assertFalse(d3.should_invoke_llm)
        self.assertEqual(d3.response_text, SYSTEM_WORK_RESPONSE)

        # How are you
        d4 = evaluate_chat_guardrails("How are you?")
        self.assertEqual(d4.category, ResponseCategory.IMMEDIATE_GENERAL)
        self.assertFalse(d4.should_invoke_llm)
        self.assertEqual(d4.response_text, STATUS_RESPONSE)

    # 3. User-context question → immediate response when information exists
    def test_user_context_question_when_info_exists(self):
        user_ctx = {"name": "Sarah Connor", "role": "Senior SOC Lead"}
        decision = evaluate_chat_guardrails("What's my name?", user_context=user_ctx)
        self.assertEqual(decision.category, ResponseCategory.IMMEDIATE_GENERAL)
        self.assertFalse(decision.should_invoke_llm)
        self.assertIn("Sarah Connor", decision.response_text)
        self.assertIn("Senior SOC Lead", decision.response_text)

    # 4. No hallucinated user information when context is absent
    def test_no_hallucinated_user_information(self):
        # Empty user context
        decision = evaluate_chat_guardrails("What is my name?", user_context={})
        self.assertEqual(decision.category, ResponseCategory.IMMEDIATE_GENERAL)
        self.assertFalse(decision.should_invoke_llm)
        self.assertIn("No specific personal name is configured", decision.response_text)
        # Verify it did not invent a fake name
        for fake in ["John Doe", "Alice", "Admin", "Bob"]:
            self.assertNotIn(fake, decision.response_text)

    # 5. UEBA alert question → analysis pipeline
    def test_ueba_alert_question_routes_to_pipeline(self):
        queries = [
            "Why was this user flagged?",
            "Explain this alert",
            "What caused this risk score?",
            "What suspicious behavior was detected?",
            "Why does employee U123 look suspicious?",
        ]
        for q in queries:
            decision = evaluate_chat_guardrails(q, alert_context=self.sample_alert_context)
            self.assertEqual(decision.category, ResponseCategory.DOMAIN_ANALYSIS)
            # Must either provide a faithful in-context answer or route to LLM
            self.assertTrue(decision.evidence_grounded)

    # 6. UEBA follow-up question → analysis pipeline / context preservation
    def test_ueba_followup_question_in_alert_context(self):
        followups = [
            "Tell me what happened here",
            "What activity contributed most?",
            "What should I do next?",
            "Why?",
            "Details?",
        ]
        for f in followups:
            decision = evaluate_chat_guardrails(f, alert_context=self.sample_alert_context)
            self.assertEqual(decision.category, ResponseCategory.DOMAIN_ANALYSIS)
            self.assertTrue(decision.evidence_grounded)

    # 7. Unrelated movie question → early scope response
    def test_unrelated_movie_question_early_scope_response(self):
        movie_queries = [
            "Who is the hero of this movie?",
            "Who directed Inception?",
            "Tell me about the latest Bollywood film",
            "What is your favorite cinema actor?",
        ]
        for mq in movie_queries:
            decision = evaluate_chat_guardrails(mq, alert_context=self.sample_alert_context)
            self.assertEqual(decision.category, ResponseCategory.OUT_OF_SCOPE)
            self.assertFalse(decision.should_invoke_llm)
            self.assertEqual(decision.response_text, SCOPE_RESPONSE_TEXT)

    # 8. Unrelated general question → early scope response
    def test_unrelated_general_question_early_scope_response(self):
        general_queries = [
            "What's the weather today?",
            "Write me a poem about flowers",
            "Tell me a joke",
            "Who won yesterday's cricket match?",
            "How to cook chicken biryani recipe?",
            "How to invert a binary tree in python?",
        ]
        for gq in general_queries:
            decision = evaluate_chat_guardrails(gq)
            self.assertEqual(decision.category, ResponseCategory.OUT_OF_SCOPE)
            self.assertFalse(decision.should_invoke_llm)
            self.assertEqual(decision.response_text, SCOPE_RESPONSE_TEXT)

    # 9. Ambiguous question → concise clarification
    def test_ambiguous_question_concise_clarification(self):
        ambiguous = ["?", "...", "asdfgh", "umm", "k"]
        for amb in ambiguous:
            decision = evaluate_chat_guardrails(amb, alert_context=self.sample_alert_context)
            self.assertEqual(decision.category, ResponseCategory.CLARIFICATION)
            self.assertFalse(decision.should_invoke_llm)
            self.assertEqual(decision.response_text, CLARIFICATION_RESPONSE)

    # 10. Repetitive query token saving shortcut
    def test_repetitive_query_token_saving_shortcut(self):
        history = [
            {"role": "user", "content": "What is the risk score?"},
            {"role": "assistant", "content": "The composite risk score is 88.5 [CRITICAL]."},
        ]
        # Same user question repeated
        decision = evaluate_chat_guardrails(
            "What is the risk score?",
            alert_context=self.sample_alert_context,
            conversation_history=history,
        )
        self.assertFalse(decision.should_invoke_llm)
        self.assertIn("88.5", decision.response_text)


class ChatGuardrailsIntegrationTest(TestCase):
    """
    End-to-end integration tests verifying API endpoint behavior with guardrails active.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = UserProfile.objects.create(
            employee_id="USR5555",
            name="Johnathan Swift",
            email="j.swift@enterprise.corp",
            role="Data Architect",
            department="IT",
            current_risk_score=91.0,
            current_severity="CRITICAL",
        )
        self.risk_score = RiskScore.objects.create(
            user=self.user,
            date=date(2026, 2, 20),
            xgb_score=0.95,
            if_score=0.90,
            peer_score=0.85,
            user_score=0.88,
            drift_score=0.70,
            final_risk=91.0,
            severity="CRITICAL",
        )
        self.alert = Alert.objects.create(
            user=self.user,
            risk_score=self.risk_score,
            title="Massive Data Staging via External Drive",
            severity="CRITICAL",
            status="OPEN",
        )
        self.shap = SHAPValue.objects.create(
            alert=self.alert,
            rank=1,
            feature_name="file_copy_to_usb_bytes",
            actual_value=10737418240.0,
            shap_value=0.52,
            direction="positive",
        )
        self.session = ChatSession.objects.create(
            alert=self.alert,
            session_token="test-guardrail-token-12345",
            analyst_name="Agent Mulder",
        )

    def test_greeting_endpoint_returns_immediate_guardrail_policy(self):
        url = f"/api/v1/explanations/sessions/{self.session.session_token}/"
        res = self.client.post(url, {"message": "hello"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()["data"]
        self.assertEqual(data["model"], "deterministic-guardrail-policy")
        self.assertEqual(data["content"], GREETING_RESPONSE)

    def test_out_of_scope_movie_endpoint_returns_scope_text(self):
        url = f"/api/v1/explanations/sessions/{self.session.session_token}/"
        res = self.client.post(url, {"message": "Who is the hero of this movie?"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()["data"]
        self.assertEqual(data["model"], "deterministic-guardrail-policy")
        self.assertEqual(data["content"], SCOPE_RESPONSE_TEXT)

    def test_ueba_domain_question_remains_fully_functional(self):
        url = f"/api/v1/explanations/sessions/{self.session.session_token}/"
        res = self.client.post(url, {"message": "Why was this user flagged?"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()["data"]
        # Grounded answer produced
        self.assertTrue(len(data["content"]) > 20)
        self.assertIn("Johnathan Swift", data["content"])
