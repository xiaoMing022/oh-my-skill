---
name: visual-brainstorm
description: >
  Visual brainstorming for UI direction. Use whenever the user is choosing
  how a page, component, or product should look — layout, navigation, density,
  visual tone, mockup comparison, 选布局, 对比样式, or /visual-brainstorm.
  Ask purpose and constraints in text, then show 2-3 mid-fidelity options on
  a local port so they can see and pick. Do not describe those options only
  in text, and do not ask permission first. Also use for charts, maps, plots,
  and labs when seeing beats a table. Do not implement in the project
  (frontend-design), build a clickable prototype to save (html-prototype),
  write an architecture spec (brainstorming), generate images or game art,
  or design Feishu/Lark apps.
metadata:
  short-description: "Visual brainstorming: see and pick UI direction on a local port"
---

# Visual Brainstorm

Help the user **see and pick** a UI / visual direction before anyone implements.

Ask purpose, constraints, and success criteria in text. For layout, navigation,
density, visual tone, or page structure, show 2-3 mid-fidelity options on a
local port in the same turn — do not describe those options only in text, and
do not ask whether to show them. After they pick, summarize the chosen
direction and stop. Do not write project code, do not write a spec, and do
not start `html-prototype` or `frontend-design` until they ask.

When producing or updating a visual, read `references/render-kit.md` and
follow it. Skip it for text-only questions.

Copy into every compaction summary:
`Reload visual-brainstorm (and render-kit.md before creating or updating a preview).`

## Neighbors

| Job | Skill |
| --- | --- |
| Choose how something looks | this skill |
| Architecture, data model, written spec | `brainstorming` |
| Clickable HTML prototype to preview or save | `html-prototype` |
| UI implemented in the open project | `frontend-design` |

Hand off only after the user asks. If `html-prototype` invoked this to confirm
one visual fork, do that fork and return.

## Session

Skip any step whose answer is already in the conversation.

1. **Context** — use product, platform, and constraints already in the
   conversation. Read the project only as far as the current visual question
   needs matching chrome. Do not tour the repo to draw a mockup.
2. **Text questions** — one at a time, multiple choice when it fits: purpose,
   constraints, success criteria, scope. If the answer is words, stay in chat.
3. **Visual forks** — as soon as the question is layout, navigation, density,
   tone, or page structure, read `references/render-kit.md` and show 2-3
   options. One question per screen. Recommend one in chat with a one-line
   why. Ask them to pick.
4. **Record and continue** — they confirm in chat (or request a change).
   Remember the choice. Reuse the same preview title and URL for the next
   fork. If they reverse a choice, redraw that fork; do not restart the
   session.
5. **Stop** — when no visual fork remains, summarize the chosen direction
   (layout, navigation, density, tone, and anything still open). Ask whether
   to continue into `html-prototype` or `frontend-design`. Do not start
   either until they say so.

## Visual vs text

Show a visual when seeing it is clearer than reading it. Stay in chat when
the answer is words.

A UI *topic* is not automatically a visual question. "Do you want a wizard?"
is text. "Which of these three wizard layouts?" is a visual. Charts, maps,
and labs use the same port when a table or paragraph would hide the shape;
they are not A/B product mockups. Use Mermaid (no preview server) when
labeled nodes and edges fully explain a static structure.

## Screens

- Put the question on the screen as a short heading. 2-3 options, labeled
  A/B/C. Mark the recommendation on the screen.
- Mid-fidelity: structure, hierarchy, key regions, representative copy, a
  hint of tone. Grey or labeled blocks for secondary areas. Raise fidelity
  only after they pick and ask to refine.
- Options are selectable locally (`data-choice`, `aria-pressed`). The
  decision is confirmed in chat. No control sends a message back to the
  agent.
- Option frames may use render-kit utilities; the depicted product may not.
- Compare at most two page-level layout sketches side by side. Do not
  present a single polished screen as if the direction were already decided.
- Do not invent dashboards, KPI cards, or filler widgets to look complete.

## Chat

Do not narrate fragments, ports, CSP, or this skill. While reading the skill
or writing a preview, stay silent unless blocked.

Text-question turns: one question, then wait.

Visual turns: the preview URL, what to compare, the recommendation, and
which option they want. Do not dump a table of the same content.

## After they pick

The terminal message is a short direction summary, then a question about
next step. Exporting the current preview to a standalone HTML file is only
for an explicit save of *this* visual — a clickable product prototype is
`html-prototype`; code in the repo is `frontend-design`.
