# Self-improvement: retrospective, versions, Evolution board

The factory improves itself in a loop, and every step is traceable. This page describes the loop, the files and the limits.
Commands: `factory/bin/evolve --help`.

## The loop

1. **Cycle.** One `/factory run` is one cycle (`c001`, `c002`, ...). `evolve cycle start` opens it; every job created meanwhile
   is stamped (`cycle`, `skill_versions`) in `job.json`, so each score can be attributed to the versions that produced it.
2. **Retrospective.** `evolve cycle close` scores the cycle (`eval report --cycle`), snapshots it in `history.jsonl`, measures
   the earlier changes and writes `cycles/<c>/input.json`: scores per agent and criterion, job metrics (escalation rate, rounds,
   cost per job), the human feedback and escalations, the skills in scope. The `retrospective` agent writes `plan.json`:
   issues per agent (gap = a criterion id or a feedback file, evidence, root cause: prompt, skill, orchestration or input), the
   orchestrator section (sequencing, routing, hand-offs), system-level recommendations, a review of the earlier changes, and
   per change: priority (P1-P3), confidence (low/medium/high), expected impact (criterion, direction, delta in points).
   A change replaces an exact passage (`old` -> `new`) of one skill file. `evolve plan check` validates the plan and renders
   `plan.md`.
3. **Human review.** The orchestrator shows the plan, then asks one question per change. `evolve decide <cycle> <change>
   approve|reject [--reason]`; a rejection needs a reason; both are appended to `audit.jsonl`. No all-or-nothing approval.
4. **Version.** `evolve apply` refuses anything not approved. It checks the active file still matches its snapshot, applies the
   change (the `old` text must match exactly once; front matter cannot change), saves `versions/<skill>/v1.3.md`, writes the
   active file and records in `registry.json`: version, date, cycle, the gap, the diff, who approved it, the expected effect.
   The previous version stays as an immutable snapshot. `evolve rollback <skill> <version>` restores any version as a new
   version. A manual edit of a skill is detected and recorded as an `external_edit` version.
5. **Measure.** At the next `cycle close`, each deployed change is compared with its expected impact using the cycle before
   and the cycle after (only cycles that ran with the new version count): `delivered` (moved by at least half the expected
   delta), `not_delivered`, `regressed` (moved the wrong way by 3+ points) or `inconclusive` (fewer than 3 samples). The next
   retrospective reviews every earlier change and may recommend a rollback.

## Scope and guard rails

In scope: `.claude/agents/*.md`, `.claude/skills/factory/SKILL.md` (the orchestrator), `targets/*/notes.md`.
Protected (the plan is rejected if it targets them): `eval-judge`, `retrospective`, `factory/bin/*`, `evals/criteria.json`,
`factory/config.json`. A system must not tune its own grader. At most `evolution.max_changes_per_cycle` (3) changes per
cycle, so that each effect stays attributable. Settings live under `evolution` in `factory/config.json`.

## Files (`factory/evolution/`, committed)

```
registry.json           per skill: path, current version, every version with date, cycle, gap, diff, approver, expected effect
versions/<skill>/vX.Y.md   the full text of every version, never rewritten
cycles/<c>/             cycle.json, input.json (for the retrospective), plan.json, plan.md
audit.jsonl             proposed -> approved|rejected -> deployed -> measured -> rolled_back, one line per event
history.jsonl           one score snapshot per cycle (overall, per agent, per criterion, job metrics, skill versions)
board.json              generated for the dashboard's Evolution board
current.json            the open cycle
```

## Evolution board

On the dashboard, under Agent confidence (collapsed by default): overall confidence by cycle with a mark where a change was
approved, a timeline of versions per changed skill (click a version for gap, diff, approver, expected and measured effect),
and the audit trail with a status filter. It reads `evolution/board.json` only.

## How the retrospective itself is judged

It is one of the nine agents in `evals/criteria.json`: it reads the cycle input and the skill before changing it, reviews earlier
changes, cites evidence for each gap, proposes exact and minimal changes, measurable expected impact, no invented work (a healthy
cycle gets no change), no protected target, calibrated priority and confidence; a judge scores whether the edits address the cause
and whether a person can decide from the plan. Three eval cases cover a clear gap, an all-green cycle and an orchestration issue.

## Limits

- A cycle has few jobs: many verdicts will be `inconclusive`, and scores move for other reasons (different issues each cycle).
  Change one thing at a time when you can.
- Approval is enforced by the script and logged (`by`, `reason`); the session that calls `apply` is the orchestrator, so the log
  records who approved but cannot prove a human click.
- A change applies from the next agent that starts; a running agent keeps its prompt.
- The retrospective's live score has no live samples yet (a cycle is not a job): it is scored by its eval cases.
