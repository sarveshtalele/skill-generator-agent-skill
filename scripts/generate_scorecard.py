#!/usr/bin/env python3
"""Generates SCORECARD.md and SKILL_REGISTRY.md from scorecards/*.json files."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_scorecards(scorecards_dir: Path) -> list[dict]:
    """Load all JSON scorecards from the scorecards directory."""
    results = []
    for json_file in sorted(scorecards_dir.glob("*.json")):
        if json_file.name in ("trace.json", "timing.json", "benchmark.json"):
            continue
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "skill_name" in data:
                data["_file"] = json_file.name
                results.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return results


def generate_scorecard_md(scorecards: list[dict], output: Path) -> None:
    """Generate SCORECARD.md — centralized quality matrix."""
    lines = [
        "# 📊 Skill Quality Scorecard",
        "",
        f"> Auto-generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "| Skill | Score | Gate | Security | Functional | Lift | Trigger F1 |",
        "|:--|:--|:--|:--|:--|:--|:--|",
    ]

    for sc in scorecards:
        name = sc.get("skill_name", "unknown")
        score = sc.get("overall_score", "N/A")
        raw_gate = sc.get("gate_decision", sc.get("status", "UNKNOWN"))
        if isinstance(raw_gate, dict):
            gate = raw_gate.get("status", "UNKNOWN")
        else:
            gate = str(raw_gate)

        # Extract dimension scores if available
        dims = sc.get("dimensions", {})
        security = dims.get("security", "—")
        functional = dims.get("functional_correctness", dims.get("functional", "—"))
        lift = dims.get("skill_lift", "—")
        trigger = dims.get("trigger_quality", dims.get("trigger", "—"))

        gate_icon = {"PASS": "✅", "WARN": "⚠️", "BLOCK": "❌"}.get(gate, "❓")
        lines.append(
            f"| `{name}` | {score}/100 | {gate_icon} {gate} "
            f"| {security} | {functional} | {lift} | {trigger} |"
        )

    lines.extend(["", "---", "", "*Run `make evaluate-all` to regenerate this scorecard.*", ""])
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Generated {output}")


def generate_registry_md(scorecards: list[dict], output: Path, skills_dir: Path | None = None) -> None:
    """Generate SKILL_REGISTRY.md — indexed skill catalog."""
    lines = [
        "# 📦 Skill Registry",
        "",
        f"> Auto-generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "| Skill | SDLC Phase | Quality Score | Description |",
        "|:---|:---:|:---:|:---|",
    ]

    for sc in scorecards:
        name = sc.get("skill_name", "unknown")
        score = sc.get("overall_score", "N/A")
        sdlc = "Implementation"
        desc = "Meta-skill for agent skill lifecycle and execution."

        # Attempt to read frontmatter from skills/<name>/SKILL.md
        if skills_dir and (skills_dir / name / "SKILL.md").exists():
            skill_md = (skills_dir / name / "SKILL.md").read_text(encoding="utf-8", errors="ignore")
            import re
            m_desc_multi = re.search(r"^description:\s*>\s*\n((?:\s{2,}.+\n?)+)", skill_md, re.MULTILINE)
            if m_desc_multi:
                desc = " ".join(line.strip() for line in m_desc_multi.group(1).splitlines() if line.strip())
            else:
                m_desc = re.search(r"^description:\s*(.+)$", skill_md, re.MULTILINE)
                if m_desc and m_desc.group(1).strip() != ">":
                    desc = m_desc.group(1).strip()
            
            m_sdlc = re.search(r"(?:sdlc-phase|sdlc):\s*(.+)$", skill_md, re.MULTILINE)
            if m_sdlc:
                sdlc = m_sdlc.group(1).strip()

        # Clean description to single line for markdown table
        desc_clean = desc.replace("\n", " ").replace("|", "\\|")
        if len(desc_clean) > 180:
            desc_clean = desc_clean[:177] + "..."

        lines.append(f"| [`{name}`](skills/{name}/README.md) | {sdlc} | **{score}/100** | {desc_clean} |")

    lines.extend(["", "---", "", "*Run `make scorecard` to regenerate this registry.*", ""])
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Generated {output}")


def main():
    repo_root = Path(__file__).parent.parent
    scorecards_dir = repo_root / "scorecards"

    if not scorecards_dir.exists():
        print("⚠️ No scorecards/ directory found.", file=sys.stderr)
        sys.exit(1)

    scorecards = load_scorecards(scorecards_dir)
    if not scorecards:
        print("⚠️ No scorecard JSON files found.", file=sys.stderr)
        sys.exit(1)

    generate_scorecard_md(scorecards, repo_root / "SCORECARD.md")
    generate_registry_md(scorecards, repo_root / "SKILL_REGISTRY.md", skills_dir=repo_root / "skills")
    print(f"📊 Processed {len(scorecards)} skill(s)")


if __name__ == "__main__":
    main()
