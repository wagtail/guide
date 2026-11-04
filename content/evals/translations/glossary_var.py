"""Promptfoo dynamic var: the glossary lines for a test's text + language.

Referenced from translations.yaml as `glossary: file://./glossary_var.py`.
The resolved value is used by the prompt function and the llm-rubric grader.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from glossary_util import matched_glossary

# Promptfoo rejects empty dynamic vars, so segments with no glossary terms get
# an explicit marker. translation_prompt.py skips the glossary section for it.
NO_GLOSSARY = "(none for this segment)"


def get_var(var_name, prompt, other_vars):
    matched = matched_glossary(
        other_vars.get("text", ""), other_vars.get("lang_code", "")
    )
    lines = "\n".join(
        f"- {source} = {translated}" for source, translated in matched.items()
    )
    return {"output": lines or NO_GLOSSARY}
