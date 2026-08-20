# Kits and theme

Pick **exactly one** kit. Load it from a version-pinned CDN. Map every
color, radius, and font through the prototype tokens below so the page
stays one product.

Do not use React/Vue libraries (Ant Design, Element Plus, Naive UI, Arco,
TDesign React). They need a bundler. If the source looks like that family,
approximate with Bootstrap or Shoelace plus matching tokens.

Do not mix kits. Do not load Tailwind Play CDN for this skill.

## Tokens

Define once on `:root` (and `[data-theme="dark"]` only if dark is in
scope). Then point the kit variables at these names.

```css
:root {
  --proto-font: "Noto Sans SC", "PingFang SC", "Hiragino Sans GB",
    system-ui, sans-serif;
  --proto-font-mono: ui-monospace, SFMono-Regular, Menlo, monospace;
  --proto-bg: #f6f7f9;
  --proto-surface: #ffffff;
  --proto-text: #1b1d21;
  --proto-text-muted: #5c6370;
  --proto-border: #e6e8ec;
  --proto-primary: #2f6fed;
  --proto-primary-fg: #ffffff;
  --proto-primary-hover: #245dd1;
  --proto-accent: #eef3fe;
  --proto-danger: #c9372c;
  --proto-success: #1f8a4c;
  --proto-warning: #b76a00;
  --proto-radius: 10px;
  --proto-shadow: 0 1px 2px rgb(27 29 33 / 6%);
}
```

Replace the hex values with colors taken from the source. Keep primary
and primary-fg contrast strong. Muted text must still read on `surface`
and on `bg`.

Chinese UI: load Noto Sans SC from `fonts.googleapis.com` or
`fonts.bunny.net` unless the brand specifies a face. One display face
plus this body face is enough.

## Which kit

| Kit | Use when | Avoid when |
| --- | --- | --- |
| **Pico CSS 2** | Content sites, simple tools, forms, marketing, docs-driven flows with few widgets | Heavy app chrome (nested nav, data tables with bulk actions, drawers) |
| **Shoelace 2** | App prototype that needs dialog, drawer, tabs, dropdown, select, menu | The source is a classic Bootstrap/Ant admin and must look like one |
| **Bootstrap 5.3** | Admin / 后台, enterprise, the source already looks like Bootstrap | Consumer marketing that should not feel like a dashboard |

Default: **Pico** for linear products, **Shoelace** for multi-panel apps,
**Bootstrap** for 后台.

## Pico CSS 2

```html
<meta name="color-scheme" content="light">
<link rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/@picocss/pico@2.0.6/css/pico.min.css">
```

Override after the kit stylesheet:

```css
:root {
  --pico-font-family: var(--proto-font);
  --pico-background-color: var(--proto-bg);
  --pico-primary: var(--proto-primary);
  --pico-primary-background: var(--proto-primary);
  --pico-primary-inverse: var(--proto-primary-fg);
  --pico-primary-hover: var(--proto-primary-hover);
  --pico-border-radius: var(--proto-radius);
}
```

Prefer semantic HTML (`main`, `article`, `button`, `dialog`, `table`).
Use Pico's `container` / `grid` only when needed. Force light with
`color-scheme: light` unless dark is requested.

## Shoelace 2

Pin a 2.x release. Autoloader pulls only the components you use.

```html
<link rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.20.1/cdn/themes/light.css">
<script type="module"
  src="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.20.1/cdn/shoelace-autoloader.js">
</script>
```

Theme via `--sl-` tokens on `:root` (map from `--proto-*`). Use
`<sl-button>`, `<sl-dialog>`, `<sl-drawer>`, `<sl-tab-group>`,
`<sl-select>`, `<sl-input>`, `<sl-dropdown>`, `<sl-icon>`. Do not also
load another icon library.

Layout (sidebar, page header, content width) is your CSS. Shoelace does
not give you an app shell — keep that shell small and token-based.

## Bootstrap 5.3

```html
<link rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js">
</script>
```

Override `--bs-primary`, `--bs-primary-rgb`, `--bs-body-bg`,
`--bs-body-color`, `--bs-border-radius`, `--bs-font-sans-serif` from the
proto tokens. Set `--bs-primary-rgb` to the same color as a comma
triple so `btn-primary` and subtle backgrounds stay consistent.

Use Bootstrap icons only if you need them:

```html
<link rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css">
```

## Icons (Pico only)

Pico has no icon set. Load Lucide UMD and `createIcons`:

```html
<script src="https://unpkg.com/lucide@0.544.0"></script>
```

Keep icons 16–20px, `currentColor`, `aria-hidden` when decorative.

## In-page views

Default structure for a single-file prototype:

```html
<body>
  <div class="app">
    <nav><!-- primary destinations, data-go="list" --></nav>
    <section data-view="list">...</section>
    <section data-view="detail" hidden>...</section>
  </div>
  <script>
    function showView(name) {
      document.querySelectorAll("[data-view]").forEach((el) => {
        el.hidden = el.getAttribute("data-view") !== name;
      });
    }
    document.addEventListener("click", (e) => {
      const go = e.target.closest("[data-go]");
      if (!go) return;
      e.preventDefault();
      showView(go.getAttribute("data-go"));
    });
  </script>
</body>
```

Wire real controls to `data-go` or to small local-state handlers (add a
row, open a dialog, toggle empty state). The first view must be the
product home, not a kit demo.

## What not to load

- Random CSS from CodePen / uiverse as a base
- Multiple icon packs
- Google Fonts beyond one family
- Maps, charts, or 3D unless the product is about them
- Analytics, auth widgets, or live API keys
