import hashlib

from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views.decorators.cache import cache_control
from wagtail.contrib.sitemaps import Sitemap

SKILL_NAME = "wagtail-guide-support"
SKILL_DESCRIPTION = (
    "A professional support helper for Wagtail CMS users. "
    "Use when answering Wagtail CMS user questions "
    "with the Wagtail Guide as authoritative documentation."
)
SCHEMA_URI = "https://schemas.agentskills.io/discovery/0.2.0/schema.json"


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
    pages = Sitemap(request).items()
    template = loader.get_template("llms_txt/llms.txt.jinja")
    context = {"pages": pages}
    content = template.render(context, request)
    response = HttpResponse(content, content_type="text/markdown;charset=utf-8")
    return response


@cache_control(max_age=3600)
def llms_full_txt_view(request):
    pages = Sitemap(request).items()
    template = loader.get_template("llms_txt/llms-full.txt.jinja")
    context = {"pages": pages}
    content = template.render(context, request)
    response = HttpResponse(content, content_type="text/markdown;charset=utf-8")
    return response
