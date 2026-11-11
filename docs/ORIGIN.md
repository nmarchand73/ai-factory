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
