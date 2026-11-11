# Factory health board

`factory/bin/metrics` computes the factory's health from files that already exist (`factory/jobs/*/job.json`, `evals/scores.json`,
`evolution/board.json`, the eval runs) and writes `factory/metrics.json`; the dashboard shows it on top of the page. `job`, `eval
report` and `evolve board` refresh it, and `metrics write` does it by hand. Nothing here costs tokens.

Each KPI has a target (`factory/config.json`, `metrics.targets`: `[value, higher_is_better]`) and a status: **good** meets the
target, **watch** is within 25% of it, **bad** is further off. The targets are starting points: set the ones your team expects.

| Group | KPI | Definition |
|---|---|---|
| Productivity | Merged this week | jobs merged in the last 7 days |
| | Lead time (median) | job start to merge, merged jobs of the window, human waits included |
| | Hands-off share | share of lead time when the factory, not a person or an author, held the job |
| | Where the time goes | average hours a merged job spends in each stage; needs-human and needs-info are waits for people |
| Flow quality | First-pass yield | merged jobs that needed one build round |
| | Rounds per job | average build rounds of merged jobs |
| | Autonomy | merged jobs that never went to a human (the approver said APPROVE, the factory merged) |
| | Escalation rate | accepted jobs that needed a human |
| Agents | Average / weakest confidence | from `eval report` (process and output criteria, see `docs/EVALS.md`) |
| | Eval cases passing | latest run of each eval case; the board also shows coverage and the age of the last eval |
| | Security review rate | reviewed jobs where the security reviewer ran (routed by intake or added by `route --diff`); 0 means the lens is never exercised |
| | Shared browser tool | `agent-browser` or `factory/bin/browse` is available, so agents don't each write a browser script |
| Cost | Cost per merged job | API-equivalent cost of merged jobs; jobs from before cost tracking (no skill versions) are left out |
| | Cost of jobs not merged | spend on rejected jobs, as a share of all spend |
| | Orchestrator overhead | orchestrator spend while no job was running, in sessions that ran jobs (up to an hour after the last one); time a job waits for a person is not billed to it |
| Vitality | Stuck jobs | a job waiting on a person over 24 h, on an author over 72 h, or in a running stage over 4 h (`metrics.stuck_hours`) |
| | Idle for | time since any job changed stage |
| | Empty cycles | cycles closed with no job: closed too early or opened by mistake |
| | Changes that delivered | of the measured skill changes, the share that delivered (see `docs/EVOLUTION.md`) |

It also shows weekly trends (8 weeks: throughput, lead time, first-pass yield, escalation rate, cost per merged job), the stuck
jobs with their PR or issue link, the weakest agent, the retrospective loop, and a per-project table.

## Honest limits

- Lead time and waits come from the stage `history` in `job.json`, recorded since this board exists. Older jobs have a lead
  time (end minus start) but no stage times: their human wait is left out, never guessed.
- A few jobs per week make medians and rates jumpy; read trends, not single points.
- "Merged by the factory" means the job went through the `merging` stage with no `needs-human` before it; a PR a person merged
  by hand counts as human-merged.
- Quality after the merge (a revert, a bug found later) is not seen: that needs signals from the target repository.
- First-pass yield counts rounds, so a job that needs a second round because the spec changed counts as rework too.
