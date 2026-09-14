---
name: visual-brainstorm
description: >
  Visual brainstorming for UI direction: plan the important decisions, show
  2-3 mid-fidelity options on a local preview, and iterate with the user until
  the agreed scope is resolved. Use for layout, navigation, density, visual
  tone, mockup comparison, 选布局, 对比样式, or /visual-brainstorm. Also use for
  charts, maps, plots, and labs when seeing beats text. Implementation and
  clickable product prototypes belong to frontend-design and html-prototype.
metadata:
  short-description: "Plan, compare, confirm, and converge on visual direction"
---

# Visual Brainstorm

Help the user see, compare, and resolve the important visual decisions before
implementation. A choice resolves one decision, not automatically the session.
Continue from that choice to the next unresolved checkpoint in the same turn;
wait only when the next step needs the user's answer. Do not invent answers
or treat silence, a local click, or an agent recommendation as confirmation.

This skill creates working previews and a small decision record outside the
project. It does not implement product code or require an architecture spec.
Do not ask permission to show a visual the task already calls for.

## Scope and neighbors

| Job | Route |
| --- | --- |
| Choose visual direction across a page or product | Full session below |
| Resolve one named visual fork, including a call from `html-prototype` | Only that fork; return its decision to the caller |
| Explain data with a chart, map, or lab | Show the relevant visual; do not impose UI checkpoints or A/B options |
| Build a clickable product prototype | `html-prototype`, if available |
| Implement UI in the open project | `frontend-design`, if available |
| Architecture, data model, written technical spec | `figure-out`, if available |
| What existing code does for a click, request, or function | `code-chain`, if available |

Honor the scope already authorized. If the user asks to proceed to a build,
hand off with confirmed decisions and explicit assumptions; do not make them
finish unnecessary comparisons or ask for the same authorization again. If
the next skill is unavailable, continue within the authorized task using the
decision record instead of claiming a tool was invoked.

## Plan the visual decisions

1. Reuse the purpose, audience, platform, constraints, references, and success
   criteria already supplied. Inspect project UI only enough to ground the
   current choice. Ask one focused text question if missing context would
   materially change the alternatives; otherwise state the assumption.
2. Present a short, ordered decision plan before or alongside the first visual.
   For a page or product this often covers structure/navigation, hierarchy and
   density, visual tone, a consequential interaction or responsive state, then
   an integrated review. Select checkpoints for this task, not to meet a quota.
   A component may need only one fork; a product usually needs several.
3. Give each checkpoint a stable ID, the question to resolve, dependencies,
   and completion evidence. Mark already answered items confirmed with their
   source; mark irrelevant items skipped with a reason. Do not re-ask them.
4. Keep the plan and decisions in `session.md` using
   [references/session.md](references/session.md). This is a working record,
   not a separate spec approval gate. Creating it is part of the workflow.

## Iterate at each checkpoint

1. Choose the highest-impact unresolved decision whose dependencies are known.
   Keep confirmed choices fixed. Show 2-3 materially different alternatives
   for that question, using equivalent copy, data, viewport, and fidelity.
   Explain one tradeoff per option and recommend one with a short reason.
2. Read [references/render-kit.md](references/render-kit.md) before producing
   or updating a preview. Read `references/charts.md` or `references/maps.md`
   only for visuals that need them. Publish to the checkpoint's own tab on the
   same session URL and verify the current revision loads: the preview is one
   fixed tabbed page, earlier checkpoints stay viewable in their tabs, and the
   open page syncs itself after a publication. Use a visual for layout,
   hierarchy, navigation, density, or tone; do not substitute a prose list of
   styles.
3. Show the checkpoint ID, a short revision label (for example D2 / R2), the
   question, A/B/C labels, and the recommendation. Map that label to the saved
   revision path in the record so feedback refers to the right alternatives.
   Ask for that decision in chat. An on-page selection is recorded to the
   session's `choices.json` as preview feedback, not confirmation. When the
   user's reply references their on-page pick ("按我页面点的"), read that file
   to resolve which option they mean; a plain recorded click without a chat
   reply confirms nothing. Use the host's single confirm-in-chat hint.
4. On a clear answer, record the chosen revision and option meaning, rationale,
   and any constraints; sync the tab badge (`session.py mark ... confirmed`),
   then update the plan and produce the next checkpoint.
   “A” alone is meaningful only for the current displayed checkpoint/revision.
   Clarify ambiguous or stale answers before applying them.
5. For “neither”, mixed preferences, or a change request, record what failed
   and revise that checkpoint. A hybrid is a new candidate, not a confirmed
   selection. When a previous choice changes, retain its history and mark
   dependent decisions `needs-review`; leave independent confirmations intact.

Make progress visible: briefly say what is settled, what the current comparison
resolves, and what remains. Do not end with “let me know if you need more” while
planned checkpoints remain. Waiting for an answer pauses the session; it does
not complete it. On resume, load the saved record and continue the pending item.

## Converge and hand off

- If two presented option sets for the same checkpoint (initial R1 and revised
  R2) are both rejected without a choice, identify the unresolved criterion
  and ask one targeted question before drawing R3.
  Offer a smaller scope or a recommended default; do not silently accept it.
- Stop adding checkpoints once the agreed scope is covered. Newly discovered
  issues belong in the plan only if they affect the task's outcome. Cosmetic
  polish and exhaustive component states are not automatic new rounds.
- For a full session, combine the confirmed decisions into one sketch and
  request an integrated review. This is allowed to be a single screen: it
  verifies how selected parts fit together, rather than pretending an initial
  direction is already decided. Include a critical narrow/interaction state
  if it was in scope. Fix inconsistencies before calling the result complete.
- Complete when all in-scope checkpoints are confirmed or explicitly deferred
  by the user, and the integrated review is accepted. A single-fork session
  completes on that fork's confirmation. A user request to stop, pause, or
  build early is honored and recorded without claiming full validation.
- Finish with the chosen direction, any deferred decisions/assumptions, the
  preview URL, and a short ordered next-step plan appropriate to the requested
  prototype or implementation. Pass `session.md` and the selected revision
  paths to the next skill. Continue an already authorized build immediately;
  otherwise offer the next step without starting product implementation.

## Visual quality and communication

- Mid-fidelity means actual structure, hierarchy, representative content, and
  a hint of tone. Grey blocks suffice for secondary areas. Raise detail only
  enough to answer the current question; avoid filler dashboards and widgets.
- Compare at most two page-level layouts side by side. Stack a third option.
  Use native labeled buttons for selecting options, with `data-choice` and
  `aria-pressed`; do not nest interactive mockup controls inside a button.
- Option frames may use render-kit utilities; depicted products use scoped
  product styles. Keep comparisons usable at the target and narrow widths.
- Ask purpose/constraints in text. A UI topic alone does not require a visual.
  A simple static node/edge explanation can use Mermaid without a server.
- Decision-comparison turns contain the preview link, what to compare, the recommendation,
  and one question. Use an available question tool or a concise chat question;
  no host-specific tool is required. Do not narrate fragment/CSP mechanics.
- If browser inspection is unavailable, verify HTTP output and say rendering
  was not visually checked. If the user cannot access the local port, use an
  available host preview or screenshot delivery mechanism and retain the same
  session record. Do not claim a written file is an accessible visual preview.

For compaction, preserve the session directory, current checkpoint/revision,
pending question, confirmed/deferred decisions, and next action. Include:
`Reload visual-brainstorm; read session.md; render-kit.md before any preview;
charts.md / maps.md only when needed. Verify server identity before reuse.`
