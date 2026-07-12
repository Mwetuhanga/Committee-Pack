#!/usr/bin/env python3
"""Generate a self-contained interactive committee pack HTML file from a YAML data file.

Usage:
    python build/generate_pack.py data/pack.yaml dist/committee-pack.html

Any PDF referenced via a `source_file` key in the data file is embedded as a
base64 data URI if it exists on disk (relative to the repo root). If it does
not exist, the dashboard shows a "source document not attached" note instead
of failing the build — useful for drafting a cycle's data before all source
PDFs have been collected.
"""
import base64
import json
import mimetypes
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = REPO_ROOT / "build" / "template" / "pack_template.html"


def collect_source_files(data: dict) -> set:
    paths = set()

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "source_file" and value:
                    paths.add(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return paths


def embed_files(paths: set) -> dict:
    embedded = {}
    for rel_path in sorted(paths):
        full_path = REPO_ROOT / rel_path
        if not full_path.is_file():
            print(f"  (source not found, will show as unattached: {rel_path})")
            continue
        mime, _ = mimetypes.guess_type(full_path.name)
        mime = mime or "application/octet-stream"
        b64 = base64.b64encode(full_path.read_bytes()).decode("ascii")
        embedded[rel_path] = f"data:{mime};base64,{b64}"
        print(f"  embedded: {rel_path} ({full_path.stat().st_size // 1024} KB)")
    return embedded


def js_string_literal(value) -> str:
    """JSON-encode a value for safe embedding inside an inline <script> block.

    A raw `</script` sequence inside a JSON string would terminate the
    enclosing <script> tag early (the HTML tokenizer doesn't know it's inside
    a JS string literal), so it must be escaped. This matters most for the
    embedded template source, which necessarily contains many literal
    `<script>`/`</script>` tags.
    """
    encoded = json.dumps(value, ensure_ascii=False)
    return encoded.replace("</script", "<\\/script").replace("<!--", "<\\!--")


def generate(data_path: Path, output_path: Path) -> None:
    with open(data_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    print(f"Loaded data file: {data_path}")

    source_paths = collect_source_files(data)
    print(f"Found {len(source_paths)} referenced source document(s):")
    embedded = embed_files(source_paths)

    # Captured before any substitution — this is what lets Admin Mode's
    # "export updated pack" button rebuild a fresh standalone HTML file
    # entirely client-side, without needing Python again.
    raw_template = TEMPLATE_PATH.read_text(encoding="utf-8")

    title = f"{data['meeting']['entity']} — {data['meeting']['committee']} Pack — {data['meeting']['cycle_label']}"

    output = raw_template.replace("__PACK_TITLE__", title)
    output = output.replace("__PACK_DATA_JSON__", json.dumps(data, ensure_ascii=False).replace("</script", "<\\/script"))
    output = output.replace("__PACK_FILES_JSON__", json.dumps(embedded, ensure_ascii=False).replace("</script", "<\\/script"))
    # Must be last: the payload itself still contains the other three
    # placeholder tokens (and this one) as literal text, since it's the
    # pristine pre-substitution template — an earlier replace() would
    # corrupt it.
    output = output.replace("__PACK_TEMPLATE_SOURCE_JSON__", js_string_literal(raw_template))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")

    size_kb = output_path.stat().st_size // 1024
    print(f"\nWrote {output_path} ({size_kb} KB)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    generate(Path(sys.argv[1]), Path(sys.argv[2]))
