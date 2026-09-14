from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import secrets
import signal
import tempfile
import threading
import time
from datetime import datetime, timezone
from http.client import HTTPConnection, HTTPException
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

_SKILL_DIRECTORY = Path(__file__).resolve().parents[1]
_FRAGMENT_PLACEHOLDER = "<!--__INLINE_VISUALIZATION_FRAGMENT__-->"
_DATA_CHOICE_RE = re.compile(r"\bdata-choice\s*=")
CHECKPOINT_ID_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,31}")
_CHOICE_CONFIRM_HINT = (
    '<p class="viz-choice-confirm-hint text-small text-muted" '
    'data-choice-confirm-hint="">'
    "点选会记录为预选参考；最终请在对话里回复确认。"
    "</p>\n"
)
_STATUS_LABELS = {
    "pending": "待定",
    "waiting": "待选择",
    "confirmed": "已确认",
    "needs-review": "需复核",
    "deferred": "已推迟",
    "skipped": "已跳过",
}
_RESOURCE_SOURCES = " ".join(
    (
        "blob:",
        "data:",
        "https://cdnjs.cloudflare.com",
        "https://cdn.jsdelivr.net",
        "https://esm.sh",
        "https://fonts.bunny.net",
        "https://fonts.googleapis.com",
        "https://fonts.gstatic.com",
        "https://unpkg.com",
    ),
)
_FRAME_CSP = "; ".join(
    (
        "default-src 'none'",
        f"script-src 'unsafe-inline' 'unsafe-eval' 'wasm-unsafe-eval' {_RESOURCE_SOURCES}",
        f"style-src 'unsafe-inline' {_RESOURCE_SOURCES}",
        f"img-src {_RESOURCE_SOURCES}",
        f"font-src {_RESOURCE_SOURCES}",
        f"media-src {_RESOURCE_SOURCES}",
        "worker-src blob:",
        "connect-src blob: data:",
        "frame-src 'none'",
        "object-src 'none'",
        "base-uri 'none'",
        "form-action 'none'",
    ),
)
# A srcdoc frame inherits the shell CSP, so the shell must permit resources
# which the stricter inner frame policy may load. The live shell additionally
# talks to its own origin: checkpoint frames, version polling, and choice
# reporting.
_SHELL_CSP = (
    _FRAME_CSP
    .replace("frame-src 'none'", "frame-src 'self'")
    .replace("connect-src blob: data:", "connect-src 'self' blob: data:")
)

