# Roadmap — phases and gates

mini-exchange grows in eight phases, and each one adds one kind of problem. Each phase is delivered as one project through [RB-001](../../procedures/RB-001-deliver-a-project.md), and ends at its exit gate. The next phase doesn't start until that gate passes, because each phase builds on the last one. Phase status lives in the [00-master](README.md) **Roadmap** table.

```
P0 foundations → P1 matching → P2 money → P3 real-time → P4 recovery → P5 distributed → P6 performance → P7 resilience + cloud
```

The hour estimates below are guesses that add up to 130–170 hours. They were made when every phase also included teaching steps and debug drills, which decision #23 removed, so they are likely high. Each phase project records its actual hours in its **Outcome**, so later estimates get better.

## How to read a phase

Each phase lists the same five things:

| Item | What it means |
|---|---|
| **Goal** | What the system can do at the end that it couldn't before |
| **Techniques** | What the design has to get right. The glossary defines each term |
| **Build** | What gets implemented |
| **Exit gate** | Checks that must pass, on top of RB-001's verification (section 8) |
| **Estimate** | Hours, as a guess |

## P0 — Foundations

- **Goal:** a working Python toolchain and project skeleton.
- **Techniques:** Python types and type hints; dataclasses vs Pydantic models; modules and packages; virtual environments with uv; `async`/`await` and the event loop; FastAPI routes and dependency injection; pytest.
- **Build:** the repo layout, `pyproject.toml`, a FastAPI app with `/health`, one test, ruff and mypy, and a Compose file with Postgres and Redis. Also the commands in [CLAUDE.md](../../../CLAUDE.md) **Commands**, and a check that every planned dependency installs on Python 3.14 (decision #9).
- **Exit gate:**
  - One command runs the tests and they pass.
  - `docker compose up` brings Postgres and Redis up healthy.
  - `/health` returns 200.
- **Estimate:** 6–10 h.

## P1 — Order book and matching engine

- **Goal:** an in-memory exchange that matches orders correctly by price-time priority behind a REST API.
- **Techniques:** order book data structures and their cost (Big-O); the single-writer principle; `asyncio.Queue` and futures; property-based testing; micro-benchmarking.
- **Build:** domain models, the order book, the matching engine, the engine task and its queue, endpoints for FR-1 to FR-5, Hypothesis tests for I3–I5, and an in-process benchmark.
- **Exit gate:**
  - FR-1 to FR-5 have passing tests.
  - Hypothesis finds no violation of I3–I5 across 10,000 examples.
  - The benchmark result is recorded against NFR-1.
- **Estimate:** 15–20 h.

## P2 — Accounts, ledger, money

- **Goal:** real accounts whose money can never be created, lost or spent twice.
- **Techniques:** ACID transactions; isolation levels; row locks (`SELECT … FOR UPDATE`); idempotency keys; double-entry bookkeeping; async database access (SQLAlchemy 2.0 with asyncpg); migrations (Alembic).
- **Build:** schema and migrations, accounts with API-key auth, deposits and share issuance, reservation in the request path, settlement, idempotent submission, and a reconciliation query that checks I1 and I2.
- **Exit gate:**
  - FR-6 to FR-9 have passing tests.
  - A test with 50 parallel orders never overdraws.
  - Reconciliation passes after a random 10,000-order run.
  - The idempotency test passes.
- **Estimate:** 20–25 h.

## P3 — Real-time market data

- **Goal:** clients see the book and trades live, and a slow or flaky client can't hurt anyone else.
- **Techniques:** WebSockets; publish/subscribe fan-out; backpressure; bounded queues; sequence numbers; snapshot plus deltas; conflation.
- **Build:** book-delta events from the engine; a per-symbol publisher; public and private WebSocket endpoints; a bounded queue per client; sequence numbers and the snapshot handshake; a client library that detects gaps and resyncs. Optionally, a minimal HTML page that shows the live book.
- **Exit gate:**
  - FR-10 and FR-11 have passing tests.
  - A test client's book matches the engine's after a random run (I9).
  - Other clients' latency is unaffected by a deliberately slow client.
  - NFR-3 is measured.
- **Estimate:** 15–20 h.

## P4 — Event log and recovery

- **Goal:** kill the exchange at any instant and bring it back exactly as it was.
- **Techniques:** write-ahead logging; event sourcing; fsync and what "durable" really means; snapshots; deterministic replay; checksums.
- **Build:** an append-only command log (whether it lives in a file or in Postgres is the P4 design's call); log-before-apply; periodic snapshots; replay at startup; a written "acknowledged" contract.
- **Exit gate:**
  - FR-12 has passing tests.
  - A replay test proves I8.
  - A crash test with 100 random kill points loses no acknowledged order.
  - NFR-4 is measured.
- **Estimate:** 15–20 h.

## P5 — Services and streams

- **Goal:** split the single process into services connected by streams, and run many symbols across several engines.
- **Techniques:** partitioning by key; per-key ordering; consumer groups; at-least-once delivery vs exactly-once effects; idempotent consumers; the outbox pattern; eventual consistency; where to draw service boundaries.
- **Build:** gateway, engines (N instances, each assigned a set of symbols), settlement, market-data and order-status services as separate processes; Redis Streams between them; an outbox table in the gateway; an idempotent settlement consumer; Compose for the whole set.
- **Exit gate:**
  - FR-13 has passing tests.
  - I1, I2 and I7 hold across a random run with service restarts injected.
  - Per-symbol ordering is verified.
  - The choice of Redis Streams over Kafka is recorded as a decision (ADR) in decisions.md.
- **Estimate:** 25–30 h.

## P6 — Load, observability, performance

- **Goal:** know how fast the system is and where the time goes, then fix the actual bottleneck.
- **Techniques:** capacity estimation; load testing (open vs closed workload models); latency percentiles; distributed tracing; metrics (the RED and USE methods); profiling.
- **Build:** trading bots (FR-14); Locust scenarios; OpenTelemetry traces across services; Prometheus metrics and a Grafana dashboard; profiling runs with py-spy; a performance report.
- **Exit gate:**
  - The Q6.1 estimate is written down before the first load test.
  - NFR-2 and NFR-5 are measured.
  - One bottleneck is found by profiling and fixed, with before and after numbers.
- **Estimate:** 15–20 h.

## P7 — Resilience and cloud

- **Goal:** the system survives faults and runs on AWS from code.
- **Techniques:** timeouts; retries with backoff and jitter; circuit breakers; rate limiting (token bucket); graceful shutdown; health checks; chaos testing; infrastructure as code; cost control.
- **Entry prerequisites:** a personal AWS account, its own CLI profile and a budget alarm, all in place before the first `terraform apply` (hard rule H1 in [CLAUDE.md](../../../CLAUDE.md)).
- **Build:** Toxiproxy fault scenarios (the gateway-to-stream network partitioned, a retry storm after a brief outage, a deploy in the middle of in-flight orders); timeouts and retries on every network call; the rate limit (FR-15); graceful shutdown; the trading halt (FR-16, stretch); Terraform for the smallest AWS footprint that runs the system (Q7.3).
- **Exit gate:**
  - Every fault scenario runs with no invariant broken.
  - The stack deploys and destroys with one command each.
  - Spend stays inside budget.
- **Estimate:** 20–25 h.

## After P7

**Stretch features**, in any order, each opened as a `feat-` project:

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
