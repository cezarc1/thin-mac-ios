#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$REPO_ROOT/out/stage/build/ExampleApp.app"
DEVICE="iPhone 17 Pro"
RESULT="$REPO_ROOT/out/results/verification-report.json"
XCTESTRUN=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --app)
      APP="$2"
      shift 2
      ;;
    --device)
      DEVICE="$2"
      shift 2
      ;;
    --result)
      RESULT="$2"
      shift 2
      ;;
    --xctestrun)
      XCTESTRUN="$2"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

command -v xcrun >/dev/null || { echo "xcrun is required" >&2; exit 1; }
command -v xcodebuild >/dev/null || { echo "xcodebuild is required" >&2; exit 1; }

if [[ ! -d "$APP" ]]; then
  echo "missing app bundle: $APP" >&2
  exit 1
fi

RESULT_DIR="$(dirname "$RESULT")"
mkdir -p "$RESULT_DIR"
DEVICES_JSON="$(mktemp)"
xcrun simctl list devices available -j >"$DEVICES_JSON"
UDID="$(python3 - "$DEVICES_JSON" "$DEVICE" <<'PY'
import json
import sys

devices = json.loads(open(sys.argv[1], encoding="utf-8").read())["devices"]
needle = sys.argv[2]
for runtime_devices in devices.values():
    for device in runtime_devices:
        if device.get("udid") == needle or device.get("name") == needle:
            print(device["udid"])
            raise SystemExit(0)
raise SystemExit(1)
PY
)"
rm -f "$DEVICES_JSON"

BUNDLE_ID="$(python3 - "$APP/Info.plist" <<'PY'
import plistlib
import sys
print(plistlib.loads(open(sys.argv[1], "rb").read())["CFBundleIdentifier"])
PY
)"

set +e
BOOT_OUTPUT="$(xcrun simctl boot "$UDID" 2>&1)"
BOOT_STATUS=$?
set -e
if [[ "$BOOT_STATUS" -ne 0 ]] && ! grep -qi "current state: Booted" <<<"$BOOT_OUTPUT"; then
  printf '%s\n' "$BOOT_OUTPUT" >&2
  exit "$BOOT_STATUS"
fi
xcrun simctl bootstatus "$UDID" -b
xcrun simctl install "$UDID" "$APP"
xcrun simctl launch "$UDID" "$BUNDLE_ID" >"$RESULT_DIR/launch.log"

SCREENSHOT="$RESULT_DIR/example-app.png"
xcrun simctl io "$UDID" screenshot "$SCREENSHOT"

XCODEBUILD_STATUS="not_run"
XCODEBUILD_LOG="$RESULT_DIR/test-without-building.log"
ACCESSIBILITY_TREE="$RESULT_DIR/accessibility-tree.txt"
ACCESSIBILITY_EXTRACTED="false"
if [[ -n "$XCTESTRUN" ]]; then
  set +e
  xcodebuild test-without-building \
    -xctestrun "$XCTESTRUN" \
    -destination "platform=iOS Simulator,id=$UDID" \
    -resultBundlePath "$RESULT_DIR/Verification.xcresult" \
    2>&1 | tee "$XCODEBUILD_LOG"
  XCODEBUILD_EXIT="${PIPESTATUS[0]}"
  set -e
  if [[ "$XCODEBUILD_EXIT" -ne 0 ]]; then
    exit "$XCODEBUILD_EXIT"
  fi
  XCODEBUILD_STATUS="passed"
  if PYTHONPATH="$REPO_ROOT/src" python3 -m ios_linux_harness.cli.extract_accessibility_tree --log "$XCODEBUILD_LOG" --output "$ACCESSIBILITY_TREE"; then
    ACCESSIBILITY_EXTRACTED="true"
  fi
fi

python3 - "$RESULT" "$UDID" "$APP" "$BUNDLE_ID" "$SCREENSHOT" "$XCODEBUILD_STATUS" "$ACCESSIBILITY_TREE" "$ACCESSIBILITY_EXTRACTED" <<'PY'
import json
import sys
from pathlib import Path

result, udid, app, bundle_id, screenshot, xcodebuild_status, accessibility_tree, accessibility_extracted = sys.argv[1:]
tree_extracted = accessibility_extracted == "true"
payload = {
    "status": "success",
    "device_udid": udid,
    "app": app,
    "bundle_id": bundle_id,
    "screenshot": screenshot,
    "screenshot_bytes": Path(screenshot).stat().st_size,
    "xcodebuild_test_without_building": xcodebuild_status,
    "accessibility_tree": accessibility_tree if tree_extracted else None,
    "accessibility_tree_extracted": tree_extracted,
}
Path(result).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY

echo "wrote $RESULT"
