# 🧪 Task-Based Testing & Verification Plan: `token-telemetry`

This document outlines the systematic verification lifecycle for the **`token-telemetry`** skill. Follow and check off each task below to validate unit-level correctness, end-to-end procedural execution, and quality evaluation gates.

---

## 📋 Task 1: Unit Testing (Deterministic Code Execution)

- [ ] **Task 1.1: Syntax & Import Validation**:
  - Run Python compilation on the engine script:
    ```bash
    python -m py_compile skills/token-telemetry/scripts/token_telemetry_skill.py
    ```
- [ ] **Task 1.2: Script Direct Execution**:
  - Execute the script directly with `--help` and sample inputs:
    ```bash
    python skills/token-telemetry/scripts/token_telemetry_skill.py --target . --output ./output
    ```
  - Verify JSON output creation under `./output/token-telemetry_report.json`.
- [ ] **Task 1.3: Exit Code & Error Handling**:
  - Verify clean exit code `0` on valid inputs and non-zero on malformed inputs.

---

## 🎭 Task 2: End-to-End (E2E) Procedural Testing

- [ ] **Task 2.1: User Prompt Activation**:
  - Test prompt in AI IDE (Claude Code, Cursor, Antigravity):
    > *"Run token-telemetry on this project"*
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
   - **Prompt**: `"Execute token-telemetry analysis on the target repository."`
   - **Expected Output**: `"Formatted token-telemetry report containing verified findings and actionable recommendations."`
   - **Assertions**:
     - `contains:findings`
     - `contains:recommendations`
     - `matches:(?i)(token-telemetry|report|analysis)`

- [ ] **User Confirmation**: [X] Approved proposed test suite for automated benchmark execution.

---

## 📊 Task 4: Automated Evaluation & Gating (`evaluator-skill`)

- [ ] **Task 4.1: Run Local Skill Evaluation**:
  ```bash
  python -m evaluator.cli skill skills/token-telemetry --output-dir scorecards
  ```
- [ ] **Task 4.2: Inspect Quality Scorecard**:
  - Verify overall quality score $\ge 90.0 / 100$.
  - Security (NVIDIA SkillSpector) = `100.0%` (0 Critical, 0 High).
  - Gate Decision = `✅ PASS`.
