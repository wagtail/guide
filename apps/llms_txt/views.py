import hashlib

from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views.decorators.cache import cache_control
from wagtail.contrib.sitemaps import Sitemap
from wagtail.models import Site

SKILL_NAME = "wagtail-guide-support"
SKILL_DESCRIPTION = (
    "A professional support helper for Wagtail CMS users. "
    "Use when answering Wagtail CMS user questions "
    "with the Wagtail Guide as authoritative documentation."
)
SCHEMA_URI = "https://schemas.agentskills.io/discovery/0.2.0/schema.json"

RESPONSE_CONTENT_TYPE = "text/markdown;charset=utf-8"
LLMS_TXT_TEMPLATE = "llms_txt/llms.txt.jinja"
LLMS_FULL_TXT_TEMPLATE = "llms_txt/llms-full.txt.jinja"

# Rendered llms.txt files are expensive to generate: they render the markdown
# for every page of the site within a single request. Their output only
# changes when pages are published, unpublished, moved, or deleted, so the
# rendered content is cached server-side (Redis in production), and
# invalidated via signals in apps.llms_txt.signals. The timeout is only a
# safety net for missed invalidations, complementing the browser / CDN caching
# of the @cache_control decorators below.
CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours.


def get_cache_key(site_pk, template_name):
    return f"llms_txt:{site_pk}:{template_name}"


def invalidate_cache():
    """Drop cached llms.txt content for all sites."""
    site_pks = Site.objects.values_list("pk", flat=True)
    for site_pk in site_pks:
        for template_name in (LLMS_TXT_TEMPLATE, LLMS_FULL_TXT_TEMPLATE):
            cache.delete(get_cache_key(site_pk, template_name))


def _render_llms_txt(request, template_name):
    sitemap = Sitemap(request)
    # Same site resolution as Sitemap.items(), so the cache key is in sync
    # with the pages being rendered.
    site = sitemap.get_wagtail_site()
    key = get_cache_key(site.pk, template_name)
    content = cache.get(key)
    if content is None:
        context = {"pages": sitemap.items()}
        content = loader.get_template(template_name).render(context, request)
        cache.set(key, content, timeout=CACHE_TIMEOUT)
    return HttpResponse(content, content_type=RESPONSE_CONTENT_TYPE)


def _render_skill_md(request):
    template = loader.get_template("llms_txt/skill.md.jinja")
    context = {"skill_name": SKILL_NAME, "skill_description": SKILL_DESCRIPTION}
    return template.render(context, request)


def _skill_digest(content):
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


@cache_control(max_age=3600)
def agent_skill_view(request):
    content = _render_skill_md(request)
    return HttpResponse(content, content_type="text/markdown;charset=utf-8")


@cache_control(max_age=3600)
def agent_skills_index_view(request):
    skill_content = _render_skill_md(request)
    skill_url = f"/.well-known/agent-skills/{SKILL_NAME}/SKILL.md"
    data = {
        "$schema": SCHEMA_URI,
        "skills": [
            {
                "name": SKILL_NAME,
                "type": "skill-md",
                "description": SKILL_DESCRIPTION,
                "url": skill_url,
                "digest": _skill_digest(skill_content),
            }
        ],
    }
    return JsonResponse(data, json_dumps_params={"indent": 2})


@cache_control(max_age=3600)
def llms_txt_view(request):
    return _render_llms_txt(request, LLMS_TXT_TEMPLATE)


@cache_control(max_age=3600)
def llms_full_txt_view(request):
    return _render_llms_txt(request, LLMS_FULL_TXT_TEMPLATE)
