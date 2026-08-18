# Skill Generator & Evaluator Agent Skill Bundle 🤖⚡

An enterprise-grade package containing the **`skill-creator`** and **`evaluator-skill`** agent skills. Conforms 100% to the [Agent Skills Specification v1.0](https://agentskills.io/specification) and [NVIDIA SkillSpector](https://github.com/nvidia/skillspector) security standards.

Install directly into **Claude Code**, **Cursor**, **Antigravity**, **Windsurf**, or **GitHub Copilot** with a single `npx` command.

---

## 📦 Bundled Skills

```
┌─────────────────┬────────────────┬──────────────────────────┬────────────────────────────────────────────────────────┐
│ Skill Name      │ Quality Score  │ Status                   │ Capabilities & Description                             │
├─────────────────┼────────────────┼──────────────────────────┼────────────────────────────────────────────────────────┤
│ skill-creator   │   96.1 / 100   │ ✅ PASS (SkillSpector)    │ Interactive Q&A chatbot skill creator. Builds Spec 1.0 │
│                 │                │                          │ skills, custom SDD bundles, testing.md, & evals.json   │
├─────────────────┼────────────────┼──────────────────────────┼────────────────────────────────────────────────────────┤
│ evaluator-skill │   92.6 / 100   │ ✅ PASS (SkillSpector)    │ Full 8-dimension quality & NVIDIA SkillSpector AST     │
│                 │                │                          │ security scanner producing Markdown & JSON scorecards  │
└─────────────────┴────────────────┴──────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### 1. Interactive Multi-IDE Installer
```bash
npx github:sarveshtalele/skill-generator-agent-skill install
```

### 2. Direct 1-Line IDE Commands
```bash
# 1. Install into Claude Code (~/.claude/skills/)
npx github:sarveshtalele/skill-generator-agent-skill install --target claude

# 2. Install into Cursor (.cursor/skills/)
npx github:sarveshtalele/skill-generator-agent-skill install --target cursor

# 3. Install into Antigravity / Gemini CLI (~/.gemini/antigravity/skills/)
npx github:sarveshtalele/skill-generator-agent-skill install --target antigravity

# 4. Install into Windsurf (.windsurf/skills/)
npx github:sarveshtalele/skill-generator-agent-skill install --target windsurf
```

### 3. Install a Specific Skill
```bash
# Install only skill-creator into Claude Code
npx github:sarveshtalele/skill-generator-agent-skill install skill-creator --target claude

# Install only evaluator-skill into Cursor
npx github:sarveshtalele/skill-generator-agent-skill install evaluator-skill --target cursor
```

---

## 🗑️ Uninstallation

```bash
# Interactive uninstaller
npx github:sarveshtalele/skill-generator-agent-skill uninstall

# Direct removal from an IDE
npx github:sarveshtalele/skill-generator-agent-skill uninstall --target claude
npx github:sarveshtalele/skill-generator-agent-skill uninstall skill-creator --target cursor
```

---

## 🔄 End-to-End Skill Creation Workflow

When you ask your AI assistant (`Claude Code`, `Cursor`, `Antigravity`):
> *"Create a new skill for database migration auditing"*

The **`skill-creator`** skill triggers and executes:
1. **Interactive Q&A**: Asks 3-4 clarifying technical questions about requirements, scripts, triggers, and tooling.
2. **Implementation Plan**: Formulates an architectural blueprint and asks for your approval.
3. **Deterministic Scaffolding**: Scaffolds `skills/<name>/` (`SKILL.md`, `scripts/`, `references/`, `manifest.yaml`, `skill-card.json`).
4. **Task-Based `testing.md` Checklist**: Emits a unit & E2E verification plan.
5. **User Test Alignment**: Synthesizes `evals/evals.json` upon your confirmation.
6. **Automated Evaluation (`evaluator-skill`)**: Audits against 17 NVIDIA SkillSpector categories, asserts functional accuracy, and delivers a 95+ Scorecard.

---

## 📁 Repository Structure

```
skill-generator-agent-skill/
├── bin/
│   └── install.js                     # Multi-IDE NPX installer / uninstaller
├── skills/
│   ├── skill-creator/                 # Autonomous & Interactive Q&A Skill Creator
│   │   ├── SKILL.md                   # Spec 1.0 definition
│   │   ├── scripts/skill_scaffolder.py
│   │   ├── scripts/test_plan_orchestrator.py
│   │   ├── manifest.yaml
│   │   ├── skill-card.json
│   │   └── evals/evals.json
│   └── evaluator-skill/               # 8-Dimension Quality & Security Evaluator
│       ├── SKILL.md                   # Spec 1.0 definition
│       ├── scripts/run_evaluation.py
│       ├── manifest.yaml
│       ├── skill-card.json
│       └── evals/evals.json
├── scorecards/
│   ├── skill-creator.md & .json       # Score: 96.1/100 (✅ PASS)
│   └── evaluator-skill.md & .json     # Score: 92.6/100 (✅ PASS)
├── docs/
│   ├── Agent_skills-checklist.md      # Actionable 8-task creation guide
│   └── CHEATSHEET.md                  # Complete command cheat-sheet
└── package.json                       # NPX packaging descriptor
```

---

## 📄 License
MIT © [Sarvesh Talele](https://github.com/sarveshtalele)
