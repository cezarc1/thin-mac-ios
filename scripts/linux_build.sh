#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURE_ROOT="$REPO_ROOT/fixtures/ios-app"
STAGE="$REPO_ROOT/out/stage"
DOCKER_IMAGE="swift:6.3"
TARGET="arm64-apple-ios26.0-simulator"
MIN_VERSION="26.0"
SDK_VERSION="26.5"
BUNDLE_ID="dev.example.IOSLinuxVerificationHarness"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stage)
      STAGE="$2"
      shift 2
      ;;
    --docker-image)
      DOCKER_IMAGE="$2"
      shift 2
      ;;
    --target)
      TARGET="$2"
      shift 2
      ;;
    --min-version)
      MIN_VERSION="$2"
      shift 2
      ;;
    --sdk-version)
      SDK_VERSION="$2"
      shift 2
      ;;
    --bundle-id)
      BUNDLE_ID="$2"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

command -v docker >/dev/null || { echo "docker is required" >&2; exit 1; }

SDK="$STAGE/xcode/iPhoneSimulator.sdk"
LINKER="$STAGE/xtool-toolset/extracted/bin/ld64.lld"

if [[ ! -d "$SDK" ]]; then
  echo "missing staged SDK: $SDK" >&2
  echo "run: scripts/package_sdk.sh --stage $STAGE" >&2
  exit 1
fi

if [[ ! -d "$STAGE/xcode/clang" ]]; then
  echo "missing staged clang resource directory: $STAGE/xcode/clang" >&2
  echo "run: scripts/package_sdk.sh --stage $STAGE" >&2
  exit 1
fi

if [[ ! -x "$LINKER" ]]; then
  echo "missing xtool Darwin linker: $LINKER" >&2
  echo "run: scripts/stage_xtool_toolset.sh --stage $STAGE" >&2
  exit 1
fi

CLANG_VERSION_DIR="$(find "$STAGE/xcode/clang" -mindepth 1 -maxdepth 1 -type d | sort -Vr | head -1)"
if [[ -z "$CLANG_VERSION_DIR" ]]; then
  echo "missing staged clang resource directory under $STAGE/xcode/clang" >&2
  exit 1
fi

CLANG_VERSION="$(basename "$CLANG_VERSION_DIR")"
BUILD="$STAGE/build"
APP="$BUILD/ExampleApp.app"
FRAMEWORKS="$BUILD/BinaryFrameworks"
PROBE_FRAMEWORK="$FRAMEWORKS/ProbeBinaryKit.framework"

rm -rf "$BUILD"
mkdir -p "$APP/Frameworks" "$PROBE_FRAMEWORK/Headers" "$PROBE_FRAMEWORK/Modules"
cp "$FIXTURE_ROOT/Sources/ProbeBinaryKit/ProbeBinaryKit.h" "$PROBE_FRAMEWORK/Headers/ProbeBinaryKit.h"
cp "$FIXTURE_ROOT/Sources/ProbeBinaryKit/module.modulemap" "$PROBE_FRAMEWORK/Modules/module.modulemap"

python3 - "$APP" "$PROBE_FRAMEWORK" "$BUNDLE_ID" <<'PY'
import plistlib
import sys
from pathlib import Path

app = Path(sys.argv[1])
framework = Path(sys.argv[2])
bundle_id = sys.argv[3]

app_plist = {
    "CFBundleDevelopmentRegion": "en",
    "CFBundleExecutable": "ExampleApp",
    "CFBundleIdentifier": bundle_id,
    "CFBundleInfoDictionaryVersion": "6.0",
    "CFBundleName": "ExampleApp",
    "CFBundlePackageType": "APPL",
    "CFBundleShortVersionString": "1.0",
    "CFBundleVersion": "1",
    "LSRequiresIPhoneOS": True,
    "UIApplicationSceneManifest": {
        "UIApplicationSupportsMultipleScenes": False,
        "UISceneConfigurations": {},
    },
    "UILaunchScreen": {},
}
framework_plist = {
    "CFBundleExecutable": "ProbeBinaryKit",
    "CFBundleIdentifier": "dev.example.ProbeBinaryKit",
    "CFBundleInfoDictionaryVersion": "6.0",
    "CFBundleName": "ProbeBinaryKit",
    "CFBundlePackageType": "FMWK",
    "CFBundleShortVersionString": "1.0",
    "CFBundleSupportedPlatforms": ["iPhoneSimulator"],
    "CFBundleVersion": "1",
}
entitlements = {
    "application-identifier": f"ABCDE12345.{bundle_id}",
    "com.apple.developer.team-identifier": "ABCDE12345",
    "get-task-allow": True,
}
with (app / "Info.plist").open("wb") as handle:
    plistlib.dump(app_plist, handle, sort_keys=False)
