@echo off
REM Cross-platform Windows Batch task runner for skill-generator-agent-skill.
REM Replaces Makefile on Windows Command Prompt (cmd.exe).

set SKILL=%2
if "%SKILL%"=="" set SKILL=skill-creator

REM Detect Python
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PY=python
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set PY=py
    ) else (
        echo [ERROR] Python is not installed or not in PATH.
        exit /b 1
    )
)

if "%1"=="validate" goto validate
if "%1"=="security" goto security
if "%1"=="security-sarif" goto security_sarif
if "%1"=="evaluate" goto evaluate
if "%1"=="baseline" goto baseline
if "%1"=="trigger" goto trigger
if "%1"=="package" goto package
if "%1"=="scorecard" goto scorecard
if "%1"=="batch" goto batch
if "%1"=="evaluate-all" goto evaluate_all
goto help

:validate
echo [INFO] Validating Spec 1.0 compliance for %SKILL%...
%PY% skills/evaluator-skill/scripts/structural_check.py skills/%SKILL%
goto end

:security
echo [INFO] Running 68-pattern AST and Taint security scan on %SKILL%...
%PY% skills/evaluator-skill/scripts/security_scan.py skills/%SKILL% --format json
goto end

:security_sarif
echo [INFO] Generating SARIF 2.1.0 report for %SKILL%...
%PY% skills/evaluator-skill/scripts/security_scan.py skills/%SKILL% --format sarif --output results-%SKILL%.sarif
goto end

:evaluate
echo [INFO] Running full 8-dimension evaluation for %SKILL%...
%PY% skills/evaluator-skill/scripts/run_evaluation.py --skill skills/%SKILL% --output ./scorecards
goto end

:baseline
echo [INFO] Evaluating %SKILL% with empirical baseline lift comparison...
%PY% skills/evaluator-skill/scripts/run_evaluation.py --skill skills/%SKILL% --output ./scorecards --with-baseline
goto end

:trigger
echo [INFO] Running trigger description optimization loop for %SKILL%...
%PY% skills/skill-creator/scripts/run_loop.py --skill skills/%SKILL%
goto end

:package
echo [INFO] Packaging %SKILL% into distributable .skill ZIP...
%PY% skills/skill-creator/scripts/package_skill.py --skill skills/%SKILL% --output ./dist
goto end

:scorecard
echo [INFO] Regenerating SCORECARD.md and SKILL_REGISTRY.md...
%PY% scripts/generate_scorecard.py
goto end

:batch
echo [INFO] Running batch evaluation across all skills...
%PY% skills/evaluator-skill/scripts/batch_scan.py skills/ --output ./scorecards
goto end

:evaluate_all
echo [INFO] Evaluating all bundled skills...
%PY% skills/evaluator-skill/scripts/run_evaluation.py --skill skills/skill-creator --output ./scorecards
%PY% skills/evaluator-skill/scripts/run_evaluation.py --skill skills/evaluator-skill --output ./scorecards
%PY% skills/evaluator-skill/scripts/run_evaluation.py --skill skills/token-telemetry --output ./scorecards
%PY% scripts/generate_scorecard.py
goto end

:help
echo.
echo Skill Generator and Evaluator - Windows Command Prompt Runner
echo.
echo Usage:
echo   run.bat ^<command^> [skill-name]
echo.
echo Available Commands:
echo   validate ^<skill^>        Validate specification compliance
echo   security ^<skill^>        Run 68-pattern AST and Taint security scan
echo   security-sarif ^<skill^>  Generate SARIF 2.1.0 security report
echo   evaluate ^<skill^>        Execute full 8-dimension quality evaluation
echo   baseline ^<skill^>        Run evaluation with baseline lift comparison
echo   trigger ^<skill^>         Run trigger description optimization loop
echo   package ^<skill^>         Bundle skill into distributable .skill archive
echo   scorecard               Regenerate SCORECARD.md and SKILL_REGISTRY.md
echo   evaluate-all            Evaluate all skills and update scorecard
echo.
echo Examples:
echo   run.bat evaluate skill-creator
echo   run.bat security evaluator-skill
echo   run.bat package skill-creator
echo.

:end
