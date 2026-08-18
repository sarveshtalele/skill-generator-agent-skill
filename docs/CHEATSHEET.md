# ⚡ Awesome Agent Skills — Complete Command & Debugging Cheat-Sheet

**Version:** 1.0.0 · **Target Audiences:** AI Agents (Claude Code, Cursor, Antigravity, Windsurf), QA Leads, and Developers  
**Specification:** [Agent Skills 1.0](https://agentskills.io) · **Security Standard:** [NVIDIA SkillSpector 17](https://github.com/nvidia/skillspector)

---

## 📑 Table of Contents
1. [🚀 1-Command Installation & Setup](#1-1-command-installation--setup)
2. [🧪 Dimension-by-Dimension Diagnostic Commands](#2-dimension-by-dimension-diagnostic-commands)
3. [🤖 AI Agent / Claude Code Auto-Fix Prompts](#3-ai-agent--claude-code-auto-fix-prompts)
4. [🎮 Complete Contributor & PR Quality Gate Workflow](#4-complete-contributor--pr-quality-gate-workflow)
5. [🛡️ Security Remediation & Baseline Whitelisting](#5-security-remediation--baseline-whitelisting)
6. [🗑️ Skill Uninstallation Matrix](#6-skill-uninstallation-matrix)

---

## 1. 🚀 1-Command Installation & Setup

### 📦 Multi-IDE Skill Installer (Zero-Install NPX)
```bash
# 1. Interactive Installer (Choose skill & target IDE)
npx github:sarveshtalele/agentkills-test install

# 2. Direct 1-Line IDE Install:
npx github:sarveshtalele/agentkills-test install skill-evaluator --target claude  # Claude Code (~/.claude/skills/)
npx github:sarveshtalele/agentkills-test install csv-analyzer --target cursor     # Cursor (.cursor/skills/)
npx github:sarveshtalele/agentkills-test install change-impact-analysis --target antigravity # Antigravity
npx github:sarveshtalele/agentkills-test install test-design-generator --target windsurf    # Windsurf

# 3. List all 15 skills in registry
npx github:sarveshtalele/agentkills-test list
```

### 🛠️ Local Evaluation Workspace Bootstrap
```bash
# Option A: 1-Command via NPX
npx github:sarveshtalele/agentkills-test setup my-workspace
cd my-workspace

# Option B: Clone via Git (macOS / Linux)
git clone https://github.com/sarveshtalele/agentkills-test.git
cd agentkills-test
./setup.sh

# Option C: Clone via Git (Windows Command Prompt / PowerShell)
git clone https://github.com/sarveshtalele/agentkills-test.git
cd agentkills-test
setup.bat
```

---

## 2. 🧪 Dimension-by-Dimension Diagnostic Commands

Run targeted diagnostic commands to isolate and debug failures across any of the 8 quality scoring dimensions:

```
┌───────────────────────────┬─────────────────────────────────────────────────────────────┬──────────────────────────────────────────┐
│ Quality Dimension         │ macOS / Linux Command                                       │ Windows Command Prompt / PowerShell      │
├───────────────────────────┼─────────────────────────────────────────────────────────────┼──────────────────────────────────────────┤
│ 1. Spec & Frontmatter     │ python -m evaluator.cli validate skills/<name>              │ .venv\Scripts\python.exe -m evaluator.cli validate skills\<name>  │
│ 2. Security (SkillSpector)│ python -m evaluator.cli security skills/<name>              │ .venv\Scripts\python.exe -m evaluator.cli security skills\<name>  │
│ 3. Functional Assertions  │ python -m evaluator.cli functional skills/<name>            │ .venv\Scripts\python.exe -m evaluator.cli functional skills\<name>│
│ 4. Baseline Skill Lift    │ python -m evaluator.cli baseline skills/<name>              │ .venv\Scripts\python.exe -m evaluator.cli baseline skills\<name>  │
│ 5. Trigger F1 Optimizer   │ python -m evaluator.cli trigger skills/<name>               │ .venv\Scripts\python.exe -m evaluator.cli trigger skills\<name>   │
│ 6. Full Single-Skill Eval │ make test-skill SKILL=skills/<name>                         │ .venv\Scripts\python.exe -m evaluator.cli all skills\<name>       │
│ 7. Full Repository Eval   │ make repo                                                   │ .venv\Scripts\python.exe -m evaluator.cli repo                    │
│ 8. Unit Test Suite (25/25)│ make test                                                   │ .venv\Scripts\python.exe -m pytest tests\                         │
└───────────────────────────┴─────────────────────────────────────────────────────────────┴──────────────────────────────────────────┘
```

---

## 3. 🤖 AI Agent / Claude Code Auto-Fix Prompts

Copy-paste these exact prompts into **Claude Code**, **Cursor**, or **Antigravity** to have the agent diagnose and auto-fix specific skill deficiencies:

### 🛡️ Fix Security & AST Issues (SkillSpector)
```text
Run ".venv\Scripts\python.exe -m evaluator.cli security skills/<skill-name>" (or "python -m evaluator.cli security skills/<skill-name>"). Review the exact line numbers and security findings. Refactor dangerous calls (e.g. os.system, shell=True) to use safe subprocess.run(..., shell=False). If the utility is a verified safe local tool, add a suppression to .skill-quality/.skillspector-baseline.yaml.
```

### 📋 Fix Specification & YAML Frontmatter
```text
Run "python -m evaluator.cli validate skills/<skill-name>". Fix frontmatter errors in SKILL.md ensuring it has valid YAML with 'name', 'description', and kebab-case directory name matching.
```

### 📉 Fix Low Trigger Quality (F1 Score < 0.80)
```text
Run "python -m evaluator.cli trigger skills/<skill-name>". Review the failed near-miss and positive queries. Refactor the 'description:' in SKILL.md to explicitly declare when to activate and when to hand off to sibling skills.
```

### 🧪 Fix Functional Assertion Failures
```text
Run "python -m evaluator.cli functional skills/<skill-name>" and inspect grading.json. Fix failing test cases in skills/<skill-name>/evals/evals.json so assertion checks pass deterministically.
```

### 🚀 Universal 1-Shot Optimization Prompt
```text
Run "python -m evaluator.cli all skills/<skill-name>". Audit all 8 dimensions and iteratively fix any spec errors, security findings, or trigger ambiguities until the skill achieves a clean 95+ PASS gate decision.
```

---

## 4. 🎮 Complete Contributor & PR Quality Gate Workflow

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                  CONTRIBUTOR LIFECYCLE PIPELINE                                  │
├───────────────────┬───────────────────┬───────────────────┬───────────────────┬──────────────────┤
│ 1. Workspace Setup│ 2. Place Skill    │ 3. Test That Skill│ 4. Commit & PR    │ 5. Bot Verdict & │
│ cd <workspace>    │ skills/<my-skill>/│ make test-skill   │ git push origin...│ Owner Merge/Block│
│                   │                   │ (or python cmd)   │                   │                  │
└───────────────────┴───────────────────┴───────────────────┴───────────────────┴──────────────────┘
```

### Step 1: Place Your Custom Skill Folder
```bash
skills/<your-skill-name>/
├── SKILL.md                 # Required: Frontmatter + instructions (<500 lines)
├── evals/                   # Test suite
│   └── evals.json
└── scripts/                 # Optional: Automation scripts
```

### Step 2: Test Your Skill Locally
```bash
# macOS / Linux
make test-skill SKILL=skills/<your-skill-name>

# Windows (Command Prompt / PowerShell)
.venv\Scripts\python.exe -m evaluator.cli all skills\<your-skill-name>
```

### Step 3: Commit & Push Pull Request
```bash
git checkout -b feat/add-<your-skill-name>
git add skills/<your-skill-name>/
git commit -m "feat(skills): add <your-skill-name>"
git push origin feat/add-<your-skill-name>
```

### Step 4: Interpret Automated PR Bot Verdict
- **`✅ PASS`**: Gate passed (Score $\ge 80.0$, 0 Critical/High security findings). Maintainer can directly **Squash & Merge**.
- **`⚠️ WARN`**: Minor non-blocking warning (e.g. Medium security finding or F1 recommendation). Maintainer can approve at discretion.
- **`❌ BLOCK`**: Hard failure (Spec violation, failing assertion, or Critical security vulnerability). Merge is blocked until remediated.

---

## 5. 🛡️ Security Remediation & Baseline Whitelisting

The evaluator audits across all **69 vulnerability patterns** defined by the **NVIDIA SkillSpector** taxonomy:

| Category Code | Domain | Common Trigger | Recommended Remediation |
| :--- | :--- | :--- | :--- |
| `SEC-01` | Prompt Injection / Jailbreak | `ignore previous instructions` | Reword to standard procedural directives. |
| `SEC-02` | Network / Exfiltration | Outbound `curl -X POST` | Declare network interface in `SKILL.md` frontmatter `allowed-tools: Network(...)`. |
| `SEC-03` | Privilege Escalation | `sudo`, `chmod 777` | Remove elevated privilege requirements. |
| `SEC-05` | Dangerous AST | `os.system()`, `eval()`, `shell=True` | Replace with `subprocess.run(["binary", "arg"], shell=False)`. |

### 🟢 Whitelisting Legitimate Offline Tools
If your skill uses a legitimate safe utility (e.g. offline HTML report generator or local git log reader):
1. Open `.skill-quality/.skillspector-baseline.yaml`
2. Add your suppression entry:
   ```yaml
   known_suppressions:
     - skill: "<your-skill-name>"
       pattern_name: "subprocess_exec"
       reason: "Legitimate execution of local CLI tool with sanitized arguments."
   ```

---

## 6. 🗑️ Skill Uninstallation Matrix

Cleanly remove installed skills from your system or AI IDEs at any time:

### Interactive Uninstaller
```bash
npx github:sarveshtalele/agentkills-test uninstall
```

### Direct 1-Line IDE Removal Commands
```bash
# 1. Claude Code (~/.claude/skills/)
npx github:sarveshtalele/agentkills-test uninstall <skill-name> --target claude

# 2. Cursor (.cursor/skills/)
npx github:sarveshtalele/agentkills-test uninstall <skill-name> --target cursor

# 3. Antigravity / Gemini CLI (~/.gemini/antigravity/skills/)
npx github:sarveshtalele/agentkills-test uninstall <skill-name> --target antigravity

# 4. Windsurf (.windsurf/skills/)
npx github:sarveshtalele/agentkills-test uninstall <skill-name> --target windsurf

# 5. Remove ALL skills from an IDE:
npx github:sarveshtalele/agentkills-test uninstall --all --target claude
```

---

## 7. ⚠️ Intentional Skill Deletion & CI/CD Override

By default, the repository CI/CD blocks PRs that reduce the total skill corpus count to prevent accidental deletions. When **intentionally** deprecating or removing a skill:

### Option A: Include `[allow-delete]` in Commit Message / PR Title (Recommended)
```bash
# 1. Remove the skill directory & scorecard
rm -rf skills/<skill-name> scorecards/<skill-name>.*

# 2. Re-generate registry
python scripts/generate_index.py

# 3. Commit with the override flag:
git commit -m "chore: deprecate <skill-name> [allow-delete]"
git push origin main
```

### Option B: Set Environment Override Variable
```bash
ALLOW_SKILL_DELETION=1 python scripts/validate_repo.py
```