with (framework / "Info.plist").open("wb") as handle:
    plistlib.dump(framework_plist, handle, sort_keys=False)
with (app.parent / "ExampleApp.entitlements").open("wb") as handle:
    plistlib.dump(entitlements, handle, sort_keys=False)
PY

docker run --rm \
  -v "$FIXTURE_ROOT:/fixture:ro" \
  -v "$STAGE:/work" \
  "$DOCKER_IMAGE" \
  bash -lc "
set -euo pipefail
COMMON='-target $TARGET -sdk /work/xcode/iPhoneSimulator.sdk -resource-dir /work/xcode/swift -Xcc -resource-dir -Xcc /work/xcode/clang/$CLANG_VERSION -module-cache-path /tmp/swift-module-cache'

clang -target $TARGET \
  -isysroot /work/xcode/iPhoneSimulator.sdk \
  -resource-dir /work/xcode/clang/$CLANG_VERSION \
  -fPIC \
  -I /work/build/BinaryFrameworks/ProbeBinaryKit.framework/Headers \
  -c /fixture/Sources/ProbeBinaryKit/ProbeBinaryKit.c \
  -o /work/build/ProbeBinaryKit.o

/work/xtool-toolset/extracted/bin/ld64.lld \
  -arch arm64 \
  -platform_version ios-simulator $MIN_VERSION $SDK_VERSION \
  -syslibroot /work/xcode/iPhoneSimulator.sdk \
  -dylib \
  -install_name @rpath/ProbeBinaryKit.framework/ProbeBinaryKit \
  -o /work/build/BinaryFrameworks/ProbeBinaryKit.framework/ProbeBinaryKit \
  /work/build/ProbeBinaryKit.o \
  -lSystem \
  /work/xcode/clang/$CLANG_VERSION/lib/darwin/libclang_rt.iossim.a

swiftc \$COMMON \
  -module-name ExampleApp \
  -F /work/build/BinaryFrameworks \
  -Xcc -F -Xcc /work/build/BinaryFrameworks \
  -typecheck /fixture/Sources/ExampleApp/ExampleApp.swift /fixture/Sources/ExampleApp/ContentView.swift

swiftc \$COMMON \
  -module-name ExampleApp \
  -F /work/build/BinaryFrameworks \
  -Xcc -F -Xcc /work/build/BinaryFrameworks \
  -whole-module-optimization \
  -c /fixture/Sources/ExampleApp/ExampleApp.swift /fixture/Sources/ExampleApp/ContentView.swift \
  -o /work/build/ExampleApp.o

/work/xtool-toolset/extracted/bin/ld64.lld \
  -arch arm64 \
  -platform_version ios-simulator $MIN_VERSION $SDK_VERSION \
  -syslibroot /work/xcode/iPhoneSimulator.sdk \
  -L /work/xcode/swift/iphonesimulator \
  -L /work/xcode/iPhoneSimulator.sdk/usr/lib/swift \
  -F /work/build/BinaryFrameworks \
  -F /work/xcode/iPhoneSimulator.sdk/System/Library/Frameworks \
  -rpath /usr/lib/swift \
  -rpath @executable_path/Frameworks \
  -framework ProbeBinaryKit \
  -framework SwiftUI \
  -framework UIKit \
  -framework Foundation \
  -sectcreate __TEXT __entitlements /work/build/ExampleApp.entitlements \
  -o /work/build/ExampleApp.app/ExampleApp \
  /work/build/ExampleApp.o \
  -lSystem \
  /work/xcode/clang/$CLANG_VERSION/lib/darwin/libclang_rt.iossim.a
"

cp -R "$PROBE_FRAMEWORK" "$APP/Frameworks/ProbeBinaryKit.framework"
PYTHONPATH="$REPO_ROOT/src" python3 -m ios_linux_harness.cli.report --out-dir "$REPO_ROOT/out/results" >/dev/null
echo "built $APP"
