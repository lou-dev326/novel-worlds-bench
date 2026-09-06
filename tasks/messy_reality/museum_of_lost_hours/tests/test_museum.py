from __future__ import annotations

import sys
import unittest
from pathlib import Path
from datetime import datetime


TASK_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TASK_DIR))

from engine import generate_instance, render_prompt, solve_instance  # noqa: E402
from grade import grade_submission  # noqa: E402


class MuseumTaskTests(unittest.TestCase):
    def test_generation_is_deterministic(self) -> None:
        self.assertEqual(generate_instance(42), generate_instance(42))

    def test_instances_have_one_false_alarm_and_expected_traps(self) -> None:
        for seed in range(20):
            instance = generate_instance(seed)
            answer = solve_instance(instance)
            self.assertEqual(len(answer["final_locations"]), 5)
            self.assertEqual(len(answer["failed_seals"]), 3)
            self.assertEqual(len(answer["successful_rollbacks"]), 2)
            self.assertEqual(len(answer["failed_rollbacks"]), 1)
            for event in instance["events"]:
                datetime.strptime(event["time"], "%H:%M")
            false_alarms = [
                alarm
                for alarm in instance["alarms"]
                if answer["final_locations"][alarm["artifact"]]
                != alarm["claimed_room"]
            ]
            self.assertEqual(len(false_alarms), 1)

    def test_prompt_contains_all_artifacts_and_required_schema(self) -> None:
        instance = generate_instance(7)
        prompt = render_prompt(instance)
        for artifact in instance["initial_locations"]:
            self.assertIn(artifact, prompt)
        self.assertIn('"failed_seals"', prompt)
        self.assertIn('"false_alarm"', prompt)

    def test_correct_submission_scores_100(self) -> None:
        instance = generate_instance(9)
        answer = solve_instance(instance)
        result = grade_submission(answer, answer)
        self.assertEqual(result["score"], 100.0)

    def test_empty_submission_scores_0(self) -> None:
        instance = generate_instance(11)
        answer = solve_instance(instance)
        result = grade_submission(answer, {})
        self.assertEqual(result["score"], 0.0)


if __name__ == "__main__":
    unittest.main()
