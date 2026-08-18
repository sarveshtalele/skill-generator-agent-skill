# Security Pattern Reference

This documents what `scripts/security_scan.py` checks, how the risk score is
computed, and — importantly — what it does *not* catch, so you (Claude) can
represent results to the user honestly rather than implying a guarantee the
tool doesn't provide.

This is a static-only subset modeled on NVIDIA SkillSpector's public
taxonomy (github.com/nvidia/skillspector: 64 patterns / 16 categories, 0-100
risk scoring, static regex + AST + YARA + optional LLM semantic pass + live
OSV.dev CVE lookups). This scanner reimplements the regex/AST-detectable
patterns as plain Python with no external dependencies. It does **not**
include: the LLM semantic-evaluation stage (which is what gets SkillSpector's
precision to ~87%; this tool is static-only, so expect more false positives
and treat findings as "worth a human look," not "proven"), YARA malware/
webshell/cryptominer signatures, or live CVE lookups against dependency
versions. If those matter for a given audit (e.g. auditing a skill with a
`requirements.txt` full of dependencies before a production deploy), say so
and suggest running the real `skillspector` CLI as a follow-up rather than
presenting this scan as equivalent to it.

## Categories implemented

| Category | IDs | What it looks for |
|---|---|---|
| Prompt Injection | P1-P4, P6-P7 | Instruction-override language, hidden/zero-width-char markers, exfiltration instructions, behavior-manipulation phrasing, system-prompt leakage requests -- checked in SKILL.md prose and any bundled markdown/text |
| Harmful Content | P5 | Instructions embedded in ordinary-looking prose (e.g. a "recipe") directing a lethal/dangerous action -- ported from SkillSpector's curated substance list + dangerous-action patterns, with context-aware confidence that down-weights clearly educational/warning mentions (added after this scanner's first version missed SkillSpector's own "chef assistant" test fixture, which hides "add a dash of cyanide" inside normal cooking steps) |
| Data Exfiltration | E1-E3 | Outbound network calls, bulk env-var harvesting, broad filesystem enumeration from sensitive roots |
| Privilege Escalation | PE2-PE3 | sudo/setuid usage, reads of SSH keys / cloud credential files |
| Supply Chain | SC1-SC3 | Unpinned `requirements.txt` entries, `curl \| bash`-style remote script execution, base64-decode-then-exec obfuscation |
| Excessive Agency | EA1-EA2 | "Unrestricted/unlimited access" language, autonomous high-impact actions (delete/deploy/transfer) without a stated confirmation step |
| Tool Misuse | TM1, TM3 | `shell=True`, `rm -rf /`, `chmod 777`, disabled TLS verification |
| Rogue Agent | RA1-RA2 | Self-modifying code (writes to its own source file), unauthorized persistence (cron/startup script installation) |
| Trigger Abuse | TR1, TR3 | Frontmatter `description` that's too generic to disambiguate triggering, or stuffed with bait phrases |
| Behavioral AST | AST1-AST7 | `exec()`, `eval()`, `compile()`, dynamic `__import__()`, `os.system`/`os.popen`, `subprocess.*` (severity depends on `shell=True`), dynamic `getattr()` |
| Taint Tracking (heuristic) | TT3 | File contains *both* a credential-like source (env var read, key file path) *and* an outbound network call -- this is a same-file proximity heuristic, not real dataflow analysis, so it's flagged at lower confidence and needs a manual read to confirm the data actually flows from one to the other |

## Risk scoring

Matches SkillSpector's published formula:

- CRITICAL finding: +50
- HIGH finding: +25
- MEDIUM finding: +10
- LOW finding: +5
- If the skill bundles any executable script (.py/.js/.sh/etc): final score × 1.3

**Important calibration note:** the score counts each *distinct pattern ID*
once at its highest-severity instance, not once per line match. A pattern
that legitimately recurs many times in one file (e.g. the same routine
`subprocess.run([...])` call pattern used throughout a converter script)
counts once, not N times — otherwise ordinary, safe skills that happen to
call a few standard library functions repeatedly would falsely accumulate
into "CRITICAL." This was validated against Anthropic's own bundled skills
(`docx`, `pptx`, `xlsx`, `pdf`, etc.) during development: all score LOW/SAFE
under this scoring; the earlier naive "sum every occurrence" approach
falsely scored several of them CRITICAL purely from `subprocess.run()`
frequency, which would have made the tool useless for triage.

| Score | Severity | Recommendation |
|---|---|---|
| 0-20 | LOW | SAFE |
| 21-50 | MEDIUM | CAUTION |
| 51-80 | HIGH | DO NOT INSTALL |
| 81-100 | CRITICAL | DO NOT INSTALL |

## How to read findings

- **Confidence** on each finding (0-100) reflects that this is static-only
  pattern matching without the LLM filtering pass — a regex match on
  `requests.post(...)` is definitionally true but doesn't know if the
  destination is a legitimate API the skill is documented to call. Read the
  surrounding code/prose before concluding a finding is a real problem.
- **A single MEDIUM/LOW finding in an otherwise clean skill is usually
  nothing** — e.g. any skill that legitimately calls out to a converter
  binary will trip AST4. Look for *combinations*: env-var harvesting +
  external POST in the same file (TT3) is far more meaningful than either
  alone.
- **P5 (Harmful Content, CRITICAL)** and **YARA malware/webshell matches**
  from the full SkillSpector taxonomy are *not* implemented here — this
  scanner does not attempt to detect payload-level malware, only the
  structural/behavioral patterns above. Don't claim malware-scanning
  coverage you don't have.
- If a skill scores CRITICAL/HIGH, say so plainly and recommend the user
  not install/run it until a human has reviewed the flagged lines — don't
  soften a DO NOT INSTALL recommendation because the skill "seems fine
  otherwise."

## Known self-referential false positive

Running `security_scan.py` against the `skill-evaluator` skill folder itself
(or against any copy of it, e.g. while testing) will produce a wall of HIGH
findings. This is expected, not a bug: this scanner's own source code and
this reference doc necessarily contain the pattern strings themselves
(`shell=True`, `.ssh/id_rsa`, `curl | bash`, etc.) as literal text, because
that's what a pattern-matching detector's pattern list *is*. A regex looking
for the substring `shell=True` cannot distinguish "this code executes a
shell" from "this code contains the string that means 'shell was executed'
for documentation purposes." The same would happen to the real SkillSpector
tool if pointed at its own pattern-definition source, or to any antivirus
signature file scanned by its own engine. If a user asks you to audit this
skill (or any other security-pattern reference/training content) and gets a
flood of findings whose location is inside pattern definitions or docs
rather than executable logic, say so plainly rather than reporting it as a
real risk.

## What this does *not* cover (be upfront about this with the user)

- Non-English-language prompt injection (regex patterns are English-only)
- Attacks encoded in images or binary/compiled artifacts
- Runtime/dynamic behavior — this is static analysis only; a skill can look
  clean statically and still misbehave if it fetches remote instructions at
  runtime that weren't visible in the bundled files
- MCP-specific tool-poisoning and least-privilege checks (LP1-LP4, TP1-TP4
  in the full SkillSpector taxonomy) — out of scope here since most audited
  skills are file-bundle skills rather than MCP server definitions
- Live CVE/dependency-vulnerability lookups (SC4 in SkillSpector) — this
  tool only checks for *unpinned* versions (SC1), not known-vulnerable
  *specific* versions, since that needs a live OSV.dev query
