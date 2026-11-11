# Origin

This factory is a deliberate fork of ZazenCodes' *software factory v2*
(<https://github.com/zazencodes/zazencodes-season-3/tree/main/src/software-factory-claude-code-v2>),
published under GPLv3 (see `LICENSE`). It evolves independently here: no synchronization with the
upstream is planned.

Main differences:

- the factory lives in its own repo and works on **several target projects** from the outside
  (local clone + worktrees), instead of being copied into each project;
- `config.json` declares the targets; `checks.sh` and `notes.md` are per target;
- `factory/bin/target` adds and checks a target;
- the dashboard shows one swimlane per project;
- every `gh` call names its repo (`--repo`); none depends on the current directory.
- `job queue` lists issues without `gh --label` (GitHub's search index lags behind new issues);
- costs are split per agent and per step, include the orchestrator session, and `job summary` reports them per project;
- the dashboard adds per-project cost spread, GitHub links (open PR to merge, open issue to answer), a latest-5 Done
  column, tab-title count and optional notifications, and caches finished jobs;
- the intake agent runs on Opus instead of Fable;
- the manual is interactive and bilingual (English by default).
