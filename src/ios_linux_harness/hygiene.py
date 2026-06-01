from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HygieneFinding:
    kind: str
    path: str
    message: str


def scan_for_forbidden_paths(root: Path) -> list[HygieneFinding]:
    findings: list[HygieneFinding] = []
    for path in _walk_paths(root):
        kind = _classify_forbidden_path(path)
        if kind:
            findings.append(
                HygieneFinding(
                    kind=kind,
                    path=str(path.relative_to(root)),
                    message=_message_for(kind),
                )
            )
    return findings


def _walk_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts or "out" in path.parts:
            continue
        paths.append(path)
    return paths


def _classify_forbidden_path(path: Path) -> str | None:
    name = path.name
    suffix = path.suffix.lower()
    if name.endswith(".sdk") and ("Simulator" in name or name in {"MacOSX.sdk", "iPhoneOS.sdk"}):
        return "apple_sdk"
    if name.endswith(".xcresult"):
        return "xcresult_bundle"
    if suffix == ".p8" or name.startswith("AuthKey_"):
        return "signing_key"
    if suffix in {".mobileprovision", ".provisionprofile"}:
        return "provisioning_profile"
    if suffix in {".p12", ".cer"}:
        return "signing_certificate"
    if suffix in {".ipa", ".xctest"} or name.endswith(".app"):
        return "build_artifact"
    return None


def _message_for(kind: str) -> str:
    messages = {
        "apple_sdk": "Apple SDKs must be staged locally, not committed.",
        "xcresult_bundle": "Xcode result bundles are generated evidence, not source.",
        "signing_key": "Signing keys must never be committed.",
        "provisioning_profile": "Provisioning profiles must never be committed.",
        "signing_certificate": "Signing certificates must never be committed.",
        "build_artifact": "Built Apple artifacts belong under ignored output directories.",
    }
    return messages[kind]
