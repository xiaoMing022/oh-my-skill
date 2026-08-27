# Inventory

How to discover what the open project already uses. Read this during the
**Inventory** step. Do not invent a new stack when an existing one is clear.

## Where to look

Read only as far as needed to answer the checklist. Prefer manifests and
shared theme entry points over touring every page.

- Package manifests: `package.json`, workspace package manifests, lockfiles
- App shells / providers: root layout, theme providers, `ThemeProvider`, CSS
  variable roots
- Token / theme files: `globals.css`, `theme.*`, `tokens.*`, Tailwind config,
  CSS-variable maps, design-token JSON
- Component entry points: `components/ui`, design-system packages, Storybook
- Chart / map / motion imports across a sample of feature pages

## Checklist

Record what is **dominant** (most screens) vs **exception** (one-off).

| Area | Capture |
| --- | --- |
| UI components | Library or in-house kit (e.g. shadcn, Ant Design, MUI, custom). Key primitives in use. |
| Styling | Tailwind, CSS Modules, styled-components, vanilla CSS, utility layers. Token source of truth. |
| Theme | Light/dark support. Primary / accent / semantic colors. Radius and spacing scale if present. |
| Typography | Font families, weights, size scale, where loaded (Google Fonts, self-host, system). |
| Charts | Library (ECharts, Recharts, Chart.js, D3, etc.) and shared palette / tooltip patterns. |
| Motion | CSS transitions, Framer Motion / Motion, Lottie, library defaults. Reduced-motion handling. |
| Icons | Icon set and sizing conventions. |
| Density / tone | Compact tool UI vs marketing openness; flat vs elevated surfaces. |

## Competing sources

If the repo has **more than one** theme, component kit, or chart library in
active use, list each with where it appears. Recommend consolidating on the
dominant one unless the user already named a target.

## Output shape

Keep the inventory short enough to paste into chat as the confirmation
proposal: stack summary, recommended baseline (colors, type, density), and
open forks that need a user choice.
