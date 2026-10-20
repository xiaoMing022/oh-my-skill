---
name: visualization
description: >
  Show instead of tell: render options, schemes, flows, timelines, charts, or
  maps as framed HTML on a local port, and resolve the decision in dialogue.
  Use for layout, navigation, density, visual tone, mockup comparison, 选布局,
  对比样式, 方案对比, 架构图, 流程图, 时间线, 图表, 选型对比, or
  /visualization. Product implementation belongs to designer; intent
  discovery to brainstorming.
metadata:
  short-description: "Render framed visual options locally, confirm in dialogue"
---

# Visualization

Help the user see, compare, and resolve the important decisions before
implementation — UI direction, option schemes, flows, timelines, charts,
or maps. Seeing beats reading whenever the question is about something
they will look at, choose between, or follow step by step.

A choice resolves one decision, not automatically the session. Continue
from that choice to the next unresolved checkpoint in the same turn;
wait only when the next step needs the user's answer. Do not invent
answers, treat silence or an agent recommendation as confirmation, or
treat a click on the page as confirmation: confirmation happens only in
dialogue.

This skill writes framed HTML previews into the project at
`.oh-my-skills/visualization/<session-slug>/` and serves them on a local port. It
does not implement product code or require an architecture spec. Do not
ask permission to show a visual the task already calls for.

Read an incoming handoff first. Reuse its confirmed/delegated choices, current
preview revisions, scope, and existing session. Ask only about unresolved
decisions; receiving a handoff does not restart the comparison. If all project
writes are forbidden, use an available host preview or permitted temporary
location rather than writing `.oh-my-skills/` inside that project. Explicit
working/export locations override defaults within the host's permissions.

## Scope and neighbors

| Job | Route |
| --- | --- |
| Choose direction with visual options, schemes, or diagrams | Full session below |
| Resolve one named fork, including a theme fork call from `designer` | Only that fork; return its decision to the caller |
| Explain data with a chart, map, or lab | Show the relevant visual; do not impose UI checkpoints or A/B options |
| Implement UI in the open project | `designer`, if available |
| Uncover what to build and why | `brainstorming`, if available |
| What existing code does for a click, request, or function | `code-chain`, if available |

Honor the scope already authorized. If the user asks to proceed to a
build, hand off with confirmed decisions and explicit assumptions; do
not make them finish unnecessary comparisons or ask for the same
authorization again. If the next skill is unavailable, continue within
the authorized task using the decision record instead of claiming a
tool was invoked.

## Plan the visual decisions

1. Reuse the purpose, audience, platform, constraints, references, and
   success criteria already supplied. Inspect the project only enough to
   ground the current choice. Ask one focused text question if missing
   context would materially change the alternatives; otherwise state the
   assumption.
2. Present a short, ordered decision plan before or alongside the first
   visual. Checkpoints may cover structure/navigation, hierarchy and
   density, visual tone, a scheme or flow comparison, a timeline, or a
   chart — select checkpoints for this task, not to meet a quota. A
   plain explainer (one diagram that answers one question) needs no A/B
   quota at all.
3. Give each checkpoint a stable ID, the question to resolve,
   dependencies, and completion evidence. Mark already answered items
   confirmed with their source; mark irrelevant items skipped with a
   reason. Do not re-ask them.
4. Keep the plan and decisions in `session.md` using
   [references/session.md](references/session.md). This is a working
   record, not a separate spec approval gate. Creating it is part of the
   workflow.

## Iterate at each checkpoint

1. Choose the highest-impact unresolved decision whose dependencies are
   known. Keep confirmed choices fixed. For decisions, show 2-3
   materially different alternatives at equivalent copy, data, viewport,
   and fidelity; explain one tradeoff per option and recommend one with
   a short reason. For explainers, show one visual.
2. Read [references/render-kit.md](references/render-kit.md) before
   producing or updating a preview. Read `references/charts.md` or
   `references/maps.md` only for visuals that need them. Publish to the
   session's `.oh-my-skills/visualization/<slug>/` directory and verify the static
   file loads over HTTP: every checkpoint is a standalone framed page,
   and `index.html` links them all on one stable URL. Use a visual for
   layout, hierarchy, navigation, density, tone, scheme, flow, or data;
   do not substitute a prose list of styles.
