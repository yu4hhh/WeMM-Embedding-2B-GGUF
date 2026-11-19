#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ROOT_DIR=$(cd -- "$SCRIPT_DIR/.." && pwd)

exec llama-server \
  -m "$ROOT_DIR/WeMM-Embedding-2B-Q4_K_M.gguf" \
  --embedding --port 8080

# In another shell:
# curl http://127.0.0.1:8080/v1/embeddings -H 'Content-Type: application/json' \
#   -d '{"input":"多模态检索测试"}'
