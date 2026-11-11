# AI Factory (hub)

This repo holds the factory, not the projects' code: projects are declared in `factory/config.json`
(`targets`) and cloned into `targets/<name>/repo`. The agents and the skill (`.claude/`) are shared by every target.

## Rules
- `factory/bin/job` is the only writer of `factory/jobs/<id>/job.json`; never edit it by hand.
- Every `gh` call in the code names its repo (`--repo`); don't add any that depends on the working directory.
- Never edit `targets/*/repo` or `workspaces/` by hand: only the scripts touch them.
- A target's checks live in `targets/<name>/checks.sh` (non-interactive, never rewrites files).
- The dashboard only reads files under `factory/`: `config.json`, `jobs/<id>/job.json` and its round files, and
  `jobs/_orchestration.json`. A new field in `job.json` is written by `factory/bin/job` and read by `factory/dashboard.html`.
- Costs come from Claude Code's transcripts (`cost_breakdown` in `factory/bin/job`); a model without a price in
  `config.json` is left out of the cost with a warning, it must never stop a job.

- What each agent is judged on lives in `evals/criteria.json` (criteria, weights, sources); `docs/EVALS.md` is generated from it (`factory/bin/eval docs > docs/EVALS.md`). A change to an agent's assignment or output format must update the criteria, `format_checks` and the rules in `factory/bin/eval`, and the eval cases in `evals/`.
- An eval case runs in `factory/evals/runs/` (gitignored), never in a real job.

## Validation
`python3 -m unittest tests/test_factory.py tests/test_eval.py` (fake `gh`, local git repos, synthetic transcripts).

## Commands
`/factory run [<target>]`, `/factory run <target>#<n>`, `/factory eval [<agent>|all] [<case>]`, `/factory scores`, `/factory <free text>`.
Add a project: `factory/bin/target add <name> <owner/repo>`, then `factory/bin/target check <name>`.
