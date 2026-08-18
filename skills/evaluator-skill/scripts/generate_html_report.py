#!/usr/bin/env python3
"""
generate_html_report.py — Render a combined quality + security JSON into a
standalone HTML dashboard.

Usage:
    python3 generate_html_report.py <combined.json> <output.html>

Expected input schema (single mode):
{
  "mode": "single",
  "skill_name": "...",
  "job_summary": "...",
  "structural_score": 69, "content_score": 72, "overall_score": 70,
  "risk_score": 15, "risk_severity": "LOW", "recommendation": "SAFE",
  "issues": [{"severity","category","message","fix","source"}],
  "security_findings": [{"id","category","severity","file","line","snippet","description"}]
}

Batch mode:
{
  "mode": "batch",
  "skills": [ <one of the above dicts per skill, each also has "skill_name"> ],
  "cross_skill_issues": [{"message", "skills": [...]}]
}
"""
import argparse
import html
import json
import sys

SEVERITY_COLOR = {
    "critical": "#dc2626", "major": "#ea580c", "minor": "#ca8a04",
    "CRITICAL": "#dc2626", "HIGH": "#ea580c", "MEDIUM": "#ca8a04", "LOW": "#16a34a",
}

CSS = """
:root { --bg:#0f1117; --panel:#181b24; --border:#262b3a; --text:#e5e7eb; --muted:#9ca3af; --accent:#5eead4; }
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 32px; }
h1 { font-size: 22px; margin-bottom: 4px; }
h2 { font-size: 16px; color: var(--accent); margin-top: 32px; border-bottom: 1px solid var(--border); padding-bottom: 6px; }
.sub { color: var(--muted); margin-bottom: 24px; font-size: 13px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px,1fr)); gap: 12px; margin: 16px 0; }
.card { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 16px; }
.score { font-size: 30px; font-weight: 700; }
.label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 4px; }
.bar-track { background: #262b3a; border-radius: 6px; height: 8px; overflow: hidden; margin-top: 10px; }
.bar-fill { height: 100%; border-radius: 6px; }
.pill { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }
table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--border); vertical-align: top; }
th { color: var(--muted); font-weight: 600; font-size: 11px; text-transform: uppercase; }
.issue { background: var(--panel); border: 1px solid var(--border); border-left: 4px solid; border-radius: 6px; padding: 10px 14px; margin-bottom: 8px; }
.issue .msg { font-weight: 600; margin-bottom: 3px; }
.issue .fix { color: var(--muted); font-size: 13px; }
.mono { font-family: ui-monospace, SFMono-Regular, monospace; font-size: 12px; color: var(--muted); }
.skill-section { border: 1px solid var(--border); border-radius: 10px; padding: 20px; margin-bottom: 20px; background: #12141c; }
.skill-header { display: flex; justify-content: space-between; align-items: center; }
.rank-table td, .rank-table th { padding: 6px 10px; }
"""


def score_color(score):
    if score >= 80:
        return "#16a34a"
    if score >= 50:
        return "#ca8a04"
    return "#dc2626"


def bar(score, color=None):
    color = color or score_color(score)
    return (f'<div class="bar-track"><div class="bar-fill" style="width:{max(score,0)}%;'
            f'background:{color}"></div></div>')


def pill(text, color):
    return f'<span class="pill" style="background:{color}22;color:{color};border:1px solid {color}55">{html.escape(str(text))}</span>'


def render_issue_list(issues, key_severity="severity"):
    if not issues:
        return '<p class="sub">None found.</p>'
    out = []
    for it in issues:
        sev = it.get(key_severity, "minor")
        color = SEVERITY_COLOR.get(sev, "#6b7280")
        msg = html.escape(it.get("message") or it.get("description", ""))
        fix = it.get("fix")
        conf = it.get("confidence")
        assessment = it.get("your_assessment")
        loc = ""
        if "file" in it:
            loc = f'<div class="mono">{html.escape(it["file"])}:{it.get("line", "")}  {html.escape(it.get("snippet",""))}</div>'
        meta = []
        if conf is not None:
            meta.append(f"scanner confidence: {conf}%")
        if assessment:
            meta.append(f"reviewed as: {html.escape(assessment)}")
        meta_line = f'<div class="fix">{" · ".join(meta)}</div>' if meta else ""
        out.append(
            f'<div class="issue" style="border-left-color:{color}">'
            f'<div class="msg">{pill(sev, color)} {msg}</div>'
            + (f'<div class="fix">Fix: {html.escape(fix)}</div>' if fix else "")
            + meta_line + loc + '</div>'
        )
    return "\n".join(out)


