#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from ios_linux_harness.hygiene import HygieneFinding, scan_for_forbidden_paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Reject committed Apple SDKs, build outputs, and signing material.")
    parser.add_argument("root", nargs="?", type=Path, default=Path("."))
    parser.add_argument("--all-files", action="store_true", help="Scan every file instead of only git-tracked files.")
    args = parser.parse_args()

    findings = scan_for_forbidden_paths(args.root) if args.all_files else scan_tracked_files(args.root)
    if findings:
        for finding in findings:
            print(f"{finding.kind}: {finding.path} - {finding.message}")
        return 1
    print("hygiene=clean")
    return 0


def scan_tracked_files(root: Path) -> list[HygieneFinding]:
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if completed.returncode != 0 or not completed.stdout:
        return scan_for_forbidden_paths(root)

    findings: list[HygieneFinding] = []
    for raw in completed.stdout.split(b"\0"):
        if not raw:
            continue
        path = root / raw.decode("utf-8")
        findings.extend(scan_forbidden_single_path(root, path))
    return findings


def scan_forbidden_single_path(root: Path, path: Path) -> list[HygieneFinding]:
    temp_root = path.parent
    raw_findings = scan_for_forbidden_paths(temp_root)
    relative = str(path.relative_to(temp_root))
    return [
        HygieneFinding(finding.kind, str(path.relative_to(root)), finding.message)
        for finding in raw_findings
        if finding.path == relative
    ]


if __name__ == "__main__":
    raise SystemExit(main())
