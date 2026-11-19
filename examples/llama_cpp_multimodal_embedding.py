#!/usr/bin/env python3
"""Create an image or video embedding with llama.cpp's current MTMD API.

The server must be started with --mmproj and --embedding. The media marker is
generated per server process, so this client obtains it from /props instead of
hard-coding it.
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import pathlib
import sys
import urllib.error
import urllib.request

SUPPORTED_DIMENSIONS = (64, 128, 256, 512, 1024, 2048)


def post_json(url: str, payload: dict) -> object:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer no-key"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"llama.cpp returned HTTP {error.code}: {detail}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"could not connect to llama.cpp at {url}: {error.reason}") from error


def get_json(url: str) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read())
    except urllib.error.URLError as error:
        raise RuntimeError(f"could not connect to llama.cpp at {url}: {error.reason}") from error


def extract_embedding(response: object) -> list[float]:
    # /embedding returns [{"embedding": [[...]]}].
    if isinstance(response, list) and response:
        embedding = response[0]["embedding"]
        return embedding[0] if embedding and isinstance(embedding[0], list) else embedding

    # /v1/embeddings returns {"data": [{"embedding": [...]}]}.
    if isinstance(response, dict) and response.get("data"):
        return response["data"][0]["embedding"]

    raise RuntimeError(f"unrecognized embedding response: {response!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--media", "--image", "--video", dest="media", required=True,
        help="image or video file accepted by llama.cpp MTMD (video requires ffmpeg/ffprobe)",
    )
    parser.add_argument("--server", default="http://127.0.0.1:8080", help="llama-server base URL")
    parser.add_argument("--caption", default="", help="optional text placed before the media")
    parser.add_argument(
        "--dimension",
        type=int,
        choices=SUPPORTED_DIMENSIONS,
        help="optional Matryoshka output dimension",
    )
    parser.add_argument("--model", default="WeMM-Embedding-2B-Q4_K_M.gguf", help="model name for /v1/embeddings")
    parser.add_argument("--openai-compatible", action="store_true", help="use /v1/embeddings instead of /embedding")
    parser.add_argument("--output", help="optional JSON output path; otherwise print to stdout")
    args = parser.parse_args()

    media_path = pathlib.Path(args.media)
    if not media_path.is_file():
        raise RuntimeError(f"media file does not exist: {media_path}")

    server = args.server.rstrip("/")
    props = get_json(f"{server}/props")
    marker = props.get("media_marker")
    if not marker:
        raise RuntimeError("llama.cpp /props did not return media_marker")

    media_b64 = base64.b64encode(media_path.read_bytes()).decode("ascii")
    prompt_string = f"{args.caption}\n{marker}" if args.caption else marker
    prompt = {"prompt_string": prompt_string, "multimodal_data": [media_b64]}

    if args.openai_compatible:
        endpoint = f"{server}/v1/embeddings"
        payload = {"model": args.model, "input": prompt, "encoding_format": "float"}
    else:
        endpoint = f"{server}/embedding"
        payload = {"content": prompt}

    embedding = extract_embedding(post_json(endpoint, payload))
    if args.dimension is not None:
        embedding = embedding[:args.dimension]
        prefix_norm = math.sqrt(sum(value * value for value in embedding))
        if prefix_norm == 0:
            raise RuntimeError("cannot normalize a zero-length truncated embedding")
        embedding = [value / prefix_norm for value in embedding]
    norm = math.sqrt(sum(value * value for value in embedding))
    result = {
        "model": args.model,
        "media": str(media_path),
        "dimension": len(embedding),
        "norm": norm,
        "embedding": embedding,
    }

    rendered = json.dumps(result, ensure_ascii=False)
    if args.output:
        pathlib.Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
