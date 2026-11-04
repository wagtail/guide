"""Deterministic output-format assertions for the LLM translator eval.

These mirror the rules in apps/core/translator.py's system prompt: reply with
only the translated text, keep inline tags and structure intact, and keep
<a> ids while stripping other attributes.

Each function is referenced from promptfooconfig.yaml as
file://check_format.py:<function> and receives (output, context).
"""

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from glossary_util import matched_glossary

ALLOWED_TAGS = {
    "a",
    "abbr",
    "acronym",
    "b",
    "br",
    "code",
    "em",
    "i",
    "strong",
}

BLEED_PATTERNS = [
    r"^```",
    r"^(sure|here is|let me|certainly|of course|the translation is|translated text|translation)\b",
]
BLEED_RE = re.compile("|".join(BLEED_PATTERNS), re.IGNORECASE)


class TagCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.bold_texts = []
        self._bold_depth = 0
        self._bold_buf = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag in ("b", "i"):
            self._bold_depth += 1

    def handle_startendtag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_endtag(self, tag):
        if tag in ("b", "i") and self._bold_depth:
            self._bold_depth -= 1
            if not self._bold_depth:
                self.bold_texts.append("".join(self._bold_buf).strip())
                self._bold_buf = []

    def handle_data(self, data):
        if self._bold_depth:
            self._bold_buf.append(data)


def parse_html(html):
    parser = TagCollector()
    parser.feed(html or "")
    return parser


def _pass(reason):
    return {"pass": True, "score": 1, "reason": reason}


def _fail(reason):
    return {"pass": False, "score": 0, "reason": reason}


def no_wrapper(output, context):
    if not output:
        return _fail("empty output")
    stripped = output.strip()
    if BLEED_RE.search(stripped[:200]):
        return _fail(f"reasoning/wrapper bleed detected: {stripped[:60]!r}")
    if stripped.startswith(('"', "'", "\u201c")) and stripped.endswith(
        ('"', "'", "\u201d")
    ):
        return _fail(f"output wrapped in quotes: {stripped[:60]!r}")
    source = context["vars"].get("text", "")
    if "\n" not in source and "\n" in stripped:
        return _fail(
            f"output has multiple lines but source is single-line: {stripped[:60]!r}"
        )
    return _pass("no wrapper, quote, or bleed")


def allowed_tags_only(output, context):
    found = {tag for tag, _ in parse_html(output).tags}
    disallowed = found - ALLOWED_TAGS
    if disallowed:
        return _fail(f"disallowed tags: {sorted(disallowed)}")
    return _pass(f"tags within allowed set: {sorted(found)}")


def tags_preserved(output, context):
    source = context["vars"].get("text", "")
    src = [(tag, attrs.get("id")) for tag, attrs in parse_html(source).tags]
    out = [(tag, attrs.get("id")) for tag, attrs in parse_html(output).tags]
    # Strict equality both ways: also fails when the model invents tags in a
    # plain-prose source (a known failure mode).
    if src != out:
        return _fail(f"tags differ: source={src} output={out}")
    return _pass("tag sequence and ids preserved")


def attributes_clean(output, context):
    for tag, attrs in parse_html(output).tags:
        if tag == "a":
            extra = set(attrs) - {"id"}
            if extra:
                return _fail(f"<a> has non-id attributes: {sorted(extra)}")
        elif attrs:
            return _fail(f"<{tag}> has attributes: {attrs}")
    return _pass("no attributes beyond <a id>")


def not_truncated(output, context):
    source = context["vars"].get("text", "")
    stripped = (output or "").strip()
    if len(stripped) < 0.25 * len(source):
        return _fail(
            f"output suspiciously short ({len(stripped)} chars vs {len(source)} source)"
        )
    return _pass("output length plausible")


def glossary_compliant(output, context):
    """<b>/<i> labels use the official Wagtail admin translation, in place."""
    source = context["vars"].get("text", "")
    lang_code = context["vars"].get("lang_code", "")
    expected = matched_glossary(source, lang_code)
    if not expected:
        return _pass("no glossary terms in this segment")
    src_bold = parse_html(source).bold_texts
    out_bold = parse_html(output).bold_texts
    if len(out_bold) != len(src_bold):
        return _fail(
            f"<b>/<i> label count differs: source={src_bold} output={out_bold}"
        )
    for i, term in enumerate(src_bold):
        if term in expected and out_bold[i] != expected[term]:
            return _fail(
                f"label {term!r} should be {expected[term]!r}, got {out_bold[i]!r}"
            )
    return _pass(f"official translations used: {expected}")


def translated(output, context):
    source = context["vars"].get("text", "")
    if not output:
        return _fail("empty output")
    if output.strip() == source.strip():
        return _fail("output is identical to source (not translated)")
    return _pass("output differs from source")
