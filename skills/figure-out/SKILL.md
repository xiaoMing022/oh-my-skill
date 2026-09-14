---
name: figure-out
description: >
  Figure out hard technical work: decompose it into decision checkpoints,
  compare 2-3 implementation approaches per task, evaluate and recommend
  one, then enter plan mode and execute only after the user confirms. Use
  for architecture, system structure, data model, implementation approach,
  理清思路, 实现思路, 技术方案, 系统结构, 架构设计, 技术选型, 怎么实现,
  拆解需求, or /figure-out. Visual layout belongs to visual-brainstorm;
  clickable HTML prototypes to html-prototype; page styling to my-designer.
metadata:
  short-description: "Figure out hard tasks: compare approaches, plan, then execute"
---

# Figure Out

Help the user figure out the important technical forks before writing a plan
or product code. Split the request into decision-bearing tasks, show 2-3
real approaches for the current task, evaluate them, and recommend one.
A choice resolves one task, not the session.

Do not invent answers, treat silence as confirmation, or start
implementation from an unconfirmed recommendation. Creating the decision
record is part of the workflow, not a separate approval gate.

## Scope and neighbors

| Job | Route |
| --- | --- |
| Architecture, data model, implementation approach, technical fork | Full session below |
| What existing code does for a click, request, or function | `code-chain` |
| Visual direction, layout, tone | `visual-brainstorm` |
| Build UI in the open project | `my-designer` |
| Clickable HTML prototype | `html-prototype` |
| Unify existing project styles | `design-unify` |

Honor already authorized work. If the user asks to proceed after approaches
are confirmed, go to the plan gate; do not reopen settled forks. If a
neighbor skill is unavailable, continue from the decision record instead of
claiming a tool was invoked.

## Plan the technical decisions

1. Reuse purpose, constraints, non-goals, and success criteria already
   supplied. Inspect existing code only enough to ground the alternatives:
   current modules, data flow, operational limits, and what a change would
   actually touch. Ask one focused question if missing context would
   materially change the options; otherwise state the assumption.
2. Present a short, ordered decision plan before or alongside the first
   comparison. Decompose the request into tasks that have a real fork —
   structure, boundaries, persistence, consistency, failure handling,
   integration, or a hard algorithm — not a project-plan checklist of every
   file to edit. Select checkpoints for this task, not to meet a quota.
3. Give each checkpoint a stable ID, the question to resolve, dependencies,
   and completion evidence. Mark already answered items confirmed with their
   source; mark irrelevant items skipped with a reason. Do not re-ask them.
4. Keep the plan and decisions in `session.md` using
   [references/session.md](references/session.md). Working files stay
   outside the project: `scripts/session.py init <slug>`.

## Iterate at each checkpoint

1. Choose the highest-impact unresolved task whose dependencies are known.
   Keep confirmed choices fixed. Show 2-3 materially different approaches
   for that question, using the same constraints and success criteria.
   Read [references/options.md](references/options.md) before writing the
   comparison. Do not invent a fake alternative when the constraints leave
   only one honest path; say so and ask to proceed with it.
2. For each option: what it is, how it would work here, tradeoffs, risks,
   and fit with the current code. Then evaluate the set and recommend one
   with a short reason. The evaluation is part of the deliverable, not an
   afterthought.
3. Show the checkpoint ID, the question, A/B/C labels, the recommendation,
   and one question. Use an available question tool or a concise chat
   question. Wait for a conversational answer.
4. On a clear answer, record the chosen option, rationale, and any
   constraints; mark the checkpoint confirmed, then produce the next one
   in the same turn. “A” or “选你推荐的” is meaningful only for the current
   displayed checkpoint. Clarify ambiguous or stale answers first.
5. For “neither”, mixed preferences, or a change request, record what
   failed and revise that checkpoint. A hybrid is a new candidate, not a
   confirmed selection. When a previous choice changes, retain its history
   and mark dependent decisions `needs-review`; leave independent
   confirmations intact.

Make progress visible: briefly say what is settled, what the current
comparison resolves, and what remains. Do not end with “let me know if you
need more” while planned checkpoints remain. Waiting for an answer pauses
the session; it does not complete it. On resume, load the saved record and
continue the pending item.

## Converge, plan, then execute

Stop adding checkpoints once the agreed scope is covered. Newly discovered
issues belong in the plan only if they change an unresolved fork.

When every in-scope checkpoint is confirmed, explicitly deferred, or the
user asks to proceed with the confirmed approaches:

1. Do not start product edits in this turn.
2. Read [references/plan-handoff.md](references/plan-handoff.md) and enter
   **plan mode**. Write a concrete implementation plan from the confirmed
   approaches, named assumptions, ordered steps, blast radius, risks, and
   verification. Wait for the user to approve that plan.
3. After plan approval, return to implementation mode if the host requires
   it, then execute the approved plan. Do not reopen settled technical
   forks unless the plan review changed them.
4. If the remaining work is visual implementation or a clickable prototype,
   hand off with the decision record instead of duplicating those skills.

A user request to stop or pause is honored and recorded without claiming
the approaches were fully validated. Finish with the chosen approaches,
deferred items, the session path, and either the approved plan or the
execution summary.

## Communication

- Prefer a comparison the user can reject over a single hidden default.
- Use a small Mermaid diagram when the fork is about structure or data
  flow; do not substitute a diagram for the evaluation.
- Ask constraints in text. A technical topic alone does not require a
  diagram, a preview server, or a visual-brainstorm session.
- Decision turns contain the checkpoint, the options, the recommendation,
  and one question.

For compaction, preserve the session directory, current checkpoint,
pending question, confirmed/deferred decisions, and next action. Include:
`Reload figure-out; read session.md and options.md; plan-handoff.md
before entering plan mode. Do not implement before the plan is approved.`
