## What and why

<!-- One idea per PR. What changes, and what problem it solves. -->

## Checklist

- [ ] `python3 -m unittest tests/test_factory.py tests/test_eval.py tests/test_evolve.py tests/test_metrics.py tests/test_target.py` passes
- [ ] I added or updated a test for the change
- [ ] A change to an eval rule or an agent's output format also updates `evals/criteria.json`, `factory/bin/eval`, the eval cases and `docs/EVALS.md`
- [ ] I did not hand-edit `factory/jobs/*/job.json`, `targets/*/repo` or `workspaces/`
- [ ] Docs (`README.md`, `docs/`, the manual) are updated if behaviour changed
