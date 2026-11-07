import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from harbor.agents.factory import AgentFactory
from harbor.models.trial.config import AgentConfig

from replay import call_api, empty_vibe_discovery
from report import report
from runner import HERE, agent_config, credentials, read
from tool_controls import CurrentVibe


class TestAdapter(unittest.TestCase):
    def test_only_empty_vibe_discovery_is_allowed(self):
        call = {
            "name": "search_tool_functions",
            "output": json.dumps(
                {
                    "status": "completed",
                    "output": {"toolCount": 0, "connectorNoticeCount": 0},
                }
            ),
        }
        self.assertTrue(empty_vibe_discovery(call))
        state = json.loads(call["output"])
        state["output"]["toolCount"] = 1
        self.assertFalse(empty_vibe_discovery({**call, "output": json.dumps(state)}))
        self.assertFalse(empty_vibe_discovery({**call, "name": "web_search"}))

    def test_vibe_export_preserves_tool_calls_and_usage(self):
        with tempfile.TemporaryDirectory() as directory:
            logs = Path(directory)
            export = logs / "vibe-export"
            export.mkdir()
            (export / "export.json").write_text(
                json.dumps(
                    {
                        "outcome": "finished",
                        "usage": {"input_tokens": 100, "output_tokens": 20},
                        "cost_usd": 0.01,
                    }
                )
            )
            (logs / "vibe.txt").write_text(
                json.dumps(
                    [
                        {
                            "type": "effect",
                            "id": "call-1",
                            "detail": {
                                "toolName": "connector_web_search.web_search",
                                "input": {"query": "test"},
                            },
                            "state": {
                                "status": "completed",
                                "output": "search results",
                            },
                        },
                        {"type": "message", "role": "assistant", "content": "Answer"},
                    ]
                )
            )
            agent = CurrentVibe(logs_dir=logs, model_name="mistral/mistral-large-4")
            trajectory = agent._convert_sessions_to_trajectory(
                agent._get_session_chain()
            )
            self.assertEqual(
                trajectory.steps[0].tool_calls[0].function_name,
                "connector_web_search.web_search",
            )
            self.assertIn(
                "search results", trajectory.steps[0].observation.results[0].content
            )
            self.assertEqual(trajectory.final_metrics.total_prompt_tokens, 100)
            self.assertEqual(trajectory.final_metrics.total_cost_usd, 0.01)
            self.assertEqual(trajectory.steps[-1].message, "Answer")

    def test_report_keeps_missing_trials_and_costs_visible(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            trial = root / "jobs/model--baseline/trial/result.json"
            trial.parent.mkdir(parents=True)
            trial.write_text(
                json.dumps(
                    {"agent_info": {"version": "1"}, "agent_result": {"cost_usd": None}}
                )
            )
            (root / "manifest.json").write_text(
                json.dumps(
                    {
                        "repeat": 3,
                        "cases": [{}],
                        "jobs": [
                            {"name": "model--baseline", "entry": {"model": "model"}}
                        ],
                    }
                )
            )
            (root / "grades.json").write_text(
                json.dumps(
                    {
                        "results": {
                            "results": [
                                {
                                    "testCase": {"vars": {"trial_path": str(trial)}},
                                    "success": False,
                                    "response": {"error": "Invalid no-tools arm"},
                                }
                            ]
                        }
                    }
                )
            )
            with patch("builtins.print"):
                report(root)
            with (root / "comparison.csv").open() as file:
                row = next(csv.DictReader(file))
            self.assertEqual(row["expected"], "3")
            self.assertEqual(row["errors"], "1")
            self.assertEqual(row["known_agent_cost_usd"], "")
            self.assertEqual(row["cost_coverage"], "0")

    def test_every_matrix_arm_uses_valid_harbor_options(self):
        for entry in read(HERE / "matrix.yaml")["entries"]:
            for arm in read(HERE / "arms.yaml")[entry["harness"]]:
                config = AgentConfig.model_validate(agent_config(entry, arm, {}))
                cls = AgentFactory.get_agent_class_from_config(config)
                cls.options_model.model_validate(config.kwargs)

    def test_model_specific_keys_and_no_values_in_config(self):
        entry = next(
            e
            for e in read(HERE / "matrix.yaml")["entries"]
            if e["id"] == "opencode-deepseek"
        )
        with patch.dict("os.environ", {}, clear=True):
            auth = credentials(
                entry,
                {
                    "neuralwatt_keys": {
                        "deepseek-v4.1-flash": "test-secret",
                        "glm-5.3-flash": "wrong-key",
                    }
                },
            )
        self.assertEqual(auth, {"NEURALWATT_API_KEY": "test-secret"})
        self.assertNotIn("test-secret", json.dumps(agent_config(entry, "native", {})))

    def replay(self, steps, arm="native", exception=None, harness="opencode"):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "agent").mkdir()
            (path / "agent/trajectory.json").write_text(json.dumps({"steps": steps}))
            (path / "result.json").write_text(
                json.dumps(
                    {
                        "agent_info": {"name": harness},
                        "exception_info": exception,
                        "agent_result": {"cost_usd": None},
                    }
                )
            )
            return call_api(
                "unused",
                {},
                {"vars": {"trial_path": str(path / "result.json"), "arm": arm}},
            )

    def test_answer_and_tool_observation_are_preserved(self):
        steps = [
            {
                "source": "agent",
                "message": "Searching",
                "tool_calls": [
                    {
                        "tool_call_id": "a",
                        "function_name": "webfetch",
                        "arguments": {"url": "https://guide.wagtail.org/"},
                    }
                ],
                "observation": {
                    "results": [{"source_call_id": "a", "content": "page content"}]
                },
            },
            {"source": "agent", "message": [{"type": "text", "text": "Final answer"}]},
        ]
        response = self.replay(steps)
        self.assertEqual(response["output"], "Final answer")
        self.assertEqual(response["metadata"]["toolCalls"][0]["output"], "page content")
        self.assertNotIn("cost", response)
        self.assertIn("Invalid no-tools arm", self.replay(steps, "baseline")["error"])

    def test_codex_web_rejects_non_web_tools(self):
        for name in ("web_search_call", "exec", "exec_command", "js_repl"):
            steps = [
                {
                    "source": "agent",
                    "message": "",
                    "tool_calls": [
                        {"tool_call_id": "a", "function_name": name, "arguments": {}}
                    ],
                },
                {"source": "agent", "message": "Final answer"},
            ]
            response = self.replay(steps, "web", harness="codex")
            if name == "web_search_call":
                self.assertEqual(response["output"], "Final answer")
            else:
                self.assertIn("Invalid Codex web-only arm", response["error"])

    def test_failed_run_does_not_grade_partial_answer(self):
        response = self.replay(
            [{"source": "agent", "message": "Partial answer"}],
            exception={"exception_type": "AgentTimeoutError"},
        )
        self.assertEqual(response, {"error": "AgentTimeoutError"})

    def test_baseline_without_tools_is_scored(self):
        self.assertEqual(
            self.replay([{"source": "agent", "message": "From memory"}], "baseline")[
                "output"
            ],
            "From memory",
        )

    def test_unfinished_tool_turn_is_not_an_answer(self):
        result = self.replay(
            [
                {"source": "agent", "message": "I will look that up."},
                {
                    "source": "agent",
                    "message": "",
                    "tool_calls": [
                        {
                            "tool_call_id": "a",
                            "function_name": "webfetch",
                            "arguments": {},
                        }
                    ],
                },
            ]
        )
        self.assertIn("without a final answer", result["error"])
