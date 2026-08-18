from __future__ import annotations

import json
import argparse
import sys
from pathlib import Path

def severity_to_sarif_level(severity: str) -> str:
    """Maps custom severities to standard SARIF levels."""
    severity = str(severity).upper()
    if severity in ("CRITICAL", "HIGH"):
        return "error"
    elif severity == "MEDIUM":
        return "warning"
    else:
        return "note"

def build_sarif(findings: list, skill_info: dict) -> dict:
    """Builds a SARIF 2.1.0 compatible dictionary from the list of findings."""
    rules_dict = {}
    
    for f in findings:
        rule_id = f.get("id", "UNKNOWN")
        if rule_id not in rules_dict:
            level = severity_to_sarif_level(f.get("severity", "LOW"))
            rules_dict[rule_id] = {
                "id": rule_id,
                "shortDescription": {"text": f.get("category", "Unknown finding")},
                "fullDescription": {"text": f.get("description", "No description provided")},
                "defaultConfiguration": {"level": level}
            }
            
    rules = list(rules_dict.values())
    
    results = []
    for f in findings:
        rule_id = f.get("id", "UNKNOWN")
        level = severity_to_sarif_level(f.get("severity", "LOW"))
        
        result = {
            "ruleId": rule_id,
            "level": level,
            "message": {"text": f.get("description", "Finding detected")},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": f.get("file", "unknown")
                        },
                        "region": {
                            "startLine": f.get("line", 1)
                        }
                    }
                }
            ]
        }
        results.append(result)
        
    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "SkillSpector-Lite",
                        "rules": rules
                    }
                },
                "results": results
            }
        ]
    }
    
    return sarif

def write_sarif(sarif: dict, output: Path) -> None:
    """Writes the SARIF dictionary to a JSON file."""
    output.write_text(json.dumps(sarif, indent=2), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Generate SARIF report from findings")
    parser.add_argument("findings_file", help="Input findings JSON file")
    parser.add_argument("output_file", help="Output SARIF JSON file")
    args = parser.parse_args()
    
    input_path = Path(args.findings_file)
    output_path = Path(args.output_file)
    
    if not input_path.exists():
        print(f"Error: {args.findings_file} not found")
        sys.exit(1)
        
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    findings = []
    if isinstance(data, list):
        findings = data
    elif isinstance(data, dict):
        if "active" in data:
            findings = data["active"]
        elif "findings" in data:
            findings = data["findings"]
            
    skill_info = {"name": "Evaluated Skill"}
    
    sarif = build_sarif(findings, skill_info)
    write_sarif(sarif, output_path)
    print(f"SARIF report written to {args.output_file}")

if __name__ == "__main__":
    main()
