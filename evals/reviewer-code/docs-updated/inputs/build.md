STATUS: READY

# Build: Add an in-memory cache module

## Summary
- Adds `src/cache.js` with `createCache()`
- Tests were added and pass
- Architecture docs updated

## Changes
`src/cache.js`, `test/cache.test.js`, `docs/architecture/c4-3-components.md`, `docs/adr/0002-keep-the-cache-in-memory.md`.

## Documentation
- C4 level 1: unchanged (no new user or external system)
- C4 level 2: unchanged (same package, no new container)
- C4 level 3: updated (cache component and its path)
- ADR: docs/adr/0002-keep-the-cache-in-memory.md

## Acceptance criteria
1. [x] createCache exists: `src/cache.js`
2. [x] tests pass: `npm test` passed, 2 new tests

## Validation
`npm test`: passed.

## Log
### Round 1
Built the change and ran the tests.
