"""Tests for `target check`'s agent-browser warning and the shared `browse` helper.

Run: python3 -m unittest tests/test_target.py
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


class TargetCheckBrowserWarning(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.root = self.tmp / "root"
        (self.root / "factory" / "bin").mkdir(parents=True)
        shutil.copy(SRC / "factory" / "bin" / "target", self.root / "factory" / "bin" / "target")
        config = json.loads((SRC / "factory" / "config.json").read_text())
        config["targets"] = {"alpha": {"repo": "me/alpha", "base_branch": "main", "merge_method": "squash",
                                       "protected_paths": []}}
        (self.root / "factory" / "config.json").write_text(json.dumps(config))
        (self.root / "targets" / "alpha").mkdir(parents=True)  # no clone: check stops early, after the browser line
        state = self.tmp / "gh.json"
        state.write_text(json.dumps({"user": "tester"}))
        self.env = {"FACTORY_GH": str(SRC / "tests" / "fake_gh.py"), "FAKE_GH_STATE": str(state)}
        # a PATH holding only the tools the script needs (python, git), plus a dir we control
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        for tool in ("git", "bash", "env"):
            found = shutil.which(tool)
            if found:
                (self.bin / tool).symlink_to(found)

    def check(self):
        env = {**os.environ, **GIT_ENV, **self.env, "PATH": str(self.bin)}
        return subprocess.run([sys.executable, str(self.root / "factory" / "bin" / "target"), "check", "alpha"],
                              cwd=self.root, capture_output=True, text=True, env=env)

    def test_missing_agent_browser_warns_with_the_fallback_and_is_not_a_failure(self):
        res = self.check()
        self.assertIn("WARN  agent-browser not found", res.stdout)
        self.assertIn("factory/bin/browse", res.stdout)
        self.assertNotIn("FAIL  agent-browser", res.stdout)
        self.assertNotIn("agent-browser", res.stderr)  # the later failure (no clone) is not about the browser

    def test_present_agent_browser_is_ok_without_warning(self):
        fake = self.bin / "agent-browser"
        fake.write_text("#!/bin/sh\nexit 0\n")
        fake.chmod(0o755)
        res = self.check()
        self.assertIn("ok    agent-browser is installed", res.stdout)
        self.assertNotIn("WARN", res.stdout)


def quiet_server(directory):
    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    srv = HTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(directory)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


class BrowseHelper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(SRC / "factory" / "bin"))
        cls.browse = SRC / "factory" / "bin" / "browse"
        import importlib.machinery, importlib.util
        loader = importlib.machinery.SourceFileLoader("browse", str(cls.browse))
        spec = importlib.util.spec_from_loader("browse", loader)
        cls.mod = importlib.util.module_from_spec(spec)
        loader.exec_module(cls.mod)
        cls.chrome = cls.mod.find_chrome()

    def run_browse(self, *args, env=None):
        return subprocess.run([sys.executable, str(self.browse), *args], capture_output=True, text=True,
                              env={**os.environ, **(env or {})}, timeout=90)

    def test_usage_is_in_the_header(self):
        res = self.run_browse("--help")
        self.assertEqual(res.returncode, 0)
        self.assertIn("--viewport", res.stdout)
        self.assertIn("read-only", res.stdout)

    def test_refuses_non_web_urls_and_bad_options(self):
        self.assertNotEqual(self.run_browse("javascript:alert(1)").returncode, 0)
        self.assertNotEqual(self.run_browse("http://x/", "--mode", "nope").returncode, 0)
        self.assertNotEqual(self.run_browse("http://x/", "--viewport", "big").returncode, 0)

    def test_no_chrome_exits_2(self):
        res = self.run_browse("http://127.0.0.1:1/", env={"BROWSE_CHROME": "/nonexistent/chrome", "PATH": "/usr/bin:/bin"})
        if self.chrome and "/Applications" in self.chrome:
            self.skipTest("Chrome found in /Applications regardless of PATH")
        self.assertEqual(res.returncode, 2)

    def test_against_a_local_http_server(self):
        if not self.chrome:
            self.skipTest("no Chrome on this machine")
        site = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, site, True)
        (site / "index.html").write_text(
            '<!doctype html><html lang="en"><title>Smoke</title><h1>Hello page</h1><nav><a href="/x">X</a></nav>'
            '<label for=q>Search</label><input id=q required><button>Go</button><img src="a.png">'
            "<script>console.error('boom')</script></html>")
        srv = quiet_server(site)
        self.addCleanup(srv.shutdown)
        url = f"http://127.0.0.1:{srv.server_address[1]}/"
        res = self.run_browse(url, "--mode", "text")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("Hello page", res.stdout)
        res = self.run_browse(url, "--mode", "summary", "--viewport", "375x812")
        self.assertEqual(res.returncode, 0, res.stderr)
        for expected in ("title: Smoke", "viewport: 375x812", "h1 Hello page", 'input[text] "Search" required',
                         "(NO ALT) a.png", "console.error: boom", "HTTP 404"):
            self.assertIn(expected, res.stdout)
        shot = site / "s.png"
        res = self.run_browse(url, "--mode", "shot", "--viewport", "400x300", "--out", str(shot))
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(shot.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        res = self.run_browse(url, "--eval", "document.title")
        self.assertEqual(res.stdout.strip(), '"Smoke"')


if __name__ == "__main__":
    unittest.main()
