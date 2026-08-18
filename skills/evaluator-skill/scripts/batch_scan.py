#!/usr/bin/env python3
"""
batch_scan.py — Run structural_check.py and security_scan.py over every skill
found in a directory (a skill library / marketplace folder), plus cross-skill
checks: description-overlap (possible trigger competition or duplication).

A "skill" is any folder containing a SKILL.md at its own root (not nested
inside a scripts/references/assets subfolder).

Usage:
    python3 batch_scan.py <library_path> [--json] [--out results.json]
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import structural_check
import security_scan

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "scripts", "references", "assets"}
STOPWORDS = {"the", "a", "an", "and", "or", "to", "of", "for", "in", "on", "with", "this", "that",
             "use", "skill", "file", "files", "when", "user", "is", "are", "be", "it", "as", "any",
             "including"}


def find_skills(library_path):
    skills = []
    for entry in sorted(os.listdir(library_path)):
        full = os.path.join(library_path, entry)
        if not os.path.isdir(full) or entry in SKIP_DIRS or entry.startswith("."):
            continue
        if os.path.isfile(os.path.join(full, "SKILL.md")):
            skills.append(full)
        else:
            # one level deeper (e.g. a category folder containing several skills)
            for sub in sorted(os.listdir(full)):
                subfull = os.path.join(full, sub)
                if os.path.isdir(subfull) and os.path.isfile(os.path.join(subfull, "SKILL.md")):
                    skills.append(subfull)
    return skills


def description_words(desc):
    words = re.findall(r"[a-zA-Z]{3,}", desc.lower())
    return {w for w in words if w not in STOPWORDS}


def find_overlaps(skill_descriptions):
    """skill_descriptions: {name: description}. Returns list of overlap findings."""
    overlaps = []
    names = list(skill_descriptions.keys())
    word_sets = {n: description_words(d) for n, d in skill_descriptions.items()}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            wa, wb = word_sets[a], word_sets[b]
            if not wa or not wb:
                continue
            overlap = wa & wb
            jaccard = len(overlap) / len(wa | wb)
            if jaccard >= 0.35 and len(overlap) >= 4:
                overlaps.append({
                    "skills": [a, b],
                    "jaccard": round(jaccard, 2),
                    "shared_terms": sorted(overlap)[:12],
                    "message": f"'{a}' and '{b}' descriptions overlap heavily ({round(jaccard*100)}% shared "
                               f"vocabulary) -- possible trigger competition or duplicated scope.",
                })
    return overlaps


def run_batch(library_path):
    skill_paths = find_skills(library_path)
    results = []
    descriptions = {}

    for sp in skill_paths:
        struct = structural_check.check_skill(sp)
        sec = security_scan.scan_skill(sp)
        skillmd = os.path.join(sp, "SKILL.md")
        desc = ""
        if os.path.isfile(skillmd):
            with open(skillmd, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            fm, _ = structural_check.load_frontmatter(text)
            if fm:
                desc = fm.get("description", "")
        name = struct["skill_name"]
        descriptions[name] = desc
        results.append({
            "skill_name": name,
            "path": os.path.relpath(sp, library_path),
            "structural_score": struct["structural_score"],
            "structural_issues": struct["issues"],
            "risk_score": sec["risk_score"],
            "risk_severity": sec["risk_severity"],
            "recommendation": sec["recommendation"],
            "security_findings": sec["findings"],
            "components": sec["components"],
        })

    overlaps = find_overlaps(descriptions)

    return {
        "mode": "batch",
        "library_path": library_path,
        "skill_count": len(results),
        "skills": results,
        "cross_skill_issues": overlaps,
    }


def main():
    ap = argparse.ArgumentParser(description="Batch structural + security scan of a skill library")
    ap.add_argument("library_path")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", help="write JSON results to this path")
    args = ap.parse_args()

    if not os.path.isdir(args.library_path):
        print(f"error: {args.library_path} is not a directory", file=sys.stderr)
        sys.exit(1)

    result = run_batch(args.library_path)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Scanned {result['skill_count']} skill(s) in {args.library_path}")
        for s in result["skills"]:
            print(f"  {s['skill_name']}: structural={s['structural_score']}/100  "
                  f"risk={s['risk_score']}/100 ({s['risk_severity']})")
        if result["cross_skill_issues"]:
            print(f"\nCross-skill issues ({len(result['cross_skill_issues'])}):")
            for o in result["cross_skill_issues"]:
                print(f"  {o['message']}")


if __name__ == "__main__":
    main()
