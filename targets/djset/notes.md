# djset (nmarchand73/djset): notes for the factory's agents

The agents read this file and the project's own AGENTS.md or CLAUDE.md. Jobs run
in a fresh git worktree outside the repo, so this file is canonical when the
project's own docs are thin. Keep each section short and concrete.

## Setup
Nothing to install: a static site (`index.html`, `sets.js`, `themes.js`, `bios.js`,
`analyser.js`) with no build step and no dependencies. Python 3 and Node are only
needed for the checks. `videos/` and `audio/` (gitignored, ~17 GB) are not in a
fresh checkout, so the player cannot play media there: don't try to fix that.

## Dev server
`python3 serve.py` serves the site on `127.0.0.1:8766` (override with `HORIZON_PORT`).
Use a server rather than opening the file: YouTube embeds need a proper Referer.

## Validation
`targets/djset/checks.sh`: syntax of every `.js` file and of `serve.py`, local files
referenced by `index.html` exist, and `sets.js` is well formed (unique ids, artist,
tracks with non-decreasing `seconds`).

## Hot spots (security reviewer)
- `serve.py`: must keep `private/` unreachable (it holds YouTube cookies and extract
  logs) and keep binding to `127.0.0.1` only.
- Track titles, artists and bios come from `sets.js` / `bios.js`; check anything that
  puts them in the page with `innerHTML` instead of `textContent`.
- Third-party scripts and styles loaded from CDNs (plyr, Google Fonts): adding or
  changing one is a supply-chain change.
- Never commit `private/`, cookies or media.

## Design (UI and UX reviewers)
Single page app. Per-artist visual universes live in `themes.js`, bios in `bios.js`,
the audio spectrum/VU meters in `analyser.js`, set data and tracklists in `sets.js`.
Users are fans following a DJ set with its tracklist. Copy is in French.
When `sets.js`, `themes.js`, `bios.js` or `analyser.js` change, bump the `?v=NN`
query on their `<script>` tags in `index.html` so browsers do not keep stale copies.

## Always escalate (approver)
Changes to `serve.py`, to the CDN scripts or stylesheets in `index.html`, or to
`.gitignore` (it keeps media and `private/` out of git).

## What this project is for (intake)
Horizon: a personal viewer for DJ sets (video or YouTube) with tracklist, artist
themes, bios and a live audio spectrum. Issues about adding sets or improving that
viewer belong; unrelated tooling does not.
