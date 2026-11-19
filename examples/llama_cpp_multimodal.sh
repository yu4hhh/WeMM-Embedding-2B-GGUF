#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ROOT_DIR=$(cd -- "$SCRIPT_DIR/.." && pwd)

# The projector is BF16 and must be paired with a main GGUF:
exec llama-server \
  -m "$ROOT_DIR/WeMM-Embedding-2B-Q4_K_M.gguf" \
  --mmproj "$ROOT_DIR/mmproj-WeMM-Embedding-2B-BF16.gguf" \
  --embedding --port 8080

# In another shell, send an image with the current llama.cpp API:
# python3 examples/llama_cpp_multimodal_embedding.py --image ./image.jpg
#
# The server generates a marker at startup. The client reads it from /props and
# sends a prompt object containing prompt_string + multimodal_data. Do not use
# the legacy image_data/[img-N] payload: current llama.cpp can silently treat it
# as ordinary text for embedding requests.
