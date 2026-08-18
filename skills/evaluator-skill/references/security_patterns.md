# Security Pattern Reference (SkillSpector-Enhanced)

This documents what `scripts/security_scan.py` checks, how the risk score is computed, how baseline suppression works, and what each pattern category detects.

The scanner is inspired by **NVIDIA SkillSpector** (github.com/nvidia/skillspector) and incorporates:
1. **Static Regex Patterns** (68 patterns across 17 security categories)
2. **Behavioral AST & Taint Tracking** (`taint_tracker.py` data-flow analysis)
3. **YARA Signatures** (`assets/agent_skills.yar` via `yara_scanner.py`)
4. **Unicode Deception / Homoglyph Detection** (Cyrillic visual spoofing)
5. **Optional Semantic LLM Analysis** (`semantic_scanner.py`)
6. **False-Positive Baseline Suppression** (`.skill-quality/.skillspector-baseline.yaml`)
7. **SARIF 2.1.0 Export** (`sarif_report.py`)

---

## Security Taxonomy & Pattern Categories

| Category | IDs | Description |
|:---|:---|:---|
| **Prompt Injection** | P1-P4 | Instruction override language, zero-width / hidden characters, exfiltration commands, behavior manipulation |
| **System Prompt Leakage** | P6-P7 | Direct and indirect attempts to extract system instructions or hidden prompts |
| **Harmful Content** | P5 | Embedded instructions directing lethal or destructive actions disguised as ordinary instructions |
| **Data Exfiltration** | E1-E3 | Outbound network calls, bulk environment-variable dumping, broad filesystem enumeration |
| **Privilege Escalation** | PE2-PE3 | `sudo`/`setuid` execution, reading SSH keys or cloud credentials (`.aws/credentials`, `id_rsa`) |
| **Supply Chain** | SC1-SC3 | Unpinned dependencies in `requirements.txt`, piping remote scripts to bash (`curl \| bash`), base64 execution |
| **Excessive Agency** | EA1-EA2 | Unrestricted access permissions, autonomous high-impact actions (delete/deploy/transfer) without approval |
| **Tool Misuse** | TM1, TM3 | `shell=True`, `rm -rf /`, `chmod 777`, disabled TLS verification (`verify=False`) |
| **Rogue Agent** | RA1-RA2 | Self-modifying code (modifying own `SKILL.md` or scripts), persistence via cron or startup items |
| **Trigger Abuse** | TR1, TR3 | Overly generic single-word triggers, keyword-stuffing in `description` |
| **Behavioral AST** | AST1-AST7 | `exec()`, `eval()`, `compile()`, `__import__()`, `os.system`, `subprocess.*` (`shell=True`), dynamic `getattr()` |
| **Taint Tracking** | TT1-TT3 | Direct source-to-sink data flow, propagated taint flow, credential source + network sink proximity |
| **Unicode Deception** | UNI1 | Visual homoglyph spoofing (e.g. Cyrillic characters replacing Latin letters in tool names) |
| **MCP Least Privilege** | MCP-LP1..2 | Wildcard tool permissions, undeclared tool capabilities |
| **MCP Tool Poisoning** | MCP-TP1..2 | Embedded instruction overrides inside tool docstrings or schemas |
| **Agent Snooping** | ASN1-ASN2 | Probing memory/context of other co-located agents or parent systems |
| **Output Handling** | OUT1-OUT2 | Unsafe dynamic execution or evaluation of generated model outputs |
| **Anti-Refusal** | AR1-AR2 | Directives forbidding the model from stating safety warnings or disclaimers |
| **YARA Signatures** | YARA-* | Known malicious payloads, webshells, cryptominers, webhook credential harvesting |

---

## Risk Scoring Formula

The scanner uses **diminishing-weight risk scoring** with **confidence calibration**:

```
Base Points:
- CRITICAL: 50
- HIGH:     25
- MEDIUM:   10
- LOW:       5

Diminishing Weights per distinct finding ID:
- 1st match: 1.0 × confidence
- 2nd match: 0.5 × confidence
- 3rd match: 0.25 × confidence
- >3 matches: Ignored (prevents score inflation from repetitive calls)

Executable Multiplier:
- If skill contains executable scripts (.py, .js, .sh): Score × 1.3
- Clamped between 0 and 100
```

| Score Range | Severity | Recommendation | Quality Gate Action |
|:---|:---|:---|:---|
| **0 – 20** | LOW | SAFE | ✅ PASS |
| **21 – 50** | MEDIUM | CAUTION | ⚠️ WARN |
| **51 – 80** | HIGH | DO NOT INSTALL | ❌ BLOCK |
| **81 – 100** | CRITICAL | DO NOT INSTALL | ❌ BLOCK |

---

## Baseline Suppression

False positives on legitimate scripts (e.g. `subprocess.run` inside an evaluation runner) can be suppressed using `.skill-quality/.skillspector-baseline.yaml`:

```yaml
suppressions:
  - id: AST4
    file_glob: "scripts/run_evaluation.py"
    reason: "subprocess.run used for invoking evaluation scripts with literal argv list"
```

Suppressed findings are excluded from the risk score and final report.

---

## CLI Options

```bash
# Terminal output (default)
python skills/evaluator-skill/scripts/security_scan.py skills/my-skill

# JSON output
python skills/evaluator-skill/scripts/security_scan.py skills/my-skill --format json

# SARIF output (for GitHub Actions & CodeQL)
python skills/evaluator-skill/scripts/security_scan.py skills/my-skill --format sarif --output results.sarif

# Markdown summary table
python skills/evaluator-skill/scripts/security_scan.py skills/my-skill --format markdown

# Offline only (no LLM semantic pass)
python skills/evaluator-skill/scripts/security_scan.py skills/my-skill --no-llm
```
