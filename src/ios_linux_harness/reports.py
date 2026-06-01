from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ios_linux_harness.prior_art import REQUIRED_PROJECTS, PriorArtAudit


@dataclass(frozen=True)
class ReportPaths:
    markdown: Path
    json: Path


def render_markdown_report(audit: PriorArtAudit) -> str:
    lines = [
        "# iOS-on-Linux Verification Harness Report",
        "",
        "## Bottom Line",
        "",
        "Not first to cross-compile iOS from Linux. Not first to split Linux builds from Mac runtime execution.",
        "",
        "This harness is publishable only if the narrower verification deltas below survive source-visible prior-art review.",
        "",
        f"- publish_gate: `{audit.publish_gate}`",
        f"- publish_gate_reason: {audit.publish_gate_reason}",
        "",
        "## Candidate Deltas",
        "",
    ]
    if audit.candidate_deltas:
        for key in audit.candidate_deltas:
            surface = next(surface for surface in audit.surfaces if surface.key == key)
            lines.append(f"- `{surface.key}`: {surface.title}")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Surface Matrix",
            "",
            "| Surface | Verdict | Prior Art Found | Claim Discipline |",
            "| --- | --- | --- | --- |",
        ]
    )
    for surface in audit.surfaces:
        lines.append(
            f"| {surface.title} | `{surface.verdict}` | `{surface.prior_art_found}` | {surface.claim} |"
        )
    lines.extend(
        [
            "",
            "## Required Prior-Art Sources",
            "",
            "| Source | Audited |",
            "| --- | --- |",
        ]
    )
    for project, audited in audit.audited_projects.items():
        lines.append(f"| [`{project}`]({REQUIRED_PROJECTS[project]}) | `{audited}` |")
    lines.append("")
    return "\n".join(lines)


def write_report_bundle(audit: PriorArtAudit, out_dir: Path) -> ReportPaths:
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown = out_dir / "novelty-matrix.md"
    json_path = out_dir / "novelty-matrix.json"
    markdown.write_text(render_markdown_report(audit), encoding="utf-8")
    json_path.write_text(audit.to_json(), encoding="utf-8")
    return ReportPaths(markdown=markdown, json=json_path)
