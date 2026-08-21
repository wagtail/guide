import re
from html import unescape

from django.utils.translation import get_language_info, trans_real
from django.utils.translation import gettext_lazy as _
from wagtail_ai.agents.base import get_llm_service as _get_llm_service
from wagtail_localize.machine_translators.base import BaseMachineTranslator
from wagtail_localize.strings import StringValue

# Text inside <b>/<i> tags — most often a Wagtail admin UI label.
UI_LABEL_RE = re.compile(r"<(b|i)\b[^>]*>(.*?)</\1>", re.IGNORECASE | re.DOTALL)


class LLMTranslator(BaseMachineTranslator):
    display_name = _("LLM Translator")

    provider_alias = "translator"
    temperature = 0
    default_system_prompt = (
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
    default_glossary_prompt = (
        "\n- Text inside <b> or <i> tags is usually a label from the Wagtail "
        "admin interface. When a term appears in the glossary below, use the "
        "official translation exactly as given; otherwise translate it "
        "naturally and consistently.\n"
        "Glossary (official Wagtail admin translations):\n{glossary}"
    )

    def __init__(self, options):
        super().__init__(options)
        self.provider_alias = self.options.get("provider", self.provider_alias)
        self.temperature = self.options.get("temperature", self.temperature)

    def can_translate(self, source_locale, target_locale):
        return source_locale.language_code != target_locale.language_code

    def get_prompt_context(self, source_locale, target_locale):
        return {
            "source_language": get_language_info(source_locale.language_code)["name"],
            "target_language": get_language_info(target_locale.language_code)["name"],
        }

    def get_ui_terms(self, strings):
        """Unique <b>/<i> label texts across the strings, in order."""
        terms = []
        for string in strings:
            for _tag, text in UI_LABEL_RE.findall(string.get_translatable_html()):
                term = unescape(re.sub(r"<[^>]+>", "", text)).strip()
                if term and term not in terms:
                    terms.append(term)
        return terms

    def get_glossary(self, target_locale, terms):
        """Map each term to its official admin translation, where one exists.

        Looks the terms up in Django's merged translation catalog for the
        target language, which includes Wagtail's own admin translations.
        """
        catalog = trans_real.translation(target_locale.language_code)._catalog
        glossary = {}
        for term in terms:
            translated = catalog.get(term)
            if isinstance(translated, str) and translated.strip():
                glossary[term] = translated
        return glossary

    def get_system_prompt(self, source_locale, target_locale, glossary=None):
        template = self.options.get("SYSTEM_PROMPT", self.default_system_prompt)
        prompt = template.format(
            **self.get_prompt_context(source_locale, target_locale)
        )
        if glossary:
            glossary_template = self.options.get(
                "GLOSSARY_PROMPT", self.default_glossary_prompt
            )
            lines = "\n".join(
                f"- {source} = {translated}" for source, translated in glossary.items()
            )
            prompt += glossary_template.format(glossary=lines)
        return prompt

    def get_messages(self, source_locale, target_locale, string, glossary=None):
        return [
            {
                "role": "system",
                "content": self.get_system_prompt(
                    source_locale, target_locale, glossary=glossary
                ),
            },
            {
                "role": "user",
                "content": string.get_translatable_html(),
            },
        ]

    def translate_string(self, string, content):
        return StringValue.from_translated_html(content)

    def get_llm_service(self, alias):
        return _get_llm_service(alias)

    def translate(self, source_locale, target_locale, strings):
        llm_service = self.get_llm_service(self.provider_alias)
        glossary = self.get_glossary(target_locale, self.get_ui_terms(strings))
        results = {}
        for string in strings:
            messages = self.get_messages(
                source_locale, target_locale, string, glossary=glossary
            )
            response = llm_service.completion(
                messages=messages, temperature=self.temperature
            )
            content = (response.choices[0].message.content or "").strip()
            results[string] = self.translate_string(string, content)
        return results