3. Show the checkpoint ID, a short revision label (for example D2 / R2),
   the question, A/B/C labels, and the recommendation. Map that label
   to the saved revision path in the record so feedback refers to the
   right alternatives. Ask for that decision in chat, in plain words —
   for example "选 A 还是 B?" or "这个流程图缺了什么?".
   On-page buttons are visual only: a click confirms nothing. A reply
   like "选 B" or "都不太好，保留 A 的信息量" is the confirmation.
4. On a clear answer, record the chosen revision and option meaning,
   rationale, and any constraints; sync the badge
   (`session.py mark ... confirmed`), then update the plan and produce
   the next checkpoint. “A” alone is meaningful only for the current
   displayed checkpoint/revision. Clarify ambiguous or stale answers
   before applying them.
5. For “neither”, mixed preferences, or a change request, record what
   failed and revise that checkpoint. A hybrid is a new candidate, not
   a confirmed selection. When a previous choice changes, retain its
   history and mark dependent decisions `needs-review`; leave
   independent confirmations intact.

Make progress visible: briefly say what is settled, what the current
comparison resolves, and what remains. Do not end with “let me know if
you need more” while planned checkpoints remain. Waiting for an answer
pauses the session; it does not complete it. On resume, load the saved
record and continue the pending item.

## Converge and hand off

- If two presented option sets for the same checkpoint (initial R1 and
  revised R2) are both rejected without a choice, identify the
  unresolved criterion and ask one targeted question before drawing R3.
  Offer a smaller scope or a recommended default; do not silently
  accept it.
- Stop adding checkpoints once the agreed scope is covered. Newly
  discovered issues belong in the plan only if they affect the task's
  outcome. Cosmetic polish and exhaustive component states are not
  automatic new rounds.
- For a full session, combine the confirmed decisions into one sketch
  and request an integrated review. This is allowed to be a single
  screen: it verifies how selected parts fit together, rather than
  pretending an initial direction is already decided. Include a
  critical narrow/interaction state if it was in scope. Fix
  inconsistencies before calling the result complete.
- Complete when all in-scope checkpoints are confirmed or explicitly
  deferred by the user, and the integrated review is accepted. A
  single-fork session completes on that fork's confirmation. A user
  request to stop, pause, or build early is honored and recorded
  without claiming full validation.
- Finish with the chosen direction, any deferred decisions/
  assumptions, the preview URL, and a short ordered next-step plan
  appropriate to the requested prototype or implementation. Pass
  `session.md` and the selected revision paths to the next skill.
  Continue an already authorized build immediately; otherwise offer the
  next step without starting product implementation.

## Visual quality and communication

- Mid-fidelity means actual structure, hierarchy, representative
  content, and a hint of tone. Grey blocks suffice for secondary
  areas. Raise detail only enough to answer the current question;
  avoid filler dashboards and widgets.
- Compare at most two page-level layouts side by side. Stack a third
  option. Use native labeled buttons for options, with `data-choice`
  and `aria-pressed`; do not nest interactive mockup controls inside a
  button.
- Option frames may use render-kit utilities; depicted products use
  scoped product styles. Keep comparisons usable at the target and
  narrow widths.
- Ask purpose/constraints in text. A UI topic alone does not require a
  visual. A simple static node/edge explanation can use Mermaid
  without a server.
- Decision-comparison turns contain the preview link, what to compare,
  the recommendation, and one question. Use an available question tool
  or a concise chat question; no host-specific tool is required. Do
  not narrate fragment/frame mechanics.
- If browser inspection is unavailable, verify HTTP output and say
  rendering was not visually checked. If the user cannot access the
  local port, use an available host preview or screenshot delivery
  mechanism and retain the same session record. Do not claim a written
  file is an accessible visual preview.

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

For compaction, preserve the session directory, current
checkpoint/revision, pending question, confirmed/deferred decisions,
and next action. Include: `Reload visualization; read session.md;
render-kit.md before any preview; charts.md / maps.md only when
needed.`
