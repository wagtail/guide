"""Promptfoo prompt function for the batch (document-level) translation eval.

Mirrors LLMTranslator.get_messages in apps/core/translator.py, but sends all
segments of a page as ONE document (XML, JSON, or JSON-Schema envelope) in a
single LLM request. The envelope format is chosen per test via the `format`
var. Each envelope gets a worked few-shot example (source document ->
translated document) as a user/assistant message pair.

Keep the glossary prompt in sync with apps/core/translator.py.
"""

SYSTEM_PROMPT = (
    "You are a professional translator translating text from "
    "{source_language} to {target_language}.\n"
    "Translate only the text and keep its structure intact.\n"
    "- Only standard HTML inline tags are allowed: a, abbr, acronym, b, "
    "code, em, i, strong, br.\n"
    "- <a> tags may keep only their id attribute; other tags must have no "
    "attributes.\n"
    "- Preserve any inline tags, whitespace, and punctuation exactly."
)

GLOSSARY_PROMPT = (
    "\n- Text inside <b> or <i> tags is usually a label from the Wagtail "
    "admin interface. When a term appears in the glossary below, use the "
    "official translation exactly as given; otherwise translate it "
    "naturally and consistently.\n"
    "Glossary (official Wagtail admin translations):\n{glossary}"
)

FORMAT_INSTRUCTIONS = {
    "xml": (
        "The document is a list of segments wrapped in XML. Translate it as "
        "ONE document and reply with the same XML structure, with the same "
        "segment ids in the same order:\n"
        "<document>\n"
        '<segment id="s1">translated text</segment>\n'
        '<segment id="s2">translated text</segment>\n'
        "</document>\n"
        "Reply with the <document> XML and nothing else - no wrapper, "
        "explanation, or code fence of any kind. Translate every segment; "
        "never drop, merge, reorder, add, or repeat segments."
    ),
    "json": (
        'The document is a JSON array of {"id", "text"} objects. '
        "Translate it as ONE document and reply with ONLY a JSON array of "
        'the same objects with the same ids in the same order, each "text" '
        "replaced by its translation:\n"
        '[{"id": "s1", "text": "translated text"}, ...]\n'
        "Reply with the JSON array and nothing else - no wrapper, "
        "explanation, or code fence of any kind. Translate every segment; "
        "never drop, merge, reorder, add, or repeat segments."
    ),
    "json-schema": (
        'The document is a JSON array of {"id", "text"} objects. '
        "Translate it as ONE document, replying through the provided "
        'response format schema: an object {"segments": [{"id", '
        '"text"}, ...]} with the same ids in the same order, each '
        '"text" replaced by its translation. Translate every segment; '
        "never drop, merge, reorder, add, or repeat segments."
    ),
}

# Few-shot example per envelope: (source document, translated document).
# Generic English/French so it works for every target language; it
# demonstrates the mechanics: same ids, same order, tags preserved, slug
# segments kept as-is, escaped-HTML segments translated inside the escapes.
FEWSHOT = {
    "xml": (
        "<document>\n"
        '<segment id="s1">Getting started</segment>\n'
        '<segment id="s2">getting-started</segment>\n'
        '<segment id="s3">Click <b>Save</b> in the <a id="a1">edit screen</a> '
        "to keep your work.</segment>\n"
        "</document>",
        "<document>\n"
        '<segment id="s1">Premiers pas</segment>\n'
        '<segment id="s2">getting-started</segment>\n'
        '<segment id="s3">Cliquez sur <b>Enregistrer</b> dans l\''
        '<a id="a1">écran de modification</a> pour conserver votre '
        "travail.</segment>\n"
        "</document>",
    ),
    "json": (
        '[\n  {"id": "s1", "text": "Getting started"},\n'
        '  {"id": "s2", "text": "getting-started"},\n'
        '  {"id": "s3", "text": "Click <b>Save</b> in the <a id=\\"a1\\">edit '
        'screen</a> to keep your work."}\n]',
        '[\n  {"id": "s1", "text": "Premiers pas"},\n'
        '  {"id": "s2", "text": "getting-started"},\n'
        '  {"id": "s3", "text": "Cliquez sur <b>Enregistrer</b> dans l\''
        '<a id=\\"a1\\">écran de modification</a> pour conserver votre '
        'travail."}\n]',
    ),
    "json-schema": (
        '[\n  {"id": "s1", "text": "Getting started"},\n'
        '  {"id": "s2", "text": "getting-started"},\n'
        '  {"id": "s3", "text": "Click <b>Save</b> in the <a id=\\"a1\\">edit '
        'screen</a> to keep your work."}\n]',
        '{\n  "segments": [\n'
        '    {"id": "s1", "text": "Premiers pas"},\n'
        '    {"id": "s2", "text": "getting-started"},\n'
        '    {"id": "s3", "text": "Cliquez sur <b>Enregistrer</b> dans l\''
        '<a id=\\"a1\\">écran de modification</a> pour conserver votre '
        'travail."}\n  ]\n}',
    ),
}


def fewshot_messages(fmt):
    src, dst = FEWSHOT[fmt]
    return [
        {"role": "user", "content": src},
        {"role": "assistant", "content": dst},
    ]


def prompt(context):
    variables = context["vars"]
    fmt = variables["format"]
    system = SYSTEM_PROMPT.format(
        source_language=variables.get("source_language", "English"),
        target_language=variables["target_language"],
    )
    glossary = (variables.get("glossary") or "").strip()
    if glossary.startswith("(none"):
        glossary = ""
    if glossary:
        system += GLOSSARY_PROMPT.format(glossary=glossary)
    system += "\n" + FORMAT_INSTRUCTIONS[fmt]
    if fmt == "xml":
        user = variables["src_doc"]
    else:
        user = variables["doc"]
    return [
        {"role": "system", "content": system},
        *fewshot_messages(fmt),
        {"role": "user", "content": user},
    ]
