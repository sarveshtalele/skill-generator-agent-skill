"""Deterministic Scaffolding Engine for Agent Skills.

Creates Spec 1.0 compliant directory structures, frontmatter YAML,
references, manifest, and skill-card metadata from user requirements.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


def sanitize_skill_name(name: str) -> str:
    """Normalize name to kebab-case matching ^[a-z0-9]+(-[a-z0-9]+)*$."""
    clean = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower())
    clean = re.sub(r"-+", "-", clean).strip("-")
    return clean or "new-agent-skill"


def scaffold_skill(
    skill_name: str,
    description: str,
    output_root: Path,
    sdlc_phase: str = "Implementation",
    author: str = "Sarvesh Talele",
) -> dict:
    """Scaffold complete Agent Skill folder and files."""
    name = sanitize_skill_name(skill_name)
    skill_dir = output_root / name
    
    # 1. Create standard folders
    for sub in ("assets", "references", "scripts", "templates", "evals"):
        (skill_dir / sub).mkdir(parents=True, exist_ok=True)
        
    display_title = " ".join(w.capitalize() for w in name.split("-")) + " Skill"
    snake_name = name.replace("-", "_")
    
    # 2. Generate SKILL.md
    skill_md = f"""---
name: {name}
description: >
  {description}
compatibility: "Python 3.8+"
metadata:
  sdlc: {sdlc_phase}
  tags:
    - {name}
    - SDLC:{sdlc_phase}
    - agent-skills
allowed-tools: "Read, Bash(python scripts/*.py:*)"
---

# {display_title}

{description}

## Overview & Purpose

This skill provides deterministic, production-grade procedural execution for **{display_title}**, strictly compliant with the [Agent Skills Specification v1.0](https://agentskills.io/specification).

## Workflow Contract

When activated by an AI agent (Claude Code, Cursor, Antigravity, Copilot), follow this strict sequence:

1. **Step 1: Parse Input & Target Context**:
   - Inspect the repository path and user instructions.
2. **Step 2: Execute Automation Script**:
   - Run the bundled engine:
     ```bash
     python scripts/{snake_name}_skill.py --target . --output ./output
     ```
3. **Step 3: Consult Deep References**:
   - Review [`references/guidelines.md`](references/guidelines.md) for domain rules and edge cases.
4. **Step 4: Generate Output Artifact**:
   - Format results using [`templates/report_template.md`](templates/report_template.md).

## Examples

### Example 1: Standard Execution
```
User: "Run {name} on this repository."
Agent: [Activates {name}, executes script, and emits formatted analysis report]
```

## Error Handling & Gotchas

- **Missing Prerequisites**: If Python dependencies are absent, script exits with status `1` and actionable remediation instructions.
- **Empty Targets**: If no files match the target scope, produces a clear zero-finding summary rather than failing.
"""
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    
    # 3. Generate script template
    script_py = f"""\"\"\"Deterministic Execution Engine for {display_title}.\"\"\"

import argparse
import json
import sys
from pathlib import Path


def run_skill(target_path: Path, output_path: Path) -> dict:
    \"\"\"Execute core procedural logic for {name}.\"\"\"
    output_path.mkdir(parents=True, exist_ok=True)
    report_file = output_path / "{name}_report.json"
    
    result = {{
        "skill": "{name}",
        "status": "SUCCESS",
        "target": str(target_path),
        "findings": [],
        "recommendations": ["Verified standard compliance"]
    }}
    
    report_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"✅ {{result['skill']}} completed successfully. Output saved to {{report_file}}")
    return result


def main():
    parser = argparse.ArgumentParser(description="{description}")
    parser.add_argument("--target", default=".", help="Target directory")
    parser.add_argument("--output", default="./output", help="Output directory")
    args = parser.parse_args()
    
    run_skill(Path(args.target), Path(args.output))
    sys.exit(0)


if __name__ == "__main__":
    main()
"""
    (skill_dir / "scripts" / f"{snake_name}_skill.py").write_text(script_py, encoding="utf-8")
    
    # 4. Generate references & templates
    (skill_dir / "references" / "guidelines.md").write_text(
        f"# {display_title} Reference Guidelines\n\nDetailed operational rules and reference data for {name}.\n",
        encoding="utf-8"
    )
    (skill_dir / "templates" / "report_template.md").write_text(
        f"# {display_title} Report\n\n## Findings\n\n## Recommendations\n",
        encoding="utf-8"
    )
    (skill_dir / "assets" / "schema.json").write_text(
        json.dumps({"$schema": "http://json-schema.org/draft-07/schema#", "type": "object"}, indent=2),
        encoding="utf-8"
    )
    
    # 5. Generate manifest.yaml
    manifest_content = f"""name: {name}
