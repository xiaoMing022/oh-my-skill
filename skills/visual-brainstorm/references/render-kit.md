# Render kit

How to write and serve a preview. Read this before creating or updating a
visual. Session flow, what to ask in text, and when to stop live in
`SKILL.md` — do not restate them here. Chart / plot / grid composition is in
`charts.md`; map composition is in `maps.md` — read those only when needed.

Skill directory: the folder that contains `SKILL.md` (parent of `references/`).

## Host and Environment

Preview is served on a **local HTTP port** so the user can interactively view and test it. Do not link or ask the user to open a raw filesystem `.html` path as the primary visual.

Working root: `~/.agent-skills/visualizations/`, or the expanded
`AGENT_VISUALIZATIONS_DIR` when set. Keep scratch files outside the user's git
working tree. Use a unique directory per task, not a shared title-based file.

## HTML output contract

### Session files

Create a session with the bundled helper (replace `<skill-dir>` with the
actual skill directory; quote real paths in commands):

```bash
python3 <skill-dir>/scripts/session.py init <ascii-hyphenated-title>
```

Read the returned absolute session path and save it in conversation state.
Use that exact directory on later turns; do not run `init` for each checkpoint.
Keep these files there:

- `session.md`: decision plan, evidence, pending question, and next actions;
  follow `session.md` in this references directory.
- `checkpoints.json`: tab manifest owned by the helper (checkpoint IDs, tab
  labels, statuses). Maintain it only through `publish` and `mark`.
- `checkpoints/<id>.fragment.html`: the current source behind each tab.
- `draft.fragment.html`: editable candidate, never served directly.
- `revisions/<checkpoint>-<id>.fragment.html`: source snapshots created by
  publication.
- `choices.json`: latest on-page selection per checkpoint, written by the
  preview server. Preview feedback only — never confirmation evidence. Read it
  when the user's chat reply references their on-page pick (for example
  "就按我页面上点的"); the decision still needs that chat reply.
- `serve.json`: temporary ownership/connection metadata, not decision history.

The preview page is one fixed shell with a tab per checkpoint. Publishing a
checkpoint updates only its own tab; every earlier checkpoint stays viewable
on the same URL. Write the draft as a literal file, then publish it to the
checkpoint it answers, with a short human tab label:

```bash
python3 <skill-dir>/scripts/session.py publish <session-dir> <session-dir>/draft.fragment.html \
  --checkpoint D2 --title <short-label>
```

The helper checks UTF-8, nonempty fragment format, size, and renderability,
then saves a revision and atomically replaces that checkpoint's fragment. These
checks do not prove that layout or JavaScript works; inspect the result too.
Record the returned revision in `session.md` before asking for a selection.
A publication sets the tab status to `waiting` unless `--status` overrides it.
When the user confirms or defers a decision, sync the tab badge:

```bash
python3 <skill-dir>/scripts/session.py mark <session-dir> D2 confirmed
```

To revisit an older revision, publish that snapshot to its checkpoint again and
record the reason. Never edit saved revisions in place. One agent writes a
session at a time; independent conversations use separate sessions.

### Fragment

- Write only an HTML fragment: no `<!doctype>`, `<html>`, `<head>`, or `<body>`.
- Write literal markup: use `<div class="card">Hi</div>` plus a real newline,
  never `<div class=\"card\">Hi</div>\n`. Never embed the fragment in an inline
  Python, JavaScript, or shell string. Read it back; rewrite literal `\"` or
  `\n`.
- Keep CSS and JavaScript in the fragment only when base classes are
  insufficient. Load static resources only from the CDN allowlist. Never use
  `fetch`, XHR, WebSocket, or other API calls.
- Give the fragment root a unique ID and select it with
  `document.getElementById(...)`. Never derive the root from
  `document.currentScript`; scripts may sit outside the root.
- Keep visualizations under 1 MB. Aggregate, bin, downsample, reduce precision,
  or drop unused fields from large inline datasets.
- Check that JavaScript has no undefined identifiers, every queried element
  exists, and the primary interaction updates the visual.

### Delivery

- Keep the fragment focused on the visualization. Do not include explanatory
  paragraphs, formulas, instructions, or narrative callouts. Include only
  necessary labels, legends, values, and accessible text alternatives.
