# Security policy

## Reporting a vulnerability

Please don't open a public issue for a security problem. Use GitHub's private reporting instead:
**Security tab → "Report a vulnerability"** on [nmarchand73/ai-factory](https://github.com/nmarchand73/ai-factory/security/advisories/new).
Say what you found, how to reproduce it and what it affects. You will get an answer as soon as possible, and a fix or a
decision before anything is disclosed.

## Supported versions

Only the latest commit on `main` is supported.

## What to keep in mind

The factory runs Claude Code agents on your machine and pushes branches to your repositories, so:

- **The `factory` label is the trust boundary.** Only issues carrying it are built, and labeling needs triage or write
  access to the project. Issue text reaches agents only as quoted data in `issue.md`, never inside a prompt.
- **The factory never deploys,** and only pushes `factory/<job>` branches; merges go through `factory/bin/job merge`.
- **A project's `checks.sh` is part of its security.** It is run by the factory from outside the job's branch, so a branch
  can't change the checks it is judged by, but it only catches what it tests.
- **Protected paths** (for example `.github/workflows/*`, set per project in `factory/config.json`) escalate to a human.
- Secrets don't belong in `factory/config.json`, `targets/*/notes.md` or job files.

Reports about prompt injection through an issue, a branch escaping its worktree, or the factory writing outside its
folders are in scope.
