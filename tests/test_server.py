import json
import subprocess
import sys
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from algotrace.server import make_server
from algotrace.algorithms import CATALOG


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(0)
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def fetch(self, path, payload=None, headers=None, raw=None):
        data = json.dumps(payload).encode() if payload is not None else raw
        sent = {"Content-Type": "application/json"} if data is not None else {}
        sent.update(headers or {})
        request = Request(self.base + path, data=data, headers=sent)
        try:
            response = urlopen(request, timeout=5)
        except HTTPError as error:
            response = error
        with response:
            return response.status, response.read(), response.headers

    def test_static_files_and_catalog(self):
        for path, content_type in (("/", "text/html"), ("/app.js", "text/javascript"), ("/style.css", "text/css")):
            status, body, headers = self.fetch(path)
            self.assertEqual(status, 200)
            self.assertIn(content_type, headers["Content-Type"])
            self.assertGreater(len(body), 100)
            self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        status, body, _ = self.fetch("/api/catalog")
        self.assertEqual(status, 200)
        self.assertEqual(len(json.loads(body)), 32)

    def test_run_and_compare_end_to_end(self):
        status, body, _ = self.fetch("/api/run", {"algorithm": "merge", "values": [7, 1, -2]})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["result"], [-2, 1, 7])
        status, body, _ = self.fetch("/api/compare", {"values": [7, 1, -2]})
        self.assertEqual(status, 200)
        self.assertEqual(len(json.loads(body)["results"]), 14)

    def test_every_algorithm_through_http(self):
        for name, spec in CATALOG.items():
            target = 2 if spec.category == "search" else spec.parameter_default if spec.parameter else None
            with self.subTest(algorithm=name):
                status, body, _ = self.fetch("/api/run", {"algorithm": name, "values": [1, 2, 2, 3, 5], "target": target})
                self.assertEqual(status, 200, body)
                payload = json.loads(body)
                self.assertEqual(payload["events"][-1]["kind"], "complete")
                self.assertEqual(payload["algorithm"], name)

    def test_parameter_validation_and_skipped_sort_through_http(self):
        status, body, _ = self.fetch("/api/run", {"algorithm": "sliding_window", "values": [1, 2], "target": 3})
        self.assertEqual(status, 400)
        self.assertIn("Window size", json.loads(body)["error"])
        status, body, _ = self.fetch("/api/compare", {"values": [-1000000, 1000000]})
        self.assertEqual(status, 200)
        self.assertEqual([row["algorithm"] for row in json.loads(body)["results"] if "skipped" in row], ["counting"])

    def test_bad_requests(self):
        cases = [({"algorithm": "binary", "values": [3, 1], "target": 1}, "ascending"),
                 ({"algorithm": "bubble", "values": [True]}, "integer"),
                 ({"algorithm": "linear", "values": []}, "target")]
        for payload, message in cases:
            status, body, _ = self.fetch("/api/run", payload)
            self.assertEqual(status, 400)
            self.assertIn(message.lower(), json.loads(body)["error"].lower())
        for raw in (b"{bad json", b"[]", b"\xff", b'{"values":' + b'[' * 1500):
            status, _, _ = self.fetch("/api/run", raw=raw)
            self.assertEqual(status, 400)

    def test_limits_origin_and_host(self):
        status, _, _ = self.fetch("/api/run", raw=b" " * 8193)
        self.assertEqual(status, 413)
        status, _, _ = self.fetch("/api/run", {}, {"Content-Type": "text/plain"})
        self.assertEqual(status, 415)
        status, _, _ = self.fetch("/api/run", {}, {"Origin": "https://example.com"})
        self.assertEqual(status, 403)
        status, _, _ = self.fetch("/", headers={"Host": "untrusted.example"})
        self.assertEqual(status, 403)

    def test_static_allowlist(self):
        for path in ("/README.md", "/../README.md", "/algotrace/server.py", "/missing"):
            self.assertEqual(self.fetch(path)[0], 404)
        self.assertEqual(self.fetch("/api/missing", {})[0], 404)


class CommandLineTests(unittest.TestCase):
    def invoke(self, *args):
        return subprocess.run([sys.executable, "-m", "algotrace", *args],
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=10)

    def test_search_cli(self):
        result = self.invoke("run", "binary", "--values", "1,3,5", "--target", "3")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["result"], 1)

    def test_compare_and_empty_cli(self):
        result = self.invoke("run", "bubble", "--values", "", "--compare")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(json.loads(result.stdout)), 14)

    def test_invalid_cli(self):
        result = self.invoke("run", "binary", "--values", "4,2", "--target", "2")
        self.assertEqual(result.returncode, 2)
        self.assertIn("ascending", result.stderr)

    def test_listing_cli_and_array_parameter(self):
        result = self.invoke("list", "--category", "search")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(result.stdout.strip().splitlines()), 8)
        self.assertIn("fibonacci_search", result.stdout)
        result = self.invoke("run", "sliding_window", "--values", "1,2,3,4", "--target", "2")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["result"], {"sum": 7, "start": 2, "end": 3})


if __name__ == "__main__":
    unittest.main()
