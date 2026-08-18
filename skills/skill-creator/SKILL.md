---
name: skill-creator
description: >
  Interactive, Q&A-driven Agent Skill creator. When a user requests a new skill, it acts
  as a clarifying interview chatbot, asks detailed approach questions, formulates an
  implementation plan, and requests explicit user approval before scaffolding the skill,
  generating testing.md, test cases, and evaluating the skill end-to-end.
  Trigger on: create skill, build agent skill, scaffold skill, new agent skill, generate skill from prompt.
compatibility: "Python 3.8+"
metadata:
  sdlc: Implementation
  tags:
    - skill-creator
    - SDLC:Implementation
    - agent-skills
    - interactive-chatbot
    - scaffolding
allowed-tools: "Read, Bash(python scripts/*.py:*)"
---

# Skill Creator

An interactive, Q&A-driven agent skill for authoring, testing, and evaluating new **Agent Skills** conforming strictly to the [Agent Skills Specification v1.0](https://agentskills.io/specification) and [NVIDIA SkillSpector](https://github.com/nvidia/skillspector) security standards.

## 🤖 Core Interactive Behavior Contract (Crucial)

When a user prompts with a skill idea (e.g., *"I want to create a skill for X"* or *"Build an agent skill for Y"*), **DO NOT immediately generate files**. You must strictly operate as a consultative architect through a structured Q&A interview:

```
User Skill Request
        │
        ▼
Phase 1: Interactive Q&A Discovery (Ask 3-4 clarifying technical questions)
        │
        ▼
Phase 2: Formal Implementation Plan Formulation (Architectural Blueprint)
        │
        ▼
Phase 3: Explicit User Approval Gate (STOP and wait for user's confirmation)
        │
        ▼ (ONLY after user confirms "Yes / Approved")
Phase 4: Scaffolding & Task Testing Matrix (`skills/<name>/` + `testing.md`)
        │
        ▼
Phase 5: User Test Case Review & `evals/evals.json` Synthesis
        │
        ▼
Phase 6: Automated Quality & Security Audit via `evaluator-skill` (95+ PASS Scorecard)
```

---

## 📑 Step-by-Step Interactive Workflow

### Phase 1: Interactive Q&A Discovery Interview
When the user states their initial idea, reply in chat asking **4 specific clarifying questions**:

1. **Target SDLC Phase & Primary Task**:
   - What specific SDLC phase does this belong to (*Requirements, Architecture, Implementation, Testing, Security, Maintenance*)?
   - What is the primary input (e.g., source code, git diff, Jira story, OpenAPI spec, CSV) and primary output deliverable?
2. **Deterministic Script vs. LLM Boundary**:
   - Should there be bundled offline Python scripts (e.g., AST parsers, linters, graph generators) in `scripts/`, or does it rely purely on progressive disclosure prompt contracts?
3. **Trigger Invocations & Intent Boundaries**:
   - What are 3-5 example user prompts that should explicitly trigger this skill?
   - Are there near-miss queries that should NOT trigger it (to prevent collisions)?
4. **Target Tools & Environment Dependencies**:
   - Does it require special CLI tools (e.g., `git`, `npm`, `pytest`, `snyk`) or Python standard libraries?

---

### Phase 2: Formulate Comprehensive Implementation Plan
Once the user answers the clarifying questions, synthesize their requirements into a formal blueprint and present it in chat:

```markdown
### 📐 Proposed Skill Implementation Plan: `<skill-name>`

- **Skill Name**: `<kebab-case-name>`
- **SDLC Phase**: `<Phase>`
- **Trigger Description**: `<Concise description of WHAT and WHEN>`
- **Progressive Disclosure Architecture**:
  - `SKILL.md`: Procedural workflow contract (<500 lines)
  - `scripts/<name>_skill.py`: Deterministic CLI tool
  - `references/`: Domain rulebooks & API catalogs
  - `templates/`: Output report blueprint
  - `manifest.yaml` & `skill-card.json`: Enterprise packaging
- **Verification Plan**:
  - `testing.md`: Task-based checklist for Unit testing & E2E scenarios
  - `evals/evals.json`: Benchmark assertion suite

> ❓ **User Approval Required**: *Does this plan match your expectations? Please reply with **Approve** (or provide modifications) to begin scaffolding the skill.*
```

---

### Phase 3: Explicit User Approval Gate (CRITICAL)
**STOP and wait for the user's explicit approval.** Do not create any file until the user confirms the plan.

---

### Phase 4: Scaffolding Directory & Core Artifacts
Once approved, execute the bundled deterministic scaffolder:

**For a Single Skill:**
```bash
python skills/skill-creator/scripts/skill_scaffolder.py \
  --name "<skill-name>" \
  --description "<approved trigger description>" \
  --sdlc "<approved SDLC phase>"
```

**For a 4-Phase Spec-Driven Development (SDD) Bundle:**
```bash
python skills/skill-creator/scripts/skill_scaffolder.py \
  --name "<bundle-prefix>" \
  --description "<domain description>" \
  --bundle sdd
```
*(This automatically scaffolds all 4 interconnected lifecycle skills: `<prefix>-specify`, `<prefix>-plan`, `<prefix>-implement`, and `<prefix>-verify`)*.

Generate the task-based testing checklist:
```bash
python skills/skill-creator/scripts/test_plan_orchestrator.py --skill skills/<skill-name>
```

---

### Phase 5: Present `testing.md` & Synthesize `evals.json`
Present the proposed test cases in `testing.md` to the user:
> *"I have scaffolded the skill and created `testing.md`. Please review the test cases above. Once confirmed, I will generate the evaluation suites and run end-to-end verification."*

Upon confirmation, write the benchmark suite:
```bash
python skills/skill-creator/scripts/test_plan_orchestrator.py --skill skills/<skill-name> --with-evals
```

---

### Phase 6: Automated Quality & AST Security Audit
Invoke the evaluator to verify 100% specification compliance, functional accuracy, and NVIDIA SkillSpector AST safety:
```bash
python -m evaluator.cli all skills/<skill-name> --output-dir scorecards
```
Deliver the final `scorecards/<skill-name>.md` report with **`✅ PASS`**.

---

## 🎯 Example Dialog Workflow

### Example A: Single Skill Creation
```
User: "I want to create a skill for analyzing SQL migration scripts."

Agent: "I'd love to help you build the `sql-migration-analyzer` skill! To design the optimal architecture, could you clarify:
1. What specific checks should it perform (e.g. table locks, unindexed foreign keys, destructive DROP statements)?
2. Should we bundle an offline SQL AST parser script in `scripts/`?
3. What are 3 typical prompts you'll use to trigger this skill?
4. What output report format do you prefer (Markdown summary, JSON, or PR checklist)?"

User: [Answers questions]

Agent: [Presents formal Implementation Plan and asks: 'Will you approve this plan to begin creation?']

User: "Looks great, approved!"

Agent: [Scaffolds skills/sql-migration-analyzer/, generates testing.md, confirms test cases, creates evals.json, evaluates score, and presents final 96+ PASS scorecard].
```

### Example B: Custom SDD Bundle Creation
```
User: "Can you create a custom SDD bundle for Cloudflare Worker development?"

Agent: "Absolutely! I will design a 4-phase SDD bundle (`cf-worker-specify`, `cf-worker-plan`, `cf-worker-implement`, `cf-worker-verify`).
Let me clarify a few technical requirements:
1. What runtime APIs / bindings should be validated in the specify contract (KV, D1, R2, Queues)?
2. What test runner should be configured for the verify phase (Vitest / Miniflare / Workerd)?
3. What security checks should be prioritized?"

User: [Answers questions]

Agent: [Formulates 4-phase bundle plan and asks for approval]

User: "Approved!"

Agent: [Runs `skill_scaffolder.py --name cf-worker --bundle sdd`, scaffolds all 4 skills, generates testing plans, verifies each, and outputs 4 passing scorecards].
```

