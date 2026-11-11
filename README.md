# AI Factory

A GitHub issue labeled `factory` becomes a pull request, built and reviewed by Claude Code agents. The factory lives
here and works on any number of projects; the projects only receive PRs. Fork of ZazenCodes' v2 ([origin](docs/ORIGIN.md)).

![The pipeline: intake, spec, build, gate, parallel reviewers, approver](docs/img/pipeline.png)

## Quick start

```bash
factory/bin/target add my-project owner/repo      # clone, labels, checks.sh and notes.md to complete
$EDITOR targets/my-project/checks.sh targets/my-project/notes.md
factory/bin/target check my-project               # must end with "target is ready"
gh issue edit 12 --repo owner/repo --add-label factory
claude                                            # in a fresh session, at the root of THIS repo
> /factory run my-project#12                      # or /factory run for every queue
```

## Commands

| | |
|---|---|
| `/factory run [<project>[#<n>]]` | build the queued issues, `concurrency` at a time |
| `/factory health` · `scores` | KPIs and agent confidence |
| `/factory eval [<agent>]` | replay an agent's eval cases and score them |
| `/factory retro` · `evolve` | improvement plan, approved change by change; roll back a skill version |
| `factory/bin/target archive <name>` | stop building a project and hide it on the dashboard |
| `factory/bin/job summary` | jobs and their cost per project, step and agent |

Dashboard: `cd factory && python3 -m http.server`, then <http://localhost:8000/dashboard.html>.

## Documentation

- **[Manual](docs/manuel-factory.html)** (English and French, interactive), or
  [view it in the browser](https://htmlpreview.github.io/?https://github.com/nmarchand73/ai-factory/blob/main/docs/manuel-factory.html)
- [Agent evals and confidence](docs/EVALS.md) · [Self-improvement](docs/EVOLUTION.md) · [Health KPIs](docs/HEALTH.md)
- [AGENTS.md](AGENTS.md): rules for working on the factory itself

## Configuration

`factory/config.json`: `concurrency`, `max_rounds`, reviewer models per risk and per surface, projects under `targets`,
prices for the cost report. Agent models are the `model:` line of `.claude/agents/*.md`; restart the session after editing one.

## Tests

```bash
python3 -m unittest tests/test_factory.py tests/test_eval.py tests/test_evolve.py tests/test_metrics.py tests/test_target.py
```

## Layout

```
.claude/skills/factory, .claude/agents    the orchestrator and the 9 agents
factory/                                  config.json, bin/ (the scripts), dashboard.html, evolution/
evals/                                    eval cases, fixtures and judge rubrics
targets/<name>/checks.sh, notes.md        per-project checks and guidance
docs/                                     manual, EVALS, EVOLUTION, HEALTH, screenshots
```
