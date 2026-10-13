---
runbook_id: RB-001
title: "Build one phase of mini-exchange"
version: 1.0.0
status: active
owner: "Akash (learner and project owner)"
owner_contact: "this repo"
last_reviewed: 2026-10-13
review_by: 2026-12-31            # or at the P1 retro, whichever comes first
last_executed: never
audience: "Akash, with Claude as implementer. Assumes beginner Python and strong infrastructure experience."
estimated_duration: "6 to 30 hours per phase, over several sessions (per-phase estimates in plan.md)"
executor_mode: human-with-agent-assist
supersedes: none
related:
  - "../plan.md (what each phase builds, and its exit gate)"
  - "../requirements.md (the IDs a design cites)"
  - "../design.md (architecture and each phase's open questions)"
  - "RB-002-run-a-debug-drill.md (used at Step 11)"
---

# RB-001 Build one phase of mini-exchange

> **Read this box first if something feels wrong.**
>
> - **Stop conditions:**
>   1. A command would use a `tpp-*` AWS profile, a TPP repo or TPP data. Stop at once; this project never touches TPP.
>   2. A slice's tests are still red after two fix attempts. Go to D2.
>   3. Akash can't explain the previous slice. Don't build on top of it, because the gap in understanding grows with every slice that follows. Go to E1.
> - **Escalate to:** section 10, E1–E4.
> - **Safe state:** the last green commit is checked out, tests pass, and the work folder's `progress.md` records where you stopped.

## 1. Purpose and scope

- **Purpose:** turn one phase of [plan.md](../plan.md) into working, tested code that Akash understands well enough to explain and debug without Claude.
- **In scope:** the primer, Akash's design and its review, the slice plan, the build loop, the hand-written piece, the drills, the exit gate, and the documentation updates.
- **Out of scope:** choosing which phase is next (plan.md fixes the order); how a drill runs ([RB-002](RB-002-run-a-debug-drill.md)); research questions that need answering before a design is possible (a `research-` folder, see [work/README.md](../work/README.md)).
- **Success looks like:** every check in section 8 passes, and plan.md shows the phase as `complete`.

## 2. Triggers

| # | Trigger | How it reaches you | First action |
|---|---|---|---|
| T1 | The previous phase's gate passed, or the project is starting (P0) | plan.md status table | Step 1 |
| T2 | Resuming a phase after a break | The work folder's README **Status** and `progress.md` | Re-read both, then go to the step `progress.md` records |
| T3 | A stretch feature is picked after P7 | plan.md **After P7** | Step 1, treating the feature as a small phase in a `feat-` folder |

**Do not use this runbook when** you're chasing a bug (use RB-002), or when you need to learn how something works before you can design with it, such as "how does Kafka guarantee ordering?" (open a `research-` work folder).

## 3. Prerequisites

| Kind | Requirement | How to verify you have it |
|---|---|---|
| Tools | uv, Python 3.14, Docker Desktop running, git | `uv --version`, `uv run python --version`, `docker info`, `git --version` (P0 installs uv, so P0 itself starts without it) |
| State | The previous phase is complete | plan.md status table shows `complete` for it |
| State | Working tree clean | `git status` reports nothing to commit |
| Inputs | This phase's section in plan.md, and its open questions in design.md | Read both |
| Time | A block of one to two hours | A slice shouldn't be split across two sessions |

## 4. Risks and safety notes

| Risk | When it bites | Control built into this runbook |
|---|---|---|
| The code works but Akash can't explain it | Every slice | The predict step (6), the teach-back step (9), and the oral check (V4) |
| The phase grows extra features | Step 5 onward | The slice plan is approved up front. New ideas go to the work folder's **Next**, not into this phase |
| A large change that can't be debugged | Step 7 | The slice size limit, and a commit after every green slice |
| TPP AWS profiles or accounts get used | P7 | Stop condition 1 and [CLAUDE.md](../../CLAUDE.md) rule 5 |
| AWS spend runs on | P7 | Budget alarm before the first apply. R2 at the end of every P7 session |

**Irreversible actions:** none locally, because git keeps every committed state. In P7, `terraform apply` and `terraform destroy` against the personal AWS account are tagged `[A→H]`: Claude prepares the plan, and Akash reads it and runs the command.

## 5. Overview

1. Open the phase (Steps 1–2)
2. Design (Steps 3–4, Decision D1)
3. Plan the slices (Step 5)
4. Build loop, once per slice (Steps 6–10, Decision D2)
5. Drills (Step 11, through RB-002)
6. Close the phase (Steps 12–14, then verification V1–V6)

## 6. Procedure

### Step 1 — Open the work folder

- **Executor:** [A]
- **Action:** Create `runbook/work/YYYY-MM-DD_pN-<name>/`. It holds `README.md` from [templates/work-readme.md](../templates/work-readme.md), `design.md` from [templates/phase-design.md](../templates/phase-design.md), and empty `progress.md` and `teach-back.md` files, plus a `drills/` folder. Add the folder to the [work index](../work/README.md). Set the phase to `active` in plan.md, with a link to the folder.
- **Expected result:** the folder exists, and both plan.md and the work index link to it.
- **If not:** fix the path and retry.

