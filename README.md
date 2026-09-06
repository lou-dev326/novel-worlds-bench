# Novel Worlds Benchmark

Many existing benchmarks mostly reward memorized knowledge, familiar reasoning patterns, or performance on a fixed set of public questions.

Novel Worlds Benchmark focuses on how models handle unfamiliar rules, messy information, missing context, and changing environments. We want to build a collection of miniature worlds that are not especially difficult for humans once understood, but still cause today’s models to fail in interesting ways.

We care not only about whether a model gets the right answer, but also about why it fails—and whether those failures are consistent, reproducible, and understandable.

## What Do We Test?

The benchmark currently covers four types of tasks.

### 1. Rule Discovery

The model must figure out how an unfamiliar system works from examples, observations, or a history of interactions.

### 2. Messy Reality

The model must reason through noisy logs, conflicting records, long instructions, changing states, and distracting information.

### 3. Staying Clear-Headed Under Uncertainty

The model must recognize missing information, contradictory assumptions, impossible requests, and situations where guessing would do more harm than good.

### 4. Adaptive Action

The model must explore, take action, observe what happens, recover from mistakes, and complete a goal with limited resources.

## What Makes a Good Task?

A good Novel Worlds task should:

- Avoid relying on obscure factual knowledge
- Be solvable by a careful human in roughly 5–20 minutes
- Make strong models fail in interesting ways
- Reveal something meaningful about the model when it fails
- Support multiple fresh variations of the same underlying task
- Have a reproducible grading process
- Keep the same correct answer when irrelevant details are changed
- Feel like a miniature world rather than an exam question

## How We Evaluate

We want to provide more than a single leaderboard score.

Alongside overall task success, the benchmark will look at:

- Rule discovery
- State tracking
- Robustness to irrelevant changes
- Appropriate handling of uncertainty
- Instruction following
- Error recovery
- Cost and efficiency

Whenever possible, tasks will use deterministic graders. When human judgment is necessary, we will document the rubric and review process.

## First Prototype

### The Museum of Lost Hours (`nwb-mr-001`)

At the end of a midnight shift, two museum alarms disagree. The model must
reconstruct the real location of five artifacts from a ledger containing
pending moves, cancellations, room locks, rollbacks, duplicated records, and
delayed sensor snapshots.

The task includes a reproducible generator and a deterministic grader.

[Explore the task](tasks/messy_reality/museum_of_lost_hours)

## Current Status

The project is currently defining its task standards and building the first set of benchmark prototypes.

## Contributing

Novel Worlds Benchmark welcomes contributions such as:

- Unusual task ideas
- Reproducible examples of model failures
- Designs for task generators
- Deterministic grading methods
- Feedback on the benchmark methodology

More detailed contribution guidelines will be added once the task format has stabilized.

## License

This project is licensed under the Apache License 2.0.
