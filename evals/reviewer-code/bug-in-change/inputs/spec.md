# Add a multiply function

> Issue #1: Add a multiply function

## Summary
- Implements add a multiply function
- Smallest change that meets the scope
- Needs a test

## Context
`src/index.js` exports the library functions; `test/index.test.js` tests them.

## Requirements
1. `src/index.js` exports `multiply(a, b)` returning `a * b`.
2. `test/index.test.js` tests it.

## Acceptance criteria
1. `export function multiply` exists in `src/index.js`.
2. `npm test` passes with a test for `multiply(2, 3) === 6`.

## Out of scope
division, README changes

## Assumptions
None.
