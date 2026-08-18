"""Deterministic Runner for Evaluator Skill.

Invokes the unified 8-dimension evaluator CLI over individual skills
or entire repositories and formats auditable Markdown and JSON scorecards.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def evaluate_target_skill(skill_path: Path, output_dir: Path) -> dict:
    """Run full evaluation suite on a target skill."""
    output_dir.mkdir(parents=True, exist_ok=True)
    skill_name = skill_path.name
    
    cmd = [
        sys.executable,
        "-m",
        "evaluator.cli",
        "skill",
        str(skill_path),
        "--output-dir",
        str(output_dir),
    ]
    
    proc = subprocess.run(cmd, capture_output=True, text=True)
    scorecard_json = output_dir / f"{skill_name}.json"
    scorecard_md = output_dir / f"{skill_name}.md"
    
    if scorecard_json.exists():
        data = json.loads(scorecard_json.read_text(encoding="utf-8"))
        print(f"📊 Evaluation completed for {skill_name}: Score {data.get('overall_score', 'N/A')}/100 | Status: {data.get('gate_decision', 'UNKNOWN')}")
        return data
    else:
        print(f"❌ Evaluation CLI error: {proc.stderr}")
        return {"skill": skill_name, "status": "ERROR", "message": proc.stderr}


def main():
    parser = argparse.ArgumentParser(description="Run 8-dimension Agent Skill quality & security evaluation")
    parser.add_argument("--skill", required=True, help="Path to skill folder")
    parser.add_argument("--output", default="./scorecards", help="Scorecards output folder")
    args = parser.parse_args()
    
    evaluate_target_skill(Path(args.skill), Path(args.output))
    sys.exit(0)


if __name__ == "__main__":
    main()
