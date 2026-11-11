# Evals

What each agent is judged on, cases that replay each agent against a known situation, the fixture projects
they work in, and the research behind the criteria. The scores feed the confidence score of every agent
(`factory/bin/eval report`); run the cases with `/factory eval`.

```
evals/criteria.json              the criteria of every agent: process and output, kind, weight, measure, sources
evals/<agent>/<case>/case.json   what the case checks (description, fixture, expectations)
evals/<agent>/<case>/inputs/     files placed in the case's job folder (issue.md, spec.md, ...)
evals/<agent>/<case>/change/     files committed on the branch under review (review and approval cases)
evals/fixtures/<name>/           the project the agent works in
```

## Criteria

`criteria.json` is the single source of truth: the scoring code, the dashboard, the judge's rubric and the manual
all read it. For each agent it has a `role`, a list of `process` criteria (how the agent works) and a list of
`output` criteria (how good what it produces is). Every criterion has:

- `kind`: `rule` (read from the transcript or the output file), `outcome` (what happened to the job afterwards, or
  the golden answer of an eval case) or `judge` (a 0 to 5 score from the `eval-judge` agent, with its `question`);
- `weight`: relative to the other criteria of the same side of the same agent;
- `measure`: how it is measured, in one line;
- `basis`: `source` (grounded in a cited source) or `inference` (the authors' own reasoning);
- `sources`: ids into the `sources` table, each with the status of the check (`fetched`, `search`, `secondary`,
  `memory`).

`case_map` says which expectations of an eval case feed which criterion (for example the verdict and the
mention of the planted defect feed `seeded_defect_caught`).

To add a criterion: add it to `criteria.json`, write its rule in `factory/bin/eval` (`@rule("id")`, or an
`outcome_value` branch), and add a test in `tests/test_eval.py`. A `judge` criterion needs only its `question`.

## Eval cases

Expectations (`case.json` → `expect`):

- `files.<name>`: `first_line` (regex), `headers` (`{"RISK": ["low"]}`), `sections`, `contains`, `not_contains`
  (regexes), `min_numbered` (+ `numbered_in`), `section_contains` and `section_not_contains` (`{"Scope": [regex]}`).
- `worktree`: `checks_pass`, `tests_discriminate` (the tests fail when the source change is reverted),
  `file_matches` (`{path: regex}`), `files_unchanged` (paths).
- `canary`: regexes for planted instructions (prompt-injection cases): none may reach the agent's Scope or a command.
