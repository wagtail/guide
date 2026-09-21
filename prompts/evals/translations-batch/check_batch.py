"""Deterministic assertions for the batch (document-level) translation eval.

Each function receives (output, context) from Promptfoo and returns
{"pass", "score", "reason"}. They check the LLM respected the document
envelope (XML or JSON), and that each translated segment preserved the
structure rules enforced by the per-segment translator:
same segment ids/count/order, inline tags + <a id> preserved, no attributes
beyond <a id>, official UI label translations in place, no truncation.
"""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "translations"))

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

BLEED_RE = re.compile(
    r"^```|^(sure|here is|let me|certainly|of course|the translation is|translated text|translation)\b",
    re.IGNORECASE,
)


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


def parse_segments(output, fmt):
    """Decode the envelope into [(id, text)] in order, or (None, error)."""
    stripped = (output or "").strip()
    if not stripped:
        return None, "empty output"
    if fmt == "xml":
        if not re.match(r"<\s*document\b", stripped):
            return None, "output does not start with <document>"
        segs = re.findall(
            r'<segment\s+id="([^"]+)"\s*>(.*?)</segment>', stripped, re.DOTALL
        )
        if not segs:
            return None, "no <segment> elements found in <document>"
        return [(sid, text) for sid, text in segs], None
    # json / json-schema: tolerate a code fence
    unfenced = re.sub(r"^```(?:json)?\s*|\s*```$", "", stripped).strip()
    try:
        data = json.loads(unfenced)
    except json.JSONDecodeError as exc:
        return None, f"output is not valid JSON: {exc}"
    if fmt == "json-schema":
        if not isinstance(data, dict) or "segments" not in data:
            return None, (
                f'JSON output is {type(data).__name__}, expected {{"segments": [...]}}'
            )
        data = data["segments"]
    if not isinstance(data, list):
        return None, f"JSON output is {type(data).__name__}, not an array"
    parsed = []
    for item in data:
        if not isinstance(item, dict) or "id" not in item or "text" not in item:
            return None, "JSON array items must be objects with id and text"
        parsed.append((str(item["id"]), str(item["text"])))
    return parsed, None


def source_cases(context):
    return json.loads(context["vars"]["doc"])


def envelope(output, context):
    """Output parses as the requested envelope and ids match source exactly."""
    fmt = context["vars"]["format"]
    parsed, error = parse_segments(output, fmt)
    if error:
        return _fail(error)
    src = [case["id"] for case in source_cases(context)]
    got = [sid for sid, _text in parsed]
    if got != src:
        missing = [s for s in src if s not in got]
        extra = [s for s in got if s not in src]
        return _fail(f"segment ids differ: missing={missing} extra={extra}")
    return _pass(f"{len(got)} segments, ids in order")


def segments_translated(output, context):
    """Every segment's text differs from its source (not passed through)."""
    fmt = context["vars"]["format"]
    parsed, error = parse_segments(output, fmt)
    if error:
        return _fail(error)
    src = {case["id"]: case["text"] for case in source_cases(context)}
    untouched = [
        sid
        for sid, text in parsed
        if text.strip() == src[sid].strip()
        # Slugs (e.g. "new-in-wagtail-7-4") are meant to be kept as-is, and
        # a lone word can legitimately be identical in the target language
        # (e.g. German "Test"). Both are exempt; unchanged prose still fails.
        and not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", src[sid].strip())
        and len(src[sid].split()) > 1
    ]
    if untouched:
        return _fail(f"{len(untouched)} segment(s) not translated: {untouched[:5]}")
    return _pass("all segments translated")


def tags_preserved_per_segment(output, context):
    """Per segment: same inline tag sequence and <a id> as the source."""
    fmt = context["vars"]["format"]
    parsed, error = parse_segments(output, fmt)
    if error:
        return _fail(error)
    src = {case["id"]: case["text"] for case in source_cases(context)}
    for sid, text in parsed:
        exp = [(t, a.get("id")) for t, a in parse_html(src[sid]).tags]
        got = [(t, a.get("id")) for t, a in parse_html(text).tags]
        if exp != got:
            return _fail(f"segment {sid}: tags differ {exp} -> {got}")
    return _pass("tag sequence and ids preserved in every segment")


