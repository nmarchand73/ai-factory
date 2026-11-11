---
name: factory
description: Run the software factory on GitHub issues.
---

# Factory

## build

Spawn the builder with the spec and wait for it to report.

## review

Start the reviewers as soon as the builder reports READY, then run the gate.

When every reviewer has finished, advance the job to approve.
