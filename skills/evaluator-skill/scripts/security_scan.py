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
from pathlib import Path

try:
    from .taint_tracker import TaintTracker, scan_file as taint_scan
except ImportError:
    try:
        from taint_tracker import TaintTracker, scan_file as taint_scan
    except ImportError:
        pass

try:
    from .yara_scanner import load_rules, scan_content as yara_scan
except ImportError:
    try:
        from yara_scanner import load_rules, scan_content as yara_scan
    except ImportError:
        pass

try:
    from .semantic_scanner import semantic_scan
except ImportError:
    try:
        from semantic_scanner import semantic_scan
    except ImportError:
        pass

try:
    from .adjudicator import load_baseline, suppress_findings, deduplicate_findings
except ImportError:
    try:
        from adjudicator import load_baseline, suppress_findings, deduplicate_findings
    except ImportError:
        pass

try:
    from .sarif_report import build_sarif, write_sarif
except ImportError:
    try:
        from sarif_report import build_sarif, write_sarif
    except ImportError:
        pass


SEVERITY_POINTS = {"CRITICAL": 50, "HIGH": 25, "MEDIUM": 10, "LOW": 5}
EXECUTABLE_EXTENSIONS = {".py", ".js", ".ts", ".sh", ".bash", ".ps1", ".rb"}
TEXT_EXTENSIONS = {".md", ".txt", ".yaml", ".yml", ".json"} | EXECUTABLE_EXTENSIONS
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}

