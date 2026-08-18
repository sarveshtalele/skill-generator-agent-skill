#!/usr/bin/env python3
"""
structural_check.py — Objective authoring best-practice checker for a single skill.

Checks the mechanically-verifiable half of skill quality: valid frontmatter,
description quality, SKILL.md length discipline, progressive disclosure,
anatomy (are bundled scripts/references actually referenced and present),
and presence of examples. This is deliberately narrow and deterministic --
the content-completeness judgment half lives in Claude's own read of
references/rubric.md, not in this script.

Usage:
    python3 structural_check.py <skill_path> [--json]

Output (--json):
{
  "skill_name": str,
  "structural_score": int (0-100),
  "issues": [{"severity","category","message","fix","source":"structural"}],
  "stats": {...}
}
"""
import argparse
import json
import os
import re
import sys

DEDUCTIONS = {
    "critical": 30,
    "major": 15,
    "minor": 5,
}


def load_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not m:
        return None, text
    fm_text = m.group(1)
    body = text[m.end():]
    fm = {}
    # simple key: value parser (frontmatter here is flat -- name/description/compatibility)
    cur_key = None
    for line in fm_text.splitlines():
        km = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
        if km:
            cur_key = km.group(1)
            fm[cur_key] = km.group(2).strip()
        elif cur_key and line.startswith((" ", "\t")):
            fm[cur_key] += " " + line.strip()
    return fm, body


