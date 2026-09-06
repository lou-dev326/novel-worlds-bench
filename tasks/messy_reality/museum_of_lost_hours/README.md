# The Museum of Lost Hours

**Task ID:** `nwb-mr-001`  
**Family:** Messy Reality  
**Status:** Prototype  
**Version:** 0.1.0

At the end of a midnight shift, two museum alarms disagree. The model must
reconstruct the real location of five strangely named artifacts from a ledger
containing pending requests, seals, cancellations, room locks, rollbacks,
transmission echoes, delayed sensor snapshots, and irrelevant staff notes.

The task tests whether a model can separate reported activity from state that
actually changed.

## What is measured

- Event-sourced state tracking
- Cancellation and rollback semantics
- Resistance to stale or irrelevant observations
- Correct handling of duplicate records
- Exact structured output

## Files

- `engine.py` generates instances, applies the rules, and renders prompts.
- `generate.py` is the command-line instance generator.
- `grade.py` scores model submissions without an LLM judge.
- `examples/public_001/` contains a fully disclosed development example.
- `tests/` checks generation, invariants, prompt rendering, and grading.

## Generate an instance

From the repository root:

```bash
python tasks/messy_reality/museum_of_lost_hours/generate.py \
  --seed 20260906 \
  --output /tmp/museum-instance
```

The generator writes:

- `instance.json` — structured world and ledger
- `prompt.md` — model-facing task
- `answer.json` — deterministic answer key

Evaluation seeds should remain private until their release is retired. The
included public example is for development and inspection only.

## Grade a submission

```bash
python tasks/messy_reality/museum_of_lost_hours/grade.py \
  --answer tasks/messy_reality/museum_of_lost_hours/examples/public_001/answer.json \
  --submission submission.json
```

Scoring totals 100 points:

- Final artifact locations: 60
- Failed seals: 15
- Successful rollbacks: 10
- Failed rollbacks: 5
- False alarm: 10

Ticket-list components use set F1 so that listing every ticket is penalized.

## Current limitations

Version 0.1 uses a fixed causal skeleton while randomizing artifact names,
rooms, ticket IDs, timestamps, alarm order, and surface details. It is designed
to validate the task concept before adding more event structures.

