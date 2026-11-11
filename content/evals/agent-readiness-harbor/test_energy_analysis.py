import argparse
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from energy_analysis import (
    analyze,
    energy,
    match_requests,
    native_turns,
    regime,
    timestamp,
    window_assignments,
)


class TestEnergyAttribution(unittest.TestCase):
    def setUp(self) -> None:
        self.request = {
            "request_id": "request-one",
            "requested_model": "model-one",
            "created_at": "2026-11-07T00:00:10Z",
            "prompt_tokens": 12,
            "cached_tokens": 10,
            "completion_tokens": 5,
            "energy_joules": 3600,
            "attribution_method": "gpu_measured",
        }
        self.turn = {
            "trial_id": "one",
            "model": "model-one",
            "timestamp": timestamp(self.request["created_at"]) + 0.5,
            "prompt_tokens": 12,
            "cached_tokens": 10,
            "completion_tokens": 5,
        }

    def test_zero_missing_and_estimates(self) -> None:
        self.assertEqual(energy({"energy_joules": 0}), (0, "unknown_method"))
        self.assertEqual(energy({}), (None, "missing"))
        self.assertEqual(energy({"energy_joules": -1}), (None, "missing"))
        self.assertEqual(
            energy(
                {"energy_kwh": 0.001, "attribution_method": "conservative_fallback"}
            ),
            (1, "estimated"),
        )
        self.assertEqual(energy(self.request), (1, "reported_non_estimate"))

    def test_join_requires_model_tokens_and_time(self) -> None:
        self.assertEqual(match_requests([self.turn], [self.request])[0], {0: 0})
        for change in (
            {"model": "other"},
            {"cached_tokens": 0},
            {"completion_tokens": 4},
            {"timestamp": self.turn["timestamp"] + 4},
        ):
            self.assertEqual(
                match_requests([{**self.turn, **change}], [self.request])[0], {}
            )

    def test_ambiguous_matches_never_allocate_twice(self) -> None:
        matches, candidates = match_requests(
            [self.turn, {**self.turn, "trial_id": "outside:one"}], [self.request]
        )
        self.assertEqual(matches, {})
        self.assertEqual(candidates, {0: [0], 1: [0]})
        self.assertEqual(
            match_requests(
                [self.turn], [self.request, {**self.request, "request_id": "two"}]
            )[0],
            {},
        )
        with self.assertRaisesRegex(ValueError, "Duplicate request"):
            match_requests([self.turn], [self.request, self.request])

    def test_known_request_id_must_not_fall_back_to_a_different_id(self) -> None:
        matches, _ = match_requests(
            [{**self.turn, "request_id": "not-in-export"}], [self.request]
        )
        self.assertEqual(matches, {})

    def test_native_tokens_include_cache_and_reasoning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "agent").mkdir()
            event = {
                "type": "step_finish",
                "timestamp": 10000,
                "sessionID": "session",
                "part": {
                    "messageID": "message",
                    "tokens": {
                        "input": 2,
                        "output": 3,
                        "reasoning": 2,
                        "cache": {"read": 10, "write": 0},
                    },
                },
            }
            (root / "agent/opencode.txt").write_text(
                "bad line\n" + (json.dumps(event) + "\n") * 2
            )
            turns = native_turns(
                {
                    "id": "one",
                    "model": "neuralwatt/model-one",
                    "trial_path": str(root / "result.json"),
                }
            )
            self.assertEqual(len(turns), 1)
            self.assertEqual(
                (
                    turns[0]["prompt_tokens"],
                    turns[0]["cached_tokens"],
                    turns[0]["completion_tokens"],
                ),
                (12, 10, 5),
            )

    def test_change_day_is_not_claimed_post_change(self) -> None:
        self.assertEqual(
            regime({"created_at": "2026-11-06T23:59:59Z"}), "change_day_uncertain"
        )
        self.assertEqual(regime(self.request), "post_change")

    def test_time_windows_never_split_across_cohorts_or_debug_tasks(self) -> None:
        trial = {
            "id": "one",
            "phase": "initial",
            "harness": "opencode",
            "model": "neuralwatt/model-one",
            "arm": "native",
            "agent_execution": {
                "started_at": "2026-11-07T00:00:00Z",
                "finished_at": "2026-11-07T00:00:11Z",
            },
        }
        allocations, _ = window_assignments([trial], [self.request], set())
        self.assertEqual(
            (allocations[0]["trace_id"], allocations[0]["match_method"]),
            ("one", "time_only"),
        )
        allocations, _ = window_assignments(
            [trial, {**trial, "id": "two"}], [self.request], set()
        )
        self.assertEqual(
            (allocations[0]["trace_id"], allocations[0]["match_method"]),
            ("", "group_only_time"),
        )
        for change, reason in (
            ({"id": "two", "arm": "no-tools"}, "different_cohorts_overlap"),
            ({"id": "outside:two"}, "outside_task_competes"),
        ):
            allocations, excluded = window_assignments(
                [trial, {**trial, **change}], [self.request], set()
            )
            self.assertEqual(allocations, [])
            self.assertEqual(excluded[reason], 1)
        self.assertEqual(window_assignments([trial], [self.request], {0}), ([], {}))
        self.assertEqual(
            window_assignments([], [self.request], set())[1]["no_eligible_window"], 1
        )

    def test_task_denominators_missingness_and_csv_totals(self) -> None:
        base = {
            "phase": "initial",
            "harness": "opencode",
            "model": "neuralwatt/model-one",
            "arm": "native",
            "case": "case",
            "passed": True,
            "execution_error": False,
            "agent_execution": {
                "started_at": "2026-11-07T00:00:00Z",
                "finished_at": "2026-11-07T00:00:11Z",
            },
        }
        trials = [{**base, "id": "one"}, {**base, "id": "missing", "passed": False}]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = argparse.Namespace(
                trials=root / "trials.jsonl", cache=root, output=root
            )
            args.trials.write_text("\n".join(json.dumps(row) for row in trials))
            with (
                patch("energy_analysis.load_trials", return_value=trials),
                patch("energy_analysis.read_requests", return_value=[self.request]),
                patch("energy_analysis.other_trials", return_value=[]),
                patch("energy_analysis.native_turns", side_effect=[[self.turn], []]),
            ):
                analyze(args)
            rows = list(
                csv.DictReader((root / "ENERGY_TRIALS.csv").read_text().splitlines())
            )
            self.assertEqual(rows[0]["covered_task_energy_wh"], "1.0")
            self.assertEqual(rows[1]["attributed_energy_wh"], "")
            group = next(
                r
                for r in csv.DictReader(
                    (root / "ENERGY_GROUPS.csv").read_text().splitlines()
                )
                if r["scope"] == "cohort"
            )
            self.assertEqual(
                (
                    group["attempts"],
                    group["covered_tasks"],
                    group["partial_or_unknown_tasks"],
                ),
                ("2", "1", "1"),
            )
            self.assertEqual(group["mean_covered_task_wh"], "1.0")
            # An overlapping auxiliary request belongs to the cohort, not either
            # task. Its energy changes the batch mean, never the strict median.
            extra = {**self.request, "request_id": "auxiliary", "prompt_tokens": 99}
            with (
                patch("energy_analysis.load_trials", return_value=trials),
                patch(
                    "energy_analysis.read_requests", return_value=[self.request, extra]
                ),
                patch("energy_analysis.other_trials", return_value=[]),
                patch("energy_analysis.native_turns", side_effect=[[self.turn], []]),
            ):
                analyze(args)
            batch = list(
                csv.DictReader(
                    (root / "ENERGY_WINDOW_GROUPS.csv").read_text().splitlines()
                )
            )[0]
            self.assertEqual(
                (
                    batch["group_only_requests"],
                    batch["group_only_wh"],
                    batch["window_attributed_total_wh"],
                    batch["mean_window_attributed_wh_per_attempt"],
                ),
                ("1", "1.0", "2.0", "1.0"),
            )
            group = next(
                r
                for r in csv.DictReader(
                    (root / "ENERGY_GROUPS.csv").read_text().splitlines()
                )
                if r["scope"] == "cohort"
            )
            self.assertEqual(
                (group["covered_tasks"], group["median_attributed_attempt_wh"]),
                ("0", "1.0"),
            )


if __name__ == "__main__":
    unittest.main()
