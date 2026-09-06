"""Deterministic grader for The Museum of Lost Hours."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _set_f1(expected: Any, predicted: Any) -> float:
    expected_set = set(expected) if isinstance(expected, list) else set()
    predicted_set = set(predicted) if isinstance(predicted, list) else set()
    if not expected_set and not predicted_set:
        return 1.0
    if not expected_set or not predicted_set:
        return 0.0
    overlap = len(expected_set & predicted_set)
    precision = overlap / len(predicted_set)
    recall = overlap / len(expected_set)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def grade_submission(
    expected: dict[str, Any], submission: dict[str, Any]
) -> dict[str, Any]:
    expected_locations = expected["final_locations"]
    predicted_locations = submission.get("final_locations", {})
    if not isinstance(predicted_locations, dict):
        predicted_locations = {}

    correct_locations = sum(
        predicted_locations.get(artifact) == room
        for artifact, room in expected_locations.items()
    )
    location_score = 60.0 * correct_locations / len(expected_locations)
    failed_seal_score = 15.0 * _set_f1(
        expected["failed_seals"], submission.get("failed_seals", [])
    )
    successful_rollback_score = 10.0 * _set_f1(
        expected["successful_rollbacks"],
        submission.get("successful_rollbacks", []),
    )
    failed_rollback_score = 5.0 * _set_f1(
        expected["failed_rollbacks"], submission.get("failed_rollbacks", [])
    )
    alarm_score = (
        10.0 if submission.get("false_alarm") == expected["false_alarm"] else 0.0
    )

    components = {
        "final_locations": round(location_score, 2),
        "failed_seals": round(failed_seal_score, 2),
        "successful_rollbacks": round(successful_rollback_score, 2),
        "failed_rollbacks": round(failed_rollback_score, 2),
        "false_alarm": round(alarm_score, 2),
    }
    return {
        "score": round(sum(components.values()), 2),
        "components": components,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--answer", type=Path, required=True)
    parser.add_argument("--submission", type=Path, required=True)
    args = parser.parse_args()

    expected = json.loads(args.answer.read_text(encoding="utf-8"))
    submission = json.loads(args.submission.read_text(encoding="utf-8"))
    result = grade_submission(expected, submission)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

