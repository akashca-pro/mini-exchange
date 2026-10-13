# mini-exchange

A small stock exchange in Python and FastAPI. Traders send buy and sell orders over an API. A matching engine pairs them, money and shares move between accounts, and prices stream live to every connected client.

## Owner

Akash · repo `C:\Users\AkashAnilChembarathi\personal\mini-exchange` (moved from `~\projects\` on 2026-10-13, decision #18) · GitHub `akashca-pro/mini-exchange` · opened 2026-10-13

## Status

`active` — 2026-10-13. Before P0: the runbook is written and committed, and no code exists yet. The full state, the roadmap and every project are in the master project, [00-master](runbook/projects/00-master/README.md).

## How we work

Work runs as projects (decision #24):

- **[00-master](runbook/projects/00-master/README.md)** never closes. It holds where things stand, the P0–P7 roadmap, the index of every project, and what's next.
- **Every phase, feature, bug or research question** gets a dated folder under [runbook/projects/](runbook/projects/README.md), such as `2026-10-20_p0-foundations` or `2026-10-13_bug-guard-not-firing`.
- **Every project follows [RB-001](runbook/procedures/RB-001-deliver-a-project.md).** Claude drafts the design and Akash approves it. Claude then builds it in small slices, each ending green and committed straight to `main`, and Akash approves every commit (decisions #23 and #25).

## How it works

The system grows in eight phases, and each phase adds one kind of problem the previous design can't handle:

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

## Files

| File | What's there |
|---|---|
| [runbook/projects/00-master/](runbook/projects/00-master/README.md) | Where things stand, the roadmap, every project, what's next |
| [runbook/projects/](runbook/projects/README.md) | How projects work: kinds, folder names, what a folder holds |
| [runbook/requirements.md](runbook/requirements.md) | What the exchange must do, the invariants that must never break, performance targets |
| [runbook/design.md](runbook/design.md) | Target architecture and why, how it grows per phase, domain model, matching and ledger rules, open questions each phase design must answer |
| [runbook/decisions.md](runbook/decisions.md) | Every decision and its reason: one project, a single writer per book, integers for money, Redis before Kafka |
| [runbook/procedures/RB-001-deliver-a-project.md](runbook/procedures/RB-001-deliver-a-project.md) | Step by step: open, design, approve, build, verify and close a project |
| [runbook/glossary.md](runbook/glossary.md) | Trading terms and system-design terms in plain English |
| [runbook/templates/](runbook/templates/) | Blank project README and project design |
| [CLAUDE.md](CLAUDE.md) | Rules for Claude here: hard rules, approvals, which file to update when |
| [runbook/changelog.md](runbook/changelog.md) | Dated history, newest first |
