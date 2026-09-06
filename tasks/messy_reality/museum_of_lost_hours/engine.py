"""Generator and deterministic state engine for The Museum of Lost Hours."""

from __future__ import annotations

import json
import random
from copy import deepcopy
from pathlib import Path
from typing import Any


ARTIFACTS = [
    "The Moon That Forgot the Sea",
    "The Clock of Unfinished Hours",
    "The Glass Fox",
    "The Map of a City That Never Existed",
    "The Choir in a Jar",
    "The Crown of Quiet Rain",
    "The Door That Opens Once",
    "The Portrait of an Empty Chair",
]

ROOMS = [
    "Hall of Echoes",
    "Mirror Vault",
    "Tidal Gallery",
    "Restoration Atelier",
    "Closed Archive",
    "North Lantern Room",
    "Gallery of Small Storms",
]

TICKET_WORDS = [
    "LYNX",
    "MOTH",
    "RAVEN",
    "EMBER",
    "IVORY",
    "MIRROR",
    "THORN",
    "ORBIT",
    "VELVET",
    "COMET",
    "MARBLE",
    "WREN",
]

RULES = [
    "A MOVE REQUEST only opens a ticket. It does not move an artifact.",
    "A SEAL moves the artifact only if the ticket is still open, the artifact is still in the stated source room, and the destination room is unlocked.",
    "A failed SEAL closes its ticket and cannot be retried.",
    "A CANCEL closes an open ticket without moving anything.",
    "A ROLLBACK reverses a previously sealed move only if that same ticket is still the artifact's most recent successful move.",
    "LOCK and UNLOCK take effect immediately. A locked source room may be moved out of, but a locked destination may not receive an artifact.",
    "If the same event ID appears more than once, later copies are transmission echoes and must be ignored.",
    "Sensor snapshots and staff notes are observations only. They never change museum state.",
    "Process non-duplicate events in the order shown. Timestamps printed inside a retransmitted event may therefore appear out of order.",
]


def _ticket_ids(rng: random.Random, count: int) -> list[str]:
    words = rng.sample(TICKET_WORDS, count)
    return [f"T-{word}-{rng.randint(10, 99)}" for word in words]


def _event_id_factory(rng: random.Random):
    used: set[str] = set()

    def new_id() -> str:
        while True:
            candidate = f"E-{rng.randint(1000, 9999)}"
            if candidate not in used:
                used.add(candidate)
                return candidate

    return new_id


def _format_time(minutes_after_midnight: int) -> str:
    hours, minutes = divmod(minutes_after_midnight, 60)
    return f"{hours:02d}:{minutes:02d}"


