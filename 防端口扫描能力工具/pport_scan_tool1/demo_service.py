#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import sys

PORT = int(sys.argv[1])
LABEL = sys.argv[2]

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = (
            f"{LABEL}\n"
            f"server={socket.gethostname()}\n"
            f"port={PORT}\n"
            f"path={self.path}\n"
            f"client_ip={self.client_address[0]}\n"
        ).encode()

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[{self.client_address[0]}:{PORT}] {fmt % args}")

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()