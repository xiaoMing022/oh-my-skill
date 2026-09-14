---
name: my-designer
description: >
  Design and implement frontend pages, components, and applications with one
  coherent project design system. Use for new UI, adding pages to an existing
  app, frontend design, 前端设计, 页面设计, or styling a feature. Reuse the
  project's visual baseline; when none exists, confirm a theme visually with
  visual-brainstorm before building. For project-wide style migration use
  design-unify; for standalone clickable HTML prototypes use html-prototype.
metadata:
  short-description: "Build coherent frontend UI from a confirmed project design system"
---

# Frontend Design

Build working interfaces whose pages, components, content hierarchy, and states
belong to the same product. Make deliberate aesthetic choices appropriate to
its audience; carry those choices across subsequent work. Distinctiveness can
come from precise typography, composition, and interaction, not necessarily
unusual fonts, decorative effects, or a new palette on every page.

This is the project's implementation skill. Use the supplied requirements,
existing code, and confirmed visual decisions together. Do not call this skill
recursively. In hosts with namespaced skills, prefer this package's sibling
skills for handoffs.

## Establish the baseline

Before styling, inspect the target app's entry point, theme/provider, shared
components, styling configuration, and one or two representative screens.
Read only enough to locate the actual design authority and import path.
No `globals.css` does **not** mean no design system: a component-library theme,
CSS Modules, utility configuration, shared package, or provider can own it.
Distinguish a placeholder starter theme from an intentional, repeatedly used
baseline. Follow app boundaries in monorepos; neighboring products may have
intentionally different brands.

Read [references/design-context.md](references/design-context.md) for durable
records, source precedence, and where styles belong. Decide which case applies:

| Situation | Action |
| --- | --- |
| Coherent project baseline or already confirmed theme | Reuse it; briefly name the source and relevant rules, then build. Do not ask for the same theme again. |
| New project, starter-only styles, or no usable baseline | Ask about unresolved purpose/brand preferences, then use the theme confirmation below. |
| Mixed styles in a bounded feature task | Use that app's intended shared system; fix local inconsistencies without migrating the whole project. Clarify only if choosing the authority materially changes the result. |
| User requests a broad rebrand or cross-project style cleanup | Use `design-unify` for the migration if available, passing existing confirmations and scope. |
| Request is architecture or an implementation-approach fork | Use `figure-out` if available; resume UI work after that direction is confirmed. |
| Request is what existing code does for a click, request, or function | Use `code-chain` if available; do not turn an explanation into a restyle. |
| Request is only visual exploration or a standalone prototype | Use `visual-brainstorm` or `html-prototype`; do not turn it into product implementation. |

## Confirm a missing theme once

1. Reuse known audience, purpose, brand assets, accessibility needs, density,
   light/dark scope, and examples. If preferences are missing, actively ask one
   concise question such as “有必须沿用的品牌风格，还是希望我给出几种方向？”
   Use a question tool if available, otherwise chat. Do not interrogate users
   about individual hex values, radii, or font weights.
2. When enough context is known, call `visual-brainstorm` for **one theme fork**:
   2-3 distinct but suitable style directions on the same representative
   content, layout, and viewport. Compare typography, surfaces, palette,
   density, and the treatment of primary actions together. Show real UI
   samples, not mood adjectives or color swatches alone. State a recommendation
   and tradeoff. The preview and its decision record stay outside the project.
3. Tell the visual skill its scope is a theme fork and the caller will resume
   implementation. A clear user selection completes theme confirmation; do
   not expand it into a full product discovery or repeat an integrated theme
   approval. A mixed/rejected choice remains unresolved: refine that fork
   using its bounded iteration rules, not a new set of unrelated themes.
4. Capture the selected option meaning, revision, evidence, and design rules.
   Translate the selected theme into the project's native token/component
   system, then continue the already requested build in the same turn.
   Do not copy preview host CSS, iframe wrappers, or sandbox behavior into the
   product. A sketch expresses intent, not production architecture.

