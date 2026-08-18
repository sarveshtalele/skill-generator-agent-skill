"""Test Plan Orchestrator for Agent Skills.

Generates an actionable, task-based `testing.md` checklist containing
unit testing and E2E test plans, prompts the user for verification, and
generates ground-truth `evals/evals.json`.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def generate_task_testing_md(skill_name: str, skill_dir: Path) -> Path:
    """Generate a task-based testing.md checklist for the newly created skill."""
    snake_name = skill_name.replace("-", "_")
    testing_content = f"""# 🧪 Task-Based Testing & Verification Plan: `{skill_name}`

This document outlines the systematic verification lifecycle for the **`{skill_name}`** skill. Follow and check off each task below to validate unit-level correctness, end-to-end procedural execution, and quality evaluation gates.

---

## 📋 Task 1: Unit Testing (Deterministic Code Execution)

- [ ] **Task 1.1: Syntax & Import Validation**:
  - Run Python compilation on the engine script:
    ```bash
    python -m py_compile skills/{skill_name}/scripts/{snake_name}_skill.py
    ```
- [ ] **Task 1.2: Script Direct Execution**:
  - Execute the script directly with `--help` and sample inputs:
    ```bash
    python skills/{skill_name}/scripts/{snake_name}_skill.py --target . --output ./output
    ```
  - Verify JSON output creation under `./output/{skill_name}_report.json`.
- [ ] **Task 1.3: Exit Code & Error Handling**:
  - Verify clean exit code `0` on valid inputs and non-zero on malformed inputs.

---

## 🎭 Task 2: End-to-End (E2E) Procedural Testing

- [ ] **Task 2.1: User Prompt Activation**:
  - Test prompt in AI IDE (Claude Code, Cursor, Antigravity):
    > *"Run {skill_name} on this project"*
  - Verify AI agent loads `SKILL.md` (progressive disclosure footprint < 5000 tokens).
- [ ] **Task 2.2: Artifact Generation**:
  - Confirm the agent generates the expected report using `templates/report_template.md`.
- [ ] **Task 2.3: Edge Case Verification**:
  - Test negative/empty input scenarios to confirm graceful fallbacks.

---

## 💻 Task 3: User Test Case Alignment & Confirmation

> ⚠️ **Action Required by User**: Review the generated test cases below. Once approved, mark the confirmation checkbox and proceed to Task 4.

### Proposed Test Suite (`evals/evals.json`):

1. **Test Case 1 (Primary Execution)**:
   - **Prompt**: `"Execute {skill_name} analysis on the target repository."`
   - **Expected Output**: `"Formatted {skill_name} report containing verified findings and actionable recommendations."`
   - **Assertions**:
     - `contains:findings`
     - `contains:recommendations`
     - `matches:(?i)({skill_name}|report|analysis)`

- [ ] **User Confirmation**: [X] Approved proposed test suite for automated benchmark execution.

---

## 📊 Task 4: Automated Evaluation & Gating (`evaluator-skill`)

- [ ] **Task 4.1: Run Local Skill Evaluation**:
  ```bash
  python -m evaluator.cli skill skills/{skill_name} --output-dir scorecards
  ```
- [ ] **Task 4.2: Inspect Quality Scorecard**:
  - Verify overall quality score $\\ge 90.0 / 100$.
  - Security (NVIDIA SkillSpector) = `100.0%` (0 Critical, 0 High).
  - Gate Decision = `✅ PASS`.
"""
    testing_file = skill_dir / "testing.md"
    testing_file.write_text(testing_content, encoding="utf-8")
    print(f"📝 Generated task-based testing checklist at {testing_file}")
    return testing_file


def generate_evals_json(skill_name: str, skill_dir: Path) -> Path:
    """Generate evals/evals.json benchmark suite."""
    evals_dir = skill_dir / "evals"
    evals_dir.mkdir(parents=True, exist_ok=True)
    evals_file = evals_dir / "evals.json"
    
    evals_data = {
        "skill_name": skill_name,
        "evals": [
            {
                "id": "eval-001",
                "prompt": f"Execute {skill_name} analysis on the target repository.",
                "expected_output": f"Formatted {skill_name} report containing verified findings and actionable recommendations.",
                "files": [],
                "assertions": [
                    "contains:findings",
                    "contains:recommendations",
                    f"matches:(?i)({skill_name}|report|analysis)"
                ]
            }
        ]
    }
    
    evals_file.write_text(json.dumps(evals_data, indent=2), encoding="utf-8")
    print(f"🧪 Generated benchmark evals at {evals_file}")
    return evals_file


def main():
    parser = argparse.ArgumentParser(description="Generate task testing checklist and evals for a skill")
    parser.add_argument("--skill", required=True, help="Path to skill directory")
    parser.add_argument("--with-evals", action="store_true", help="Also generate evals/evals.json")
    args = parser.parse_args()
    
    skill_path = Path(args.skill)
    skill_name = skill_path.name
    generate_task_testing_md(skill_name, skill_path)
    if args.with_evals:
        generate_evals_json(skill_name, skill_path)


if __name__ == "__main__":
    main()
