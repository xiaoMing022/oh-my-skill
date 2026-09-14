"""Create isolated workspaces and publish recoverable per-checkpoint preview tabs."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
import uuid
from pathlib import Path

from render import (
    CHECKPOINT_ID_RE,
    atomic_write,
    checkpoint_fragment_path,
    load_manifest,
    read_fragment,
    render,
)

STATUSES = ("pending", "waiting", "confirmed", "needs-review", "deferred", "skipped")


def _write_manifest(directory: Path, manifest: dict) -> None:
    atomic_write(
        directory / "checkpoints.json",
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    )


def _session_directory(directory: Path) -> Path:
    directory = directory.expanduser().resolve()
    if (not (directory / "session.md").is_file()
            or not (directory / "revisions").is_dir()
            or not (directory / "checkpoints").is_dir()):
        raise ValueError("not an initialized session directory")
    return directory


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
    (directory / "revisions").mkdir()
    (directory / "checkpoints").mkdir()
    atomic_write(directory / "session.md", f"# {title}\n\nStatus: exploring\n")
    _write_manifest(directory, {"title": title, "checkpoints": []})
    return directory


def publish(
    directory: Path,
    source: Path,
    checkpoint: str = "main",
    title: str | None = None,
    status: str | None = None,
) -> dict:
    directory = _session_directory(directory)
    _validated(checkpoint, status)
    manifest = load_manifest(directory)
    fragment = read_fragment(source)
    # Write an immutable snapshot first; a failure leaves the live preview intact.
    revision = directory / "revisions" / f"{checkpoint}-{uuid.uuid4().hex}.fragment.html"
    atomic_write(revision, fragment)
    try:
        render(revision)
    except (OSError, ValueError):
        revision.unlink()
        raise
    target = checkpoint_fragment_path(directory, checkpoint)
    atomic_write(target, fragment)
    entry = next((item for item in manifest["checkpoints"] if item["id"] == checkpoint), None)
    if entry is None:
        entry = {"id": checkpoint}
        manifest["checkpoints"].append(entry)
    if title:
        entry["title"] = title
    entry.setdefault("title", checkpoint)
    # A fresh publication reopens the question unless the caller says otherwise.
    entry["status"] = status or "waiting"
    entry["updated"] = time.time()
    _write_manifest(directory, manifest)
    return {"session": str(directory), "checkpoint": checkpoint,
            "revision": str(revision), "fragment": str(target)}


def mark(directory: Path, checkpoint: str, status: str) -> dict:
    directory = _session_directory(directory)
    _validated(checkpoint, status)
    manifest = load_manifest(directory)
    entry = next((item for item in manifest["checkpoints"] if item["id"] == checkpoint), None)
    if entry is None:
        raise ValueError(f"unknown checkpoint: {checkpoint}")
    entry["status"] = status
    _write_manifest(directory, manifest)
    return {"session": str(directory), "checkpoint": checkpoint, "status": status}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="create an isolated session directory")
    init.add_argument("title")
    init.add_argument("--root", type=Path, default=Path(os.environ.get(
        "AGENT_VISUALIZATIONS_DIR", "~/.agent-skills/visualizations")))
    update = sub.add_parser("publish", help="publish a fragment to one checkpoint tab")
    update.add_argument("session", type=Path)
    update.add_argument("source", type=Path)
    update.add_argument("--checkpoint", default="main", help="checkpoint ID, e.g. D1")
    update.add_argument("--title", help="short human tab label for the checkpoint")
    update.add_argument("--status", choices=STATUSES,
                        help="tab status after publishing (default: waiting)")
    marker = sub.add_parser("mark", help="update the status badge on a checkpoint tab")
    marker.add_argument("session", type=Path)
    marker.add_argument("checkpoint")
    marker.add_argument("status", choices=STATUSES)
    args = parser.parse_args()
    if args.command == "init":
        print(json.dumps({"session": str(initialize(args.title, args.root))}))
    elif args.command == "publish":
        print(json.dumps(publish(args.session, args.source, args.checkpoint,
                                 args.title, args.status)))
    else:
        print(json.dumps(mark(args.session, args.checkpoint, args.status)))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(f"Session error: {error}")