def render_skill(data):
    name = html.escape(data.get("skill_name", "skill"))
    job = html.escape(data.get("job_summary", ""))
    structural = data.get("structural_score")
    content = data.get("content_score")
    overall = data.get("overall_score", structural)
    risk = data.get("risk_score", 0)
    risk_sev = data.get("risk_severity", "LOW")
    rec = data.get("recommendation", "SAFE")
    issues = data.get("issues", [])
    sec_findings = data.get("security_findings", [])

    quality_cards = ""
    if structural is not None:
        quality_cards += (f'<div class="card"><div class="label">Structural</div>'
                           f'<div class="score" style="color:{score_color(structural)}">{structural}</div>'
                           f'{bar(structural)}</div>')
    if content is not None:
        quality_cards += (f'<div class="card"><div class="label">Content completeness</div>'
                           f'<div class="score" style="color:{score_color(content)}">{content}</div>'
                           f'{bar(content)}</div>')
    quality_cards += (f'<div class="card"><div class="label">Overall quality</div>'
                       f'<div class="score" style="color:{score_color(overall)}">{overall}</div>'
                       f'{bar(overall)}</div>')

    risk_color = SEVERITY_COLOR.get(risk_sev, "#6b7280")
    quality_cards += (f'<div class="card"><div class="label">Security risk</div>'
                       f'<div class="score" style="color:{risk_color}">{risk}</div>'
                       f'{bar(risk, risk_color)}<div style="margin-top:8px">{pill(rec, risk_color)}</div></div>')

    return f"""
    <div class="skill-section">
      <div class="skill-header"><h1 style="margin:0">{name}</h1></div>
      {f'<p class="sub">{job}</p>' if job else ''}
      <div class="grid">{quality_cards}</div>
      <h2>Quality gaps ({len(issues)})</h2>
      {render_issue_list(issues)}
      <h2>Security findings ({len(sec_findings)})</h2>
      {render_issue_list(sec_findings)}
    </div>
    """


def render_ranked_table(skills):
    rows = ""
    for s in sorted(skills, key=lambda x: -(x.get("overall_score", x.get("structural_score", 0)) or 0)):
        overall = s.get("overall_score", s.get("structural_score", "-"))
        rows += (f'<tr><td>{html.escape(s.get("skill_name",""))}</td>'
                 f'<td>{overall}</td>'
                 f'<td>{s.get("structural_score","-")}</td>'
                 f'<td>{s.get("content_score","-")}</td>'
                 f'<td>{pill(s.get("risk_severity","LOW"), SEVERITY_COLOR.get(s.get("risk_severity","LOW"),"#6b7280"))}</td>'
                 f'<td>{s.get("risk_score",0)}</td></tr>')
    return f"""
    <table class="rank-table">
      <tr><th>Skill</th><th>Overall</th><th>Structural</th><th>Content</th><th>Risk</th><th>Risk score</th></tr>
      {rows}
    </table>
    """


def build_html(data):
    if data.get("mode") == "batch":
        skills = data.get("skills", [])
        cross = data.get("cross_skill_issues", [])
        body = f"""
        <h1>Skill Library Audit</h1>
        <p class="sub">{len(skills)} skill(s) scanned in {html.escape(data.get('library_path',''))}</p>
        <h2>Ranked overview</h2>
        {render_ranked_table(skills)}
        <h2>Cross-skill / library-level findings ({len(cross)})</h2>
        {render_issue_list([{"severity":"major","message":c["message"]} for c in cross])}
        {''.join(render_skill(s) for s in skills)}
        """
    else:
        body = render_skill(data)

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Skill Evaluation Report</title>
<style>{CSS}</style></head><body>{body}</body></html>"""


def main():
    ap = argparse.ArgumentParser(description="Render a skill evaluation JSON into an HTML dashboard")
    ap.add_argument("input_json")
    ap.add_argument("output_html")
    args = ap.parse_args()

    with open(args.input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    html_out = build_html(data)
    with open(args.output_html, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"Wrote {args.output_html}")


if __name__ == "__main__":
    main()
