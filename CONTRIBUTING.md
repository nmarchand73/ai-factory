# Contributing

Thanks for helping. NG AI Factory is a factory that builds other projects, so a few rules keep it trustworthy.

## Set up

You need `python3` (3.10 or later), `git`, `bash`, and, to run the factory itself, the `gh` CLI and Claude Code.
The tests need neither `gh` nor Claude Code: they use a fake `gh`, local git repos and synthetic transcripts.

```bash
git clone https://github.com/nmarchand73/ai-factory.git && cd ai-factory
python3 -m unittest tests/test_factory.py tests/test_eval.py tests/test_evolve.py tests/test_metrics.py tests/test_target.py
```

## Before you open a PR

- Read [AGENTS.md](AGENTS.md): it lists the rules (who writes which file, what the dashboard reads, what is protected).
- Keep the tests green and add one for what you change. A new KPI, an eval rule or an agent output change also updates
  `evals/criteria.json`, the rules in `factory/bin/eval`, the eval cases, and `docs/EVALS.md`
  (`factory/bin/eval docs > docs/EVALS.md`).
- Don't edit `factory/jobs/*/job.json` by hand (only `factory/bin/job` writes it), and don't edit `targets/*/repo` or
  `workspaces/`.
- Agent prompts and skills under `.claude/` change through the retrospective and `evolve apply` after approval, so that the
  version history stays true. If you edit one by hand, run `factory/bin/evolve init` so it is recorded as a version.
- Keep a PR to one idea, with a description of what changed and why.

## Reporting bugs and ideas

Open an issue with the template. For a security problem, don't open a public issue: see [SECURITY.md](SECURITY.md).

## License

By contributing you agree that your contribution is released under the project's license, GPL-3.0 (see [LICENSE](LICENSE)
and [NOTICE](NOTICE)).
