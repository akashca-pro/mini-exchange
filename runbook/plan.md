# Plan — phases and gates

The project has eight phases, and each one adds one kind of problem. A phase starts with Akash's design and ends at its exit gate. The next phase doesn't start until that gate passes, because each phase builds on the last one, and an unexplained gap carries forward and grows. Every phase runs through [RB-001](procedures/RB-001-build-a-phase.md), and every drill through [RB-002](procedures/RB-002-run-a-debug-drill.md).

```
P0 foundations → P1 matching → P2 money → P3 real-time → P4 recovery → P5 distributed → P6 performance → P7 resilience + cloud
```

## Phase status

| Phase | Name | Status | Work folder |
|---|---|---|---|
| P0 | Foundations | not started | — |
| P1 | Order book and matching engine | not started | — |
| P2 | Accounts, ledger, money | not started | — |
| P3 | Real-time market data | not started | — |
| P4 | Event log and recovery | not started | — |
| P5 | Services and streams | not started | — |
| P6 | Load, observability, performance | not started | — |
| P7 | Resilience and cloud | not started | — |

The hour estimates below are guesses. Each work folder's retro records the actual hours, so later estimates get better. Calibrating estimates against reality is itself part of LO6. The guesses add up to 130–170 hours in total.

## How to read a phase

Each phase lists the same seven things:

| Item | What it means |
|---|---|
| **Goal** | What the system can do at the end that it couldn't before |
| **Concepts** | What Akash learns. Claude's primer covers these in RB-001 Step 2 |
| **Build** | What gets implemented |
| **Hand-written** | The piece Akash types personally, because writing it by hand is how the language sticks |
| **Drills** | Planted failures Akash debugs through RB-002 |
| **Exit gate** | Checks that must pass, on top of RB-001's standard verification |
| **Estimate** | Hours, as a guess |

## P0 — Foundations

