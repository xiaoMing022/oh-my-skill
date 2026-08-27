---
name: design-unify
description: >
  Unify a frontend project's visual design system: inventory components,
  charts, styles, and motion libraries, confirm theme tokens (colors, type,
  density) with the user, then apply consistently. Large scopes go through a
  reviewed plan first. Use when the user wants 设计规范统一, 统一风格,
  统一主题, 主题色统一, 字体统一, design system unify, UI style unify, or
  runs /design-unify. Do not use for greenfield distinctive pages
  (frontend-design), 2-3 visual forks (visual-brainstorm), or clickable HTML
  prototypes (html-prototype).
metadata:
  short-description: "Unify project UI: inventory stack, confirm theme, plan if large, apply"
---

# Design Unify

Bring an existing frontend project onto **one** confirmed visual baseline —
theme colors, typography, density/tone, and the component / chart / motion
patterns it already uses — without inventing a new aesthetic.

Reload this skill before auditing or applying unify work.

## Neighbors

| Job | Skill |
| --- | --- |
| Unify style across the open project | this skill |
| Pick a new layout / tone with sketches | `visual-brainstorm` |
| Build a distinctive new page or UI | `frontend-design` |
| Clickable HTML prototype to save | `html-prototype` |

Hand off only when the user asks for those jobs. If they only want a written
spec and no code changes, stop after the confirmed baseline summary.

## Workflow

Follow these steps in order. Skip a step only when its answer is already in
the conversation. Do not edit product files before **Confirm baseline**
passes.

1. **Inventory** — read `references/inventory.md`. Discover the dominant
   component kit, styling system, theme/token source, fonts, chart library,
   motion approach, and density/tone. Note competing stacks. Stay inside the
   open project; do not tour unrelated repos.
2. **Confirm baseline** — present a short proposal in chat: recommended
   stack to keep, theme colors, typography, density/tone, and how charts /
   motion should align. Lead with one recommendation and a one-line why.
   Confirm forks one at a time when several matter (especially primary color,
   fonts, and overall tone). Prefer keeping the project's existing libraries
   over introducing new ones. Do not change files until they approve.
3. **Scope gate** — after approval, estimate blast radius against the
   confirmed baseline (tokens only vs shared components vs many feature
   pages). Then:
   - **Small** — a token/theme file plus a handful of call sites, or one
     surface family: implement in this skill.
   - **Large** — cross-cutting theme migration, many routes/components, or
     consolidating competing kits: enter plan mode (`enter_plan_mode`) and
     produce a concrete change plan for user review. If plan mode is
     unavailable, use the `design` skill (`/design`) the same way. Do not
     start broad edits until they approve the plan.
4. **Apply** — execute the approved baseline (or approved plan). Put tokens
   and shared primitives first, then shared components, then pages. Match
   existing code conventions. Do not redesign IA or invent new product UI
   while unifying.
5. **Check** — summarize what changed and what still drifts. If the app is
   runnable and browser tools are available, spot-check a few representative
   screens for token and component consistency. Fix clear regressions from
   this unify pass before finishing.

## Confirm baseline

Treat theme color, typography, and overall tone as blocking. Also confirm
when inventory finds forks in:

- Component kit (which one wins)
- Chart library / series colors
- Motion library vs CSS-only
- Light / dark / both

Skip re-asking what the user already settled in this conversation. If they
say 直接做 / 不用确认 / skip on a fork that does not change the baseline,
proceed with the recommendation.

When seeing competing themes would help more than reading hex values, use
`visual-brainstorm` for that fork only, then return here.

## Scope gate detail

**Small** examples: updating CSS variables in one theme file; aligning a few
buttons/cards to existing tokens; fixing one chart palette helper.

**Large** examples: migrating off a second UI kit; renaming or reshaping
tokens used across many packages; restyling most authenticated routes.

For large work, the plan must list: target baseline, files or areas in
order, risks (breaking visual regressions, dark mode), and how progress will
be verified. Wait for explicit plan approval before applying.

## Apply rules

- Source of truth is the **confirmed** baseline, not a newly invented brand.
- Prefer editing shared tokens and primitives so pages inherit consistency.
- Do not add a second component or chart library while unifying.
- Do not expand scope into features, copy rewrites, or layout experiments
  unless the user asked in the same request.
- Stay on the current branch and working tree; do not create branches or
  worktrees unless the user explicitly asks.

## Done

Finish with: the confirmed baseline (colors, type, density, stack), what was
changed, known remaining drift, and whether a follow-up pass is needed.
