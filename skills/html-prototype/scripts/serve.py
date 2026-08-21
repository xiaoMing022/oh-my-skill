from __future__ import annotations

import argparse
import json
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class PrototypeHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, _format: str, *_args: object) -> None:
        pass


def serve(root: Path, port: int, info_path: Path | None) -> None:
    root = root.resolve()
    if not root.is_dir():
        raise SystemExit(f"root is not a directory: {root}")

    handler = partial(PrototypeHandler, directory=str(root))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    url = f"http://127.0.0.1:{server.server_port}/"
    payload = {
        "url": url,
        "port": server.server_port,
        "pid": os.getpid(),
        "root": str(root),
    }
    print(url, flush=True)
    if info_path is not None:
        info_path.parent.mkdir(parents=True, exist_ok=True)
        info_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Serve an HTML prototype directory on a local port.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="directory that contains index.html",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="port; default is any free port",
    )
    parser.add_argument(
        "--info",
        type=Path,
        help="write url/port/pid JSON to this path",
    )
    args = parser.parse_args()
    serve(args.root, args.port, args.info)


if __name__ == "__main__":
    main()
