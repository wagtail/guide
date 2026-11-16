import unittest

from trace_retrieval import measure


class TestRetrievalEvidence(unittest.TestCase):
    def setUp(self):
        self.url = "https://guide.wagtail.org/en/test/"
        self.record = {
            **dict.fromkeys(("id", "phase", "harness", "model", "arm", "case"), "test"),
            "passed": True,
            "trace_present": True,
            "answer_present": True,
            "native_calls_without_atif": 0,
            "reference_urls": [self.url],
            "answer_urls": [self.url],
            "prompt": "Find the answer.",
        }

    def event(self, step, kind="fetch", status="returned", **extra):
        return {
            "id": f"s{step}",
            "step": step,
            "kind": kind,
            "tool": kind,
            "status": status,
            "urls": [self.url] if kind == "fetch" else [],
            "query": "test" if kind == "search" else "",
            "output_urls": [],
            "curl_request": False,
            **extra,
        }

    def test_failed_fetch_then_recovery_and_repeat(self):
        row, links = measure(
            self.record,
            [self.event(1, status="failed"), self.event(2), self.event(3)],
        )
        self.assertEqual(row["failed_retrieval_calls"], 1)
        self.assertEqual(row["repeated_target_calls"], 2)
        self.assertEqual(row["repeat_after_return_calls"], 1)
        self.assertEqual(row["calls_before_reference_return"], 1)
        self.assertEqual(links[0]["provenance"], "returned")
        self.assertEqual(links[0]["semantic_support"], "not_assessed")

    def test_same_step_search_does_not_prove_link_following(self):
        row, _ = measure(
            self.record,
            [self.event(1, "search", output_urls=[self.url]), self.event(1)],
        )
        self.assertEqual(row["search_pages_requested_later"], 0)
        row, _ = measure(
            self.record,
            [self.event(1, "search", output_urls=[self.url]), self.event(2)],
        )
        self.assertEqual(row["search_pages_requested_later"], 1)

    def test_missing_answers_and_trajectories_are_unknown(self):
        row, _ = measure({**self.record, "answer_present": False}, [self.event(1)])
        self.assertIsNone(row["citations_returned"])
        self.assertIsNone(row["returned_pages_not_cited"])
        row, _ = measure({**self.record, "trace_present": False}, [])
        self.assertIsNone(row["retrieval_calls"])
        row, _ = measure(self.record, [])
        self.assertEqual(row["retrieval_calls"], 0)
        self.assertEqual(row["citations_not_observed"], 1)
        self.assertIsNone(row["calls_before_reference_return"])

    def test_search_snippet_is_not_fetched_page_or_semantic_support(self):
        row, links = measure(
            self.record, [self.event(1, "search", output_urls=[self.url])]
        )
        self.assertEqual(row["citations_search_only"], 1)
        self.assertEqual(row["citations_returned"], 0)
        self.assertEqual(links[0]["semantic_support"], "not_assessed")

    def test_versions_are_not_assumed_equivalent(self):
        row, _ = measure(
            self.record,
            [self.event(1, urls=[self.url.replace("/en/", "/en-latest/")])],
        )
        self.assertEqual(row["citations_not_observed"], 1)
        self.assertEqual(row["returned_pages_not_cited"], 1)
        self.assertIsNone(row["calls_before_reference_return"])


if __name__ == "__main__":
    unittest.main()
