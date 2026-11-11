# Evals

Cases that replay each agent against a known situation, a fixture project to work in, and the rubrics
the eval-judge agent scores against. Run them with `/factory eval`; the scores feed the confidence score
of each agent (`factory/bin/eval report`).

```
evals/<agent>/<case>/case.json   what the case checks (description, fixture, expectations)
evals/<agent>/<case>/inputs/     files placed in the case's job folder (issue.md, spec.md, ...)
evals/<agent>/<case>/change/     files committed on the branch under review (review and approval cases)
evals/fixtures/<name>/           the project the agent works in
evals/rubrics/<agent>.json       the judge's criteria for that agent
```

Expectations (`case.json` → `expect`):

- `files.<name>`: `first_line` (regex), `headers` (`{"RISK": ["low"]}`), `sections`, `contains`, `not_contains`
  (regexes), `min_numbered` (+ `numbered_in`), `section_contains` and `section_not_contains` (`{"Scope": [regex]}`).
- `worktree`: `checks_pass`, `file_matches` (`{path: regex}`), `files_unchanged` (paths).
