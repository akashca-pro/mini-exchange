# Design

How the exchange works at its target shape, and how it gets there phase by phase. This file holds the architecture. Each phase's detailed design is Akash's one-pager in its work folder, which links back here. The open questions at the bottom are left open on purpose, because answering them is the phase design's job.

## Target architecture

This is the shape at the end of P5. P6 adds measurement around it and P7 adds fault handling and the cloud deploy; neither changes the shape.

```
 clients (bots, test clients)
    │ REST: place, cancel, query
    ▼
 ┌─────────────────────────────────┐
 │ gateway (FastAPI)               │  auth · validation · idempotency · rate limit
 │                                 │  reserves funds in Postgres before forwarding
 └───────────────┬─────────────────┘
                 │ commands, keyed by symbol
                 ▼
 ┌─────────────────────────────────┐
 │ command stream (Redis Streams)  │
 └───────┬─────────────────┬───────┘
         ▼                 ▼
 ┌───────────────┐ ┌───────────────┐
 │ engine A      │ │ engine B      │  one task owns each order book:
 │ AAPL, MSFT    │ │ TSLA, NVDA    │  log the command, apply it, emit events
 └───────┬───────┘ └───────┬───────┘
         └────────┬────────┘
                  ▼ events: accepted, trade, canceled, book delta
 ┌─────────────────────────────────┐
 │ event stream (Redis Streams)    │
 └────┬───────────┬────────────┬───┘
      ▼           ▼            ▼
 settlement   market data   order status
 ledger in    WebSocket     read model for
 Postgres     to clients    GET /orders
```

The reasons behind the shape:

- **One writer per order book.** A single asyncio task owns each book and commands queue up in front of it. Matching needs no locks, and the order of events is exactly the order of the queue, which P4's replay depends on. Capacity grows by spreading symbols across more engines, not by adding threads to one book. Real exchanges work the same way; the LMAX architecture is the well-known write-up (decision #5).
- **Money in Postgres, the book in memory.** Money needs transactions, so it lives in a database. The book needs speed, so it lives in memory, and the P4 event log is what makes memory recoverable (decision #7).
- **Funds are reserved before matching.** The gateway reserves funds in Postgres before the command reaches the engine. Otherwise the engine would need a database round trip inside its hot loop to ask "can this account pay?", and every other order on that symbol would wait behind it.
- **Everything after the engine consumes events.** Settlement, market data and order status can each fall behind or restart without stopping matching. The price is eventual consistency: an order can show as filled a few milliseconds before the balances do. Living with that trade-off is the core of P5.

## How the design grows

| Phase | What's added | Shape at the end of the phase |
|---|---|---|
| P0 | Project skeleton | One FastAPI process with a health endpoint. Postgres and Redis run in Docker Compose but nothing uses them yet |
| P1 | Order book and matching | One process: API → `asyncio.Queue` → engine task. Everything lives in memory and is lost on restart |
| P2 | Accounts and ledger | Adds Postgres. Funds are reserved in the request path, and settlement runs in-process after each trade |
| P3 | Market data | WebSocket fan-out in the same process, with a bounded queue per client and numbered updates |
| P4 | Event log | The engine logs each command before applying it. Periodic snapshots, and replay at startup |
| P5 | Services and streams | Split into gateway, engine × N, settlement, market data and order status, connected by Redis Streams |
| P6 | Load and observability | Bots, load tests, traces across services, metrics dashboards |
| P7 | Resilience and cloud | Network-fault injection, timeouts, retries, rate limits, graceful shutdown, then deployment to AWS from Terraform |

## Domain model

All prices are integer ticks and all cash is integer cents (decision #6). With a tick of one cent, $101.00 is stored as `10100`.

| Entity | Key fields | Notes |
|---|---|---|
| Symbol | ticker, tick size, lot size | For example AAPL, tick 1 cent, lot 1 share |
| Order | id, client order ID, account, symbol, side, type (limit or market), price, quantity, filled, status, sequence number | Market orders carry no price |
| Trade | id, symbol, price, quantity, maker order, taker order, sequence number | Price is always the maker's (resting order's) price |
| Account | id, API key hash | Arrives in P2 |
| Ledger entry | transaction ID, account, asset (USD or a symbol), bucket (available or reserved), amount (signed integer) | Each transaction's entries sum to zero per asset |
| Event | sequence number, type, payload | Arrives in P4. The log is the source of truth for the book |

An order moves through these states:

```
NEW ─▶ REJECTED                              validation or funds check failed
NEW ─▶ ACCEPTED ─▶ PARTIALLY_FILLED ─▶ FILLED
          │               │
          └───────────────┴──▶ CANCELED      user cancel, or a market order's remainder
```

## Matching rules

Each symbol's book has two sides. Bids (buys) are sorted from the highest price down, and asks (sells) from the lowest price up. Each price level is a first-in, first-out queue.

An incoming buy keeps matching while the best ask is at or below its limit (a market buy accepts any price). Sells mirror this. Each match trades the smaller of the two remaining quantities at the resting order's price. Whatever is left of a limit order rests at its price, at the back of that level's queue. Whatever is left of a market order is canceled.

Example. The asks are A (5 @ $101, arrived first), B (3 @ $101), and C (10 @ $102). A buy limit for 10 @ $101 arrives:

1. It fills 5 with A at $101, and A leaves the book.
2. It fills 3 with B at $101, and B leaves the book.
3. The next ask is $102, above the limit, so matching stops.
4. The remaining 2 rest as a bid at $101.

The book is now best bid $101 × 2 and best ask $102 × 10, which is not crossed (I3).

## Ledger rules

Every account holds each asset (USD and each symbol) in two buckets, available and reserved. Every movement is a transaction whose entries sum to zero per asset, so money and shares cannot appear or vanish (invariants I1 and I2). Balances are sums of entries, never a number that gets overwritten.

Example: Alice buys 10 AAPL at $150.00 from Bob. Amounts are in cents and shares.

| Moment | Entry | Amount |
|---|---|---|
| Bob's sell is accepted | Bob AAPL available | −10 |
| | Bob AAPL reserved | +10 |
| Alice's buy is accepted | Alice USD available | −150000 |
| | Alice USD reserved | +150000 |
| The trade settles | Alice USD reserved | −150000 |
| | Bob USD available | +150000 |
| | Bob AAPL reserved | −10 |
| | Alice AAPL available | +10 |

## Open questions for the phase designs

Each phase design answers its own set, or says "don't know, because…". A wrong answer that gets reviewed teaches more than a blank.

**P1**

- Q1.1 Which data structures give fast best-price lookup, first-in-first-out order within a price level, and fast cancel by order ID? What does each operation cost?
- Q1.2 Why one engine task with a queue rather than a lock around the book? What exactly breaks with two tasks?
- Q1.3 What does a market order do when the opposite side is empty?
- Q1.4 Should an account be able to trade with itself? If not, which of its two orders gets canceled?
- Q1.5 The engine runs in a different task from the HTTP request. How does the request get the engine's result back?

**P2**

- Q2.1 How do you reserve funds for a market buy, which has no price?
- Q2.2 Reserve funds before the engine sees the order, or after? What goes wrong each way?
- Q2.3 Which isolation level, and which rows get locked, so that 50 concurrent orders cannot overdraw one account?
- Q2.4 Where is the idempotency key stored and enforced? What does a retry get back while the first attempt is still in flight?
- Q2.5 A buy limit at $101 fills at $100. What happens to the extra reserved cash, and when?

**P3**

- Q3.1 A client receives update #57 right after #55. What does it do?
- Q3.2 One client's connection is slow. Drop it, buffer for it without limit, or send it fewer, merged updates (conflation)? What does each cost?
- Q3.3 How does a new subscriber get a snapshot that lines up exactly with the update stream?

**P4**

- Q4.1 Write a command to the log before applying it, or after? What does each choice lose in a crash?
- Q4.2 What must the engine never do, so that replay gives identical results? Think about clocks, random IDs and set iteration order.
- Q4.3 How often should the engine snapshot, and how do you know a snapshot isn't corrupt?
- Q4.4 At what moment is an order "acknowledged" to the client, and what exactly does that promise?

**P5**

- Q5.1 How do you keep per-symbol order on a stream that several consumers read?
- Q5.2 The stream delivers each message at least once. How does settlement avoid applying a trade twice?
- Q5.3 The gateway writes a reservation to Postgres and publishes a command to Redis. One succeeds and the other fails. Now what?
- Q5.4 How do you move a symbol from engine A to engine B without losing or duplicating orders?

**P6**

- Q6.1 Before measuring anything: what is your estimate of the maximum orders per second, and where will the bottleneck be? Write it down, and compare after.
- Q6.2 What's the difference between average, p50 and p99 latency, and why does an exchange care most about p99?

**P7**

- Q7.1 Which calls need timeouts, with what values, and what happens when one fires?
- Q7.2 How do retries turn a small outage into a big one, and what stops that?
- Q7.3 What is the smallest AWS footprint that runs the whole system, and what does it cost per day?
