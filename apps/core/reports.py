from django.conf import settings
from django.forms import Media
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from wagtail.admin.views.reports import PageReportView
from wagtail.permissions import page_permission_policy

from apps.core.models import ContentPage


def iter_annotated_blocks(page):
    """Yield (index, StreamChild) for each text_annotated block in the page's body."""
    for block_index, block in enumerate(page.body):
        if block.block_type == "text_annotated":
            yield block_index, block


def _truncate(text, max_length):
    if len(text) > max_length:
        return text[:max_length] + "…"
    return text


def _parse_version(version):
    if not version:
        return None
    try:
        return tuple(int(part) for part in version.split("."))
    except ValueError:
        return None


def _build_block_detail(block_index, block, current_version):
    value = block.value
    change_type = value.get("change_type")
    version = value.get("version")
    content = value.get("content")

    current = _parse_version(current_version)
    parsed_version = _parse_version(version)
    outdated = bool(current and parsed_version and parsed_version < current)

    return {
        "block_index": block_index,
        "version": version,
        "change_type": change_type,
        "content_preview": _truncate(strip_tags(str(content)).strip(), 100),
        "outdated": outdated,
    }


class BlockUsageReportView(PageReportView):
    page_title = _("Annotated blocks usage")
    header_icon = "doc-empty-inverse"
    results_template_name = "core/admin/reports/block_usage_results.html"
    index_url_name = "block_usage_report"
    index_results_url_name = "block_usage_report_results"
    any_permission_required = ["add", "change", "publish"]

    #: Loaded once via `{{ media.css }}` / `{{ media.js }}` in the listing
    #: template (rendered on full page load, not re-included on every
    #: AJAX filter/pagination refresh of the results fragment).
    media = Media(
        css={"all": ["core/css/block_usage_report.css"]},
        js=["core/js/block_usage_report.js"],
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_version = getattr(settings, "WAGTAIL_GUIDE_CURRENT_VERSION", None)

    def get_queryset(self):
        permitted_pages = page_permission_policy.instances_user_has_permission_for(
            self.request.user, "change"
        ).exact_type(ContentPage)

        pages = []
        for page in permitted_pages.specific():
            block_details = [
                _build_block_detail(block_index, block, self.current_version)
                for block_index, block in iter_annotated_blocks(page)
            ]
            if not block_details:
                continue

            page.block_usage_blocks = block_details
            page.block_usage_flagged_count = sum(
                1 for b in block_details if b["outdated"]
            )
            page.block_usage_flagged = page.block_usage_flagged_count > 0
            page.block_usage_min_version = min(
                (b["version"] for b in block_details if b["version"]), default=""
            )
            pages.append(page)

        pages.sort(
            key=lambda p: (
                not p.block_usage_flagged,
                not p.live,
                p.block_usage_min_version or "",
            )
        )
        return pages

    def decorate_paginated_queryset(self, object_list):
        # The per-page block breakdown is already attached in get_queryset,
        # but export relies on the decorated object_list too, so keep it as-is.
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_version"] = self.current_version
        context["media"] += self.media
        return context
