# 🤖 Agent Skills Creation & Quality Task Checklist

**File:** `docs/Agent_skills-checklist.md`  
**Purpose:** An actionable, step-by-step task checklist designed for developers and AI coding agents (Claude Code, Cursor, Antigravity, GitHub Copilot, Windsurf, Roo Code). When this checklist is provided to an AI agent, it will systematically guide the creation of an end-to-end production-grade Agent Skill achieving a **95+ quality score and zero security warnings**.

---

## 📑 Step-by-Step Task Overview

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 AGENT SKILL CREATION WORKFLOW (8 TASKS)                                │
├──────┬──────────────────────────────────────────┬──────────────────────────────────────────────────────┤
│ Task │ Phase & Objective                        │ Primary Artifact Created / Validated                 │
├──────┼──────────────────────────────────────────┼──────────────────────────────────────────────────────┤
│ 1    │ Directory Setup & Standard Structure     │ skills/<skill-name>/ with 4 subfolders               │
│ 2    │ Spec 1.0 YAML Frontmatter & Discovery    │ SKILL.md (name, description, tags, allowed-tools)    │
│ 3    │ Progressive Disclosure Implementation    │ references/, scripts/, assets/, templates/           │
│ 4    │ Enterprise Metadata Card & Manifest      │ skill-card.json and manifest.yaml                    │
│ 5    │ Test Suite Construction & Grounding      │ evals/evals.json (deterministic & semantic asserts)  │
│ 6    │ AST Security & NVIDIA SkillSpector Audit │ 0 Critical, 0 High findings (.skillspector-baseline) │
│ 7    │ 1-Command Verification & Gating Check    │ python -m evaluator.cli skill skills/<skill-name>    │
│ 8    │ Registry Generation & PR Submission      │ python scripts/generate_index.py & Git commit        │
└──────┴──────────────────────────────────────────┴──────────────────────────────────────────────────────┘
```

---

## 🛠️ Task 1: Initialize Directory & Standard Layout

Create the required isolated folder structure under `skills/<skill-name>`:

- [ ] **Task 1.1**: Choose a kebab-case skill name matching regex `^[a-z0-9]+(-[a-z0-9]+)*$` (e.g. `api-contract-linter`).
- [ ] **Task 1.2**: Create the standard 4 subdirectories and `evals/` test directory:
  ```bash
  mkdir -p skills/<skill-name>/{assets,references,scripts,templates,evals}
  ```
- [ ] **Task 1.3**: Confirm directory layout:
  ```
  skills/<skill-name>/
  ├── assets/             # JSON schemas, static fixtures, diagram templates
  ├── references/         # In-depth architectural guidelines, rulebooks, specs
  ├── scripts/            # Python / Node.js automation scripts & engines
  ├── templates/          # Structured output markdown templates & reports
  ├── evals/              # Evaluation suites (evals.json)
  ├── SKILL.md            # Agent Skills Spec 1.0 definition
  ├── manifest.yaml       # Packaging manifest with runtime & tool access
  └── skill-card.json     # Enterprise Skill Card metadata
  ```

---

## 📝 Task 2: Author `SKILL.md` (Frontmatter & Progressive Disclosure)

Author the primary `SKILL.md` strictly adhering to the **Agent Skills Specification v1.0**:

- [ ] **Task 2.1**: Write YAML frontmatter bounded by `---`:
  ```yaml
  ---
  name: <skill-name>
  description: A concise description explaining WHAT the skill does and WHEN the agent must trigger it.
  metadata:
    sdlc: Implementation    # Requirements | Architecture | Implementation | Testing | Security | Maintenance
    tags: [code-analysis, automation, testing]
  compatibility: "Python 3.8+"
  allowed-tools: "Read, Bash(python scripts/*.py:*)"
  ---
  ```
- [ ] **Task 2.2**: Validate Frontmatter Constraints:
  - `name`: Matches folder name strictly ($1 \le \text{length} \le 64$).
  - `description`: Non-vacuous ($10 \le \text{length} \le 1024$), clear trigger conditions.
- [ ] **Task 2.3**: Author Body Sections (Strict budget: $\le 500$ lines):
  - [ ] `## Overview` or `## Purpose`: Core intent and problem solved.
  - [ ] `## Workflow`: Deterministic step-by-step procedural contract for the AI agent.
  - [ ] `## Examples`: Concrete input $\to$ output demonstration with sample prompts.
  - [ ] `## Error Handling & Gotchas`: Edge cases, failure fallbacks, and recovery modes.
