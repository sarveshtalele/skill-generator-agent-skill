---
name: token-telemetry
description: Use when tracking, analyzing, or optimizing Claude token usage, prompt caching hit ratios, execution latency, or API costs from session logs, transcripts, or telemetry traces. Trigger on 'token usage', 'claude telemetry', 'track tokens', or 'calculate api cost'.
allowed-tools: [run_command, view_file, write_to_file]
tags: [telemetry, token-tracking, cost-optimization, claude, prompt-caching]
metadata:
  sdlc-phase: Maintenance & Security
  version: 1.0.0
---

# ⚡ Claude Token Telemetry & Cost Analyzer

The `token-telemetry` skill enables developers and AI coding assistants to track, analyze, and optimize token usage, prompt cache hit ratios, and API expenditures across the Anthropic Claude model family (`claude-3-7-sonnet`, `claude-3-5-sonnet`, `claude-3-5-haiku`, `claude-3-opus`).

---

## 🎯 When to Use This Skill

Activate this skill when:
- Analyzing token consumption for a completed or ongoing Claude session
- Measuring prompt cache hit rates and evaluating cache efficiency
- Projecting API costs across different Claude models
- Diagnosing token spikes, context window bloat, or slow generation latencies
- Generating structured Markdown/JSON cost audit reports

---

## 🛠️ Procedural Execution Workflow

### Step 1: Locate Session Trace / Transcript
Locate the session trace JSON, JSONL transcript, or token usage dictionary.

```bash
# Example transcript paths:
~/.claude/transcripts/session-123.jsonl
scorecards/timing.json
scorecards/trace.json
```

### Step 2: Execute Deterministic Token Analysis CLI
Run the bundled offline Python token analysis engine:

```bash
python scripts/token_tracker.py <path-to-transcript> --model claude-3-7-sonnet --format markdown --output telemetry_report.md
```

Supported Arguments:
- `--model`: `claude-3-7-sonnet` (default), `claude-3-5-sonnet`, `claude-3-5-haiku`, `claude-3-opus`
- `--format`: `terminal`, `markdown`, `json`
- `--output`: File path to save output summary

### Step 3: Interpret Telemetry Metrics
Review the generated report for the 4 core telemetry indicators:
1. **Total Tokens**: Input + Output + Cache Read + Cache Write.
2. **Estimated Cost (USD)**: Calculated using official model unit pricing from [pricing_models.md](references/pricing_models.md).
3. **Cache Hit Ratio (%)**: $\frac{T_{\text{read}}}{T_{\text{in}} + T_{\text{read}}} \times 100$. Target: $\ge 75\%$.
4. **Throughput**: Tokens per second.

### Step 4: Apply Optimization Strategies
- **Low Cache Hit Ratio (<50%)**: Reorder system prompt blocks so static instructions are placed before dynamic turn context.
- **Output Token Spikes**: Enforce concise response length constraints in prompt guidelines.
- **High Input Costs**: Offload large file scanning to [scripts/token_tracker.py](scripts/token_tracker.py) (0 model tokens).

---

## 📚 Deep Resources & References

- [Model Pricing & Mathematical Formulas](references/pricing_models.md)
- [Telemetry JSON Schemas](references/schemas.md)
- [Automation CLI Script](scripts/token_tracker.py)
- [Task-Based Verification Checklist](testing.md)
- [Automated Multi-Type Assertions](evals/evals.json)
