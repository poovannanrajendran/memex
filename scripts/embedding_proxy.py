"""Authenticated, embedding-only bridge to loopback Ollama; no generation route."""
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import urllib.request


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        expected = "Bearer " + os.environ["MEMEX_EMBED_TOKEN"]
        if not hmac.compare_digest(self.headers.get("Authorization", ""), expected):
            self.send_error(401)
            return
        if self.path != "/api/embed":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 65536:
                self.send_error(413)
                return
            body = json.loads(self.rfile.read(length))
            if body.get("model") != "nomic-embed-text:latest" or not isinstance(body.get("input"), str):
                self.send_error(400)
                return
            request = urllib.request.Request("http://127.0.0.1:11434/api/embed",
                data=json.dumps({"model": body["model"], "input": body["input"], "truncate": True}).encode(),
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(request, timeout=90) as response:
                data = response.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception:
            self.send_error(502, "Local embedding service unavailable")

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    if not os.environ.get("MEMEX_EMBED_TOKEN"):
        raise RuntimeError("MEMEX_EMBED_TOKEN required")
    ThreadingHTTPServer((os.environ.get("MEMEX_EMBED_BIND", "192.168.1.24"), 11435), Handler).serve_forever()
