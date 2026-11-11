"""factory/bin/metrics: the health numbers behind the dashboard's Factory health board."""
import json
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]
NOW = datetime.now(timezone.utc).replace(microsecond=0)


def iso(hours_ago):
    return (NOW - timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


def job(jid, stage, hist, target="a", rounds=1, cost=1.0, accept=True, started=None, ended=None, **extra):
    """hist: [(stage, hours_ago)] oldest first."""
    j = {"id": jid, "target": target, "stage": stage, "round": rounds, "cost_usd": cost, "title": jid,
         "issue_url": f"https://x/{jid}", "pr_url": f"https://x/pr/{jid}",
         "intake": {"decision": "ACCEPT" if accept else "REJECT"}, "cost_by_agent": {"builder": cost / 2, "approver": cost / 2},
         "history": [{"stage": s, "ts": iso(h)} for s, h in hist],
         "started": started or iso(hist[0][1]), "ended": ended}
    j.update(extra)
    return j


class Metrics(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.root = self.tmp / "root"
        (self.root / "factory" / "bin").mkdir(parents=True)
        shutil.copy(SRC / "factory" / "bin" / "metrics", self.root / "factory" / "bin" / "metrics")
        shutil.copy(SRC / "factory" / "config.json", self.root / "factory" / "config.json")
        (self.root / "evals").mkdir()
        self.jobs = self.root / "factory" / "jobs"

    def put(self, j):
        d = self.jobs / j["id"]
        d.mkdir(parents=True)
        (d / "job.json").write_text(json.dumps(j))

    def run_metrics(self, *args):
        res = subprocess.run([str(self.root / "factory" / "bin" / "metrics"), *args], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, res.stderr)
        return res

    def data(self):
        self.run_metrics("write")
        return json.loads((self.root / "factory" / "metrics.json").read_text())

    def seed(self):
        # J1: clean, merged by the approver in 3 hours
        self.put(job("001-clean", "merged", [("intake", 10), ("spec", 9.9), ("build", 9.5), ("gate", 8), ("review", 7.8), ("approve", 7.5),
                                              ("merging", 7.2), ("merged", 7)], rounds=1, ended=iso(7), cost=1.0))
        # J2: escalated, waited 5h for a person, two build rounds, merged
        self.put(job("002-human", "merged", [("intake", 30), ("spec", 29.9), ("build", 29.5), ("gate", 28), ("review", 27.5), ("approve", 27),
                                              ("needs-human", 26), ("build", 21), ("gate", 20), ("review", 19.8), ("approve", 19.5),
                                              ("merging", 19.2), ("merged", 19)], rounds=2, ended=iso(19), cost=3.0, target="b"))
        # J3: rejected at intake
        self.put(job("003-no", "rejected", [("intake", 12), ("rejected", 11.9)], ended=iso(11.9), cost=0.1, accept=False))
        # J4: waiting on a person for 30 hours
        self.put(job("004-stuck", "needs-human", [("intake", 40), ("spec", 39.9), ("build", 39), ("gate", 35), ("review", 34), ("needs-human", 30)],
                     ended=iso(30), cost=2.0))
        # J5: running, built a minute ago
        self.put(job("005-running", "build", [("intake", 2), ("spec", 1.9), ("build", 1.5)], cost=0.5))

    def test_productivity_numbers(self):
        self.seed()
        p = self.data()["productivity"]
        self.assertEqual(p["throughput_7d"], 2)
        self.assertEqual(p["wip"], 1)
        self.assertEqual(p["waiting_on_human"], 1)
        self.assertAlmostEqual(p["lead_time_p50_h"], 3.0, places=1)         # nearest rank of [3, 11]
        self.assertAlmostEqual(p["human_wait_p50_h"], 0.0, places=1)
        self.assertAlmostEqual(p["human_wait_p90_h"] if "human_wait_p90_h" in p else 0, 0.0, places=1)
        self.assertAlmostEqual(p["cycle_efficiency"], 9 / 14, places=2)       # 5 of 14 hours are a person's
        self.assertAlmostEqual(p["stage_avg_h"]["needs-human"], 2.5, places=1)     # (0 + 5) over the two merged jobs

    def test_flow_quality_numbers(self):
        self.seed()
        f = self.data()["flow"]
        self.assertEqual(f["first_pass_yield"], 0.5)        # J1 only
        self.assertEqual(f["avg_rounds"], 1.5)
        self.assertEqual(f["autonomy"], 0.5)                # J1 merged with no human, J2 went through needs-human
        self.assertEqual(f["rework_rate"], 0.5)
        self.assertEqual(f["escalation_rate"], 0.5)         # J2 and J4 of the four accepted jobs
        self.assertAlmostEqual(f["intake_reject_rate"], 0.2)

    def test_cost_and_waste(self):
        self.seed()
        c = self.data()["cost"]
        self.assertEqual(c["total_usd"], 6.6)
        self.assertEqual(c["per_merged_job_usd"], 2.0)
        self.assertEqual(c["waste_usd"], 0.1)               # the rejected job
        self.assertEqual(c["by_agent_usd"]["builder"], 3.3)

    def test_stuck_jobs_and_vitality(self):
        self.seed()
        v = self.data()["vitality"]
        self.assertEqual([s["job"] for s in v["stuck"]], ["004-stuck"])
        self.assertGreater(v["stuck"][0]["hours"], 29)
        self.assertEqual(v["stuck"][0]["url"], "https://x/pr/004-stuck")
        self.assertEqual(v["jobs_started_7d"], 5)
        self.assertLess(v["idle_days"], 1)

    def test_kpis_have_targets_and_statuses(self):
        self.seed()
        k = self.data()["kpis"]
        self.assertEqual(k["throughput_7d"]["status"], "bad")            # 2 against a target of 3 (below 75% of it)
        self.assertEqual(k["first_pass_yield"]["status"], "watch")       # 0.5 against 0.6
        self.assertEqual(k["stuck_jobs"]["status"], "watch")             # a target of zero: one stuck job is a watch, more is bad
        self.assertEqual(k["lead_time_p50_h"]["status"], "good")
        self.assertIsNone(k["agent_confidence"]["value"])                # no scores yet
        self.assertEqual(k["agent_confidence"]["status"], "none")

    def test_cost_per_merged_job_leaves_out_jobs_from_before_cost_tracking(self):
        self.put(job("001-old", "merged", [("intake", 50), ("merged", 49)], cost=0.0, ended=iso(49)))
        self.put(job("002-new", "merged", [("intake", 20), ("merged", 19)], cost=3.0, ended=iso(19), skill_versions={"agent:builder": "1.0"}))
        self.assertEqual(self.data()["cost"]["per_merged_job_usd"], 3.0)

    def test_security_lens_rate_browser_tool_and_empty_cycles(self):
        self.put(job("001-ui", "merged", [("intake", 20), ("review", 19), ("merged", 18)], ended=iso(18),
                     agents={"reviewers": {"code": "haiku", "ux": "sonnet"}}))
        self.put(job("002-sec", "merged", [("intake", 20), ("review", 19), ("merged", 18)], ended=iso(18),
                     agents={"reviewers": {"code": "haiku", "security": "opus"}}))
        self.put(job("003-early", "build", [("intake", 2), ("build", 1)]))        # never reviewed: not in the rate
        evo = self.root / "factory" / "evolution"
        evo.mkdir()
        (evo / "board.json").write_text(json.dumps({"cycles": [
            {"cycle": "c001", "ts": iso(48), "overall": 70, "jobs": 2}, {"cycle": "c002", "ts": iso(24), "overall": None, "jobs": 0}], "audit": []}))
        (self.root / "factory" / "bin" / "browse").write_text("#!/bin/sh\n")
        k = self.data()["kpis"]
        self.assertEqual(k["security_lens_fire_rate"]["value"], 0.5)
        self.assertEqual(k["security_lens_fire_rate"]["status"], "good")
        self.assertEqual(k["cycles_with_zero_jobs"]["value"], 1)
        self.assertEqual(k["cycles_with_zero_jobs"]["status"], "watch")
        self.assertEqual(k["browser_tool_available"]["value"], 1)

    def test_targets_come_from_the_config(self):
        self.seed()
        cfg = json.loads((self.root / "factory" / "config.json").read_text())
        cfg["metrics"] = {"targets": {"throughput_7d": [1, True]}, "stuck_hours": {"needs-human": 100}}
        (self.root / "factory" / "config.json").write_text(json.dumps(cfg))
        d = self.data()
        self.assertEqual(d["kpis"]["throughput_7d"]["status"], "good")
        self.assertEqual(d["vitality"]["stuck"], [])

    def test_weekly_series_and_targets_breakdown(self):
        self.seed()
        d = self.data()
        self.assertEqual(len(d["series"]["weeks"]), 8)
        self.assertEqual(sum(d["series"]["throughput"]), 2)
        self.assertEqual(set(d["by_target"]), {"a", "b"})
        self.assertEqual(d["by_target"]["b"]["merged"], 1)
        self.assertEqual(d["by_target"]["b"]["first_pass_yield"], 0.0)

    def test_agents_learning_and_evals_are_read_from_their_files(self):
        self.seed()
        ev = self.root / "factory" / "evals"
        (ev / "runs" / "r1" / "builder__x").mkdir(parents=True)
        (ev / "runs" / "r1" / "builder__x" / "result.json").write_text(json.dumps({"agent": "builder", "case": "x", "passed": True, "ts": iso(24)}))
        (ev / "runs" / "r1" / "intake__y").mkdir(parents=True)
        (ev / "runs" / "r1" / "intake__y" / "result.json").write_text(json.dumps({"agent": "intake", "case": "y", "passed": False, "ts": iso(24)}))
        (ev / "scores.json").write_text(json.dumps({"agents": {
            "builder": {"confidence": 90, "label": "trusted", "provisional": False, "process": {"score": 90}, "output": {"score": 90}},
            "intake": {"confidence": 60, "label": "watch", "provisional": True, "process": {"score": 60}, "output": {"score": 60}}}}))
        evo = self.root / "factory" / "evolution"
        evo.mkdir()
        (evo / "board.json").write_text(json.dumps({"cycles": [{"cycle": "c001", "ts": iso(48), "overall": 70}, {"cycle": "c002", "ts": iso(24), "overall": 75}],
            "audit": [{"status": "measured", "version": "1.1", "verdict": "delivered"}, {"status": "rejected"},
                      {"status": "measured", "version": "1.1", "verdict": "regressed"}, {"status": "proposed"}]}))
        d = self.data()
        self.assertEqual(d["agents"]["avg_confidence"], 75.0)
        self.assertEqual(d["agents"]["weakest"], {"agent": "intake", "confidence": 60})
        self.assertEqual(d["agents"]["labels"], {"trusted": 1, "ok": 0, "watch": 1})
        self.assertEqual(d["agents"]["eval_pass_rate"], 0.5)
        self.assertAlmostEqual(d["agents"]["last_eval_age_days"], 1.0, places=1)
        l = d["vitality"]["learning"]
        self.assertEqual((l["cycles"], l["proposed"], l["rejected"], l["deployed"], l["delivered"], l["regressed"]), (2, 4, 1, 2, 1, 1))
        self.assertEqual(l["change_delivery_rate"], 0.5)
        self.assertEqual(l["overall_trend"], [70, 75])

    def test_jobs_without_a_stage_history_still_count(self):
        j = job("001-old", "merged", [("intake", 5)], ended=iso(2), cost=1.0)
        del j["history"]
        self.put(j)
        d = self.data()
        self.assertEqual(d["productivity"]["throughput_7d"], 1)
        self.assertAlmostEqual(d["productivity"]["lead_time_p50_h"], 3.0, places=1)
        self.assertIsNone(d["productivity"]["human_wait_p50_h"])           # unknown, never guessed
        self.assertIsNone(d["flow"]["autonomy"])

    def test_an_empty_factory_does_not_break(self):
        d = self.data()
        self.assertEqual(d["productivity"]["throughput_7d"], 0)
        self.assertIsNone(d["productivity"]["lead_time_p50_h"])
        self.assertIn("kpis", d)
        self.assertIn("Factory health", self.run_metrics("show").stdout)


class JobHistory(unittest.TestCase):
    def test_job_records_the_stage_history_and_refreshes_the_metrics(self):
        import os
        tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, tmp, True)
        src = (SRC / "factory" / "bin" / "job").read_text()
        self.assertIn('job.setdefault("history", []).append({"stage": stage', src)
        self.assertIn('job["history"] = [{"stage": "intake"', src)
        self.assertIn("refresh_metrics", src)


if __name__ == "__main__":
    unittest.main()
