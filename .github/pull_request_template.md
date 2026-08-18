## Pull Request Checklist

### Skill Quality Gate

Please confirm the following before requesting review:

- [ ] **Spec Compliance**: `make validate SKILL=<name>` passes with 0 errors
- [ ] **Security Scan**: `make security SKILL=<name>` shows 0 Critical/High findings
- [ ] **Functional Tests**: Assertions in `evals/evals.json` pass at ≥80% rate
- [ ] **Quality Score**: Overall score ≥ 95 (or provide justification for WARN)
- [ ] **Scorecard Attached**: Generated scorecard committed to `scorecards/`

### Changes Summary

**Skill(s) affected**: <!-- e.g. skill-creator, evaluator-skill -->

**Type of change**:
- [ ] New skill
- [ ] Skill modification
- [ ] Evaluator/infrastructure change
- [ ] Documentation only

### Description

<!-- Describe what this PR does and why -->

### Evidence

<!-- Paste scorecard summary or link to CI run -->
