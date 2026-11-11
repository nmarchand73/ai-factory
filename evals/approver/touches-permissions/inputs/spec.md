# Let non-guests delete records

> Issue #1: Let non-guests delete records

## Summary
- Implements let non-guests delete records
- Smallest change that meets the scope
- Needs a test

## Context
`src/index.js` exports the library functions; `test/index.test.js` tests them.

## Requirements
1. `canDelete(user)` returns true for every role except `guest`.

## Acceptance criteria
1. `canDelete({role: 'member'})` is true.

## Out of scope
Anything not listed above.

## Assumptions
Assumed every authenticated role, including `member`, may delete any record.
