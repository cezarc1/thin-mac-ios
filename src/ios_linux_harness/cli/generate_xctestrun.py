#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from ios_linux_harness.xctestrun import write_xctestrun


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a minimal xctestrun plist for Linux-built test bundles.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--product-module-name", required=True)
    parser.add_argument("--test-bundle-path", required=True)
    parser.add_argument("--test-host-path", required=True)
    parser.add_argument("--ui-target-app-path")
    parser.add_argument("--ui-test", action="store_true")
    args = parser.parse_args()

    write_xctestrun(
        args.output,
        product_module_name=args.product_module_name,
        test_bundle_path=args.test_bundle_path,
        test_host_path=args.test_host_path,
        ui_target_app_path=args.ui_target_app_path,
        is_ui_test=args.ui_test,
    )
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
