# ⚡ Skill Generator & Evaluator — Complete Command & Debugging Cheat-Sheet

**Target Environments:** Claude Code, Cursor, Antigravity, Windsurf, GitHub Copilot  
**Specification:** [Agent Skills 1.0](https://agentskills.io) · **Security Standard:** [NVIDIA SkillSpector](https://github.com/nvidia/skillspector)

---

## 📑 Table of Contents
1. [🚀 1-Command Installation & Setup](#1-1-command-installation--setup)
2. [🧪 Makefile Quick Commands](#2-makefile-quick-commands)
3. [📊 Dimension-by-Dimension Diagnostic Commands](#3-dimension-by-dimension-diagnostic-commands)
4. [🤖 AI Agent Auto-Fix Prompts](#4-ai-agent-auto-fix-prompts)
5. [🎮 Complete Contributor Quality Gate Workflow](#5-complete-contributor-quality-gate-workflow)
6. [🛡️ Security Remediation & Baseline Whitelisting](#6-security-remediation--baseline-whitelisting)

---

## 1. 🚀 1-Command Installation & Setup

### 📦 Multi-IDE Skill Installer (Zero-Install NPX)
```bash
# 1. Interactive Multi-IDE Installer
npx github:sarveshtalele/skill-generator-agent-skill install

# 2. Direct 1-Line IDE Install:
npx github:sarveshtalele/skill-generator-agent-skill install --target claude        # Claude Code (~/.claude/skills/)
npx github:sarveshtalele/skill-generator-agent-skill install --target cursor        # Cursor (.cursor/skills/)
npx github:sarveshtalele/skill-generator-agent-skill install --target antigravity   # Antigravity (~/.gemini/antigravity/skills/)
npx github:sarveshtalele/skill-generator-agent-skill install --target windsurf      # Windsurf (.windsurf/skills/)

# 3. Install a Specific Skill
npx github:sarveshtalele/skill-generator-agent-skill install skill-creator --target claude
npx github:sarveshtalele/skill-generator-agent-skill install evaluator-skill --target cursor

# 4. Uninstall
npx github:sarveshtalele/skill-generator-agent-skill uninstall
```

---

## 2. 🧪 Multi-Platform Quick Commands

### 🍎 macOS & 🐧 Linux (`Makefile`)
```bash
make help                     # Show available targets
make validate SKILL=<name>    # Check specification compliance
make security SKILL=<name>    # Run 68-pattern AST security & taint scan
make security-sarif SKILL=<name> # Run security scan with SARIF 2.1.0 output
make evaluate SKILL=<name>    # Full 8-dimension quality evaluation
make baseline SKILL=<name>    # Run evaluation with baseline LLM lift comparison
make trigger SKILL=<name>     # Run description trigger optimization loop
make package SKILL=<name>     # Bundle skill into distributable .skill ZIP
make scorecard                # Regenerate SCORECARD.md & SKILL_REGISTRY.md
make evaluate-all             # Evaluate all skills in repository
```

### 🪟 Windows PowerShell (`.\run.ps1`) — Zero-Make Required
```powershell
.\run.ps1 validate <name>       # Check specification compliance
.\run.ps1 security <name>       # Run 68-pattern AST security & taint scan
.\run.ps1 security-sarif <name> # Run security scan with SARIF 2.1.0 output
.\run.ps1 evaluate <name>       # Full 8-dimension quality evaluation
.\run.ps1 baseline <name>       # Run evaluation with baseline LLM lift comparison
.\run.ps1 trigger <name>        # Run description trigger optimization loop
.\run.ps1 package <name>        # Bundle skill into distributable .skill ZIP
.\run.ps1 scorecard             # Regenerate SCORECARD.md & SKILL_REGISTRY.md
.\run.ps1 evaluate-all          # Evaluate all skills in repository
```

### 🪟 Windows Command Prompt (`run.bat`)
```cmd
run.bat validate <name>        # Check specification compliance
run.bat security <name>        # Run 68-pattern AST security scan
run.bat evaluate <name>        # Full 8-dimension quality evaluation
run.bat baseline <name>        # Evaluation with baseline lift comparison
run.bat trigger <name>         # Run description trigger optimization loop
run.bat package <name>         # Bundle skill into distributable .skill ZIP
run.bat scorecard              # Regenerate SCORECARD.md & SKILL_REGISTRY.md
run.bat evaluate-all           # Evaluate all skills in repository
```

---

## 3. 📊 Dimension-by-Dimension Diagnostic Commands

| Quality Dimension | Command | Output File |
|:---|:---|:---|
| **1. Spec & Frontmatter** | `python skills/evaluator-skill/scripts/structural_check.py skills/<name>` | Terminal / JSON |
| **2. Security (SkillSpector)** | `python skills/evaluator-skill/scripts/security_scan.py skills/<name> --format sarif --output results.sarif` | `results.sarif` |
| **3. Functional Assertions** | `python skills/evaluator-skill/scripts/run_evaluation.py --skill skills/<name> --output ./scorecards` | `scorecards/<name>.json` |
| **4. Baseline Skill Lift** | `python skills/evaluator-skill/scripts/run_evaluation.py --skill skills/<name> --with-baseline` | `scorecards/<name>_benchmark.json` |
| **5. Trigger F1 Optimizer** | `python skills/skill-creator/scripts/run_loop.py --skill skills/<name> --iterations 5` | `optimization_report.json` |
| **6. Execution Trace** | `python skills/evaluator-skill/scripts/run_evaluation.py --skill skills/<name>` | `scorecards/<name>_trace.json` |
| **7. Distributable Package** | `python skills/skill-creator/scripts/package_skill.py --skill skills/<name> --output ./dist` | `dist/<name>.skill` |
| **8. Interactive Eval Review**| `python skills/skill-creator/eval-viewer/generate_review.py --workspace . --port 8765` | `http://localhost:8765` |

---

## 4. 🤖 AI Agent Auto-Fix Prompts

Copy-paste these prompts into **Claude Code**, **Cursor**, or **Antigravity** to diagnose and auto-fix skill deficiencies:

### 🛡️ Fix Security & AST Issues
```text
Run "python skills/evaluator-skill/scripts/security_scan.py skills/<skill-name>". Review the exact line numbers and security findings. Refactor dangerous calls (e.g. os.system, shell=True, exec) to safe standard library alternatives. If the utility is a verified safe local tool, add a suppression to .skill-quality/.skillspector-baseline.yaml.
```

### 📋 Fix Specification & Frontmatter Errors
```text
Run "python skills/evaluator-skill/scripts/structural_check.py skills/<skill-name>". Fix frontmatter errors in SKILL.md ensuring it has valid YAML with 'name', 'description', and kebab-case directory name matching.
```

### 📉 Optimize Low Trigger Quality (F1 Score < 0.80)
```text
Run "python skills/skill-creator/scripts/run_loop.py --skill skills/<skill-name>". Review the failed near-miss and positive queries. Update the 'description:' in SKILL.md to explicitly declare when to activate and when not to activate.
```

### 🧪 Fix Functional Assertion Failures
```text
Run "python skills/evaluator-skill/scripts/run_evaluation.py --skill skills/<skill-name>" and inspect scorecards/<skill-name>.json. Fix failing test cases in skills/<skill-name>/evals/evals.json so all multi-type assertion checks pass deterministically.
```

---

## 5. 🎮 Complete Contributor Quality Gate Workflow

```bash
# 1. Author or modify skill
# 2. Run local checks
make validate SKILL=<my-skill>
make security SKILL=<my-skill>
make evaluate SKILL=<my-skill>

# 3. Ensure Quality Score >= 95.0 and 0 Critical/High security issues
# 4. Regenerate registry & scorecard
make scorecard

# 5. Commit and submit PR
git add skills/ scorecards/ SCORECARD.md SKILL_REGISTRY.md
git commit -m "feat(skill): add <my-skill>"
git push origin feature/<my-skill>
```

---

## 6. 🛡️ Security Remediation & Baseline Whitelisting

If a tool legitimately uses subprocesses or regex literals that trip AST detectors, add an entry to `.skill-quality/.skillspector-baseline.yaml`:

```yaml
suppressions:
  - id: AST4
    file_glob: "scripts/my_tool.py"
    reason: "subprocess.run used with literal argv list for converter CLI"
  - id: P2
    file_glob: "scripts/formatter.py"
    reason: "Unicode emojis used in UI rendering"
```
