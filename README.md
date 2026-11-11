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

Always launch from this repo, never from a project. Several projects run side by side: `/factory run` drains
every project's queue (`concurrency` jobs at a time, shared), `/factory run <project>` one project,
`/factory run <project>#<n>` one issue.

## Dashboard

`cd factory && python3 -m http.server`, then <http://localhost:8000/dashboard.html>.

- one swimlane per project, stages as columns, jobs as cards with a chip per round (gate, code, ux, ui, security);
- GitHub links everywhere: issue and PR pills, **Open PR to merge** on jobs that need you, **Open issue to answer**
  on jobs waiting for their author, the repo in each lane header;
- cumulative cost per project, spread per step and per agent (including the orchestrator session);
- the tab title shows how many jobs need you, and an optional browser notification fires when one starts waiting;
- the Done column shows the latest 5 jobs per project (the cost still counts all of them).

## Models and settings

`factory/config.json`: `concurrency`, `max_rounds`, reviewer models per risk (`routing`) and per surface
(`surface_reviewers`), per-project settings under `targets`, prices used for the cost report.
The fixed agents' models are the `model:` line of `.claude/agents/*.md`: intake, spec-writer, builder and approver
use Opus; reviewers follow `config.json`. Restart the Claude Code session after editing an agent file.

## Cost report

`factory/bin/job summary` prints the jobs, then the cost per project, step and agent. Costs are API-equivalent
estimates read from Claude Code's transcripts; the `/factory` session's own tokens are shared between the jobs
running at the time (use a session dedicated to the factory).

## Documentation

Full manual (English and French, interactive): `docs/manuel-factory.html`.
Tests: `python3 -m unittest tests/test_factory.py`.

## Layout

```
.claude/skills/factory, .claude/agents   the orchestrator and the 8 agents (a single copy)
factory/                                  config.json, bin/{job,gate,route,target}, dashboard.html
targets/<name>/checks.sh, notes.md        per-project checks and guidance (committed)
targets/<name>/repo                       local clone of the project (gitignored)
workspaces/<name>/<job>                   job worktrees (gitignored)
factory/jobs/<job>                        job state (gitignored)
docs/                                     manual, origin notes, dashboard screenshot
```
