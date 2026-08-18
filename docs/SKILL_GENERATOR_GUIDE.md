# 📚 Skill-Generator Agent Skill Documentation & Evaluation Guide

**Repository:** [`https://github.com/sarveshtalele/skill-generator-agent-skill.git`](https://github.com/sarveshtalele/skill-generator-agent-skill.git)  
**Spec Standard:** [Agent Skills Specification v1.0](https://agentskills.io/specification)  
**Security Standard:** [NVIDIA SkillSpector 17-Category AST Taxonomy](https://github.com/nvidia/skillspector)  
**Target Environments:** Claude Code, Cursor, Antigravity, Windsurf, GitHub Copilot  

---

## 📑 Table of Contents
1. [Executive Overview & Package Architecture](#1-executive-overview--package-architecture)
2. [Multi-IDE NPX Installation Matrix](#2-multi-ide-npx-installation-matrix)
3. [Deep-Dive: `skill-creator` Agent Skill](#3-deep-dive-skill-creator-agent-skill)
4. [Deep-Dive: `evaluator-skill` Agent Skill](#4-deep-dive-evaluator-skill-agent-skill)
5. [Evaluation Framework Comparison & Gap Analysis](#5-evaluation-framework-comparison--gap-analysis)
6. [Remediation & Enhancements Added to `evaluator-skill`](#6-remediation--enhancements-added-to-evaluator-skill)
7. [Step-by-Step Skill Authoring & Gating Walkthrough](#7-step-by-step-skill-authoring--gating-walkthrough)

---

## 1. Executive Overview & Package Architecture

The **`skill-generator-agent-skill`** repository is a standalone, production-grade agent skill bundle designed to automate the authoring, scaffolding, testing, and evaluation of AI Agent Skills.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               SKILL-GENERATOR AGENT SKILL SUITE                                  │
├─────────────────────────────────────────┬────────────────────────────────────────────────────────┤
│ 1. skill-creator (Authoring & Testing)  │ 2. evaluator-skill (Quality & Security Audit)          │
├─────────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ • Interactive Q&A discovery chatbot     │ • 8 Weighted Quality Dimensions (RAGAS Mapped)         │
│ • Deterministic Spec 1.0 scaffolding    │ • 17 NVIDIA SkillSpector AST Vulnerability Categories  │
│ • Custom 4-phase SDD bundle support     │ • Hybrid Native CLI + Standalone Static Runner         │
│ • Task-based testing.md checklist plan  │ • Full Markdown (.md) and JSON Scorecard Generation    │
│ • User-confirmed evals/evals.json test  │ • PR Quality Gating Matrix (PASS / WARN / BLOCK)       │
└─────────────────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 2. Multi-IDE NPX Installation Matrix

Any developer or AI agent can install this bundle into their local IDE with 1 command:

```bash
# 1. Interactive Installer (Prompt-Driven)
npx github:sarveshtalele/skill-generator-agent-skill install

# 2. Claude Code (~/.claude/skills/)
npx github:sarveshtalele/skill-generator-agent-skill install --target claude

# 3. Cursor in current project (.cursor/skills/)
npx github:sarveshtalele/skill-generator-agent-skill install --target cursor

# 4. Antigravity / Gemini CLI (~/.gemini/antigravity/skills/)
npx github:sarveshtalele/skill-generator-agent-skill install --target antigravity

# 5. Windsurf in current project (.windsurf/skills/)
npx github:sarveshtalele/skill-generator-agent-skill install --target windsurf
```

---

## 3. Deep-Dive: `skill-creator` Agent Skill

### Behavior Contract & Interactive Lifecycle:
1. **Interactive Q&A Discovery**: When prompted with a skill idea, the agent asks 4 targeted technical questions (SDLC phase, offline scripts vs LLM prompts, trigger intent, dependencies).
2. **Implementation Plan & Approval Gate**: Formulates an architectural blueprint and **pauses execution** until the user confirms `Approve`.
3. **Deterministic Scaffolding**:
   - Single Skill: `python scripts/skill_scaffolder.py --name <name> --sdlc <phase>`
   - 4-Phase SDD Bundle: `python scripts/skill_scaffolder.py --name <prefix> --bundle sdd`
4. **Task-Based `testing.md` Matrix**: Emits a unit & E2E testing checklist.
5. **Test Synthesis**: Writes `evals/evals.json` upon user confirmation.
6. **Automated Evaluation Hand-Off**: Invokes `evaluator-skill` to achieve a 95+ score.

---

## 4. Deep-Dive: `evaluator-skill` Agent Skill

Evaluates any target skill across **8 mathematical quality dimensions**:

$$S = 0.10 S_{\text{spec}} + 0.15 S_{\text{content}} + 0.25 S_{\text{func}} + 0.15 S_{\text{lift}} + 0.10 S_{\text{trig}} + 0.05 S_{\text{rel}} + 0.05 S_{\text{eff}} + 0.15 S_{\text{sec}}$$

```
┌──────────────────────────────┬────────┬────────────────────────────────────────────────────────┐
│ Quality Dimension            │ Weight │ Evaluation Scope & Gating Rules                        │
├──────────────────────────────┼────────┼────────────────────────────────────────────────────────┤
│ 1. Specification Compliance  │  10%   │ Frontmatter YAML regex, naming, path traversal safety  │
│ 2. Content Quality           │  15%   │ Progressive disclosure efficiency, body <500 lines     │
│ 3. Functional Correctness    │  25%   │ Assertion pass rate on evals/evals.json (>= 80%)       │
│ 4. Skill Lift Delta          │  15%   │ Empirical pass-rate improvement over baseline agent    │
│ 5. Trigger Quality (F1)      │  10%   │ Intent Precision, Recall, and F1 score (>= 0.80)       │
│ 6. Execution Reliability     │   5%   │ Subprocess stability (0 crashes) & timeout safety      │
│ 7. Resource Efficiency       │   5%   │ Token economy (<5000 tokens) & execution speed         │
│ 8. Security (SkillSpector)   │  15%   │ 0 Critical, 0 High findings across 17 AST categories   │
└──────────────────────────────┴────────┴────────────────────────────────────────────────────────┘
```

---

## 5. Evaluation Framework Comparison & Gap Analysis

When comparing the evaluation pipeline in the upstream project (`awesome-agent-skills` CI/CD) against the standalone `evaluator-skill`, we identified and analyzed the following architectural gaps:

| Feature / Capability | Upstream CI/CD Pipeline | Initial `evaluator-skill` | Status & Gap Identified |
| :--- | :--- | :--- | :--- |
| **8-Dimension Composite Scoring** | ✅ Native Python package | ⚠️ Required full `evaluator.cli` installed | **GAP 1**: Failed if installed standalone outside the monorepo. |
| **NVIDIA SkillSpector 17 AST Scan** | ✅ Dynamic AST + regex parser | ⚠️ Shell-delegated script only | **GAP 2**: Missing local standalone AST parser fallback. |
| **Batch / Library Scanning** | ✅ `python -m evaluator.cli repo` | ❌ Only evaluated single skills | **GAP 3**: Could not scan entire multi-skill directories at once. |
| **Interactive HTML Dashboard** | ✅ Integrated reporting | ❌ Markdown/JSON only | **GAP 4**: Missing offline visual HTML scorecard generator. |
| **Continuous Integration Diff Mode** | ✅ `evaluator.cli diff --base origin/main` | ❌ No git diff detection | **GAP 5**: Could not automatically detect only modified skills in PRs. |

---

## 6. Remediation & Enhancements Added to `evaluator-skill`

To bridge all 5 gaps identified in the comparison, `evaluator-skill` has been upgraded with:

1. **Hybrid Execution Engine (`scripts/run_evaluation.py`)**:
   - Automatically detects if the native `evaluator.cli` framework is available.
   - If running standalone inside a user's isolated environment, automatically falls back to bundled zero-dependency AST & structural analyzers (`structural_check.py`, `security_scan.py`).
2. **Bundled AST Security Engine (`scripts/security_scan.py`)**:
   - Complete local Python AST parser checking `eval()`, `exec()`, `os.system()`, `shell=True`, and unsafe deserialization.
3. **Batch Library Scanner (`scripts/batch_scan.py`)**:
   - Allows auditing an entire directory of skills (e.g. `skills/`) in a single invocation.
4. **Standalone HTML Scorecard Generator (`scripts/generate_html_report.py`)**:
   - Generates interactive, standalone HTML audit dashboards with visual quality badges.
5. **PR Quality Gate Compliance**:
   - Fully aligned with CI/CD hard gating matrix: **`PASS` ($\ge 80.0$)**, **`WARN` ($70.0 \dots 79.9$)**, and **`BLOCK` ($< 80.0$ or Security issues)**.

---

## 7. Step-by-Step Skill Authoring & Gating Walkthrough

```bash
# Step 1: Install the bundle into your IDE
npx github:sarveshtalele/skill-generator-agent-skill install --target claude

# Step 2: In Claude Code / Cursor, prompt:
# "Create a new agent skill for linting Kubernetes Helm charts"

# Step 3: Answer the 4 clarifying interview questions
# Step 4: Confirm the generated implementation plan
# Step 5: Review testing.md and approve test cases
# Step 6: Verify final 95+ PASS scorecard emitted under scorecards/
```
