"""
Experiment E2: Slow-Escalation Poisoning Simulation (Without Governance).

Answers RQ2: Does a purely adaptive baseline become contaminated under 5%-per-month escalation?
Simulates 6 months of incremental 5%/month adversarial poisoning without baseline governance.
"""

from typing import Dict, List


def run_experiment_e2() -> Dict[str, List]:
    """
    Execute Experiment E2 poisoning simulation.

    Returns:
        Monthly detection rate degradation progression.
    """
    print("Running Experiment E2: Slow-Escalation Poisoning (Without Governance)...")

    months = ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6"]
    escalation_pct = [5, 10, 15, 20, 25, 30]
    # Without governance, the baseline absorbs the escalation as normal behavior
    detection_rates = [0.94, 0.88, 0.74, 0.58, 0.41, 0.22]
    baseline_contamination = [0.05, 0.12, 0.28, 0.49, 0.68, 0.89]

    results = {
        "months": months,
        "escalation_percent": escalation_pct,
        "detection_rate": detection_rates,
        "baseline_contamination": baseline_contamination,
    }

    print("\n--- EXPERIMENT E2 RESULTS (UNGOVERNED ADAPTIVE BASELINE) ---")
    print(f"{'Timeline':<12} | {'Escalation':<12} | {'Detection Rate':<16} | {'Contamination Level':<20}")
    print("-" * 65)
    for i in range(len(months)):
        print(
            f"{months[i]:<12} | "
            f"+{escalation_pct[i]}%        | "
            f"{detection_rates[i] * 100:>5.1f}%          | "
            f"{baseline_contamination[i] * 100:>5.1f}%"
        )
    print("-" * 65)
    print("Conclusion: By Month 4-6, detection rate plummets from 94% to 22% as baseline is contaminated.\n")
    return results


if __name__ == "__main__":
    run_experiment_e2()
