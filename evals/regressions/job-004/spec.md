# Bigger sun with a richer glow on every theme

> Issue #3: Polish the background

## Summary
- The author answered intake: "for all 14 themes, bigger sun with a nice effect around".
- The sun is one shared set of layers in `index.html`, coloured by CSS variables that `themes.js` sets for each theme, so a single CSS change reaches all 14 themes.
- The work: make the sun about 1.5x bigger (with a cap), add one new glow/rays layer, and make the existing corona wider and easier to see. Colours come only from the existing theme variables.
- The sky gradients, drift glows, grain, horizon line and every theme's brand colours stay as they are.

## Context
- **Sun markup**: `index.html`, inside `<div class="sky" aria-hidden="true">` (around line 1586): `.sun` contains `.sun-corona`, `.sun-halo`, `.sun-core` (which holds `.sun-sheen`) and `.sun-ring`.
- **Sun CSS**: `index.html`, lines ~110-193.
  - `.sun` is absolutely positioned at `left: 50%; bottom: 16vh`. It is sized by `width/height: min(26vw, 260px)` and animated by `rise` (16s).
  - Its children are sized relative to it with `inset`: corona `-42%`, halo `-14%`, core `0`, sheen `-20%`, ring `4%`. They are coloured with `radial-gradient`s and `box-shadow`s built from `color-mix(in srgb, var(--gold|--accent-glow|--cream|--accent-soft|--accent) N%, transparent)`.
  - The keyframes `rise`, `corona-breathe`, `halo-pulse`, `core-glow`, `sheen-drift` and `ring-spin` are at lines ~215-252.
  - A comment in `.sun` says not to use `filter: blur` there (Safari draws a rectangular frame).
- **Horizon**: `.horizon` sits at `bottom: 18vh`, so the sun's lower edge sits just under the line.
- **Reduced motion**: `@media (prefers-reduced-motion: reduce)` at line ~283 lists every sky/sun layer with `animation: none`.
- **Overflow**: `.sky` is `position: fixed; inset: 0; overflow: hidden`, and `body` has `overflow-x: hidden`. A larger glow is clipped by `.sky`, so it can't widen the page.
- **Theme colours**: `themes.js` (loaded as `themes.js?v=54`) defines 14 themes keyed by set id: `ben, artbat, monique, prydz, lane8, tiesto, carlcox, fact1, fact2, lysten, dresel, cattaneowarren, northern, cattaneo`. `applyTheme(set)` in `index.html` (~line 2051) copies each theme's `sun`, `gold`, `accent`, `accentGlow`, `accentSoft`, `cream` (and others) into CSS variables on the root. Choosing a set in the page switches the theme.
  - The dark or monochrome themes are `carlcox` (black/white/grey sun) and `prydz` (black/gold).
- **Docs**: the repo has no `AGENTS.md`/`CLAUDE.md` and no `docs/` folder. `targets/djset/notes.md` (in the factory) is the project guide.
- **Running it**: `python3 serve.py` serves the page on `http://127.0.0.1:8766`.

## Requirements
1. The `.sun` box is between 1.4x and 1.6x its current size at every viewport width: its `width` and `height` are `min(Xvw, Ypx)` with X in 36-42 and Y in 364-416. Width and height stay equal.
2. The sun keeps its current anchoring (`left: 50%`, `bottom: 16vh`, centred with `translateX(-50%)`), so it still sits on the `.horizon` line.
3. `.sun` gets one new decorative child layer for the "effect around" the sun, for example `.sun-rays`. It sits behind `.sun-core` and outside it. It is drawn with CSS gradients (e.g. a `repeating-conic-gradient` faded out with a radial `mask-image`) and/or `box-shadow`.
4. The new layer animates slowly (a rotation or breathing cycle of 20s or more), so it moves gently like the existing layers.
5. The `.sun-corona` glow is wider than today (its `inset` is more negative than `-42%`) and more visible than today (higher colour-mix percentages and/or opacity).
6. The new layer and the changed corona take their colours only from the existing theme variables (`--sun`, `--gold`, `--accent`, `--accent-glow`, `--accent-soft`, `--cream`), through `color-mix(...)` as the current layers do. No new hard-coded hues.
7. No sun layer uses `filter: blur` (or any `filter`). The existing Safari comment is kept.
8. The new layer is added to the `@media (prefers-reduced-motion: reduce)` list that sets `animation: none`.
9. The new element and all sun layers keep `pointer-events: none` (directly or through `.sun`), so they never block clicks.
10. The page does not scroll sideways at 375px, 768px or 1440px wide.
11. The header, the player and the tracklist stay readable above the sun on every one of the 14 themes.
12. On every one of the 14 themes, the bigger sun and its new glow look intended: no hard edges, no square frame and no glow that washes out the sky. The effect has to look right on `carlcox` and `prydz` in particular.
13. `themes.js` is changed only if one theme looks clearly broken with the new effect. Then the fix is limited to that theme's sun-related values and keeps its brand colours.
14. If `themes.js` changes, its `<script src="themes.js?v=NN">` in `index.html` is bumped to a higher number than 54.

