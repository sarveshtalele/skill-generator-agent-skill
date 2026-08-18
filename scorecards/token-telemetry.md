# 🤖 Agent Skill Evaluation: `token-telemetry`

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

- ✅ `file:scripts/token_tracker.py` (File scripts/token_tracker.py exists)
- ✅ `file:references/pricing_models.md` (File references/pricing_models.md exists)
- ✅ `contains:token-telemetry` (Text found in output)
- ✅ `matches:(?i)(claude|token|cost|pricing|cache)` (Regex matched output)
- ✅ `Calculates exact USD API cost and prompt cache hit ratio` (Matched 6/6 keywords)
- ✅ `file:references/pricing_models.md` (File references/pricing_models.md exists)
- ✅ `contains:claude-3-7-sonnet` (Text found in output)
- ✅ `contains:claude-3-5-haiku` (Text found in output)
- ✅ `matches:(?i)(3.00|0.80|15.00|cache)` (Regex matched output)
- ✅ `Provides accurate per-million pricing rates for all Claude model families` (Matched 8/8 keywords)
- ✅ `file:references/schemas.md` (File references/schemas.md exists)
- ✅ `contains:TokenRecord` (Text found in output)
- ✅ `matches:(?i)(input_tokens|output_tokens|cache_hit_ratio)` (Regex matched output)
- ✅ `Emits compliant JSON telemetry record with all required metrics` (Matched 8/8 keywords)
- ✅ `contains:SKILL.md` (Text found in output)
- ✅ `matches:(?i)(cache|ratio|optimization|strategy)` (Regex matched output)
- ✅ `Recommends placing static instructions before dynamic turn context to maximize cache hits` (Matched 11/11 keywords)
- ✅ `file:scripts/token_tracker.py` (File scripts/token_tracker.py exists)
- ✅ `matches:(?i)(table|breakdown|throughput|total)` (Regex matched output)
- ✅ `Executes deterministic token analysis CLI and outputs structured Markdown breakdown` (Matched 8/8 keywords)