- Serve on a local port. Never treat a saved `.html` file as the preview.
  The server serves the whole session directory: a fixed page with a tab bar
  (checkpoint ID, label, status badge) and one sandboxed frame per checkpoint,
  loaded on demand from `/checkpoint/<id>`. The page polls `/__version` and
  syncs incrementally — a new checkpoint's tab appears and activates, a
  republished checkpoint reloads only its own frame, and status badges update
  in place — without a full page reload, so the user's state in other tabs is
  preserved. On-page option clicks are recorded to `choices.json` via
  `/__choice` as preview feedback. Never restart the server per checkpoint.

  Check an existing server by identity, not just PID existence:

  ```bash
  python3 <skill-dir>/scripts/render.py <session-dir> \
    --status --info <session-dir>/serve.json
  ```

  A successful check means this port belongs to this session and instance.
  Reuse its URL; an open page syncs itself after publication. Metadata from
  older skill versions without an identity token is not reusable. Never kill a
  PID read from JSON.

  If no info file exists, start with the host's background-process mechanism
  so the process can remain alive across turns (this command stays running):

  ```bash
  python3 <skill-dir>/scripts/render.py <session-dir> \
    --serve --info <session-dir>/serve.json --title <task-title>
  ```

  If startup is still in progress, allow it to finish before checking again.
  If an existing info file fails identity verification, retry once after a
  short delay. Preserve it under a unique `serve.stale-<id>.json` name before
  restarting. If another agent/process owns an active startup, do not rename
  its metadata or start another server. Never overwrite another session's files.
  For legacy processes without identity metadata, use only a known host process
  handle to stop them; otherwise leave them alone and create a new session.

  Read the printed URL, verify `--status` and an HTTP GET of the preview before
  sharing it. Check that the active tab's checkpoint and revision match the
  pending question. On first start, open the URL with an available browser
  mechanism; on subsequent turns the same open page auto-refreshes. If no
  browser inspection tool is available, report that limitation. Check the primary interaction and target
  and narrow layouts when browser tools are available. Never claim the user
  can access a port based only on having written a file.

  A server exits after 30 minutes without a successful preview GET (configurable
  with positive `--idle-timeout` seconds). Status and `/__version` probes do not
  extend its life; an expired page shows a stopped-preview notice. Reopen the
  same session after expiry; record the new URL. For explicit stop:

  ```bash
  python3 <skill-dir>/scripts/render.py <session-dir> \
    --stop --info <session-dir>/serve.json
  ```

  Stop verifies an instance token and never signals an arbitrary PID. Wait for
  the managed process to exit or its owned info file to disappear. Normal stop,
  idle expiry, SIGINT, and SIGTERM release the socket and owned metadata. A hard
  crash may leave stale metadata; use the recovery procedure above. Keep source
  and decision files on stop. Do not accumulate one server per checkpoint.
- Widen only when several compact option or chart panels must remain side by
  side for direct comparison. Never widen a single plot, map, grid, diagram,
  timeline, or full-size mockup; stack them vertically instead.
- When awaiting a visual decision, include the preview URL, what to compare,
  and one choice question. Pause, completion, handoff, and plain explainers do
  not require another choice question. Do not dump a Markdown table or repeat
  the visual's data. Do not use a raw file path as the live preview.

### External resources

- Allowed origins: `cdnjs.cloudflare.com`, `esm.sh`, `cdn.jsdelivr.net`,
  `unpkg.com`, `fonts.googleapis.com`, `fonts.gstatic.com`, and
  `fonts.bunny.net`. Other origins fail silently under the kit CSP.

## Exporting an existing visualization

- Keep the fragment as the editable source. The live preview is the port, not
  an exported file. When the user explicitly asks to save or export what is
  already shown, then render a standalone document:

  ```bash
  python3 <skill-dir>/scripts/render.py \
    <session-dir>/checkpoints/<checkpoint-id>.fragment.html \
    <destination>.html
  ```

  Passing the session directory instead of one fragment exports the whole
  tabbed document. Exports are offline self-contained snapshots: every
  checkpoint is inlined and no live polling or choice reporting is included.

