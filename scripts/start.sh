#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose up -d --build
printf 'Dashboard: http://localhost:6080\n'
