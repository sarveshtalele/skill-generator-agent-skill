from __future__ import annotations

import sys
import re
import fnmatch
import argparse
import json
from pathlib import Path

def load_baseline(baseline_path: Path) -> dict:
    """Loads a suppressions baseline from a YAML file without using PyYAML."""
    baseline = {"suppressions": []}
    if not baseline_path.exists():
        return baseline
        
    content = baseline_path.read_text(encoding="utf-8")
    
    blocks = content.split("- id:")
    if len(blocks) > 1:
        for block in blocks[1:]:
            lines = block.strip().split('\n')
            if not lines: continue
            
            finding_id = lines[0].strip().strip("'\"")
            file_glob = ""
            reason = ""
            
            for line in lines[1:]:
                line = line.strip()
                if line.startswith("file_glob:"):
                    file_glob = line[10:].strip().strip("'\"")
                elif line.startswith("reason:"):
                    reason = line[7:].strip().strip("'\"")
                    
            if finding_id and file_glob:
                baseline["suppressions"].append({
                    "id": finding_id,
                    "file_glob": file_glob,
                    "reason": reason
                })
                
    return baseline

def suppress_findings(findings: list, baseline: dict) -> tuple[list, list]:
    """Separates findings into active and suppressed based on the baseline."""
    active = []
    suppressed = []
    
    suppressions = baseline.get("suppressions", [])
    
    for f in findings:
        is_suppressed = False
        for s in suppressions:
            sid = s.get("id", "*")
            id_match = (sid == "*" or sid == f.get("id") or fnmatch.fnmatch(f.get("id", ""), sid))
            if id_match and fnmatch.fnmatch(f.get("file", ""), s.get("file_glob", "*")):
                is_suppressed = True
                break
        
        if is_suppressed:
            suppressed.append(f)
        else:
            active.append(f)
            
    return active, suppressed

def save_baseline(findings: list, output_path: Path) -> None:
    """Writes a new baseline YAML file with the provided findings."""
    lines = ["suppressions:"]
    for f in findings:
        lines.append(f"  - id: '{f.get('id', '')}'")
        lines.append(f"    file_glob: '{f.get('file', '*')}'")
        lines.append(f"    reason: 'Auto-generated suppression'")
    output_path.write_text("\n".join(lines), encoding="utf-8")

def deduplicate_findings(findings: list) -> list:
    """Removes duplicate findings that have the exact same id, file, and line."""
    seen = set()
    deduped = []
    for f in findings:
        key = (f.get("id"), f.get("file"), f.get("line"))
        if key not in seen:
            seen.add(key)
            deduped.append(f)
    return deduped

def main():
    parser = argparse.ArgumentParser(description="Adjudicator")
    parser.add_argument("findings", help="Findings JSON file")
    parser.add_argument("--baseline", help="Baseline YAML file", default=".baseline.yml")
    parser.add_argument("--save-baseline", help="Output baseline YAML file")
    args = parser.parse_args()
    
    try:
        with open(args.findings, "r", encoding="utf-8") as f:
            findings = json.load(f)
    except Exception as e:
        print(f"Error loading findings: {e}")
        sys.exit(1)
        
    findings = deduplicate_findings(findings)
    baseline = load_baseline(Path(args.baseline))
    active, suppressed = suppress_findings(findings, baseline)
    
    if args.save_baseline:
        save_baseline(active, Path(args.save_baseline))
        
    print(json.dumps({"active": active, "suppressed": suppressed}, indent=2))

if __name__ == "__main__":
    main()