def check_skill(skill_path):
    issues = []
    skillmd_path = os.path.join(skill_path, "SKILL.md")
    stats = {"skillmd_lines": 0, "referenced_files": [], "missing_referenced_files": [],
              "bundled_files_not_referenced": []}

    if not os.path.isfile(skillmd_path):
        return {
            "skill_name": os.path.basename(skill_path.rstrip("/")),
            "structural_score": 0,
            "issues": [{"severity": "critical", "category": "anatomy",
                        "message": "No SKILL.md found at the root of this folder.",
                        "fix": "Add a SKILL.md with YAML frontmatter (name, description) at the folder root.",
                        "source": "structural"}],
            "stats": stats,
        }

    with open(skillmd_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    stats["skillmd_lines"] = text.count("\n") + 1

    fm, body = load_frontmatter(text)

    # --- Frontmatter validity ---
    if fm is None:
        issues.append({"severity": "critical", "category": "frontmatter",
                        "message": "SKILL.md has no valid YAML frontmatter block (--- ... ---).",
                        "fix": "Add frontmatter with at minimum `name:` and `description:` fields.",
                        "source": "structural"})
        fm = {}

    name = fm.get("name", "")
    description = fm.get("description", "")
    folder_name = os.path.basename(skill_path.rstrip("/"))

    if not name:
        issues.append({"severity": "critical", "category": "frontmatter",
                        "message": "Missing `name` field in frontmatter.",
                        "fix": "Add `name: <skill-name>` matching the folder name.",
                        "source": "structural"})
    elif name != folder_name:
        issues.append({"severity": "minor", "category": "frontmatter",
                        "message": f"Frontmatter name '{name}' does not match folder name '{folder_name}'.",
                        "fix": "Rename one to match the other for consistency and easier packaging.",
                        "source": "structural"})

    if not description:
        issues.append({"severity": "critical", "category": "frontmatter",
                        "message": "Missing `description` field in frontmatter.",
                        "fix": "Add a `description` stating what the skill does and when to trigger it.",
                        "source": "structural"})
    else:
        if len(description) < 40:
            issues.append({"severity": "major", "category": "description",
                            "message": f"Description is very short ({len(description)} chars) -- "
                                       "unlikely to disambiguate triggering from other skills.",
                            "fix": "Expand to state both what the skill does and specific phrases/contexts that should trigger it.",
                            "source": "structural"})
        trigger_markers = re.search(r"\b(use (this|when)|whenever|trigger|use it (when|for))\b", description, re.IGNORECASE)
        if not trigger_markers:
            issues.append({"severity": "major", "category": "description",
                            "message": "Description states what the skill does but has no clear 'when to use' triggering language.",
                            "fix": "Add explicit trigger phrasing, e.g. 'Use this whenever the user ...'.",
                            "source": "structural"})
        if len(description) > 1200:
            issues.append({"severity": "minor", "category": "description",
                            "message": f"Description is quite long ({len(description)} chars) -- "
                                       "the metadata layer is meant to stay compact since it's always in context.",
                            "fix": "Trim to the essential what/when; move elaboration into the SKILL.md body.",
                            "source": "structural"})

    # --- SKILL.md length discipline ---
    if stats["skillmd_lines"] > 500:
        issues.append({"severity": "major", "category": "progressive_disclosure",
                        "message": f"SKILL.md body is {stats['skillmd_lines']} lines, over the ~500-line guideline.",
                        "fix": "Move detail into references/*.md files and link to them from the body, "
                               "keeping SKILL.md as an index + workflow.",
                        "source": "structural"})

    # --- Examples present ---
    has_example_lang = re.search(r"\b(example|e\.g\.|for instance)\b", body, re.IGNORECASE)
    has_code_block = "```" in body
    if not has_example_lang and not has_code_block:
        issues.append({"severity": "minor", "category": "examples",
                        "message": "No worked examples or code blocks found in the SKILL.md body.",
                        "fix": "Add at least one concrete example showing the skill's expected input/output.",
                        "source": "structural"})

    # --- Anatomy: are referenced files present, are bundled files referenced ---
    # Strip fenced code blocks first -- illustrative JSON/shell examples inside ``` ``` often
    # contain example-looking paths (e.g. "scripts/x.py" in a sample JSON snippet) that aren't
    # real bundle references, so only look at inline text for the "does this file exist" check.
    body_no_fences = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    # Match either backticked paths `scripts/...` or markdown links [text](scripts/...)
    found_refs = set(re.findall(r"`((?:scripts|references|assets)/[\w./\-]+\.\w+)`", body_no_fences))
    found_links = set(re.findall(r"\]\(((?:scripts|references|assets)/[\w./\-]+\.\w+)\)", body_no_fences))
    referenced = found_refs | found_links
    stats["referenced_files"] = sorted(referenced)

    bundled = []
    for sub in ("scripts", "references", "assets"):
        subdir = os.path.join(skill_path, sub)
        if os.path.isdir(subdir):
            for root, dirs, files in os.walk(subdir):
                dirs[:] = [d for d in dirs if d != "__pycache__"]
                for fn in files:
                    if fn == "__pycache__" or fn.endswith((".pyc", ".pyo")):
                        continue
                    rel = os.path.relpath(os.path.join(root, fn), skill_path)
                    bundled.append(rel.replace(os.sep, "/"))

    for rel in referenced:
        candidate = rel.replace("`", "")
        if candidate.startswith(("scripts/", "references/", "assets/")):
            full = os.path.join(skill_path, candidate)
            if not os.path.isfile(full):
                stats["missing_referenced_files"].append(candidate)

    if stats["missing_referenced_files"]:
        issues.append({"severity": "critical", "category": "anatomy",
                        "message": f"SKILL.md references {len(stats['missing_referenced_files'])} file(s) that "
                                   f"don't exist in the bundle: {', '.join(stats['missing_referenced_files'][:5])}"
                                   + ("..." if len(stats["missing_referenced_files"]) > 5 else ""),
                        "fix": "Either add the missing files or remove the reference -- a broken pointer "
                               "means Claude will look for something that isn't there mid-task.",
                        "source": "structural"})

    unreferenced = [b for b in bundled if not any(b.endswith(r.lstrip("`")) or r.lstrip("`") in b for r in referenced)]
    # ignore obvious support files that don't need individual mention
    unreferenced = [b for b in unreferenced if not re.search(r"__init__\.py$|LICENSE|\.gitkeep$", b)]
    stats["bundled_files_not_referenced"] = unreferenced
    if unreferenced:
        issues.append({"severity": "minor", "category": "anatomy",
                        "message": f"{len(unreferenced)} bundled file(s) exist but aren't mentioned anywhere in "
                                   f"SKILL.md: {', '.join(unreferenced[:5])}" + ("..." if len(unreferenced) > 5 else ""),
                        "fix": "Either reference them from SKILL.md (so Claude knows when to open them) or remove "
                               "them if unused.",
                        "source": "structural"})

    # --- Writing style: heavy first person / vague hedging (light heuristic, minor only) ---
    vague_count = len(re.findall(r"\b(maybe|perhaps|might want to|could try)\b", body, re.IGNORECASE))
    if vague_count >= 5:
        issues.append({"severity": "minor", "category": "writing_style",
                        "message": f"Body has {vague_count} instances of hedging language (maybe/perhaps/might).",
                        "fix": "Prefer direct, imperative instructions -- skills are more reliably followed as procedure than as suggestion.",
                        "source": "structural"})

    # --- Score ---
    score = 100
    for issue in issues:
        score -= DEDUCTIONS.get(issue["severity"], 0)
    score = max(score, 0)

    return {
        "skill_name": name or folder_name,
        "structural_score": score,
        "issues": issues,
        "stats": stats,
    }


def main():
    ap = argparse.ArgumentParser(description="Structural best-practice check for a Claude skill folder")
    ap.add_argument("skill_path")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(args.skill_path):
        print(f"error: {args.skill_path} is not a directory", file=sys.stderr)
        sys.exit(1)

    result = check_skill(args.skill_path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Structural score: {result['structural_score']}/100")
        for issue in result["issues"]:
            print(f"  [{issue['severity'].upper()}] {issue['category']}: {issue['message']}")


if __name__ == "__main__":
    main()
