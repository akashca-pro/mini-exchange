# mini-exchange

A small stock exchange, built to learn Python, FastAPI and system design by doing. Traders send buy and sell orders over an API. A matching engine pairs them, money and shares move between accounts, and prices stream live to every connected client.

The exchange is how we learn, not what we're aiming for. The goal is for Akash to design, build, troubleshoot and explain concurrent, real-time, correctness-critical systems, which are the core skills of a senior engineer and architect with infrastructure depth. Claude writes most of the code, so the project is organised around understanding rather than output. Akash designs each phase before any code exists, predicts before running, explains every slice back, and debugs planted failures without being given the answer.

## Owner

Akash · repo `C:\Users\AkashAnilChembarathi\personal\mini-exchange` (moved from `~\projects\` on 2026-10-13, decision #18) · GitHub `akashca-pro/mini-exchange` · opened 2026-10-13

## Status

`active` — 2026-10-13. Runbook written, no code yet, nothing committed. P0 (foundations) is next. The machine has Python 3.13.12 and 3.14.5, Docker 29.6.1 on WSL2 and git 2.54. **uv is not installed, and P0 needs it.** Decisions #5–#12 in [decisions.md](runbook/decisions.md) are Claude's proposals until Akash confirms them, except #10, which #18 superseded. Hard rules H1 (never touch TPP) and H2 (personal GitHub only) are in [CLAUDE.md](CLAUDE.md). The personal git identity, the SSH deploy key and the GitHub repo are set up, and SSH to GitHub works (decisions #16–#20). The repo now lives in `~/personal/`, and the personal git hooks are verified in a real commit.

The Claude Code guard blocks tool calls as designed since the session 3 fix (decision #21). Before it, Windows PowerShell turned the guard's "block" exit code into one Claude Code treats as "allow" ([bug folder](runbook/work/2026-10-13_bug-guard-not-firing/README.md), now `done`). The fix was verified in the session that applied it and again in a fresh session (session 4).

## How it works

The system grows in eight phases. Each phase adds one kind of problem the previous design can't handle, so every phase starts by finding where the last design falls short:

```
P0 foundations → P1 matching → P2 money → P3 real-time → P4 recovery → P5 distributed → P6 performance → P7 resilience + cloud
```

At the end of P5 the system looks like this. P6 and P7 add measurement, fault handling and the cloud deploy around the same shape:

```
 clients ─ REST ─▶ gateway          auth · idempotency · reserves funds in Postgres
    ▲                 │
    │                 ▼ commands, keyed by symbol
    │              stream
    │                 ▼
    │            engine × N         one task owns each order book · event log
    │                 ▼ events
    │              stream
    │        ┌────────┼─────────────┐
    │        ▼        ▼             ▼
    │   settlement  market data   order status
    │   (ledger)        │
    └─── WebSocket ─────┘
```

[design.md](runbook/design.md) explains why each piece sits where it does and how the shape grows phase by phase.

Every phase runs the same loop, written as runbook [RB-001](runbook/procedures/RB-001-build-a-phase.md):

1. Akash writes a one-page design and Claude reviews it.
2. Claude builds it in small slices. Before each slice Akash predicts the outcome, and after it Akash explains the slice back.
3. Akash runs the phase's debug drills ([RB-002](runbook/procedures/RB-002-run-a-debug-drill.md)).
4. The exit gate checks two things: the code works, and Akash can explain it without notes.

## Next

1. Add the remote `git@github.com:akashca-pro/mini-exchange.git`, make the first commit (Akash approves the message, RB-001 Step 10) and push. Decide at that point whether slices go straight to `main` or through a branch and PR (decision #11). From then on, Akash does PRs, merges and CI in the browser (decision #17).
2. Finish the decision walkthrough: read [requirements.md](runbook/requirements.md), [design.md](runbook/design.md) and [plan.md](runbook/plan.md), then confirm or change #5–#12 one at a time. #5 (one writer per order book) was explained in session 2 and awaits Akash's answer.
3. Install uv: `winget install --id=astral-sh.uv -e`.
4. Start P0 with [RB-001](runbook/procedures/RB-001-build-a-phase.md) Step 1. The workflow skills (`/review-design`, `/slice`, `/drill`) are added during P0, each just before it's first needed.

## Files

| File | What you'd learn there |
|---|---|
| [runbook/requirements.md](runbook/requirements.md) | The learning outcomes, what the exchange must do, the invariants that must never break, performance targets |
| [runbook/design.md](runbook/design.md) | Target architecture and why, how it grows per phase, domain model, matching and ledger rules, open questions each phase design must answer |
| [runbook/plan.md](runbook/plan.md) | The eight phases: concepts, what gets built, the hand-written piece, drills, exit gates, estimates |
| [runbook/decisions.md](runbook/decisions.md) | Why one project not many, why a single writer per book, why integers for money, why Redis before Kafka |
| [runbook/procedures/RB-001-build-a-phase.md](runbook/procedures/RB-001-build-a-phase.md) | The step-by-step loop for building a phase, with its decision points and exit checks |
| [runbook/procedures/RB-002-run-a-debug-drill.md](runbook/procedures/RB-002-run-a-debug-drill.md) | How a debug drill runs, the hint ladder, and the debugging toolbox |
| [runbook/glossary.md](runbook/glossary.md) | Trading terms and system-design terms in plain English |
| [runbook/work/](runbook/work/README.md) | One folder per phase, feature, research question or bug, and how to open one |
| [runbook/templates/](runbook/templates/) | Blank phase design, drill report and work-folder README |
| [CLAUDE.md](CLAUDE.md) | Rules for Claude here: teaching mode, no TPP access, which file to update when |
| [runbook/changelog.md](runbook/changelog.md) | Dated history, newest first |