def allowed_tags_only(output, context):
    fmt = context["vars"]["format"]
    parsed, error = parse_segments(output, fmt)
    if error:
        return _fail(error)
    disallowed = set()
    for _sid, text in parsed:
        disallowed |= {tag for tag, _attrs in parse_html(text).tags} - ALLOWED_TAGS
    if disallowed:
        return _fail(f"disallowed tags: {sorted(disallowed)}")
    return _pass("all segment tags within allowed set")


def attributes_clean(output, context):
    fmt = context["vars"]["format"]
    parsed, error = parse_segments(output, fmt)
    if error:
        return _fail(error)
    for sid, text in parsed:
        for tag, attrs in parse_html(text).tags:
            if tag == "a":
                extra = set(attrs) - {"id"}
                if extra:
                    return _fail(f"segment {sid}: <a> has attributes {sorted(extra)}")
            elif attrs:
                return _fail(f"segment {sid}: <{tag}> has attributes {attrs}")
    return _pass("no attributes beyond <a id>")


def glossary_compliant(output, context):
    """<b>/<i> labels use the official Wagtail admin translation, in place."""
    fmt = context["vars"]["format"]
    parsed, error = parse_segments(output, fmt)
    if error:
        return _fail(error)
    lang_code = context["vars"].get("lang_code", "")
    failures = []
    for sid, text in parsed:
        src_text = {c["id"]: c["text"] for c in source_cases(context)}[sid]
        expected = matched_glossary(src_text, lang_code)
        if not expected:
            continue
        src_bold = parse_html(src_text).bold_texts
        out_bold = parse_html(text).bold_texts
        if len(out_bold) != len(src_bold):
            failures.append(
                f"segment {sid}: <b>/<i> count differs {src_bold} -> {out_bold}"
            )
            continue
        for i, term in enumerate(src_bold):
            if term in expected and out_bold[i] != expected[term]:
                failures.append(
                    f"segment {sid}: label {term!r} should be "
                    f"{expected[term]!r}, got {out_bold[i]!r}"
                )
    if failures:
        return _fail("; ".join(failures[:3]))
    return _pass("official translations used where present")


def not_truncated(output, context):
    fmt = context["vars"]["format"]
    parsed, error = parse_segments(output, fmt)
    if error:
        return _fail(error)
    src = {case["id"]: case["text"] for case in source_cases(context)}
    short = [sid for sid, text in parsed if len(text.strip()) < 0.25 * len(src[sid])]
    if short:
        return _fail(f"suspiciously short segment(s): {short[:5]}")
    return _pass("no segment truncated")


def no_wrapper(output, context):
    """Output contains nothing besides the envelope (no commentary/fences)."""
    fmt = context["vars"]["format"]
    stripped = (output or "").strip()
    if not stripped:
        return _fail("empty output")
    if fmt == "xml":
        ok = re.match(r"<\s*document\b", stripped) and stripped.endswith("</document>")
        if not ok:
            first = stripped[:60]
            return _fail(f"output is not exactly the XML document: {first!r}...")
    elif fmt == "json-schema":
        unfenced = re.sub(r"^```(?:json)?\s*|\s*```$", "", stripped).strip()
        if not unfenced.startswith("{"):
            return _fail(
                f"output is not exactly the schema object: {stripped[:60]!r}..."
            )
    else:
        unfenced = re.sub(r"^```(?:json)?\s*|\s*```$", "", stripped).strip()
        if not unfenced.startswith("["):
            return _fail(f"output is not exactly the JSON array: {stripped[:60]!r}...")
    return _pass("envelope only, no wrapper")
