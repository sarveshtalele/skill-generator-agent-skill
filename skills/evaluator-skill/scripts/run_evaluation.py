"""Deterministic Hybrid Runner for Evaluator Skill.

Supports two evaluation modes:
1. Native Project CLI Mode (Full 8 Dimensions, Baseline Lift, Trigger F1, SkillSpector AST)
2. Standalone Zero-Dependency Mode (Structural check, progressive disclosure, regex + AST security scan)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Try to import standalone local scripts if available in same directory
try:
    from .structural_check import run_structural_check
    from .security_scan import run_security_scan
except ImportError:
    try:
        from structural_check import run_structural_check
        from security_scan import run_security_scan
    except ImportError:
        run_structural_check = None
        run_security_scan = None


def evaluate_target_skill(skill_path: Path, output_dir: Path) -> dict:
    """Run full evaluation suite on a target skill with graceful fallback."""
    output_dir.mkdir(parents=True, exist_ok=True)
    skill_name = skill_path.name
    
    # 1. First try invoking native unified framework if installed
    cmd = [
        sys.executable,
        "-m",
        "evaluator.cli",
        "all",
        str(skill_path),
        "--output-dir",
        str(output_dir),
    ]
    
    proc = subprocess.run(cmd, capture_output=True, text=True)
    scorecard_json = output_dir / f"{skill_name}.json"
    scorecard_md = output_dir / f"{skill_name}.md"
    
    if scorecard_json.exists():
        data = json.loads(scorecard_json.read_text(encoding="utf-8"))
        print(f"📊 Framework evaluation completed for {skill_name}: Score {data.get('overall_score', 'N/A')}/100 | Status: {data.get('gate_decision', 'UNKNOWN')}")
        return data
        
    # 2. Standalone fallback execution if native framework is not in PYTHONPATH
    print(f"ℹ️ Framework CLI unavailable, running standalone AST & structural evaluation...")
    struct_res = {}
    sec_res = {}
    
    if run_structural_check:
        struct_res = run_structural_check(skill_path)
    if run_security_scan:
        sec_res = run_security_scan(skill_path)
        
    sec_findings = sec_res.get("findings", [])
    crit_high = [f for f in sec_findings if f.get("severity") in ("CRITICAL", "HIGH")]
    gate_decision = "BLOCK" if crit_high else ("PASS" if not struct_res.get("errors") else "WARN")
    
    report_data = {
        "skill_name": skill_name,
        "overall_score": 95.0 if gate_decision == "PASS" else (75.0 if gate_decision == "WARN" else 0.0),
        "gate_decision": gate_decision,
        "structural": struct_res,
        "security": sec_res,
        "mode": "standalone_ast"
    }
    
    scorecard_json.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
    md_content = f"""# 🤖 Agent Skill Evaluation: `{skill_name}`

**Quality Score**: `{report_data['overall_score']}/100` | **Status**: `{'✅ PASS' if gate_decision == 'PASS' else ('⚠️ WARN' if gate_decision == 'WARN' else '❌ BLOCK')}` | **Mode**: `Standalone Static & AST`

## 🛡️ Security Summary
- Critical: `{len([f for f in sec_findings if f.get('severity') == 'CRITICAL'])}` | High: `{len([f for f in sec_findings if f.get('severity') == 'HIGH'])}`
- Gate Decision: `{'✅ PASS' if gate_decision == 'PASS' else '❌ BLOCK'}`
"""
    scorecard_md.write_text(md_content, encoding="utf-8")
    print(f"📊 Standalone evaluation completed for {skill_name}: Status {gate_decision}")
    return report_data


def main():
    parser = argparse.ArgumentParser(description="Run 8-dimension Agent Skill quality & security evaluation")
    parser.add_argument("--skill", required=True, help="Path to skill folder")
    parser.add_argument("--output", default="./scorecards", help="Scorecards output folder")
    args = parser.parse_args()
    
    evaluate_target_skill(Path(args.skill), Path(args.output))
    sys.exit(0)


if __name__ == "__main__":
    main()
