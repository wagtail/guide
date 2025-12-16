from jinja2.ext import Extension

from apps.llms_txt.rich_text import richtext_markdown


class LLMsTxtExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)

        self.environment.filters.update(
            {
                "richtext_markdown": richtext_markdown,
            }
        )


llms_txt = LLMsTxtExtension
