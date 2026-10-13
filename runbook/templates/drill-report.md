# Drill — {pN-name}

{YYYY-MM-DD} · budget {n} min · branch `drill/{pN-name}` · trigger: {planned / real bug / practice}

## Symptom

{Exactly as the drill master reported it, and the reproduce command.}

## Observations

{Facts only, no guesses. At least one should be "it does not happen when…".}

1.
2.
3.

## Location

{"The fault is in X, because observation Y."}

## Hypotheses

| # | Hypothesis (mechanism) | Disproof test | Result |
|---|---|---|---|
| 1 | | | |
| 2 | | | |

## Root cause

{The mechanism in two or three sentences: how the fault produces the symptom.}

## Fix

{In words first, then what changed.}

## Regression test

{Test name.} Fails before the fix: {yes/no}. Passes after the fix: {yes/no}.

## How production would catch this

{A metric, alert or log line, or a design change that makes it impossible.}

## Score

- Time to root cause: {min}
- Hints used: {none / H1 / H2 / H3 / H4}
- What I'd do first next time:
