# Turning the baseline into maintainable UI

Read when mapping a chosen theme into code or checking consistency. Apply the
parts relevant to the surface; a small component does not need a system rewrite.

## Tokens and the cascade

Use the project's native mechanism. Existing provider tokens should not be
shadowed by a parallel agent CSS palette. Existing utilities should map to the
same theme; module-local styling should consume established variables or values.
If there is no authority, create a minimal app-owned theme in the usual source
location and import/provide it once at the appropriate app boundary.

Use semantic roles for repeated decisions: page/surface/raised backgrounds;
primary/secondary/on-accent text; border/focus; primary action; success/warning/
danger; type hierarchy; spacing/density; radii/elevation; motion and layering.
These are roles, not mandated identifier spellings. Reuse existing token names.
Add only roles actually needed by the requested screens. Do not tokenize every
incidental dimension or create an unused enterprise-scale token taxonomy.

- Map surface and foreground together; verify hover, disabled, selected, and
  error combinations as well as default colors. Theme modes change role values,
  not the meaning of components.
- Keep repeated styles centralized. Fixed image aspect ratios, one-off artwork,
  and data-driven geometry can be local; document exceptions that affect the
  design language. Avoid regex-based “no literal values anywhere” enforcement.
- In an existing app, scope new rules to the feature/component unless an
  app-wide change is intended. Inspect inheritance, order, specificity, and
  overlay/portal roots before changing global selectors.
- Avoid repeated `!important`, appended override sheets, duplicated resets,
  and selectors that restyle all library internals. Use supported component
  variants/theme APIs or a deliberate wrapper where needed.
- Watch selector specificity. A type-based class and an element selector can
  cancel each other's padding or margin. Do not ship rules that fight.
- A shared button change can affect many screens. Verify representative
  consumers; do not fix only the newly created page and leave the rest broken.

## Client adaptation

For multiple or additional clients, read only the applicable sections of
[clients.md](clients.md). Carry confirmed semantic roles into each native owner;
adapt units, input, navigation, and validation to the platform. Native sheets,
modals, and Web portals must receive the appropriate scoped theme. Keep a
compact role-to-owner map without forcing stable native identifiers to match.

## Visual language

Choose a small set of principles tied to the user's task and apply them to
composition. A dense operational tool may emphasize scan paths and stable
controls; an editorial surface may emphasize reading rhythm and imagery. Do
not transplant decorative landing-page treatments into every work screen.
Build with the brief's real content. Placeholder copy that could sit on any
product makes the layout feel templated even when the CSS is careful.

### When an axis is free

These looks are legitimate when the brief asks for them. They are tells when
they show up no matter what the subject is. If the user pinned one, follow
it. If the axis was free, do not spend it here:

1. Warm cream ground, high-contrast serif display, terracotta or clay accent.
2. Near-black ground with one acid-green or vermilion accent.
3. Broadsheet: hairline rules, zero radius, newspaper columns.
4. The card kit: identical rounded cards, one radius on everything, the same
   soft grey shadow, gradient washes as decoration.
5. Template chrome on every surface: tracked-out all-caps eyebrows, meta
   strings joined by middle dots, `WORD — fragment` labels, a monospace face
   on small data, a `→` stuck on every link and button.

On a maintained baseline, skip this list and execute the existing voice.
The rules below still apply inside that voice.

**First view:** Open on the most characteristic thing in this subject's world:
a headline, an image, a live sample, or one interactive moment. A big number,
a small label, supporting stats, and a gradient accent is the default
treatment. Use it only when that is truly the best opening. On a work tool,
the first view is usually the task itself, not a hero.

**Typography:** One family, or two that are clearly distinct. Set a real
scale — size, weight, width, and spacing with jobs — instead of a new face
for every level. When type is the headline, the treatment is part of the
design, not a neutral delivery of the words. Keep line length under about
80 characters; a serif body can run slightly longer and needs a little more
line-height than a sans. Cover the languages in use, including Chinese.
Preserve existing fonts unless a change is intended. System fonts are valid.
If choosing new assets, use permitted sources, suitable fallbacks, and a
loading strategy that keeps content readable. Do not fetch several decorative
families by default.

Skip the common generated-page tells: accenting a single word in a headline
with italic, bold, or a different color; all-caps labels; a label sitting
above content that did not need one.