- Exports cannot replace the source. Existing destinations require an intended
  replacement with `--force`; otherwise choose a new path. Rendering embeds the
  source and base CSS, but optional CDN libraries still need network access; do
  not promise offline functionality without checking it.
- Apply this export flow only when they ask to save the existing preview as
  a file. For a general website request, build a new responsive
  site in the open project without this skill's guidance.

## Composition

Choose the smallest composition that fits.

- Prefer interaction detail over permanent panels, toolbars, repeated legends,
  or long stacks. Add only requested controls, use one mechanism per state, and
  never invent search, filter, or reset controls.
- Keep filters, selections, and other presentation-only interactions local.
  Do not add custom buttons that message the agent; the only reporting channel
  is the built-in `data-choice` recording to `choices.json`, and it is preview
  feedback, not a request. If a selected value needs investigation, the user
  will ask in chat.
- Show only metrics that explain the requested behavior. Put live values in
  control headers or on the visual before cards. Treat maxima as ceilings, not
  targets. Never invent qualitative scores, status cards, or secondary fact
  grids to fill space.

### UI mockups and design options

How to draw the options. When to show them, how many, and when to stop
are in `SKILL.md`.

- Label options A/B/C (or short names). Stay at **reference fidelity**:
  layout, hierarchy, key regions, representative copy, and a hint of tone.
  Grey or labeled blocks are enough for secondary areas. Do not design every
  control, empty state, icon, or dashboard widget; depict a critical state when
  that state is the current planned decision. Do not invent a complete
  design system. Raise fidelity only enough to answer a planned refinement
  or integrated review.
- Make each option selectable (a native labeled `button` with
  `data-choice` and `aria-pressed`). A selection gives local visual feedback
  and is recorded to the session's `choices.json` as preview feedback; the
  user still confirms in chat. The host injects a confirm-in-chat hint when
  `[data-choice]` is present; do not duplicate that hint in the fragment.
- The visualization is the preview, not a widget inside the depicted product.
- Use product and platform context already in the conversation. Read the
  project only as far as the current visual question needs matching chrome.
  If its design is unavailable, infer a light sketch from the platform.
- NEVER use visualization CSS variables or utility classes inside a mockup
  (for example, `--card`, `--font-size-base`, `.card`, or `.btn`). Option
  frames around the mockups may use those utilities; the depicted product may
  not. Define root-scoped, product-specific colors and type inside the mockup.
  This rule overrides all general visualization guidance.
- Keep only the surrounding surface transparent. Give product windows, cards,
  menus, and popovers opaque backgrounds, and stack overlays above the product
  content.
- Follow the host's active appearance with product-specific
  `light-dark(<light>, <dark>)` colors unless a fixed theme is requested.
- **Contained mockup:** Frame a component, dialog, small feature, or mobile
  screen as a compact product surface inside an option.
- **Full-page mockup:** Use only after the user has chosen a direction, or when
  comparing 2 page-level layouts; still keep them sketchy, not production UI.
- Put app-wide navigation and pickers in the app chrome, and local controls in
  their component. Omit single-option pickers. Show realistic structure, not
  invented dashboards, filler cards, or oversized icons.

### Interactive explainer or simulation

- Use compact controls or status, one compact dominant visual, and at most one
  single-line selected-state detail. Default to no summary cards; allow up to
  three only when changing metrics are central.
- Crop empty space and fit the available width. For step-throughs, add only
  requested step controls and update one current visual; never add parameter
  controls, formulas, metric cards, or side-by-side steps unless asked.

### Charts, plots, grids, and maps

- Charts, plots, dense categorical grids, and allocations: `charts.md`.
- Maps: `maps.md`.

## Layout and accessibility

- Use semantic HTML, keyboard-accessible controls, and concise labels.
- Keep the top-level surface transparent and unframed, and fill the available
  width. Design for 736px, or 1,024px in wide mode, and support widths down to
  320px. Stack side-by-side content when it no longer fits.
- At every supported width, text, controls, cards, toolbars, and dynamic content
  must fit without overlap or clipping. Reflow by stacking or wrapping; use
  `.table-responsive` only when table columns cannot fit. Avoid fixed outer
  widths, other horizontal overflow, internal scrolling, `position: fixed`,
  and viewport-height layouts.
