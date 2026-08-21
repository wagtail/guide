from bs4 import BeautifulSoup
from django.template import Context, Template
from django_ai_core.contrib.index import VectorIndex, registry
from django_ai_core.contrib.index.chunking import ParagraphChunkTransformer
from django_ai_core.contrib.index.embedding import CoreEmbeddingTransformer
from django_ai_core.contrib.index.source import ModelSource
from django_ai_core.contrib.index.storage.pgvector import PgVectorProvider
from wagtail_ai.agents.base import get_llm_service

from apps.core.models.content import ContentPage


def render_body_text(obj) -> str:
    """Render a page's StreamField body to plain text (HTML tags stripped)."""
    template = Template("{% load wagtailcore_tags %}{% include_block body %}")
    html = template.render(Context({"body": obj.body}))
    return BeautifulSoup(html, "lxml").get_text()


def render_first_paragraph(obj) -> str:
    """
    Render the first substantive text block of a page's StreamField body,
    skipping non-text blocks such as "alert" callouts, which tend to
    restate the search description rather than add distinct content.
    """
    for block in obj.body:
        if block.block_type == "text":
            html = str(block.value)
        elif block.block_type == "text_annotated":
            html = str(block.value["content"])
        else:
            continue
        text = BeautifulSoup(html, "lxml").get_text().strip()
        if text:
            return text
    return ""


class PageSource(ModelSource):
    """ModelSource that renders StreamField body to plain text for embeddings."""

    def __init__(self, queryset=None, **kwargs):
        super().__init__(queryset=queryset, **kwargs)
        self.chunk_transformer = ParagraphChunkTransformer(
            min_chunk_size=100,
            max_chunk_size=1500,
        )

    def get_content(self, obj):
        text = render_body_text(obj)
        parts = [obj.title]
        if obj.search_description:
            parts.append(obj.search_description)
        if obj.seo_title and obj.seo_title != obj.title:
            parts.append(obj.seo_title)
        parts.append(text)
        return "\n\n".join(parts)

    def get_metadata(self, obj):
        metadata = super().get_metadata(obj)
        if obj.locale:
            metadata["locale"] = obj.locale.language_code
        return metadata


@registry.register()
class PageIndex(VectorIndex):
    storage_provider = PgVectorProvider()

    def __init__(self):
        self.sources = [
            PageSource(
                queryset=ContentPage.objects.live().public(),
            )
        ]
        self.embedding_transformer = CoreEmbeddingTransformer(
            get_llm_service("embedding")
        )
        super().__init__()

    def search_sources(self, query, *, locale=None, **kwargs):
        qs = super().search_sources(query, **kwargs)
        if locale:
            qs = qs.filter(locale=locale)
        return qs
