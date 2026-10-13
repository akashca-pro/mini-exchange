# {Project} design

> Drafted by Claude and approved by Akash before any code exists ([RB-001](../../procedures/RB-001-deliver-a-project.md), Steps 2–3). The **Approval** table at the bottom records each round.

## Problem

{What can't the system do yet, and why does that matter? Two to four sentences.}

## Requirements covered

| ID | Requirement, invariant or target (from requirements.md) | How it's proven |
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

## Answers to the open questions

{Phase projects: each Q{N}.x that design.md lists for this phase, answered.}

## Alternatives considered

| Option | Why not |
|---|---|
| | |

## Still open

{Anything unverified, each marked [CONFIRM] with how it will be settled. Settle these before approval, or say why they can wait.}

## Approval

| Round | Date | Akash's answer | Changes requested |
|---|---|---|---|
| 1 | | {approved / changes requested} | |
