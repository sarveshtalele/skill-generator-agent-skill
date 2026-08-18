# 💻 Multi-IDE Installation & Configuration Guide

The **`skill-generator-agent-skill`** bundle is designed to run seamlessly across all major AI coding IDEs and CLI agents conforming to the [Agent Skills Specification v1.0](https://agentskills.io/specification).

---

## ⚡ 1-Click Multi-IDE Setup (NPX)

The fastest way to install or update the skills across any IDE on macOS, Linux, or Windows:

```bash
# 1. Interactive Installer (Select IDE and Skills)
npx github:sarveshtalele/skill-generator-agent-skill install
```

### Interactive Prompt Flow:
1. **Target IDE Selection**: Choose between Claude Code, Cursor, Antigravity, Windsurf, or Copilot.
2. **Scope Selection**: Choose between **Project-level** (inside a specific repo) or **Global-level** (`~/.<ide>/skills/`).
3. **Project Directory**: Confirm or customize target workspace directory (defaults to current working directory).

### Direct 1-Line Commands (Project vs Global Scope):

```bash
# 📁 Project-Level Installation (Current Workspace / Repo) [Recommended]
npx github:sarveshtalele/skill-generator-agent-skill install --target claude --scope project
npx github:sarveshtalele/skill-generator-agent-skill install --target cursor --dir ./my-project
npx github:sarveshtalele/skill-generator-agent-skill install --target antigravity --project
npx github:sarveshtalele/skill-generator-agent-skill install --target windsurf --dir /path/to/repo

# 🌐 Global Installation (Available across all projects in user home dir)
npx github:sarveshtalele/skill-generator-agent-skill install --target claude --global
npx github:sarveshtalele/skill-generator-agent-skill install --target antigravity --global
```

---

## 📁 Standard IDE Directory Layout Matrix

When installed, skills are copied into standard locations recognized natively by each IDE runtime:

| IDE / Environment | Global Skill Directory | Workspace / Project Directory |
|:---|:---|:---|
| **Claude Code** | `~/.claude/skills/<skill-name>/` | `.claude/skills/<skill-name>/` |
| **Cursor IDE** | `~/.cursor/skills/<skill-name>/` | `.cursor/skills/<skill-name>/` |
| **Google Antigravity** | `~/.gemini/antigravity/skills/<skill-name>/` | `.gemini/skills/<skill-name>/` |
| **Codeium Windsurf** | `~/.windsurf/skills/<skill-name>/` | `.windsurf/skills/<skill-name>/` |
| **GitHub Copilot** | N/A | `.github/skills/<skill-name>/` |

---

## 🛠️ Manual Installation (Air-Gapped & Enterprise Workspaces)

For secure enterprise environments without direct internet/npm access:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sarveshtalele/skill-generator-agent-skill.git
   cd skill-generator-agent-skill
   ```

2. **Copy to Your Desired Target**:
   ```bash
   # For Claude Code (macOS / Linux):
   mkdir -p ~/.claude/skills
   cp -r skills/skill-creator ~/.claude/skills/
   cp -r skills/evaluator-skill ~/.claude/skills/

   # For Cursor (Project-level):
   mkdir -p .cursor/skills
   cp -r skills/skill-creator .cursor/skills/
   cp -r skills/evaluator-skill .cursor/skills/

   # For Google Antigravity:
   mkdir -p ~/.gemini/antigravity/skills
   cp -r skills/skill-creator ~/.gemini/antigravity/skills/
   cp -r skills/evaluator-skill ~/.gemini/antigravity/skills/
   ```

---

## 🗑️ Uninstallation

Remove installed skills at any time:

```bash
# Interactive uninstaller
npx github:sarveshtalele/skill-generator-agent-skill uninstall

# Direct removal by target IDE
npx github:sarveshtalele/skill-generator-agent-skill uninstall --target claude
npx github:sarveshtalele/skill-generator-agent-skill uninstall skill-creator --target cursor
```
