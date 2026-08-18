# 🛠️ Skill Creator Agent Skill (`skill-creator`)

> **The Enterprise Meta-Skill Creator conforming to Agent Skills Specification v1.0**  
> *Interactively designs, scaffolds, optimizes, and bundles production-grade AI agent skills with zero-token deterministic Python tooling.*

---

## 📖 Overview

The **`skill-creator`** agent skill guides users and AI coding assistants through a structured **10-Phase Skill Creation Lifecycle**. It automatically generates canonical folder structures, Spec 1.0 compliant `SKILL.md` frontmatter, deterministic execution scripts, multi-type test assertions (`evals.json`), task-based verification checklists (`testing.md`), and distributable `.skill` packages.

---

## 📁 Where to Paste This Skill Folder

To install and use `skill-creator` anywhere, simply copy the `skill-creator/` directory into your AI coding assistant's skill directory:

### 1. Project-Level Installation (Current Repository / Project)
Place the folder in your project's root under the appropriate IDE folder:

| AI IDE / Assistant | Destination Path |
|:---|:---|
| **Claude Code** | `<your-project-root>/.claude/skills/skill-creator/` |
| **Cursor** | `<your-project-root>/.cursor/skills/skill-creator/` |
| **Google Antigravity** | `<your-project-root>/.gemini/antigravity/skills/skill-creator/` |
| **Windsurf / Cascade** | `<your-project-root>/.windsurf/skills/skill-creator/` |
| **VS Code / Cline** | `<your-project-root>/.cline/skills/skill-creator/` |

### 2. Global Installation (Available Across All Projects on Your Machine)

| AI IDE / Assistant | Global Destination Path |
|:---|:---|
| **Claude Code** | `~/.claude/skills/skill-creator/` |
| **Cursor** | `~/.cursor/skills/skill-creator/` |
| **Google Antigravity** | `~/.gemini/antigravity/skills/skill-creator/` |
| **Windsurf** | `~/.windsurf/skills/skill-creator/` |

---

## ⚡ How to Use This Skill

### In AI Chat (Natural Language)
Once the folder is placed in your IDE's skills path, activate the skill by asking:

> *"Create an agent skill for database migrations conforming to Spec 1.0"*  
> *"Scaffold a new skill for Kubernetes cluster diagnostics"*  
> *"Optimize the trigger description for my security audit skill"*

### Direct CLI Execution
You can also run the bundled scripts directly from your terminal:

```bash
# 1. Scaffold a new Spec 1.0 compliant skill
python scripts/skill_scaffolder.py my-new-skill --type implementation --output ./skills

# 2. Synthesize testing checklist and evals suite
python scripts/test_plan_orchestrator.py my-new-skill --output ./skills/my-new-skill

# 3. Optimize skill trigger description with 60/40 train/test split
python scripts/run_loop.py --skill ./skills/my-new-skill --max-iterations 5

# 4. Bundle into a distributable .skill archive
python scripts/package_skill.py --skill ./skills/my-new-skill --output ./dist
```

---

## 🔄 10-Phase Skill Creation Lifecycle

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        10-PHASE DETERMINISTIC CREATION PIPELINE                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Phase 1: Interactive Requirements Q&A (Domain, triggers, tools)                        │
│ Phase 2: Spec 1.0 Scaffolding (`skill_scaffolder.py` -> 6 canonical dirs)              │
│ Phase 3: Pushy Trigger Engineering (High recall, zero overlap)                         │
│ Phase 4: Procedural Workflow Authoring (SKILL.md <500 lines)                           │
│ Phase 5: Zero-Token Python CLI Implementation (scripts/ in standard library)           │
│ Phase 6: Deep References & Schema Contracts (references/ and assets/)                  │
│ Phase 7: Test Plan Alignment (`testing.md` checklist with user review)                 │
│ Phase 8: Multi-Type Benchmark Synthesizing (`evals/evals.json`)                        │
│ Phase 9: Trigger F1 Optimization Loop (`run_loop.py` with 60/40 split)                 │
│ Phase 10: Distributable Packaging (`package_skill.py` -> .skill archive)               │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Bundle File Layout

```
skill-creator/
├── SKILL.md                          # Spec 1.0 workflow contract (<500 lines)
├── manifest.yaml                     # Packaging manifest
├── skill-card.json                   # Enterprise metadata card
├── scripts/
│   ├── skill_scaffolder.py           # Canonical directory and file scaffolder
│   ├── test_plan_orchestrator.py     # testing.md & evals.json synthesizer
│   ├── run_loop.py                   # 60/40 trigger optimization loop
│   ├── improve_description.py        # Pushy description optimizer
│   ├── run_eval.py                   # Trigger evaluation and F1 calculator
│   └── package_skill.py              # Distributable .skill packager
├── agents/
│   ├── grader.md                     # Grader subagent prompt
│   ├── comparator.md                 # Blind A/B comparator prompt
│   └── analyzer.md                   # Post-hoc analysis subagent prompt
├── eval-viewer/
│   ├── generate_review.py            # Local review server
│   └── viewer.html                   # Interactive 2-tab benchmark viewer
└── evals/
    └── evals.json                    # Automated test benchmark
```
