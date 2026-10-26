# Charts

Read with `render-kit.md` when the visual is a chart, plot, dense categorical
grid, or part-to-whole / time allocation. Host, delivery, layout, color, and
utilities stay in `render-kit.md`. Map composition is in `maps.md`.

## Graphs and plots

- Use D3 for data-rich Cartesian or statistical plots and handwritten SVG for
  simple, directly labeled values. Keep diagrams, simulations, and maps under
  their existing guidance. Load the version-pinned approved-CDN script
  `https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js`.
- Render the figure, legend, and subplots directly on the transparent host
  surface. Frame only the SVG plot area; never wrap charts in `.card`, rounded
  panels, filled backgrounds, or shadowed containers.
- Give the figure a concise visible title. Render each Cartesian subplot in
  its own responsive SVG with a matching `viewBox`, a thin frame, and visible
  `text.axis-title[data-axis="x"]` and `text.axis-title[data-axis="y"]`
  showing quantities and units.
- Set each SVG `viewBox` from its own container's measured width, redraw with
  `ResizeObserver`, and reserve at least 64px for the y axis. Never scale down
  a fixed-width `viewBox`.
- Derive padded domains with `d3.extent(...)` over all observations,
  uncertainty, and references. Inset scale ranges for marker radii and keep
  every path inside `rect[data-chart-frame]`; never draw endpoint connectors
  outside the frame or guess or hard-code the domain.
- After every draw, measure tick, axis, and value-label bounds together.
  Leave 4px between labels, anchor edge labels inward, and remove optional
  annotations first. At 360px, show at most four x ticks and stack panels.
- Prefer `--viz-series-1` through `--viz-series-6` for chart series; use
  `--foreground` and `--border` for neutrals, cycle the six series tokens when
  more are needed, and never use literal or fallback colors. Give every SVG
  label `fill: var(--foreground)` and `font-size: 12px`; never shrink labels
  below 11 screen pixels. Stack subplots when their labels no longer fit.
- Keep observations, trends, and important values visible. Use bands for dense
  uncertainty, whiskers for isolated estimates, and one compact, wrapping
  legend. Render one real `<button type="button" aria-pressed="true">` per
  series with a small swatch and neutral text; toggle its line, markers, and
  tooltip row together. Keep buttons transparent, borderless, and
  indistinguishable from inline text; never use `.btn`, pills, badges,
  rounded borders, or filled and selected backgrounds.
- Share one root-relative, pointer-transparent
  `<div class="tooltip" role="tooltip">` using `--popover` and
  `--popover-foreground`. In each multi-series SVG, give the full-plot overlay
  both `data-chart-hit` and `data-chart-hover-overlay="cross-series"`. Keep
  the `data-chart-hover-guide` at the exact cursor x, interpolate every
  visible series there, and show one aligned `data-chart-hover-marker` and
  tooltip row per visible series; never snap the guide to a nearby sample.
- Find ordered observations with `d3.bisector(d => d.x).center(values, x)`;
  never pass an accessor to `d3.bisectCenter`.
- Give isolated marks transparent `data-chart-hit` targets at least 32 screen
  pixels across; use one nearest-point overlay for dense scatter.
- Author marks, tooltips, and theme colors so they read at 736px and stack
  cleanly toward 360px (1,024px only in wide mode).
- For named numeric data and one-off analyses, start with the plot. Put values
  and takeaways on its marks, axes, or annotations. Never add a KPI row,
  controls, cards, or panels unless those UI elements are explicitly requested.
- For sequences or parallel work, use aligned lanes on one time axis. Encode
  phase and resource in the marks; annotate totals, waits, and bottlenecks on
  the axis or lanes, not above the plot.
- For distributions or multi-metric comparisons, use shared-scale facets or
  small multiples. Render every requested dimension simultaneously; never hide
  one behind a toggle.

## Dense categorical grid

- Use one compact horizontal selected-item summary, then a grid with exactly one
  readable identifier per cell, then one small legend. Render only that
  identifier as visible cell text; put all other metadata in an accessible label
  or one summary line, not badges or fact grids. Allow only selection unless
  asked.

## Part-to-whole or time allocation

- Use compact metrics and one stacked chart of category allocation per period.
  Never substitute totals-only bars or duplicate it as a heatmap and totals
  chart.

## Chart craft

- Prefer inline SVG for simple charts and version-pinned approved-CDN
  libraries when native interaction, scales, legends, or layout materially
  improve the result.
- Resolve theme colors before passing them to canvas or chart APIs that cannot
  parse CSS variables or `light-dark(...)`; redraw when the theme changes.
- Use a tooltip unless it would distract from a simple, directly labeled chart.
  Keep chart-library tooltips and grouped legend interactions native; never
  replace them with a custom one-point tooltip. For SVG, attach `data-tooltip`
  directly to the real pointer-accessible mark and include its label, value,
  and units; the kit handles themed positioning and keyboard focus.
- Animate transitions between chart states so lines and marks move to their new
  values, resampling paths when point counts differ. Do not animate initial
  appearance or use fade-only effects; never loop motion, and honor
  `prefers-reduced-motion`.
- Scope SVG styles to the chart class. Never target every `svg` in a container
  that also contains Lucide icons.
- Include labeled axes, units, and directly labeled important values. Give every
  chart, SVG, canvas, and widget a concise screen-reader summary using a role and
  accessible name or description, SVG `<title>`/`<desc>`, fallback text, or an
  `.sr-only` heading or description.
- Reserve space for the longest formatted label at every supported width. Axis
  ticks are secondary and may use `.text-small` when space is tight. Never
  overlap or clip text against marks, axes, legends, labels, or edges; move or
  reduce labels rather than squeeze them.
- Add a legend only when multiple series cannot be labeled directly.
- Pair color with shape or text so meaning never depends on color alone.
