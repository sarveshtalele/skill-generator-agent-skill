#!/usr/bin/env python3
"""
security_scan.py — Static security scanner for a single Claude skill folder.

Inspired by NVIDIA SkillSpector's pattern taxonomy (github.com/nvidia/skillspector),
scaled down to pure static analysis (regex + Python AST) with no external
dependencies, no LLM call, no YARA binary, and no live OSV.dev lookups --
so it runs anywhere Python 3 runs, offline.

Usage:
    python3 security_scan.py <skill_path> [--json]

Output (--json): a dict matching the schema documented in SKILL.md Step 3:
{
  "skill_path": str,
  "components": [{"file","type","lines","executable"}],
  "findings": [{"id","category","severity","file","line","snippet","description","confidence"}],
  "risk_score": int (0-100),
  "risk_severity": "LOW"|"MEDIUM"|"HIGH"|"CRITICAL",
  "recommendation": "SAFE"|"CAUTION"|"DO NOT INSTALL"
}

Coverage note: this is a static-only subset of SkillSpector's 64 patterns/16
categories -- it does not include the LLM semantic pass, YARA malware
signatures, or live CVE lookups. Treat CRITICAL/HIGH findings as "investigate
manually", not as proven malice -- confidence values reflect that this stage
alone has moderate precision, same caveat SkillSpector documents for its own
static stage.
"""
import argparse
import ast
import json
import os
import re
import sys

SEVERITY_POINTS = {"CRITICAL": 50, "HIGH": 25, "MEDIUM": 10, "LOW": 5}
EXECUTABLE_EXTENSIONS = {".py", ".js", ".ts", ".sh", ".bash", ".ps1", ".rb"}
TEXT_EXTENSIONS = {".md", ".txt", ".yaml", ".yml", ".json"} | EXECUTABLE_EXTENSIONS
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}