If the user already supplies a precise style or explicitly delegates the
choice (“按你推荐的直接做 / 不用确认”), proceed with that direction and record
it as supplied or delegated, not as a visual choice they never made. If the
visual skill is unavailable, use an available browser/preview mechanism for
the same scoped comparison. If no visual delivery is possible, explain the
limitation and ask for a supplied direction or permission to use your default;
do not claim that text choices are a visually confirmed theme.

While a required answer is pending, continue independent inspection/planning
but do not commit a speculative theme into the product. Pause with the exact
pending question; silence and preview clicks are not confirmations.

## Define the design contract

Keep a concise, project-specific contract in the existing design documentation,
or an external working record when the project has none. Write only decisions
that guide implementation; a small component does not require a full catalog.

- Purpose and visual thesis: a sentence connecting the audience's task with
  the design approach, plus a few stable principles (for example, prioritize
  queue scanning, keep actions predictable, reserve emphasis for exceptions).
- Foundations: semantic colors and surface/text pairs, type hierarchy and
  fallback fonts, spacing/density, content widths, radii, borders, elevation.
- Component grammar: one source for each shared primitive and consistent
  variants, sizes, icon treatment, form feedback, navigation, and overlays.
- Behavior: responsive reflow, relevant interaction states, focus treatment,
  theme modes, motion intent, and reduced-motion behavior.
- Authority: actual runtime source paths and scope, confirmed decision evidence,
  approved exceptions, and anything still assumed or deferred.

Rules describe relationships, not a compulsory visual recipe. Reuse existing
names and scales. Avoid a universal palette, mandatory gradient, arbitrary
ban on system fonts, or the assumption that every app needs dark mode.
Consult [references/implementation.md](references/implementation.md) when
mapping the contract into code and checking the resulting UI.

## Implement coherently

1. Give a short implementation plan proportional to the task: foundations or
   token extension, shared primitives, target screens, important states, then
   verification. Build within the authorized scope; the plan itself is not an
   additional approval gate.
2. Start with existing tokens and shared components. For a new baseline, wire
   the smallest native theme source into the actual app entry point. A cache
   outside the repo must never become a runtime stylesheet dependency.
3. Build one representative slice, including its important states, to verify
   the design rules before replicating across pages. This is an implementation
   check, not a mandatory second user confirmation of the theme.
4. Apply the same contract throughout the requested surfaces. Extend semantic
   roles/variants centrally when needed; avoid page-local replacements for
   shared buttons, spacing scales, or typography. A new page may have a
   different layout while still using the same design language.
5. Keep real behavior intact: navigation, forms, validation, loading and failure
   states. Do not invent metrics or active-looking controls that silently do
   nothing. Use clearly identified fixtures only when live data is unavailable.
6. Review new UI beside a representative existing screen. Fix drift introduced
   by the change at the responsible token/component rather than covering it
   with repeated overrides. Recheck consumers when changing a shared primitive.

Use the installed stack and versions; consult available current official or
Context7 documentation when library-specific syntax is needed. Apply relevant
framework/accessibility skills when available. Do not add dependencies, switch
component libraries, or mandate a particular framework just for visual novelty.
If a needed capability is absent, choose a small native solution where suitable.

## Verify and finish

Run the checks appropriate to the changed surface: existing build/type/lint
checks, relevant interaction tests, and browser inspection when available.
Check a representative wide and narrow viewport; exercise the primary action,
keyboard focus, content overflow, and relevant empty/error/loading states.
Check supported theme modes and reduced motion if affected. Distinguish HTTP
availability, visual inspection, and behavior testing; none substitutes for all
three. Do not claim pixel fidelity or accessibility compliance without evidence.

Update the design record with actual source paths, intentional exceptions,
what changed, and outstanding decisions. Source changes on resume can invalidate
an old record; re-read the live authority instead of blindly restoring cached
values. Finish with the implemented result, the shared style source, verification
performed, and material limitations. If work is paused, save the next action
and pending question without claiming completion.

For compaction preserve: target app/root, design-record location, runtime theme
sources, selected theme evidence, confirmed/assumed distinctions, changed shared
components, pending decision, and next action. Reload this skill and the current
project sources before further design work.
