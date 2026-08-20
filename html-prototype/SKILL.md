---
name: html-prototype
description: >
  Turn a product doc or user requirements into a clickable HTML product
  prototype, confirm uncertain directions with the user, and save HTML
  files to disk. Use when the user wants a 产品原型, HTML原型, PRD 转原型,
  需求文档转原型, 高保真原型, 落盘 HTML, 保存原型, clickable prototype, or
  to prototype from a Feishu/Lark doc, wiki, screenshot, image, or
  webpage. Use when the user runs /html-prototype. Do not use for
  standalone 2-3 sketch options with no prototype to build
  (design-preview), for building a project website/app (frontend-design),
  for Feishu 妙搭 apps (lark-apps), or for generated images and game art.
metadata:
  short-description: "HTML prototype from docs; confirm visually; save files"
---

# HTML Prototype

Build a **clickable product prototype** in standalone HTML from whatever
the user already has: a Feishu/Lark doc, pasted requirements, screenshots,
or a webpage. Write real HTML files. Confirm forks the source does not
settle — visually with `design-preview`, otherwise in chat — before
building the full prototype.

This is not `design-preview` alone (that skill only shows sketch options).
This is not `frontend-design` (distinctive UI inside the user's project).
Do not write into a git working tree unless the user asked to 落盘 there.

Reload this skill before creating or updating a prototype.

## Workflow

Follow these steps in order. Stop and tell the user if a step is blocked.

1. **Collect inputs** — read `references/inputs.md`. Gather every Feishu
   URL, webpage, image, local file, pasted requirement, and any save path
   (`落盘`, Desktop, project folder) in this turn.
2. **Check capabilities** — for Feishu/Lark URLs, run the Feishu gate
   below *before* fetching. For webpages and images, use the matching
   intake in `references/inputs.md`.
3. **Extract a product brief** — users, jobs-to-be-done, screens, primary
   flows, entities, brand cues (color, type, density, platform). Keep it
   internal unless they asked for a spec.
4. **Confirm uncertainties** — see **Confirm before building**. Do not
   write the full prototype until this gate passes.
5. **Choose one kit and a theme** — read `references/kits.md`. The kit and
   tokens must match what the user confirmed (or what the source already
   settled). Do not mix kits.
6. **Build and write files** — standalone HTML on disk, local state only,
   realistic copy. Cover the primary flows the source describes. Serve
   the working copy on a local port. If they asked to 落盘, also write
   the files to that path.
7. **Verify** — open the served URL (Playwright if available) at 1280px
   and 390px. Click the primary flow. Fix broken navigation, contrast,
   clipped text, and mixed styles before responding.

## Confirm before building

Like brainstorming: do not pretend a fork is decided. Do not generate the
full prototype while a choice would change IA, chrome, kit, or theme.

Skip this gate when the source already settles the fork, or the user
says 直接做 / 不用确认 / skip.

Otherwise list the open forks internally, then confirm **one at a time**.
Lead with a recommendation and a one-line why. Prefer 2-3 concrete
options over an open prompt.

**Text in chat** when the answer is words: audience, v1 scope, entities,
which flows ship first, C 端 vs 内部工具 when both fit.

**`design-preview` when seeing is better than reading:** layout, nav
(sidebar / top / bottom), density, visual tone, page composition. Read
the `design-preview` skill and follow it for that turn: 2-3 mid-fidelity
options, one question on the screen, local port, user picks in chat.
Then return here and keep going. Do not treat the sketch as the
prototype.

If `design-preview` is unavailable, show the same 2-3 options as a short
text choice and continue.

Do not batch visual and text questions. Do not open `design-preview` for
scope or requirements questions. After each answer, drop settled forks
and only ask what is still open. When none remain, build.

## Feishu gate

Run this gate whenever an input is a Feishu/Lark/Wiki/Docx URL or token
(`feishu.cn`, `feishu.com`, `larksuite.com`, `larkoffice.com`,
`doubao.com` with `/docx/` or `/wiki/`).

1. Confirm the `lark-doc` skill is available in this session. If it is
   not, stop. Tell the user this session cannot read Feishu docs, and
   ask them to paste the content or enable the Lark skills.
2. Confirm `lark-cli` is on `PATH`. If it is not, stop and say so.
3. Read `lark-shared` and `lark-doc` before calling the CLI. Document
   reads use `--as user`.
4. Check login:

   ```bash
   LARKSUITE_CLI_NO_UPDATE_NOTIFIER=1 LARKSUITE_CLI_NO_SKILLS_NOTIFIER=1 \
     lark-cli auth status --json --verify
   ```

   Need a verified **user** identity with docs access. If login is missing
   or unverified, follow `lark-shared` split-flow
   (`auth login --domain docs --no-wait --json`), show the URL and QR,
   and end the turn so the user can authorize. Do not block polling in
   the same turn.
5. Fetch with `lark-cli docs +fetch`. Prefer `--doc-format markdown` and
   `--detail simple`. For long docs: `outline` first, then `section` or
   `keyword` for product/requirements chapters. Do not pull the whole
   doc unless it is short.
6. Permission or missing-scope errors: follow `lark-shared`. Do not
   invent document content.
7. Embedded images: preview or download with `docs +media-preview` /
   `+media-download` when they carry brand or layout. Embedded sheets or
   bitables: extract tokens and read via `lark-sheets` / `lark-base` only
   if they hold requirements or sample data the prototype needs.

Wiki vs Docx is still `lark-doc` (`/wiki/` and `/docx/`). Spreadsheet or
Base links are data sources, not the prototype shell.

## Prototype contract

- Output directory: `~/.grok/prototypes/<slug>/` (create if missing).
  `<slug>` is ASCII, lowercase, hyphenated, stable across updates.
- Default to **one** `index.html` plus optional `proto.css` / `proto.js`
  in that folder. Split files only when one document would be unreadable.
- Full HTML document: `<!doctype html>`, `lang` matching the product
  (usually `zh-CN`), charset, viewport. Not a fragment.
- Client-only. No `fetch`/XHR/WebSocket to backends. Sample data is
  inlined. Navigation is in-page views or relative links in the same folder.
- Primary flows must be clickable end to end (list → detail → create/edit
  → success or empty). Do not ship a pretty first screen with dead
  buttons.
- Use copy, names, and field labels from the source. Invent placeholders
  only where the source is silent, and keep them plausible.
- One kit. One typeface pair. One radius scale. One primary color.
  Map kit variables to the token set in `references/kits.md`.
- Responsive: desktop shell and a usable 390px layout. If the product is
  mobile-only, design mobile first and keep desktop as a framed phone.
- Accessibility: native controls, labels, visible focus, contrast that
  holds on the actual surfaces.

## Delivery

The working copy is always real files on disk:

`~/.grok/prototypes/<slug>/` (create if missing)

Preview that folder on a **local HTTP port**. Info file:
`~/.grok/prototypes/<slug>.serve.json`

If that file exists and its `pid` is still alive, only rewrite the HTML
(the server re-reads files on each request). Ask the user to refresh.

Otherwise start the server in the background:

```bash
python3 <skill-dir>/scripts/serve.py \
  --root ~/.grok/prototypes/<slug> \
  --info ~/.grok/prototypes/<slug>.serve.json
```

Share `http://127.0.0.1:<port>/`. On first start only, `open "$URL"` —
open the URL, not a file path.

## Save / 落盘

HTML on disk is a first-class output, not an afterthought.

- Always keep the working copy under `~/.grok/prototypes/<slug>/`.
- When the user names a destination (Desktop, a folder, the current
  repo, `~/...`), copy the prototype folder there after a successful
  build. Create parents if needed. Overwrite the previous copy of the
  same slug only in that destination.
- When they say 落盘 / 保存 / 导出 / save without a path, write to
  `~/Desktop/<slug>/` and tell them the path. If they wanted the
  project instead, they can say so and you move it.
- Write into a git working tree only when they asked to put it there.
- Default is a folder (`index.html` plus optional css/js). If they
  want a single file, inline css/js into one `index.html` at the
  destination.
- After 落盘, the final message includes both the preview URL and the
  absolute file path. Do not paste the HTML. Do not dump the source doc.

```bash
mkdir -p "<dest>/<slug>"
cp -R ~/.grok/prototypes/<slug>/. "<dest>/<slug>/"
```

## Style

- Theme tokens come from the source: screenshot colors first, then
  written brand, then a restrained inference. Never default to purple
  gradients, Inter, or generic dashboard chrome when the product has a
  face.
- Light theme unless the product is dark or the user asked for dark.
- Status colors (success/warning/danger) are semantic and rare. Do not
  rainbow the UI.
- Density matches the product: tools and admin are tighter; consumer
  marketing is more open. Do not mix both on one screen.
- Motion is short and functional. Honor `prefers-reduced-motion`.
- Do not clone Ant Design / Element in React. Those need a bundler.
  Approximate the language with the chosen HTML kit and tokens if the
  source is clearly that family.

Read `references/kits.md` before writing markup.
