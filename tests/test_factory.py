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

    def build_commit(self, job_id, d, path="feature.txt", pr=1, repo=None, text="x\n"):
        job = self.job_json(job_id)
        wt = Path(job["worktree"])
        (wt / path).parent.mkdir(parents=True, exist_ok=True)
        (wt / path).write_text(text)
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

    def test_an_archived_target_is_not_queued_or_built_and_can_come_back(self):
        self.add_issue("me/alpha", 4, "A")
        self.add_issue("me/beta", 5, "B")
        self.assertIn("beta: archived", self.bin("target", "archive", "beta").stdout)
        cfg = json.loads((self.root / "factory" / "config.json").read_text())
        self.assertTrue(cfg["targets"]["beta"]["archived"])
        self.assertIn("archived", self.bin("target", "list").stdout)
        q = self.bin("job", "queue").stdout
        self.assertIn("alpha", q)
        self.assertNotIn("beta", q)
        self.assertIn("archived", self.bin("job", "queue", "beta", ok=False).stderr)
        self.assertIn("archived", self.bin("job", "create", "beta", "5", ok=False).stderr)
        self.assertEqual(self.bin("job", "create", "4").returncode, 0)          # one active target: a bare number is fine again
        self.bin("target", "unarchive", "beta")
        self.assertNotIn("archived", json.loads((self.root / "factory" / "config.json").read_text())["targets"]["beta"])
        self.assertIn("beta", self.bin("job", "queue").stdout)

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

    def in_review(self, number, path, text):
        self.add_issue("me/alpha", number, f"Feature {number}")
        job_id, d = self.to_build("alpha", number)
        self.build_commit(job_id, d, path=path, pr=number, text=text)
        self.bin("job", "advance", job_id, "gate")
        self.bin("gate", job_id)
        self.bin("job", "advance", job_id, "review")
        return job_id

    def test_the_diff_adds_the_security_reviewer_when_intake_rated_the_job_ui_only(self):
        safe = self.in_review(21, "style.css", ".sun { width: 40vw; }\n")
        self.assertIn("no security trigger", self.bin("route", safe, "--diff").stdout)
        self.assertNotIn("security", self.job_json(safe)["agents"]["reviewers"])
        risky = self.in_review(22, "search.js", "box.innerHTML = query;\n")
        out = self.bin("route", risky, "--diff").stdout
        self.assertIn("security reviewer added", out)
        self.assertIn("search.js", out)
        self.assertIn("security", self.job_json(risky)["agents"]["reviewers"])
        self.assertIn("code", self.job_json(risky)["agents"]["reviewers"])      # adds, never replaces
        self.assertIn("already routed", self.bin("route", risky, "--diff").stdout)

    def test_a_sensitive_path_alone_adds_the_security_reviewer(self):
        job_id = self.in_review(23, "deploy.sh", "echo hi\n")
        self.assertIn("deploy.sh matches", self.bin("route", job_id, "--diff").stdout)

    def test_route_diff_needs_a_job_in_review_and_cannot_drop_a_reviewer(self):
        self.add_issue("me/alpha", 24, "Early")
        job_id, _ = self.to_build("alpha", 24)
        self.assertIn("once the gate has passed", self.bin("route", job_id, "--diff", ok=False).stderr)
        review = self.in_review(25, "a.txt", "x\n")
        res = self.bin("job", "agents", review, json.dumps({"reviewers": {}}), ok=False)
        self.assertIn("can't be removed", res.stderr)

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
        out = self.bin("job", "summary").stdout
        self.assertIn("cost by project, step and agent", out)
        self.assertRegex(out, r"alpha\s+\$[\d.]+\s+\(1 job\)")
        self.assertRegex(out, r"Build\s+\$[\d.]+\s+builder")
        self.assertRegex(out, r"Review\s+\$[\d.]+\s+(code|ux)")

    def test_orchestrator_cost_is_shared_between_running_jobs(self):
        import re as _re
        from datetime import datetime, timedelta, timezone
        self.add_issue("me/alpha", 11, "One")
        self.add_issue("me/beta", 12, "Two")
        a = self.bin("job", "create", "alpha", "11").stdout.strip()
        b = self.bin("job", "create", "beta", "12").stdout.strip()
        start = datetime.now(timezone.utc)
        iso = lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        slug = _re.sub(r"[^A-Za-z0-9]", "-", str(self.root))
        proj = self.tmp / "claude" / "projects" / slug
        proj.mkdir(parents=True)

        def asst(mid, when):
            return {"type": "assistant", "timestamp": iso(when),
                    "message": {"id": mid, "model": "claude-opus-5-5", "usage": {"input_tokens": 1000000, "output_tokens": 0}}}
        skill = {"type": "assistant", "timestamp": iso(start - timedelta(hours=2)),
                 "message": {"id": "s0", "model": "claude-opus-5-5", "usage": {"input_tokens": 0, "output_tokens": 0},
                             "content": [{"type": "tool_use", "name": "Skill", "input": {"skill": "factory"}}]}}
        lines = [asst("before", start - timedelta(hours=3)),   # before /factory: not the factory's
                 skill,
                 asst("idle", start - timedelta(hours=1)),    # after /factory, no job running: overhead
                 asst("busy", start + timedelta(seconds=30))]  # two jobs running: shared
        (proj / "session1.jsonl").write_text("\n".join(json.dumps(x) for x in lines) + "\n")
        self.bin("job", "sync", a)
        self.bin("job", "sync", b)
        price = json.loads((self.root / "factory" / "config.json").read_text())["prices_usd_per_mtok"]["claude-opus-5-5"]["input"]
        for jid in (a, b):
            self.assertAlmostEqual(self.job_json(jid)["cost_by_agent"]["orchestrator"], price / 2, places=3)
        over = json.loads((self.root / "factory" / "jobs" / "_orchestration.json").read_text())
        self.assertAlmostEqual(over["outside_jobs_usd"], price, places=3)
        out = self.bin("job", "summary").stdout
        self.assertIn("orchestration while no job was running", out)
        self.assertRegex(out, r"Orchestr\.\s+\$")

    def test_orchestration_while_a_job_waits_for_its_author_is_not_billed_to_it(self):
        import re as _re
        from datetime import datetime, timedelta, timezone
        self.add_issue("me/alpha", 15, "Waits")
        a = self.bin("job", "create", "alpha", "15").stdout.strip()
        base = datetime.now(timezone.utc) - timedelta(minutes=30)
        iso = lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        path = self.root / "factory" / "jobs" / a / "job.json"
        job = json.loads(path.read_text())
        job.update(started=iso(base), ended=iso(base + timedelta(minutes=20)), stage="merged", history=[
            {"stage": "intake", "ts": iso(base)}, {"stage": "needs-info", "ts": iso(base + timedelta(minutes=5))},
            {"stage": "intake", "ts": iso(base + timedelta(minutes=15))}, {"stage": "merged", "ts": iso(base + timedelta(minutes=20))}])
        path.write_text(json.dumps(job))
        slug = _re.sub(r"[^A-Za-z0-9]", "-", str(self.root))
        proj = self.tmp / "claude" / "projects" / slug
        proj.mkdir(parents=True)
        asst = lambda mid, when: {"type": "assistant", "timestamp": iso(when), "message": {
            "id": mid, "model": "claude-opus-5-5", "usage": {"input_tokens": 1000000, "output_tokens": 0}}}
        skill = {"type": "assistant", "timestamp": iso(base - timedelta(minutes=1)), "message": {
            "id": "s0", "model": "claude-opus-5-5", "usage": {"input_tokens": 0, "output_tokens": 0},
            "content": [{"type": "tool_use", "name": "Skill", "input": {"skill": "factory"}}]}}
        lines = [skill, asst("running", base + timedelta(minutes=1)), asst("parked", base + timedelta(minutes=10)),
                 asst("much-later", base + timedelta(hours=5))]
        (proj / "run.jsonl").write_text("\n".join(json.dumps(x) for x in lines) + "\n")
        other = [{"type": "assistant", "timestamp": iso(base - timedelta(hours=3)), "message": {   # a session that ran no job
            "id": "d0", "model": "claude-opus-5-5", "usage": {"input_tokens": 0, "output_tokens": 0},
            "content": [{"type": "tool_use", "name": "Skill", "input": {"skill": "factory"}}]}}, asst("dev", base - timedelta(hours=2))]
        (proj / "dev.jsonl").write_text("\n".join(json.dumps(x) for x in other) + "\n")
        self.bin("job", "sync", a)
        price = json.loads((self.root / "factory" / "config.json").read_text())["prices_usd_per_mtok"]["claude-opus-5-5"]["input"]
        self.assertAlmostEqual(self.job_json(a)["cost_by_agent"]["orchestrator"], price, places=3)   # only the running minute
        over = json.loads((self.root / "factory" / "jobs" / "_orchestration.json").read_text())
        self.assertAlmostEqual(over["outside_jobs_usd"], price, places=3)       # the parked minute, inside a run
        self.assertAlmostEqual(over["outside_sessions_usd"], 2 * price, places=3)  # a dev session and a message hours later

    def test_queue_gives_the_pr_url_for_a_job_that_needs_a_human(self):
        self.add_issue("me/alpha", 13, "Needs me")
        job_id = self.bin("job", "create", "alpha", "13").stdout.strip()
        path = self.root / "factory" / "jobs" / job_id / "job.json"
        job = json.loads(path.read_text())
        job.update(stage="needs-human", pr=21, pr_url="https://github.com/me/alpha/pull/21")
        path.write_text(json.dumps(job))
        st = self.gh_state()
        st.setdefault("prs", {}).setdefault("me/alpha", {})["21"] = {"head": job["branch"], "state": "OPEN"}
        self.state.write_text(json.dumps(st))
        out = self.bin("job", "queue", "alpha").stdout
        self.assertIn("merge https://github.com/me/alpha/pull/21, or give feedback", out)

    def test_queue_gives_the_issue_url_for_a_job_waiting_for_its_author(self):
        self.add_issue("me/alpha", 14, "Question")
        job_id = self.bin("job", "create", "alpha", "14").stdout.strip()
        path = self.root / "factory" / "jobs" / job_id / "job.json"
        job = json.loads(path.read_text())
        job["stage"] = "needs-info"
        path.write_text(json.dumps(job))
        out = self.bin("job", "queue", "alpha").stdout
        self.assertIn("waiting for the author: https://github.com/me/alpha/issues/14", out)

    def test_unknown_target_is_refused(self):
        res = self.bin("job", "create", "nope", "1", ok=False)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("unknown target", res.stderr)


if __name__ == "__main__":
    unittest.main()
