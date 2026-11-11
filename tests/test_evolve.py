"""factory/bin/evolve: cycles, plans, per-change approval, versions, rollback, measurement, board."""
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
import importlib.machinery
import importlib.util
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]


def body_line(path):
    """A stable line of a skill file's body to anchor a change on."""
    text = path.read_text()
    body = text.split("\n---\n", 1)[1]
    return next(l for l in body.splitlines() if l.strip() and len(l) > 20 and body.count(l) == 1)


class Evolve(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.root = self.tmp / "root"
        (self.root / "factory" / "bin").mkdir(parents=True)
        for name in ("evolve", "eval", "job", "gate", "route", "target"):
            shutil.copy(SRC / "factory" / "bin" / name, self.root / "factory" / "bin" / name)
        shutil.copy(SRC / "factory" / "config.json", self.root / "factory" / "config.json")
        shutil.copytree(SRC / "evals", self.root / "evals")
        shutil.copytree(SRC / ".claude", self.root / ".claude")
        self.env = {**os.environ, "CLAUDE_CONFIG_DIR": str(self.tmp / "claude"), "FACTORY_OPERATOR": "alice"}
        self.evo = self.root / "factory" / "evolution"
        self.builder = self.root / ".claude" / "agents" / "builder.md"
        self.orch = self.root / ".claude" / "skills" / "factory" / "SKILL.md"

    def evolve(self, *args, ok=True):
        res = subprocess.run([str(self.root / "factory" / "bin" / "evolve"), *args], cwd=self.root,
                             capture_output=True, text=True, env=self.env)
        if ok and res.returncode != 0:
            raise AssertionError(f"evolve {args} failed:\n{res.stdout}\n{res.stderr}")
        if not ok and res.returncode == 0:
            raise AssertionError(f"evolve {args} should have failed:\n{res.stdout}")
        return res

    def change(self, cid="ch1", target=None, old=None, new=None, **extra):
        old = old if old is not None else body_line(self.builder)
        c = {"id": cid, "gap": {"summary": "checks are not run before committing", "evidence": "builder.runs_checks 40 (n=3)"},
             "old": old, "new": new if new is not None else old + "\nRun the checks before every commit.",
             "expected_impact": {"criterion": "runs_checks", "direction": "up", "delta": 20},
             "priority": "P1", "confidence": "medium"}
        if target:
            c["target"] = target
        c.update(extra)
        return c

    def plan(self, cid, agent_changes=(), orch_changes=(), **extra):
        p = {"previous_changes_review": [], "agents": {"builder": {"issues": [
            {"gap": "runs_checks", "evidence": "n=3, 40", "root_cause": "prompt"}], "changes": list(agent_changes)}},
            "orchestrator": {"issues": [], "changes": list(orch_changes)},
            "system": [{"recommendation": "Run the gate before review", "priority": "P2", "confidence": "low"}]}
        p.update(extra)
        d = self.evo / "cycles" / cid
        d.mkdir(parents=True, exist_ok=True)
        (d / "plan.json").write_text(json.dumps(p))
        return p

    def start(self):
        self.evolve("init")
        return self.evolve("cycle", "start").stdout.strip()

    def registry(self):
        return json.loads((self.evo / "registry.json").read_text())

    def audit(self):
        return [json.loads(l) for l in (self.evo / "audit.jsonl").read_text().splitlines()]

    def status_of(self, cid, change):
        rows = [e for e in self.audit() if e.get("cycle") == cid and e.get("change") == change]
        return rows[-1]["event"]


class Versions(Evolve):
    def test_init_registers_baselines_and_protects_the_grader(self):
        self.evolve("init")
        skills = self.registry()["skills"]
        self.assertIn("agent:builder", skills)
        self.assertIn("skill:factory", skills)
        self.assertNotIn("agent:eval-judge", skills)
        self.assertNotIn("agent:retrospective", skills)
        self.assertEqual(skills["agent:builder"]["current"], "1.0")
        snap = self.evo / "versions" / "agent__builder" / "v1.0.md"
        self.assertEqual(snap.read_text(), self.builder.read_text())

    def test_a_manual_edit_becomes_a_version(self):
        self.evolve("init")
        self.builder.write_text(self.builder.read_text() + "\nA manual note.\n")
        self.evolve("init")
        e = self.registry()["skills"]["agent:builder"]
        self.assertEqual(e["current"], "1.1")
        self.assertEqual(e["versions"][-1]["kind"], "external_edit")
        self.assertIn("+A manual note.", e["versions"][-1]["diff"])

    def test_cycle_start_is_idempotent_and_jobs_are_stamped(self):
        cid = self.start()
        self.assertEqual(cid, "c001")
        self.assertEqual(self.evolve("cycle", "start").stdout.strip(), "c001")
        loader = importlib.machinery.SourceFileLoader("jobmod", str(self.root / "factory" / "bin" / "job"))
        job = importlib.util.module_from_spec(importlib.util.spec_from_loader("jobmod", loader))
        loader.exec_module(job)
        stamp = job.evolution_stamp()
        self.assertEqual(stamp["cycle"], "c001")
        self.assertEqual(stamp["skill_versions"]["agent:builder"], "1.0")


class Plan(Evolve):
    def test_a_valid_plan_is_rendered_and_every_change_is_logged_as_proposed(self):
        cid = self.start()
        self.plan(cid, [self.change("ch1")])
        self.evolve("plan", "check", cid)
        md = (self.evo / "cycles" / cid / "plan.md").read_text()
        self.assertIn("## builder", md)
        self.assertIn("## Orchestrator", md)
        self.assertIn("## System-level recommendations", md)
        self.assertIn("P1", md)
        self.assertEqual(self.status_of(cid, "ch1"), "proposed")
        self.evolve("plan", "check", cid)                         # a second check does not log it again
        self.assertEqual(len([e for e in self.audit() if e["event"] == "proposed"]), 1)

    def invalid(self, change, text, **kw):
        cid = self.start()
        self.plan(cid, [change], **kw)
        res = self.evolve("plan", "check", cid, ok=False)
        self.assertIn(text, res.stderr)

    def test_protected_and_unknown_targets_are_refused(self):
        self.invalid(self.change(target="agent:eval-judge"), "not a skill the retrospective may change")

    def test_the_old_text_must_match_exactly_once(self):
        self.invalid(self.change(old="this text is nowhere"), "matches 0 times")
        self.invalid(self.change(old="the"), "matches")

    def test_front_matter_cannot_change(self):
        self.invalid(self.change(old="name: builder", new="name: builder2"), "front matter")

    def test_a_change_needs_a_gap_with_evidence_and_a_measurable_impact(self):
        self.invalid(self.change(gap={"summary": "x"}), "gap needs a summary and evidence")
        self.invalid(self.change(expected_impact={"criterion": "runs_checks"}), "expected_impact needs")

    def test_too_many_changes_are_refused(self):
        cid = self.start()
        lines = [l for l in self.builder.read_text().split("\n---\n", 1)[1].splitlines() if len(l) > 25][:5]
        lines = [l for l in lines if self.builder.read_text().count(l) == 1][:4]
        self.assertGreaterEqual(len(lines), 4)
        self.plan(cid, [self.change(f"ch{i}", old=l) for i, l in enumerate(lines)])
        self.assertIn("the limit is 3", self.evolve("plan", "check", cid, ok=False).stderr)

    def test_the_orchestrator_section_targets_the_skill(self):
        cid = self.start()
        old = body_line(self.orch)
        self.plan(cid, orch_changes=[self.change("o1", old=old, new=old + "\nAnnounce each stage.", target="agent:builder")])
        self.assertIn("orchestrator changes target skill:factory", self.evolve("plan", "check", cid, ok=False).stderr)


class Approval(Evolve):
    def two_changes(self):
        cid = self.start()
        lines = [l for l in self.builder.read_text().split("\n---\n", 1)[1].splitlines()
                 if len(l) > 25 and self.builder.read_text().count(l) == 1][:2]
        self.plan(cid, [self.change("a", old=lines[0]), self.change("b", old=lines[1])])
        self.evolve("plan", "check", cid)
        return cid

    def test_nothing_is_applied_without_approval(self):
        cid = self.two_changes()
        before = self.builder.read_text()
        self.assertIn("only an approved change", self.evolve("apply", cid, "a", ok=False).stderr)
        self.assertEqual(self.builder.read_text(), before)

    def test_each_change_is_decided_on_its_own(self):
        cid = self.two_changes()
        self.evolve("decide", cid, "a", "approve")
        self.evolve("decide", cid, "b", "reject", "--reason", "too vague for the builder")
        self.assertEqual(self.status_of(cid, "a"), "approved")
        rejected = [e for e in self.audit() if e["event"] == "rejected"][0]
        self.assertEqual(rejected["reason"], "too vague for the builder")
        self.assertEqual(rejected["by"], "alice")
        self.assertIn("is rejected", self.evolve("apply", cid, "b", ok=False).stderr)
        self.evolve("apply", cid, "a")
        self.assertEqual(self.status_of(cid, "a"), "deployed")
        self.assertEqual(self.registry()["skills"]["agent:builder"]["current"], "1.1")

    def test_a_rejection_needs_a_reason_and_a_decision_is_final(self):
        cid = self.two_changes()
        self.assertIn("needs --reason", self.evolve("decide", cid, "a", "reject", ok=False).stderr)
        self.evolve("decide", cid, "a", "approve", "--by", "bob")
        self.assertIn("already approved", self.evolve("decide", cid, "a", "reject", "--reason", "x", ok=False).stderr)

    def test_applying_versions_the_skill_and_keeps_the_backup(self):
        cid = self.two_changes()
        original = self.builder.read_text()
        self.evolve("decide", cid, "a", "approve", "--by", "bob")
        self.evolve("apply", cid, "a")
        self.assertNotEqual(self.builder.read_text(), original)
        backup = self.evo / "versions" / "agent__builder" / "v1.0.md"
        self.assertEqual(backup.read_text(), original)                           # the old version is untouched
        new = self.evo / "versions" / "agent__builder" / "v1.1.md"
        self.assertEqual(new.read_text(), self.builder.read_text())
        v = self.registry()["skills"]["agent:builder"]["versions"][-1]
        self.assertEqual((v["version"], v["cycle"], v["approved_by"], v["change"]), ("1.1", cid, "bob", "a"))
        self.assertEqual(v["gap"]["summary"], "checks are not run before committing")
        self.assertEqual(v["expected_effect"]["criterion"], "runs_checks")
        self.assertIn("+Run the checks before every commit.", v["diff"])
        self.assertEqual(frontmatter(self.builder.read_text()), frontmatter(original))

    def test_a_change_goes_stale_when_the_skill_moved(self):
        cid = self.two_changes()
        self.evolve("decide", cid, "a", "approve")
        old = self.change("a")["old"]
        self.builder.write_text(self.builder.read_text().replace(old, "something else entirely"))
        self.assertIn("matches 0 times", self.evolve("apply", cid, "a", ok=False).stderr)


def frontmatter(text):
    return re.match(r"---\n.*?\n---\n", text, re.S).group(0)


class Rollback(Evolve):
    def deploy(self):
        cid = self.start()
        self.plan(cid, [self.change("a")])
        self.evolve("plan", "check", cid)
        self.evolve("decide", cid, "a", "approve")
        self.evolve("apply", cid, "a")
        return cid

    def test_any_earlier_version_can_be_restored_and_history_is_kept(self):
        cid = self.deploy()
        original = (self.evo / "versions" / "agent__builder" / "v1.0.md").read_text()
        self.evolve("rollback", "agent:builder", "1.0", "--reason", "it made the builder slower")
        self.assertEqual(self.builder.read_text(), original)
        e = self.registry()["skills"]["agent:builder"]
        self.assertEqual([v["version"] for v in e["versions"]], ["1.0", "1.1", "1.2"])
        self.assertEqual(e["versions"][-1]["kind"], "rollback")
        self.assertEqual(e["versions"][-1]["rolled_back_to"], "1.0")
        self.assertEqual(self.status_of(cid, "a"), "rolled_back")
        self.assertTrue((self.evo / "versions" / "agent__builder" / "v1.1.md").exists())
        self.evolve("rollback", "agent:builder", "v1.1")                          # and forward again
        self.assertIn("Run the checks before every commit.", self.builder.read_text())

    def test_trace_lists_every_version_and_its_gap(self):
        self.deploy()
        out = self.evolve("trace", "agent:builder").stdout
        self.assertIn("v1.0", out)
        self.assertIn("v1.1", out)
        self.assertIn("checks are not run before committing", out)


class Measure(Evolve):
    def history(self, before, after, n=3, version="1.1"):
        rows = [
            {"cycle": "c001", "ts": "2026-01-01T00:00:00Z", "overall": 60, "metrics": {"jobs": 3},
             "skill_versions": {"agent:builder": "1.0"},
             "agents": {"builder": {"confidence": 60, "label": "watch", "process": 60, "output": 60, "n": 3,
                                    "criteria": {"runs_checks": {"score": before, "n": 3, "side": "process", "label": "x", "weight": 1}}}}},
            {"cycle": "c002", "ts": "2026-01-02T00:00:00Z", "overall": 70, "metrics": {"jobs": 3},
             "skill_versions": {"agent:builder": version},
             "agents": {"builder": {"confidence": 70, "label": "ok", "process": 70, "output": 70, "n": n,
                                    "criteria": {"runs_checks": {"score": after, "n": n, "side": "process", "label": "x", "weight": 1}}}}}]
        (self.evo / "history.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))

    def deployed(self):
        cid = self.start()
        self.plan(cid, [self.change("a")])
        self.evolve("plan", "check", cid)
        self.evolve("decide", cid, "a", "approve")
        self.evolve("apply", cid, "a")

    def verdict(self, before, after, **kw):
        self.deployed()
        self.history(before, after, **kw)
        self.evolve("measure", "c002")
        return [e for e in self.audit() if e["event"] == "measured"][-1]

    def test_delivered_when_the_metric_moved_enough(self):
        e = self.verdict(40, 65)
        self.assertEqual((e["verdict"], e["before"], e["after"], e["delta"]), ("delivered", 40, 65, 25))

    def test_not_delivered_when_it_barely_moved(self):
        self.assertEqual(self.verdict(40, 44)["verdict"], "not_delivered")

    def test_regressed_when_it_got_worse(self):
        self.assertEqual(self.verdict(60, 50)["verdict"], "regressed")

    def test_inconclusive_with_too_few_samples(self):
        self.assertEqual(self.verdict(40, 90, n=1)["verdict"], "inconclusive")

    def test_a_cycle_that_ran_before_the_change_does_not_count(self):
        self.deployed()
        self.history(40, 90, version="1.0")
        self.evolve("measure", "c002")
        self.assertEqual([e for e in self.audit() if e["event"] == "measured"], [])


class Close(Evolve):
    def make_job(self, jid, cid):
        d = self.root / "factory" / "jobs" / jid
        (d / "round-1").mkdir(parents=True)
        (d / "job.json").write_text(json.dumps({
            "id": jid, "target": "t", "issue": 1, "stage": "needs-human", "round": 1, "cycle": cid,
            "started": "2026-01-01T00:00:00Z", "cost_usd": 1.5, "skill_versions": {"agent:builder": "1.0"},
            "intake": {"decision": "ACCEPT", "risk": "low", "rescoped": False, "surfaces": []},
            "worktree": str(self.root / "workspaces" / "t" / jid)}))
        (d / "decision.md").write_text("ESCALATE\n\nThe change touches the auth module.\n")
        (d / "feedback-1.md").write_text("# Feedback 1\n\nPlease keep the old API.\n")
        (d / "build.md").write_text("STATUS: READY\n\n## Summary\n- a\n- b\n- c\n\n## Acceptance criteria\n1. [x] one: ok\n")
        return d

    def transcript(self, job_dir):
        slug = re.sub(r"[^A-Za-z0-9]", "-", str(self.root))
        sub = self.tmp / "claude" / "projects" / slug / "s1" / "subagents"
        sub.mkdir(parents=True, exist_ok=True)
        rows = [{"type": "user", "message": {"role": "user", "content": f"Job: x. Job folder: {job_dir}/. rest"}, "timestamp": "2026-01-01T00:00:00Z"},
                {"type": "assistant", "timestamp": "2026-01-01T00:00:09Z",
                 "message": {"id": "mz", "model": "claude-haiku-5-5", "usage": {"input_tokens": 10, "output_tokens": 10},
                             "content": [{"type": "tool_use", "id": "tz", "name": "SubagentHandback", "input": {"message": "STATUS: READY"}}]}}]
        (sub / "agent-1.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        (sub / "agent-1.meta.json").write_text(json.dumps({"agentType": "builder"}))

    def test_closing_a_cycle_snapshots_scores_and_collects_the_feedback(self):
        cid = self.start()
        d = self.make_job("001-a", cid)
        self.make_job("002-other", "c099")                                          # another cycle's job
        self.transcript(d)
        self.evolve("cycle", "close", cid)
        inp = json.loads((self.evo / "cycles" / cid / "input.json").read_text())
        self.assertEqual(inp["cycle"], cid)
        self.assertEqual(inp["metrics"]["jobs"], 1)
        self.assertEqual(inp["metrics"]["escalation_rate"], 1.0)
        self.assertIn("builder", inp["scores"])
        self.assertIn("runs_checks", inp["scores"]["builder"]["criteria"])
        self.assertEqual({f["file"] for f in inp["feedback"]}, {"jobs/001-a/feedback-1.md", "jobs/001-a/decision.md"})
        self.assertEqual(inp["limits"]["max_changes"], 3)
        hist = [json.loads(l) for l in (self.evo / "history.jsonl").read_text().splitlines()]
        self.assertEqual(hist[0]["cycle"], cid)
        self.assertEqual(hist[0]["skill_versions"]["agent:builder"], "1.0")
        self.assertEqual(json.loads((self.evo / "cycles" / cid / "cycle.json").read_text())["status"], "closed")
        self.assertEqual(self.evolve("cycle", "start").stdout.strip(), "c002")      # a closed cycle is not reopened

    def test_the_board_shows_versions_scores_and_the_audit_trail(self):
        cid = self.start()
        d = self.make_job("001-a", cid)
        self.transcript(d)
        self.evolve("cycle", "close", cid)
        self.plan(cid, [self.change("a")])
        self.evolve("plan", "check", cid)
        self.evolve("decide", cid, "a", "approve")
        self.evolve("apply", cid, "a")
        board = json.loads((self.evo / "board.json").read_text())
        self.assertEqual(board["cycles"][0]["cycle"], cid)
        self.assertIn("builder", board["cycles"][0]["agents"])
        self.assertEqual([v["version"] for v in board["skills"]["agent:builder"]["versions"]], ["1.0", "1.1"])
        row = board["audit"][0]
        self.assertEqual((row["change"], row["status"], row["version"]), ("a", "deployed", "1.1"))
        self.assertEqual([s["event"] for s in row["stages"]], ["proposed", "approved", "deployed"])


class EvalHook(Evolve):
    def test_scores_can_be_limited_to_one_cycle(self):
        d = self.root / "factory" / "jobs" / "001-a"
        d.mkdir(parents=True)
        (d / "job.json").write_text(json.dumps({"id": "001-a", "target": "t", "stage": "merged", "cycle": "c001", "started": "2026-01-01T00:00:00Z"}))
        res = subprocess.run([str(self.root / "factory" / "bin" / "eval"), "report", "--cycle", "c002", "--json"],
                             cwd=self.root, capture_output=True, text=True, env=self.env)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertFalse((self.root / "factory" / "evals" / "scores.json").exists())   # a cycle report writes nothing
        self.assertEqual(json.loads(res.stdout)["agents"]["builder"]["samples"]["live"], 0)


if __name__ == "__main__":
    unittest.main()
