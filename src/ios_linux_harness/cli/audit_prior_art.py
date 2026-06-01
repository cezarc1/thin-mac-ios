#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from ios_linux_harness.prior_art import REQUIRED_PROJECTS, run_audit
from ios_linux_harness.reports import write_report_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit source-visible prior art and emit a novelty matrix.")
    parser.add_argument("--prior-art-root", type=Path, default=Path("out/prior-art"))
    parser.add_argument("--out-dir", type=Path, default=Path("out/results"))
    parser.add_argument("--fetch", action="store_true", help="Shallow-clone missing prior-art repositories.")
    args = parser.parse_args()

    if args.fetch:
        fetch_prior_art(args.prior_art_root)

    audit = run_audit(args.prior_art_root if args.prior_art_root.exists() else None)
    paths = write_report_bundle(audit, args.out_dir)
    print(f"wrote {paths.markdown}")
    print(f"wrote {paths.json}")
    print(f"publish_gate={audit.publish_gate}")
    print(audit.publish_gate_reason)
    return 0 if audit.publish_gate == "pass" else 2


def fetch_prior_art(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for project, url in REQUIRED_PROJECTS.items():
        target = root / project
        if target.exists():
            subprocess.run(["git", "-C", str(target), "fetch", "--depth", "1", "origin"], check=False)
            subprocess.run(["git", "-C", str(target), "reset", "--hard", "FETCH_HEAD"], check=False)
            continue
        subprocess.run(["git", "clone", "--depth", "1", url, str(target)], check=True)


if __name__ == "__main__":
    raise SystemExit(main())