- **Goal:** a working Python toolchain and project skeleton, plus enough Python to read what Claude writes.
- **Concepts:** Python types and type hints; dataclasses vs Pydantic models; modules and packages; virtual environments with uv; `async`/`await` and the event loop; FastAPI routes and dependency injection; pytest.
- **Build:** the repo layout, `pyproject.toml`, a FastAPI app with `/health`, one test, ruff and mypy, and a Compose file with Postgres and Redis. Also the commands in [CLAUDE.md](../CLAUDE.md) **Commands**, and a check that every planned dependency installs on Python 3.14 (decision #9).
- **Hand-written:** a small async program in which three coroutines sleep for different times and print, run with `asyncio.gather`. Predict the print order before running it.
- **Drills:**
  - D0.1 The app won't start (planted import problem).
  - D0.2 One blocking call in an async endpoint makes concurrent requests wait in line. Measure it, then explain why.
- **Exit gate:**
  - One command runs the tests and they pass.
  - `docker compose up` brings Postgres and Redis up healthy.
  - `/health` returns 200.
  - Akash explains in their own words what the event loop does when code hits `await`.
- **Estimate:** 6–10 h.

## P1 — Order book and matching engine

- **Goal:** an in-memory exchange that matches orders correctly by price-time priority behind a REST API.
- **Concepts:** order book data structures and their cost (Big-O); the single-writer principle; `asyncio.Queue` and futures; property-based testing; micro-benchmarking.
- **Build:** domain models, the order book, the matching engine, the engine task and its queue, endpoints for FR-1 to FR-5, Hypothesis tests for I3–I5, and an in-process benchmark.
- **Hand-written:** the matching loop.
- **Drills:**
  - D1.1 An `await` inside the matching loop lets two orders interleave, and one resting order gets filled twice.
  - D1.2 Prices stored as floats create a price level that never matches.
- **Exit gate:**
  - FR-1 to FR-5 have passing tests.
  - Hypothesis finds no violation of I3–I5 across 10,000 examples.
  - The benchmark result is recorded against NFR-1.
- **Estimate:** 15–20 h.

## P2 — Accounts, ledger, money

- **Goal:** real accounts whose money can never be created, lost or spent twice.
- **Concepts:** ACID transactions; isolation levels; row locks (`SELECT … FOR UPDATE`); idempotency keys; double-entry bookkeeping; async database access (SQLAlchemy 2.0 with asyncpg); migrations (Alembic).
- **Build:** schema and migrations, accounts with API-key auth, deposits and share issuance, reservation in the request path, settlement, idempotent submission, and a reconciliation query that checks I1 and I2.
- **Hand-written:** the reservation transaction.
- **Drills:**
  - D2.1 Fifty concurrent buys overdraw one account (a read-modify-write race).
  - D2.2 A client retries after a timeout and creates a duplicate order.
  - D2.3 Two transactions lock the same rows in opposite order and deadlock.
- **Exit gate:**
  - FR-6 to FR-9 have passing tests.
  - A test with 50 parallel orders never overdraws.
  - Reconciliation passes after a random 10,000-order run.
  - The idempotency test passes.
- **Estimate:** 20–25 h.

## P3 — Real-time market data

- **Goal:** clients see the book and trades live, and a slow or flaky client can't hurt anyone else.
- **Concepts:** WebSockets; publish/subscribe fan-out; backpressure; bounded queues; sequence numbers; snapshot plus deltas; conflation.
- **Build:** book-delta events from the engine; a per-symbol publisher; public and private WebSocket endpoints; a bounded queue per client; sequence numbers and the snapshot handshake; a client library that detects gaps and resyncs. Optionally, a minimal HTML page that shows the live book.
- **Hand-written:** the client's gap detection and resync.
- **Drills:**
  - D3.1 One slow client stalls the feed for everyone, because sends happen one after another.
  - D3.2 A snapshot taken between two updates makes a client's book drift.
  - D3.3 Memory grows without limit, from an unbounded queue held for a dead client.
- **Exit gate:**
  - FR-10 and FR-11 have passing tests.
  - A test client's book matches the engine's after a random run (I9).
  - Other clients' latency is unaffected by a deliberately slow client.
  - NFR-3 is measured.
- **Estimate:** 15–20 h.

## P4 — Event log and recovery

- **Goal:** kill the exchange at any instant and bring it back exactly as it was.
- **Concepts:** write-ahead logging; event sourcing; fsync and what "durable" really means; snapshots; deterministic replay; checksums.
- **Build:** an append-only command log (whether it lives in a file or in Postgres is the P4 design's call); log-before-apply; periodic snapshots; replay at startup; a written "acknowledged" contract.
- **Hand-written:** replay from the latest snapshot.
- **Drills:**
  - D4.1 `kill -9` in the middle of a trade. Prove the state after restart matches.
  - D4.2 The engine reads the wall clock inside matching, so replay produces different results.
  - D4.3 The last log record was half-written when the process died.
- **Exit gate:**
  - FR-12 has passing tests.
  - A replay test proves I8.
  - A crash test with 100 random kill points loses no acknowledged order.
  - NFR-4 is measured.
- **Estimate:** 15–20 h.

## P5 — Services and streams

- **Goal:** split the single process into services connected by streams, and run many symbols across several engines.
- **Concepts:** partitioning by key; per-key ordering; consumer groups; at-least-once delivery vs exactly-once effects; idempotent consumers; the outbox pattern; eventual consistency; where to draw service boundaries.
- **Build:** gateway, engines (N instances, each assigned a set of symbols), settlement, market-data and order-status services as separate processes; Redis Streams between them; an outbox table in the gateway; an idempotent settlement consumer; Compose for the whole set.
- **Hand-written:** the idempotent settlement consumer.
- **Drills:**
  - D5.1 A consumer restarts, messages are redelivered, and trades settle twice.
  - D5.2 The Redis publish succeeds but the Postgres commit fails, so the engine trades on funds that were never reserved (the dual-write problem).
  - D5.3 Settlement is down for 10 minutes. What do users see, and does it catch up?
- **Exit gate:**
  - FR-13 has passing tests.
  - I1, I2 and I7 hold across a random run with service restarts injected.
  - Per-symbol ordering is verified.
  - Akash writes the ADR on Redis Streams vs Kafka.
- **Estimate:** 25–30 h.

## P6 — Load, observability, performance

- **Goal:** know how fast the system is and where the time goes, then fix the actual bottleneck.
- **Concepts:** capacity estimation; load testing (open vs closed workload models); latency percentiles; distributed tracing; metrics (the RED and USE methods); profiling.
- **Build:** trading bots (FR-14); Locust scenarios; OpenTelemetry traces across services; Prometheus metrics and a Grafana dashboard; profiling runs with py-spy; a performance report.
- **Hand-written:** one bot strategy.
- **Drills:**
  - D6.1 p99 latency spikes under load, because something is blocking the event loop.
  - D6.2 A missing database index makes settlement fall further and further behind.
  - D6.3 The dashboard says healthy while users see errors, because it measures the wrong thing.
- **Exit gate:**
  - The Q6.1 estimate is written down before the first load test.
  - NFR-2 and NFR-5 are measured.
  - One bottleneck is found by profiling and fixed, with before and after numbers.
- **Estimate:** 15–20 h.

## P7 — Resilience and cloud

- **Goal:** the system survives faults and runs on AWS from code.
- **Concepts:** timeouts; retries with backoff and jitter; circuit breakers; rate limiting (token bucket); graceful shutdown; health checks; chaos testing; infrastructure as code; cost control.
- **Entry prerequisites:** a personal AWS account, its own CLI profile and a budget alarm, all in place before the first `terraform apply` ([CLAUDE.md](../CLAUDE.md) rule 5).
- **Build:** Toxiproxy fault scenarios; timeouts and retries on every network call; the rate limit (FR-15); graceful shutdown; the trading halt (FR-16, stretch); Terraform for the smallest AWS footprint that runs the system (Q7.3).
- **Hand-written:** the token-bucket rate limiter.
- **Drills:**
  - D7.1 The network between gateway and stream partitions.
  - D7.2 A retry storm follows a brief outage.
  - D7.3 A deploy kills in-flight orders, because shutdown isn't graceful.
- **Exit gate:**
  - Every drill is survived with no invariant broken.
  - The stack deploys and destroys with one command each.
  - Spend stays inside budget.
  - Akash gives the 30-minute whiteboard walkthrough (LO9).
- **Estimate:** 20–25 h.

## After P7

**Stretch features**, in any order, each opened as a `feat-` work folder:

- Swap Redis Streams for Kafka or Redpanda.
- Stop orders and iceberg orders.
- Fees and maker-taker rebates.
- Run on Kubernetes.
- A real trading UI.
- Drive the bots from public market data.
- Engine failover with leader election, which leads into the Raft project below.

**Follow-on projects**, each in its own repo with this same runbook layout:

| Project | What it adds |
|---|---|
| Task queue from scratch (a mini Celery or SQS) | Visibility timeouts, retries with backoff, dead-letter queues, leader election for scheduled jobs |
| Flash-sale ticket booking (10,000 users, 100 seats) | Extreme contention, preventing overselling, virtual waiting rooms |
| Ride-hailing dispatcher | Geospatial indexing (geohash or H3), streaming location updates, real-time matching |
| Raft-based key-value store | Consensus, replication, network partitions. The hardest of the four, so it comes last |
