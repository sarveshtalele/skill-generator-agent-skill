---
name: token-telemetry
description: Use when tracking, analyzing, or visualizing token consumption, LLM costs (USD $ & INR ₹), tool calls, and prompt caching across Claude Code, Antigravity (Gemini CLI), Cursor, and Hermes Agent for a specific project or globally. Trigger on 'token telemetry', 'track tokens', 'llm cost', 'token dashboard', or 'claude spend'.
allowed-tools: [run_command, view_file, write_to_file]
tags: [telemetry, token-tracking, cost-optimization, claude, gemini, cursor, hermes, usd-inr, observability]
metadata:
  sdlc-phase: Maintenance & Security
  version: 2.0.0
---

# ⚡ TokenTelemetry: Local Observability & Spend Dashboard

The `token-telemetry` skill provides 100% local, zero-dependency observability and spend tracking for AI coding agents (**Claude Code**, **Antigravity / Gemini CLI**, **Cursor**, **Codex**) and autonomous agents (**Hermes Agent**). It tracks tokens, tool calls, reasoning steps, and calculates real-time expenditures in both **USD ($)** and **INR (₹)**.

---

## 🎯 When to Use This Skill

Activate this skill when:
- **Project-Level Cost Audit**: Analyzing tokens, latency, and spend for a specific repository or codebase.
- **Global Machine Telemetry**: Scanning all host agent transcripts across `~/.claude`, `~/.gemini/antigravity`, `~/.cursor`, and `~/.hermes`.
- **Dual Currency Cost Reporting**: Viewing costs calculated simultaneously in **USD ($)** and **INR (₹)**.
- **Interactive Web Dashboard**: Launching a local HTTP dashboard (`http://localhost:3000`) for visual waterfall analytics.
- **Budget Alerts**: Setting spending thresholds with automated 80% warning and 100% limit indicators.

---

## 🛠️ Procedural Execution Workflow

### Step 1: Execute Project-Level or Global Analysis
Run the bundled offline Python engine to scan session logs and calculate metrics:

```bash
# 📁 1. Analyze Current Project (Markdown summary with USD & INR)
python scripts/token_tracker.py --format markdown

# 🌐 2. Analyze All Global Host Agents across the machine
python scripts/token_tracker.py --global --format markdown

# 💰 3. Custom INR Conversion Rate (Default: 87.50 INR/USD)
python scripts/token_tracker.py --inr-rate 88.00 --format terminal

# 🎯 4. Set Budget Limit with Alert Threshold ($15.00 USD)
python scripts/token_tracker.py --budget 15.00
```

### Step 2: Launch the Interactive Local Web Dashboard
To view real-time charts, per-project heatmaps, and session waterfalls:

```bash
python scripts/serve_dashboard.py --port 3000
# Or using the main CLI:
python scripts/token_tracker.py --serve --port 3000
```
Open **`http://localhost:3000`** in your browser.

### Step 3: Interpret Telemetry & Cost Breakdown
Review the generated reports for core observability signals:
1. **Total Spend**: Exact cost in both **USD ($)** and **INR (₹)** across prompt, output, cache-read, and cache-creation tokens.
2. **Prompt Cache Hit Ratio (%)**: $\frac{T_{\text{read}}}{T_{\text{in}} + T_{\text{read}}} \times 100$. (Target: $\ge 75\%$).
3. **Tool Call Waterfall**: Frequency and duration of agent tool calls (`view_file`, `run_command`, `replace_file_content`).
4. **Agent & Model Distribution**: Usage breakdown across Claude 3.7 Sonnet, Gemini 2.0 Pro, GPT-4o, and Hermes.

---

## 📚 Deep Resources & References

- [Multi-Model Pricing Catalog & Dual Currency Formulas](references/pricing_models.md)
- [Telemetry JSON Schema Contracts](references/schemas.md)
- [Interactive Dashboard Server](scripts/serve_dashboard.py)
- [Core Token Tracking CLI](scripts/token_tracker.py)
- [Standalone Dashboard HTML Asset](assets/dashboard.html)
- [Task-Based Verification Checklist](testing.md)
- [Automated Multi-Type Assertions](evals/evals.json)
