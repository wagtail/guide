import json
import tempfile
import unittest
from pathlib import Path

from trace_analysis import (
    curl_targets,
    extract_events,
    local_command,
    sanitized,
    status,
    techniques,
    urls,
)
from trace_review import CONTEXT, stage


class TestTraceAnalysis(unittest.TestCase):
    def test_shell_url_is_not_a_fetch_without_network_command(self):
        steps = [
            {
                "step_id": 1,
                "tool_calls": [
                    {
                        "tool_call_id": "a",
                        "function_name": "Bash",
                        "arguments": {
                            "command": "echo https://guide.wagtail.org/llms.txt"
                        },
                    },
                    {
                        "tool_call_id": "b",
                        "function_name": "Bash",
                        "arguments": {
                            "command": "curl https://guide.wagtail.org/llms.txt"
                        },
                    },
                ],
            }
        ]
        events = extract_events(steps, "trial")
        self.assertEqual(events[0]["urls"], [])
        self.assertEqual(events[1]["surfaces"], ["llms_txt"])
        self.assertEqual(events[1]["status"], "unobserved")

    def test_shell_headers_and_url_path_words_are_not_actions(self):
        targets, used = curl_targets(
            "curl -H 'Referer: https://example.com/' https://guide.wagtail.org/; echo https://other.example/"
        )
        self.assertTrue(used)
        self.assertEqual(targets, ["https://guide.wagtail.org/"])
        self.assertFalse(local_command("curl https://guide.wagtail.org/en/find-pages/"))
        self.assertFalse(local_command("echo 'ls; find'"))
        self.assertTrue(local_command("ls -la && grep -r Wagtail ."))
        self.assertEqual(
            curl_targets("curl https://guide.wagtail.org/\necho https://example.com/"),
            ([], True),
        )
        self.assertEqual(
            curl_targets(
                "curl --data-urlencode https://example.com/ https://guide.wagtail.org/"
            ),
            (["https://guide.wagtail.org/"], True),
        )
        self.assertEqual(
            curl_targets(
                "curl --unknown-option https://example.com/ https://guide.wagtail.org/"
            ),
            ([], True),
        )
        self.assertEqual(
            curl_targets(
                "curl https://guide.wagtail.org/; curl --unknown-option https://example.com/"
            ),
            ([], True),
        )

    def test_parallel_calls_do_not_establish_link_following(self):
        search = {
            "tool_call_id": "a",
            "function_name": "WebSearch",
            "arguments": {"query": "Wagtail guide"},
        }
        fetch = {
            "tool_call_id": "b",
            "function_name": "WebFetch",
            "arguments": {"url": "https://guide.wagtail.org/llms.txt"},
        }
        observation = {
            "results": [
                {
                    "source_call_id": "a",
                    "content": "See https://guide.wagtail.org/llms.txt",
                }
            ]
        }
        parallel = [
            {"step_id": 1, "tool_calls": [search, fetch], "observation": observation}
        ]
        self.assertFalse(
            techniques(extract_events(parallel, "t"), "")["visible_link_following"]
        )
        parallel_flags = techniques(extract_events(parallel, "t"), "")
        self.assertFalse(parallel_flags["search_first"])
        self.assertTrue(parallel_flags["mixed_first_navigation"])
        sequential = [
            {"step_id": 1, "tool_calls": [search], "observation": observation},
            {"step_id": 2, "tool_calls": [fetch]},
        ]
        events = extract_events(sequential, "t")
        self.assertTrue(techniques(events, "")["search_result_following"])
        self.assertEqual(events[1]["url_provenance"][0]["source_event"], "t:s1:0")
        self.assertEqual(events[1]["url_provenance"][0]["match"], "exact_sanitized_url")

    def test_opaque_requests_are_not_promoted_to_executed_fetches(self):
        steps = [
            {
                "step_id": 2,
                "tool_calls": [
                    {
                        "tool_call_id": "a",
                        "function_name": "exec",
                        "arguments": {
                            "input": 'await tools.web__run({search_query: [{q: "Wagtail"}], open: [{ref_id: "https://guide.wagtail.org/"}]})'
                        },
                    }
                ],
                "observation": {
                    "results": [
                        {"source_call_id": "a", "content": "code-mode host is disabled"}
                    ]
                },
            }
        ]
        event = extract_events(steps, "t")[0]
        self.assertTrue(event["script_search_request"])
        self.assertTrue(event["script_fetch_request"])
        self.assertEqual(event["urls"], [])
        self.assertEqual(event["status"], "error_text")
        self.assertEqual(event["output_urls"], [])

    def test_structured_errors_and_missing_observations(self):
        self.assertEqual(status({"content": '{"success":false}'}), "failed")
        self.assertEqual(
            status({"content": '{"status":"completed","decision":"deny"}'}), "denied"
        )
        self.assertEqual(
            status({"content": "A page about permission denied errors"}), "returned"
        )
        self.assertEqual(status(None), "unobserved")
        self.assertEqual(status(None, "error"), "failed")
        self.assertEqual(
            status({"content": "data", "extra": {"tool_result_is_error": True}}),
            "failed",
        )

    def test_url_metadata_decoding_and_secret_query_removal(self):
        self.assertEqual(
            urls(
                '{"success":{"content":"See https://guide.wagtail.org/llms.txt\\nNext"}}'
            ),
            ["https://guide.wagtail.org/llms.txt"],
        )
        self.assertEqual(
            urls("https://user:secret@guide.wagtail.org/en/?token=secret#anchor"),
            ["https://guide.wagtail.org/en/"],
        )

    def test_staging_is_whitelisted_and_sanitizes_string_leaves(self):
        secret = {
            "command": "Authorization: Bearer secretvalue",
            "url": "https://user:password@example.com/?token=secret",
            "count": 2,
        }
        safe = sanitized(secret)
        self.assertNotIn("secretvalue", json.dumps(safe))
        self.assertEqual(safe["url"], "https://example.com/")
        self.assertEqual(safe["count"], 2)
        record = dict.fromkeys(CONTEXT)
        record.update(
            id="a",
            prompt="Bearer secretvalue",
            trial_path="/private/native",
            raw_credentials="secretvalue",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "stage"
            stage(root, [record], [], population=50)
            self.assertEqual(
                {p.name for p in (root / "a").iterdir()},
                {"context.json", "events.jsonl", "trial.log"},
            )
            self.assertNotIn("secretvalue", (root / "a/context.json").read_text())
            self.assertNotIn("/private/native", (root / "a/context.json").read_text())
            self.assertNotEqual(
                json.loads((root / "selection.json").read_text())["selection"],
                "All attempts",
            )


if __name__ == "__main__":
    unittest.main()
