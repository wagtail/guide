"""Promptfoo dynamic var: the glossary lines for a batch test's document.

Like prompts/evals/translations/glossary_var.py, but collects UI label terms
across ALL segments of the document (vars.doc, a JSON string of
{"id", "text"} cases), since the batch eval translates whole pages.

Referenced from translations-batch.yaml as `glossary: file://./glossary_var.py`.
The resolved value is used by the prompt function and the llm-rubric grader.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent

sys.path.insert(0, str(HERE / ".." / "translations"))

from glossary_util import matched_glossary

# Promptfoo rejects empty dynamic vars, so documents with no glossary terms
# get an explicit marker. translation_prompt.py skips the section for it.
NO_GLOSSARY = "(none for this document)"


def get_var(var_name, prompt, other_vars):
    doc = json.loads(other_vars.get("doc", "[]"))
    text = "\n".join(case["text"] for case in doc)
    matched = matched_glossary(text, other_vars.get("lang_code", ""))
    # Keep first-seen order, as in LLMTranslator.get_ui_terms.
    lines = "\n".join(f"- {src} = {dst}" for src, dst in matched.items())
    return {"output": lines or NO_GLOSSARY}
