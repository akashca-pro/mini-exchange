---
runbook_id: RB-002
title: "Run a debug drill"
version: 1.0.0
status: active
owner: "Akash (learner and project owner)"
owner_contact: "this repo"
last_reviewed: 2026-10-13
review_by: 2026-12-31            # or after the first three drills, whichever comes first
last_executed: never
audience: "Akash investigates; Claude is drill master. Assumes beginner Python."
estimated_duration: "Budget per drill, 60 minutes by default; plan.md or the drill master may set another"
executor_mode: human-with-agent-assist
supersedes: none
related:
  - "../plan.md (the planned drills for each phase)"
  - "RB-001-build-a-phase.md (Step 11 and Decision D2 send you here)"
  - "../templates/drill-report.md"
---

# RB-002 Run a debug drill

> **Read this box first if something feels wrong.**
>
> - **Stop conditions:**
>   1. The investigation needs a TPP system, profile or data. Stop; this project never touches TPP.
>   2. A `drill/*` branch has been merged into `main`. Stop and go to R2, because a planted bug is now in the real code.
>   3. Time spent has reached twice the budget. Take the full answer (hint level H4), then still finish Steps 7–9.
> - **Escalate to:** the hint ladder, section 10.
> - **Safe state:** `main` checked out at its last green commit, with the drill branch kept for reference.

## 1. Purpose and scope

- **Purpose:** find the root cause of a failure with a disciplined method and the tools a production engineer uses, without being handed the answer, so that troubleshooting becomes a habit rather than luck.
- **In scope:** the planted drills plan.md lists for each phase; real bugs found while building (RB-001, D2); extra practice drills on request.
- **Out of scope:** redesigning a component after a drill exposes a design flaw. That goes back through RB-001, Step 4.
- **Success looks like:** a root cause stated as a mechanism, a regression test that fails before the fix and passes after it, and a finished report.

## 2. Triggers

| # | Trigger | How it reaches you | First action |
|---|---|---|---|
| T1 | A planned drill | RB-001, Step 11 | Step 1 |
| T2 | A real bug during a build | RB-001, Decision D2 | Step 2. No planting needed; investigate on `main`, in the slice's uncommitted work (decision #22) |
| T3 | Akash wants extra practice | Ask Claude for a "surprise drill" on any finished phase | Step 1 |

**Do not use this runbook when** the cause is already known. That's an ordinary fix in RB-001, Step 7.

## 3. Prerequisites

| Kind | Requirement | How to verify you have it |
|---|---|---|
| State | `main` is clean and green | `git status` is clean, and the full check passes |
| Inputs | The symptom, a reproduce command and a time budget | Given by Claude at Step 1 |
| Tools | The phase's tools, from the toolbox in section 12 | Each runs: `--version` or a trial run |
| Time | The whole budget is free | A drill interrupted halfway loses its observations |

**Roles.** The **drill master** [A] plants the fault on a branch, states the symptom the way a user would report it, answers factual questions about the setup ("is Redis running?"), and gives hints only when asked. The **investigator** [H] does everything else.

## 4. Risks and safety notes

| Risk | When it bites | Control built into this runbook |
|---|---|---|
| A planted bug reaches `main` | Step 9 | Drill branches are never merged. Only the regression test moves to `main`, by cherry-pick |
| Reading the answer key | Any time | Don't diff the drill branch against `main`, and don't read the planting commit. Doing so turns a drill into reading |
| Guessing and editing code at random | Steps 3–6 | Observe before hypothesizing, and change one thing at a time |
| A "fix" that hides the symptom but not the cause | Step 8 | The regression test has to fail for the stated reason before the fix (Step 7) |

**Irreversible actions:** none.

## 5. Overview

1. Set up (Steps 1–2)
2. Observe and locate (Steps 3–4)
3. Hypothesize and test (Steps 5–6, Decision D1)
4. Prove and fix (Steps 7–8)
5. Report and close (Step 9, then verification V1–V4)

## 6. Procedure

### Step 1 — Plant the fault

