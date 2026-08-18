# Contributing to Skill Generator & Evaluator Agent Skill Bundle

Thank you for your interest in contributing! We welcome contributions to existing skills, new agent skills, and improvements to the evaluation and security tooling.

---

## 🛠️ Development Workflow

1. **Fork and Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/skill-generator-agent-skill.git
   cd skill-generator-agent-skill
   ```

2. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/my-new-skill
   ```

3. **Author or Modify Skills**:
   - Every skill must reside in `skills/<skill-name>/` and conform to [Agent Skills Specification v1.0](https://agentskills.io/specification).
   - Keep `SKILL.md` under 500 lines using progressive disclosure (`references/`, `scripts/`, `assets/`, `templates/`).
   - Create multi-type test cases in `evals/evals.json`.

---

## 🧪 Quality Gate Verification

Before opening a pull request, verify that your changes pass all local quality and security checks:

```bash
# 1. Validate Specification Compliance
make validate SKILL=<skill-name>

# 2. Run AST Security & Taint Scan
make security SKILL=<skill-name>

# 3. Execute Full 8-Dimension Evaluation
make evaluate SKILL=<skill-name>

# 4. (Optional) Run Baseline Comparison
make baseline SKILL=<skill-name>

# 5. Regenerate Scorecards
make scorecard
```

### Pull Request Acceptance Criteria
- **Quality Score**: Overall Score $\ge 95.0$ (`PASS`).
- **Security**: 0 Critical and 0 High security findings across the 68 SkillSpector pattern categories.
- **Functional Pass Rate**: $\ge 80\%$ on all assertions defined in `evals/evals.json`.
- **Zero-Dependency Core**: All Python scripts in `scripts/` must run using only the Python standard library.

---

## 📋 Pull Request Submission

1. Ensure the generated scorecard is committed to `scorecards/<skill-name>.md` and `.json`.
2. Fill out the [Pull Request Template](.github/pull_request_template.md).
3. GitHub Actions CI will automatically run specification checks, generate SARIF security reports, and enforce the quality gate.