_SESSION_SHELL = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="__CSP__">
<title>__TITLE__</title>
<style>
:root{color-scheme:light dark}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{display:flex;flex-direction:column;font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;background:light-dark(rgb(255 255 255),rgb(24 24 24));color:light-dark(rgb(23 23 23),rgb(237 237 237))}
header{flex:none;display:flex;flex-wrap:wrap;align-items:center;gap:.25rem .75rem;padding:.5rem .75rem;border-bottom:1px solid light-dark(rgb(0 0 0/.12),rgb(255 255 255/.16))}
header h1{margin:0;font-size:14px;font-weight:500}
nav[role=tablist]{display:flex;flex-wrap:wrap;gap:.25rem}
nav [role=tab]{display:inline-flex;align-items:center;gap:.4rem;padding:.3rem .65rem;border:1px solid light-dark(rgb(0 0 0/.15),rgb(255 255 255/.2));border-radius:999px;background:transparent;color:inherit;font:inherit;cursor:pointer}
nav [role=tab][aria-selected=true]{background:light-dark(rgb(23 23 23),rgb(237 237 237));border-color:transparent;color:light-dark(rgb(255 255 255),rgb(24 24 24))}
.vb-tab-id{font-weight:500}
.vb-status{font-size:11px;padding:.05rem .4rem;border-radius:999px;background:light-dark(rgb(0 0 0/.08),rgb(255 255 255/.14))}
[role=tab][aria-selected=true] .vb-status{background:light-dark(rgb(255 255 255/.25),rgb(0 0 0/.2))}
.vb-stale{flex-basis:100%;margin:0;font-size:12px;color:light-dark(rgb(150 40 27),rgb(255 160 140))}
main{flex:1;min-height:0}
main [role=tabpanel]{height:100%}
main iframe{display:block;width:100%;height:100%;border:0}
.vb-empty{margin:2rem auto;color:light-dark(rgb(0 0 0/.55),rgb(255 255 255/.6))}
</style>
</head>
<body>
<header>
<h1>__TITLE__</h1>
<nav role="tablist" aria-label="决策检查点">__TABS__</nav>
<p class="vb-stale" id="vb-stale" hidden>预览服务已停止；请在对话中让代理重新启动预览。</p>
</header>
<main>__PANELS__</main>
<script>
(() => {
__SCRIPT__
})();
</script>
</body>
</html>
"""

# Shared tab behavior: switching, keyboard support, restoring the saved tab.
_TABS_JS = """
  const tablist = document.querySelector("[role=tablist]");
  const main = document.querySelector("main");
  const storageKey = "visual-brainstorm-active-tab";
  const allTabs = () => Array.from(tablist.querySelectorAll("[data-vb-tab]"));
  const activate = (id, persist) => {
    let found = false;
    for (const tab of allTabs()) {
      const selected = tab.dataset.vbTab === id;
      tab.setAttribute("aria-selected", selected ? "true" : "false");
      const panel = document.getElementById("panel-" + tab.dataset.vbTab);
      if (panel != null) panel.hidden = !selected;
      if (selected) found = true;
    }
    if (found && persist) {
      try { sessionStorage.setItem(storageKey, id); } catch {}
    }
    return found;
  };
  tablist.addEventListener("click", (event) => {
    const tab = event.target.closest("[data-vb-tab]");
    if (tab != null) activate(tab.dataset.vbTab, true);
  });
  tablist.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    const tabs = allTabs();
    const index = tabs.findIndex((tab) => tab.getAttribute("aria-selected") === "true");
    if (index < 0) return;
    const next = tabs[(index + (event.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length];
    activate(next.dataset.vbTab, true);
    next.focus();
    event.preventDefault();
  });
  let saved = null;
  try { saved = sessionStorage.getItem(storageKey); } catch {}
  if (saved != null) activate(saved, false);