- **Executor:** [A]
- **Action:** Create the branch `drill/pN-<name>` from `main`. Plant the fault, or set up the condition: load, a killed process, a network fault. Commit it with the message `drill setup`, so the commit message gives nothing away. Then state three things in chat and nothing more: the symptom as a user would report it, the command that reproduces it, and the time budget.
- **Expected result:** Akash has the symptom, the reproduce command and the budget.
- **If not:** ask for whichever is missing.

### Step 2 — Reproduce

- **Executor:** [H]
- **Action:** Start a timer. Run the reproduce command and see the symptom for yourself. Copy [templates/drill-report.md](../templates/drill-report.md) to `drills/<name>.md` in the phase's work folder.
- **Expected result:** you have seen the symptom.
- **If not:** ask the drill master for the exact environment. That's a factual question, not a hint. A bug you can't reproduce is a bug you can't prove you've fixed.

### Step 3 — Observe before guessing

- **Executor:** [H]
- **Action:** Collect facts without changing any code: the full error output, logs, test output, state (database rows, book contents, queue lengths) and timings. Then narrow it down: when does it happen, and when doesn't it? Try one client against many, one symbol against many, idle against loaded. Write everything under **Observations**.
- **Expected result:** at least three observations, including at least one of the form "it does not happen when…".
- **If not:** you're missing visibility. Add logging or a breakpoint (which only observes, so it doesn't count as a change), then repeat this step.

### Step 4 — Locate

- **Executor:** [H]
- **Action:** Find the smallest area the fault can be in: which component, which function. Use stack traces, timestamps in the logs, breakpoints, and shrinking the input until the bug only just still happens.
- **Expected result:** one sentence in the report, of the form "the fault is in X, because observation Y".
- **If not:** if two areas remain equally likely, keep both and carry them into Step 5.

### Step 5 — Hypothesize

- **Executor:** [H]
- **Action:** Write at least two hypotheses about the mechanism, meaning how the fault produces the symptom. For each one, write the cheapest test that would prove it wrong: a log line, a breakpoint, a smaller input, or a targeted unit test.
- **Expected result:** the **Hypotheses** table has two or more rows, each with a disproof test.
- **If not:** if you can only think of one hypothesis, ask "what else would produce exactly these observations?" If nothing comes, that's E1 (hint level H1).

### Step 6 — Test the hypotheses, cheapest first

- **Executor:** [H]
- **Action:** Run each disproof test and record the result in the table. Change one thing at a time, and undo each experiment before running the next.
- **Expected result:** exactly one hypothesis survives, and it explains every observation from Step 3.
- **If not:** go to D1.

### Step 7 — Write the regression test first

- **Executor:** [H] (Claude helps with syntax on request, per RB-001 E4)
- **Action:** Write a test that fails *because of* the fault, and run it on the drill branch.
- **Expected result:** the test fails, and its failure message matches the mechanism you identified.
- **If not:** the test doesn't capture the fault. Go back to Step 5, because your mechanism may be wrong.

### Step 8 — Fix

- **Executor:** [H] for small fixes; [A→H] for large ones
- **Action:** Describe the fix in words in the report first. Then implement it: Akash for small fixes, Claude for large ones once Akash approves the description. Run the full check.
- **Expected result:** the regression test passes and the full check is green.
- **If not:** the fix is wrong or incomplete. Go to Step 6.

### Step 9 — Report and close

- **Executor:** [H], then [A]
- **Action:** Finish the report: the root cause as a mechanism in two or three sentences, how you found it, time to root cause, hints used, the regression test, and how production would catch this (a metric, an alert, a log line, or a design change that makes it impossible). Then switch to `main`. For a planted drill, cherry-pick only the regression-test commit onto `main`. For a real bug (T2) you're already on `main`, and the fix goes in through RB-001 as part of the slice in progress (decision #22).
- **Expected result:** the report is complete, `main` has the new test, and the full check on `main` is green.
- **If not:** if the cherry-pick conflicts, Claude resolves it in a way that keeps only the test.

## 7. Decision points

### D1 — After testing the hypotheses

| Observation | Meaning | Go to |
|---|---|---|
| One hypothesis survives and explains every observation | Root cause found | Step 7 |
| One survives but leaves an observation unexplained | Partial answer, maybe two faults | Step 3, focusing on the unexplained observation |
| None survives | Data is missing | Step 3: add instrumentation and observe again |
| The time budget has passed | Stuck | Section 10, next hint level |

