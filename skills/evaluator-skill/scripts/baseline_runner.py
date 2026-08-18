from __future__ import annotations
import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict
import argparse
import sys

@dataclass
class BaselineResult:
    output: str
    duration_ms: int
    token_count: int
    success: bool

@dataclass
class LiftMetrics:
    pass_rate_delta: float
    time_delta_ms: int
    token_delta: int
    with_pass_rate: float
    without_pass_rate: float

def setup_baseline_workspace(eval_case: dict, workspace_root: Path) -> Path:
    """Creates a clean workspace and injects fixture files for baseline evaluation."""
    workspace = workspace_root / "baseline_workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    
    fixtures = eval_case.get("fixtures", {})
    for path, content in fixtures.items():
        file_path = workspace / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
    return workspace

def run_baseline_prompt(prompt: str, workspace: Path) -> BaselineResult:
    """Executes a prompt without the skill to measure baseline performance."""
    # This simulates baseline LLM execution
    start = time.time()
    time.sleep(0.1)  # Simulated delay
    duration_ms = int((time.time() - start) * 1000)
    
    return BaselineResult(
        output=f"[Baseline] Evaluated prompt: {prompt}",
        duration_ms=duration_ms,
        token_count=100,  # Simulated token count
        success=True
    )

def compute_skill_lift(with_skill_results: list, baseline_results: list) -> LiftMetrics:
    """Computes the lift metrics by comparing performance with and without the skill."""
    def get_pass_rate(results):
        if not results: return 0.0
        passed = sum(1 for r in results if r.get('success', False))
        return passed / len(results)

    with_pass = get_pass_rate(with_skill_results)
    without_pass = get_pass_rate(baseline_results)
    
    with_time = sum(r.get('duration_ms', 0) for r in with_skill_results) / max(1, len(with_skill_results))
    without_time = sum(r.get('duration_ms', 0) for r in baseline_results) / max(1, len(baseline_results))
    
    with_tokens = sum(r.get('token_count', 0) for r in with_skill_results) / max(1, len(with_skill_results))
    without_tokens = sum(r.get('token_count', 0) for r in baseline_results) / max(1, len(baseline_results))

    return LiftMetrics(
        pass_rate_delta=with_pass - without_pass,
        time_delta_ms=int(with_time - without_time),
        token_delta=int(with_tokens - without_tokens),
        with_pass_rate=with_pass,
        without_pass_rate=without_pass
    )

def write_benchmark(lift: LiftMetrics, output_dir: Path) -> Path:
    """Writes benchmark data to benchmark.json and benchmark.md."""
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "benchmark.json"
    md_path = output_dir / "benchmark.md"
    
    lift_score = max(0.0, min(100.0, (lift.pass_rate_delta + 0.20) / 0.70 * 100.0))
    data = asdict(lift)
    data['lift_score'] = lift_score
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    md_content = f"""# Skill Lift Benchmark

- **With Skill Pass Rate:** {lift.with_pass_rate:.2%}
- **Without Skill Pass Rate:** {lift.without_pass_rate:.2%}
- **Pass Rate Delta:** {lift.pass_rate_delta:+.2%}
- **Time Delta:** {lift.time_delta_ms:+} ms
- **Token Delta:** {lift.token_delta:+} tokens
- **Lift Score:** {lift_score:.2f}/100
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    return json_path

def main():
    parser = argparse.ArgumentParser(description="Run baseline evaluation metrics")
    parser.add_argument("--output-dir", type=str, required=True, help="Directory to save benchmarks")
    args = parser.parse_args()
    
    # Sample execution
    lift = LiftMetrics(0.25, -300, -150, 0.95, 0.70)
    write_benchmark(lift, Path(args.output_dir))
    print(f"Benchmark written to {args.output_dir}")

if __name__ == "__main__":
    main()
