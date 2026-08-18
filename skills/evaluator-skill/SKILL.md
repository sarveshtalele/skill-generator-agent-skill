---
name: evaluator-skill
description: >
  Audits agent skills on quality (best practices, progressive disclosure, functional lift, trigger F1)
  and security (NVIDIA SkillSpector 17-category vulnerability taxonomy), producing scored Markdown & JSON reports.
  Use when the user wants to audit, evaluate, score, vet, or find risks in one or more skills.
  Trigger on: audit skill, evaluate skill, check skills for gaps, is this skill safe to install, scan for vulnerabilities, score my skills.
compatibility: "Python 3.8+"
metadata:
  sdlc: Maintenance
  tags:
    - evaluator-skill
    - SDLC:Maintenance
    - SDLC:Quality
    - SDLC:Security-Audit
    - NVIDIA-SkillSpector
allowed-tools: "Read, Bash(python scripts/*.py:*)"
---

# Evaluator Skill

A comprehensive, production-grade agent skill for evaluating and auditing **Agent Skills** against the [Agent Skills Specification v1.0](https://agentskills.io/specification) and [NVIDIA SkillSpector](https://github.com/nvidia/skillspector) security rules.

## Overview & Execution Contract

This skill runs static analysis, AST inspection, functional assertion grading, trigger intent classification, and progressive disclosure checks across **8 weighted quality dimensions**:

```
┌──────────────────────────────┬────────┬────────────────────────────────────────────────────────┐
│ Dimension                    │ Weight │ Description & Target Metrics                           │
├──────────────────────────────┼────────┼────────────────────────────────────────────────────────┤
│ 1. Specification Compliance  │  10%   │ Frontmatter schema, naming regex, link containment     │
│ 2. Content Quality           │  15%   │ Progressive disclosure, line budget (<500 lines)       │
│ 3. Functional Correctness    │  25%   │ Assertion pass rate on evals/evals.json (>= 80%)       │
│ 4. Skill Lift Delta          │  15%   │ Empirical pass-rate delta (with-skill vs without-skill)│
│ 5. Trigger Quality (F1)      │  10%   │ Intent precision, recall, and F1 score (>= 0.80)       │
│ 6. Reliability               │   5%   │ Zero-crash subprocess execution & timeout guards       │
│ 7. Efficiency                │   5%   │ Token economy (<5000 tokens) and speed (<5s latency)   │
│ 8. Security (SkillSpector)   │  15%   │ 0 Critical, 0 High findings across 17 AST categories   │
└──────────────────────────────┴────────┴────────────────────────────────────────────────────────┘
```

## Step-by-Step Procedural Workflow

When activated, follow this exact workflow:

### Step 1: Execute Automated Evaluation Engine
Run the evaluation runner against the target skill:
```bash
python skills/evaluator-skill/scripts/run_evaluation.py \
  --skill skills/<target-skill-name> \
  --output ./scorecards
```

### Step 2: Review Findings in Scorecard
Inspect the generated reports:
- Markdown Scorecard: `scorecards/<target-skill-name>.md`
- Machine-Readable JSON: `scorecards/<target-skill-name>.json`

### Step 3: Enforce Quality Gate Matrix
- 🟢 **`✅ PASS`**: Overall Score $\ge 80.0$, 0 Critical/High security issues $\to$ Ready to merge / install.
- ⚠️ **`⚠️ WARN`**: $70.0 \le \text{Score} < 80.0$, Medium findings, or $F_1 < 0.80 \to$ Maintainer review recommended.
- 🔴 **`❌ BLOCK`**: Spec errors, failing assertions, or Critical security findings $\to$ Blocked from merge.

### Step 4: Present Formatted Summary to User
Display the scorecard metrics table, security findings breakdown, and clear remediation guidance.

## Examples

### Example: Auditing an Existing Skill
```
User: "Audit skills/csv-analyzer and verify if it's safe to install."
Agent:
1. Executes run_evaluation.py --skill skills/csv-analyzer --output ./scorecards
2. Reads scorecards/csv-analyzer.md
3. Presents quality breakdown (Score: 96.1/100 · Gate: ✅ PASS · Security: 100% Clean).
```

## Error Handling & Gotchas

- **AST False Positives**: If legitimate CLI tools trigger benign warnings, add suppression entries to `.skill-quality/.skillspector-baseline.yaml`.
- **Missing Evals**: If `evals/evals.json` is missing, the skill scores 0 on functional lift and alerts the author.
