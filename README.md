# AI Factory

**Label a GitHub issue. Get back a reviewed, tested pull request.** Claude Code agents read the issue, write a spec,
build the change, run your project's checks, review it from several angles, and either merge it or hand it to you with a
clear reason. You stay in charge of what matters: what gets built, and anything the factory is not sure about.

Why this one:

- **It works on your projects, not inside them.** One factory runs any number of repos; they only receive PRs.
- **It tells you how good it is.** Every agent has a confidence score and every run has a cost, lead time and
  first-pass yield, instead of a feeling that "it seems to work".
- **It gets better, on your terms.** After each run it proposes precise changes to its own agents; nothing changes until
  you approve that change, and each one is measured afterwards and can be rolled back.
- **It leaves the project better documented.** C4 diagrams and ADRs are kept up to date as part of the change.
- **It is cheap enough to try.** Two real jobs on a static site cost $1.84 (9 min) and $3.09 (16 min, two review rounds), in
  API-equivalent terms.

It is a fork of ZazenCodes' [software factory v2](https://github.com/zazencodes/zazencodes-season-3/tree/main/src/software-factory-claude-code-v2)
(GPLv3, see [origin](docs/ORIGIN.md)). The original gives the pipeline and the agents; this fork makes it run on several
projects, measures it, and lets it improve on purpose.

![The pipeline: intake, spec, build, gate, parallel reviewers, approver](docs/img/pipeline.png)

| Step | Who | What it does |
|---|---|---|
| intake | agent (Opus) | decides if the issue is worth building and at what scope, rates risk and surfaces, or asks the author |
| spec | agent (Opus) | turns it into testable acceptance criteria |
| build | agent (Opus) | implements on a `factory/<job>` branch, opens the draft PR, documents the change (C4, ADR) |
| gate | script | runs the project's `checks.sh`; a failure goes back to the builder, no reviewer runs |
| review | agents, in parallel | code always; UX and UI for visible changes; security for sensitive ones |
| approve | agent (Opus) | merges the PR, or escalates it to you with the reason |

## Quick start

```bash
factory/bin/target add my-project owner/repo      # clone, labels, checks.sh and notes.md to complete
$EDITOR targets/my-project/checks.sh targets/my-project/notes.md
factory/bin/target check my-project               # must end with "target is ready"
gh issue edit 12 --repo owner/repo --add-label factory
claude                                            # in a fresh session, at the root of THIS repo
> /factory run my-project#12                      # or /factory run for every queue
```

## What this fork adds

**Runs on several projects, from the outside.** The original is copied into each project. Here the factory is its own
repo: a local clone and one git worktree per job, `config.json` declares the projects, and `checks.sh` and `notes.md` are
per project. `factory/bin/target` adds, checks and archives a project. Every `gh` call names its repo, and the queue no
longer depends on GitHub's lagging label search.

**Every agent is measured.** Each agent has a confidence score (0-100) from a *process* metric (how it works) and an *output*
metric (how good its work is), with criteria written for its own job: an intake is judged on reading the code before
deciding, a security reviewer on tracing input to sinks, an approver on re-reading the evidence. Evidence comes from live
jobs and from 27 replayable eval cases, with an `eval-judge` agent for what rules cannot check. See [EVALS](docs/EVALS.md).

**The factory improves itself, under your control.** After each run a retrospective agent traces every gap to an agent
or the orchestrator and proposes changes. You approve or reject **each one**; an approved change becomes a new version of
the skill, the next cycle measures whether it worked, and any version can be restored. The grader, the scripts and the
config can never be changed by it. See [EVOLUTION](docs/EVOLUTION.md).


**A health board with numbers, not impressions.** Lead time, first-pass yield, autonomy, escalation, cost per merged job,
stuck jobs, the weakest agent, whether the improvement loop delivers: computed from what the factory already writes, at no
token cost, each with a target. See [HEALTH](docs/HEALTH.md).


**Documentation of the application it changes.** The builder keeps C4 diagrams (levels 1 to 3) and ADRs true in the
project's `docs/`; the spec asks for them, the code reviewer blocks a branch that lacks them, and the evals score them.

**Security looks at the code, not only at the issue.** Intake can route a security reviewer from the issue text; after the
gate, `route --diff` adds it when the diff touches a sensitive path or adds a risky line (`innerHTML`, `eval(`, a CDN
script, a secret), whatever intake rated.

