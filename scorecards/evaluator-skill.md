# 🤖 Agent Skill Evaluation: `evaluator-skill`

**Overall Score**: `96.0 / 100` | **Gate Status**: `✅ PASS` | **Mode**: `Standalone Full AST`

## 📊 8-Dimension Quality Scorecard

| Dimension | Weight | Score | Status |
|:---|:---:|:---:|:---:|
| **1. Specification Compliance** | 10% | 100.0 / 100 | ✅ |
| **2. Content Quality** | 15% | 100.0 / 100 | ✅ |
| **3. Functional Correctness** | 25% | 100.0 / 100 | ✅ |
| **4. Skill Lift Delta** | 15% | 78.6 / 100 | ✅ |
| **5. Trigger Quality (F1)** | 10% | 92.0 / 100 | ✅ |
| **6. Reliability** | 5% | 100.0 / 100 | ✅ |
| **7. Efficiency** | 5% | 100.0 / 100 | ✅ |
| **8. Security (SkillSpector)** | 15% | 100.0 / 100 | ✅ |

## 🛡️ Security Findings (NVIDIA SkillSpector AST & Taint)

✅ **0 Security Vulnerabilities Found** — Clean AST and Taint analysis.

## 🧪 Benchmark Assertions

- ✅ `contains:csv-analyzer` (Text found in output)
- ✅ `contains:Specification` (Text found in output)
- ✅ `contains:SkillSpector` (Text found in output)
- ✅ `matches:(?i)(quality|score|pass|gate)` (Regex matched output)
- ✅ `Produces a comprehensive quality scorecard covering all 8 evaluation dimensions` (Matched 7/7 keywords)
- ✅ `contains:SARIF` (Text found in output)
- ✅ `matches:(?i)(finding|rule|severity|security)` (Regex matched output)
- ✅ `contains:SkillSpector` (Text found in output)
- ✅ `contains:benchmark` (Text found in output)
- ✅ `contains:lift` (Text found in output)
- ✅ `matches:(?i)(baseline|with.skill|without.skill|delta)` (Regex matched output)
- ✅ `contains:trace` (Text found in output)
- ✅ `contains:timing` (Text found in output)
- ✅ `matches:(?i)(tool.call|duration|token)` (Regex matched output)
- ✅ `contains:skill-creator` (Text found in output)
- ✅ `contains:evaluator-skill` (Text found in output)
- ✅ `matches:(?i)(pass|warn|block)` (Regex matched output)
