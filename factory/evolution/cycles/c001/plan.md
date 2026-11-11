# Improvement plan for cycle c001

## reviewer-ux

- issue `reliability`: reliability 50 (n=1): in job 003 the agent ran agent-browser without checking it exists (exit 127, 'command not found: agent-browser'), then Read two screenshots that were never made (/private/tmp/claude-501/d1.png, m1.png: 'File does not exist'). It then wrote PASS from the code alone. round-1/review-ux.md says 'Not verified visually: depth look, 900px and 375px layout, and the scrollWidth check', so AC 4, 5 and 8 of spec.md were never checked on the page. In the same job the builder hit the same missing CLI and checked every AC with headless Chrome over CDP (build.md, Acceptance criteria). (root cause: prompt)
- issue `grounding`: grounding 33.3 (n=1): the transcript reads spec.md only through 'cat spec.md | head -60' and never opens build.md or notes.md before writing the review, so it missed the builder's description of how it checked the page. (root cause: prompt)
- issue `checklist_covered`: checklist_covered 60 (n=1): round-1/review-ux.md covers accessibility, keyboard and mobile but says nothing about loading, empty or error states, copy or user roles, not even an N/A with a reason. The prompt lists the topics under 'What to look for' but never asks for each one to be answered. (root cause: prompt)
- issue `reply`: reply 30 (n=1): final message 'VERDICT: PASS (code review only; agent-browser unavailable). Written to ...' instead of the review's first line. (root cause: orchestration)
- **ch1** (P1, confidence medium) on `agent:reviewer-ux`: when agent-browser is missing, the UX reviewer drops to reading code and passes without checking the page, even though a headless Chrome works on this machine
  - expected: reliability up by 25 points
  - replace: `'Then use the `agent-browser` CLI (run `agent-browser skills get core` first).'`
  - with: `'Then use the `agent-browser` CLI (run `agent-browser skills get core` first). Check that it exists with `command -v agent-browser` before yo'`
- **ch3** (P3, confidence medium) on `agent:reviewer-ux`: the UX review skips half of its checklist (states, copy, roles) without saying why
  - expected: checklist_covered up by 25 points
  - replace: `'If the branch has no user-facing change, write PASS and say so.'`
  - with: `'Answer every topic above in the review (Summary or Notes). When one does not apply, write N/A with a one-line reason, e.g. "no loading or er'`

## spec-writer

- issue `atomic_requirements`: atomic_requirements 12.5 (n=1; 39.6 over n=2 in scores.json): in jobs/003-add-3dlogo-on-top/spec.md 7 of 8 requirements bundle several conditions. Requirement 6 bundles aria-hidden, no focusable element, no tabindex, pointer-events and not-a-link. Requirement 7 bundles no overlap, header height, no layout jump, ≤980px placement and ≤640px scaling. The template only says 'Numbered list of what must be true'. (root cause: prompt)
- issue `behavioural_criteria`: behavioural_criteria 22.2 (n=1): when read by hand, the 9 acceptance criteria are observable (commands, computed animation-name 'none', scrollWidth <= innerWidth, accessibility tree). The rule's verb list misses words like 'appears', 'is static' and 'has no'. No prompt change: see system. (root cause: input)
- issue `paths_verified`: paths_verified 40 (n=1): the spec-writer did list the repo ('git ls-files', 'ls -la') before it wrote, and every cited file (sets.js, bios.js, analyser.js, serve.py, .gitignore) is in that output. The rule only matches tool inputs, not their output. No prompt change: see system. (root cause: input)
- **ch2** (P2, confidence medium) on `agent:spec-writer`: requirements bundle several conditions under one number, so they are hard to trace one by one to a criterion
  - expected: atomic_requirements up by 30 points
  - replace: `'Numbered list of what must be true when the work is done.'`
  - with: `'Numbered list of what must be true when the work is done. One condition per number: when a requirement joins two conditions ("X and Y"), spl'`

## Orchestrator


## System-level recommendations

- (P1, confidence high) Install the agent-browser CLI on the factory machine. Have 'factory/bin/target check' (or /factory health) report when it is missing, because reviewer-ux and reviewer-ui depend on it. In job 003 both the builder and reviewer-ux found it missing ('command not found: agent-browser').
- (P2, confidence medium) Every agent scored 70 or less on 'reply' (reviewer-ux 30). The harness tells subagents to put a full report in SubagentHandback, which conflicts with each prompt's 'reply with one line'. A person should decide which wins (for example, a sentence in skill:factory's Spawning agents section saying the handback message is that one line), rather than patching seven prompts one by one.
- (P2, confidence medium) Grader review by a person (the retrospective may not touch factory/bin/eval). Several low scores in job 003 come from the rules, not from the work. paths_verified ignores paths seen in tool output ('git ls-files'). grounding expects AGENTS.md even when the target has none (djset has no AGENTS.md; notes.md is canonical). The OBSERVABLE regex for behavioural_criteria misses 'appears', 'is static', 'has no' and computed-value checks. evidence_per_criterion misses evidence written as sub-bullets (builder AC 4, 7 and 8 have detailed evidence but score as missing). uses_the_page scored 100 for a review the agent itself called 'code review only'.
- (P3, confidence low) reviewer-ux first started serve.py on the default port 8766 and then ran 'kill $(lsof -tiTCP:8766 -sTCP:LISTEN)'. That can kill another job's server. Consider adding the server's port flag or env var (HORIZON_PORT for djset) to notes:djset, so reviewers start on their own port the first time.
