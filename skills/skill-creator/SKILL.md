---
name: skill-creator
description: >
  Interactive, Q&A-driven Agent Skill creator and optimizer. When a user requests a new skill or bundle, it acts
  as a clarifying architect chatbot, asks detailed approach questions, formulates an implementation plan,
  requests explicit user confirmation, deterministically scaffolds the skill, generates task checklists and test cases,
  runs parallel baseline and security audits, launches interactive eval reviews, auto-optimizes trigger descriptions,
  and packages distributable .skill bundles.
  Use whenever the user wants to design, author, scaffold, test, optimize, package, or build a new agent skill or SDD bundle.
  Trigger on: create skill, build agent skill, scaffold skill, new agent skill, generate skill from prompt, create sdd bundle, optimize skill description, package skill, test skill evals.
compatibility: "Python 3.8+"
metadata:
  sdlc: Implementation
  tags:
    - skill-creator
    - SDLC:Implementation
    - agent-skills
    - interactive-chatbot
    - scaffolding
    - trigger-optimization
allowed-tools: "Read, Bash(python scripts/*.py:*)"
---

# Skill Creator

An interactive, Q&A-driven agent skill for authoring, evaluating, optimizing, and packaging new **Agent Skills** conforming strictly to the [Agent Skills Specification v1.0](https://agentskills.io/specification) and [NVIDIA SkillSpector](https://github.com/nvidia/skillspector) security standards.

---

## 🤖 End-to-End Skill Creation Lifecycle (10-Phase Workflow)

When a user requests a new skill, follow this structured lifecycle to ensure optimal architecture, thorough verification, and trigger precision:

```
User Skill Request
        │
        ▼
Phase 1: Interactive Discovery Interview (4 focused technical questions)
        │
        ▼
Phase 2: Formal Implementation Blueprint Formulation
        │
        ▼
Phase 3: Explicit User Confirmation Gate (Wait for user approval before writing code)
        │
        ▼ (ONLY after user approves)
Phase 4: Deterministic Scaffolding (`skills/<name>/` + `testing.md`)
        │
        ▼
Phase 5: Test Case Alignment & `evals/evals.json` Synthesis
        │
        ▼
Phase 6: Quality & Security Evaluation via `evaluator-skill` (PASS / WARN / BLOCK)
        │
        ▼
Phase 7: Baseline Lift Testing & Subagent Grading (`agents/grader.md`)
        │
        ▼
Phase 8: Interactive Human Review via Eval Viewer (`eval-viewer/generate_review.py`)
        │
        ▼
Phase 9: Description Trigger Optimization Loop (`scripts/run_loop.py`)
        │
        ▼
Phase 10: Distributable Package Bundling (`scripts/package_skill.py`)
```

---

## 📑 Step-by-Step Execution Contract

### Phase 1: Interactive Discovery Interview
When the user states their initial skill idea, ask **4 specific clarifying questions** to nail down the technical requirements:
1. **Target SDLC Phase & I/O Contract**: What SDLC phase does this belong to (*Requirements, Architecture, Implementation, Testing, Security, Maintenance*)? What are the primary inputs (e.g. diffs, source files, specs) and deliverables?
2. **Deterministic Script vs. LLM Boundary**: Should logic be encapsulated into offline deterministic scripts in `scripts/` (to save tokens and ensure reproducibility), or does it rely purely on markdown procedural prompts?
3. **Trigger Invocations & Intent Boundaries**: What are 3-5 example user prompts that should explicitly trigger this skill? What are near-miss queries that should NOT trigger it?
4. **Environment & Tool Dependencies**: Does the skill require CLI tools (`git`, `npm`, `pytest`) or pure standard library Python?

### Phase 2: Formulate Comprehensive Implementation Plan
Synthesize the requirements into a formal blueprint and present it in chat:

```markdown
### 📐 Proposed Skill Implementation Plan: `<skill-name>`

- **Skill Name**: `<kebab-case-name>`
- **SDLC Phase**: `<Phase>`
- **Trigger Description**: `<Pushy description of WHAT the skill does and WHEN to trigger it>`
- **Progressive Disclosure Architecture**:
  - `SKILL.md`: Main procedural workflow contract (<500 lines)
  - `scripts/<name>_skill.py`: Offline automation engine
  - `references/`: Domain rulebooks & schema definitions
  - `templates/`: Structured output templates
  - `manifest.yaml` & `skill-card.json`: Spec 1.0 metadata
- **Verification & Evaluation Plan**:
  - `testing.md`: Task-based checklist for manual & automated verification
  - `evals/evals.json`: Benchmark assertion suite (multi-type assertions)

> ❓ **User Confirmation Required**: Please confirm if you approve this plan to begin scaffolding.
```

### Phase 3: Explicit User Confirmation Gate
Wait for the user's explicit confirmation before creating files. This prevents wasted tokens and misaligned implementations.

### Phase 4: Deterministic Scaffolding
Execute the bundled scaffolder to build the standard directory layout:

```bash
# For a single skill:
python skills/skill-creator/scripts/skill_scaffolder.py \
  --name "<skill-name>" \
  --description "<trigger description>" \
  --sdlc "<sdlc phase>"

# For a 4-Phase Spec-Driven Development (SDD) bundle:
python skills/skill-creator/scripts/skill_scaffolder.py \
  --name "<bundle-prefix>" \
  --description "<domain description>" \
  --bundle sdd

# Generate task checklist:
python skills/skill-creator/scripts/test_plan_orchestrator.py --skill skills/<skill-name>
```

### Phase 5: Test Case Alignment & `evals.json` Synthesis
Review the generated `testing.md` checklist and synthesize the multi-type assertion suite:
```bash
python skills/skill-creator/scripts/test_plan_orchestrator.py --skill skills/<skill-name> --with-evals
```

### Phase 6: Quality & Security Evaluation
Run the evaluator to audit specification compliance, AST safety, and security patterns:
```bash
python skills/evaluator-skill/scripts/run_evaluation.py --skill skills/<skill-name> --output ./scorecards
```

### Phase 7: Baseline Lift Testing & Subagent Grading
Execute baseline comparison to ensure the skill demonstrates empirical improvement over the base LLM:
```bash
python skills/evaluator-skill/scripts/run_evaluation.py --skill skills/<skill-name> --output ./scorecards --with-baseline
```
Use the specialized subagents in `agents/`:
- [`agents/grader.md`](agents/grader.md): Evidence-based assertion grading.
- [`agents/comparator.md`](agents/comparator.md): Blind A/B comparison between skill versions.
- [`agents/analyzer.md`](agents/analyzer.md): Post-hoc improvement synthesis.

### Phase 8: Interactive Human Review via Eval Viewer
Launch the local eval viewer web server to allow the user to review outputs, inspect benchmark graphs, and provide qualitative feedback:
```bash
python skills/skill-creator/eval-viewer/generate_review.py --workspace . --port 8765
```

### Phase 9: Description Trigger Optimization Loop
Optimize the frontmatter `description` to ensure high trigger precision and recall (F1 score $\ge 0.80$):
```bash
python skills/skill-creator/scripts/run_loop.py --skill skills/<skill-name> --iterations 5
```

### Phase 10: Distributable Package Bundling
Once all quality gates pass, package the skill into a distributable `.skill` archive:
```bash
python skills/skill-creator/scripts/package_skill.py --skill skills/<skill-name> --output ./dist
```

---

## 📦 Bundled Resources & Engine Scripts

- **Scaffolding**: [`scripts/skill_scaffolder.py`](scripts/skill_scaffolder.py), [`scripts/test_plan_orchestrator.py`](scripts/test_plan_orchestrator.py), [`scripts/quick_validate.py`](scripts/quick_validate.py)
- **Trigger Optimization**: [`scripts/run_eval.py`](scripts/run_eval.py), [`scripts/improve_description.py`](scripts/improve_description.py), [`scripts/run_loop.py`](scripts/run_loop.py)
- **Packaging & Delivery**: [`scripts/package_skill.py`](scripts/package_skill.py)
- **Subagents**: [`agents/grader.md`](agents/grader.md), [`agents/comparator.md`](agents/comparator.md), [`agents/analyzer.md`](agents/analyzer.md)
- **Eval Reviewer UI**: [`eval-viewer/generate_review.py`](eval-viewer/generate_review.py), [`eval-viewer/viewer.html`](eval-viewer/viewer.html), [`assets/eval_review.html`](assets/eval_review.html)
- **Schemas & Protocols**: [`references/schemas.md`](references/schemas.md)

---

## 🎯 Authoring Best Practices (Progressive Disclosure)

1. **Keep `SKILL.md` under 500 lines**: Use `SKILL.md` for high-level workflow orchestration. Move detailed domain rules to `references/*.md` and templates to `templates/*.md`.
2. **Explain the "Why"**: Models follow instructions better when given context and rationale rather than arbitrary uppercase commands.
3. **Pushy Descriptions**: Frontmatter descriptions should explicitly list trigger phrases and edge-case intents to prevent under-triggering.
4. **Extract Repeated Work**: If evaluation runs show the model frequently writing boilerplate code, extract that logic into a bundled script in `scripts/`.