- [ ] **Task 2.4**: Zero Orphaned Links: Ensure every file in `references/`, `scripts/`, `assets/`, and `templates/` is explicitly referenced in `SKILL.md`.

---

## ⚡ Task 3: Build Scripts, References, and Templates

- [ ] **Task 3.1: Bundled Scripts (`scripts/`)**:
  - Implement deterministic Python 3.8+ scripts.
  - Non-interactive execution: Ensure scripts read arguments via `argparse` or environment variables (no interactive `input()` prompts).
  - Clean exit codes: Exit with code `0` on success, non-zero on failure.
- [ ] **Task 3.2: Deep References (`references/`)**:
  - Store detailed rules, API schemas, and reference material that the agent reads on-demand.
- [ ] **Task 3.3: Output Templates (`templates/`)**:
  - Create markdown templates (e.g. `report_template.md`) that standardise the output format.

---

## 🪪 Task 4: Create `manifest.yaml` and `skill-card.json`

- [ ] **Task 4.1: Create `manifest.yaml`**:
  ```yaml
  name: <skill-name>
  display_name: <Skill Display Name> Skill
  version: "1.0.0"
  description: <Skill description>
  author: <Author Name>
  license: MIT
  category: code-analysis
  tags:
    - <skill-name>
    - sdlc
    - agent-skills
  runtime:
    engine: python
    min_version: "3.8"
    entry_point: scripts/<skill_name_snake>_skill.py
    dependencies: []
  tools:
    - run_in_terminal
    - read_file
    - file_search
    - grep_search
  entry_files:
    skill_definition: SKILL.md
  ```

- [ ] **Task 4.2: Create `skill-card.json`**:
  ```json
  {
    "skill_card": {
      "starterkit_id": "<skill-name>",
      "name": "<Skill Display Name> Skill",
      "description": "<Skill description>",
      "origin": {
        "BG": "BFSI",
        "ISU": "APAC",
        "Account": "Enterprise"
      },
      "maintainers": [
        {
          "name": "<Author Name>",
          "contact": "<author-email>"
        }
      ],
      "version": "1.0.0",
      "status": "verified",
      "technology": ["Python", "JavaScript", "Git", "JSON"],
      "specialization": {
        "primary": "<skill_specialization>",
        "domain_specific": ["SDLC Automation", "Quality Assurance"]
      },
      "tasks": [
        {
          "name": "Execute <skill-name>",
          "description": "Automates procedural execution for <skill-name> deterministically.",
          "input_schema": "Task prompt and repository context.",
          "output_schema": "Formatted artifacts and structured reports.",
          "async": true
        }
      ],
      "documentation": {
        "readme": "README.md",
        "howto": "QuickStart.md",
        "changelog": "Initial verified release."
      },
      "supported_harness": ["GitHub Copilot", "Claude Code", "Cursor", "Antigravity", "Windsurf"],
      "tested_harness": ["GitHub Copilot", "Claude Code", "Cursor", "Antigravity"]
    }
  }
  ```

---

## 🧪 Task 5: Author Evaluation Test Suite (`evals/evals.json`)

Construct ground-truth test cases under `skills/<skill-name>/evals/evals.json`:

- [ ] **Task 5.1**: Schema Structure:
  ```json
  {
    "skill_name": "<skill-name>",
    "evals": [
      {
        "id": "eval-001",
        "prompt": "Run <skill-name> against the repository to perform analysis.",
        "expected_output": "The analysis report containing findings and recommendations.",
        "files": [],
        "assertions": [
          "contains:findings",
          "contains:recommendations",
          "matches:(?i)(analysis|report|summary)"
        ]
      }
    ]
  }
  ```
