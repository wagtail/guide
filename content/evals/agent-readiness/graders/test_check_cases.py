"""Regression checks for grading changes; no candidates or judges are called."""

import unittest

import yaml
from check_cases import TESTS, TEXT_CHECKS, check, passes_all


class TestCaseGrading(unittest.TestCase):
    def checks(self, name):
        case = next(
            c for c in yaml.safe_load(TESTS.read_text()) if c["description"] == name
        )
        return [a for a in case["assert"] if a["type"] in TEXT_CHECKS]

    def test_multi_tenancy_table_is_not_rejected_for_phrase_order(self):
        answer = """| Property | Multi-site | Multi-tenancy |
| --- | --- | --- |
| Database | Shared | Separate per tenant |
| Media and users | Shared | Isolated |
| Support | Out of the box | Requires customizations |
https://guide.wagtail.org/en/reference/multi-site/
"""
        self.assertTrue(
            passes_all(self.checks("info-multi-site-vs-multi-tenancy"), answer)
        )

    def test_supplied_release_version_and_citation_are_not_enough(self):
        self.assertFalse(
            passes_all(
                self.checks("start-release-8-0"),
                "Wagtail 8.0. https://guide.wagtail.org/en/releases/new-in-wagtail-8-0/",
            )
        )

    def test_references_and_negative_controls(self):
        self.assertEqual(check(), [])