**Honest costs.** Cost per project, step and agent, including the orchestrator's own tokens, without billing a job for the
time it waits on a person.

**A dashboard to run it from.** One swimlane per project, most recently active first, with GitHub links on every card
(open the PR to merge, open the issue to answer), a count of what needs you, optional notifications, and archived
projects tucked away.

![The dashboard](docs/img/dashboard-swimlanes.png)

**Safer plumbing.** `factory/bin/job` is the only writer of job state and refuses illegal moves; a cycle can't be closed
twice or while a job is still running; a shared headless-browser helper (`factory/bin/browse`) replaces one script per
agent. The intake agent runs on Opus, and the manual is interactive and bilingual.

## How each part works

**Evals.** An eval case is a replayable situation (`evals/<agent>/<case>/`): an issue, a repo, a branch. The agent runs on it
in a scratch folder, and the result is checked by rules on its transcript and files, then by the `eval-judge` agent for
quality. Live jobs feed the same scores for free. Few samples pull a score toward neutral, so a new agent shows as
*provisional*. `factory/bin/eval report` prints every agent's confidence; `/factory eval builder` replays one agent.

![Agent confidence on the dashboard](docs/img/agents-confidence.png)

**Health.** `factory/bin/metrics` reads the job files, scores and evolution history and writes the KPIs the dashboard shows:
productivity (merged per week, lead time, hands-off share), flow quality (first-pass yield, rounds, autonomy, escalations),
agents (confidence, weakest agent), cost and vitality (stuck jobs, idle time, whether the retrospective loop delivers). Each
has a target in `config.json` and a status: good, watch or bad. `factory/bin/metrics show` prints it; `/factory health`
explains it.

![The factory health board](docs/img/factory-health.png)

**Application documentation.** On every change the builder keeps the project's C4 diagrams (context, containers, components,
as Mermaid in `docs/architecture/`) and an ADR in `docs/adr/` for each significant decision (a new dependency, a module
boundary). A change inside an existing component leaves the diagrams alone. It reports this in build.md.

![C4 diagrams written by the builder](docs/img/c4-diagrams.png)

**Self-improvement.** `evolve cycle close` snapshots the cycle's scores and feedback, the retrospective writes a plan of
precise text changes to agent prompts, and you approve each. `evolve apply` writes the new version (the old one is kept),
and the next cycle measures whether the targeted score moved: delivered, not delivered or regressed.
`factory/bin/evolve status` lists the changes; `/factory evolve rollback <skill> <version>` restores one.

![The evolution board: versions, scores before and after, audit trail](docs/img/evolution-board.png)

**Security review.** The security reviewer reads the diff and traces untrusted input to sinks; it is scored on findings that
give the vector, a fix and ideally a CWE id. It runs when intake rates a security surface (auth, input reaching queries or HTML,
secrets, payments), or when `route --diff` finds a sensitive path or risky line in the code.

**Cost.** Costs are API-equivalent, read from Claude Code's transcripts: every agent's tokens priced per model
(`prices_usd_per_mtok`), plus the orchestrator session's own, shared between the jobs running at the time.
`factory/bin/job summary` splits them per project, step and agent. Run `/factory run` in a fresh session: the orchestrator
was about 40% of a job's cost, mostly re-reading its context.

## What to expect, honestly

This is early software with a short track record: a handful of real jobs on small projects, a lot of tests (about 120)
and 27 eval cases, but not months of production use.

- **Scores are provisional.** With few jobs behind them, confidence scores lean on eval cases and shift as evidence arrives. Some graders
  have been wrong (we fixed several after the first retrospective); treat a score as a signal to look, not a verdict.
- **The security reviewer has not yet run on a real job.** It is routed and tested, but the jobs so far were cosmetic.
- **It is not a replacement for review.** The approver merges only when everything passes and nothing sensitive is touched;
  changes to protected paths or anything it doubts go to you.
- **Costs are API-equivalent estimates** from Claude Code's transcripts, not an invoice, and the orchestrator session can
  be about 40% of a job's cost unless you run it in a fresh session.
- **It needs a GitHub repo, the `gh` CLI, Claude Code, and a `checks.sh` per project** that actually catches mistakes. The
  factory is only as safe as those checks.
- **It builds and opens PRs; it never deploys.**

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
