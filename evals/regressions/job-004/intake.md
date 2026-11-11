DECISION: ACCEPT
RISK: low
SURFACES: ui
RESCOPED: yes

## Summary
- Thanks for the answer: "for all 14 themes, bigger sun with a nice effect around".
- The sun and its glow layers are shared by every set and take their colours from each theme, so one change to the shared sun reaches all 14 themes.
- Accepted: a bigger sun with a richer, more visible glow around it, in each theme's existing colours.
- Left out: reworking the sky gradients or moving away from the artist/label brand colours, since your answer didn't ask for that.

## Scope
Build:
- Make the sun clearly bigger on every set. Today it is `min(26vw, 260px)`. Aim for roughly 1.4x to 1.6x, with a cap so it stays in proportion on large screens and doesn't swamp small or mobile screens.
- Give it a nicer effect around it: a wider, softer and more visible glow, layered rays or corona, building on the existing corona, halo, ring and sheen layers. It should still breathe gently as it does now.
- The effect takes its colours from each theme's current variables (`--sun`, `--gold`, `--accent-glow`, `--cream`, `--accent-soft`), so all 14 themes get it in their own palette. Check it on all 14, including the dark or monochrome ones (for example the black/white/grey and the black/gold themes), so that each one looks good.
- Keep the sun sitting on the horizon line, keep the tracklist, player and text readable above it, and keep the page from scrolling sideways.
- Respect `prefers-reduced-motion`: any new animation has to stop there like the existing ones do.
- Don't use `filter: blur` on the sun (the CSS notes that Safari draws a rectangular frame with it). Use gradients and shadows as the current layers do.
- If `themes.js` changes, bump its `?v=NN` in `index.html`.

Left out:
- Changing the sky gradients, drift glows, grain or horizon colours.
- Changing any theme's brand colours. A per-theme sun tweak is fine only if one theme looks clearly broken with the new effect.

## Why
The sun is built from shared layers in `index.html` (`.sun`, `.sun-corona`, `.sun-halo`, `.sun-core`, `.sun-sheen`, `.sun-ring`) sized by one `width/height` rule. Its colours come from per-set variables that `themes.js` sets for all 14 themes, so "all 14 themes, bigger sun" fits in one small CSS change that is easy to check visually. You didn't answer the brand-colour question and didn't ask for colour changes, so the safest reading is to keep the palettes as they are.
