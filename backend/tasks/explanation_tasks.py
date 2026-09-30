"""
Celery Asynchronous Tasks Compatibility Module.
Re-exports tasks from apps.explanations.tasks and apps.baselines.tasks.
"""

from apps.explanations.tasks import generate_alert_explanation_task
from apps.baselines.tasks import run_baseline_governance_task

# Re-export weekly governance task alias
run_weekly_governance_check_task = run_baseline_governance_task

__all__ = (
    "generate_alert_explanation_task",
    "run_baseline_governance_task",
    "run_weekly_governance_check_task",
)
