---
name: oms-designer
description: >
  Design and build interaction UI for Web and mobile/mini-program/desktop
  clients in one project design language with per-client adaptation. Use for
  new screens, feature styling, style migration, 前端设计, 页面设计,
  交互设计, 统一风格, 多端适配,
  or screens that look templated, generic, or 千篇一律.
  Reuse the project's native theme/token source via a short design contract;
  when no usable baseline exists, confirm a subject-specific theme once
  through oms-visualization.
metadata:
  short-description: "Interaction design for Web + clients from contract and native tokens"
---

# Interaction Design

Build working interfaces whose pages, components, content hierarchy, and states
belong to the same product — on Web and on client surfaces (mobile apps,
mini-programs, desktop clients). One design language, per-client adaptation:
not one fixed pixel layout copied everywhere. When the project already has a
voice, stay in it and carry it forward. When an aesthetic axis is still free,
choose a voice from this subject's audience, materials, and job — then commit.
Distinctiveness can come from precise typography, composition, and interaction.
It does not require a new palette, an unusual font, or decoration on every page.

This is the project's implementation skill. Use the supplied requirements,
existing code, and confirmed visual decisions together. Do not call this skill
recursively. In hosts with namespaced skills, prefer this package's sibling
skills for handoffs.

## Choose the smallest workflow

Read any incoming handoff before inspecting or asking again. Carry forward its
scope, confirmed decisions, and delegated choices; check the current source
before reusing an old theme or trace. Ask only about gaps that change the work.

| Work | Minimum workflow |
| --- | --- |
| Local correction in an existing UI | Inspect the affected component and consumed tokens; make the scoped fix; check the affected state. No new theme comparison, contract, or session by default. |
| New page/feature on an established baseline | Reuse the current contract and primitives; model the primary interaction and relevant failure path; implement and check representative layouts. Record only new decisions. |
| New baseline or explicitly requested rebrand | Resolve only missing or delegated visual choices, define a small native contract, then implement one representative slice before expanding. |
| Broad style migration | Read [references/migration.md](references/migration.md); inventory affected consumers, define staged changes and compatibility, then migrate and check each batch within the requested scope. |
| Additional client | Keep confirmed semantic roles; read only the matching parts of [references/clients.md](references/clients.md); adapt navigation, input, units, and states to that client. |

Scale records and verification to the change. A theme comparison, a new design
record, and a wide/narrow test matrix are not prerequisites for a one-state
correction. Broader checks are justified when a shared source or behavior changes.
Working records default to `.oh-my-skills/designer/contexts/` when needed;
runtime components, tokens, and maintained design docs use the project's normal
locations. Authorized source/doc changes outside the working root need no extra
permission. If all project-file writes are forbidden, use an available host
preview or permitted temporary location, including for oms-visualization records.

## Establish the baseline

For a local correction, inspect the affected component and its consumed theme
source. For a new page, baseline, migration, or client, inspect the target app's
entry point, theme/provider, shared components, styling configuration, and one
or two representative screens.
Read only enough to locate the actual design authority and import path.
No `globals.css` does **not** mean no design system: a component-library theme,
CSS Modules, utility configuration, shared package, or provider can own it.
Distinguish a placeholder starter theme from an intentional, repeatedly used
baseline. Follow app boundaries in monorepos; neighboring products may have
intentionally different brands.

Detect the client target(s) for this task: responsive Web, iOS/Android,
mini-program, or desktop. Each client has its own native token owner (CSS
variables, utility theme, provider theme, native theme file, WXSS theme);
locate each one instead of assuming the Web source covers all clients.

Read [references/design-context.md](references/design-context.md) for durable
records, source precedence, and where styles belong. Decide which case applies:

| Situation | Action |
| --- | --- |
| Coherent project baseline or already confirmed theme | Reuse it; briefly name the source and relevant rules, then build. Do not ask for the same theme again. |
| New project, starter-only styles, or no usable baseline | Ask about unresolved purpose/brand preferences, then use the theme confirmation below. |
| Mixed styles in a bounded feature task | Use that app's intended shared system; fix local inconsistencies without migrating the whole project. Clarify only if choosing the authority materially changes the result. |
| User requests a broad rebrand or cross-project style cleanup | Use the staged migration workflow in `references/migration.md`; preserve independent app boundaries. |
| Request is an architecture or implementation-approach fork | Decide inline with a short plan; if intent itself is unsettled, send it to `oms-brainstorming` first. |
| Request is what existing code does for a click, request, or function | Use `oms-code-chain` if available; do not turn an explanation into a restyle. |
| Request is only visual exploration or a standalone preview | Use `oms-visualization` in single-fork scope; do not turn it into product implementation. |

