# Render kit

How to write and serve a preview. Read this before creating or updating a
visual. Session flow, what to ask in text, and when to stop live in
`SKILL.md` — do not restate them here. Chart / plot / grid composition is in
`charts.md`; map composition is in `maps.md` — read those only when needed.

Skill directory: the folder that contains `SKILL.md` (parent of `references/`).

## Host and Environment

Preview is served on a **local HTTP port** so the user can interactively
view it. Do not link or ask the user to open a raw filesystem `.html`
path as the primary visual.

Working root: `<project-root>/.oh-my-skills/visualization/`, one directory per
session (see `session.md`). These are reviewable session artifacts that
may be committed: `session.md`, `checkpoints.json`, `checkpoints/`,
`revisions/`. Never commit `serve.json`.

## HTML output contract

### Session files

Create a session with the bundled helper (replace `<skill-dir>` with the
actual skill directory; run from the project root; quote real paths):

```bash
python3 <skill-dir>/scripts/session.py init <ascii-hyphenated-title>
```

Read the returned session path and save it in conversation state. Use
that exact directory on later turns; do not run `init` for each
checkpoint. Layout:

- `session.md`: decision plan, evidence, pending question, next actions;
  follow `session.md` in this references directory.
- `checkpoints.json`: manifest owned by the helper (checkpoint IDs,
  titles, statuses). Maintain it only through `publish` and `mark`.
- `index.html`: static session page linking every checkpoint, served as
  `/` — one stable URL across publications. Regenerated on every
  `publish` / `mark`.
- `checkpoints/<id>.html`: the current full standalone document per
  checkpoint (frame + content). Served as `/checkpoints/<id>.html`.
- `checkpoints/<id>.fragment.html`: the current source behind each page.
- `draft.fragment.html`: editable candidate, never served directly.
- `revisions/<checkpoint>-<n>.html`: immutable framed snapshots
  (`D2-01`, `D2-02`, …). Reference these in `session.md`.
- `revisions/<checkpoint>-<n>.fragment.html`: matching source snapshots.
- `serve.json`: temporary serve metadata (`url`, `port`, `pid`, `root`).
  Ephemeral — never commit, never treat as decision history.

Publish the draft to the checkpoint it answers, with a short human label:

```bash
python3 <skill-dir>/scripts/session.py publish <session-dir> <session-dir>/draft.fragment.html \
  --checkpoint D2 --title <short-label>
```

The helper checks UTF-8, nonempty fragment format, and size, wraps the
fragment in the fixed frame (`assets/frame.html` + kit CSS/JS), saves an
immutable revision, and atomically replaces that checkpoint's page.
These checks do not prove that layout or JavaScript works; inspect the
result too. Record the returned revision label (for example `R2`) in
`session.md` before asking for a selection. A publication sets the
status to `waiting` unless `--status` overrides it. When the user
confirms or defers a decision, sync the badge (which regenerates
`index.html`):

```bash
python3 <skill-dir>/scripts/session.py mark <session-dir> D2 confirmed
```

To revisit an older revision, publish that snapshot's fragment to its
checkpoint again and record the reason. Never edit saved revisions in
place. One agent writes a session at a time; independent conversations
use separate sessions.

List sessions when resuming:

```bash
python3 <skill-dir>/scripts/session.py list
```

Manual cleanup only — never automatic:

```bash
python3 <skill-dir>/scripts/session.py prune <session-dir> --force
python3 <skill-dir>/scripts/session.py prune --older-than 30 --force
```

Without `--force` the command only lists candidates. Do not bulk-delete
old sessions as routine cleanup.

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
- Serve the session directory on a local port with the host's
  background-process mechanism so it stays alive across turns (this
  command stays running):

  ```bash
  python3 <skill-dir>/scripts/serve.py --root <session-dir> --port 0 \
    --info <session-dir>/serve.json
  ```

  Read the printed URL, then verify with an HTTP GET of `/` and the
  current checkpoint page before sharing it. Check that the checkpoint
  and revision match the pending question. On first start, open the URL
  with an available browser mechanism. After republishing, the user
  refreshes the page — there is no live push. Never restart the server
  per checkpoint, and never claim the user can access a port based only
  on having written a file.
- To stop serving, stop the managed background process. Keep all source
  and decision files. Do not accumulate one server per checkpoint.
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

Every checkpoint page is already a standalone document (frame + content
inlined). Export is a plain copy:

```bash
cp .oh-my-skills/visualization/<slug>/checkpoints/<checkpoint-id>.html <destination>.html
```

Exports cannot replace the source. For a general website request, build
a new responsive site in the open project without this skill's guidance.

## Composition

Choose the smallest composition that fits.

- Prefer interaction detail over permanent panels, toolbars, repeated legends,
  or long stacks. Add only requested controls, use one mechanism per state, and
  never invent search, filter, or reset controls.
- Keep filters, selections, and other presentation-only interactions local.
  On-page buttons are visual only and report nothing to the agent; if a
  selected value needs investigation, the user will say so in chat.
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
- Make each option a native labeled `button` with `data-choice` and
  `aria-pressed` for local visual feedback. Clicks confirm nothing; the
  user confirms in chat. Do not add any reporting call to the fragment —
  the frame footer already says confirmation happens in dialogue.
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

### Scheme, flow, and timeline comparisons

- Compare schemes the same way as UI options: A/B/C labels, one tradeoff
  each, one recommendation. Keep each scheme schematic — nodes, edges, and
  stage labels — not production architecture diagrams.
- For flows, show the happy path plus the one branch that matters. For
  timelines, show milestones and dependencies, not a full project plan.
- A static node/edge explanation that needs no comparison can stay a
  Mermaid diagram in chat without a server.

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
