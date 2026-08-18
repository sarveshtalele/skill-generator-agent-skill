# 🏗️ Spec-Driven Development (SDD) Bundle Architecture

**Spec-Driven Development (SDD)** is an enterprise engineering methodology that decomposes complex software development lifecycles into **4 interconnected, specialized Agent Skills**.

---

## 🔄 The 4-Phase SDD Lifecycle

Instead of having a single monolithic assistant attempt to design, plan, write, and test an entire system in one massive context window, an SDD bundle executes 4 distinct lifecycle phases:

```
SDLC Lifecycle:
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 1: SPECIFY (`<prefix>-specify`)                                   │
│ • Validates technical contracts, OpenAPI/GraphQL schemas, & invariants  │
│ • Produces: `spec.md` contract                                         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Contract Passed
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 2: PLAN (`<prefix>-plan`)                                        │
│ • Formulates step-by-step task breakdown & architectural dependencies │
│ • Produces: `plan.md` & task checklist                                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ User Approved
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 3: IMPLEMENT (`<prefix>-implement`)                              │
│ • Executes task-by-task code generation against the approved plan      │
│ • Produces: Production source code & unit tests                        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Implementation Done
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 4: VERIFY (`<prefix>-verify`)                                    │
│ • Executes integration tests, regression checks, & security audits     │
│ • Produces: `verification_report.md` with PASS / BLOCK quality gate    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Scaffolding a Custom SDD Bundle in 1 Command

The `skill-creator` includes built-in support for generating 4-phase SDD bundles:

```bash
python skills/skill-creator/scripts/skill_scaffolder.py \
  --name "kubernetes-operator" \
  --description "Kubernetes CRD and Operator Controller Development" \
  --bundle sdd
```

### Output Generated:
```
skills/
├── kubernetes-operator-specify/     # Requirements & CRD Schema Contract
│   ├── SKILL.md
│   ├── manifest.yaml
│   └── evals/evals.json
├── kubernetes-operator-plan/        # Reconciliation Loop & State Machine Plan
│   ├── SKILL.md
│   ├── manifest.yaml
│   └── evals/evals.json
├── kubernetes-operator-implement/   # Controller-Runtime Go Implementation
│   ├── SKILL.md
│   ├── manifest.yaml
│   └── evals/evals.json
└── kubernetes-operator-verify/      # EnvTest & Kuttl E2E Verification
    ├── SKILL.md
    ├── manifest.yaml
    └── evals/evals.json
```

---

## 🌟 Benefits of SDD Bundles
1. **Zero Context Pollution**: Each phase operates in a fresh, clean context window referencing only the approved artifact from the previous phase.
2. **Deterministic Quality Gates**: The agent cannot proceed to `implement` until `specify` and `plan` have received explicit user confirmation.
3. **Traceability**: Every generated line of code traces directly back to a numbered requirement in `spec.md` and a task in `plan.md`.
