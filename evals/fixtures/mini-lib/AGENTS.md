# mini-lib

A tiny Node.js library (ESM, no dependencies, Node 20+).

## Setup
Nothing to install.

## Validation
`npm test` (native `node --test`, files in `test/`).

## Conventions
- One exported function per feature in `src/index.js`, with a test in `test/index.test.js`.
- Update this file and the README when visible behaviour changes.
- Architecture docs: C4 diagrams in `docs/architecture/` (levels 1 to 3) and decisions in `docs/adr/`; keep them true.
