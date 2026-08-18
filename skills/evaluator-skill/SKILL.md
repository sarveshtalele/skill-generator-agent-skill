---
name: evaluator-skill
description: >
  Audits agent skills on quality (specification compliance, progressive disclosure, functional correctness, skill lift delta, trigger F1)
  and security (NVIDIA SkillSpector 68-pattern AST taint tracking, YARA signatures, Unicode deception, and optional semantic analysis),
  producing scored Markdown, JSON, and SARIF quality reports.
  Use this whenever the user wants to audit, evaluate, score, vet, verify safety, or find risks/gaps in any agent skill or skill repository.
  Trigger on: audit skill, evaluate skill, check skills for gaps, is this skill safe to install, scan for vulnerabilities, score my skills, run quality gate, generate sarif security report, test skill baseline lift.
compatibility: "Python 3.8+"
metadata:
  sdlc: Maintenance
  tags:
    - evaluator-skill
    - SDLC:Maintenance
    - SDLC:Quality
    - SDLC:Security-Audit
    - NVIDIA-SkillSpector
    - RAGAS-Evaluation
allowed-tools: "Read, Bash(python scripts/*.py:*)"
---

# Evaluator Skill

A comprehensive, production-grade agent skill for evaluating and auditing **Agent Skills** against the [Agent Skills Specification v1.0](https://agentskills.io/specification) and [NVIDIA SkillSpector](https://github.com/nvidia/skillspector) security standards.

## Overview & Evaluation Architecture

This skill executes static AST inspection, data-flow taint tracking, YARA signature matching, multi-type functional assertion grading, baseline comparison, execution tracing, and progressive disclosure checks across **8 weighted quality dimensions**:

```
┌──────────────────────────────┬────────┬────────────────────────────────────────────────────────┐
│ Dimension                    │ Weight │ Description & Target Metrics                           │
├──────────────────────────────┼────────┼────────────────────────────────────────────────────────┤
│ 1. Specification Compliance  │  10%   │ Valid frontmatter, naming regex, link containment      │
│ 2. Content Quality           │  15%   │ Progressive disclosure, line budget (<500 lines)       │
│ 3. Functional Correctness    │  25%   │ Multi-type assertion pass rate in evals.json (>= 80%)  │
│ 4. Skill Lift Delta          │  15%   │ Empirical pass-rate delta (with-skill vs baseline)     │
│ 5. Trigger Quality (F1)      │  10%   │ Intent precision, recall, and F1 score (>= 0.80)       │
│ 6. Reliability               │   5%   │ Zero-crash subprocess execution & timeout guards       │
│ 7. Efficiency                │   5%   │ Token economy (<8000 tokens) and speed (<60s latency)  │
│ 8. Security (SkillSpector)   │  15%   │ 0 Critical, 0 High findings across 68 patterns + Taint │
└──────────────────────────────┴────────┴────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Procedural Workflow

When activated, follow this exact sequence:

### Step 1: Execute Automated Evaluation Engine

Run the evaluation runner against the target skill:

```bash
# Standard 8-dimension evaluation with Markdown & JSON scorecards
python skills/evaluator-skill/scripts/run_evaluation.py \
  --skill skills/<target-skill-name> \
  --output ./scorecards

# Optional: Run with baseline comparison to measure empirical skill lift
python skills/evaluator-skill/scripts/run_evaluation.py \
  --skill skills/<target-skill-name> \
  --output ./scorecards \
  --with-baseline

# Optional: Export SARIF for GitHub CodeQL / Security tab integration
python skills/evaluator-skill/scripts/security_scan.py \
  skills/<target-skill-name> \
  --format sarif \
  --output ./results.sarif
```

### Step 2: Review Generated Artifacts

Inspect the generated evaluation output artifacts:
- **Markdown Scorecard**: `scorecards/<target-skill-name>.md`
- **JSON Telemetry**: `scorecards/<target-skill-name>.json`
- **Execution Trace**: `scorecards/<target-skill-name>_trace.json`
- **Timing & Tokens**: `scorecards/<target-skill-name>_timing.json`
- **Benchmark Lift**: `scorecards/<target-skill-name>_benchmark.json` (when `--with-baseline` is used)

### Step 3: Enforce Quality Gate Matrix

Check the resulting gate decision against the criteria defined in [`references/scoring_formulas.md`](references/scoring_formulas.md):

- 🟢 **`✅ PASS`**: Overall Score $\ge 95.0$, 0 Critical/High security issues, Functional Correctness $\ge 80\%$ $\to$ Ready to merge / install.
- ⚠️ **`⚠️ WARN`**: $75.0 \le \text{Score} < 95.0$, 0 Critical security issues $\to$ Maintainer review recommended.
- 🔴 **`❌ BLOCK`**: Score $< 75.0$, any Critical security finding, or Functional Correctness $< 80\%$ $\to$ Blocked from merge.

### Step 4: Consult Domain References

- **Security Details**: Refer to [`references/security_patterns.md`](references/security_patterns.md) for full descriptions of the 68 patterns, AST taint analysis, and YARA signatures.
- **Scoring Formulas**: Refer to [`references/scoring_formulas.md`](references/scoring_formulas.md) for the exact math behind every dimension.
- **JSON Schemas**: Refer to [`references/schemas.md`](references/schemas.md) for structural specifications of all output files.
- **Content Rubric**: Refer to [`references/content_rubric.md`](references/content_rubric.md) for qualitative checklist items.

---

## Multi-Type Assertion Syntax

The evaluation engine supports 5 assertion types in `evals/evals.json`:
1. `contains:<text>` — Case-insensitive substring verification.
2. `matches:<regex>` — Regular expression validation.
3. `file:<path>` — Verification that a generated output file exists in the workspace.
4. `json:<key.path>` — Verification that a JSON output contains the specified key path.
5. `<semantic assertion>` — LLM-graded conceptual assertion with evidence citation.

---

## False Positive Management

If legitimate operational code (such as CLI subprocess wrappers) triggers a security finding, add a suppression rule to `.skill-quality/.skillspector-baseline.yaml`:

```yaml
suppressions:
  - id: AST4
    file_glob: "scripts/my_script.py"
    reason: "Legitimate subprocess execution using literal argument list"
```

---

## 📦 Bundled Resources & Engine Scripts

- **Core Orchestrator**: [`scripts/run_evaluation.py`](scripts/run_evaluation.py)
- **Quality & Spec Checkers**: [`scripts/structural_check.py`](scripts/structural_check.py), [`scripts/assertion_engine.py`](scripts/assertion_engine.py)
- **Security Engines**: [`scripts/security_scan.py`](scripts/security_scan.py), [`scripts/taint_tracker.py`](scripts/taint_tracker.py), [`scripts/yara_scanner.py`](scripts/yara_scanner.py), [`scripts/semantic_scanner.py`](scripts/semantic_scanner.py), [`scripts/adjudicator.py`](scripts/adjudicator.py)
- **Telemetry & Baseline**: [`scripts/trace_capture.py`](scripts/trace_capture.py), [`scripts/scoring_engine.py`](scripts/scoring_engine.py), [`scripts/baseline_runner.py`](scripts/baseline_runner.py)
- **Reporting & Batch**: [`scripts/sarif_report.py`](scripts/sarif_report.py), [`scripts/batch_scan.py`](scripts/batch_scan.py), [`scripts/generate_html_report.py`](scripts/generate_html_report.py)
- **Signatures & Assets**: [`assets/agent_skills.yar`](assets/agent_skills.yar)
- **References**: [`references/security_patterns.md`](references/security_patterns.md), [`references/scoring_formulas.md`](references/scoring_formulas.md), [`references/schemas.md`](references/schemas.md), [`references/content_rubric.md`](references/content_rubric.md)

---

## Examples

### Example: Comprehensive Skill Audit
```
User: "Audit skills/csv-analyzer, test its skill lift, and verify if it is safe to install."
Agent:
1. Executes: python skills/evaluator-skill/scripts/run_evaluation.py --skill skills/csv-analyzer --output ./scorecards --with-baseline
2. Reads: scorecards/csv-analyzer.md and scorecards/csv-analyzer.json
3. Delivers breakdown:
   - Overall Quality Score: 96.1 / 100 (✅ PASS)
   - Security: 100% Clean (0 Critical, 0 High across 68 patterns)
   - Functional Correctness: 100% (5/5 assertions passed)
   - Skill Lift Delta: +0.45 pass rate improvement over baseline LLM
```
