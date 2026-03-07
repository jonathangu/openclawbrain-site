# OpenClawBrain Principal Operator Guide (Canonical Product)

OpenClawBrain is the shipped TypeScript package system for memory, learning, packs, activation state, and deterministic compile behind an OpenClaw-owned runtime boundary.

Operator visuals:
- [Brains dashboard](/docs/brains-dashboard/)

Companion docs:
- setup quickstart: [docs/setup-guide.md](setup-guide.md)
- integration contract: [docs/openclaw-integration.md](openclaw-integration.md)
- operations playbooks: [docs/ops-recipes.md](ops-recipes.md)
- new agent SOP: [docs/new-agent-sop.md](new-agent-sop.md)

## 1) Day-0 bring-up

From the OpenClawBrain TypeScript workspace root:

```bash
corepack enable
pnpm install
pnpm check
pnpm release:pack
```

Promote one versioned pack set into OpenClaw runtime. Do not deploy mixed revisions across core packages.

## 2) Runtime boundary and ownership

OpenClaw owns:
- serving runtime lifecycle
- fail-open behavior
- prompt assembly and request routing
- deployment/canary/rollback controls
- runtime diagnostics

OpenClawBrain owns:
- memory structure and learning policy behavior
- contracts/events/event-export/workspace metadata
- provenance and immutable pack assembly
- activation/promotion/rollback state for pack sets
- deterministic compiler output from active pack state
- learner logic and off-path teacher updates

Keep this boundary explicit in all runbooks and incidents.

## 3) Pack operations: activate, promote, rollback

Operator pack discipline:

1. Build candidate pack set (`pnpm check`, `pnpm release:pack`).
2. Activate candidate in canary runtime scope.
3. Validate hot-path latency, fail-open behavior, and background loop health.
4. Promote candidate globally.
5. Roll back to previous active pack set if health regresses.

Deterministic compile means the same active pack state must produce the same context compilation behavior.

## 4) Default-on operating model

Required defaults in production profiles:
- fast boot from existing files
- background learning enabled
- prioritize new events over deep historical backlog
- allow larger compiled context when it removes avoidable model/tool round-trips
- human + self label harvesting enabled
- scanner + harvest loops enabled
- continuous graph learning enabled (decay, Hebbian co-firing, structural updates)
- teacher off hot path

## 5) Health signals to monitor

Hot path:
- turn latency budget
- fail-open activation rate
- route function/compile evaluation success rate

Background loops:
- ingest lag for new events
- backlog depth for historical data
- label harvest throughput (human + self)
- scanner/harvest worker error rates
- graph update throughput (decay/co-firing/structure)

Provenance/quality:
- event normalization success/failure counts
- provenance chain completeness
- correction retention trend

## 6) Incident handling

If hot path is unhealthy:
- keep OpenClaw serving via fail-open
- disable only the failing brain feature flag(s)
- retain event export/provenance stream for later recovery

If background learning is unhealthy:
- continue serving on current learned route function
- prioritize queue repair for new events first
- backfill historical queues after new-event lag is stable

If scanner/harvest loop is unhealthy:
- isolate worker faults from serving runtime
- keep labels and exported events queued durably
- restart loop workers without resetting runtime identity

## 7) Proof boundary (non-negotiable)

Mechanism/workflow proof supports safe promotion discipline. It is not a stand-in for live answer-quality claims.

Mechanism/workflow proof examples:
- schema/contract compatibility
- deterministic normalization and export
- provenance continuity
- stable compiler/activation behavior

Live product proof examples:
- better user-visible relevance/accuracy
- lower repeat-error rate after corrections
- stronger reliability under live traffic

## 8) Operator responsibilities

Operator owns:
- package promotion discipline
- runtime rollout and rollback hygiene
- SLO monitoring for hot path and background loops
- secret handling and environment hardening

Operator does not own:
- inventing alternate memory contracts outside published package boundaries
- bypassing provenance requirements for short-term debugging convenience

## 9) Routine checks

Run these checks before each production promotion:

```bash
corepack enable
pnpm install
pnpm check
pnpm release:pack
```

Then validate in runtime:
- canary traffic stable
- fail-open path tested
- new-event learning lag within SLO
- background scanner/harvest healthy
