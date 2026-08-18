# Scorecard: `evaluator-skill`

**Overall Quality Score**: `92.6/100`  
**Evaluation Status**: **✅ PASS**  
**Evaluation Mode**: `⚡ Static Heuristic (Fast CI)`  

## Dimension Breakdown

| Quality Dimension | Weight | Score | Status |
| :--- | :---: | :---: | :---: |
| **Specification Compliance** | 10% | `100.0` | ✅ |
| **Content & Progressive Disclosure** | 15% | `90.0` | ✅ |
| **Functional Correctness** | 25% | `100.0` | ✅ |
| **Skill Lift vs Baseline** | 15% | `75.0` | ✅ |
| **Trigger Quality (F1)** | 10% | `90.9` | ✅ |
| **Reliability** | 5% | `90.0` | ✅ |
| **Token & Time Efficiency** | 5% | `85.0` | ✅ |
| **Security (SkillSpector)** | 15% | `100.0` | ✅ |
| **Total Composite Score** | **100%** | **`92.6`** | **✅ PASS** |

## Benchmark Summary
- **Test Cases**: `1/1 passed`
- **Skill Lift**: `100.0% with skill` vs `75.0% without skill` (Delta: `+25.0pp`)
- **Resource Footprint**: `~0.0s execution`, `~0 tokens`

## Security Profile (NVIDIA SkillSpector)
- **Confirmed Critical**: `0`
- **Confirmed High**: `0`
- **Medium / Low**: `0 Medium`, `0 Low`
- **Suppressed False Positives**: `1`

### Security Findings Details

| Severity | Category | File:Line | Finding Description / Evidence |
| :--- | :--- | :--- | :--- |
| 🟡 `MEDIUM` | `Dangerous Code AST` | `run_evaluation.py:31` | Subprocess Invocation via subprocess.run - `  28 \|         str(output_dir),   29 \|     ]   30 \|        31 >     proc = su` |

## Regression Analysis
- **Overall Delta**: `+0.0 points`
- **Functional Delta**: `+0.0 points`
- **Security Delta**: `+0.0 points`
- **Verdict**: ✅ No regressions.
