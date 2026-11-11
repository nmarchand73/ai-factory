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

## Agent evals and confidence

Every agent has a confidence score (0-100) built from two composite metrics:

- **process**, how it works;
- **output**, how good what it produces is.

The criteria are written for each agent's own assignment, not shared: an intake is judged on looking at the code
before deciding, on treating the issue as data and on asking little; a builder on running the checks and never
weakening a test; a security reviewer on tracing input to sinks and on findings that give vector, fix and CWE; an
approver on re-reading the evidence and on naming the escalation triggers it checked. Each criterion is a rule on the
transcript or the file, an outcome of the real job, or a score from the `eval-judge` agent, and says whether it rests
on a source or on our own reasoning. They come from a research pass (Anthropic's agent-eval guidance, OWASP, DORA,
Google's review guide, NN/g, WCAG, METR and others); see `docs/EVALS.md` and `evals/criteria.json`.

Evidence comes from live jobs (free: job files and transcripts) and from eval cases, 24 replayable situations in
`evals/` (at least one per agent). Little evidence pulls a score toward a neutral value, so a new agent shows as
*provisional*.

```bash
factory/bin/eval report            # confidence of every agent; also fills the dashboard's Agents panel
factory/bin/eval score builder     # every metric of one agent
> /factory eval builder            # in Claude Code: replay an agent's cases, score them, call the judge
```

## Self-improvement

After each `/factory run` (a *cycle*), a `retrospective` agent reads the cycle's scores, metrics and feedback, traces each
gap to an agent, the orchestrator or an upstream agent, and writes an improvement plan. You approve or reject **each change on
its own** (rejections are logged with your reason); an approved change becomes a new version of the skill (the previous one is
kept, any version can be restored) and the next cycle measures whether it worked. The Evolution board on the dashboard shows
versions, scores before and after, and the audit trail. The grader, the retrospective itself, the scripts, the criteria and the
config can never be changed by it. See `docs/EVOLUTION.md`.

```bash
factory/bin/evolve status                      # proposed, approved, deployed, measured changes
factory/bin/evolve trace agent:builder         # every version of a skill and the gap behind each
> /factory evolve rollback agent:builder 1.0   # in Claude Code: restore an earlier version
```

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
Tests: `python3 -m unittest tests/test_factory.py tests/test_eval.py tests/test_evolve.py`.

## Layout

```
.claude/skills/factory, .claude/agents   the orchestrator and the 9 agents (a single copy)
factory/                                  config.json, bin/{job,gate,route,target,eval,evolve}, dashboard.html, evolution/ (versions, cycles, audit)
evals/                                    eval cases, fixtures and judge rubrics per agent
targets/<name>/checks.sh, notes.md        per-project checks and guidance (committed)
targets/<name>/repo                       local clone of the project (gitignored)
workspaces/<name>/<job>                   job worktrees (gitignored)
factory/jobs/<job>                        job state (gitignored)
docs/                                     manual, origin notes, dashboard screenshot
```