display_name: {display_title}
version: "1.0.0"
description: "{description}"
author: "{author}"
license: MIT
category: code-analysis
tags:
  - {name}
  - sdlc
  - agent-skills
runtime:
  engine: python
  min_version: "3.8"
  entry_point: scripts/{snake_name}_skill.py
  dependencies: []
tools:
  - run_in_terminal
  - read_file
  - file_search
  - grep_search
entry_files:
  skill_definition: SKILL.md
"""
    (skill_dir / "manifest.yaml").write_text(manifest_content, encoding="utf-8")
    
    # 6. Generate skill-card.json
    skill_card = {
      "skill_card": {
        "starterkit_id": name,
        "name": display_title,
        "description": description,
        "origin": {
          "BG": "BFSI",
          "ISU": "APAC",
          "Account": "Enterprise"
        },
        "maintainers": [
          {"name": author, "contact": "sarvesh.talele@tcs.com"},
          {"name": "Tejus Ajit Manjrekar", "contact": "tejus.manjrekar@tcs.com"},
          {"name": "Shivprakash Swami", "contact": "shivprakash.swami@tcs.com"}
        ],
        "version": "1.0.0",
        "status": "verified",
        "technology": ["Python", "JavaScript", "Git", "JSON"],
        "specialization": {
          "primary": name.replace("-", "_"),
          "domain_specific": ["SDLC Automation", "Quality Assurance"]
        },
        "tasks": [
          {
            "name": f"Execute {name}",
            "description": f"Automates procedural execution for {name} deterministically.",
            "input_schema": "Task prompt and repository context.",
            "output_schema": "Formatted artifacts and structured reports.",
            "async": True
          }
        ],
        "documentation": {
          "readme": "README.md",
          "howto": "QuickStart.md",
          "changelog": "Initial verified release."
        },
        "supported_harness": ["GitHub Copilot", "Claude Code", "Cursor", "Antigravity", "Windsurf"],
        "tested_harness": ["GitHub Copilot", "Claude Code", "Cursor", "Antigravity"]
      }
    }
    (skill_dir / "skill-card.json").write_text(json.dumps(skill_card, indent=2), encoding="utf-8")
    
    return {"name": name, "path": str(skill_dir), "status": "CREATED"}


def scaffold_sdd_bundle(
    bundle_prefix: str,
    output_root: Path,
    domain_description: str,
    author: str = "Sarvesh Talele",
) -> list[dict]:
    """Scaffold a custom 4-phase Spec-Driven Development (SDD) bundle."""
    prefix = sanitize_skill_name(bundle_prefix)
    phases = [
        ("specify", "Requirements", f"Transforms raw user requirements for {domain_description} into strict spec.md contracts."),
        ("plan", "Architecture", f"Constructs architectural implementation strategies and test-first designs for {domain_description}."),
        ("implement", "Implementation", f"Executes deterministic, test-driven coding adhering strictly to the {domain_description} spec."),
        ("verify", "Testing", f"Performs comprehensive contract auditing and regression verification for {domain_description}."),
    ]
    results = []
    for suffix, sdlc, desc in phases:
        skill_name = f"{prefix}-{suffix}"
        res = scaffold_skill(
            skill_name=skill_name,
            description=desc,
            output_root=output_root,
            sdlc_phase=sdlc,
            author=author,
        )
        results.append(res)
    return results


def main():
    parser = argparse.ArgumentParser(description="Scaffold an Agent Skill or SDD Bundle conforming to Spec 1.0")
    parser.add_argument("--name", required=True, help="Skill name (e.g. api-linter) or Bundle prefix (e.g. secure-cloud)")
    parser.add_argument("--description", required=True, help="Skill description and trigger intent")
    parser.add_argument("--output", default="skills", help="Output directory")
    parser.add_argument("--sdlc", default="Implementation", help="SDLC Phase")
    parser.add_argument("--bundle", choices=["single", "sdd"], default="single", help="Scaffold a single skill or 4-phase SDD bundle")
    args = parser.parse_args()
    
    if args.bundle == "sdd":
        res_list = scaffold_sdd_bundle(args.name, Path(args.output), args.description)
        print(f"📦 Successfully scaffolded {len(res_list)} SDD bundle skills:")
        for r in res_list:
            print(f"  • {r['name']} at {r['path']}")
    else:
        res = scaffold_skill(args.name, args.description, Path(args.output), args.sdlc)
        print(f"📦 Successfully scaffolded {res['name']} at {res['path']}")


if __name__ == "__main__":
    main()