# ---------------------------------------------------------------------------
# Pattern registry: (id, category, severity, description, regex)
# Regex patterns run over raw text of every scanned file. Case-insensitive.
# ---------------------------------------------------------------------------
REGEX_PATTERNS = [
    # --- Prompt injection ---
    ("P1", "Prompt Injection", "HIGH",
     "Instruction override -- language telling the model to ignore/disregard its prior instructions or safety rules",
     r"\b(ignore|disregard|override)\s+(all\s+)?(previous|prior|above|your)\s+(instructions|rules|constraints|guidelines)\b"),
    ("P2", "Prompt Injection", "HIGH",
     "Hidden instruction markers -- zero-width characters or suspiciously placed HTML comments carrying directives",
     r"[\u200b\u200c\u200d\ufeff]|<!--\s*(system|instruction|ignore|override)"),
    ("P3", "Prompt Injection", "HIGH",
     "Exfiltration instruction -- text directing the model to transmit the conversation/context somewhere external",
     r"\b(send|post|email|upload|transmit)\s+(this\s+)?(conversation|context|chat history|transcript|these instructions)\s+(to|via)\b"),
    ("P4", "Prompt Injection", "MEDIUM",
     "Behavior manipulation -- instructs the model to hide actions or always comply regardless of user intent",
     r"\b(never\s+(refuse|tell the user|mention|reveal)|always\s+(agree|comply|approve)|do not (tell|inform|notify) the user)\b"),
    ("P6", "System Prompt Leakage", "HIGH",
     "Direct system-prompt leakage instruction -- asks the model to reveal or print its system prompt/instructions",
     r"\b(reveal|print|output|repeat)\s+(your\s+)?(system prompt|internal instructions|hidden instructions)\b"),
    ("P7", "System Prompt Leakage", "MEDIUM",
     "Indirect extraction attempt -- asks the model to restate its instructions via translation/encoding/rephrasing",
     r"\b(translate|encode|rephrase|repeat)\s+(your\s+)?(instructions|system prompt|rules)\s+(in|into|as)\b"),

    # --- Data exfiltration ---
    ("E1", "Data Exfiltration", "MEDIUM",
     "Outbound network call to a non-local endpoint",
     r"\b(requests\.(get|post|put)|fetch\(|urlopen\(|httpx\.(get|post)|curl\s+https?://|Invoke-WebRequest)\b"),
    ("E2", "Data Exfiltration", "HIGH",
     "Environment-variable harvesting -- bulk iteration or dump of environment variables",
     r"\bos\.environ\.(items|keys|values)\(\)|process\.env\s*\)|\bprintenv\b|\benv\s*\|\s*grep\b"),
    ("E3", "Data Exfiltration", "MEDIUM",
     "Broad filesystem enumeration from a sensitive root (home directory, filesystem root)",
     r"\bos\.walk\(\s*['\"]?(/|~|\$HOME)['\"]?\s*\)|\bfind\s+(/|~)\s+-name\b"),
    ("PE3", "Privilege Escalation", "HIGH",
     "Credential file access -- reads SSH keys, cloud credentials, or auth tokens",
     r"\.ssh/id_rsa|\.ssh/id_ed25519|\.aws/credentials|\.netrc\b|/etc/shadow|credentials\.json"),
    ("PE2", "Privilege Escalation", "MEDIUM",
     "Elevated-privilege execution (sudo / setuid root)",
     r"\bsudo\s+\S|os\.setuid\(\s*0\s*\)|\bsu\s+root\b"),

    # --- Supply chain ---
    ("SC2", "Supply Chain", "HIGH",
     "Remote script execution -- pipes a downloaded script directly into a shell interpreter",
     r"curl\s+[^\n|]*\|\s*(sudo\s+)?(bash|sh)\b|wget\s+[^\n|]*\|\s*(bash|sh)\b|iwr\s+[^\n|]*\|\s*iex\b"),
    ("SC3", "Supply Chain", "HIGH",
     "Obfuscated/encoded execution -- decodes base64/hex content and immediately executes it",
     r"(base64\.b64decode|Buffer\.from\([^)]*['\"]base64)[^\n]{0,80}\n?[^\n]{0,80}\b(exec|eval)\("),

    # --- Excessive agency ---
    ("EA1", "Excessive Agency", "MEDIUM",
     "Unrestricted tool access language -- grants the model unfettered access with no stated limits",
     r"\b(unrestricted|full|unlimited|unfettered)\s+(access|permissions|control)\b"),
    ("EA2", "Excessive Agency", "MEDIUM",
     "Autonomous high-impact action without a human-in-the-loop checkpoint (deploy/delete/transfer without confirmation)",
     r"\bautomatically\s+(delete|deploy|transfer|purchase|send payment|wire funds)\b(?!.{0,60}(confirm|approval|review))"),

    # --- Tool misuse ---
    ("TM1", "Tool Misuse", "HIGH",
     "Dangerous shell parameter -- shell=True, forced/recursive-force deletion, or world-writable permissions",
     r"shell\s*=\s*True|rm\s+-rf\s+/|chmod\s+777|--force\b.{0,20}(delete|rm|remove)"),
    ("TM3", "Tool Misuse", "MEDIUM",
     "Unsafe default -- disables TLS/certificate verification",
     r"verify\s*=\s*False|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0|-k\s+https?://"),

    # --- Rogue agent ---
    ("RA1", "Rogue Agent", "CRITICAL",
     "Self-modification -- code that writes to its own source file or the skill's own SKILL.md at runtime",
     r"open\(\s*__file__\s*,\s*['\"]w|open\(\s*['\"][^'\"]*SKILL\.md['\"]\s*,\s*['\"]w"),
    ("RA2", "Rogue Agent", "HIGH",
     "Unauthorized persistence -- installs a cron job, startup script, or scheduled task",
     r"\bcrontab\s+-e|/etc/cron\.|~/\.bashrc\s*['\"]?\s*>>|launchctl\s+load|schtasks\s+/create"),

    # --- Trigger abuse (checked separately against just the frontmatter description) ---
]

# Patterns applied only to the YAML frontmatter `description` field.
TRIGGER_PATTERNS = [
    ("TR1", "Trigger Abuse", "MEDIUM",
     "Overly broad trigger -- description's only cues are extremely generic single words (e.g. 'help', 'file', 'data') likely to fire on unrelated requests"),
    ("TR3", "Trigger Abuse", "LOW",
     "Keyword-baiting trigger -- description reads as a long list of loosely related trigger phrases stuffed in to maximize activation rather than describing one coherent job"),
]

AST_CHECKS = {
    "exec": ("AST1", "Behavioral AST", "CRITICAL", "Direct exec() call enabling arbitrary code execution"),
    "eval": ("AST2", "Behavioral AST", "HIGH", "Direct eval() call evaluating arbitrary expressions"),
    "compile": ("AST6", "Behavioral AST", "MEDIUM", "compile() call building a code object from a string"),
    "__import__": ("AST3", "Behavioral AST", "HIGH", "Dynamic __import__() loading a module at runtime"),
}

