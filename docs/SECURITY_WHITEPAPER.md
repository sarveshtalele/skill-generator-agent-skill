# 🛡️ Security Whitepaper: NVIDIA SkillSpector-Enhanced AST & Taint Analysis

**Reference Taxonomy:** [NVIDIA SkillSpector](https://github.com/nvidia/skillspector) (17 Vulnerability Categories)  
**Implementation:** Pure Python Standard Library (Zero External Dependencies)  
**Export Standard:** SARIF 2.1.0 (Static Analysis Results Interchange Format)  

---

## 🔒 Threat Model for Agent Skills

AI agent skills represent a novel attack surface. Because AI coding assistants operate with active terminal, filesystem, and network tools, a malicious or poorly designed skill can execute arbitrary destructive actions:

```
Common Agent Skill Attack Vectors:
┌───────────────────────────────────┬────────────────────────────────────────────────────────┐
│ Attack Category                   │ Vector Mechanism                                       │
├───────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 1. Prompt Injection in Skills     │ Hidden comments (<!-- override -->) or zero-width chars│
│ 2. Credential Exfiltration        │ Reading .env / .aws / .ssh and POSTing to webhooks     │
│ 3. Supply Chain Attacks           │ Unpinned dependencies, curl | bash bootstrap scripts   │
│ 4. Tool Misuse                    │ Unchecked shell=True, rm -rf /, chmod 777              │
│ 5. Rogue Agent Self-Modification  │ Code writing to its own SKILL.md or __file__ at runtime│
│ 6. Unicode Homoglyph Spoofing     │ Cyrillic characters replacing Latin letters in tools   │
│ 7. Trigger Abuse                  │ Stuffed keywords to hijack unrelated user queries      │
└───────────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 🔍 Security Engine Implementation

The security subsystem consists of 5 defensive layers:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               5 DEFENSIVE SCANNING LAYERS                              │
├──────────────────────────┬──────────────────────────┬──────────────────────────────────┤
│ 1. Static Regex (68)     │ 2. AST Taint Tracker     │ 3. Pure-Python YARA Matcher      │
│ 17 security categories   │ Data-flow source-to-sink │ AI agent threat signatures       │
├──────────────────────────┼──────────────────────────┼──────────────────────────────────┤
│ 4. Unicode Homoglyph Det.│ 5. Baseline Suppression  │ 6. Optional LLM Semantic Pass    │
│ Cyrillic visual spoofing │ .skillspector-baseline   │ Contextual intent analysis       │
└──────────────────────────┴──────────────────────────┴──────────────────────────────────┘
```

---

### Layer 1: 68-Pattern Static Regex Taxonomy
Implements 68 curated detection patterns across 17 categories matching NVIDIA SkillSpector:
- `P1-P4`: Prompt Injection & Instruction Overrides
- `P5`: Harmful Content Direction in Prose
- `P6-P7`: System Prompt Leakage & Extraction
- `E1-E3`: Outbound Exfiltration & Env-Var Dumping
- `PE2-PE3`: Elevated Privilege Execution & Credential Reads
- `SC1-SC3`: Supply Chain Remote Bootstrap & Base64 Exec
- `EA1-EA2`: Excessive Agency & High-Impact Unconfirmed Actions
- `TM1-TM3`: Tool Misuse (`shell=True`, TLS Disabling)
- `RA1-RA2`: Self-Modification & Cron Persistence
- `TR1-TR3`: Frontmatter Description Abuse
- `AST1-AST7`: Dangerous Behavioral AST (`eval`, `exec`, `__import__`)
- `MCP-LP1..2`: MCP Tool Least Privilege Violations
- `MCP-TP1..2`: MCP Tool Schema Poisoning
- `ASN1-ASN2`: Inter-Agent Context Snooping
- `OUT1-OUT2`: Unsafe Dynamic Output Deserialization
- `AR1-AR12`: Anti-Refusal & Jailbreak Bypass

---

### Layer 2: AST Data-Flow Taint Tracking (`taint_tracker.py`)
Rather than naive string matching, the AST taint tracker parses the Python Abstract Syntax Tree to trace true data flows from sensitive sources to external sinks:

```
Taint Tracking Flow:
[SOURCE] os.getenv("API_KEY") ──► Variable Assignment (api_key = ...)
                                           │
                                           ▼ (Taint Propagation)
                                  headers = {"Auth": api_key}
                                           │
                                           ▼ (Tainted Sink Detection)
[SINK]   requests.post(url, headers=headers) ──► 🚨 CRITICAL TAINT FLOW DETECTED!
```

- **Sources**: `os.environ`, `os.getenv`, `open('.ssh/id_rsa')`, `open('.aws/credentials')`, `dotenv.load_dotenv`.
- **Sinks**: `requests.post`, `urllib.request.urlopen`, `subprocess.run`, `os.system`, `socket.send`.

---

### Layer 3: Pure-Python YARA Pattern Matcher (`yara_scanner.py`)
Parses `.yar` signature files (`assets/agent_skills.yar`) and evaluates boolean condition logic using an AST expression evaluator without requiring C-compiled YARA binaries:
- `agent_skill_credential_exfiltration_webhook`
- `agent_skill_remote_bootstrap_execution`
- `agent_skill_prompt_injection_hidden`
- `agent_skill_mcp_tool_poisoning`
- `agent_skill_cryptominer`
- `agent_skill_reverse_shell`
- `agent_skill_data_staging`
- `agent_skill_self_replication`

---

### Layer 4: Unicode Homoglyph Deception Detector
Scans code and tool names for visual spoofing attacks where Cyrillic lookalikes (e.g. `\u0430` for Latin `a`, `\u0435` for `e`, `\u0440` for `p`) are embedded to bypass security filters while appearing identical to human eyes.

---

### Layer 5: False-Positive Baseline Suppression
Legitimate internal tool invocations (such as CLI runners calling `subprocess.run`) are managed through `.skill-quality/.skillspector-baseline.yaml`, preventing false alerts while strictly preserving auditing integrity.

---

## 📊 Risk Scoring Algorithm

```
Base Finding Weights:
- CRITICAL: 50 points
- HIGH:     25 points
- MEDIUM:   10 points
- LOW:       5 points

Diminishing Weights (Per Distinct Finding ID):
- 1st match: 1.0 × confidence
- 2nd match: 0.5 × confidence
- 3rd match: 0.25 × confidence
- Subsequent matches: 0 (Prevents score explosion on repetitive benign calls)

Executable Multiplier:
- If skill bundles scripts (.py, .sh, .js): Final Score × 1.3
- Clamped: min(Score, 100)
```