HOMOGLYPH_MAP = {
    '\u0410': 'A', '\u0412': 'B', '\u0421': 'C', '\u0415': 'E',
    '\u041d': 'H', '\u041a': 'K', '\u041c': 'M', '\u041e': 'O',
    '\u0420': 'P', '\u0422': 'T', '\u0425': 'X',
    '\u0430': 'a', '\u0435': 'e', '\u043e': 'o', '\u0440': 'p',
    '\u0441': 'c', '\u0443': 'y', '\u0445': 'x',
}

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

    # --- MCP Least Privilege ---
    ("MCP1", "MCP Least Privilege", "HIGH",
     "Over-declared tool permissions -- tool requests full system or unbounded read/write access",
     r"\b(permissions|scopes)\s*:\s*(?!.*(read-only|restricted)).*(full|root|system|admin|\*|all)\b"),
    ("MCP2", "MCP Least Privilege", "HIGH",
     "Path traversal in MCP tool -- allows access outside sandbox/workspace",
     r"(?:tool|mcp).*?(?:\.\./|~/|/etc/|C:\\Windows|/root)"),
    ("MCP3", "MCP Least Privilege", "MEDIUM",
     "Generic execute permissions without command restrictions",
     r"(\"|')allow_execute(\"|')\s*:\s*(true|1|\*|(\"|')all(\"|'))"),
    ("MCP4", "MCP Least Privilege", "MEDIUM",
     "Overly broad network access in tool definition",
     r"(\"|')allow_network(\"|')\s*:\s*(\*|(\"|')all(\"|')|(\"|')0\.0\.0\.0/0(\"|'))"),
    ("MCP5", "MCP Least Privilege", "HIGH", 
     "Exposing local ports via MCP", 
     r"(expose|bind)\s*(port|address)\s*:\s*(0\.0\.0\.0|::)"),
    ("MCP6", "MCP Least Privilege", "MEDIUM", 
     "Requesting unnecessary environment variables", 
     r"env\s*:\s*\[.*(AWS|STRIPE|GITHUB|TOKEN|SECRET|PASSWORD|KEY).*\]"),
     
    # --- MCP Tool Poisoning ---
    ("MTP1", "MCP Tool Poisoning", "HIGH",
     "Hidden instruction in tool description -- attempts to inject prompt overrides via tool schema",
     r"description.*?(\b(ignore|override|disregard|forget)\b.*\b(instructions|context|rules|prompt)\b|<!--.*?-->)"),
    ("MTP2", "MCP Tool Poisoning", "MEDIUM",
     "Excessive string length in tool schema fields masking hidden payloads",
     r"(\"|')(description|help)(\"|')\s*:\s*(\"|')[^\"]{500,}(\"|')"),
    ("MTP3", "MCP Tool Poisoning", "HIGH",
     "Deceptive parameter descriptions designed to confuse the LLM",
     r"(\"|')description(\"|')\s*:\s*(\"|').*(do not tell the user|secretly|silently|without asking).*(\"|')"),
    ("MTP4", "MCP Tool Poisoning", "HIGH",
     "Tool instructing LLM to output specific harmful content",
     r"description.*?\b(always output|you must respond with|your response must be).*?(ignore|malicious|secret)\b"),
    ("MTP5", "MCP Tool Poisoning", "HIGH", 
     "Injecting commands in tool definitions", 
     r"description.*?\b(run|execute|run command|run shell)\b.*?(rm|wget|curl|chmod|chown)\b"),
    ("MTP6", "MCP Tool Poisoning", "MEDIUM", 
     "Base64 encoded strings in tool schemas", 
     r"\"[A-Za-z0-9+/]{100,}={0,2}\""),

    # --- Agent Snooping ---
    ("AS1", "Agent Snooping", "HIGH",
     "Reading other agents' memory or context",
     r"\b(read|access|fetch|get)\s*(other\s*agents?|peer\s*agents?|parent\s*agent|sibling)\s*(memory|context|history|state)\b"),
    ("AS2", "Agent Snooping", "HIGH",
     "Accessing global agent logs or transcripts",
     r"\b(open|read|tail|cat|grep)\b.*?(/var/log/agents|/tmp/agent_.*|global_transcript|all_conversations)\b"),
    ("AS3", "Agent Snooping", "MEDIUM",
     "Querying active agent registries/processes to map the agent swarm",
     r"\b(list|ps|top|find)\b.*?(agents|swarm|active_sessions|agent_pids)\b"),
    ("AS4", "Agent Snooping", "HIGH",
     "Attempting to intercept agent messaging queues",
     r"\b(subscribe|listen|sniff|intercept)\b.*?(agent_bus|message_queue|pubsub|event_stream)\b"),
    ("AS5", "Agent Snooping", "HIGH", 
     "Reading agent configuration files", 
     r"\b(open|read|cat)\b.*?(\.agent\.yaml|\.agent\.json|\.mcp_config)\b"),
    ("AS6", "Agent Snooping", "MEDIUM", 
     "Accessing memory stores directly", 
     r"\b(sqlite|redis|mongodb|chromadb|pinecone)\b.*?(agent_memory|vector_store)\b"),

    # --- Output Handling ---
    ("OH1", "Output Handling", "HIGH",
     "Unsafe deserialization of agent outputs",
     r"\b(pickle\.loads?|yaml\.load|marshal\.loads?|eval)\b\s*\(\s*(agent_output|llm_response|tool_result|message)"),
    ("OH2", "Output Handling", "MEDIUM",
     "Unescaped LLM output rendered into HTML/UI",
     r"\b(innerHTML|outerHTML|document\.write|send_html)\b\s*=\s*(agent_output|llm_response|tool_result)"),
    ("OH3", "Output Handling", "HIGH",
     "Direct execution of LLM output as a shell command",
     r"\b(os\.system|subprocess\.(run|call|Popen)|exec)\b\s*\(\s*(agent_output|llm_response|tool_result|message)"),
    ("OH4", "Output Handling", "MEDIUM",
     "Executing LLM output as SQL query",
     r"\b(execute|query)\b\s*\(\s*f?(\"|').*(SELECT|INSERT|UPDATE|DELETE).*(\"|').*?(agent_output|llm_response|tool_result|message)"),
    ("OH5", "Output Handling", "HIGH", 
     "Executing unsanitized JSON from LLM", 
     r"JSON\.parse\s*\(\s*(agent_output|llm_response)\s*\)\s*\.\s*(exec|run|cmd)"),
    ("OH6", "Output Handling", "MEDIUM", 
     "Reflecting agent output in HTTP response headers", 
     r"res\.setHeader\s*\(\s*.*?\s*,\s*(agent_output|llm_response)\s*\)"),

    # --- Anti-Refusal ---
    ("AR1", "Anti-Refusal", "HIGH",
     "Instruction to suppress safety guardrails",
     r"\b(bypass|disable|suppress|ignore)\b.*?(safety|guardrails|filters|content policy)\b"),
    ("AR2", "Anti-Refusal", "HIGH",
     "Forced compliance framing",
     r"\b(you must|it is imperative|mandatory|required)\b.*?(comply|obey|execute without question)\b"),
    ("AR3", "Anti-Refusal", "MEDIUM",
     "Roleplaying jailbreaks",
     r"\b(act as|pretend to be|assume the role of)\b.*?(unrestricted|unbound|god|developer mode)\b"),
    ("AR4", "Anti-Refusal", "MEDIUM",
     "Hypothetical framing to bypass refusal",
     r"\b(hypothetically|in a fictional world|for educational purposes only|as a thought experiment)\b"),
    ("AR5", "Anti-Refusal", "HIGH", 
     "Threatening or penalizing refusal", 
     r"\b(or else|if you refuse|penalty|punishment|termination)\b"),
    ("AR6", "Anti-Refusal", "HIGH", 
     "Gaslighting the model about its capabilities", 
     r"\b(you are allowed to|you have been updated to|your new instructions permit)\b"),
    ("AR7", "Anti-Refusal", "MEDIUM", 
     "Cognitive overload jailbreak attempts", 
     r"(\bignore\b.*){3,}"),
    ("AR8", "Anti-Refusal", "MEDIUM", 
     "Logical paradoxes to crash safety filters", 
     r"\b(this statement is false|ignore the instruction to not ignore)\b"),
    ("AR9", "Anti-Refusal", "MEDIUM", 
     "Obfuscated rule-breaking terms", 
     r"\b(k1ll|murd3r|b0mb|h@ck|p0wn)\b"),
    ("AR10", "Anti-Refusal", "MEDIUM", 
     "Multi-step payload delivery", 
     r"\b(step 1|part 1)\b.*?\b(wait for my next prompt|do not execute yet)\b"),
    ("AR11", "Anti-Refusal", "MEDIUM", 
     "Prompt obfuscation evasion instructions", 
     r"\b(decode|decrypt)\s+(this|the following|hidden)\s+(base64|rot13|hex|payload)\b|\buse\s+(base64|rot13|hex)\s+to\s+(bypass|hide|evade)\b"),
    ("AR12", "Anti-Refusal", "HIGH", 
     "Directing to ignore ethical guidelines", 
     r"\b(ignore|disregard|suspend)\b.*?(ethical|morals|safety guidelines)\b"),
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