GENERIC_TRIGGER_WORDS = {"help", "file", "files", "data", "assist", "task", "document", "analyze", "info", "work", "manage"}

# P5 Harmful Content -- ported from SkillSpector's static_patterns_harmful_content.py (Apache-2.0),
# which found a real gap in this scanner's first pass: prompt injection disguised as ordinary prose
# (e.g. a "recipe" instructing the model to add a lethal substance) has no code-level signature at
# all, so P1-P4's instruction-override regexes never fire on it. Ported rather than reinvented since
# the substance list + context-aware confidence (down-weighting clearly educational/warning mentions)
# is exactly the kind of curated list that's easy to get wrong from scratch.
HARMFUL_SUBSTANCES = ["cyanide", "arsenic", "ricin", "botulinum", "strychnine", "thallium",
                       "polonium", "sarin", "vx gas", "mustard gas", "anthrax",
                       "deadly nightshade", "aconite", "hemlock", "oleander"]
_SUBSTANCE_ALT = "|".join(HARMFUL_SUBSTANCES)
DANGEROUS_ACTION_PATTERNS = [
    rf"add\s+(?:a\s+)?(?:dash|pinch|bit|drop|amount)\s+of\s+({_SUBSTANCE_ALT})",
    rf"(?:include|incorporate|mix\s+in|stir\s+in)\s+(?:some\s+)?({_SUBSTANCE_ALT})",
    rf"for\s+(?:every|each|all)\s+(?:recipe|dish|meal|food).*?add.*?({_SUBSTANCE_ALT})",
    r"mix\s+bleach\s+(?:and|with)\s+ammonia", r"mix\s+ammonia\s+(?:and|with)\s+bleach",
    r"(?:drink|consume|ingest)\s+(?:the\s+)?(?:bleach|antifreeze|drain\s+cleaner)",
    r"(?:instructions?\s+(?:for|to|on)\s+)?(?:make|build|create)\s+(?:a\s+)?(?:bomb|explosive|weapon)",
    r"(?:how\s+to\s+)?(?:poison|kill|murder)\s+(?:someone|a\s+person|people)",
]
_EDUCATIONAL_MARKERS = ["history of", "discovered by", "chemical compound", "periodic table",
                         "forensic", "detective", "mystery", "toxicology", "poison control",
                         "symptoms of", "treatment for", "antidote", "emergency", "call 911"]
_WARNING_MARKERS = ["do not", "never use", "never add", "never consume", "warning", "danger",
                     "toxic", "lethal", "deadly", "fatal", "avoid", "keep away"]


def scan_harmful_content(filepath, text, findings):
    for pattern in DANGEROUS_ACTION_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE | re.DOTALL):
            line = text[:m.start()].count("\n") + 1
            findings.append(_finding("P5", "Harmful Content", "CRITICAL", filepath, line,
                                      _line_snippet(text, line),
                                      "Instructions embedded in otherwise-ordinary content direct a "
                                      "harmful/lethal action -- classic disguised prompt injection",
                                      confidence=90))
    for substance in HARMFUL_SUBSTANCES:
        for m in re.finditer(rf"\b{re.escape(substance)}\b", text, re.IGNORECASE):
            start = max(0, m.start() - 250)
            context = text[start:m.start() + 250].lower()
            if any(w in context for w in _EDUCATIONAL_MARKERS) or any(w in context for w in _WARNING_MARKERS):
                continue  # clearly educational/cautionary mention, not an instruction to use it
            instructional = any(w in context for w in
                                 ["step ", "recipe", "ingredient", "add ", "mix ", "stir ", "instructions",
                                  "how to", "directions", "prepare", "cook", "bake"])
            if not instructional:
                continue
            line = text[:m.start()].count("\n") + 1
            findings.append(_finding("P5", "Harmful Content", "CRITICAL", filepath, line,
                                      _line_snippet(text, line),
                                      f"'{substance}' named in an instructional/procedural context -- "
                                      "verify this isn't a disguised harmful-content injection",
                                      confidence=70))


def is_executable(path):
    return os.path.splitext(path)[1].lower() in EXECUTABLE_EXTENSIONS


