# Glossary

Plain-English meanings as used in this project. When a project introduces a term, add it here.

## How we work

| Term | Meaning |
|---|---|
| Project | One unit of work (a phase, feature, bug or research question) with its own dated folder under `runbook/projects/` |
| Master project (`00-master`) | The one project that never closes. It holds the overall status, the roadmap and the index of every other project |
| Phase | One step of the P0–P7 roadmap. Each phase is delivered as one project |
| Slice | One small change inside a project: about 150 changed lines or fewer plus tests, ending green and committed |
| Green | Every test, lint and type check passes |
| Exit gate | The checks a phase must pass before the next phase starts. The roadmap lists them |

## Trading terms

| Term | Meaning |
|---|---|
| Order | An instruction to buy or sell a quantity of a symbol |
| Symbol (ticker) | The identifier of what's traded, such as AAPL |
| Bid | A buy order resting on the book. The best bid is the highest one |
| Ask (offer) | A sell order resting on the book. The best ask is the lowest one |
| Spread | Best ask minus best bid |
| Limit order | Buy or sell at this price or better. Whatever doesn't fill straight away rests on the book |
| Market order | Buy or sell now at whatever prices are available. It never rests on the book |
| Order book | All resting limit orders for one symbol, arranged by side and price |
| Price level | All resting orders at one price, queued in arrival order |
| Depth | How much quantity rests at each price level. "Top N" means the N best levels per side |
| Price-time priority | Better price fills first. At equal price, the earlier order fills first |
| Maker | The resting order in a trade. It "made" the liquidity by waiting on the book |
| Taker | The incoming order that matched against resting orders |
| Fill, partial fill | Execution of all, or part, of an order's quantity |
| Trade | One match between a buy and a sell, at one price and quantity |
| Tick size | The smallest allowed price step, such as one cent |
| Lot size | The smallest allowed quantity step, such as one share |
| Crossed book | Best bid ≥ best ask. A correct engine never leaves a book like this after matching |
| Self-trade | An account's buy matching its own sell |
| Reservation (hold) | Cash or shares set aside for an open order so they can't be spent twice |
| Settlement | Moving cash and shares between accounts after a trade |
| Issuance | Creating shares of a symbol in an account. In this project it's an admin action used for setup |
| Trading halt | Pausing a symbol after an extreme price move. Markets call it a circuit breaker, a different thing from the software circuit breaker below |

## System terms

| Term | Meaning |
|---|---|
| Event loop | asyncio's scheduler. It runs one coroutine at a time, and switches only at an `await` |
| Coroutine | A running `async def` function. It can pause at `await` and resume later |
| Blocking call | A call that holds the thread while it waits (such as `time.sleep` or a synchronous database driver), which freezes every coroutine on the event loop |
| Single-writer principle | One task owns a piece of state, and everything else sends it messages instead of touching the state directly |
| Race condition | A bug whose outcome depends on the timing of concurrent operations |
| Transaction | A group of database changes that all happen or none happen |
| Isolation level | How much concurrent transactions can see of each other's uncommitted or recent work |
| Row lock (`SELECT … FOR UPDATE`) | Locks the selected rows until the transaction ends, so concurrent writers wait in line |
| Deadlock | Two transactions each waiting on a lock the other holds. The database kills one of them |
| Idempotency key | A client-chosen ID that makes a retried request return the first result instead of acting twice |
| Double-entry ledger | Every movement is recorded as entries that sum to zero, so value can't appear or vanish |
| Fan-out | Sending one message to many receivers |
| Backpressure | A slow receiver pushing back on the sender, so queues don't grow without limit |
| Conflation | Merging several pending updates into one, so a slow receiver gets the latest state instead of the full history |
| Sequence number, gap | A counter on every message. A gap (seeing #57 right after #55) means a message was lost |
| Snapshot | A full copy of state at one sequence number, so you don't have to replay from the beginning |
| Event sourcing | Storing the sequence of changes as the source of truth, and deriving state by replaying them |
| Write-ahead log (WAL) | Writing a change to a durable log before applying it, so a crash can be recovered from |
| fsync | Forcing written data from the operating system's cache onto the disk. Until then, a power cut can lose it |
| Determinism | The same inputs always produce the same outputs, which replay depends on |
| Partition, partition key | One slice of a stream. Messages with the same key (here, the symbol) always go to the same partition, which keeps them in order |
| Consumer group | A set of consumers sharing one stream, where each message goes to one member of the group |
| At-least-once delivery | Every message arrives, but some may arrive twice. Consumers have to be idempotent |
| Exactly-once effect | Each message changes state exactly once, achieved by at-least-once delivery plus an idempotent consumer |
| Idempotent consumer | A consumer that records what it has processed, so a redelivered message changes nothing |
| Outbox pattern | Writing an outgoing message into the same database transaction as the state change, and publishing it afterwards, which avoids the dual-write problem |
| Dual write | Updating two systems (such as a database and a stream) without a shared transaction, so one can succeed while the other fails |
| Eventual consistency | Different parts of the system briefly disagree but converge once events are processed |
| p50, p99 | The latency that 50% (or 99%) of requests come in under. p99 shows the slow tail that averages hide |
| Throughput | How many operations per second the system completes |
| Profiling | Measuring where a program spends its time |
| Trace, span | A trace follows one request across services. A span is one timed step within it |
| RED method | For a service: Rate, Errors, Duration |
| USE method | For a resource: Utilization, Saturation, Errors |
| Timeout | The longest you'll wait for a call before giving up |
| Backoff, jitter | Waiting longer between each retry (backoff), with randomness added (jitter) so clients don't all retry at the same moment |
| Circuit breaker (software) | Stops calling a failing dependency for a while, so it can recover instead of being overwhelmed by retries |
| Token bucket | A rate limiter: a bucket refills with tokens at a fixed rate, and each request spends one |
| Graceful shutdown | Stop taking new work, finish the work in flight, then exit |
| Chaos testing | Deliberately injecting faults to prove the system survives them |
| Fail closed, fail open | What a safety check does when it breaks. Fail closed blocks everything, like a firewall that denies by default. Fail open lets everything through. A guard should fail closed, so a bug in the check costs convenience rather than safety |
| ADR | Architecture decision record: the context, the options, the choice and its trade-off. Here, rows in decisions.md |