"""

# Live-preview extras: incremental sync from /__version (new tabs appear,
# changed checkpoints reload their own frame, badges update in place — the
# page itself never reloads) and forwarding on-page selections to /__choice.
_LIVE_JS = """
  const banner = document.getElementById("vb-stale");
  const buildTab = (cp) => {
    const button = document.createElement("button");
    button.type = "button";
    button.setAttribute("role", "tab");
    button.id = "tab-" + cp.id;
    button.setAttribute("aria-controls", "panel-" + cp.id);
    button.setAttribute("aria-selected", "false");
    button.dataset.vbTab = cp.id;
    const identifier = document.createElement("span");
    identifier.className = "vb-tab-id";
    identifier.textContent = cp.id;
    const label = document.createElement("span");
    label.className = "vb-tab-label";
    label.textContent = cp.title;
    const badge = document.createElement("span");
    badge.className = "vb-status";
    badge.textContent = cp.statusLabel || "";
    badge.hidden = !cp.statusLabel;
    button.append(identifier, " ", label, " ", badge);
    return button;
  };
  const buildPanel = (cp) => {
    const section = document.createElement("section");
    section.setAttribute("role", "tabpanel");
    section.id = "panel-" + cp.id;
    section.setAttribute("aria-labelledby", "tab-" + cp.id);
    section.hidden = true;
    const frame = document.createElement("iframe");
    frame.setAttribute("sandbox", "allow-scripts");
    frame.referrerPolicy = "no-referrer";
    frame.title = cp.title;
    frame.src = "/checkpoint/" + cp.id;
    section.append(frame);
    return section;
  };
  const updateTab = (cp) => {
    const button = document.getElementById("tab-" + cp.id);
    if (button == null) return;
    const label = button.querySelector(".vb-tab-label");
    if (label != null) label.textContent = cp.title;
    const badge = button.querySelector(".vb-status");
    if (badge != null) {
      badge.textContent = cp.statusLabel || "";
      badge.hidden = !cp.statusLabel;
    }
  };
  let known = null;
  let newestStamp = 0;
  const seedState = (state) => {
    known = new Map();
    for (const cp of state.checkpoints) {
      known.set(cp.id, { etag: cp.etag, updated: cp.updated || 0 });
      newestStamp = Math.max(newestStamp, cp.updated || 0);
    }
  };
  const applyState = (state) => {
    const seen = new Set();
    let newest = null;
    for (const cp of state.checkpoints) {
      seen.add(cp.id);
      if (newest == null || (cp.updated || 0) > (newest.updated || 0)) newest = cp;
      const previous = known.get(cp.id);
      if (previous == null) {
        document.querySelector(".vb-empty")?.remove();
        tablist.append(buildTab(cp));
        main.append(buildPanel(cp));
      } else {
        if (previous.etag !== cp.etag) {
          const frame = document.querySelector("#panel-" + cp.id + " iframe");
          if (frame != null) frame.src = "/checkpoint/" + cp.id + "?v=" + encodeURIComponent(cp.etag);
        }
        updateTab(cp);
      }
      known.set(cp.id, { etag: cp.etag, updated: cp.updated || 0 });
    }
    for (const id of Array.from(known.keys())) {
      if (seen.has(id)) continue;
      known.delete(id);
      const button = document.getElementById("tab-" + id);
      const wasActive = button?.getAttribute("aria-selected") === "true";
      button?.remove();
      document.getElementById("panel-" + id)?.remove();
      if (wasActive) {
        const rest = allTabs();
        if (rest.length > 0) activate(rest[0].dataset.vbTab, false);
      }
    }
    if (newest != null && (newest.updated || 0) > newestStamp) {
      newestStamp = newest.updated || 0;
      activate(newest.id, false);
    }
  };
  let failures = 0;
  const poll = () => {
    fetch("/__version", { cache: "no-store" })
      .then((response) => response.json())
      .then((state) => {
        failures = 0;
        banner.hidden = true;
        if (known == null) seedState(state); else applyState(state);
        setTimeout(poll, 2000);
      })
      .catch(() => {
        failures += 1;
        if (failures >= 3) banner.hidden = false;
        setTimeout(poll, failures >= 3 ? 10000 : 2000);
      });
  };
  setTimeout(poll, 1000);
  window.addEventListener("message", (event) => {
    const data = event.data;
    if (data == null || data.type !== "visual-brainstorm-choice" || typeof data.choice !== "string") return;
    for (const frame of document.querySelectorAll("main iframe")) {
      if (frame.contentWindow !== event.source) continue;
      const panel = frame.closest("[role=tabpanel]");
      const id = panel != null ? panel.id.replace(/^panel-/, "") : "";
      if (id === "") return;
      fetch("/__choice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ checkpoint: id, choice: data.choice.slice(0, 200) }),
      }).catch(() => {});
      return;
    }
  });
"""


def atomic_write(path: Path, content: str, overwrite: bool = True) -> None:
    """Replace in the same directory, so readers never see a partial file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if overwrite:
            os.replace(temporary, path)
        else:
            os.link(temporary, path)  # Atomic create: do not clobber a concurrent export.
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


def load_manifest(session_dir: Path) -> dict:
    """Read and validate the checkpoint manifest owned by session.py."""
    path = session_dir / "checkpoints.json"
    if not path.is_file():
        raise ValueError("not an initialized session directory (missing checkpoints.json)")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or not isinstance(manifest.get("checkpoints"), list):
        raise ValueError("invalid session manifest")
    seen = set()
    for entry in manifest["checkpoints"]:
        identifier = entry.get("id") if isinstance(entry, dict) else None
        if (not isinstance(identifier, str)
                or CHECKPOINT_ID_RE.fullmatch(identifier) is None
                or identifier in seen):
            raise ValueError("invalid session manifest")
        seen.add(identifier)
    return manifest


