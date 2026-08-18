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
- ✅ `matches:(?i)(USD|INR|₹|\$|87\.50|pricing)` (Regex matched output)
- ✅ `Calculates exact LLM costs in both USD and INR using current conversion rates` (Matched 8/8 keywords)
- ✅ `file:scripts/token_tracker.py` (File scripts/token_tracker.py exists)
- ✅ `matches:(?i)(claude|gemini|cursor|hermes|global)` (Regex matched output)
- ✅ `contains:SessionTelemetry` (Text found in output)
- ✅ `Auto-detects and aggregates session logs across all installed agent runtimes` (Matched 8/8 keywords)
- ✅ `file:scripts/serve_dashboard.py` (File scripts/serve_dashboard.py exists)
- ✅ `file:assets/dashboard.html` (File assets/dashboard.html exists)
- ✅ `matches:(?i)(dashboard|localhost|3000|http\.server|serve)` (Regex matched output)
- ✅ `Serves interactive responsive dashboard with per-project heatmaps and tool waterfalls` (Matched 9/9 keywords)
- ✅ `file:scripts/token_tracker.py` (File scripts/token_tracker.py exists)
- ✅ `matches:(?i)(budget|alert|warning|threshold|limit)` (Regex matched output)
- ✅ `Monitors budget limits and flags observational alerts at 80% and 100% thresholds` (Matched 8/8 keywords)
- ✅ `file:references/schemas.md` (File references/schemas.md exists)
- ✅ `contains:tool_calls` (Text found in output)
- ✅ `matches:(?i)(tool|waterfall|frequency|reasoning|tokens_per_second)` (Regex matched output)
- ✅ `Emits complete tool call waterfall analytics and throughput statistics` (Matched 8/8 keywords)
