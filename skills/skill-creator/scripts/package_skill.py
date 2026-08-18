"""Bundles skill directory into .skill ZIP."""

from __future__ import annotations
import argparse
import os
import zipfile
import sys
from pathlib import Path

def validate_before_package(skill_dir: Path) -> list[str]:
    """Pre-flight checks: SKILL.md exists, frontmatter valid, no Critical security."""
    errors = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md is missing")
    
    # Mock checks for now
    return errors

def package_skill(skill_dir: Path, output_dir: Path) -> Path:
    """Validates, then creates .skill ZIP excluding evals/, __pycache__/, .git/, .workspaces/"""
    errors = validate_before_package(skill_dir)
    if errors:
        raise ValueError(f"Validation failed: {errors}")
        
    output_dir.mkdir(parents=True, exist_ok=True)
    skill_name = skill_dir.name
    output_zip = output_dir / f"{skill_name}.skill"
    
    excludes = {'evals', '__pycache__', '.git', '.workspaces'}
    
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            dirs[:] = [d for d in dirs if d not in excludes]
            for file in files:
                if file.endswith('.pyc') or file == '.DS_Store':
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)
                
    return output_zip

def main():
    parser = argparse.ArgumentParser(description='Package a skill directory')
    parser.add_argument('--skill', required=True, help='Path to skill directory')
    parser.add_argument('--output', required=True, help='Output directory')
    args = parser.parse_args()
    
    try:
        out_path = package_skill(Path(args.skill), Path(args.output))
        print(f"Successfully packaged: {out_path}")
    except Exception as e:
        print(f"Error packaging skill: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
