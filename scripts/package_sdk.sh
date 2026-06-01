#!/usr/bin/env bash
set -euo pipefail

XCODE="/Applications/Xcode.app"
STAGE="out/stage"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --xcode)
      XCODE="$2"
      shift 2
      ;;
    --stage)
      STAGE="$2"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

DEVELOPER="$XCODE/Contents/Developer"
TOOLCHAIN="$DEVELOPER/Toolchains/XcodeDefault.xctoolchain/usr"
SIM_PLATFORM="$DEVELOPER/Platforms/iPhoneSimulator.platform"
SIM_SDK="$SIM_PLATFORM/Developer/SDKs/iPhoneSimulator.sdk"
DEV_FRAMEWORKS="$SIM_PLATFORM/Developer/Library/Frameworks"
DEV_PRIVATE_FRAMEWORKS="$SIM_PLATFORM/Developer/Library/PrivateFrameworks"
CLANG_DIR="$TOOLCHAIN/lib/clang"

for path in "$SIM_SDK" "$TOOLCHAIN/lib/swift" "$CLANG_DIR" "$DEV_FRAMEWORKS" "$DEV_PRIVATE_FRAMEWORKS"; do
  if [[ ! -e "$path" ]]; then
    echo "missing required Xcode path: $path" >&2
    exit 1
  fi
done

mkdir -p "$STAGE/xcode"

copy_once() {
  local src="$1"
  local dst="$2"
  if [[ -e "$dst" ]]; then
    echo "exists $dst"
    return
  fi
  echo "copy $src -> $dst"
  /usr/bin/ditto "$src" "$dst"
}

copy_once "$SIM_SDK" "$STAGE/xcode/iPhoneSimulator.sdk"
copy_once "$TOOLCHAIN/lib/swift" "$STAGE/xcode/swift"
copy_once "$CLANG_DIR" "$STAGE/xcode/clang"
copy_once "$DEV_FRAMEWORKS" "$STAGE/xcode/iPhoneSimulatorDeveloperLibraryFrameworks"
copy_once "$DEV_PRIVATE_FRAMEWORKS" "$STAGE/xcode/iPhoneSimulatorDeveloperLibraryPrivateFrameworks"

python3 - "$XCODE" "$STAGE" <<'PY'
import json
import sys
from pathlib import Path

xcode = Path(sys.argv[1])
stage = Path(sys.argv[2])
metadata = {
    "xcode": str(xcode),
    "stage": str(stage),
    "note": "Local Apple SDK staging only. Do not commit this directory.",
}
(stage / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
PY

echo "staged Xcode simulator inputs under $STAGE/xcode"
