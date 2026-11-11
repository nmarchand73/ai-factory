"""Tests for the multi-target factory scripts, with a fake gh and local bare repos.

Run: python3 -m unittest tests/test_factory.py
"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def sh(*cmd, cwd=None, env=None, ok=True):
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env={**os.environ, **GIT_ENV, **(env or {})})
    if ok and res.returncode != 0:
        raise AssertionError(f"{cmd} failed:\n{res.stdout}\n{res.stderr}")
    return res


class Factory(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.root = self.tmp / "factory-root"
        (self.root / "factory" / "bin").mkdir(parents=True)
        for name in ("job", "gate", "route", "target"):
            shutil.copy(SRC / "factory" / "bin" / name, self.root / "factory" / "bin" / name)
        config = json.loads((SRC / "factory" / "config.json").read_text())
        config["concurrency"] = 2
        config["targets"] = {}
        self.state = self.tmp / "gh.json"
        self.state.write_text(json.dumps({"user": "tester"}))
        self.env = {"FACTORY_GH": str(SRC / "tests" / "fake_gh.py"), "FAKE_GH_STATE": str(self.state),
                    "CLAUDE_CONFIG_DIR": str(self.tmp / "claude")}
        for name in ("alpha", "beta"):
            self.make_target(config, name)
        (self.root / "factory" / "config.json").write_text(json.dumps(config))

    def make_target(self, config, name):
        repo = f"me/{name}"
        bare = self.tmp / f"{name}.git"
        seed = self.tmp / f"{name}-seed"
        sh("git", "init", "-q", "--bare", "-b", "main", str(bare))
        sh("git", "init", "-q", "-b", "main", str(seed))
        (seed / "app.txt").write_text("hello\n")
        (seed / ".github" / "workflows").mkdir(parents=True)
        (seed / ".github" / "workflows" / "ci.yml").write_text("on: push\n")
        sh("git", "add", "-A", cwd=seed)
        sh("git", "commit", "-q", "-m", "init", cwd=seed)
        sh("git", "push", "-q", str(bare), "main", cwd=seed)
        clone = self.root / "targets" / name / "repo"
        sh("git", "clone", "-q", str(bare), str(clone))
        (self.root / "targets" / name / "checks.sh").write_text("#!/usr/bin/env bash\nset -e\ntest -f app.txt\n")
        config["targets"][name] = {"repo": repo, "base_branch": "main", "merge_method": "squash",
                                   "protected_paths": [".github/workflows/*"]}

    # -- helpers
    def gh_state(self):
        return json.loads(self.state.read_text())

    def add_issue(self, repo, number, title, labels=("factory",)):
        st = self.gh_state()
        st.setdefault("issues", {}).setdefault(repo, {})[str(number)] = {"title": title, "state": "OPEN", "labels": list(labels)}
        self.state.write_text(json.dumps(st))

    def bin(self, name, *args, ok=True, stdin=None):
        res = subprocess.run([str(self.root / "factory" / "bin" / name), *args], cwd=self.root, input=stdin,
                             capture_output=True, text=True, env={**os.environ, **GIT_ENV, **self.env})
        if ok and res.returncode != 0:
            raise AssertionError(f"{name} {args} failed:\n{res.stdout}\n{res.stderr}")
        return res

    def job_json(self, job_id):
        return json.loads((self.root / "factory" / "jobs" / job_id / "job.json").read_text())

    def to_build(self, target, number):
        """Drive a job to the point where the builder has pushed a commit and opened a PR."""
        job_id = self.bin("job", "create", target, str(number)).stdout.strip()
        d = self.root / "factory" / "jobs" / job_id
        (d / "intake.md").write_text("DECISION: ACCEPT\nRISK: low\nSURFACES: none\nRESCOPED: no\n\n## Summary\n- ok\n\n## Scope\nx\n")
        self.bin("route", job_id)
        self.bin("job", "advance", job_id, "spec")
        (d / "spec.md").write_text("# spec\n")
        self.bin("job", "advance", job_id, "build")
        return job_id, d

    def build_commit(self, job_id, d, path="feature.txt", pr=1, repo=None):
        job = self.job_json(job_id)
        wt = Path(job["worktree"])
        (wt / path).parent.mkdir(parents=True, exist_ok=True)
        (wt / path).write_text("x\n")
        sh("git", "add", "-A", cwd=wt)
        sh("git", "commit", "-q", "-m", "feat", cwd=wt)
        sh("git", "push", "-q", "origin", job["branch"], cwd=wt)
        st = self.gh_state()
        st["prs"].setdefault(repo or f"me/{job['target']}", {})[str(pr)] = {"head": job["branch"], "state": "OPEN"}
        self.state.write_text(json.dumps(st))
        (d / "build.md").write_text("STATUS: READY\n")

    # -- tests
    def test_queue_lists_every_target_with_a_target_column(self):
        self.add_issue("me/alpha", 3, "Alpha thing")
        self.add_issue("me/beta", 3, "Beta thing")
        rows = [r.split("\t") for r in self.bin("job", "queue").stdout.strip().splitlines()]
        self.assertIn(["new", "alpha", "3", "-", "-", "Alpha thing"], rows)
        self.assertIn(["new", "beta", "3", "-", "-", "Beta thing"], rows)

    def test_concurrency_is_shared_across_targets(self):
        for n, repo in enumerate(("me/alpha", "me/beta", "me/alpha"), start=1):
            self.add_issue(repo, n, f"t{n}")
        kinds = [r.split("\t")[0] for r in self.bin("job", "queue").stdout.strip().splitlines()]
        self.assertEqual(kinds.count("new"), 2)
        self.assertEqual(kinds.count("hold"), 1)

    def test_bare_issue_number_is_ambiguous_with_two_targets(self):
        self.add_issue("me/alpha", 3, "A")
        self.bin("job", "create", "alpha", "3")
        res = self.bin("job", "summary", "3", ok=False)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("ambiguous", res.stderr)
        self.assertEqual(self.bin("job", "summary", "alpha#3").returncode, 0)

    def test_job_ids_are_global_and_worktrees_live_outside_the_target(self):
        self.add_issue("me/alpha", 1, "First")
        self.add_issue("me/beta", 1, "Second")
        a = self.bin("job", "create", "alpha", "1").stdout.strip()
        b = self.bin("job", "create", "beta", "1").stdout.strip()
        self.assertTrue(a.startswith("001-") and b.startswith("002-"))
        self.assertEqual(self.job_json(a)["worktree"], str(self.root / "workspaces" / "alpha" / a))
        self.assertEqual(self.job_json(b)["target"], "beta")

    def test_every_gh_call_names_its_repo(self):
        self.add_issue("me/alpha", 1, "First")
        self.bin("job", "queue")
        self.bin("job", "create", "alpha", "1")
        calls = self.gh_state()["calls"]
        self.assertTrue(calls)
        for argv in calls:
            if argv[0] != "api":
                self.assertIn("--repo", argv, argv)

    def test_full_pipeline_to_merge(self):
        self.add_issue("me/alpha", 7, "Add feature")
        job_id, d = self.to_build("alpha", 7)
        wt = Path(self.job_json(job_id)["worktree"])
        self.assertTrue(wt.exists())
        self.assertTrue(str(wt).startswith(str(self.root / "workspaces" / "alpha")))
        self.build_commit(job_id, d)
        self.bin("job", "advance", job_id, "gate")
        self.assertEqual(self.job_json(job_id)["pr"], 1)
        self.assertIn("GATE: PASS", self.bin("gate", job_id).stdout)
        self.bin("job", "advance", job_id, "review")
        rd = d / "round-1"
        (rd / "review-code.md").write_text("VERDICT: PASS\n")
        self.bin("job", "sync", job_id)
        self.bin("job", "advance", job_id, "approve")
        (d / "decision.md").write_text("APPROVE\n\n## Summary\n- ok\n")
        self.assertIn("merged", self.bin("job", "merge", job_id).stdout)
        self.assertEqual(self.job_json(job_id)["stage"], "merged")
        self.assertEqual(self.gh_state()["prs"]["me/alpha"]["1"]["state"], "MERGED")
        self.assertFalse(wt.exists())

    def test_gate_uses_the_targets_own_checks_and_protects_its_paths(self):
        self.add_issue("me/beta", 2, "Touch CI")
        job_id, d = self.to_build("beta", 2)
        self.build_commit(job_id, d, path=".github/workflows/ci.yml", pr=1)
        wt = Path(self.job_json(job_id)["worktree"])
        (wt / ".github/workflows/ci.yml").write_text("on: pull_request\n")
        sh("git", "commit", "-qam", "edit ci", cwd=wt)
        sh("git", "push", "-q", "origin", self.job_json(job_id)["branch"], cwd=wt)
        res = self.bin("gate", job_id, ok=False)
        self.assertEqual(res.returncode, 1)
        self.assertIn("protected", res.stdout)

    def test_a_branch_cannot_replace_the_targets_checks(self):
        self.add_issue("me/alpha", 4, "Sneaky")
        job_id, d = self.to_build("alpha", 4)
        wt = Path(self.job_json(job_id)["worktree"])
        (wt / "app.txt").unlink()  # the factory's checks.sh requires app.txt
        self.build_commit(job_id, d, path="checks.sh")
        res = self.bin("gate", job_id, ok=False)
        self.assertEqual(res.returncode, 1)
        self.assertIn("GATE: FAIL", res.stdout)

    def test_reject_removes_labels_and_cleans_the_worktree(self):
        self.add_issue("me/alpha", 5, "Nope")
        job_id = self.bin("job", "create", "alpha", "5").stdout.strip()
        d = self.root / "factory" / "jobs" / job_id
        (d / "intake.md").write_text("DECISION: NEEDS-INFO\nRISK: low\nSURFACES: none\nRESCOPED: no\n\n## Summary\n- q\n\n## Question\nwhat?\n")
        self.bin("job", "advance", job_id, "needs-info")
        self.assertIn("factory:needs-info", self.gh_state()["issues"]["me/alpha"]["5"]["labels"])
        self.bin("job", "reject", job_id, stdin="out of scope")
        self.assertEqual(self.job_json(job_id)["stage"], "rejected")
        self.assertNotIn("factory", self.gh_state()["issues"]["me/alpha"]["5"]["labels"])

    def test_target_add_refuses_an_empty_repo(self):
        st = self.gh_state()
        st["repos"] = {"me/empty": {"viewerPermission": "ADMIN", "defaultBranchRef": None}}
        self.state.write_text(json.dumps(st))
        res = self.bin("target", "add", "empty", "me/empty", ok=False)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("no commits yet", res.stderr)
        self.assertNotIn("empty", json.loads((self.root / "factory" / "config.json").read_text())["targets"])

    def test_a_model_without_a_price_does_not_break_the_job(self):
        import re as _re
        self.add_issue("me/alpha", 9, "Costs")
        job_id = self.bin("job", "create", "alpha", "9").stdout.strip()
        slug = _re.sub(r"[^A-Za-z0-9]", "-", str(self.root))
        sub = self.tmp / "claude" / "projects" / slug / "session1" / "subagents"
        sub.mkdir(parents=True)
        needle = f"Job folder: {self.root / 'factory' / 'jobs' / job_id}/"
        first = {"message": {"content": f"{needle} Target: alpha"}}
        usage = {"id": "m1", "model": "claude-unknown-9", "usage": {"input_tokens": 1000, "output_tokens": 1000}}
        second = {"type": "assistant", "message": usage}
        (sub / "agent-1.jsonl").write_text(json.dumps(first) + "\n" + json.dumps(second) + "\n")
        res = self.bin("job", "sync", job_id)
        self.assertIn("no price for model claude-unknown-9", res.stderr)
        self.assertEqual(self.job_json(job_id)["cost_usd"], 0.0)

    def test_cost_is_split_by_agent_type(self):
        import re as _re
        self.add_issue("me/alpha", 10, "Split")
        job_id = self.bin("job", "create", "alpha", "10").stdout.strip()
        slug = _re.sub(r"[^A-Za-z0-9]", "-", str(self.root))
        sub = self.tmp / "claude" / "projects" / slug / "session1" / "subagents"
        sub.mkdir(parents=True)
        needle = f"Job folder: {self.root / 'factory' / 'jobs' / job_id}/"
        prices = json.loads((self.root / "factory" / "config.json").read_text())["prices_usd_per_mtok"]
        for n, (agent, model) in enumerate([("builder", "claude-opus-5-5"), ("reviewer-code", "claude-haiku-5-5"),
                                             ("reviewer-ux", "claude-sonnet-5-5")]):
            first = {"message": {"content": f"{needle} Target: alpha"}}
            usage = {"id": f"m{n}", "model": model, "usage": {"input_tokens": 1000000, "output_tokens": 0}}
            (sub / f"agent-{n}.jsonl").write_text(json.dumps(first) + "\n" + json.dumps({"type": "assistant", "message": usage}) + "\n")
            (sub / f"agent-{n}.meta.json").write_text(json.dumps({"agentType": agent}))
        self.bin("job", "sync", job_id)
        job = self.job_json(job_id)
        self.assertEqual(set(job["cost_by_agent"]), {"builder", "reviewer-code", "reviewer-ux"})
        self.assertAlmostEqual(job["cost_by_agent"]["builder"], prices["claude-opus-5-5"]["input"], places=3)
        self.assertAlmostEqual(job["cost_usd"], sum(job["cost_by_agent"].values()), places=3)

    def test_unknown_target_is_refused(self):
        res = self.bin("job", "create", "nope", "1", ok=False)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("unknown target", res.stderr)


if __name__ == "__main__":
    unittest.main()
