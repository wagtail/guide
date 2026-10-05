import json
from http import HTTPStatus

from bs4 import BeautifulSoup
from django.test import TestCase

from apps.core.factories import ContentPageFactory, HomePageFactory, LocaleFactory


def get_graph(response):
    soup = BeautifulSoup(response.content, "lxml")
    scripts = soup.find_all("script", type="application/ld+json")
    assert len(scripts) == 1, f"Expected one JSON-LD script, found {len(scripts)}"
    data = json.loads(scripts[0].string)
    assert data["@context"] == "https://schema.org"
    return {node["@id"].rsplit("#", 1)[-1]: node for node in data["@graph"]}


class TestStructuredData(TestCase):
    def setUp(self):
        self.home = HomePageFactory()
        self.section = ContentPageFactory(
            parent=self.home, title="How-to guides", slug="how-to-guides"
        )
        self.page = ContentPageFactory(
            parent=self.section,
            title="Manage snippets",
            slug="manage-snippets",
            search_description="Create and edit snippets.",
        )
        for page in (self.home, self.section, self.page):
            page.save_revision().publish()

    def test_homepage_identity(self):
        graph = get_graph(self.client.get(self.home.url))

        organization = graph["organization"]
        self.assertEqual(organization["@type"], "Organization")
        self.assertEqual(organization["name"], "Wagtail")
        self.assertEqual(organization["url"], "https://wagtail.org/")
        self.assertIn("https://github.com/wagtail", organization["sameAs"])
        self.assertIn(
            "https://www.linkedin.com/company/wagtail-cms/", organization["sameAs"]
        )
        self.assertTrue(organization["logo"].startswith("http"))

        website = graph["website"]
        self.assertEqual(website["@type"], "WebSite")
        self.assertTrue(website["description"])
        self.assertEqual(website["publisher"], {"@id": organization["@id"]})

        software = graph["software"]
        self.assertEqual(software["@type"], "SoftwareSourceCode")
        self.assertIn("https://www.wikidata.org/wiki/Q25206006", software["sameAs"])
        self.assertNotIn("offers", software)
        self.assertEqual(
            software["license"], "https://opensource.org/license/bsd-3-clause"
        )

        webpage = graph["webpage"]
        self.assertEqual(webpage["@type"], "WebPage")
        self.assertEqual(webpage["url"], self.home.full_url)
        self.assertEqual(webpage["isPartOf"], {"@id": website["@id"]})
        self.assertEqual(webpage["about"], {"@id": software["@id"]})
        self.assertNotIn("breadcrumb", webpage)
        self.assertNotIn("author", webpage)

    def test_homepage_description_falls_back_to_introduction(self):
        self.home.introduction = "<p>Learn to <b>use</b> Wagtail &amp; more.</p>"
        self.home.save_revision().publish()

        graph = get_graph(self.client.get(self.home.url))
        self.assertEqual(
            graph["webpage"]["description"], "Learn to use Wagtail & more."
        )

        self.home.search_description = "The Wagtail user guide."
        self.home.save_revision().publish()

        graph = get_graph(self.client.get(self.home.url))
        self.assertEqual(graph["webpage"]["description"], "The Wagtail user guide.")

    def test_content_page_is_tech_article_with_breadcrumbs(self):
        graph = get_graph(self.client.get(self.page.url))

        article = graph["webpage"]
        self.assertEqual(article["@type"], "TechArticle")
        self.assertEqual(article["headline"], "Manage snippets")
        self.assertEqual(article["description"], "Create and edit snippets.")
        self.assertEqual(article["url"], self.page.full_url)
        self.assertEqual(article["inLanguage"], "en")
        self.assertEqual(article["publisher"], {"@id": graph["organization"]["@id"]})
        self.assertEqual(article["author"], {"@id": graph["organization"]["@id"]})
        self.assertIn("datePublished", article)
        self.assertIn("dateModified", article)

        breadcrumb = graph["breadcrumb"]
        self.assertEqual(article["breadcrumb"], {"@id": breadcrumb["@id"]})
        self.assertEqual(
            [
                (item["position"], item["name"], item["item"])
                for item in breadcrumb["itemListElement"]
            ],
            [
                (1, self.home.title, self.home.full_url),
                (2, "How-to guides", self.section.full_url),
                (3, "Manage snippets", self.page.full_url),
            ],
        )

    def test_breadcrumbs_skip_unpublished_ancestors(self):
        self.section.unpublish()

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            [
                (item["position"], item["name"])
                for item in get_graph(response)["breadcrumb"]["itemListElement"]
            ],
            [(1, self.home.title), (2, "Manage snippets")],
        )

    def test_translated_page_language(self):
        de = LocaleFactory(language_code="de")
        page_de = self.page.copy_for_translation(de, copy_parents=True)
        page_de.save_revision().publish()

        graph = get_graph(self.client.get(page_de.url))
        self.assertEqual(graph["webpage"]["inLanguage"], "de")
        self.assertEqual(graph["webpage"]["url"], page_de.full_url)

    def test_title_cannot_break_out_of_script(self):
        self.page.title = "</script><script>alert(1)</script>"
        self.page.save_revision().publish()

        response = self.client.get(self.page.url)
        self.assertNotContains(response, "</script><script>alert(1)")
        graph = get_graph(response)
        self.assertEqual(graph["webpage"]["headline"], self.page.title)

    def test_not_found_page_has_site_identity_only(self):
        response = self.client.get("/en/does-not-exist/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        graph = get_graph(response)
        self.assertEqual(set(graph), {"organization", "website", "software"})