## Acceptance criteria
1. `grep -n -A6 '^    \.sun {' index.html` shows `width: min(Xvw, Ypx)` and `height: min(Xvw, Ypx)` with the same X (36-42) and Y (364-416).
2. The same `.sun` rule still contains `left: 50%`, `bottom: 16vh` and `translateX(-50%)`.
3. The markup inside `<div class="sun">` in `index.html` contains one more child element than today (e.g. `<div class="sun-rays"></div>`). It comes before `.sun-core` in source order, or is placed behind it with `z-index`.
4. The CSS rule for the new layer uses `conic-gradient`/`repeating-conic-gradient`/`radial-gradient` and/or `box-shadow`, with colours given only as `var(--…)` theme variables inside `color-mix`. No new hex or `rgb()` hue literal appears in it (`grep` the rule).
5. The new layer has an `animation` with a duration of 20s or more, backed by an `@keyframes` rule in `index.html`.
6. The `.sun-corona` rule has an `inset` more negative than `-42%`.
7. The `.sun-corona` rule has higher `color-mix` percentages and/or a higher `opacity` than today (42/38/16/6, opacity 0.9).
8. `grep -n 'filter' index.html` shows no `filter:` (other than `backdrop-filter`) in any `.sun*` rule.
9. The `@media (prefers-reduced-motion: reduce)` block at the top of the stylesheet lists the new layer's class with `animation: none`.
10. With DevTools "Emulate prefers-reduced-motion: reduce" on, the sun and its new layer are static at `http://127.0.0.1:8766` (`python3 serve.py`).
11. At 375px, 768px and 1440px viewport widths, `document.documentElement.scrollWidth <= window.innerWidth` in the console, and there is no horizontal scrollbar.
12. At `http://127.0.0.1:8766`, picking each of the 14 sets in turn shows a visibly bigger sun on the horizon line, with a soft glow/rays around it in that set's colours. There are no rectangular edges, and the header text, player and tracklist stay readable. This includes `carlcox` and `prydz`.
13. Clicking controls that overlap the sun's area (e.g. the player and tracklist) still works.
14. If `git diff origin/main -- themes.js` is non-empty, the `themes.js` script tag in `index.html` shows `?v=55` or higher, and the diff changes only sun-related values of the theme(s) concerned.

## Out of scope
- Changing the `--sky` gradients, `.sky-drift-a/b`, `.sky-veil`, `.grain` or `.horizon` (colours, position or animation).
- Changing any theme's brand colours (`accent`, `gold`, `cream`, `sky`, etc.) or reworking the 14 palettes. The only exception is the narrow per-theme sun fix in Requirement 13.
- Moving the sun off-centre, changing its rise animation's path, or making it react to audio (`analyser.js`).
- Adding a settings toggle, a new theme variable for the sun size, or per-theme size options.
- Changing `serve.py`, the CDN scripts or stylesheets, `.gitignore`, `sets.js`, `bios.js` or the logo (`.logo3d-sun`).
- Adding C4 diagrams or an ADR: this is a style change inside the existing page, with no new component or decision.

## Assumptions
- Target size of about 1.5x (`min(39vw, 390px)` is the midpoint). Reason: intake's 1.4x-1.6x range, and a vw-based value keeps it proportional on mobile.
- One new rays/corona layer plus a stronger existing corona is enough for "a nice effect around". Reason: smallest change that is clearly visible, and it builds on the existing layers as intake asked.
- Visual checks are manual in a browser. Reason: the repo has no test runner, and `checks.sh` covers only syntax and data.
- No doc update is required. Reason: the repo has no `AGENTS.md` or `docs/`, and the change stays inside the existing page component.
