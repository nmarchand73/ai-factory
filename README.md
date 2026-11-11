# AI Factory

A software factory driven by Claude Code: a GitHub issue labeled `factory` becomes a pull request
(intake → spec → build → gate → parallel reviewers → approver). The factory lives **here** and works on
as many projects as you like; the projects only receive PRs. Fork of ZazenCodes' v2, see `docs/ORIGIN.md`.

## Quick start

```bash
factory/bin/target add my-project owner/repo      # clone, labels, checks.sh and notes.md to complete
$EDITOR targets/my-project/checks.sh targets/my-project/notes.md
factory/bin/target check my-project               # must end with "target is ready"
gh issue edit 12 --repo owner/repo --add-label factory
claude                                            # at the root of THIS repo
> /factory run my-project#12                      # or /factory run
```

Dashboard (one swimlane per project): `cd factory && python3 -m http.server`, then <http://localhost:8000/dashboard.html>.

Full manual (English and French, interactive): `docs/manuel-factory.html`. Tests: `python3 -m unittest tests/test_factory.py`.

## Layout

```
.claude/skills/factory, .claude/agents   the orchestrator and the 8 agents (a single copy)
factory/                                  config.json, bin/{job,gate,route,target}, dashboard.html
targets/<name>/checks.sh, notes.md        per-project checks and guidance (committed)
targets/<name>/repo                       local clone of the project (gitignored)
workspaces/<name>/<job>                   job worktrees (gitignored)
factory/jobs/<job>                        job state (gitignored)
```