## 8. Verification

| # | Check | Pass criterion | Executor |
|---|---|---|---|
| V1 | The regression test proves the fault | It fails on the drill branch before the fix and passes after | [A] |
| V2 | The root cause is a mechanism, not a location | It reads like "an `await` inside the match loop lets a second order read the book before the first order's fill is applied", not "a bug in matching.py" | [A] reviews |
| V3 | The score is recorded | Time to root cause and hints used are in the report | [H] |
| V4 | `main` is safe | `main` is green with the new test, and the drill branch is unmerged | [A] |

- **Declare the drill done only when** V1–V4 pass.
- **Completion actions:** add a row to the execution log below, and link the report from the work README.

## 9. Rollback and recovery

### R1 — Abandon the drill

- **Use when:** the drill can't continue, for example because the environment is broken for reasons unrelated to the drill.
- **Authority needed:** Akash.
- **Steps:**
  1. Run `git switch main`. → Expected: a clean tree, the drill branch kept.
  2. Note in the report why the drill was abandoned. → Expected: one line.
- **Verify rollback:** the full check on `main` passes.

### R2 — A drill branch was merged into `main`

- **Use when:** stop condition 2.
- **Authority needed:** Akash.
- **Steps:**
  1. Find the merge commit with `git log --merges -5`. → Expected: the drill merge is listed.
  2. Revert it with `git revert -m 1 <merge-sha>`. → Expected: a new commit that undoes the drill.
- **Verify rollback:** the full check on `main` passes, and the planted fault's reproduce command no longer shows the symptom on `main`.

## 10. Escalation — the hint ladder

Ask for hints one level at a time. Each level gives away a little more.

| Level | Ask when | The drill master gives |
|---|---|---|
| H1 | The budget has passed, or 20 minutes have gone by with no new observation | **Where to look:** the component, or the kind of tool that would show it |
| H2 | 15 minutes after H1 | **What to observe:** the specific measurement or experiment that exposes the fault |
| H3 | 15 minutes after H2 | **The mechanism, as a question**, for example "what can another task do while this one is awaiting?" |
| H4 | 15 minutes after H3, or at twice the budget | **The full answer** with an explanation. Steps 7–9 still happen |

The number of hints used is your score, and it should fall as the project goes on. Record it honestly, because a falling score is the evidence for learning outcome LO8.

## 11. Glossary

Terms used here are defined in [glossary.md](../glossary.md).

## 12. Debugging toolbox

| Tool | Use it to | First phase |
|---|---|---|
| `pytest -x -vv` | Stop at the first failure and show full detail | P0 |
| `breakpoint()`, or the VS Code debugger | Pause execution and inspect live state | P0 |
| Structured logging (one event per line, with fields) | Correlate what happened, and when, across tasks | P0 |
| asyncio debug mode (`PYTHONASYNCIODEBUG=1`) | Log callbacks that block the event loop for too long | P0 |
| Hypothesis | Find the smallest input that breaks an invariant | P1 |
| `psql`, with the `pg_stat_activity` and `pg_locks` views | See running queries and who is waiting on which lock | P2 |
| `redis-cli` (`MONITOR`, `XINFO`, `XPENDING`) | Watch traffic, and inspect streams and unacknowledged messages | P3, P5 |
| py-spy (`top`, `dump`, `record`) | See where a running process spends its time, without restarting it | P6 |
| Trace viewer (OpenTelemetry backend) | Follow one order across services | P6 |
| Toxiproxy | Inject latency, drops and partitions between services | P7 |
| `git bisect` | Find the commit that introduced a real bug | any |

## 13. Change log

| Version | Date | Author (role) | Change | Reviewed by (role) |
|---|---|---|---|---|
| 1.0.0 | 2026-10-13 | Claude (implementer) | Initial version | Akash (owner), pending |

## 14. Execution log

| Date | Drill | Budget | Time to root cause | Hints used | Notes |
|---|---|---|---|---|---|
| | | | | | |
