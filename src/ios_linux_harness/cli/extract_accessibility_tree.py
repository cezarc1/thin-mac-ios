#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from ios_linux_harness.verification import write_accessibility_tree


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract marked XCUI accessibility output from an xcodebuild log.")
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if write_accessibility_tree(args.log, args.output):
        print(f"wrote {args.output}")
        return 0
    print(f"no complete accessibility tree found in {args.log}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
