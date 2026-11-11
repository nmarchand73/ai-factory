# AI Factory (hub)

This repo holds the factory, not the projects' code: projects are declared in `factory/config.json`
(`targets`) and cloned into `targets/<name>/repo`. The agents and the skill (`.claude/`) are shared by every target.

## Rules
- `factory/bin/job` is the only writer of `factory/jobs/<id>/job.json`; never edit it by hand.
- Every `gh` call in the code names its repo (`--repo`); don't add any that depends on the working directory.
- Never edit `targets/*/repo` or `workspaces/` by hand: only the scripts touch them.
- A target's checks live in `targets/<name>/checks.sh` (non-interactive, never rewrites files).

## Validation
`python3 -m unittest tests/test_factory.py` (uses a fake `gh` and local git repos).

## Commands
`/factory run [<target>]`, `/factory run <target>#<n>`, `/factory <free text>`.
Add a project: `factory/bin/target add <name> <owner/repo>`, then `factory/bin/target check <name>`.
