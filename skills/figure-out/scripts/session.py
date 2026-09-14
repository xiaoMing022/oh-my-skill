"""Create isolated figure-out sessions and track checkpoint statuses."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

CHECKPOINT_ID_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,31}")
STATUSES = ("pending", "waiting", "confirmed", "needs-review", "deferred", "skipped")
SESSION_STATUSES = (
    "exploring", "waiting", "planning", "executing", "complete", "paused", "handed-off",
)


def atomic_write(path: Path, text: str) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _write_manifest(directory: Path, manifest: dict) -> None:
    atomic_write(
        directory / "checkpoints.json",
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    )


def _session_directory(directory: Path) -> Path:
    directory = directory.expanduser().resolve()
    if (not (directory / "session.md").is_file()
            or not (directory / "checkpoints.json").is_file()):
        raise ValueError("not an initialized session directory")
    return directory


def _load_manifest(directory: Path) -> dict:
    try:
        manifest = json.loads((directory / "checkpoints.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"corrupt checkpoints.json: {error}") from error
    if not isinstance(manifest, dict) or not isinstance(manifest.get("checkpoints"), list):
        raise ValueError("checkpoints.json must contain a checkpoints list")
    return manifest


def _validated(checkpoint: str, status: str | None) -> None:
    if CHECKPOINT_ID_RE.fullmatch(checkpoint) is None:
        raise ValueError(
            "checkpoint ID must start with a letter and use only letters, digits,"
            " hyphens, or underscores (max 32 characters)",
        )
    if status is not None and status not in STATUSES:
        raise ValueError(f"status must be one of: {', '.join(STATUSES)}")


def initialize(title: str, root: Path) -> Path:
    if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", title) is None or len(title) > 64:
        raise ValueError("title must be lowercase ASCII words separated by hyphens (max 64 characters)")
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix=f"{title}-", dir=root))
    atomic_write(directory / "session.md", f"# {title}\n\nStatus: exploring\n")
    _write_manifest(directory, {"title": title, "status": "exploring", "checkpoints": []})
    return directory


def add_checkpoint(
    directory: Path,
    checkpoint: str,
    title: str | None = None,
    status: str = "pending",
) -> dict:
    directory = _session_directory(directory)
    _validated(checkpoint, status)
    manifest = _load_manifest(directory)
    entry = next((item for item in manifest["checkpoints"] if item["id"] == checkpoint), None)
    if entry is None:
        entry = {"id": checkpoint}
        manifest["checkpoints"].append(entry)
    if title:
        entry["title"] = title
    entry.setdefault("title", checkpoint)
    entry["status"] = status
    entry["updated"] = time.time()
    _write_manifest(directory, manifest)
    return {"session": str(directory), "checkpoint": checkpoint, "status": status}


def mark(directory: Path, checkpoint: str, status: str) -> dict:
    directory = _session_directory(directory)
    _validated(checkpoint, status)
    manifest = _load_manifest(directory)
    entry = next((item for item in manifest["checkpoints"] if item["id"] == checkpoint), None)
    if entry is None:
        raise ValueError(f"unknown checkpoint: {checkpoint}")
    entry["status"] = status
    entry["updated"] = time.time()
    _write_manifest(directory, manifest)
    return {"session": str(directory), "checkpoint": checkpoint, "status": status}


def set_status(directory: Path, status: str) -> dict:
    directory = _session_directory(directory)
    if status not in SESSION_STATUSES:
        raise ValueError(f"session status must be one of: {', '.join(SESSION_STATUSES)}")
    manifest = _load_manifest(directory)
    manifest["status"] = status
    _write_manifest(directory, manifest)
    return {"session": str(directory), "status": status}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="create an isolated session directory")
    init.add_argument("title")
    init.add_argument("--root", type=Path, default=Path(os.environ.get(
        "AGENT_FIGURE_OUT_DIR", "~/.agent-skills/figure-out")))
    adder = sub.add_parser("add", help="add or update a checkpoint in the session")
    adder.add_argument("session", type=Path)
    adder.add_argument("checkpoint")
    adder.add_argument("--title", help="short human label for the checkpoint")
    adder.add_argument("--status", choices=STATUSES, default="pending")
    marker = sub.add_parser("mark", help="update a checkpoint status")
    marker.add_argument("session", type=Path)
    marker.add_argument("checkpoint")
    marker.add_argument("status", choices=STATUSES)
    session_status = sub.add_parser("status", help="update the session-level status")
    session_status.add_argument("session", type=Path)
    session_status.add_argument("status", choices=SESSION_STATUSES)
    args = parser.parse_args()
    if args.command == "init":
        print(json.dumps({"session": str(initialize(args.title, args.root))}))
    elif args.command == "add":
        print(json.dumps(add_checkpoint(args.session, args.checkpoint, args.title, args.status)))
    elif args.command == "mark":
        print(json.dumps(mark(args.session, args.checkpoint, args.status)))
    else:
        print(json.dumps(set_status(args.session, args.status)))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(f"Session error: {error}")