## Confirm a missing theme once

1. Reuse known audience, purpose, brand assets, accessibility needs, density,
   light/dark scope, and examples. If preferences are missing, actively ask one
   concise question such as “有必须沿用的品牌风格，还是希望我给出几种方向？”
   Use a question tool if available, otherwise chat. Do not interrogate users
   about individual hex values, radii, or font weights.
2. When enough context is known, call `oms-visualization` for **one theme fork**:
   2-3 directions that differ because of this subject, shown on the same
   representative content, layout, and viewports (for example desktop wide
   plus a 390px narrow frame, or phone plus mini-program frame for client
   tasks). Compare typography, surfaces, palette, density, and the treatment
   of primary actions together. Show real UI samples, not mood adjectives or
   color swatches alone. State a recommendation and tradeoff. Do not offer
   three costumes from the same generic kit.  The preview and its decision
   record stay under `.oh-my-skills/visualization/`.
3. Tell the visual skill its scope is a theme fork and the caller will resume
   implementation. A clear user selection completes theme confirmation; do
   not expand it into a full product discovery or repeat an integrated theme
   approval. A mixed/rejected choice remains unresolved: refine that fork
   using its bounded iteration rules, not a new set of unrelated themes.
4. Capture the selected option meaning, revision, evidence, and design rules.
   Translate the selected theme into each client's native token/component
   system (same semantic role names where possible), then continue the
   already requested build in the same turn.
   Do not copy preview host CSS, iframe wrappers, or sandbox behavior into the
   product. A sketch expresses intent, not production architecture.

If the user already supplies a precise style or explicitly delegates the
choice (“按你推荐的直接做 / 不用确认”), proceed with that direction and record
it as supplied or delegated, not as a visual choice they never made. If the
visual skill is unavailable, use an available browser/preview mechanism for
the same scoped comparison. If no visual delivery is possible, explain the
limitation and ask for a supplied direction or permission to proceed with the
subject-specific direction you recommend; do not claim that text choices are
a visually confirmed theme.

While a required answer is pending, continue independent inspection/planning
but do not commit a speculative theme into the product. Pause with the exact
pending question; silence and preview clicks are not confirmations.

## Make the look belong to this subject

A maintained baseline already chose the voice. Execute it precisely: hierarchy,
density, and the one emphasis this screen needs. Do not restyle the product
to look "more designed."

When the brief leaves an axis free — a new product, a rebrand, or a screen
with no maintained theme — the look has to come from this subject. Name who
uses it, the primary job, and the materials or vernacular of that world
before choosing type, color, or layout. A picture-book shelf and an analyst
queue should not share a costume. If the subject is missing and materially
changes the design, ask one focused question; if the user delegated that choice,
state the subject you choose and continue within that delegation.

Use a deliberate emphasis when it serves the task, and keep surrounding content
quiet. An editorial or expressive surface may have a memorable headline or
interaction; an operational tool can express its identity through scan order,
density, and dependable feedback. A decorative focal element is optional.
Open on what users came to do or see. Use a large metric or gradient accent only
when it helps that purpose.

Before product code for a new direction, write a short plan: a handful of
named color roles, typefaces and their jobs, the layout idea, and what makes
this surface specific. Then check that plan against the brief. If any part
is the look you would ship for any similar page, revise that part and say
what changed. Where the user already pinned a direction, follow it, including
when they asked for a look that would otherwise be a default. The generic
cluster, and the type, motion, structure, and copy rules, are in
[references/implementation.md](references/implementation.md).

While building, remove decoration only when it does not serve the brief; there
is no deletion quota. Words are part of the design: name an action by what the
user gets, keep that verb
through the flow, and make empty and error states say what to do next.

## Define the design contract

Keep a concise, project-specific contract in the existing design documentation,
or an external working record when the project has none. Write only decisions
that guide implementation; a small component does not require a full catalog.

- Subject and task emphasis: who it is for, the primary job, and how hierarchy
  supports it; an expressive focal choice only when relevant. A maintained
  baseline can record "reuse existing voice" instead.
- Purpose and visual thesis: a sentence connecting that job with the design
  approach, plus a few stable principles (for example, prioritize queue
  scanning, keep actions predictable, reserve emphasis for exceptions).
- Foundations: semantic colors and surface/text pairs, type hierarchy and
  fallback fonts, spacing/density, content widths, radii, borders, elevation.
