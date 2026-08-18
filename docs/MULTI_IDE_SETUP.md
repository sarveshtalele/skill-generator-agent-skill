# 💻 Multi-IDE Installation & Configuration Guide

The **`skill-generator-agent-skill`** bundle is designed to run seamlessly across all major AI coding IDEs and CLI agents conforming to the [Agent Skills Specification v1.0](https://agentskills.io/specification).

---

## 📁 Standard IDE Directory Layout Matrix

Simply copy the skill folder (`skill-creator/`, `evaluator-skill/`, or `token-telemetry/`) into the appropriate directory recognized natively by your AI coding assistant:

| IDE / Environment | Global Skill Directory (All Projects) | Workspace / Project Directory (Local Only) |
|:---|:---|:---|
| **Claude Code** | `~/.claude/skills/<skill-name>/` | `<project-root>/.claude/skills/<skill-name>/` |
| **Cursor IDE** | `~/.cursor/skills/<skill-name>/` | `<project-root>/.cursor/skills/<skill-name>/` |
| **Google Antigravity** | `~/.gemini/antigravity/skills/<skill-name>/` | `<project-root>/.gemini/skills/<skill-name>/` |
| **Codeium Windsurf** | `~/.windsurf/skills/<skill-name>/` | `<project-root>/.windsurf/skills/<skill-name>/` |
| **VS Code / Cline** | `~/.cline/skills/<skill-name>/` | `<project-root>/.cline/skills/<skill-name>/` |
| **GitHub Copilot** | N/A | `<project-root>/.github/skills/<skill-name>/` |

---

## 🛠️ Step-by-Step Installation Instructions

### Option 1: Project-Level Installation (Current Codebase)
To equip a specific repository with these capabilities without affecting other projects:

```bash
# In your target project root directory:

# For Claude Code:
mkdir -p .claude/skills
cp -r /path/to/skill-generator-agent-skill/skills/* .claude/skills/

# For Cursor IDE:
mkdir -p .cursor/skills
cp -r /path/to/skill-generator-agent-skill/skills/* .cursor/skills/

# For Google Antigravity:
mkdir -p .gemini/skills
cp -r /path/to/skill-generator-agent-skill/skills/* .gemini/skills/

# For Windsurf:
mkdir -p .windsurf/skills
cp -r /path/to/skill-generator-agent-skill/skills/* .windsurf/skills/
```

### Option 2: Global Installation (Available in Every Session on Your System)
To make the skills available globally across all terminals and projects:

```bash
# For Claude Code (macOS / Linux):
mkdir -p ~/.claude/skills
cp -r /path/to/skill-generator-agent-skill/skills/* ~/.claude/skills/

# For Cursor IDE:
mkdir -p ~/.cursor/skills
cp -r /path/to/skill-generator-agent-skill/skills/* ~/.cursor/skills/

# For Google Antigravity:
mkdir -p ~/.gemini/antigravity/skills
cp -r /path/to/skill-generator-agent-skill/skills/* ~/.gemini/antigravity/skills/

# For Windsurf:
mkdir -p ~/.windsurf/skills
cp -r /path/to/skill-generator-agent-skill/skills/* ~/.windsurf/skills/
```

---

## ⚡ How Each Assistant Detects the Skills

1. **Automatic Discovery**: When the assistant starts, it scans the configured skills folder and reads each `SKILL.md` frontmatter (`name`, `description`, `tags`).
2. **Pushy Trigger Matching**: When your prompt matches the intent (e.g. *"Create a new skill"*, *"Audit skill security"*, *"Check token telemetry"*), the assistant loads the full `SKILL.md` procedural workflow.
3. **Execution**: The assistant runs the zero-token Python scripts located inside `scripts/` locally.

---

## 🗑️ Uninstallation / Removal

To remove any skill, simply delete its folder:

```bash
# Remove from project:
rm -rf .claude/skills/<skill-name>
rm -rf .cursor/skills/<skill-name>

# Remove globally:
rm -rf ~/.claude/skills/<skill-name>
rm -rf ~/.gemini/antigravity/skills/<skill-name>
```