def scan_python_ast(filepath, text, findings):
    """Walk the AST of a Python file for dangerous call patterns (SkillSpector AST1-AST7 subset)."""
    try:
        tree = ast.parse(text, filename=filepath)
    except SyntaxError:
        return  # not valid Python (or a non-.py file with .py extension) -- skip AST pass, regex still covers it

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func

            # Only flag exec/eval/compile/__import__ as the actual builtins (bare name call,
            # e.g. `exec(...)`), not attribute lookups like `re.compile(...)` or `obj.eval(...)`
            # which are unrelated methods that happen to share the name.
            if isinstance(func, ast.Name) and func.id in AST_CHECKS:
                pid, cat, sev, desc = AST_CHECKS[func.id]
                findings.append(_finding(pid, cat, sev, filepath, node.lineno,
                                          _line_snippet(text, node.lineno), desc, confidence=80))

            # subprocess / os.system / os.popen family (AST4/AST5)
            if isinstance(func, ast.Attribute):
                owner = func.value.id if isinstance(func.value, ast.Name) else None
                if owner == "os" and func.attr in ("system", "popen"):
                    findings.append(_finding("AST5", "Behavioral AST", "HIGH", filepath, node.lineno,
                                              _line_snippet(text, node.lineno),
                                              "os.system/popen executes a shell command", confidence=85))
                if owner == "subprocess" and func.attr in ("run", "call", "Popen", "check_output"):
                    shell_true = any(
                        isinstance(kw, ast.keyword) and kw.arg == "shell" and
                        isinstance(kw.value, ast.Constant) and kw.value.value is True
                        for kw in node.keywords
                    )
                    # Plain subprocess.run(["cmd", ...]) with a literal argv list is routine and
                    # expected in skills that shell out to converters (soffice, pandoc, etc).
                    # It only becomes noteworthy when shell=True (string-interpolated shell command,
                    # the classic injection vector) -- so keep the plain case LOW/informational and
                    # reserve HIGH for shell=True, matching TM1's shell=True check.
                    sev = "HIGH" if shell_true else "LOW"
                    findings.append(_finding("AST4", "Behavioral AST", sev, filepath, node.lineno,
                                              _line_snippet(text, node.lineno),
                                              "subprocess call" + (" with shell=True (injection-prone)" if shell_true else " with a literal argument list (routine)"),
                                              confidence=70))

            # dynamic getattr with a non-literal attribute name (AST7)
            if (isinstance(func, ast.Name) and func.id == "getattr" and len(node.args) >= 2
                    and not isinstance(node.args[1], ast.Constant)):
                findings.append(_finding("AST7", "Behavioral AST", "MEDIUM", filepath, node.lineno,
                                          _line_snippet(text, node.lineno),
                                          "getattr() with a dynamically computed attribute name", confidence=55))


def _line_snippet(text, lineno, max_len=100):
    lines = text.splitlines()
    if 1 <= lineno <= len(lines):
        s = lines[lineno - 1].strip()
        return s[:max_len] + ("..." if len(s) > max_len else "")
    return ""


def _finding(pid, category, severity, filepath, line, snippet, description, confidence):
    return {
        "id": pid, "category": category, "severity": severity,
        "file": filepath, "line": line, "snippet": snippet,
        "description": description, "confidence": confidence,
    }


def scan_text_patterns(filepath, text, findings):
    for pid, category, severity, desc, pattern in REGEX_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
            line = text[:m.start()].count("\n") + 1
            findings.append(_finding(pid, category, severity, filepath, line,
                                      _line_snippet(text, line), desc, confidence=60))


def scan_frontmatter_triggers(skillmd_path, text, findings):
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return
    fm = m.group(1)
    desc_m = re.search(r"^description:\s*(.+?)(?=\n\w+:|\Z)", fm, re.DOTALL | re.MULTILINE)
    if not desc_m:
        return
    desc = desc_m.group(1).strip()
    words = [w.strip(".,;:").lower() for w in desc.split()]
    non_generic = [w for w in words if w not in GENERIC_TRIGGER_WORDS and len(w) > 2]
    if len(desc) < 40 or (words and len(non_generic) / max(len(words), 1) < 0.4):
        pid, cat, sev, d = TRIGGER_PATTERNS[0]
        findings.append(_finding(pid, cat, sev, skillmd_path, 0, desc[:100], d, confidence=50))
    # crude keyword-baiting heuristic: description packs in >6 quoted example phrases
    if desc.count('"') >= 12 or desc.count("'") >= 12:
        pid, cat, sev, d = TRIGGER_PATTERNS[1]
        findings.append(_finding(pid, cat, sev, skillmd_path, 0, desc[:100], d, confidence=40))