- Component grammar: one source for each shared primitive and consistent
  variants, sizes, icon treatment, form feedback, navigation, and overlays.
- Behavior: responsive reflow and per-client adaptation (breakpoints, touch
  targets, safe-area insets, density variants, platform navigation patterns),
  relevant interaction states, focus treatment, theme modes, motion intent,
  and reduced-motion behavior.
- Token map (multi-client tasks): each semantic role mapped to its native
  owner per client — for example Web CSS variable, iOS asset/SwiftUI value,
  Android Compose colorScheme, mini-program WXSS variable.
- Authority: actual runtime source paths and scope per client, confirmed
  decision evidence, approved exceptions, and anything still assumed or
  deferred.

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
   the smallest native theme source into the actual app entry point. For each
   additional client, map the same roles into that client's native owner.
   A cache outside the repo must never become a runtime stylesheet dependency.
3. For new baselines, multi-page work, or migrations, build one representative
   slice, including its important states and the
   primary client plus a narrow/touch state, to verify the design rules
   before replicating across pages. This is an implementation check, not a
   mandatory second user confirmation of the theme. A local correction uses the
   affected existing component as its slice.
4. Apply the same contract throughout the requested surfaces. Extend semantic
   roles/variants centrally when needed; avoid page-local replacements for
   shared buttons, spacing scales, or typography. A new page may have a
   different layout while still using the same design language.
5. Keep real behavior intact: navigation, forms, validation, loading and failure
   states. Do not invent metrics or active-looking controls that silently do
   nothing. Use clearly identified fixtures only when live data is unavailable.
   For changed interactions, map the relevant states and transitions: trigger,
   pending operation, success/failure, and recovery. Define repeat-submit and
   cancellation behavior, and handling of stale results after navigation or
   object changes, only where the interaction can encounter them. Reuse the
   current state model; do not introduce a state-machine dependency by default.
6. Review new UI beside a representative existing screen. Fix drift introduced
   by the change at the responsible token/component rather than covering it
   with repeated overrides. Recheck consumers when changing a shared primitive.

Use the installed stack and versions; consult available current official or
Context7 documentation when library-specific syntax is needed. Apply relevant
framework/accessibility skills when available. Do not add dependencies, switch
component libraries, or mandate a particular framework just for visual novelty.
If a needed capability is absent, choose a small native solution where suitable.

## Verify and finish

Use the selected workflow to choose checks for the changed surface: existing
build/type/lint checks, relevant interaction tests, and browser inspection when
available.
For new pages, reflow changes, and shared migrations, check representative wide
and narrow viewports. For a local correction, check the affected state and
consumers. As relevant, exercise the primary action, keyboard focus, content
overflow, and relevant empty/error/loading states.
For client surfaces add a touch-target, safe-area, and platform-navigation
spot check. Check supported theme modes and reduced motion if affected.
Distinguish HTTP availability, visual inspection, and behavior testing; none
substitutes for all three. When the direction was new, look at the built
screen and confirm the task emphasis and any selected expressive choice survived.
Do not claim pixel fidelity or accessibility compliance without evidence.

Update the design record with actual source paths, intentional exceptions,
what changed, and outstanding decisions. Source changes on resume can invalidate
an old record; re-read the live authority instead of blindly restoring cached
values. Finish with the implemented result, the shared style source, verification
performed, and material limitations. If work is paused, save the next action
and pending question without claiming completion.

## Handoff

When transferring or resuming work, use these six fields in the existing record
or conversation; use `none`/`unknown` where needed:

```text
Scope: project/app/client, boundaries, and actions already authorized
Confirmed: supplied requirements or approved decisions, with evidence refs
Delegated: entrusted choices, actual choices made and rationale, with refs
Pending: unanswered questions, unconfirmed assumptions, blockers or none
Evidence: source paths/symbols, record/preview revisions, freshness and check limits
Next action: receiving skill/workflow, concrete step, continue or wait and why
```

Read the incoming record first; reuse current themes/traces and existing sessions.
Revalidate changed or stale sources, reopen only affected decisions, and continue
authorized work without repeating approval. Keep delegation distinct from a
user selection. Update the existing record instead of creating a duplicate.
If a sibling skill is unavailable, continue the authorized workflow with this
information; do not claim it was invoked.

For compaction preserve: target app/root, workflow, client list, subject, task
emphasis, design-record location, runtime theme sources per client, selected
theme evidence, confirmed/assumed distinctions, changed shared components,
pending decision, and next action.
Reload this skill and the current project sources before further design work.
