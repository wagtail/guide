"""Generate documents.json for the batch translation eval from real guide content.

Converts versioned guide markdown (prompts/content/en/...) into the same
translatable-segment form wagtail-localize produces:
- [text](href) -> <a id="aN">text</a>, **text** -> <b>text</b>, `text` -> <code>text</code>
- headings, paragraphs, and list items become one segment each
- the page title (H1), "Page URL" line, images, and "---" rules are skipped

Re-run after editing the source content, then regenerate the test files:

    uv run python prompts/evals/translations-batch/build_documents.py
    uv run python prompts/evals/translations-batch/build_tests.py
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
CONTENT = HERE.parents[1] / "content" / "en"

# (markdown path relative to content/en, document id)
PAGES = [
    ("how-to-guides/manage-pages.md", "manage-pages"),
    ("about.md", "about"),
]


def md_inline(text: str, next_link_id: int) -> tuple[str, int]:
    """Convert inline markdown to the HTML segment form, numbering <a> ids."""
    link_id = next_link_id

    def link_repl(match: re.Match) -> str:
        nonlocal link_id
        link_id += 1
        return f'<a id="a{link_id - 1}">{match.group(1)}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\w)\*([^*\n]+)\*(?!\w)", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text, link_id


def segment_markdown(md: str) -> list[str]:
    """Split guide markdown into translatable segments."""
    segments: list[str] = []
    link_id = 0
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        # Skip page title (H1), URL line, images, rules, blank lines.
        if (
            stripped.startswith("# ")
            or stripped.startswith("Page URL:")
            or stripped.startswith("![")
            or stripped in ("", "---")
        ):
            i += 1
            continue
        if stripped.startswith("#"):
            # Headings: strip the hashes and any bold markup.
            segments.append(stripped.lstrip("#").strip().replace("**", ""))
            i += 1
            continue
        if stripped.startswith("- "):
            text, link_id = md_inline(stripped[2:], link_id)
            segments.append(text.strip())
            i += 1
            continue
        # Blockquote intro or plain paragraph: accumulate to the blank line.
        para: list[str] = []
        while i < len(lines):
            current = lines[i].strip()
            if current.startswith("![") or current in ("", "---"):
                break
            para.append(current.lstrip("> "))
            i += 1
        text, link_id = md_inline(" ".join(para), link_id)
        segments.append(text)
    return segments


def main() -> None:
    docs = []
    for rel_path, doc_id in PAGES:
        md = (CONTENT / rel_path).read_text(encoding="utf-8")
        segments = segment_markdown(md)
        cases = [{"id": f"s{n}", "text": seg} for n, seg in enumerate(segments, 1)]
        docs.append(
            {
                "id": doc_id,
                "description": (
                    f"Full page: {rel_path} — {len(cases)} segments, "
                    f"{sum(len(c['text']) for c in cases)} chars"
                ),
                "vars": {"doc": json.dumps(cases, ensure_ascii=False)},
            }
        )
        print(f"{doc_id}: {len(cases)} segments")

    path = HERE / "documents.json"
    path.write_text(json.dumps(docs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