def checkpoint_fragment_path(session_dir: Path, checkpoint: str) -> Path:
    return session_dir / "checkpoints" / f"{checkpoint}.fragment.html"


def session_state(session_dir: Path) -> dict:
    """Manifest plus a change marker per checkpoint; drives incremental refresh."""
    manifest = load_manifest(session_dir)
    digest = hashlib.sha256((session_dir / "checkpoints.json").read_bytes())
    checkpoints = []
    for entry in manifest["checkpoints"]:
        stat = checkpoint_fragment_path(session_dir, entry["id"]).stat()
        etag = f"{stat.st_mtime_ns}-{stat.st_size}"
        digest.update(f"|{entry['id']}:{etag}".encode())
        checkpoints.append({
            "id": entry["id"],
            "title": str(entry.get("title") or entry["id"]),
            "status": entry.get("status"),
            "statusLabel": _STATUS_LABELS.get(entry.get("status"), ""),
            "updated": entry.get("updated") or 0,
            "etag": etag,
        })
    return {"etag": digest.hexdigest(), "title": manifest.get("title"),
            "checkpoints": checkpoints}


def record_choice(session_dir: Path, checkpoint: object, choice: object) -> dict:
    """Persist the latest on-page selection per checkpoint (preview feedback)."""
    manifest = load_manifest(session_dir)
    if not any(entry["id"] == checkpoint for entry in manifest["checkpoints"]):
        raise ValueError("unknown checkpoint")
    if not isinstance(choice, str) or not 1 <= len(choice.strip()) <= 200:
        raise ValueError("invalid choice")
    path = session_dir / "choices.json"
    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        existing = {}
    if not isinstance(existing, dict):
        existing = {}
    existing[checkpoint] = {
        "choice": choice.strip(),
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    atomic_write(path, json.dumps(existing, ensure_ascii=False, indent=2) + "\n")
    return existing[checkpoint]


def server_request(info_path: Path, source_path: Path, stop: bool = False) -> dict:
    """Authenticate the instance over loopback; never trust a PID or stored URL."""
    info = json.loads(info_path.read_text(encoding="utf-8"))
    if not isinstance(info, dict):
        raise ValueError("invalid server metadata")
    port, token = info.get("port"), info.get("token")
    if (type(port) is not int or not 1 <= port <= 65535
            or not isinstance(token, str) or len(token) != 64
            or info.get("source") != str(source_path.resolve())):
        raise ValueError("server metadata does not match this preview")
    connection = HTTPConnection("127.0.0.1", port, timeout=2)
    try:
        connection.request("POST" if stop else "GET",
                           "/__stop" if stop else "/__health",
                           headers={"X-Preview-Token": token})
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError("preview identity check failed")
        payload = json.loads(response.read())
        if not isinstance(payload, dict) or payload.get("instance") != token or payload.get("source") != info["source"]:
            raise ValueError("preview identity check failed")
        return {"url": f"http://127.0.0.1:{port}/", "source": info["source"],
                "status": "stopping" if stop else "running"}
    finally:
        connection.close()


def _with_choice_confirm_hint(fragment: str) -> str:
    if "data-choice-confirm-hint" in fragment:
        return fragment
    if _DATA_CHOICE_RE.search(fragment) is None:
        return fragment
    return _CHOICE_CONFIRM_HINT + fragment


def _frame_document(fragment: str, document_title: str) -> str:
    """Wrap one fragment in the sandboxed inner document shown inside a tab."""
    stylesheet = (_SKILL_DIRECTORY / "assets" / "visualize.css").read_text(
        encoding="utf-8",
    )
    inner_kit = (_SKILL_DIRECTORY / "assets" / "visualize.html").read_text(
        encoding="utf-8",
    )
    inner_html = inner_kit.replace(_FRAGMENT_PLACEHOLDER, fragment)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="{_FRAME_CSP}">
<title>{document_title}</title>
<style>{stylesheet}
html>body{{padding:0}}</style>
</head>
<body>
{inner_html}
</body>
</html>
"""


def render(fragment_path: Path, title: str | None = None) -> str:
    """Render one fragment as a standalone single-frame document (exports, validation)."""
    fragment = _with_choice_confirm_hint(read_fragment(fragment_path))
    document_title = escape(title or fragment_path.stem.replace("-", " ").title())
    frame_html = _frame_document(fragment, document_title)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="{_SHELL_CSP}">
<title>{document_title}</title>
<style>:root{{color-scheme:light dark;background:light-dark(rgb(255 255 255), rgb(24 24 24))}}html,body{{margin:0}}body{{box-sizing:border-box;padding:1rem;background:inherit}}iframe{{display:block;width:100%;height:calc(100vh - 2rem);margin:0 auto;border:0}}</style>
</head>
<body>
<iframe sandbox="allow-scripts" referrerpolicy="no-referrer" title="{document_title}" srcdoc="{escape(frame_html)}"></iframe>
</body>
</html>
"""


def render_checkpoint(session_dir: Path, checkpoint: str, title: str | None = None) -> str:
    """Render one checkpoint's inner frame document, served at /checkpoint/<id>."""
    session_dir = session_dir.resolve()
    manifest = load_manifest(session_dir)
    entry = next((item for item in manifest["checkpoints"] if item["id"] == checkpoint), None)
    if entry is None:
        raise ValueError(f"unknown checkpoint: {checkpoint}")
    fragment = _with_choice_confirm_hint(
        read_fragment(checkpoint_fragment_path(session_dir, checkpoint)),
    )
    session_title = str(title or manifest.get("title") or session_dir.name)
    label = str(entry.get("title") or checkpoint)
    return _frame_document(fragment, escape(f"{session_title} · {label}"))


def render_session(session_dir: Path, title: str | None = None, live: bool = False) -> str:
    """Render the fixed tabbed shell for a session.

    live=True serves lightweight frames loaded from /checkpoint/<id> plus
    incremental auto-refresh; live=False inlines every checkpoint so the
    document is a self-contained offline export with no polling.
    """
    session_dir = session_dir.resolve()
    manifest = load_manifest(session_dir)
    checkpoints = manifest["checkpoints"]
    document_title = escape(str(title or manifest.get("title") or session_dir.name))
    default_id = (
        max(checkpoints, key=lambda entry: entry.get("updated") or 0)["id"]
        if checkpoints else ""
    )
    tabs, panels = [], []
    for entry in checkpoints:
        identifier = entry["id"]
        label = escape(str(entry.get("title") or identifier))
        status_label = _STATUS_LABELS.get(entry.get("status"), "")
        selected = "true" if identifier == default_id else "false"
        badge_hidden = "" if status_label else " hidden"
        tabs.append(
            f'<button type="button" role="tab" id="tab-{identifier}" '
            f'aria-controls="panel-{identifier}" aria-selected="{selected}" '
            f'data-vb-tab="{identifier}">'
            f'<span class="vb-tab-id">{identifier}</span> '
            f'<span class="vb-tab-label">{label}</span> '
            f'<span class="vb-status"{badge_hidden}>{status_label}</span></button>'
        )
        hidden = "" if identifier == default_id else " hidden"
        if live:
            frame = (
                f'<iframe sandbox="allow-scripts" referrerpolicy="no-referrer" '
                f'title="{label}" src="/checkpoint/{identifier}"></iframe>'
            )
        else:
            fragment = _with_choice_confirm_hint(
                read_fragment(checkpoint_fragment_path(session_dir, identifier)),
            )
            frame_html = _frame_document(fragment, f"{document_title} · {label}")
            frame = (
                f'<iframe sandbox="allow-scripts" referrerpolicy="no-referrer" '
                f'title="{label}" srcdoc="{escape(frame_html)}"></iframe>'
            )
        panels.append(
            f'<section role="tabpanel" id="panel-{identifier}" '
            f'aria-labelledby="tab-{identifier}"{hidden}>{frame}</section>'
        )
    if not panels:
        panels.append('<p class="vb-empty">该会话还没有已发布的检查点预览。</p>')
    return (
        _SESSION_SHELL
        .replace("__CSP__", _SHELL_CSP)
        .replace("__TITLE__", document_title)
        .replace("__TABS__", "".join(tabs))
        .replace("__PANELS__", "\n".join(panels))
        .replace("__SCRIPT__", _TABS_JS + (_LIVE_JS if live else ""))
    )


def render_source(source: Path, title: str | None = None, live: bool = False) -> str:
    """Render a session directory as a tabbed document, or a fragment file directly."""
    return render_session(source, title, live=live) if source.is_dir() else render(source, title)


def _request_path(raw_path: str) -> str:
    return raw_path.split("?", 1)[0]


def serve(
    source_path: Path,
    title: str | None,
    port: int,
    info_path: Path | None = None,
    idle_timeout: int = 1800,
) -> None:
    source_path = source_path.resolve()
    is_session = source_path.is_dir()
    # Fail before announcing a broken preview; the offline render also
    # validates every checkpoint fragment, which the live shell does not read.
    render_source(source_path, title, live=False)
    token = secrets.token_hex(32)
    identity = {"instance": token, "source": str(source_path)}
    last_activity = time.monotonic()
    stopping = False
    choices_lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def setup(self) -> None:
            super().setup()
            self.connection.settimeout(2)

        def respond_json(self, payload: dict) -> None:
            encoded = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def respond_html(self, document: str) -> None:
            nonlocal last_activity
            encoded = document.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            last_activity = time.monotonic()
            self.wfile.write(encoded)

        def management(self, stop: bool = False) -> None:
            nonlocal stopping
            if not secrets.compare_digest(self.headers.get("X-Preview-Token", ""), token):
                self.send_error(403)
                return
            self.respond_json(identity)
            if stop:
                stopping = True

        def do_POST(self) -> None:
            nonlocal last_activity
            if self.path == "/__stop":
                self.management(stop=True)
                return
            if _request_path(self.path) == "/__choice" and is_session:
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                except ValueError:
                    length = 0
                if not 0 < length <= 4096:
                    self.send_error(400)
                    return
                try:
                    payload = json.loads(self.rfile.read(length))
                    if not isinstance(payload, dict):
                        raise ValueError("invalid payload")
                    with choices_lock:
                        recorded = record_choice(source_path, payload.get("checkpoint"),
                                                 payload.get("choice"))
                except (OSError, ValueError):
                    self.send_error(400)
                    return
                last_activity = time.monotonic()
                self.respond_json({"ok": True, "recorded": recorded})
                return
            self.send_error(404)

        def do_GET(self) -> None:
            request_path = _request_path(self.path)
            if request_path == "/__health":
                self.management()
                return
            if request_path == "/__version" and is_session:
                # Change probes never extend the idle lifetime.
                try:
                    self.respond_json(session_state(source_path))
                except (OSError, ValueError):
                    self.send_error(500)
                return
            if request_path.startswith("/checkpoint/") and is_session:
                identifier = request_path[len("/checkpoint/"):]
                if CHECKPOINT_ID_RE.fullmatch(identifier) is None:
                    self.send_error(404)
                    return
                try:
                    document = render_checkpoint(source_path, identifier, title)
                except ValueError:
                    self.send_error(404)
                    return
                except OSError:
                    self.send_error(500)
                    return
                self.respond_html(document)
                return
            if request_path not in ("/", "/index.html"):
                self.send_error(404)
                return
            try:
                document = render_source(source_path, title, live=is_session)
            except (OSError, ValueError):
                self.send_error(500)
                return
            self.respond_html(document)

        def log_message(self, _format: str, *_args: object) -> None:
            pass

    # Exclusive metadata ownership also prevents concurrent starts for one session.
    # A hard crash can leave this file behind: recovery requires an explicit
    # failed identity check and renaming the stale file, never killing its PID.
    info_fd = None
    if info_path is not None:
        info_path.parent.mkdir(parents=True, exist_ok=True)
        info_fd = os.open(info_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    server = None
    previous_signals = {}
    def request_stop(_signum: int, _frame: object) -> None:
        nonlocal stopping
        stopping = True

    try:
        server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        server.timeout = 0.25
        for signum in (signal.SIGTERM, signal.SIGINT):
            previous_signals[signum] = signal.signal(signum, request_stop)
        url = f"http://127.0.0.1:{server.server_port}/"
        payload = {"url": url, "port": server.server_port, "pid": os.getpid(),
                   "source": str(source_path), "token": token}
        if info_fd is not None:
            os.close(info_fd)
            info_fd = None
            atomic_write(info_path, json.dumps(payload) + "\n")
        print(url, flush=True)
        while not stopping and time.monotonic() - last_activity < idle_timeout:
            server.handle_request()
    finally:
        if server is not None:
            server.server_close()
        for signum, handler in previous_signals.items():
            signal.signal(signum, handler)
        if info_fd is not None:
            os.close(info_fd)
        if info_path is not None:
            # Do not remove metadata replaced by a later instance.
            try:
                current = info_path.read_text(encoding="utf-8")
                parsed = json.loads(current) if current else {}
                if not current or (isinstance(parsed, dict) and parsed.get("token") == token):
                    info_path.unlink()
            except (OSError, ValueError):
                pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a session directory (tabbed checkpoints) or one fragment as HTML.",
    )
    parser.add_argument(
        "source",
        type=Path,
        help="absolute session directory (tabbed preview) or fragment HTML path",
    )
    parser.add_argument("--status", action="store_true", help="verify the preview instance")
    parser.add_argument("--stop", action="store_true", help="stop the verified preview instance")
    parser.add_argument("--idle-timeout", type=int, default=1800, help="exit after idle seconds (default 1800)")
    parser.add_argument("--force", action="store_true", help="replace an existing export")
    parser.add_argument(
        "destination",
        type=Path,
        nargs="?",
        help="optional output HTML path",
    )
    parser.add_argument(
        "--title",
        help="document title; defaults to the session or fragment name",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="serve the rendered visualization locally",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="local serve port; defaults to any free port",
    )
    parser.add_argument(
        "--info",
        type=Path,
        help="write serve url/port/pid JSON to this path",
    )
    args = parser.parse_args()
    if sum((args.serve, args.status, args.stop)) > 1:
        parser.error("choose only one of --serve, --status, --stop")
    if (args.serve or args.status or args.stop) and args.destination is not None:
        parser.error("destination is only for exports")
    if args.info is not None and not (args.serve or args.status or args.stop):
        parser.error("--info requires --serve, --status, or --stop")
    if (args.status or args.stop) and args.info is None:
        parser.error("--status and --stop require --info")
    if args.idle_timeout <= 0:
        parser.error("--idle-timeout must be positive")
    if not 0 <= args.port <= 65535:
        parser.error("--port must be between 0 and 65535")
    if args.info and args.info.resolve() == args.source.resolve():
        parser.error("server metadata cannot overwrite the preview source")
    if args.destination and args.destination.resolve() == args.source.resolve():
        parser.error("export cannot overwrite its source")
    if args.status or args.stop:
        print(json.dumps(server_request(args.info, args.source, stop=args.stop)))
        return

    if args.serve:
        serve(args.source, args.title, args.port, args.info, args.idle_timeout)
        return

    # Exports and stdout renders are always offline self-contained documents.
    document = render_source(args.source, args.title, live=False)
    if args.destination is None:
        sys.stdout.write(document)
    else:
        if args.destination.exists() and not args.force:
            parser.error("export exists; choose a new path or use --force for an intended replacement")
        atomic_write(args.destination, document, overwrite=args.force)
        print(args.destination)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, HTTPException) as error:
        sys.exit(f"Preview error: {error}")
