"""Promptfoo prompt function for the LLM translator eval.

Builds the same messages as LLMTranslator.get_messages in
apps/core/translator.py: the translator system prompt, plus a glossary section
when the segment contains UI labels with official Wagtail admin translations.
Keep the prompt strings in sync with apps/core/translator.py.
"""

# Keep in sync with LLMTranslator.default_system_prompt.
SYSTEM_PROMPT = (
    "You are a professional translator translating text from "
    "{source_language} to {target_language}.\n"
    "Translate only the text and keep its structure intact.\n"
    "Reply with just the translated text and no wrapper, explanation, or "
    "code fence of any kind.\n"
    "- Only standard HTML inline tags are allowed: a, abbr, acronym, b, "
    "code, em, i, strong, br.\n"
    "- <a> tags may keep only their id attribute; other tags must have no "
    "attributes.\n"
    "- Preserve any inline tags, whitespace, and punctuation exactly."
)

# Keep in sync with LLMTranslator.default_glossary_prompt.
GLOSSARY_PROMPT = (
    "\n- Text inside <b> or <i> tags is usually a label from the Wagtail "
    "admin interface. When a term appears in the glossary below, use the "
    "official translation exactly as given; otherwise translate it "
    "naturally and consistently.\n"
    "Glossary (official Wagtail admin translations):\n{glossary}"
)


def prompt(context):
    variables = context["vars"]
    system = SYSTEM_PROMPT.format(
        source_language=variables.get("source_language", "English"),
        target_language=variables["target_language"],
    )
    glossary = (variables.get("glossary") or "").strip()
    if glossary.startswith("(none"):
        glossary = ""
    if glossary:
        system += GLOSSARY_PROMPT.format(glossary=glossary)
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": variables["text"]},
    ]
