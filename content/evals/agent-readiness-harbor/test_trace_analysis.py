import json
import tempfile
import unittest
from pathlib import Path

from trace_analysis import (
    controls,
    curl_targets,
    extract_events,
    feature_changes,
    local_command,
    sanitized,
    status,
    techniques,
    urls,
)
from trace_report import statistics_exports
from trace_review import CONTEXT, stage


class TestTraceAnalysis(unittest.TestCase):
    def test_retry_changes_require_evidence_for_each_measure(self):
        original = {"trace_present": True, "answer_present": False, "techniques": {}}
        retry = {
            "trace_present": True,
            "answer_present": True,
            "techniques": {
                "search_requested": True,
                "answer_cites_en_latest": True,
            },
        }
        features = ["search_requested", "answer_cites_en_latest"]
        self.assertEqual(
            feature_changes(original, retry, features), (["search_requested"], [])
        )
        original["trace_present"] = False
        self.assertEqual(feature_changes(original, retry, features), (None, None))

    def test_statistics_distinguish_missing_zero_and_answer_denominators(self):
        base = {
            "phase": "test",
            "harness": "test",
            "model": "test",
            "agent_version": "1",
            "arm": "native",
            "case": "question",
            "framing": "site-named",
            "passed": False,
            "execution_error": None,
            "native_tool_call_count": None,
            "native_calls_without_atif": 0,
            "agent_seconds": None,
        }
        records = [
            dict(
                base,
                id="zero",
                trace_present=True,
                answer_present=True,
                event_count=0,
                recorded_tool_call_count=0,
                techniques={"search_requested": False, "answer_cites_en_latest": True},
            ),
            dict(
                base,
                id="ten",
                trace_present=True,
                answer_present=False,
                event_count=10,
                recorded_tool_call_count=10,
                techniques={"search_requested": True},
            ),
            dict(
                base,
                id="missing",
                trace_present=False,
                answer_present=False,
                event_count=0,
                recorded_tool_call_count=None,
                techniques={},
            ),
        ]
        with tempfile.TemporaryDirectory() as directory:
            patterns, tools = statistics_exports(Path(directory), records)
        search = next(
            r
            for r in patterns
            if r["scope"] == "all-recorded" and r["pattern"] == "search_requested"
        )
        self.assertEqual(
            (
                search["present"],
                search["eligible"],
                search["unknown"],
                search["observed_rate"],
            ),
            (1, 2, 1, 0.5),
        )
        answer = next(
            r
            for r in patterns
            if r["scope"] == "all-recorded" and r["pattern"] == "answer_cites_en_latest"
        )
        self.assertEqual(
            (answer["present"], answer["eligible"], answer["unknown"]), (1, 1, 2)
        )
        calls = next(r for r in tools if r["scope"] == "all-recorded")
        self.assertEqual(
            (
                calls["count_coverage"],
                calls["zero_call_traces"],
                calls["median_calls"],
                calls["p90_calls"],
            ),
            (2, 1, 5, 10),
        )

    def test_native_error_evidence_is_retained_and_redacted(self):
        events = extract_events(
            [
                {
                    "step_id": 1,
                    "tool_calls": [
                        {
                            "tool_call_id": "failed",
                            "function_name": "webfetch",
                            "arguments": {"url": "https://guide.wagtail.org/missing/"},
                        }
                    ],
                }
            ],
            "trial",
            {"failed": {"status": "error", "error": "HTTP 404 Bearer secret-value"}},
        )
        self.assertEqual(events[0]["status"], "failed")
        self.assertNotIn("secret-value", events[0]["error_signal"])
        self.assertIn("HTTP 404", events[0]["error_signal"])

    def test_tavily_search_is_recognized_without_relabeling_raw_call(self):
        events = extract_events(
            [
                {
                    "step_id": 1,
                    "tool_calls": [
                        {
                            "tool_call_id": "tavily",
                            "function_name": "tavily_tavily_search",
                            "arguments": {"query": "Wagtail scheduling"},
                        }
                    ],
                    "observation": {
                        "results": [
                            {"source_call_id": "tavily", "content": "Search results"}
                        ]
                    },
                }
            ],
            "trial",
            {"tavily": "completed"},
        )
        self.assertEqual(events[0]["tool"], "tavily_tavily_search")
        self.assertEqual(events[0]["kind"], "mcp_search")
        self.assertEqual(events[0]["status"], "returned")
        self.assertEqual(events[0]["query"], "Wagtail scheduling")

    def test_cursor_mcp_keeps_wrapper_identity_and_extracts_target(self):
        events = extract_events(
            [
                {
                    "step_id": 1,
                    "tool_calls": [
                        {
                            "tool_call_id": "wrapper",
                            "function_name": "mcpToolCall",
                            "arguments": {
                                "serverIdentifier": "wagtail-guide",
                                "toolName": "fetch_docs_page",
                                "args": {"url": "/en/concepts/scheduled-publishing/"},
                            },
                        }
                    ],
                }
            ],
            "trial",
        )
        self.assertEqual(events[0]["tool"], "mcpToolCall")
        self.assertEqual(events[0]["kind"], "mcp_fetch")
        self.assertEqual(
            events[0]["urls"],
            ["https://guide.wagtail.org/en/concepts/scheduled-publishing/"],
        )

    def test_guide_mcp_relative_targets_and_recorded_configuration(self):
        events = extract_events(
            [
                {
                    "step_id": 1,
                    "tool_calls": [
                        {
                            "tool_call_id": "mcp",
                            "function_name": "wagtail-guide_fetch_docs_page",
                            "arguments": {"url": "/en/how-to-guides/manage-pages/"},
                        }
                    ],
                }
            ],
            "trial",
        )
        self.assertEqual(events[0]["kind"], "mcp_fetch")
        self.assertEqual(
            events[0]["urls"],
            ["https://guide.wagtail.org/en/how-to-guides/manage-pages/"],
        )
        recorded = controls(
            {
                "agent": {
                    "mcp_servers": [
                        {
                            "name": "wagtail-guide",
                            "transport": "streamable-http",
                            "url": "https://guide.wagtail.org/mcp",
                            "headers": {"Authorization": "secret"},
                        }
                    ]
                }
            }
        )
        self.assertNotIn("secret", json.dumps(recorded))
        self.assertEqual(recorded["mcp_servers"][0]["name"], "wagtail-guide")

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
