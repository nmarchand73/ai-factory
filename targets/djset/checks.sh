#!/usr/bin/env bash
# Checks for the target "djset" (Horizon: static site, no build, no dependencies).
# The gate runs this script from the factory, inside a job's worktree, so a branch
# can't edit the checks it is judged by. Fast, deterministic, non-interactive,
# nothing that rewrites files. Exit non-zero on any failure.
set -euo pipefail

# 1. Every JS file parses
for f in $(git ls-files '*.js'); do
  node --check "$f"
done

# 2. serve.py parses (ast, so no __pycache__ is written)
python3 -c "import ast,sys; ast.parse(open('serve.py').read(), 'serve.py')"

# 3. index.html exists and its local scripts/styles exist
test -f index.html
python3 - <<'PY'
import pathlib, re, sys
html = pathlib.Path("index.html").read_text(encoding="utf-8")
refs = re.findall(r'(?:src|href)="(?!https?:|//|#|mailto:|data:)([^"?#]+)', html)
missing = sorted({r for r in refs if not pathlib.Path(r).exists()})
if missing:
    sys.exit("index.html references missing files: %s" % missing)
PY

# 4. The sets data is well formed (sets.js is data the whole app depends on)
node - <<'JS'
const fs = require("fs"), vm = require("vm");
global.window = {};
vm.runInThisContext(fs.readFileSync("sets.js", "utf8"), { filename: "sets.js" });
const sets = window.SETS, errs = [], ids = new Set();
if (!Array.isArray(sets) || !sets.length) errs.push("window.SETS must be a non-empty array");
for (const s of sets || []) {
  if (!s.id || ids.has(s.id)) errs.push("missing or duplicate set id: " + s.id);
  ids.add(s.id);
  if (!s.artist) errs.push(s.id + ": no artist");
  if (!Array.isArray(s.tracks) || !s.tracks.length) { errs.push(s.id + ": no tracks"); continue; }
  let prev = -1;
  for (const t of s.tracks) {
    if (typeof t.seconds !== "number" || t.seconds < prev || !t.title)
      errs.push(s.id + ": bad track at " + t.at);
    prev = t.seconds;
  }
}
if (errs.length) { console.error(errs.join("\n")); process.exit(1); }
JS

echo "djset checks passed"