- Size every SVG from its actual container. At narrow widths, reduce ticks,
  declutter annotations, and keep visible text at least 11 screen pixels;
  never shrink a fixed-width `viewBox`.
- Keep native tab order; never add `tabindex`.
- Use native `button`, `input`, `select`, and `textarea` elements with matching
  utilities; never recreate controls.
- Keep browser or utility focus styles; never override them.

## Typography

- Scale type with `--font-size-base`. Use normal text by default and
  `.text-small` only for secondary annotations (never below 11px).
- `h1`, `h2`, and `h3` are available; use one concise visible heading for a
  self-contained chart or graph, with short panel headings only when needed.
  Do not restate the prompt or add a redundant title to other visualizations.
- Use only weights `400` and `500`. Never set custom font sizes or line heights.

## Color

- Make every fill, stroke, text, border, shadow, chart, and canvas color
  theme-aware. Never hardcode light or dark palettes such as white panels,
  off-white backgrounds, black text, slate strokes, or Tailwind color literals.
- Keep text readable against its actual background. Muted or secondary colors
  must retain clear contrast; never use `.text-muted` inside `.card` or another
  filled container unless its background preserves that contrast.
- Available theme variables include `--background`, `--foreground`, `--card`,
  `--card-foreground`, `--popover`, `--popover-foreground`, `--primary`,
  `--primary-foreground`, `--secondary`, `--secondary-foreground`, `--muted`,
  `--muted-foreground`, `--accent`, `--accent-foreground`, `--destructive`,
  `--border`, `--input`, `--ring`, `--blue`, `--orange`, `--green`, `--red`,
  `--purple`, and `--yellow`. Use `currentColor` inside SVG.
- Use `--viz-series-1` for one measure or active state. Use `--viz-series-2`
  through `--viz-series-6` only for important persistent category, series, or
  status identity; never give every peer a different color by default.
  - For categorical tiles or nodes, prefer a soft low-opacity series fill with a
    neutral or transparent border; never color every outline.
  - Keep mappings stable and pair color with labels, shapes, or line styles.
  - Secondary series colors are theme-derived; never assume hues or use them
    decoratively.
- When color encodes a category or series, apply it consistently to the
  corresponding visual marks—not just the legend—and keep large-area fills
  subtle.
- Use series colors only for chart lines, marks, and legend swatches. Keep
  values, axis text, and direct labels in `--foreground` or
  `--muted-foreground`.
- Keep chart grids and inactive structure thin and neutral. Use 1-2px neutral
  structural paths; never thicken, dash, or double-stroke the whole structure.
- In each color pair, the base token is a surface and its
  `-foreground` token is the content on that surface. Use `.btn-primary` for
  high-emphasis actions; its neutral fill is supplied by the utility. Use
  `--primary` and `--primary-foreground` for filled selected, active, or pressed
  controls. Reserve `--accent` and `--accent-foreground` for subtle interactive
  surfaces and soft highlights. Buttons with
  `aria-pressed="true"`, `aria-selected="true"`, or `.is-selected` already use
  the primary pairing.

## Design system

- Let utilities own geometry, appearance, and interaction. Use the matching
  utility for every button and form control. Never restyle utilities,
  descendants, or pseudo-elements: no custom sizes, spacing, borders, radii,
  shadows, colors, or interaction states.

### Surfaces and layout

- `.card`: The only card-like HTML surface. Use its base class unchanged for a
  necessary numeric summary, selected-item summary, or bounded interactive
  field. Before adding a fill, border, radius, or shadow to any layout container,
  either use `.card` or leave it transparent and unframed; never recreate card
  chrome on rows, panels, tiles, sections, or wrappers. Keep charts, maps,
  diagrams, tables, controls, and the whole visualization unframed. Never nest
  cards; show 2-4 summaries near the top only when useful. Structural groupings
  and repeated content are not bounded interactive fields. Organize them with
  layout or visual marks, not container chrome.
- `.viz-stat`: Use a summary `.card` with one muted label, one
  `.viz-stat-value`, and at most one short context or delta line.
