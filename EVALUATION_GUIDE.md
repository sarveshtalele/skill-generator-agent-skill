# 📘 Comprehensive Agent Skill Evaluation Guide

This guide outlines the methodology, metrics, mathematical formulas, and command interfaces used by the **`evaluator-skill`** to evaluate AI agent skills against the [Agent Skills Specification v1.0](https://agentskills.io/specification) and [NVIDIA SkillSpector](https://github.com/nvidia/skillspector) security standards.

---

## 🎯 Evaluation Methodology (RAGAS-Aligned)

The evaluation framework assesses skills across **8 weighted quality dimensions**, combining deterministic static inspection, AST data-flow analysis, multi-type assertion execution, and baseline comparison.

```
Composite Quality Score (0 - 100) = ∑ (Weight_i × Dimension_Score_i)
```

| Dimension | Weight | Target | Description |
|:---|:---:|:---:|:---|
| **1. Specification Compliance** | **10%** | 100 / 100 | Valid YAML frontmatter, naming regex, link containment, standard layout |
| **2. Content Quality** | **15%** | $\ge 90$ | Progressive disclosure (<500 lines `SKILL.md`), worked examples, reference linking |
| **3. Functional Correctness** | **25%** | $\ge 80\%$ | Multi-type assertion pass rate on `evals/evals.json` |
| **4. Skill Lift Delta** | **15%** | $> 0.0$ | Empirical performance improvement over the base LLM without the skill |
| **5. Trigger Quality (F1)** | **10%** | $\ge 0.80$ | Intent classification precision and recall across positive and negative queries |
| **6. Reliability** | **5%** | 100 / 100 | Deterministic execution without crashes, exceptions, or timeouts |
| **7. Efficiency** | **5%** | $\ge 85$ | Active context token economy (<8000 tokens) and speed (<60s) |
| **8. Security (SkillSpector)** | **15%** | 0 Crit / 0 High | 68 vulnerability patterns + AST data-flow taint tracking + YARA signatures |

---

## 📐 Scoring Formulas

### 1. Specification Compliance ($S_1$)
$$S_1 = \max(0,\; 100 - 25 \times E)$$
- $E$ = Number of structural specification errors (missing frontmatter, invalid name, broken file pointers).

### 2. Content Quality ($S_2$)
$$S_2 = 100 - D_{\text{length}} - D_{\text{examples}} - D_{\text{disclosure}}$$
- $D_{\text{length}}$ = 20 if `SKILL.md` > 500 lines, else 0
- $D_{\text{examples}}$ = 10 if no code blocks or worked examples are present, else 0
- $D_{\text{disclosure}}$ = 10 if neither `references/` nor `scripts/` exist, else 0

### 3. Functional Correctness ($S_3$)
$$S_3 = \frac{\text{Passed Assertions}}{\text{Total Assertions}} \times 100$$
*(Note: $S_3 < 80$ triggers an automatic quality gate `BLOCK`)*.

### 4. Skill Lift Delta ($S_4$)
$$S_4 = \text{clamp}\!\left(\frac{\Delta_{\text{pass\_rate}} + 0.20}{0.70} \times 100,\; 0,\; 100\right)$$
- $\Delta_{\text{pass\_rate}} = \text{PassRate}_{\text{with\_skill}} - \text{PassRate}_{\text{without\_skill}}$

### 5. Trigger Quality / F1 ($S_5$)
$$S_5 = F_1 \times 100 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}} \times 100$$

### 6. Reliability ($S_6$)
$$S_6 = \max(0,\; 100 - 50 \times \text{Failures} - 25 \times \text{Timeouts})$$

### 7. Efficiency ($S_7$)
$$S_7 = 100 - (\text{if Tokens} > 8000 \to 30) - (\text{if Time} > 60\text{s} \to 20)$$

### 8. Security ($S_8$)
$$S_8 = \max(0,\; 100 - 100 \times \text{Critical} - 40 \times \text{High} - 15 \times \text{Medium})$$
*(Note: Any Critical security finding triggers an automatic quality gate `BLOCK`)*.

---

## 🚦 Quality Gate Matrix

| Quality Gate | Condition | Action |
|:---|:---|:---|
| 🟢 **`PASS`** | $\text{Score} \ge 95.0$ AND 0 Critical/High security AND Functional $\ge 80\%$ | Automatically approved for merging and installation. |
| ⚠️ **`WARN`** | $75.0 \le \text{Score} < 95.0$ AND 0 Critical security | Requires maintainer review before merging. |
| 🔴 **`BLOCK`** | $\text{Score} < 75.0$ OR $\ge 1$ Critical finding OR Functional $< 80\%$ | Pull request or installation blocked. |

---

## 🧪 Assertion Syntax in `evals/evals.json`

Define benchmark test cases using the 5 supported assertion types:

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": "eval-001",
      "prompt": "Analyze dataset.csv and generate summary report",
      "files": ["fixtures/dataset.csv"],
      "assertions": [
        "file:output/summary.json",
        "json:summary.row_count",
        "contains:Report Generated",
        "matches:(?i)(success|completed)",
        "Calculates accurate mean and standard deviation for all numeric columns"
      ]
    }
  ]
}
```

1. **`file:<relative_path>`**: Verifies that the specified file was generated in the workspace.
2. **`json:<key_path>`**: Parses output as JSON and verifies the dot-notated key exists (e.g. `metrics.total`).
3. **`contains:<text>`**: Verifies case-insensitive substring existence in model output.
4. **`matches:<regex>`**: Verifies regular expression match.
5. **`<semantic text>`**: Evaluates conceptual compliance using LLM semantic grading.

---

## 💻 CLI Commands

```bash
# 1. Full 8-Dimension Evaluation
python skills/evaluator-skill/scripts/run_evaluation.py --skill skills/<name> --output ./scorecards

# 2. Evaluation with Baseline Comparison
python skills/evaluator-skill/scripts/run_evaluation.py --skill skills/<name> --output ./scorecards --with-baseline

# 3. Security Scan with SARIF Export
python skills/evaluator-skill/scripts/security_scan.py skills/<name> --format sarif --output results.sarif

# 4. Trigger Description Optimization
python skills/skill-creator/scripts/run_loop.py --skill skills/<name> --iterations 5

# 5. Package as Distributable .skill File
python skills/skill-creator/scripts/package_skill.py --skill skills/<name> --output ./dist

# 6. Regenerate Portfolio Scorecard
python scripts/generate_scorecard.py
```