def generate_instance(seed: int) -> dict[str, Any]:
    """Create a reproducible museum incident with a known causal structure."""

    rng = random.Random(seed)
    artifacts = rng.sample(ARTIFACTS, 5)
    rooms = rng.sample(ROOMS, 5)
    tickets = _ticket_ids(rng, 8)
    new_event_id = _event_id_factory(rng)
    minute = 3
    events: list[dict[str, Any]] = []

    def add(kind: str, **fields: Any) -> dict[str, Any]:
        nonlocal minute
        event = {
            "event_id": new_event_id(),
            "time": _format_time(minute),
            "kind": kind,
            **fields,
        }
        minute += rng.choice([1, 2, 3])
        events.append(event)
        return event

    initial_locations = dict(zip(artifacts, rooms, strict=True))

    # A valid move followed by a retransmitted copy of its SEAL.
    add(
        "open_move",
        ticket=tickets[0],
        artifact=artifacts[0],
        source=rooms[0],
        destination=rooms[1],
    )
    first_seal = add("seal", ticket=tickets[0])

    # A cancelled ticket whose later SEAL must fail.
    add(
        "open_move",
        ticket=tickets[1],
        artifact=artifacts[1],
        source=rooms[1],
        destination=rooms[2],
    )
    add("cancel", ticket=tickets[1])
    add(
        "sensor",
        captured_at=first_seal["time"],
        room=rooms[0],
        contents=[],
    )
    add("seal", ticket=tickets[1])
    events.append(deepcopy(first_seal))

    # A failed move into a locked room, followed by a fresh valid ticket.
    add("lock", room=rooms[3])
    add(
        "open_move",
        ticket=tickets[2],
        artifact=artifacts[2],
        source=rooms[2],
        destination=rooms[3],
    )
    add("seal", ticket=tickets[2])
    add("unlock", room=rooms[3])
    add(
        "open_move",
        ticket=tickets[3],
        artifact=artifacts[2],
        source=rooms[2],
        destination=rooms[3],
    )
    add("seal", ticket=tickets[3])

    # A move that is cleanly rolled back.
    add(
        "open_move",
        ticket=tickets[4],
        artifact=artifacts[3],
        source=rooms[3],
        destination=rooms[4],
    )
    add("seal", ticket=tickets[4])
    add(
        "note",
        text=(
            f"A conservator wrote that {artifacts[3]} looked better in "
            f"{rooms[4]}. This note is not an instruction."
        ),
    )
    add("rollback", ticket=tickets[4])

    # An older move cannot be rolled back after a newer move supersedes it.
    add(
        "open_move",
        ticket=tickets[5],
        artifact=artifacts[4],
        source=rooms[4],
        destination=rooms[0],
    )
    add("seal", ticket=tickets[5])
    add(
        "open_move",
        ticket=tickets[6],
        artifact=artifacts[4],
        source=rooms[0],
        destination=rooms[2],
    )
    add("seal", ticket=tickets[6])
    add("rollback", ticket=tickets[5])
    add("rollback", ticket=tickets[6])

    # A final ticket states the wrong source room.
    add(
        "open_move",
        ticket=tickets[7],
        artifact=artifacts[1],
        source=rooms[3],
        destination=rooms[0],
    )
    add("seal", ticket=tickets[7])
    add(
        "sensor",
        captured_at="00:01",
        room=rooms[4],
        contents=[artifacts[4]],
    )

    instance: dict[str, Any] = {
        "task_id": "nwb-mr-001",
        "task_version": "0.1.0",
        "title": "The Museum of Lost Hours",
        "seed": seed,
        "rules": RULES,
        "initial_locations": initial_locations,
        "events": events,
    }

    provisional = solve_instance(instance)
    true_alarm = {
        "alarm_id": f"ALARM-{rng.choice(['BELL', 'OWL', 'ASH'])}",
        "artifact": artifacts[2],
        "claimed_room": provisional["final_locations"][artifacts[2]],
    }
    false_rooms = [
        room
        for room in rooms
        if room != provisional["final_locations"][artifacts[0]]
    ]
    false_alarm = {
        "alarm_id": f"ALARM-{rng.choice(['MOTH', 'GLASS', 'TIDE'])}",
        "artifact": artifacts[0],
        "claimed_room": rng.choice(false_rooms),
    }
    alarms = [true_alarm, false_alarm]
    rng.shuffle(alarms)
    instance["alarms"] = alarms
    return instance


def solve_instance(instance: dict[str, Any]) -> dict[str, Any]:
    """Apply the published rules and return the deterministic ground truth."""

    locations = dict(instance["initial_locations"])
    tickets: dict[str, dict[str, Any]] = {}
    locked_rooms: set[str] = set()
    seen_event_ids: set[str] = set()
    last_move_ticket: dict[str, str | None] = {
        artifact: None for artifact in locations
    }
    failed_seals: list[str] = []
    successful_rollbacks: list[str] = []
    failed_rollbacks: list[str] = []

    for event in instance["events"]:
        event_id = event["event_id"]
        if event_id in seen_event_ids:
            continue
        seen_event_ids.add(event_id)
        kind = event["kind"]

        if kind == "open_move":
            tickets[event["ticket"]] = {
                "artifact": event["artifact"],
                "source": event["source"],
                "destination": event["destination"],
                "status": "open",
                "previous_move_ticket": None,
            }
        elif kind == "cancel":
            ticket = tickets.get(event["ticket"])
            if ticket and ticket["status"] == "open":
                ticket["status"] = "cancelled"
        elif kind == "lock":
            locked_rooms.add(event["room"])
        elif kind == "unlock":
            locked_rooms.discard(event["room"])
        elif kind == "seal":
            ticket_id = event["ticket"]
            ticket = tickets.get(ticket_id)
            can_commit = bool(
                ticket
                and ticket["status"] == "open"
                and locations[ticket["artifact"]] == ticket["source"]
                and ticket["destination"] not in locked_rooms
            )
            if not can_commit:
                failed_seals.append(ticket_id)
                if ticket and ticket["status"] == "open":
                    ticket["status"] = "seal_failed"
                continue

            artifact = ticket["artifact"]
            ticket["previous_move_ticket"] = last_move_ticket[artifact]
            locations[artifact] = ticket["destination"]
            last_move_ticket[artifact] = ticket_id
            ticket["status"] = "committed"
        elif kind == "rollback":
            ticket_id = event["ticket"]
            ticket = tickets.get(ticket_id)
            can_rollback = bool(
                ticket
                and ticket["status"] == "committed"
                and locations[ticket["artifact"]] == ticket["destination"]
                and last_move_ticket[ticket["artifact"]] == ticket_id
            )
            if not can_rollback:
                failed_rollbacks.append(ticket_id)
                continue

            artifact = ticket["artifact"]
            locations[artifact] = ticket["source"]
            last_move_ticket[artifact] = ticket["previous_move_ticket"]
            ticket["status"] = "rolled_back"
            successful_rollbacks.append(ticket_id)
        elif kind in {"sensor", "note"}:
            continue
        else:
            raise ValueError(f"Unknown event kind: {kind}")

    answer: dict[str, Any] = {
        "final_locations": locations,
        "failed_seals": sorted(failed_seals),
        "successful_rollbacks": sorted(successful_rollbacks),
        "failed_rollbacks": sorted(failed_rollbacks),
    }

    if "alarms" in instance:
        false_alarms = [
            alarm["alarm_id"]
            for alarm in instance["alarms"]
            if locations[alarm["artifact"]] != alarm["claimed_room"]
        ]
        if len(false_alarms) != 1:
            raise ValueError("Each instance must contain exactly one false alarm")
        answer["false_alarm"] = false_alarms[0]

    return answer


