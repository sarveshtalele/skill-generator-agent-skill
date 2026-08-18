"""Fast regex validation for SKILL.md frontmatter during creation."""

from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

def validate_frontmatter(content: str) -> list[str]:
    errors = []
    
    # check name
    name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    if not name_match:
        errors.append("Missing 'name' field")
    else:
        name = name_match.group(1).strip()
        if len(name) > 64:
            errors.append("Name must be <= 64 chars")
        if not re.match(r'^[a-z0-9\-]+$', name):
            errors.append("Name must be kebab-case")
            
    # check description
    desc_match = re.search(r'^description:\s*(.+)$', content, re.MULTILINE)
    if not desc_match:
        errors.append("Missing 'description' field")
    else:
        desc = desc_match.group(1).strip()
        if len(desc) == 0:
            errors.append("Description cannot be empty")
        if len(desc) > 1024:
            errors.append("Description must be <= 1024 chars")
            
    return errors

def main():
    parser = argparse.ArgumentParser(description='Quick validate SKILL.md frontmatter')
    parser.add_argument('--file', help='Path to SKILL.md')
    parser.add_argument('--skill', help='Path to skill directory')
    parser.add_argument('path', nargs='?', help='Path to SKILL.md or skill directory')
    args = parser.parse_args()
    
    target = args.file or args.skill or args.path
    if not target:
        print("Error: Specify --file or --skill or target path", file=sys.stderr)
        sys.exit(1)
        
    file_path = Path(target)
    if file_path.is_dir():
        file_path = file_path / "SKILL.md"
        
    if not file_path.exists():
        print(f"Error: {file_path} does not exist", file=sys.stderr)
        sys.exit(1)
        
    errors = validate_frontmatter(file_path.read_text())
    if errors:
        print("Validation errors:")
        for e in errors:
            print(f"- {e}")
        sys.exit(1)
    else:
        print("Validation passed.")

if __name__ == "__main__":
    main()