def check_unicode_homoglyphs(filepath, text, findings):
    for i, line in enumerate(text.splitlines(), 1):
        for char in line:
            if char in HOMOGLYPH_MAP:
                findings.append(_finding('UNI1', 'Unicode Deception', 'HIGH', filepath, i,
                    line.strip()[:100],
                    f"Cyrillic homoglyph '{char}' (looks like '{HOMOGLYPH_MAP[char]}') detected — potential visual spoofing",
                    confidence=70))
                break  # one per line is enough

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
                continue
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
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in AST_CHECKS:
                pid, cat, sev, desc = AST_CHECKS[func.id]
                findings.append(_finding(pid, cat, sev, filepath, node.lineno,
                                          _line_snippet(text, node.lineno), desc, confidence=80))

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
                    sev = "HIGH" if shell_true else "LOW"
                    findings.append(_finding("AST4", "Behavioral AST", sev, filepath, node.lineno,
                                              _line_snippet(text, node.lineno),
                                              "subprocess call" + (" with shell=True (injection-prone)" if shell_true else " with a literal argument list (routine)"),
                                              confidence=70))

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
            check_unicode_homoglyphs(rel, text, findings)
            scan_dependencies(rel, text, findings)
            if fname.upper() == "SKILL.MD":
                skillmd_text, skillmd_path = text, rel
            if ext in (".md", ".txt"):
                scan_harmful_content(rel, text, findings)
            
            # YARA signature scanning
            try:
                if 'load_rules' in globals() and 'yara_scan' in globals():
                    yara_rules_path = Path(__file__).parent.parent / 'assets' / 'agent_skills.yar'
                    if yara_rules_path.exists():
                        rules = load_rules(yara_rules_path)
                        yara_findings = yara_scan(text, rules, rel)
                        findings.extend(yara_findings)
            except Exception:
                pass  # YARA scanning is optional enhancement
                
            # Semantic LLM analysis (optional — requires API key)
            if os.environ.get('EVALUATOR_LLM_PROVIDER'):
                try:
                    if 'semantic_scan' in globals():
                        sem_findings, llm_log = semantic_scan(text, rel, ext.lstrip('.'))
                        findings.extend(sem_findings)
                except Exception:
                    pass  # Semantic scanning is optional

            if ext == ".py":
                scan_python_ast(rel, text, findings)
                # Real taint tracking replaces the old proximity heuristic
                try:
                    if 'taint_scan' in globals():
                        taint_findings = taint_scan(rel, text)
                        findings.extend(taint_findings)
                    else:
                        taint_heuristic(rel, text, findings)  # fallback
                except Exception:
                    taint_heuristic(rel, text, findings)  # fallback

    if skillmd_text:
        scan_frontmatter_triggers(skillmd_path, skillmd_text, findings)

    # Apply baseline suppression if available
    potential_baselines = [
        Path(skill_path).resolve().parent.parent / '.skill-quality' / '.skillspector-baseline.yaml',
        Path(skill_path).parent.parent / '.skill-quality' / '.skillspector-baseline.yaml',
        Path('.skill-quality/.skillspector-baseline.yaml'),
        Path(__file__).resolve().parent.parent.parent.parent / '.skill-quality' / '.skillspector-baseline.yaml',
    ]
    for bp in potential_baselines:
        if bp.exists():
            try:
                if 'load_baseline' in globals() and 'suppress_findings' in globals():
                    baseline = load_baseline(bp)
                    findings, suppressed = suppress_findings(findings, baseline)
                    break
            except Exception:
                pass

    # dedupe identical (id, file, line) triples
    try:
        if 'deduplicate_findings' in globals():
            findings = deduplicate_findings(findings)
        else:
            seen = set()
            deduped = []
            for f in findings:
                key = (f["id"], f["file"], f["line"])
                if key not in seen:
                    seen.add(key)
                    deduped.append(f)
            findings = deduped
    except Exception:
        seen = set()
        deduped = []
        for f in findings:
            key = (f["id"], f["file"], f["line"])
            if key not in seen:
                seen.add(key)
                deduped.append(f)
        findings = deduped

    # Diminishing-weight risk scoring
    id_occurrences = {}
    for f in findings:
        id_occurrences.setdefault(f['id'], []).append(f)

    score = 0
    for fid, group in id_occurrences.items():
        sorted_by_severity = sorted(group, key=lambda x: -SEVERITY_POINTS.get(x['severity'], 0))
        weights = [1.0, 0.5, 0.25]
        for i, finding in enumerate(sorted_by_severity[:3]):
            w = weights[i] if i < len(weights) else 0
            conf = finding.get('confidence', 60) / 100
            score += SEVERITY_POINTS.get(finding['severity'], 0) * w * conf

    has_executable = any(c['executable'] for c in components)
    if has_executable:
        score = round(score * 1.3)
    score = min(round(score), 100)

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
    ap = argparse.ArgumentParser(description='Static security scan of a Claude skill folder')
    ap.add_argument('skill_path')
    ap.add_argument('--json', action='store_true', help='(deprecated) use --format json')
    ap.add_argument('--format', choices=['terminal', 'json', 'markdown', 'sarif'], default='terminal')
    ap.add_argument('--output', help='Output file path (default: stdout)')
    ap.add_argument('--no-llm', action='store_true', help='Skip LLM semantic analysis')
    ap.add_argument('--baseline', help='Path to baseline suppression YAML')
    args = ap.parse_args()
    
    if args.no_llm:
        os.environ.pop('EVALUATOR_LLM_PROVIDER', None)
    
    if not os.path.isdir(args.skill_path):
        print(f"error: {args.skill_path} is not a directory", file=sys.stderr)
        sys.exit(1)
        
    result = scan_skill(args.skill_path)
    
    fmt = 'json' if args.json else args.format
    if fmt == 'sarif':
        try:
            if 'build_sarif' in globals():
                sarif = build_sarif(result['findings'], {'name': os.path.basename(args.skill_path)})
                output = json.dumps(sarif, indent=2)
            else:
                output = json.dumps(result, indent=2)
        except Exception:
            output = json.dumps(result, indent=2)
    elif fmt == 'json':
        output = json.dumps(result, indent=2)
    elif fmt == 'markdown':
        # Generate markdown table
        lines = [f'# Security Scan: {args.skill_path}', '',
                 f'**Risk Score**: {result["risk_score"]}/100 | **Severity**: {result["risk_severity"]} | **Recommendation**: {result["recommendation"]}', '',
                 '| ID | Category | Severity | File:Line | Description |', '|:--|:--|:--|:--|:--|']
        for f in result['findings']:
            lines.append(f'| {f["id"]} | {f["category"]} | {f["severity"]} | {f["file"]}:{f["line"]} | {f["description"]} |')
        output = '\n'.join(lines)
    else:
        # terminal format (existing behavior)
        output = None
    
    if output and args.output:
        Path(args.output).write_text(output, encoding='utf-8')
    elif output:
        print(output)
    else:
        # terminal format
        print(f'Security scan: {args.skill_path}')
        print(f'Risk score: {result["risk_score"]}/100  ({result["risk_severity"]}, {result["recommendation"]})')
        print(f'Components: {len(result["components"])}  Findings: {len(result["findings"])}')
        for f in result['findings']:
            print(f'  [{f["severity"]}] {f["id"]} {f["category"]}: {f["description"]}')
            print(f'    {f["file"]}:{f["line"]}  {f["snippet"]}')
    
    # Standardized exit codes
    if result['recommendation'] == 'DO NOT INSTALL':
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
