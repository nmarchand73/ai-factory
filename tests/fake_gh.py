#!/usr/bin/env python3
"""A tiny stand-in for the gh CLI, backed by the JSON file in $FAKE_GH_STATE.

It implements only what factory/bin/job and factory/bin/target call, and it
records every invocation under "calls" so tests can assert that each call named
its repo explicitly.
"""
import json
import os
import sys

path = os.environ["FAKE_GH_STATE"]
state = json.load(open(path))
argv = sys.argv[1:]
state.setdefault("calls", []).append(argv)


def flag(name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


def done(out=None):
    json.dump(state, open(path, "w"))
    if out is not None:
        print(out if isinstance(out, str) else json.dumps(out))
    sys.exit(0)


repo = flag("--repo")
if argv[0] != "api" and not repo and argv[:2] != ["auth", "status"] and argv[:2] != ["repo", "view"]:
    print("fake gh: missing --repo", file=sys.stderr)
    done() if False else sys.exit(3)
issues = state.setdefault("issues", {}).setdefault(repo or "-", {})
prs = state.setdefault("prs", {}).setdefault(repo or "-", {})
cmd = argv[:2]

if cmd == ["repo", "view"]:
    r = state.get("repos", {}).get(argv[2], {"viewerPermission": "WRITE", "defaultBranchRef": {"name": "main"}})
    done(r)
if cmd == ["api", "user"]:
    done(state.get("user", "tester"))
if cmd == ["issue", "list"]:
    if "--label" in argv:
        done([])  # gh --label goes through the search index, which lags behind new issues
    done([{"number": int(n), "title": i["title"], "labels": [{"name": l} for l in i["labels"]]}
          for n, i in issues.items() if i["state"] == "OPEN"])
if cmd == ["issue", "view"]:
    i = issues[argv[2]]
    done({"number": int(argv[2]), "title": i["title"], "body": i.get("body", ""), "author": {"login": "alice"},
          "labels": [{"name": l} for l in i["labels"]], "state": i["state"],
          "url": f"https://github.com/{repo}/issues/{argv[2]}",
          "comments": [{"author": {"login": "tester"}, "body": b, "createdAt": "2026-01-01T00:00:00Z"}
                       for b in i.get("comments", [])]})
if cmd == ["issue", "comment"]:
    issues[argv[2]].setdefault("comments", []).append(flag("--body"))
    done()
if cmd == ["issue", "edit"]:
    i = issues[argv[2]]
    if "--add-label" in argv:
        i["labels"] += [l for l in flag("--add-label").split(",") if l not in i["labels"]]
    if "--remove-label" in argv:
        i["labels"] = [l for l in i["labels"] if l not in flag("--remove-label").split(",")]
    done()
if cmd == ["pr", "list"]:
    done([{"number": int(n), "url": f"https://github.com/{repo}/pull/{n}"} for n, p in prs.items()
          if p["head"] == flag("--head") and p["state"] == "OPEN"])
if cmd == ["pr", "view"]:
    p = prs[argv[2]]
    done({"state": p["state"], "isDraft": p.get("draft", True)})
if cmd == ["pr", "ready"]:
    prs[argv[2]]["draft"] = False
    done()
if cmd == ["pr", "comment"]:
    prs[argv[2]].setdefault("comments", []).append(flag("--body"))
    done()
if cmd == ["pr", "close"]:
    prs[argv[2]]["state"] = "CLOSED"
    done()
if cmd == ["pr", "merge"]:
    prs[argv[2]]["state"] = "MERGED"
    done()
print(f"fake gh: unsupported {argv}", file=sys.stderr)
sys.exit(2)
