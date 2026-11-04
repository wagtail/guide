from django.test import RequestFactory, SimpleTestCase

from apps.llms_txt.negotiation import prefers_markdown


class TestPrefersMarkdown(SimpleTestCase):
    def assertPrefersMarkdown(self, accept, expected):
        headers = {"accept": accept} if accept is not None else {}
        request = RequestFactory().get("/", headers=headers)
        self.assertIs(prefers_markdown(request), expected)

    def test_markdown(self):
        for accept in (
            "text/markdown",
            "text/markdown, text/html;q=0.9",
            # Client order breaks quality ties.
            "text/markdown, text/html",
        ):
            with self.subTest(accept=accept):
                self.assertPrefersMarkdown(accept, True)

    def test_html(self):
        for accept in (
            None,
            "*/*",
            "text/*",
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "text/html, text/markdown;q=0.5",
            "text/markdown;q=0, */*",
        ):
            with self.subTest(accept=accept):
                self.assertPrefersMarkdown(accept, False)
