# eval fixture: mini-lib

## Setup
Nothing to install (Node 20+, no dependencies).

## Validation
`npm test`.

## Hot spots (security reviewer)
Anything that builds queries, shell commands or HTML from input.

## Always escalate (approver)
Authentication, permissions, pricing or any other business decision; new dependencies.

## What this project is for (intake)
A small utility library: arithmetic helpers with tests.
