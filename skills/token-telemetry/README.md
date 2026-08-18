# ⚡ TokenTelemetry Agent Skill (`token-telemetry`)

> **Local Multi-Agent Observability, Token Tracking & Spend Dashboard**  
> *Replicates full `tokentelemetry` local observability across Claude Code, Gemini CLI, Cursor, Hermes Agent, and Codex with dual-currency pricing in USD ($) and INR (₹).*

---

## 📖 Overview

The **`token-telemetry`** agent skill provides 100% local, zero-dependency observability for AI coding agents and autonomous workflows. It parses session logs, transcripts, and `history.jsonl` files to measure token consumption, prompt cache hit ratios, throughput (tps), tool call waterfalls, and exact API costs simultaneously in **USD ($)** and **INR (₹)**.

---

## 📁 Where to Paste This Skill Folder

To install and use `token-telemetry` anywhere, copy the `token-telemetry/` directory into your AI coding assistant's skill directory:

### 1. Project-Level Installation (Current Repository / Project)

| AI IDE / Assistant | Destination Path |
|:---|:---|
| **Claude Code** | `<your-project-root>/.claude/skills/token-telemetry/` |
| **Cursor** | `<your-project-root>/.cursor/skills/token-telemetry/` |
| **Google Antigravity** | `<your-project-root>/.gemini/antigravity/skills/token-telemetry/` |
| **Windsurf / Cascade** | `<your-project-root>/.windsurf/skills/token-telemetry/` |
| **VS Code / Cline** | `<your-project-root>/.cline/skills/token-telemetry/` |

### 2. Global Installation (Available Across All Projects on Your Machine)

| AI IDE / Assistant | Global Destination Path |
|:---|:---|
| **Claude Code** | `~/.claude/skills/token-telemetry/` |
| **Cursor** | `~/.cursor/skills/token-telemetry/` |
| **Google Antigravity** | `~/.gemini/antigravity/skills/token-telemetry/` |
| **Windsurf** | `~/.windsurf/skills/token-telemetry/` |

---

## ⚡ How to Use This Skill

### In AI Chat (Natural Language)
Once the folder is placed in your IDE's skills path, activate the skill by asking:

> *"Show token telemetry and spend for this project in USD and INR"*  
> *"Launch the local token telemetry dashboard on port 3000"*  
> *"How many prompt cache hits did I get across my recent Claude sessions?"*  
> *"Set a spending budget of $10.00 and check my threshold status"*

### Direct CLI Execution
You can also run the telemetry engine directly from your terminal:

```bash
# 1. Terminal report for current project (Dual USD & INR)
python scripts/token_tracker.py --format terminal

# 2. Machine-wide audit across all agents (~/.claude, ~/.gemini, ~/.cursor, ~/.hermes)
python scripts/token_tracker.py --global --format markdown

# 3. Custom INR exchange rate (Default: 87.50 INR/USD)
python scripts/token_tracker.py --inr-rate 88.00

# 4. Set budget limit with automated 80% & 100% alerts
python scripts/token_tracker.py --budget 15.00

# 5. Launch interactive web dashboard on http://localhost:3000
python scripts/serve_dashboard.py --port 3000
```

---

## 💰 Dual-Currency Pricing Model (USD $ & INR ₹)

| Model Family | Model Identifier | Input Rate ($ / ₹ per 1M) | Output Rate ($ / ₹ per 1M) | Cache Read ($ / ₹ per 1M) |
|:---|:---|:---:|:---:|:---:|
| **Claude 3.7 Sonnet** | `claude-3-7-sonnet` | **$3.00** *(₹262.50)* | **$15.00** *(₹1,312.50)* | **$0.30** *(₹26.25)* |
| **Claude 3.5 Haiku** | `claude-3-5-haiku` | **$0.80** *(₹70.00)* | **$4.00** *(₹350.00)* | **$0.08** *(₹7.00)* |
| **Gemini 2.0 Pro** | `gemini-2-0-pro` | **$1.25** *(₹109.38)* | **$5.00** *(₹437.50)* | **$0.31** *(₹27.13)* |
| **Gemini 2.0 Flash** | `gemini-2-0-flash` | **$0.10** *(₹8.75)* | **$0.40** *(₹35.00)* | **$0.025** *(₹2.19)* |
| **GPT-4o** | `gpt-4o` | **$2.50** *(₹218.75)* | **$10.00** *(₹875.00)* | **$1.25** *(₹109.38)* |
| **Hermes 3 70B** | `hermes-3-llama-3-1-70b` | **$0.40** *(₹35.00)* | **$0.80** *(₹70.00)* | **$0.10** *(₹8.75)* |

---

## 📂 Bundle File Layout

```
token-telemetry/
├── SKILL.md                          # Spec 1.0 workflow contract (<500 lines)
├── README.md                         # Setup & usage documentation
├── manifest.yaml                     # Packaging manifest
├── skill-card.json                   # Enterprise metadata card
├── testing.md                        # Task-based verification checklist
├── assets/
│   └── dashboard.html                # Standalone HTML dashboard template
├── scripts/
│   ├── token_tracker.py              # Core parser, metrics engine & CLI
│   └── serve_dashboard.py            # Local HTTP dashboard server (port 3000)
├── references/
│   ├── pricing_models.md             # Dual-currency rates & formulas catalog
│   └── schemas.md                    # JSON schema contracts
└── evals/
    └── evals.json                    # Automated test benchmark
```
