#!/usr/bin/env python3
"""Tiny static server + comments sidecar API for the commentable-html layer.

Run inside a deliverable folder:  python3 serve.py [port]   (default 8777)

  GET  /__comments__/<docId>   -> returns <docId>.comments.json  (or {"threads":[]})
  PUT  /__comments__/<docId>   -> writes the JSON body to <docId>.comments.json
  *                            -> serves static files from the current directory

Bind is localhost-only. The comment layer auto-detects this endpoint when the
page is opened over http; otherwise it falls back to localStorage. The AI reads
and writes <docId>.comments.json directly on disk between rounds.
"""
import http.server, socketserver, json, os, sys, tempfile, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8777
ROOT = os.getcwd()
PREFIX = "/__comments__/"


class Handler(http.server.SimpleHTTPRequestHandler):
    def _comments_path(self):
        doc = urllib.parse.unquote(self.path[len(PREFIX):]).strip("/").split("?")[0]
        doc = os.path.basename(doc) or "document"
        return os.path.join(ROOT, doc + ".comments.json")

    def _send_json(self, code, body=b""):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith(PREFIX):
            path = self._comments_path()
            if os.path.exists(path):
                with open(path, "rb") as f:
                    self._send_json(200, f.read())
            else:
                self._send_json(200, b'{"threads":[]}')
            return
        return super().do_GET()

    def do_PUT(self):
        if self.path.startswith(PREFIX):
            n = int(self.headers.get("Content-Length", 0))
            data = self.rfile.read(n)
            try:
                json.loads(data)
            except Exception:
                self._send_json(400, b'{"error":"invalid json"}')
                return
            path = self._comments_path()
            # atomic write: temp file + replace, so a concurrent GET never sees a partial file
            fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".", suffix=".tmp")
            with os.fdopen(fd, "wb") as f:
                f.write(data)
            os.replace(tmp, path)
            self._send_json(200, b'{"ok":true}')
            return
        self._send_json(405, b'{"error":"method not allowed"}')

    do_POST = do_PUT

    def end_headers(self):
        # No caching, so edited HTML and fresh comments always show on refresh.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


socketserver.ThreadingTCPServer.allow_reuse_address = True
with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"\n  commentable-html  →  http://127.0.0.1:{PORT}/")
    print(f"  serving {ROOT}")
    print("  Ctrl-C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  stopped.")
