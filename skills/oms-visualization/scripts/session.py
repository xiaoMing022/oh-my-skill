"""Create project-local visualization sessions and publish framed previews."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import time
from html import escape
from pathlib import Path

CHECKPOINT_ID_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,31}")
STATUSES = ("pending", "waiting", "confirmed", "needs-review", "deferred", "skipped")
STATUS_LABELS = {
    "pending": "待定",
    "waiting": "待选择",
    "confirmed": "已确认",
    "needs-review": "需复核",
    "deferred": "已推迟",
    "skipped": "已跳过",
}
_SKILL_DIRECTORY = Path(__file__).resolve().parent.parent
GITIGNORE_TEXT = "serve.json\nserve.stale-*.json\n"


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def read_fragment(path: Path) -> str:
    raw = path.read_bytes()
    if len(raw) > 1_000_000:
        raise ValueError("fragment exceeds 1 MB; reduce embedded data")
    fragment = raw.decode("utf-8")
    if not fragment.strip():
        raise ValueError("fragment is empty")
    if re.search(r"<!doctype\b|<(?:html|head|body)(?:\s|>)", fragment, re.I):
        raise ValueError("expected an HTML fragment, not a full document")
    return fragment


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


def _frame_template() -> str:
    return (_SKILL_DIRECTORY / "assets" / "frame.html").read_text(encoding="utf-8")


def _kit_css() -> str:
    return (_SKILL_DIRECTORY / "assets" / "visualize.css").read_text(encoding="utf-8")


def _kit_js() -> str:
    inner = (_SKILL_DIRECTORY / "assets" / "visualize.html").read_text(encoding="utf-8")
    return inner.replace("<!--__INLINE_VISUALIZATION_FRAGMENT__-->", "")


def _wrap_frame(title: str, meta: str, checkpoint_id: str, revision: str,
                status: str, body: str) -> str:
    template = _frame_template()
    full_body = body
    if checkpoint_id:
        kit_js = _kit_js()
        if kit_js.strip():
            full_body = body + "\n" + kit_js
    return (template
            .replace("{{SESSION_TITLE}}", escape(title))
            .replace("{{CHECKPOINT_ID}}", escape(checkpoint_id))
            .replace("{{REVISION}}", escape(revision))
            .replace("{{STATUS}}", escape(STATUS_LABELS.get(status, status)))
            .replace("{{TITLE}}", escape(f"{checkpoint_id} · {title}" if checkpoint_id else title))
            .replace("{{SESSION_META}}", escape(meta))
            .replace("{{CHECKPOINT_META}}", escape(f"{checkpoint_id} {revision}".strip()))
            .replace("{{KIT_CSS}}", _kit_css())
            .replace("{{BODY}}", full_body))


def _render_index(directory: Path, manifest: dict) -> None:
    title = str(manifest.get("title") or directory.name)
    items = []
    for entry in manifest["checkpoints"]:
        identifier = entry["id"]
        label = escape(str(entry.get("title") or identifier))
        status = str(entry.get("status") or "waiting")
        pill = escape(STATUS_LABELS.get(status, status))
        items.append(
            f'      <li><a href="checkpoints/{escape(identifier)}.html">{label}'
            f'<span class="vz-pill">{pill}</span></a></li>',
        )
    nav = "<ul class=\"vz-nav\">\n" + "\n".join(items) + "\n    </ul>" if items else ""
    body = (f"    {nav}\n" if nav else "") + "    <p>选择一个检查点查看当前版本。</p>"
    atomic_write(directory / "index.html",
                 _wrap_frame(title, title, "", "", "", body))


def initialize(title: str, root: Path) -> Path:
    if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", title) is None or len(title) > 64:
        raise ValueError("title must be lowercase ASCII words separated by hyphens (max 64 characters)")
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    slug = title
    counter = 2
    directory = root / slug
    while directory.exists():
        slug = f"{title}-{counter}"
        counter += 1
        directory = root / slug
    directory.mkdir()
    (directory / "revisions").mkdir()
    (directory / "checkpoints").mkdir()
    atomic_write(directory / "session.md", f"# {title}\n\nStatus: exploring\n")
    manifest = {"title": title, "checkpoints": []}
    _write_manifest(directory, manifest)
    _render_index(directory, manifest)
    gitignore = root / ".gitignore"
    if not gitignore.is_file():
        atomic_write(gitignore, GITIGNORE_TEXT)
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
    manifest = _load_manifest(directory)
    fragment = read_fragment(source)
    existing = [p for p in (directory / "revisions").glob(f"{checkpoint}-*.html")]
    numbers = []
    for path in existing:
        match = re.fullmatch(rf"{re.escape(checkpoint)}-(\d+)\.html", path.name)
        if match:
            numbers.append(int(match.group(1)))
    number = (max(numbers) + 1) if numbers else 1
    revision_label = f"R{number}"
    session_title = str(manifest.get("title") or directory.name)
    entry_status = status or "waiting"
    revision = directory / "revisions" / f"{checkpoint}-{number:02d}.html"
    atomic_write(revision, _wrap_frame(session_title, session_title,
                                       checkpoint, revision_label, entry_status, fragment))
    atomic_write(directory / "revisions" / f"{checkpoint}-{number:02d}.fragment.html", fragment)
    try:
        _wrap_frame(session_title, session_title, checkpoint,
                    revision_label, entry_status, fragment)
    except (OSError, ValueError):
        revision.unlink(missing_ok=True)
        raise
    target = directory / "checkpoints" / f"{checkpoint}.html"
    atomic_write(target, _wrap_frame(session_title, session_title,
                                     checkpoint, revision_label, entry_status, fragment))
    atomic_write(directory / "checkpoints" / f"{checkpoint}.fragment.html", fragment)
    entry = next((item for item in manifest["checkpoints"] if item["id"] == checkpoint), None)
    if entry is None:
        entry = {"id": checkpoint}
        manifest["checkpoints"].append(entry)
    if title:
        entry["title"] = title
    entry.setdefault("title", checkpoint)
    # A fresh publication reopens the question unless the caller says otherwise.
    entry["status"] = entry_status
    entry["updated"] = time.time()
    entry["file"] = f"checkpoints/{checkpoint}.html"
    _write_manifest(directory, manifest)
    _render_index(directory, manifest)
    return {"session": str(directory), "checkpoint": checkpoint,
            "revision": str(revision), "revision_label": revision_label,
            "fragment": str(target)}


def mark(directory: Path, checkpoint: str, status: str) -> dict:
    directory = _session_directory(directory)
    _validated(checkpoint, status)
    manifest = _load_manifest(directory)
    entry = next((item for item in manifest["checkpoints"] if item["id"] == checkpoint), None)
    if entry is None:
        raise ValueError(f"unknown checkpoint: {checkpoint}")
    entry["status"] = status
    _write_manifest(directory, manifest)
    _render_index(directory, manifest)
    return {"session": str(directory), "checkpoint": checkpoint, "status": status}


def list_sessions(root: Path) -> list:
    root = root.expanduser().resolve()
    if not root.is_dir():
        return []
    result = []
    for child in sorted(root.iterdir()):
        manifest_path = child / "checkpoints.json"
        if not child.is_dir() or not manifest_path.is_file():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        result.append({
            "session": str(child),
            "slug": child.name,
            "title": manifest.get("title", child.name),
            "checkpoints": len(manifest.get("checkpoints", [])),
        })
    return result


def _prune_candidates(target: Path | None, root: Path,
                      older_than_days: float | None) -> list[Path]:
    if target is not None:
        session = target.expanduser().resolve()
        if root not in session.parents and session != root:
            raise ValueError("session is not under the visualization root")
        _session_directory(session)
        return [session]
    if older_than_days is None:
        raise ValueError("prune needs a session or --older-than <days>")
    cutoff = time.time() - older_than_days * 86400
    candidates = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or not (child / "checkpoints.json").is_file():
            continue
        try:
            mtime = (child / "checkpoints.json").stat().st_mtime
        except OSError:
            continue
        if mtime < cutoff:
            candidates.append(child)
    return candidates


def prune(target: Path, root: Path, older_than_days: float | None) -> dict:
    root = root.expanduser().resolve()
    removed = []
    for session in _prune_candidates(target, root, older_than_days):
        shutil.rmtree(session)
        removed.append(str(session))
    return {"removed": removed}


def default_root() -> Path:
    base = os.environ.get("OH_MY_SKILLS_DIR", ".oh-my-skills").strip() or ".oh-my-skills"
    # Allow an absolute override; otherwise treat as folder name under cwd.
    base_path = Path(base)
    if base_path.is_absolute():
        return base_path / "visualization"
    return Path.cwd() / base_path / "visualization"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="create an isolated session directory")
    init.add_argument("title")
    init.add_argument("--root", type=Path, default=default_root())
    update = sub.add_parser("publish", help="publish a fragment to one checkpoint")
    update.add_argument("session", type=Path)
    update.add_argument("source", type=Path)
    update.add_argument("--checkpoint", default="main", help="checkpoint ID, e.g. D1")
    update.add_argument("--title", help="short human tab label for the checkpoint")
    update.add_argument("--status", choices=STATUSES,
                        help="tab status after publishing (default: waiting)")
    marker = sub.add_parser("mark", help="update the status badge on a checkpoint")
    marker.add_argument("session", type=Path)
    marker.add_argument("checkpoint")
    marker.add_argument("status", choices=STATUSES)
    lister = sub.add_parser("list", help="list sessions under the root")
    lister.add_argument("--root", type=Path, default=default_root())
    pruner = sub.add_parser("prune", help="delete sessions (manual only, requires --force)")
    pruner.add_argument("session", type=Path, nargs="?",
                        help="session directory to delete")
    pruner.add_argument("--root", type=Path, default=default_root())
    pruner.add_argument("--older-than", type=float, default=None,
                        help="delete sessions idle longer than this many days")
    pruner.add_argument("--force", action="store_true",
                        help="actually delete; without it, only list candidates")
    args = parser.parse_args()
    if args.command == "init":
        print(json.dumps({"session": str(initialize(args.title, args.root))}))
    elif args.command == "publish":
        print(json.dumps(publish(args.session, args.source, args.checkpoint,
                                 args.title, args.status)))
    elif args.command == "mark":
        print(json.dumps(mark(args.session, args.checkpoint, args.status)))
    elif args.command == "list":
        print(json.dumps({"sessions": list_sessions(args.root)}))
    else:
        root = args.root.expanduser().resolve()
        if not args.force:
            print(json.dumps({"candidates": [
                str(p) for p in _prune_candidates(args.session, root, args.older_than)]}))
            return
        print(json.dumps(prune(args.session, args.root, args.older_than)))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(f"Session error: {error}")
