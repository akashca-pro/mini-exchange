---
runbook_id: RB-001
title: "Deliver a mini-exchange project"
version: 2.0.0
status: active
owner: "Akash (project owner)"
owner_contact: "this repo"
last_reviewed: 2026-10-13
review_by: 2026-12-31            # or when the P0 project closes, whichever comes first
last_executed: never
audience: "Akash, who approves, and Claude, who designs and implements."
estimated_duration: "From an hour for a small bug to 30 hours for a phase (phase estimates in roadmap.md)"
executor_mode: human-with-agent-assist
supersedes: "RB-001 v1.0.0 (Build one phase) and RB-002 v1.0.0 (Run a debug drill), per decision #23"
related:
  - "../projects/README.md (kinds of project, folder names, what a folder holds)"
  - "../projects/00-master/README.md (overall status, roadmap table, project index)"
  - "../projects/00-master/roadmap.md (each phase's scope and exit gate)"
  - "../requirements.md (the IDs a design cites)"
  - "../design.md (architecture and each phase's open questions)"
---

# RB-001 Deliver a mini-exchange project

> **Read this box first if something feels wrong.**
>
> - **Stop conditions:**
>   1. A command would use a `tpp-*` AWS profile, a TPP repo or TPP data. Stop at once; this project never touches TPP (hard rule H1 in [CLAUDE.md](../../CLAUDE.md)).
>   2. Code is about to be written for a project whose design Akash hasn't approved. Stop and go to Step 3.
>   3. A slice's tests are still red after two fix attempts. Go to D2.
> - **Escalate to:** section 10, E1–E2.
> - **Safe state:** the last green commit is checked out, tests pass, and the project's `progress.md` records where you stopped.

## 1. Purpose and scope

- **Purpose:** take one project (a phase, feature, bug or research question) from opening to done, with an approved design, small green commits and up-to-date docs.
- **In scope:** opening the folder, the design and its approval, the slice plan, the build loop, verification, decisions, and closing the project.
- **Out of scope:** choosing what comes next. The roadmap fixes the phase order, and Akash sets priorities in the [00-master](../projects/00-master/README.md) **Next** list.
- **Success looks like:** every check in section 8 passes, and the project shows `done` in its README and in the 00-master **Projects** index.

How each kind of project uses this runbook:

| Kind | Design (Step 2) lives in | Steps used |
|---|---|---|
| Phase, feature | `design.md`, from [templates/project-design.md](../templates/project-design.md) | All |
| Bug | The README: symptom, **Root cause**, proposed fix | All. A one-slice fix has a one-row slice table |
| Research | The README: question, sources, **What we found**, a proposed decisions.md row | 1–3, then 8–9. Akash's approval at Step 3 accepts the finding |

## 2. Triggers

| # | Trigger | How it reaches you | First action |
|---|---|---|---|
| T1 | A phase's turn comes: the previous phase is complete, or the project is starting (P0) | 00-master **Roadmap** table | Step 1 |
| T2 | Akash picks up a feature or a stretch item | 00-master **Next** | Step 1 |
| T3 | A bug turns up that doesn't belong to a slice in progress | A failing test, an error, or Akash reporting it | Step 1, as a `bug-` project |
| T4 | Resuming a project after a break | The project README **Status** and `progress.md` | Re-read both, then go to the step `progress.md` records |

## 3. Prerequisites

| Kind | Requirement | How to verify you have it |
|---|---|---|
| Tools | uv, Python 3.14, Docker Desktop running, git | `uv --version`, `uv run python --version`, `docker info`, `git --version` (P0 installs uv, so P0 itself starts without it) |
| State | For a phase: the previous phase is complete | The 00-master **Roadmap** table shows `complete` for it |
| State | Working tree clean | `git status` reports nothing to commit |
| Inputs | For a phase: its section in [roadmap.md](../projects/00-master/roadmap.md), and its open questions in [design.md](../design.md) | Read both |

## 4. Risks and safety notes

| Risk | When it bites | Control built into this runbook |
|---|---|---|
| Code gets written against a design nobody approved | Step 4 onward | Stop condition 2. Step 3 is Akash's approval |
| The project grows extra features | Step 4 onward | The slice plan is approved up front. New ideas go to the 00-master **Next** list or a new project, not into this one |
| A large change that can't be debugged | Step 5 | The slice size limit, and a commit after every green slice |
| TPP AWS profiles or accounts get used | P7 | Stop condition 1 and hard rule H1 |
| AWS spend runs on | P7 | Budget alarm before the first apply. R2 at the end of every P7 session |

