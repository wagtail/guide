from django.utils.translation import get_language_info
from django.utils.translation import gettext_lazy as _
from wagtail_ai.agents.base import get_llm_service as _get_llm_service
from wagtail_localize.machine_translators.base import BaseMachineTranslator
from wagtail_localize.strings import StringValue


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

    def get_system_prompt(self, source_locale, target_locale):
        template = self.options.get("SYSTEM_PROMPT", self.default_system_prompt)
        return template.format(**self.get_prompt_context(source_locale, target_locale))

    def get_messages(self, source_locale, target_locale, string):
        return [
            {
                "role": "system",
                "content": self.get_system_prompt(source_locale, target_locale),
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
        results = {}
        for string in strings:
            messages = self.get_messages(source_locale, target_locale, string)
            response = llm_service.completion(
                messages=messages, temperature=self.temperature
            )
            content = (response.choices[0].message.content or "").strip()
            results[string] = self.translate_string(string, content)
        return results
