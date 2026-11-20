#!/usr/bin/env bash
set -euo pipefail
# OPTIONAL research-only environment, no iOS boot without compatible prepared firmware.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/experiments"
cd "$ROOT/experiments"
if [[ ! -d darwin-vm ]]; then
  git clone --recurse-submodules https://github.com/jprx/darwin-vm.git
else
  echo 'Repository exists; no automatic overwrite.'
fi
cat <<'MSG'
Source cloned. For full build/install instructions refer to upstream README.
Mac-dependent firmware preparation has NOT been completed.
Do NOT assume iPhone18,2 is supported or that GUI emulation works.
MSG