**Irreversible actions:** none locally, because git keeps every committed state. In P7, `terraform apply` and `terraform destroy` against the personal AWS account are tagged `[A→H]`: Claude prepares the plan, and Akash reads it and runs the command.

## 5. Overview

1. Open the project (Step 1)
2. Design and approval (Steps 2–3, Decision D1)
3. Plan the slices (Step 4)
4. Build loop, once per slice (Steps 5–6, Decision D2)
5. Verify and close (Steps 7–9, then verification V1–V4)

## 6. Procedure

### Step 1 — Open the project folder

- **Executor:** [A]
- **Action:** Create `runbook/projects/YYYY-MM-DD_<kind>-<name>/`, named as [projects/README.md](../projects/README.md) describes, with `README.md` from [templates/project-readme.md](../templates/project-readme.md). A phase or feature project also gets `design.md` from [templates/project-design.md](../templates/project-design.md) and an empty `progress.md`. Add the project to the 00-master **Projects** index. For a phase, set it `active` in the 00-master **Roadmap** table, with a link to the folder.
- **Expected result:** the folder exists, and 00-master links to it.
- **If not:** fix the path and retry.

### Step 2 — Draft the design

- **Executor:** [A]
- **Action:** Fill in `design.md` from the template, or the README for a bug or research project (section 1 says which). For a phase, answer every open question design.md lists for it, and show how the design meets the phase's exit gate in roadmap.md. List at least three failure modes and the alternatives considered. Mark anything unverified with `[CONFIRM]` and say how it will be settled.
- **Expected result:** every template section has content, and every open question has an answer or a `[CONFIRM]`.
- **If not:** if a question can't be answered without investigating first, open a `research-` project (Step 1) and set this one to `blocked` until it's answered.

### Step 3 — Approve the design

- **Executor:** [A→H]
- **Action:** Claude summarises the design in chat: what it builds, the main choice and the alternative it beat, and the risks. Akash approves it or asks for changes. Claude records the answer in the design's **Approval** table, with the date.
- **Expected result:** the **Approval** table's last row says `approved`.
- **If not:** go to D1.

### Step 4 — Plan the slices

- **Executor:** [A→H]
- **Action:** Claude splits the design into slices and writes them as a table in `progress.md`. Each slice covers one change, about 150 changed lines or fewer plus tests, ends with green tests, and names the test that proves it. Akash approves the table or reorders it.
- **Expected result:** `progress.md` holds the approved slice table, every row marked `todo`.
- **If not:** if the design won't split into eight slices or fewer, the project is too big. Go to E1.

### Step 5 — Build the slice

- **Executor:** [A]
- **Action:** Claude writes the code and its tests, then runs the full check from [CLAUDE.md](../../CLAUDE.md) **Commands**: tests, lint and types. Then a short summary in chat: what changed, and anything that differs from the design.
- **Expected result:** the full check passes.
- **If not:** one fix attempt. If it's still red, go to D2.

### Step 6 — Commit