- `.viz-grid`: Use for peer metrics or choices instead of a custom grid. It
  creates as many equal-width columns as fit and stacks when narrow. Never use it
  for the whole visual or a horizontally scrolling card row. Keep groups to 2-3
  columns at 736px and controls in a separate row.
- `.viz-row`: Use as a wrapping horizontal group with centered related values or
  inline actions that may wrap when narrow.
- `.viz-tile`: Add to a selectable dense-grid `.btn`; it stretches to fill its
  grid cell, preserves category fill, and uses an accent ring instead of solid
  selection. Never add another selected, pressed, border, outline, or shadow
  rule.
- `.viz-badge`: Use as a compact display-only accent pill for a short status,
  category, or value; never as a button.
- `.viz-controls`: Use as a wrapping row for controls affecting the same
  visualization. Keep button groups compact. Put labeled fields directly inside
  as `.form-label`; fields form at most two columns and stack when narrow.

### Controls

- `.btn`: Use for a content-sized secondary action. Add `.btn-primary` for one
  main action per control group or `.btn-ghost` for low emphasis.
- `.btn-block`: Add to a `.btn` only when the action should intentionally fill
  the available inline space. Never use it for ordinary row actions.
- `<a>`: Use for links. Add `.btn` to style a link as a button.
- `[data-tooltip]`: Use for concise supplementary plain text on static or dynamic
  triggers; the kit creates `.tooltip` elements. Keep essential content
  visible and triggers labeled. Never use `title`, custom markup, or
  initialization. Example:
  `<button type="button" data-tooltip="Reset view">Reset</button>`.
- `[data-tooltip-placement]`: Optionally prefer `top` (default), `right`,
  `bottom`, or `left`; collision handling may flip it.
- `.form-check`: Wrap a native checkbox or radio; pair `.form-check-input` and
  `.form-check-label` with matching `id` and `for`.
- `.form-switch`: Add to `.form-check` around a native checkbox.
- `.form-control`: Pair a native text, file, or color input—or a textarea—with
  `.form-label`.
- `.form-control-color`: Add to `.form-control` for a compact native color
  input.
- `.form-select`: Pair a native select with `.form-label`.
- `.form-range`: Pair a native range with a visible label; put its current value
  and units immediately before it.

### Tables

- `.table`: Use on a semantic table for a quiet, unframed data view. It provides
  wrapping cells and subtle horizontal dividers without vertical gridlines. Use
  sentence case for headers.
- `.table-responsive`: Wrap a table when its columns cannot fit at narrow
  widths. It contains horizontal overflow without clipping the visualization.
- `.table-sm`: Add to `.table` when more rows need to fit; it reduces cell
  padding without shrinking text.
- `.text-end`, `.text-center`, and `.text-nowrap`: Use inside `.table` for
  numeric/end alignment, centered values, or values that must stay on one line.
  Numeric cells use tabular figures when end-aligned.

### Text

- `.text-small`: Use for the smallest host-scaled secondary chart labels and
  annotations, never below 11px or for essential content.
- `.text-muted`: Use for secondary units, captions, timestamps, and context,
  never essential values or labels.
- `.text-destructive`: Use only for error or validation text the user needs to
  notice or act on.
- `<code>`: Use for inline commands, file names, symbols, or short references;
  put multiline code in `<pre><code>`.
- `.sr-only`: Use for visually hidden accessible text.

## Icons and mockups

- The render kit loads Lucide. Add an icon name with `data-lucide`:

  ```html
  <i data-lucide="search" aria-hidden="true"></i>
  ```

- Lucide replaces the placeholder in place with an inline SVG. Icons are 16px
  and inherit `currentColor`.
- Mark decorative icons `aria-hidden="true"`. Put action icons inside labeled
  controls; use a visible label or `aria-label` for icon-only actions.
- After adding icons dynamically, use
  `lucide.createIcons({ attrs: { width: 16, height: 16 } })`.
- Never load Lucide or another icon library from the fragment.
- Use visibly labeled buttons and inputs for small interactions. Keep all
  presentation-only interaction local to the fragment and make the first render
  useful before input changes.
- Use semantic controls, realistic spacing, and restrained chrome for mockups.
  Never fake product screenshots when inspectable UI is needed.
