from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


REQUIRED_PROJECTS = {
    "rules_applecross": "https://github.com/apple-cross-toolchain/rules_applecross",
    "xctestrunner-bash": "https://github.com/apple-cross-toolchain/xctestrunner-bash",
    "xtool": "https://github.com/xtool-org/xtool",
    "linux-app": "https://github.com/kabiroberai/linux-app",
}


TEXT_SUFFIXES = {
    ".bzl",
    ".bazel",
    ".build",
    ".c",
    ".cc",
    ".h",
    ".md",
    ".py",
    ".sh",
    ".swift",
    ".txt",
    ".yaml",
    ".yml",
}


@dataclass(frozen=True)
class AuditSurface:
    key: str
    title: str
    verdict: str
    prior_art_found: bool
    evidence: str
    claim: str


@dataclass(frozen=True)
class PriorArtAudit:
    audited_projects: dict[str, bool]
    surfaces: list[AuditSurface]
    candidate_deltas: list[str]
    publish_gate: str
    publish_gate_reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "audited_projects": self.audited_projects,
            "surfaces": [asdict(surface) for surface in self.surfaces],
            "candidate_deltas": self.candidate_deltas,
            "publish_gate": self.publish_gate,
            "publish_gate_reason": self.publish_gate_reason,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"


def run_audit(prior_art_root: Path | None) -> PriorArtAudit:
    project_text = _load_project_text(prior_art_root)
    audited_projects = {
        project: bool(prior_art_root and (prior_art_root / project).exists())
        for project in REQUIRED_PROJECTS
    }

    xctestrun_found = _has_any(
        project_text,
        [
            r"ios_xctestrun_runner",
            r"test-without-building",
            r"IsUITestBundle",
            r"xctestrunner",
        ],
    )
    swift_testing_found = _has_any(project_text, [r"swift-testing", r"Testing\.framework", r"@rpath/Testing\.framework"])
    accessibility_payload_found = _has_any(project_text, [r"accessibility[_ -]?tree", r"XCUIElement.*debugDescription"])
    binary_framework_runtime_found = _has_any(
        project_text,
        [r"binary framework.*runtime", r"ProbeBinaryKit", r"embedded binary framework"],
    )
    runtime_ladder_found = _has_any(project_text, [r"Mach-O.*dyld.*libSystem", r"runtime-substrate ladder"])

    surfaces = [
        AuditSurface(
            key="linux_cross_compile",
            title="Linux-to-iOS Swift compile/link",
            verdict="not_novel",
            prior_art_found=True,
            evidence="Documented by apple-cross-toolchain, linux-app, Swift SDK Darwin work, and xtool.",
            claim="Do not claim first discovery of iOS cross-compilation from Linux.",
        ),
        AuditSurface(
            key="linux_app_bundle",
            title="Linux-built iOS app bundle",
            verdict="not_novel",
            prior_art_found=True,
            evidence="Prior art includes SwiftUI/iOS app bundle generation from Linux-hosted builds.",
            claim="Only claim this repo is a modern minimal reproduction.",
        ),
        AuditSurface(
            key="xctestrun_ui_test_handoff",
            title="Linux-built XCTest/UI-test handoff to macOS",
            verdict="not_novel" if xctestrun_found or prior_art_root is None else "needs_audit",
            prior_art_found=xctestrun_found or prior_art_root is None,
            evidence=_evidence(
                xctestrun_found,
                "Source scan found xctestrun/UI-test runner patterns in prior art.",
                "No local xctestrun/UI-test runner pattern found in scanned sources.",
            ),
            claim="Do not treat .xctestrun handoff alone as novel.",
        ),
        AuditSurface(
            key="swift_testing_ios_bundle",
            title="Swift Testing iOS bundle built on Linux and run under CoreSimulator",
            verdict="candidate_delta" if not swift_testing_found else "not_novel",
            prior_art_found=swift_testing_found,
            evidence=_evidence(
                swift_testing_found,
                "Source scan found Swift Testing markers in prior art.",
                "Source scan did not find Swift Testing iOS simulator bundle execution markers.",
            ),
            claim="Candidate if backed by a reproducible runner log.",
        ),
        AuditSurface(
            key="visual_accessibility_payload",
            title="Visual screenshot plus accessibility tree from Linux-built app",
            verdict="candidate_delta" if not accessibility_payload_found else "not_novel",
            prior_art_found=accessibility_payload_found,
            evidence=_evidence(
                accessibility_payload_found,
                "Source scan found accessibility-tree extraction markers in prior art.",
                "Source scan did not find a combined screenshot/accessibility payload from Linux-built app artifacts.",
            ),
            claim="Candidate if the report includes screenshot bytes and app-visible accessibility evidence.",
        ),
        AuditSurface(
            key="binary_framework_runtime_evidence",
            title="Linux-built binary framework visible in tests and UI/accessibility",
            verdict="candidate_delta" if not binary_framework_runtime_found else "not_novel",
            prior_art_found=binary_framework_runtime_found,
            evidence=_evidence(
                binary_framework_runtime_found,
                "Source scan found comparable binary-framework runtime evidence.",
                "Source scan did not find binary-framework runtime evidence tied to UI/accessibility.",
            ),
            claim="Candidate if the app renders and tests a Linux-built embedded framework.",
        ),
        AuditSurface(
            key="runtime_substrate_ladder",
            title="Runtime-substrate boundary ladder",
            verdict="candidate_delta" if not runtime_ladder_found else "not_novel",
            prior_art_found=runtime_ladder_found,
            evidence=_evidence(
                runtime_ladder_found,
                "Source scan found a comparable Mach-O/dyld/libSystem boundary ladder.",
                "Source scan did not find a comparable ordered runtime-substrate ladder.",
            ),
            claim="Candidate analysis, not proof that UIKit runs on Linux.",
        ),
    ]

    candidate_deltas = [surface.key for surface in surfaces if surface.verdict == "candidate_delta"]
    missing_projects = [project for project, audited in audited_projects.items() if not audited]
    if missing_projects:
        publish_gate = "fail"
        reason = "Missing source audit checkouts: " + ", ".join(missing_projects)
    elif len(candidate_deltas) < 2:
        publish_gate = "fail"
        reason = "Fewer than two candidate deltas survived the prior-art scan."
    else:
        publish_gate = "pass"
        reason = "Required sources were audited and at least two candidate deltas remain."

    return PriorArtAudit(
        audited_projects=audited_projects,
        surfaces=surfaces,
        candidate_deltas=candidate_deltas,
        publish_gate=publish_gate,
        publish_gate_reason=reason,
    )


def _load_project_text(prior_art_root: Path | None) -> str:
    if prior_art_root is None:
        return ""
    chunks: list[str] = []
    for project in REQUIRED_PROJECTS:
        project_root = prior_art_root / project
        if not project_root.exists():
            continue
        chunks.extend(_read_text_files(project_root))
    return "\n".join(chunks)


def _read_text_files(root: Path) -> Iterable[str]:
    for path in root.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"BUILD", "WORKSPACE", "MODULE.bazel"}:
            continue
        try:
            if path.stat().st_size > 1_000_000:
                continue
            yield path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue


def _has_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL) for pattern in patterns)


def _evidence(found: bool, found_text: str, missing_text: str) -> str:
    return found_text if found else missing_text
