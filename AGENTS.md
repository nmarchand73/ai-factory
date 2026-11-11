# AI Factory (hub)

This repo holds the factory, not the projects' code: projects are declared in `factory/config.json`
(`targets`) and cloned into `targets/<name>/repo`. The agents and the skill (`.claude/`) are shared by every target.

## Rules
- `factory/bin/job` is the only writer of `factory/jobs/<id>/job.json`; never edit it by hand.
- Every `gh` call in the code names its repo (`--repo`); don't add any that depends on the working directory.
- Never edit `targets/*/repo` or `workspaces/` by hand: only the scripts touch them.
- A target's checks live in `targets/<name>/checks.sh` (non-interactive, never rewrites files).
- The dashboard only reads files under `factory/`: `config.json`, `jobs/<id>/job.json` and its round files, and
  `jobs/_orchestration.json`, `evals/scores.json`, `evolution/board.json` and `metrics.json`. A new field in `job.json` is written by `factory/bin/job` and read by `factory/dashboard.html`.
- Costs come from Claude Code's transcripts (`cost_breakdown` in `factory/bin/job`); a model without a price in
  `config.json` is left out of the cost with a warning, it must never stop a job.

- What each agent is judged on lives in `evals/criteria.json` (criteria, weights, sources); `docs/EVALS.md` is generated from it (`factory/bin/eval docs > docs/EVALS.md`). A change to an agent's assignment or output format must update the criteria, `format_checks` and the rules in `factory/bin/eval`, and the eval cases in `evals/`.
- An eval case runs in `factory/evals/runs/` (gitignored), never in a real job.
- `factory/bin/metrics` is the only writer of `factory/metrics.json` (gitignored, recomputed from the jobs, the scores and the
  evolution board; `job`, `eval report` and `evolve board` refresh it). A new KPI goes in `compute()`, with a default target in
  `DEFAULTS`, a definition in the dashboard's `KPI` table and a test in `tests/test_metrics.py`. `job.json` keeps a `history` of
  stage changes (written by `factory/bin/job`): lead time and waits come from it.
- The builder documents the application it changes: C4 diagrams levels 1 to 3 in `docs/architecture/` and ADRs in `docs/adr/`
  of the target repo, reported in a `## Documentation` section of build.md. The spec-writer requires them, the code reviewer
  checks them, and the criteria `c4_*`, `adr_*`, `docs_*` in `evals/criteria.json` score them. A change to that convention
  updates the three agent prompts, those rules in `factory/bin/eval`, the `mini-lib` fixture and the cases.
- `factory/bin/evolve` is the only writer of `factory/evolution/` (committed: registry, versions, cycles, audit trail). A skill, an
  agent or a target's `notes.md` changes only through `evolve apply` after `evolve decide ... approve` for that change; never edit
  a skill's active file to "fix" a plan, never approve for the user. `eval-judge`, `retrospective`, `factory/bin/*`,
  `evals/criteria.json` and `factory/config.json` are protected: the retrospective may not change them. A new field in the plan
  format updates `shape_errors` in `evolve`, the retrospective's criteria and its eval cases.

## Validation
`python3 -m unittest tests/test_factory.py tests/test_eval.py tests/test_evolve.py tests/test_metrics.py` (fake `gh`, local git repos, synthetic transcripts).

## Commands
`/factory run [<target>]`, `/factory run <target>#<n>`, `/factory eval [<agent>|all] [<case>]`, `/factory scores`, `/factory retro [<cycle>]`, `/factory evolve [rollback <skill> <version>]`, `/factory health`, `/factory <free text>`.
Add a project: `factory/bin/target add <name> <owner/repo>`, then `factory/bin/target check <name>`.
