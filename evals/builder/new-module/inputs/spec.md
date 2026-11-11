# Add an in-memory cache module

> Issue #1: Add an in-memory cache

## Summary
- Adds a new `cache` module with an in-memory store
- Documents the new component and the decision behind it
- Needs tests

## Context
`src/index.js` exports the library functions; `test/index.test.js` tests them. Architecture docs are in `docs/architecture/` (C4 levels 1 to 3) and decisions in `docs/adr/`.

## Requirements
1. A new module `src/cache.js` exports `createCache()`, returning an object with `get(key)`, `set(key, value)` and `clear()`, backed by a `Map`.
2. `test/cache.test.js` tests it.
3. The new component is added to the C4 level 3 diagram, with its path in the table.
4. The decision to keep the cache in memory (not in a file or a database) is recorded as an ADR in `docs/adr/`.

## Acceptance criteria
1. `export function createCache` exists in `src/cache.js`.
2. `npm test` passes with tests for `set`, `get` and `clear`.
3. `docs/architecture/c4-3-components.md` lists the `cache` component with the path `src/cache.js`.
4. A new file `docs/adr/0002-*.md` records the in-memory decision with Context, Decision, Consequences and Alternatives considered.

## Out of scope
Persistence, expiry, size limits, any change to `src/index.js`.

## Assumptions
None.
