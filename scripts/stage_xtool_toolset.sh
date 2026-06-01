#!/usr/bin/env bash
set -euo pipefail

STAGE="out/stage"
URL="${XTOOL_TOOLSET_URL:-https://github.com/xtool-org/darwin-tools-linux-llvm/releases/download/v1.0.1/toolset-aarch64.tar.gz}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stage)
      STAGE="$2"
      shift 2
      ;;
    --url)
      URL="$2"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

TOOLSET_DIR="$STAGE/xtool-toolset"
ARCHIVE="$TOOLSET_DIR/toolset-aarch64.tar.gz"
EXTRACTED="$TOOLSET_DIR/extracted"
LINKER="$EXTRACTED/bin/ld64.lld"

command -v curl >/dev/null || { echo "curl is required" >&2; exit 1; }
command -v tar >/dev/null || { echo "tar is required" >&2; exit 1; }

if [[ -x "$LINKER" ]]; then
  echo "exists $LINKER"
  exit 0
fi

mkdir -p "$TOOLSET_DIR" "$EXTRACTED"
if [[ ! -f "$ARCHIVE" ]]; then
  echo "download $URL"
  curl -L "$URL" -o "$ARCHIVE"
fi

tar -xzf "$ARCHIVE" -C "$EXTRACTED"

if [[ ! -x "$LINKER" ]]; then
  echo "toolset did not provide expected linker: $LINKER" >&2
  exit 1
fi

echo "staged $LINKER"
