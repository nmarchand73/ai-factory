# Keep the cache in memory

- Status: Accepted
- Date: 2026-01-02
- Job: eval

## Context
The library needs a cache for repeated results. It runs inside the caller's process and has no storage of its own.

## Decision
We will keep the cache in memory, in a `Map` owned by the cache object.

## Consequences
Lookups are fast and there is nothing to configure. Cached values are lost when the process ends and are not shared between processes.

## Alternatives considered
- A file on disk: adds I/O, locking and a path to configure.
- A database: adds a dependency and a deployment concern for a small library.
