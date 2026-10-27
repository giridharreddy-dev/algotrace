"""A loopback-only standard-library server with small, explicit endpoints."""

import json
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from .algorithms import CATALOG, compare_sorts, run_algorithm

WEB = Path(__file__).with_name("web")
STATIC = {"/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8")}
MAX_BODY = 8192


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def _reply(self, status, data, content_type="application/json; charset=utf-8"):
        body = json.dumps(data, ensure_ascii=False).encode() if isinstance(data, (dict, list)) else data
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def _allowed(self):
        allowed = f"127.0.0.1:{self.server.server_port}"
        if self.headers.get("Host") != allowed:
            self._reply(403, {"error": "Open the app through its printed 127.0.0.1 address."})
            return False
        origin = self.headers.get("Origin")
        if origin and origin != f"http://{allowed}":
            self._reply(403, {"error": "Cross-origin requests are not accepted."})
            return False
        return True

    def do_GET(self):
        if not self._allowed():
            return
        path = urlsplit(self.path).path
        if path == "/api/catalog":
            self._reply(200, {key: asdict(value) for key, value in CATALOG.items()})
        elif path in STATIC:
            filename, mime = STATIC[path]
            self._reply(200, (WEB / filename).read_bytes(), mime)
        else:
            self._reply(404, {"error": "Not found."})

    def do_POST(self):
        if not self._allowed():
            return
        if urlsplit(self.path).path not in ("/api/run", "/api/compare"):
            self._reply(404, {"error": "Not found."})
            return
        if self.headers.get_content_type() != "application/json":
            self._reply(415, {"error": "Send application/json."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_BODY:
                self.close_connection = True
                self._reply(413, {"error": "Request must contain 1–8192 bytes."})
                return
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("Request must be an object.")
            if urlsplit(self.path).path == "/api/run":
                result = run_algorithm(payload.get("algorithm"), payload.get("values"), payload.get("target"))
            else:
                result = {"results": compare_sorts(payload.get("values"))}
            self._reply(200, result)
        except (ValueError, UnicodeDecodeError, RecursionError) as error:
            self._reply(400, {"error": str(error) if not isinstance(error, RecursionError) else "JSON is nested too deeply."})


def make_server(port=8765):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    return server
