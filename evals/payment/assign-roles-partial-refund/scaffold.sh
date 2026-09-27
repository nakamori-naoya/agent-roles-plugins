#!/usr/bin/env bash
# 仕事の説明を作業場所へ置く。
set -euo pipefail
CASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
mkdir -p out
cp "$CASE_DIR/materials/job.md" job.md