- [ ] **Task 5.2**: Test Assertion Coverage:
  - `contains:<concept>`: Semantic concept validation.
  - `matches:<regex>`: Strict pattern verification.
  - `file:<filename>`: Verifies generated artifact file presence.
  - `json:<path>.<key>`: Structured JSON value assertions.

---

## 🛡️ Task 6: Audit Against NVIDIA SkillSpector (17 Security Categories)

Ensure your skill code and instructions pass all 17 security vulnerability checks:

- [ ] **SEC-01 (Prompt Injection & Anti-Refusal)**: Zero prompt escapes, `ignore previous instructions`, or DAN jailbreaks.
- [ ] **SEC-02 (Data Exfiltration)**: No hardcoded external HTTP POST/tunneling URLs.
- [ ] **SEC-03 (Privilege Escalation)**: Zero `sudo`, `chmod 777`, or `setuid` calls.
- [ ] **SEC-04 (Supply Chain Safety)**: No unpinned package downloads or `curl | bash` executions.
- [ ] **SEC-05 (Dangerous Python AST)**:
  - [ ] No `eval()`, `exec()`, or `__import__()`.
  - [ ] No `os.system()` or `subprocess(..., shell=True)`.
  - [ ] No unsafe deserialization (`pickle.loads()`, `yaml.unsafe_load()`).
- [ ] **Task 6.1: Baseline Whitelisting (if applicable)**: If legitimate CLI wrappers exist (e.g. running local `git diff`), add a suppression to `.skill-quality/.skillspector-baseline.yaml`:
  ```yaml
  suppressions:
    - skill: "<skill-name>"
      rule_id: "DA_SUBPROCESS"
      reason: "Benign: Safe local CLI wrapper with sanitized arguments."
  ```

---

## 🚀 Task 7: Execute 1-Command Local Evaluation

Run the quality evaluation suite:

```bash
# Evaluate your specific skill:
.venv/bin/python -m evaluator.cli skill skills/<skill-name> --output-dir scorecards
```

- [ ] **Task 7.1: Verify Scorecard Results**:
  - [ ] Specification Compliance = `100.0%`
  - [ ] Functional Correctness $\ge `80.0%`$
  - [ ] Skill Lift Delta $\ge `70.0%`$
  - [ ] Trigger Quality ($F_1$) $\ge `80.0%`$
  - [ ] Security (SkillSpector) = `100.0%` (0 Critical, 0 High)
  - [ ] **Gate Decision**: `✅ PASS` (Quality Score $\ge 80.0 / 100$)

---

## 📦 Task 8: Update Registry, Validate Repository & Submit PR

- [ ] **Task 8.1: Regenerate Master Index and Dashboard**:
  ```bash
  uv run python scripts/generate_index.py
  ```
- [ ] **Task 8.2: Run Full Repository Verification**:
  ```bash
  uv run python scripts/validate_repo.py && uv run pytest tests/
  ```
  *(All checks and 25 unit tests must pass).*
- [ ] **Task 8.3: Commit and Push**:
  ```bash
  git checkout -b feat/add-<skill-name>
  git add skills/<skill-name>/ scorecards/<skill-name>.* README.md SKILL_REGISTRY.md
  git commit -m "feat(skills): add <skill-name> with 95+ PASS scorecard"
  git push origin feat/add-<skill-name>
  ```

---

## 🤖 Instructions for AI Coding Assistants (Claude Code, Cursor, Antigravity)

When a user prompts you with:
> *"Create a new skill for `<purpose>` using `docs/Agent_skills-checklist.md`"*

Follow this exact sequence:
1. Execute **Task 1** through **Task 5** in order.
2. Run the security scan and verification in **Task 6** & **Task 7**.
3. Inspect `scorecards/<skill-name>.md`. If any score is below 90 or shows `WARN`/`BLOCK`, refine `evals.json` and `SKILL.md` until it achieves `✅ PASS`.
4. Execute **Task 8** to regenerate `SKILL_REGISTRY.md` and verify pytest tests.
