#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from ios_linux_harness.prior_art import run_audit
from ios_linux_harness.reports import write_report_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the local novelty/report bundle.")
    parser.add_argument("--prior-art-root", type=Path, default=Path("out/prior-art"))
    parser.add_argument("--out-dir", type=Path, default=Path("out/results"))
    args = parser.parse_args()

    audit = run_audit(args.prior_art_root if args.prior_art_root.exists() else None)
    paths = write_report_bundle(audit, args.out_dir)
    print(f"wrote {paths.markdown}")
    print(f"wrote {paths.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
