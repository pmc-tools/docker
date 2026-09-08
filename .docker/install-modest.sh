#!/usr/bin/env bash
set -euo pipefail

if [ -z "${TARGETPLATFORM:-}" ]; then
  echo "TARGETPLATFORM is not set (expected e.g. linux/amd64 or linux/arm64)" >&2
  exit 1
fi

case "${TARGETPLATFORM}" in
  linux/amd64) ARCH=linux-x64   ;;
  linux/arm64) ARCH=linux-arm64 ;;
  *)
    echo "Unsupported TARGETPLATFORM ${TARGETPLATFORM}" >&2
    exit 1
    ;;
esac

# The versioned filename is derived from the downloads page, e.g.
# Modest-Toolset-v3.1.311-g14c460466-linux-x64.zip
echo "Downloading Modest for ${TARGETPLATFORM}"
BASE="https://www.modestchecker.net/downloads"
STEM=$(curl -fsSL "${BASE}/" | grep -o 'Modest-Toolset-v[0-9.]\+-g[0-9a-f]\+' | head -n 1)
if [ -z "${STEM}" ]; then
  echo "Could not determine the current Modest version from ${BASE}/" >&2
  exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT
cd "${TMP}"

echo "Downloading ${STEM}-${ARCH}.zip"
curl -fsSLO "${BASE}/${STEM}-${ARCH}.zip"
unzip -q "${STEM}-${ARCH}.zip"

echo "Installing Modest to /opt/Modest"
if [ ! -d Modest ]; then
  echo "Expected a 'Modest' directory inside the download, not found" >&2
  exit 1
fi
rm -f "${STEM}-${ARCH}.zip"
rm -rf /opt/Modest
mv Modest /opt/Modest