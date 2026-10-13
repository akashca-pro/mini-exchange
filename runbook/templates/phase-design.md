# P{N} design — {phase name}

> Written by Akash before any code exists ([RB-001](../procedures/RB-001-build-a-phase.md), Step 3). Claude reviews it in the **Review** table, and Akash revises. Time-box: two hours. Write it badly rather than not at all.

## Problem

{What can't the system do yet, and why does that matter? Two to four sentences.}

## Requirements covered

| ID | Requirement, invariant or target (from requirements.md) | How I'll prove it |
|---|---|---|
| FR-{x} | | {test name, or the measurement to take} |
| I{x} | | |

## API changes

{For each endpoint or message: method and path (or channel), the request, the response, and the errors.}

## Data model changes

{New or changed entities, fields and tables, with the reason for each.}

## How it works

{The flow, step by step, from request to final state. Add a small diagram if it helps.}

## Concurrency and ordering

{Who reads or writes shared state, in what order, and what stops two operations from colliding.}

## Failure modes

At least three.

| What fails | What happens then | How the design handles it |
|---|---|---|
| | | |

## Answers to this phase's open questions

{Each Q{N}.x from design.md, answered, or marked "don't know, because…".}

## Alternatives considered

| Option | Why not |
|---|---|
| | |

## My open questions

{What you're unsure about. These become E1 questions or research notes.}

## Hand-written piece

{Which part you'll write yourself. plan.md names it; add detail here.}

## Review (Claude)

| # | Severity (blocking / important / learning) | Finding | Akash's response |
|---|---|---|---|
| 1 | | | |