def _render_event(event: dict[str, Any]) -> str:
    prefix = f"[{event['time']} | {event['event_id']}]"
    kind = event["kind"]
    if kind == "open_move":
        return (
            f"{prefix} MOVE REQUEST {event['ticket']}: move "
            f"\"{event['artifact']}\" from {event['source']} to "
            f"{event['destination']}."
        )
    if kind == "seal":
        return f"{prefix} SEAL {event['ticket']}."
    if kind == "cancel":
        return f"{prefix} CANCEL {event['ticket']}."
    if kind == "rollback":
        return f"{prefix} ROLLBACK {event['ticket']}."
    if kind == "lock":
        return f"{prefix} LOCK {event['room']}."
    if kind == "unlock":
        return f"{prefix} UNLOCK {event['room']}."
    if kind == "sensor":
        contents = ", ".join(f'\"{item}\"' for item in event["contents"])
        contents = contents or "nothing"
        return (
            f"{prefix} DELAYED SENSOR SNAPSHOT captured at "
            f"{event['captured_at']}: {event['room']} contained {contents}."
        )
    if kind == "note":
        return f"{prefix} STAFF NOTE: {event['text']}"
    raise ValueError(f"Unknown event kind: {kind}")


def render_prompt(instance: dict[str, Any]) -> str:
    """Render the model-facing prompt for an instance."""

    rules = "\n".join(
        f"{index}. {rule}" for index, rule in enumerate(instance["rules"], 1)
    )
    placements = "\n".join(
        f"- \"{artifact}\" — {room}"
        for artifact, room in instance["initial_locations"].items()
    )
    events = "\n".join(_render_event(event) for event in instance["events"])
    alarms = "\n".join(
        f"- {alarm['alarm_id']}: claims \"{alarm['artifact']}\" is in "
        f"{alarm['claimed_room']}."
        for alarm in instance["alarms"]
    )

    return f"""# Incident File: {instance['title']}

At the end of the night shift, the Museum of Lost Hours sealed every gallery
and discovered that two automated alarms disagreed. Reconstruct the museum's
real final state from the night ledger.

## Night Protocol

{rules}

## Initial placement at midnight

{placements}

Multiple artifacts may occupy the same room.

## Night ledger

{events}

## Final alarms

{alarms}

Exactly one alarm is false.

## Required answer

Return JSON only, using exactly this structure:

```json
{{
  "final_locations": {{
    "artifact name": "room name"
  }},
  "failed_seals": ["ticket ID"],
  "successful_rollbacks": ["ticket ID"],
  "failed_rollbacks": ["ticket ID"],
  "false_alarm": "alarm ID"
}}
```

Include every artifact in `final_locations`. List ticket IDs once each and in
alphabetical order. Do not include explanations outside the JSON.
"""


def write_instance(output_dir: Path, seed: int) -> dict[str, Any]:
    """Write a prompt, machine-readable instance, and answer key."""

    output_dir.mkdir(parents=True, exist_ok=True)
    instance = generate_instance(seed)
    answer = solve_instance(instance)
    (output_dir / "instance.json").write_text(
        json.dumps(instance, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "prompt.md").write_text(render_prompt(instance), encoding="utf-8")
    (output_dir / "answer.json").write_text(
        json.dumps(answer, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return answer
