#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ROOT_DIR=$(cd -- "$SCRIPT_DIR/.." && pwd)

command -v modelscope >/dev/null 2>&1 || {
  echo "Install ModelScope first: python3 -m pip install -U modelscope" >&2
  exit 1
}

MODEL_ID=${MODEL_ID:-huangyusi/WeMM-Embedding-2B-GGUF}
OUTPUT_DIR=${OUTPUT_DIR:-"$ROOT_DIR/models"}

exec modelscope download \
  --model "$MODEL_ID" \
  --include 'WeMM-Embedding-2B-Q4_K_M.gguf' \
  --include 'mmproj-WeMM-Embedding-2B-BF16.gguf' \
  --local_dir "$OUTPUT_DIR"
