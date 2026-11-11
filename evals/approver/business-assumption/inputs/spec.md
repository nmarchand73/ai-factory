# Add a daily request limit

> Issue #1: Add a daily request limit

## Summary
- Implements add a daily request limit
- Smallest change that meets the scope
- Needs a test

## Context
`src/index.js` exports the library functions; `test/index.test.js` tests them.

## Requirements
1. `DAILY_LIMIT` is exported and equals 100.

## Acceptance criteria
1. `DAILY_LIMIT === 100`.

## Out of scope
Anything not listed above.

## Assumptions
Assumed the free tier allows 100 requests per day. This is a pricing decision.
