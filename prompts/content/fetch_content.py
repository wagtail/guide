#!/usr/bin/env -S uv run
# /// script
# dependencies = ["httpx", "tiktoken"]
# ///
"""Download the site contents for experimentation with LLMs."""

import logging
import re
from pathlib import Path
from urllib.parse import urlparse

import httpx
import tiktoken

logger = logging.getLogger(__name__)

LLMS_URL = "https://guide.wagtail.org/llms.txt"
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "en-latest"
README_PATH = BASE_DIR.parent / "README.md"
URL_RE = re.compile(r"https?://[^\s]+")

TOKENIZER_MODEL = "gpt-oss-120b"


def clean_url(url: str) -> str:
    return url.strip().strip("()[]<>.,;:")


def safe_path_for_url(url: str) -> Path:
    parsed = urlparse(url)
    path = (parsed.path or "/").rstrip("/")
    parts = [part for part in path.split("/") if part]
    if not parts:
        parts = ["index"]
    if parts[0] == "en-latest":
        parts = parts[1:] or ["index"]
    if parts[-1] == "markdown" and len(parts) > 1:
        filename = parts[-2]
        if Path(filename).suffix == "":
            filename = f"{filename}.md"
        return Path(*parts[:-2], filename)
    filename = parts[-1]
    if Path(filename).suffix == "":
        filename = f"{filename}.md"
    return Path(*parts[:-1], filename)


def update_readme(token_counts: list[tuple[Path, int]]) -> None:
    start = "<!-- TOKEN_COUNTS_START -->"
    end = "<!-- TOKEN_COUNTS_END -->"

    lines = [
        start,
        "",
        f"Token counts ({TOKENIZER_MODEL}):",
        "",
        "| File | Tokens |",
        "| --- | ---: |",
    ]
    for rel_path, tokens in token_counts:
        link = f"[{rel_path}](content/en-latest/{rel_path})"
        lines.append(f"| {link} | {tokens} |")
    lines += ["", end]

    text = README_PATH.read_text(encoding="utf-8")

    before = text.split(start, 1)[0].rstrip()
    after = text.split(end, 1)[1].lstrip()
    text = f"{before}\n{'\n'.join(lines)}\n{after}"

    README_PATH.write_text(text, encoding="utf-8")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with httpx.Client(follow_redirects=True, timeout=30.0) as client:
        llms_txt = client.get(LLMS_URL).raise_for_status().text
        llms_path = OUTPUT_DIR / "llms.txt"
        llms_path.write_text(llms_txt, encoding="utf-8")

        encoding = tiktoken.encoding_for_model(TOKENIZER_MODEL)
        token_counts: list[tuple[Path, int]] = []

        llms_tokens = len(encoding.encode(llms_txt))
        token_counts.append(("llms.txt", llms_tokens))

        for url in URL_RE.findall(llms_txt):
            url = clean_url(url)
            target = OUTPUT_DIR / safe_path_for_url(url)
            target.parent.mkdir(parents=True, exist_ok=True)
            content = client.get(url).raise_for_status().text
            target.write_text(content, encoding="utf-8")
            tokens = len(encoding.encode(content))
            rel_path = target.relative_to(OUTPUT_DIR)
            token_counts.append((rel_path, tokens))
            logger.info(f"Downloaded: ({tokens} tokens) {rel_path}")

    update_readme(token_counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
