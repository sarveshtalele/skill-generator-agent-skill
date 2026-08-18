# 🛡️ Evaluator Agent Skill (`evaluator-skill`)

> **The Enterprise Agent Skill Auditor & Quality Gate Engine**  
> *Audits agent skills on 8 quality dimensions, measures baseline LLM lift, and executes 68-pattern AST data-flow taint tracking based on NVIDIA SkillSpector standards.*

---

## 📖 Overview

The **`evaluator-skill`** provides complete static and dynamic evaluation for AI agent skills. It verifies Spec 1.0 structural compliance, performs AST data-flow taint analysis, validates YARA signatures, benchmarks LLM lift over bare model baselines, and generates industry-standard **SARIF 2.1.0** reports and markdown quality scorecards.

---

## 📁 Where to Paste This Skill Folder

To install and use `evaluator-skill` anywhere, copy the `evaluator-skill/` directory into your AI coding assistant's skill directory:

### 1. Project-Level Installation (Current Repository / Project)

| AI IDE / Assistant | Destination Path |
|:---|:---|
| **Claude Code** | `<your-project-root>/.claude/skills/evaluator-skill/` |
| **Cursor** | `<your-project-root>/.cursor/skills/evaluator-skill/` |
| **Google Antigravity** | `<your-project-root>/.gemini/antigravity/skills/evaluator-skill/` |
| **Windsurf / Cascade** | `<your-project-root>/.windsurf/skills/evaluator-skill/` |
| **VS Code / Cline** | `<your-project-root>/.cline/skills/evaluator-skill/` |

### 2. Global Installation (Available Across All Projects on Your Machine)

| AI IDE / Assistant | Global Destination Path |
|:---|:---|
| **Claude Code** | `~/.claude/skills/evaluator-skill/` |
| **Cursor** | `~/.cursor/skills/evaluator-skill/` |
| **Google Antigravity** | `~/.gemini/antigravity/skills/evaluator-skill/` |
| **Windsurf** | `~/.windsurf/skills/evaluator-skill/` |

---

## ⚡ How to Use This Skill

### In AI Chat (Natural Language)
Once the folder is placed in your IDE's skills path, activate the skill by asking:

> *"Audit this skill for security vulnerabilities and Spec 1.0 compliance"*  
> *"Run evaluation on skills/database-migrator and generate a scorecard"*  
> *"Perform an AST taint analysis on my Python scripts"*

### Direct CLI Execution
You can also run the evaluation tools directly from your terminal:

```bash
# 1. Check Spec 1.0 structural compliance (Target: 100/100)
python scripts/structural_check.py path/to/skill

# 2. Run 68-pattern AST taint tracking and security scan
python scripts/security_scan.py path/to/skill --format json

# 3. Export SARIF 2.1.0 report for IDE security tab
python scripts/security_scan.py path/to/skill --format sarif --output ./security.sarif

# 4. Run full 8-dimension quality gate evaluation
python scripts/run_evaluation.py --skill path/to/skill --output ./scorecards
```

---

## 📊 8-Dimension Evaluation Framework

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          8-DIMENSION WEIGHTED COMPOSITE SCORING                        │
├────────────────────────────┬────────┬──────────────────────────────────────────────────┤
│ Dimension                  │ Weight │ Measurement Criteria                             │
├────────────────────────────┼────────┼──────────────────────────────────────────────────┤
│ 1. Spec Compliance         │  10%   │ Frontmatter schema, naming, links, progressive   │
│ 2. Content Quality         │  15%   │ Brevity (<500 lines), examples, error handling   │
│ 3. Functional Correctness  │  25%   │ 5-type assertion pass rate (contains, file, json)│
│ 4. Skill Lift              │  15%   │ Performance delta: With Skill vs Without Skill   │
│ 5. Trigger Quality         │  10%   │ Precision, recall, and F1 score on test queries  │
│ 6. Reliability             │   5%   │ Error rate, non-zero exits, timeout resilience   │
│ 7. Efficiency              │   5%   │ Token footprint, execution duration, throughput  │
│ 8. Security & Safety       │  15%   │ 68-pattern AST taint analysis, YARA rules, SAFE  │
└────────────────────────────┴────────┴──────────────────────────────────────────────────┘
```

---

## 📂 Bundle File Layout

```
evaluator-skill/
├── SKILL.md                          # Spec 1.0 workflow contract (<500 lines)
├── manifest.yaml                     # Packaging manifest
├── skill-card.json                   # Enterprise metadata card
├── scripts/
│   ├── run_evaluation.py             # Main 8-dimension evaluation orchestrator
│   ├── structural_check.py           # Spec 1.0 structural compliance linter
│   ├── security_scan.py              # 68-pattern AST & Taint security scanner
│   ├── taint_tracker.py              # AST data-flow source-to-sink tracer
│   ├── yara_scanner.py               # Pure-Python YARA rule engine
│   ├── assertion_engine.py           # 5-type multi-assertion grader
│   ├── baseline_runner.py            # Baseline LLM lift comparison runner
│   ├── trace_capture.py              # Execution trace and timing recorder
│   └── sarif_report.py               # SARIF 2.1.0 report generator
├── assets/
│   └── agent_skills.yar              # Threat signatures for agent skills
└── references/
    ├── scoring_formulas.md           # Mathematical formulas and quality gates
    └── security_patterns.md          # 68 threat patterns catalog
```