### Step 2 — Write the primer

- **Executor:** [A]
- **Action:** In the work README, write a primer of one page or less. It covers each concept listed for the phase in plan.md: what problem it solves, a minimal runnable example, and one or two links for further reading.
- **Expected result:** Akash can name each concept and say in one sentence what problem it solves.
- **If not:** E1, for the concept that didn't land.

### Step 3 — Write the design

- **Executor:** [H]
- **Action:** Fill in the work folder's `design.md` from the template. Answer every one of this phase's open questions from design.md, or write "don't know, because…". List at least three failure modes. Time-box the design to two hours, and write it badly rather than not at all.
- **Expected result:** every template section has content, and every open question for the phase has an answer or a reason why not.
- **If not:** if you're stuck on one section for more than 30 minutes, go to E1. Ask Claude about the concept, not for the answer.

### Step 4 — Review the design

- **Executor:** [A→H]
- **Action:** Claude reviews `design.md` and fills in its **Review** table, ranking each finding as one of:
  - **blocking:** it breaks a requirement or an invariant;
  - **important:** it works, but will cost later;
  - **learning:** another way to do it, worth knowing.

  Claude does not rewrite the design. Akash responds in the table, revises the design, then goes to D1.
- **Expected result:** the review table is filled in and every finding has a response.
- **If not:** go to D1.

### Step 5 — Plan the slices

- **Executor:** [A→H]
- **Action:** Claude splits the design into three to eight slices and writes them as a table in `progress.md`. Each slice covers one concept and about 150 changed lines or fewer plus tests, ends with green tests, and names the test that proves it. One slice is marked as Akash's hand-written piece (plan.md names it). Akash approves the table or reorders it.
- **Expected result:** `progress.md` holds the approved slice table, every row marked `todo`.
- **If not:** if the design won't split into eight slices or fewer, the phase is too big. Go to E3.

### Step 6 — Predict

- **Executor:** [H]
- **Action:** Before slice N is built, write three lines in `progress.md`: the code shape you expect (functions, classes, where they go), what its test will check, and one thing you think could go wrong.
- **Expected result:** three lines, written before any code exists.
- **If not:** don't skip this step. The prediction is most useful when it turns out wrong.

### Step 7 — Build the slice

- **Executor:** [A], or [H] for the hand-written slice
- **Action:**
  - **For Claude's slices:** Claude writes the code and its tests, then explains in chat what each part does, why it has this shape, the alternative and why we didn't take it, and which primer concept it shows.
  - **For the hand-written slice:** Akash writes it, asking Claude for syntax help as needed (E4). Claude then reviews it the way a senior engineer would, correctness first and readability second, without rewriting it.
- **Expected result:** the full check from [CLAUDE.md](../../CLAUDE.md) **Commands** passes: tests, lint and types.
- **If not:** one fix attempt. If it's still red, go to D2.

### Step 8 — Compare with the prediction

- **Executor:** [H]
- **Action:** In `progress.md`, set the result against the Step 6 prediction. Write each difference down, and why it happened.
- **Expected result:** a "surprises" line for this slice, even if it reads "none".
- **If not:** —

### Step 9 — Teach it back

- **Executor:** [H], then [A]
- **Action:** In `teach-back.md`, Akash explains the slice in three to six sentences, in their own words and without copying code: what it does, why it's built this way, and what would break without it. Claude then marks it correct or lists up to three corrections, and Akash rewrites the parts that were wrong.
- **Expected result:** the entry is marked correct.
- **If not:** stop condition 3. Claude re-explains with a different example (E1), then Akash writes the entry again.

### Step 10 — Commit

- **Executor:** [A→H]
- **Action:** Claude proposes a commit message in the form `pN sK: <what changed>`, Akash approves it, and the commit is made. Mark the slice `done` in `progress.md`.
- **Expected result:** `git log -1` shows the commit and `git status` is clean.
- **If not:** fix and retry. Then go to Step 6 for the next slice, or to Step 11 once every slice is done.

### Step 11 — Run the drills

- **Executor:** [H], with Claude as drill master
- **Action:** Run each drill that plan.md lists for this phase, through [RB-002](RB-002-run-a-debug-drill.md).
- **Expected result:** each drill has a finished report in the work folder's `drills/`.
- **If not:** RB-002 has its own escalation, the hint ladder.

### Step 12 — Record the decisions

- **Executor:** [A→H]
- **Action:** For every choice in this phase where a reasonable engineer could have chosen differently, Akash drafts a row in [decisions.md](../decisions.md) and Claude reviews it.
- **Expected result:** at least one new decision row for the phase.
- **If not:** if nothing seems worth recording, ask Claude what the alternatives were for the three biggest choices. There is always at least one.