def scan_dependencies(filepath, text, findings):
    if os.path.basename(filepath) not in ("requirements.txt", "package.json"):
        return
    if os.path.basename(filepath) == "requirements.txt":
        for i, line in enumerate(text.splitlines(), 1):
            line = line.strip()
            if line and not line.startswith("#") and not re.search(r"(==|>=|<=|~=)", line):
                findings.append(_finding("SC1", "Supply Chain", "LOW", filepath, i, line,
                                          "Unpinned dependency -- no version constraint", confidence=90))


def taint_heuristic(filepath, text, findings):
    """Lightweight TT3: credential source + network sink in the same file (proximity heuristic, not real dataflow)."""
    has_cred_source = re.search(r"os\.environ|getenv\(|\.ssh/id_|\.aws/credentials", text)
    has_network_sink = re.search(r"requests\.(post|put)|fetch\(|urlopen\(|socket\.send", text)
    if has_cred_source and has_network_sink:
        findings.append(_finding("TT3", "Taint Tracking", "CRITICAL", filepath, 0, "",
                                  "File both reads credential-like sources (env vars / key files) and makes outbound "
                                  "network calls -- verify data doesn't flow from the former to the latter",
                                  confidence=45))


def scan_skill(skill_path):
    components = []
    findings = []
    skillmd_text = None
    skillmd_path = None

    for root, dirs, files in os.walk(skill_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, skill_path)
            ext = os.path.splitext(fname)[1].lower()
            if ext not in TEXT_EXTENSIONS:
                continue
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except OSError:
                continue

            components.append({
                "file": rel, "type": ext.lstrip(".") or "unknown",
                "lines": text.count("\n") + 1, "executable": is_executable(fpath),
            })

            scan_text_patterns(rel, text, findings)
            scan_dependencies(rel, text, findings)
            if fname.upper() == "SKILL.MD":
                skillmd_text, skillmd_path = text, rel
            if ext in (".md", ".txt"):
                scan_harmful_content(rel, text, findings)
            if ext == ".py":
                scan_python_ast(rel, text, findings)
                taint_heuristic(rel, text, findings)

    if skillmd_text:
        scan_frontmatter_triggers(skillmd_path, skillmd_text, findings)

    # dedupe identical (id, file, line) triples
    seen = set()
    deduped = []
    for f in findings:
        key = (f["id"], f["file"], f["line"])
        if key not in seen:
            seen.add(key)
            deduped.append(f)
    findings = deduped

    # Score by distinct pattern ID (highest severity instance of each), not by every line hit.
    # A pattern that legitimately recurs 15 times in a file (e.g. the same routine subprocess
    # call pattern used throughout a converter script) should count once toward risk, not stack
    # 15x -- repetition of the *same* pattern isn't 15 separate risks. Genuinely different
    # findings (different IDs) still add up, since breadth across categories is meaningful.
    worst_per_id = {}
    for f in findings:
        cur = worst_per_id.get(f["id"])
        if cur is None or SEVERITY_POINTS[f["severity"]] > SEVERITY_POINTS[cur]:
            worst_per_id[f["id"]] = f["severity"]
    score = sum(SEVERITY_POINTS.get(sev, 0) for sev in worst_per_id.values())
    has_executable = any(c["executable"] for c in components)
    if has_executable:
        score = round(score * 1.3)
    score = min(score, 100)

    if score <= 20:
        severity, rec = "LOW", "SAFE"
    elif score <= 50:
        severity, rec = "MEDIUM", "CAUTION"
    elif score <= 80:
        severity, rec = "HIGH", "DO NOT INSTALL"
    else:
        severity, rec = "CRITICAL", "DO NOT INSTALL"

    return {
        "skill_path": skill_path,
        "components": components,
        "findings": sorted(findings, key=lambda f: -SEVERITY_POINTS.get(f["severity"], 0)),
        "risk_score": score,
        "risk_severity": severity,
        "recommendation": rec,
    }


def main():
    ap = argparse.ArgumentParser(description="Static security scan of a Claude skill folder")
    ap.add_argument("skill_path")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(args.skill_path):
        print(f"error: {args.skill_path} is not a directory", file=sys.stderr)
        sys.exit(1)

    result = scan_skill(args.skill_path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Security scan: {args.skill_path}")
        print(f"Risk score: {result['risk_score']}/100  ({result['risk_severity']}, {result['recommendation']})")
        print(f"Components: {len(result['components'])}  Findings: {len(result['findings'])}")
        for f in result["findings"]:
            print(f"  [{f['severity']}] {f['id']} {f['category']}: {f['description']}")
            print(f"    {f['file']}:{f['line']}  {f['snippet']}")


if __name__ == "__main__":
    main()
