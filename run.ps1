<#
.SYNOPSIS
    Cross-platform Windows PowerShell task runner for skill-generator-agent-skill.
    Replaces Makefile on Windows systems without requiring Make or WSL.

.EXAMPLE
    .\run.ps1 validate skill-creator
    .\run.ps1 security skill-creator
    .\run.ps1 evaluate skill-creator
    .\run.ps1 baseline skill-creator
    .\run.ps1 trigger skill-creator
    .\run.ps1 package skill-creator
    .\run.ps1 scorecard
    .\run.ps1 evaluate-all
#>

param (
    [Parameter(Position = 0)]
    [string]$Action = "help",

    [Parameter(Position = 1)]
    [string]$Skill = "skill-creator"
)

# Detect Python interpreter (python or py)
$Python = "python"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $Python = "py"
    } else {
        Write-Error "Python is not installed or not in PATH."
        exit 1
    }
}

switch ($Action.ToLower()) {
    "validate" {
        Write-Host "🔍 Validating Spec 1.0 compliance for $Skill..." -ForegroundColor Cyan
        & $Python skills/evaluator-skill/scripts/structural_check.py "skills/$Skill"
    }

    "security" {
        Write-Host "🛡️ Running 68-pattern AST & Taint security scan on $Skill..." -ForegroundColor Cyan
        & $Python skills/evaluator-skill/scripts/security_scan.py "skills/$Skill" --format json
    }

    "security-sarif" {
        Write-Host "🛡️ Generating SARIF 2.1.0 report for $Skill..." -ForegroundColor Cyan
        & $Python skills/evaluator-skill/scripts/security_scan.py "skills/$Skill" --format sarif --output "results-$Skill.sarif"
    }

    "evaluate" {
        Write-Host "📊 Running full 8-dimension evaluation for $Skill..." -ForegroundColor Cyan
        & $Python skills/evaluator-skill/scripts/run_evaluation.py --skill "skills/$Skill" --output ./scorecards
    }

    "baseline" {
        Write-Host "📈 Evaluating $Skill with empirical baseline lift comparison..." -ForegroundColor Cyan
        & $Python skills/evaluator-skill/scripts/run_evaluation.py --skill "skills/$Skill" --output ./scorecards --with-baseline
    }

    "trigger" {
        Write-Host "🎯 Running trigger description optimization loop for $Skill..." -ForegroundColor Cyan
        & $Python skills/skill-creator/scripts/run_loop.py --skill "skills/$Skill"
    }

    "package" {
        Write-Host "📦 Packaging $Skill into distributable .skill ZIP..." -ForegroundColor Cyan
        & $Python skills/skill-creator/scripts/package_skill.py --skill "skills/$Skill" --output ./dist
    }

    "scorecard" {
        Write-Host "📋 Regenerating SCORECARD.md and SKILL_REGISTRY.md..." -ForegroundColor Cyan
        & $Python scripts/generate_scorecard.py
    }

    "batch" {
        Write-Host "🔄 Running batch evaluation across all skills..." -ForegroundColor Cyan
        & $Python skills/evaluator-skill/scripts/batch_scan.py skills/ --output ./scorecards
    }

    "evaluate-all" {
        Write-Host "🚀 Evaluating all bundled skills..." -ForegroundColor Green
        & $Python skills/evaluator-skill/scripts/run_evaluation.py --skill skills/skill-creator --output ./scorecards
        & $Python skills/evaluator-skill/scripts/run_evaluation.py --skill skills/evaluator-skill --output ./scorecards
        & $Python skills/evaluator-skill/scripts/run_evaluation.py --skill skills/token-telemetry --output ./scorecards
        & $Python scripts/generate_scorecard.py
    }

    Default {
        Write-Host "⚡ Skill Generator & Evaluator — Windows PowerShell Runner" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Usage:" -ForegroundColor White
        Write-Host "  .\run.ps1 <command> [skill-name]"
        Write-Host ""
        Write-Host "Available Commands:" -ForegroundColor White
        Write-Host "  validate <skill>        Validate specification compliance (100/100)"
        Write-Host "  security <skill>        Run 68-pattern AST & Taint security scan"
        Write-Host "  security-sarif <skill>  Generate SARIF 2.1.0 security report"
        Write-Host "  evaluate <skill>        Execute full 8-dimension quality evaluation"
        Write-Host "  baseline <skill>        Run evaluation with baseline lift comparison"
        Write-Host "  trigger <skill>         Run trigger description optimization loop"
        Write-Host "  package <skill>         Bundle skill into distributable .skill archive"
        Write-Host "  scorecard               Regenerate SCORECARD.md and SKILL_REGISTRY.md"
        Write-Host "  evaluate-all            Evaluate all skills and update scorecard"
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Cyan
        Write-Host "  .\run.ps1 evaluate skill-creator"
        Write-Host "  .\run.ps1 security evaluator-skill"
        Write-Host "  .\run.ps1 package skill-creator"
    }
}
