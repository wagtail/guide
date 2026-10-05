"""
Schema.org JSON-LD describing the guide, its publisher and the software it documents.

https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data
"""

from django.utils.text import Truncator
from manifest_loader.utils import manifest
from wagtail.rich_text import get_text_for_indexing

from apps.core.models import ContentPage, HomePage

ORGANIZATION_ID = "https://wagtail.org/#organization"
SOFTWARE_ID = "https://wagtail.org/#software"

ORGANIZATION = {
    "@type": "Organization",
    "@id": ORGANIZATION_ID,
    "name": "Wagtail",
    "url": "https://wagtail.org/",
    "sameAs": [
        "https://github.com/wagtail",
        "https://www.linkedin.com/company/wagtail-cms/",
        "https://bsky.app/profile/wagtail.org",
        "https://fosstodon.org/@wagtail",
        "https://www.youtube.com/channel/UCXsuEmvisPzuJPaIdpVM0yg",
    ],
}

# Not SoftwareApplication: Google treats that as a rich result candidate and reports
# an error when it has no rating or review.
SOFTWARE = {
    "@type": "SoftwareSourceCode",
    "@id": SOFTWARE_ID,
    "name": "Wagtail",
    "description": "Open source content management system built on Django.",
    "url": "https://wagtail.org/",
    "codeRepository": "https://github.com/wagtail/wagtail",
    "programmingLanguage": "Python",
    "license": "https://opensource.org/license/bsd-3-clause",
    "publisher": {"@id": ORGANIZATION_ID},
    "sameAs": [
        "https://github.com/wagtail/wagtail",
        "https://en.wikipedia.org/wiki/Wagtail_(software)",
        "https://www.wikidata.org/wiki/Q25206006",
    ],
}

# Not Site.site_name: Google takes the name shown in results from here, and the
# site name carries an emoji.
WEBSITE_NAME = "Wagtail user guide"
WEBSITE_DESCRIPTION = (
    "Official user guide for Wagtail CMS: how to create, edit, publish and manage "
    "content in the Wagtail admin."
)


def build_graph(site, page=None, request=None):
    root_url = site.root_url
    website_id = f"{root_url}/#website"

    graph = [
        {**ORGANIZATION, "logo": root_url + manifest("images/apple-touch-icon.png")},
        {
            "@type": "WebSite",
            "@id": website_id,
            "name": WEBSITE_NAME,
            "description": WEBSITE_DESCRIPTION,
            "url": f"{root_url}/",
            "publisher": {"@id": ORGANIZATION_ID},
        },
        SOFTWARE,
    ]

    if page is not None:
        graph.extend(page_nodes(page, website_id, request))

    return {"@context": "https://schema.org", "@graph": graph}


def page_nodes(page, website_id, request=None):
    is_article = isinstance(page, ContentPage)
    url = page.get_full_url(request)
    node = {
        "@type": "TechArticle" if is_article else "WebPage",
        "@id": f"{url}#webpage",
        "url": url,
        "headline": page.seo_title or page.title,
        "inLanguage": page.locale.language_code,
        "isPartOf": {"@id": website_id},
        "about": {"@id": SOFTWARE_ID},
        "publisher": {"@id": ORGANIZATION_ID},
    }
    if is_article:
        node["author"] = {"@id": ORGANIZATION_ID}
    if description := get_description(page):
        node["description"] = description
    if page.first_published_at:
        node["datePublished"] = page.first_published_at.isoformat()
    if page.last_published_at:
        node["dateModified"] = page.last_published_at.isoformat()

    if not is_article:
        return [node]

    # Skip the tree root; the trail starts at the locale's home page.
    trail = [*page.get_ancestors().filter(depth__gt=1).live(), page]
    breadcrumb = {
        "@type": "BreadcrumbList",
        "@id": f"{url}#breadcrumb",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": position,
                "name": crumb.title,
                "item": crumb.get_full_url(request),
            }
            for position, crumb in enumerate(trail, start=1)
        ],
    }
    node["breadcrumb"] = {"@id": breadcrumb["@id"]}
    return [node, breadcrumb]


def get_description(page):
    if page.search_description:
        return page.search_description
    if isinstance(page, HomePage) and page.introduction:
        text = get_text_for_indexing(page.introduction)
        return Truncator(text).chars(300)
    return ""
