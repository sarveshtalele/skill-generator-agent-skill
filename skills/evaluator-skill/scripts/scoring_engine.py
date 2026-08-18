from __future__ import annotations
import argparse
import json
import sys

WEIGHTS = {
    "spec_compliance": 0.10,
    "content_quality": 0.15,
    "functional_correctness": 0.25,
    "skill_lift": 0.15,
    "trigger_quality": 0.10,
    "reliability": 0.05,
    "efficiency": 0.05,
    "security": 0.15
}

def compute_dimension(name: str, **kwargs) -> float:
    """Computes a specific scoring dimension based on inputs."""
    if name == "spec_compliance":
        return max(0.0, 100.0 - 25.0 * kwargs.get("error_count", 0))
    elif name == "content_quality":
        score = 100.0
        if kwargs.get("lines", 0) > 500: score -= 20.0
        if not kwargs.get("has_examples", True): score -= 10.0
        if not kwargs.get("has_progressive_disclosure", True): score -= 10.0
        return score
    elif name == "functional_correctness":
        total = kwargs.get("total", 1)
        passed = kwargs.get("passed", 0)
        return (passed / max(1, total)) * 100.0
    elif name == "skill_lift":
        lift_delta = kwargs.get("lift_delta", 0.0)
        return max(0.0, min(100.0, (lift_delta + 0.20) / 0.70 * 100.0))
    elif name == "trigger_quality":
        return kwargs.get("f1_score", 0.0) * 100.0
    elif name == "reliability":
        failures = kwargs.get("failures", 0)
        timeouts = kwargs.get("timeouts", 0)
        return max(0.0, 100.0 - (50.0 * failures + 25.0 * timeouts))
    elif name == "efficiency":
        score = 100.0
        if kwargs.get("tokens", 0) > 8000: score -= 30.0
        if kwargs.get("time_s", 0) > 60: score -= 20.0
        return score
    elif name == "security":
        critical = kwargs.get("critical", 0)
        high = kwargs.get("high", 0)
        medium = kwargs.get("medium", 0)
        return max(0.0, 100.0 - (100.0 * critical + 40.0 * high + 15.0 * medium))
    return 0.0

def compute_composite_score(dimensions: dict) -> float:
    """Computes the 8-dimension weighted composite score."""
    total_score = 0.0
    for key, weight in WEIGHTS.items():
        val = dimensions.get(key, 0.0)
        total_score += val * weight
    return total_score

def apply_gate(score: float, security_findings: list, functional_score: float = 100.0) -> str:
    """Applies gating logic to determine PASS, WARN, or BLOCK."""
    has_critical = any(f.get("severity", "").lower() == "critical" for f in security_findings)
    if has_critical or functional_score < 80.0:
        return "BLOCK"
    if score >= 95.0:
        return "PASS"
    elif score >= 75.0:
        return "WARN"
    else:
        return "BLOCK"

def main():
    parser = argparse.ArgumentParser(description="Compute evaluation scores")
    parser.add_argument("--metrics", type=str, help="JSON string of metrics")
    args = parser.parse_args()
    
    # Sample usage and testing
    dimensions = {
        "spec_compliance": compute_dimension("spec_compliance", error_count=0),
        "content_quality": compute_dimension("content_quality", lines=250, has_examples=True, has_progressive_disclosure=True),
        "functional_correctness": compute_dimension("functional_correctness", passed=9, total=10),
        "skill_lift": compute_dimension("skill_lift", lift_delta=0.35),
        "trigger_quality": compute_dimension("trigger_quality", f1_score=0.92),
        "reliability": compute_dimension("reliability", failures=0, timeouts=0),
        "efficiency": compute_dimension("efficiency", tokens=3500, time_s=25),
        "security": compute_dimension("security", critical=0, high=0, medium=0),
    }
    
    score = compute_composite_score(dimensions)
    gate = apply_gate(score, [], dimensions["functional_correctness"])
    
    print(f"Composite Score: {score:.2f}")
    print(f"Gate Result: {gate}")

if __name__ == "__main__":
    main()
