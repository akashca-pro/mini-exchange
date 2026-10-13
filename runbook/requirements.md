# Requirements

This file covers what the project has to achieve, what the exchange must do, and how we'll know. The phase numbers (P0–P7) say when each requirement arrives, and [plan.md](plan.md) holds the phase order and gates. Each phase's work-folder design cites requirements by ID, such as `FR-3` or `I2`.

## Learning outcomes

The project succeeds when Akash can do these without Claude. The exchange working is required, but on its own it isn't enough.

| ID | Akash can… | Evidence | Phases |
|---|---|---|---|
| LO1 | Read, write and debug async Python services built on FastAPI | Hand-written piece in every phase passes review | all |
| LO2 | Pick between a single writer, locks, database transactions and partitioning for a given contention problem, and defend the choice | P1, P2 and P5 designs and drills | P1, P2, P5 |
| LO3 | Design a live data feed with fan-out, backpressure and gap recovery | P3 design and drills | P3 |
| LO4 | Make in-memory state survive crashes, using event sourcing, snapshots and deterministic replay | P4 crash tests | P4 |
| LO5 | Reason about partitioning, ordering, delivery guarantees, idempotent consumers and the outbox pattern | P5 design, drills and ADR | P5 |
| LO6 | Estimate capacity, load test, profile, and fix the actual bottleneck | P6 performance report | P6 |
| LO7 | Make a system survive faults (timeouts, retries, circuit breakers, rate limits) and run it on AWS from code | P7 drills and deploy | P7 |
| LO8 | Find a root cause methodically, using fewer hints over time | Hint scores across all drill reports | all |
| LO9 | Explain an architecture and its trade-offs: written designs, ADRs, and a 30-minute whiteboard walkthrough of the exchange including failure modes | Final walkthrough at P7 exit | all |

## Functional requirements

| ID | The exchange must… | Phase |
|---|---|---|
| FR-1 | Accept a limit order: symbol, side (buy or sell), price, quantity, and a client order ID. Reject it if the price is off the tick grid, the quantity is not positive, or the symbol is unknown | P1 |
| FR-2 | Accept a market order: fill it against the best prices available now and cancel any unfilled remainder, so a market order never rests on the book | P1 |
| FR-3 | Match by price-time priority: better price first, and at equal price, earlier order first. The trade happens at the resting order's price. Partial fills are allowed | P1 |
| FR-4 | Cancel a resting order. Only the account that placed it can cancel it (ownership arrives with accounts in P2) | P1, P2 |
| FR-5 | Answer queries for order status, book depth (top N price levels per side) and recent trades per symbol | P1 |
| FR-6 | Hold accounts that authenticate with an API key. Support fake-cash deposits and share issuance, and show balances split into available and reserved | P2 |
| FR-7 | Accept an order only if the account can cover its worst case: cash for a buy, owned shares for a sell (no short selling). Reserve that amount until the order fills or is canceled | P2 |
| FR-8 | Settle each trade atomically in a double-entry ledger: the buyer pays cash and the seller delivers shares. Release unused reservation on cancel, on a fill at a better price, and on a market order's remainder | P2 |
| FR-9 | Treat submission as idempotent: the same client order ID from the same account returns the original result and never creates a second order | P2 |
| FR-10 | Publish a public market-data stream per symbol over WebSocket: a full book snapshot, then numbered incremental updates, plus a trade feed | P3 |
| FR-11 | Publish a private stream per account carrying its own order updates and fills | P3 |
| FR-12 | Recover from a crash to the exact pre-crash state, losing no acknowledged order | P4 |
| FR-13 | Trade many symbols, each matched independently, spread over several engine processes | P5 |
| FR-14 | Run simulated traders (bots) that generate realistic order flow on demand | P6 |
| FR-15 | Rate-limit order submission per account | P7 |
| FR-16 | Halt trading in a symbol when its price moves more than a set percentage within a time window, and resume after a cool-down (stretch) | P7 |

## Invariants

These must never be false. Property-based tests (Hypothesis) generate thousands of random order sequences and check them after every one. An invariant violation is always a bug, never a known issue to live with.

| ID | Invariant | Phase |
|---|---|---|
| I1 | **Cash conservation:** total cash across all accounts, available plus reserved, equals total deposits | P2 |
| I2 | **Share conservation:** total shares of each symbol across all accounts equals total issuance | P2 |
| I3 | **Never crossed:** once a command is fully processed, best bid < best ask | P1 |
| I4 | **Price-time priority:** a resting order never fills while another order on the same side is still resting with a better price, or with the same price and an earlier arrival | P1 |
| I5 | **No overfill:** for every order, filled + remaining + canceled = original quantity | P1 |
| I6 | **No negative balances:** available cash and available shares never go below zero | P2 |
| I7 | **Idempotency:** one client order ID per account produces at most one order | P2 |
| I8 | **Determinism:** replaying the same command log produces identical state | P4 |
| I9 | **Feed consistency:** a client that applies the snapshot plus every update in sequence holds the same book as the engine | P3 |

## Performance and operational targets

The numbers are first guesses. The first real measurement replaces each guess, and comparing guess to measurement is part of LO6. Every target is measured on this laptop until P7.

| ID | Target | Phase |
|---|---|---|
| NFR-1 | Engine alone, in-process, single symbol: ≥ 10,000 orders/s | P1 |
| NFR-2 | End to end over HTTP: order acknowledgement p99 ≤ 50 ms at a steady 500 orders/s | P6 |
| NFR-3 | Market data: an update reaches a WebSocket client at p99 ≤ 100 ms, and one slow client never delays the others | P3 |
| NFR-4 | Recovery: a `kill -9` at any moment loses no acknowledged order, and restart is ready in ≤ 10 s with 1 million events in the log | P4 |
| NFR-5 | Traceability: one ID follows any order end to end across every service | P6 |
| NFR-6 | Reproducibility: one command starts everything and one command runs every test | P0 onward |
| NFR-7 | Cost: AWS spend stays inside a budget set at P7 entry, with an alarm, and the whole stack is destroyed with one command | P7 |

## Constraints

- Everything runs on one Windows 11 laptop with Docker Desktop until P7.
- The language is Python with FastAPI (decision #2).
- Only fake money and generated orders. No real market data, brokers or regulation.
- The cloud is a personal AWS account only, never a TPP account or profile ([CLAUDE.md](../CLAUDE.md) rule 5).

## Out of scope

- Real money, identity checks (KYC), regulatory reporting.
- Short selling, margin, options and other derivatives.
- Microsecond latency, kernel bypass, special hardware.
- Multi-region or active-active deployment.
- A full trading UI. P3 may add a minimal page that shows the live book, only so the feed can be watched.