### Step 13 — Update the docs

- **Executor:** [A]
- **Action:** Update [design.md](../design.md) wherever the built system differs from it, add any new command to [CLAUDE.md](../../CLAUDE.md), and then, once V1–V6 pass, mark the phase `complete` in plan.md, update the README **Status**, and add a [changelog.md](../changelog.md) entry.
- **Expected result:** a reader of README.md alone knows where the project stands.
- **If not:** —

### Step 14 — Retro

- **Executor:** [H]
- **Action:** Write the **Retro** section of the work README: what was hard, what surprised you, the hints used across all drills, and estimated vs actual hours.
- **Expected result:** the retro is filled in.
- **If not:** —

## 7. Decision points

### D1 — Is the design ready to build?

| Observation | Meaning | Go to |
|---|---|---|
| No blocking findings | Ready | Step 5 |
| Blocking findings, and Akash understands why each one blocks | Revise | Step 3, changing only the affected sections |
| A blocking finding Akash still doesn't understand after one explanation | Concept gap | E1, then Step 3 |
| A third review round still has blocking findings | The design is too big | E3 |

### D2 — A slice's tests are still red after one fix attempt

| Observation | Meaning | Go to |
|---|---|---|
| The failure is in the slice's new code, and the cause is understood | Ordinary fix | Step 7 |
| The failure is in existing code that the slice touched | A real bug | Run it as a live drill: RB-002 trigger T2, with Akash investigating |
| The cause is still unknown after 30 minutes | The slice is too big | R1, split the slice, Step 5 |
| An assumption in the design is wrong | Design bug | Record it in the work folder's `design.md`, then Step 4 |

## 8. Verification

| # | Check | Pass criterion | Executor |
|---|---|---|---|
| V1 | Code health | The full check passes: tests, lint, types | [A] |
| V2 | Invariants | Hypothesis tests for this phase's invariant IDs pass across at least 10,000 examples | [A] |
| V3 | Requirements covered | Each of the phase's FR IDs has a passing test, and each NFR ID has a recorded measurement | [A] |
| V4 | Akash understands it | Claude asks five questions about the phase, including at least one "what happens if…", and Akash answers at least four correctly without notes | [A] asks, [H] answers |
| V5 | Drills done | Every planned drill has a report that states a root cause | [H] |
| V6 | Hand-written piece | Akash's slice is reviewed and committed, with green tests | [H] |

- **Declare the phase complete only when** V1–V6 all pass, plus the phase's own exit gate in plan.md.
- **Completion actions:** Step 13's status updates and Step 14's retro.

## 9. Rollback and recovery

### R1 — Abandon a slice

- **Use when:** D2 says the slice is too big, or the slice has turned into a mess.
- **Authority needed:** Akash.
- **Steps:**
  1. Run `git stash` to keep the work for later reading, or `git restore .` to throw it away. → Expected: `git status` is clean, at the last green commit.
  2. In `progress.md`, write why the slice was abandoned. → Expected: one line.
  3. Re-split it at Step 5.
- **Verify rollback:** the full check passes.
- **Cannot roll back if:** locally, it always can. AWS resources aren't covered by git; use R2 for those.

### R2 — Tear down cloud resources (P7 only)

- **Use when:** at the end of every P7 session, or when the budget alarm fires.
- **Authority needed:** Akash.
- **Steps:**
  1. Confirm the active AWS profile is the personal one, not `tpp-*`. → Expected: `aws sts get-caller-identity` shows the personal account ID.
  2. Run `terraform destroy` for the stack. → Expected: "Destroy complete!"
- **Verify rollback:** the next day, the AWS billing console shows no running resources.
- **Cannot roll back if:** —

## 10. Escalation and contacts

| Level | Escalate when | Who | How | Response |
|---|---|---|---|---|
| E1 | Stuck on a concept for more than 30 minutes, or a teach-back fails | Claude | In chat: "explain X with a different example" | Immediate |
| E2 | Stuck in a drill past its time budget | The hint ladder | [RB-002](RB-002-run-a-debug-drill.md), section 10 | One level at a time |
| E3 | The phase is at twice its estimate, or a third design review still has blocking findings | Akash decides, with Claude | Cut stretch parts or split the phase, then record a decision | Same session |
| E4 | Stuck on Python syntax or tooling rather than the concept | Claude | Ask directly. Learning time is for concepts, not fighting tools | Immediate |

**When you ask for help, say:** what you were doing, what you expected, what happened instead, what you tried, and what you think is going on.

## 11. Glossary

Terms used here are defined in [glossary.md](../glossary.md).

## 12. Change log

| Version | Date | Author (role) | Change | Reviewed by (role) |
|---|---|---|---|---|
| 1.0.0 | 2026-10-13 | Claude (implementer) | Initial version | Akash (owner), pending |

## 13. Execution log

| Phase | Started | Finished | Outcome | Hours (estimate → actual) | Deviations and notes |
|---|---|---|---|---|---|
| | | | | | |
