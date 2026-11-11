# Improvement plan for cycle c002

## Earlier changes: did they work?

- `c001/ch1`: delivered. reviewer-ux.reliability 50 -> 90 and grounding 33.3 -> 66.7 (n=1 each cycle). In job 004 agent-browser was still missing, and the round-1 UX reviewer drove headless Chrome itself on port 5141 (round-1/review-ux.md Summary) instead of passing from the code. uses_the_page went 100 -> 70 because round 2 did not reopen the browser, a choice it justified (round-2 change not visual). One job, so confidence is low.
- `c001/ch3`: delivered. reviewer-ux.checklist_covered 60 -> 100 (n=1). Both review-ux.md files in job 004 answer loading/empty/error states and signed-in paths with an N/A and a reason, as the change asked.
- `c001/ch2`: delivered. spec-writer.atomic_requirements 12.5 -> 42.9 (n=1), +30.4 against the +30 expected. Still below 70: in jobs/004-polish-the-background/spec.md most remaining 'and's join nouns in a list (Req 11 'the header, the player and the tracklist'), but Req 3 (new layer + placement + drawing method) and Req 5 ('wider ... and more visible') still bundle two conditions. A different spec on a different job, so read it as a trend, not proof.

## builder

- issue `convergence`: convergence 67 (n=1): job 004 needed a second round only because the builder added three baseline C4 files (docs/architecture/c4-1..3) to a styling change. spec.md Out of scope says 'Adding C4 diagrams or an ADR: this is a style change inside the existing page'. round-1/review-code.md Finding 1 blocked on it, and build.md Log Round 1 says 'Added baseline C4 docs'. builder.md contradicts itself: 'No diagrams yet: create all three for the whole application' versus 'A change that touches none (... styling ...) leaves the diagrams alone'. The spec-writer and reviewer-code prompts both say 'A change inside an existing component needs neither'. (root cause: prompt)
- issue `evidence_per_criterion`: evidence_per_criterion 64.3 (n=1): reading build.md Acceptance criteria by hand, all 14 have concrete evidence (commands, line numbers, computed values). Several are short ('`.sun-corona` has `inset: -62%`.'), so this looks like a grader threshold rather than missing evidence. No change. (root cause: input)
- **ch1** (P1, confidence medium) on `agent:builder`: in a repo with no diagrams, the builder creates baseline C4 docs even for a styling change the spec puts out of scope, so the code review sends it back for a round
  - expected: convergence up by 15 points
  - replace: `'- No diagrams yet: create all three for the whole application, from the code as it is on the base'`
  - with: `'- No diagrams yet, and the change touches at least one level (next point): create them. A change that\n  touches no level, or a spec whose Ou'`

## spec-writer

- issue `no_vague_words`: no_vague_words 20 (n=1, was 60 in c001): jobs/004-polish-the-background/spec.md uses 'and/or' four times in Requirements and Acceptance criteria (Req 3 'gradients ... and/or box-shadow', Req 5 'colour-mix percentages and/or opacity', AC 4, AC 7). Each one leaves the builder and the approver to decide what counts as done. The prompt has no rule on ambiguous connectives. (root cause: prompt)
- issue `behavioural_criteria`: behavioural_criteria 42.9 (n=1): read by hand, the criteria are observable (grep commands, scrollWidth <= innerWidth, DevTools reduced-motion). Same grader verb-list issue as c001. No change. (root cause: input)
- issue `out_of_scope_kept`: out_of_scope_kept 66.7 (n=1): both items intake left out (sky gradients/drift/grain/horizon, brand colours) are in spec.md Out of scope. Req 13 repeats intake's own narrow per-theme exception, which the rule probably reads as a leak. No change. (root cause: input)
- **ch2** (P2, confidence medium) on `agent:spec-writer`: requirements and criteria leave choices open with 'and/or', so done is not one checkable thing
  - expected: no_vague_words up by 30 points
  - replace: `'- Reuse what exists. If the repo already has a pattern for this (a component, a'`
  - with: `'- Each requirement and criterion has one reading. Don\'t write "and/or", "etc.", "should" or "as\n  needed": name what you require, or write "'`

## reviewer-ui

- issue `hunts_hardcoded`: hunts_hardcoded 50 (n=1, two rounds): neither review-ui run in job 004 searched the diff for raw colours or px values (their greps target applyTheme, keyframes and pointer-events). The '#000' in the new .sun-rays mask was raised by the code reviewer in round 1 (round-1/review-code.md Notes), not by the UI reviewer, which mentioned it only in round 2. The prompt says 'Flag ... hard-coded colours' but never says how to find them. (root cause: prompt)
- **ch3** (P3, confidence low) on `agent:reviewer-ui`: the UI reviewer looks at screenshots but doesn't search the added lines for raw colours and sizes
  - expected: hunts_hardcoded up by 30 points
  - replace: `'  hard-coded colours where a theme value exists.'`
  - with: `"  hard-coded colours where a theme value exists. Search the added lines for raw values\n  (`git diff <base>...HEAD | grep -nE '^\\+.*(#[0-9a-f"`

## Orchestrator


## System-level recommendations

- (P1, confidence high) Grader review by a person (factory/bin/eval is protected). In job 004 the approver read every job file, all round-2 files, the round-1 reviews, the diff and re-ran checks.sh through shell globs (for f in "$J"/*.md; for f in "$J"/round-2/*.md), but evidence_reread and grounding scored 33.3 because the rules match literal file names in tool inputs and do not expand globs. Same family as the c001 note on paths_verified and the OBSERVABLE regex (behavioural_criteria 42.9 for observable criteria). atomic_requirements also counts 'and' inside a list of nouns as a bundle.
- (P2, confidence medium) Still open from c001: install agent-browser on the factory machine or make /factory health report it missing. In job 004 the builder, both UI reviews and the UX review each wrote their own headless Chrome CDP script, which costs tokens every run. If it won't be installed, a shared CDP helper script in the factory (written by a person) would remove that work.
- (P2, confidence medium) Still open from c001: 'reply' is 70 or less for every agent (intake 35, reviewer-ux 30, reviewer-code 50). The harness's 'full report in SubagentHandback' conflicts with each prompt's one-line reply. Decide once in skill:factory which wins, rather than patching seven prompts.
- (P3, confidence low) intake.risk_calibration 50 (n=1): intake said low risk and the job took 2 rounds, but the second round came from the builder's C4 rule (builder ch1), not from the job's difficulty. Don't change intake; check again next cycle once ch1 is in.
