# 00-master — mini-exchange

The master project. It never closes. It holds the overall state of mini-exchange: where things stand, the P0–P7 roadmap, the index of every project, and what's next. Each project's detail lives in its own folder; this page links to it.

## Owner

Akash · master · covers the whole repo

## Status

`active` — 2026-10-13. Before P0: the runbook is written and committed, and no code exists yet. Work was reorganised into projects on 2026-10-13, with this master project on top (decisions #23–#25).

| Area | State |
|---|---|
| Machine | Python 3.13.12 and 3.14.5, Docker 29.6.1 on WSL2, git 2.54. **uv is not installed, and P0 needs it** |
| Repo | First commit `91223b8` pushed to `akashca-pro/mini-exchange`. Every green slice goes straight to `main` (decision #25) |
| Decisions | #5–#12 are Claude's proposals until Akash confirms them, except #10 (superseded by #18) and #11 (superseded by #25) |
| Hard rules | H1 and H2 in [CLAUDE.md](../../../CLAUDE.md) are enforced by the guard, verified in a fresh session ([bug project](../2026-10-13_bug-guard-not-firing/README.md)) |
| Git identity | The personal identity, SSH deploy key and personal git hooks are verified in a real commit and push (decisions #16–#20). Akash is the only commit author: Claude Code's attribution is off, and a `commit-msg` hook refuses any message crediting someone else (decisions #26–#27) |

## Roadmap

The system grows in eight phases. Each one adds a kind of problem the previous design can't handle, and the next starts only when the previous phase's exit gate passes. Each phase is delivered as one project. [roadmap.md](roadmap.md) holds each phase's goal, scope, exit gate and estimate.

```
P0 foundations → P1 matching → P2 money → P3 real-time → P4 recovery → P5 distributed → P6 performance → P7 resilience + cloud
```

| Phase | Name | Status | Project |
|---|---|---|---|
| P0 | Foundations | not started | — |
| P1 | Order book and matching engine | not started | — |
| P2 | Accounts, ledger, money | not started | — |
| P3 | Real-time market data | not started | — |
| P4 | Event log and recovery | not started | — |
| P5 | Services and streams | not started | — |
| P6 | Load, observability, performance | not started | — |
| P7 | Resilience and cloud | not started | — |

## Projects

Every project, newest first. [projects/README.md](../README.md) explains the kinds and naming.

| Project | Kind | Status |
|---|---|---|
| [2026-10-13_bug-guard-not-firing](../2026-10-13_bug-guard-not-firing/README.md) | Bug | `done`: guard fix verified mid-session and in a fresh session |

## Next

1. Decision walkthrough: read [requirements.md](../../requirements.md), [design.md](../../design.md) and [roadmap.md](roadmap.md), then confirm or change #5–#12 one at a time. #5 (one writer per order book) awaits Akash's answer.
2. Install uv: `winget install --id=astral-sh.uv -e`.
3. Open the P0 project with [RB-001](../../procedures/RB-001-deliver-a-project.md) Step 1.

## Files

| File | What's there |
|---|---|
| [roadmap.md](roadmap.md) | Each phase's goal, scope, exit gate and estimate, and what comes after P7 |