**Structure:** Outlines, borders, numbers, eyebrows, dividers, and labels
encode information. Numbered markers (`01 / 02 / 03`) belong on a real
sequence — a stepped process or a timeline — and nowhere else.

**Space and hierarchy:** Use a coherent spacing rhythm and say whether content
is left-aligned, centered, or justified. Density changes row and padding
decisions consistently, rather than shrinking all text. Group related content
and keep primary actions discoverable. Avoid filler cards, invented KPIs, and
repeated identical panels solely to occupy space.

**Components and icons:** Reuse the installed primitive/component family.
Select a small set of explicit variants instead of copy-pasting modified
buttons into every page. Keep icon family, stroke/weight, sizing, and alignment
consistent; give icon-only actions accessible names. Do not substitute emoji
for a cohesive icon system unless that is the chosen product language.

**Surfaces and elevation:** Use borders, fills, radius, and shadows with defined
meaning: grouping, interaction, or layering. Preserve legibility over images
and translucent effects. Overlays need a deliberate stacking and scroll model;
scoped tokens must reach portaled content through the existing theme mechanism.

**Charts and data:** Use the existing chart stack and semantic palette. Preserve
category/color meanings across screens and theme modes. Supply readable labels,
units, and non-color cues. Never invent live numbers to make a layout attractive.

**Motion:** Use motion that answers a person's action — opening, expanding,
confirming — so they can see what changed. Non-triggered motion is rare:
one orchestrated moment, such as a single page-load sequence, beats scattered
effects. A fade-and-slide on every section, and a hover transition on every
card, is the generic default. Prefer existing motion patterns and small native
effects over installing a library for decoration. Respect reduced motion,
avoid delaying task access, and keep content available if animation fails.

**Copy:** Words make the interface easier to understand. Name things by what
the user does, in plain language: they manage notifications, not webhook
config. A control says what happens when it is used (`Save changes`, not
`Submit`) and keeps that verb through the flow, so `Publish` produces
`Published`. Sentence case, active voice, one job per line. An error says
what went wrong and how to fix it, without apologizing. An empty screen
invites the next action. Match tone to the audience; do not add filler to
make a layout feel written.

## Responsive and accessible behavior

Build from content and task priority, not a screenshot's fixed dimensions.
Honor existing breakpoints; introduce another only when a real layout need
justifies it. Reflow navigation, forms, action groups, tables, and dialogs at
narrow widths. Keep essential actions reachable; use deliberate table scrolling
when columns truly must remain aligned. Check long/localized text, empty results,
large values, and text enlargement. Do not merely scale a desktop canvas
down to a phone or mini-program page: reflow navigation, action reachability,
and density for touch rather than shrinking text.

Use semantic controls and visible labels. Preserve keyboard operation, focus
visibility, meaningful reading order, and error associations. For overlays,
use the established accessible primitive and verify focus/closing behavior.
Provide non-hover access to important information. Check actual contrast and
non-color cues instead of assuming a named token is accessible everywhere.

Model only relevant states, but implement them honestly: default, focus/hover,
active/selected, disabled, loading, empty, success, and error. Reuse the app's
state conventions. A validation message needs recovery guidance; loading should
not erase the user's context or allow accidental repeat submission. Preserve
real data and callbacks; do not replace an existing integration with fixtures.
When rendering titles, messages, or other externally supplied content, use the
framework's normal escaping or DOM text APIs; do not interpolate it as raw HTML
to speed up a visual implementation.

## Verification proportional to the change

Choose representative evidence rather than mechanically expanding a test suite.
Use existing build/type/lint/test commands discovered in the project. Run tests
that exercise changed behavior; do not write tests merely asserting CSS strings.

In a browser, inspect the changed surface beside a representative existing
screen when available. Check wide/narrow reflow, primary task completion, focus,
content extremes, and affected theme/state variants. If a global primitive
changed, include another consumer that could regress. For a theme selection,
verify the implemented result still expresses the confirmed direction; do not
reopen that choice merely because implementation requires ordinary adjustments.
If the direction was new, check that the task emphasis and any chosen expressive
element survived. Operational screens need no decorative focal element.

Inspect the final diff for new competing style sources, unconsumed tokens,
page-local copies of shared components, accidental global overrides, and external
cache paths in imports. Report what was verified, what could not be run, and any
remaining drift without calling an untested result production-ready.
