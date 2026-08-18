.PHONY: validate security security-sarif evaluate baseline trigger package scorecard batch evaluate-all help

PYTHON ?= python3
SKILL ?= skill-creator
REPO_ROOT := $(shell pwd)

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

validate: ## Validate spec compliance for a skill (SKILL=name)
	$(PYTHON) skills/evaluator-skill/scripts/structural_check.py skills/$(SKILL)

security: ## Run security scan (SKILL=name)
	$(PYTHON) skills/evaluator-skill/scripts/security_scan.py skills/$(SKILL) --format json

security-sarif: ## Run security scan with SARIF output (SKILL=name)
	$(PYTHON) skills/evaluator-skill/scripts/security_scan.py skills/$(SKILL) --format sarif --output results-$(SKILL).sarif

evaluate: ## Full 8-dimension evaluation (SKILL=name)
	$(PYTHON) skills/evaluator-skill/scripts/run_evaluation.py --skill skills/$(SKILL) --output ./scorecards

baseline: ## Evaluate with baseline comparison (SKILL=name)
	$(PYTHON) skills/evaluator-skill/scripts/run_evaluation.py --skill skills/$(SKILL) --output ./scorecards --with-baseline

trigger: ## Run trigger optimization loop (SKILL=name)
	$(PYTHON) skills/skill-creator/scripts/run_loop.py --skill skills/$(SKILL)

package: ## Package skill into .skill bundle (SKILL=name)
	$(PYTHON) skills/skill-creator/scripts/package_skill.py --skill skills/$(SKILL) --output ./dist

scorecard: ## Regenerate portfolio SCORECARD.md and SKILL_REGISTRY.md
	$(PYTHON) scripts/generate_scorecard.py

batch: ## Batch evaluate all skills
	$(PYTHON) skills/evaluator-skill/scripts/batch_scan.py skills/ --output ./scorecards

evaluate-all: ## Evaluate all bundled skills
	$(MAKE) evaluate SKILL=skill-creator
	$(MAKE) evaluate SKILL=evaluator-skill
	$(MAKE) scorecard