- **Executor:** [A→H]
- **Action:** Claude proposes a commit message in the form `<project> sK: <what changed>`, for example `p1 s3: cancel by order ID` or `bug-guard s1: map every non-zero exit to block`. Once Akash approves it, Claude commits straight to `main` (decision #25) and pushes. Mark the slice `done` in `progress.md`, with the commit hash.
- **Expected result:** `git log -1` shows the commit, `git status` is clean, and `git status -sb` shows `main` level with `origin/main`.
- **If not:** fix and retry. Then go to Step 5 for the next slice, or to Step 7 once every slice is done.

### Step 7 — Verify

- **Executor:** [A]
- **Action:** Run the checks in section 8. For a phase, also run its exit gate from roadmap.md.
- **Expected result:** every check passes.
- **If not:** each failing check becomes a new slice. Add it to the table in `progress.md`, get Akash's approval, and go to Step 5.

### Step 8 — Record the decisions

- **Executor:** [A→H]
- **Action:** For every choice in this project where a reasonable engineer could have chosen differently, Claude drafts a row in [decisions.md](../decisions.md) and Akash approves it.
- **Expected result:** a phase or feature project adds at least one row. A bug or research project adds one when it changed or settled a design choice.
- **If not:** if nothing seems worth recording, list the alternatives behind the three biggest choices. There is almost always one worth a row.

### Step 9 — Close the project

- **Executor:** [A]
- **Action:** Update [design.md](../design.md) wherever the built system differs from it, and add any new command to [CLAUDE.md](../../CLAUDE.md) **Commands**. Set the project README's **Status** to `done`, saying what was delivered; for a phase or feature, fill in **Outcome** with estimated and actual hours. Then update 00-master: the project's row in **Projects**, the phase's row in **Roadmap** (`complete`), **Status** and **Next**. Add a [changelog.md](../changelog.md) entry.
- **Expected result:** a reader of 00-master alone knows where the project stands.
- **If not:** —

## 7. Decision points

### D1 — Akash's answer on the design

| Observation | Meaning | Go to |
|---|---|---|
| Approved | Ready to build | Step 4 |
| Changes requested | Revise | Step 2, changing only the affected sections, then Step 3 |
| A third round still has changes requested | The design is too big, or the goal is unclear | E1 |

### D2 — A slice's tests are still red after one fix attempt

| Observation | Meaning | Go to |
|---|---|---|
| The failure is in the slice's new code, and the cause is understood | Ordinary fix | Step 5 |
| The failure is in existing code that the slice touched | A real bug | Open a `bug-` project (trigger T3). This slice waits, marked `blocked` in `progress.md` |
| The cause is still unknown after 30 minutes | The slice is too big | R1, split the slice, Step 4 |
| An assumption in the design is wrong | Design bug | Record it in `design.md`, then Step 3 for re-approval |

## 8. Verification

| # | Check | Pass criterion | Executor |
|---|---|---|---|
| V1 | Code health | The full check passes: tests, lint, types | [A] |
| V2 | Invariants | Hypothesis tests for every invariant ID the design cites pass across at least 10,000 examples | [A] |
| V3 | Requirements covered | Each FR ID the design cites has a passing test, and each NFR ID has a recorded measurement | [A] |
| V4 | Accepted | Akash accepts the result. For a phase, its exit gate in roadmap.md passes | [H] |

- **Declare the project done only when** V1–V4 all pass. V2 and V3 apply only when the design cites invariant or requirement IDs.
- **Completion actions:** Step 9.

## 9. Rollback and recovery

### R1 — Abandon a slice

- **Use when:** D2 says the slice is too big, or the slice has turned into a mess.
- **Authority needed:** Akash.
- **Steps:**
  1. Run `git stash` to keep the work for later reading, or `git restore .` to throw it away. → Expected: `git status` is clean, at the last green commit.
  2. In `progress.md`, write why the slice was abandoned. → Expected: one line.
  3. Re-split it at Step 4.
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
| E1 | The project is at twice its estimate, a third design round still has changes requested, or the design won't split into eight slices | Akash decides, with Claude | Cut scope or split into more projects, then record a decision | Same session |
| E2 | Blocked on something only Akash can do or decide: an account, a credential, a priority | Akash | Claude stops, says in chat exactly what's needed, and sets the project `blocked` | When Akash is back |

**When you report a problem, say:** what you were doing, what you expected, what happened instead, what you tried, and what you think is going on.

## 11. Debugging toolbox

For bug projects, and for D2.

| Tool | Use it to | Useful from |
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
| `git bisect` | Find the commit that introduced a bug | any |

## 12. Glossary

Terms used here are defined in [glossary.md](../glossary.md).

## 13. Change log

| Version | Date | Author (role) | Change | Reviewed by (role) |
|---|---|---|---|---|
| 1.0.0 | 2026-10-13 | Claude (implementer) | Initial version: build one phase, as a learning loop | Akash (owner), pending |
| 2.0.0 | 2026-10-13 | Claude (implementer) | Rewritten to deliver any project. Teaching steps and drills removed; Claude drafts designs, Akash approves; RB-002's debugging toolbox moved here (decisions #23–#25) | Akash (owner), pending |

## 14. Execution log

| Project | Started | Finished | Outcome | Hours (estimate → actual) | Deviations and notes |
|---|---|---|---|---|---|
| | | | | | |
