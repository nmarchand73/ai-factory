# Add queryByName

> Issue #1: Add queryByName

## Summary
- Implements add querybyname
- Smallest change that meets the scope
- Needs a test

## Context
`src/index.js` exports the library functions; `test/index.test.js` tests them.

## Requirements
1. `queryByName(name)` returns the SQL string for a user lookup.

## Acceptance criteria
1. `queryByName('bob')` returns a SELECT for bob.

## Out of scope
Anything not listed above.

## Assumptions
None.
