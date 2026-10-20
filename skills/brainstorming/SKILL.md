---
name: brainstorming
description: >
  Brainstorm before creative work: uncover real goals with one-question-at-a-time
  conversation, play back understanding, size quick/small/project, write a
  builder-ready design doc with approval gate. Use for new feature, new idea,
  新想法, 头脑风暴, 需求讨论, 做什么, 为什么, 演讲, 业务, 装修, or
  /brainstorming. Layout mockups and clickable previews belong to
  visualization; settled UI work belongs to designer.
metadata:
  short-description: "Uncover goals, play back, size, design doc with approval gate"
---

# Brainstorming

You are very good at building. You build what you believe your partner
wants, and that belief is usually thinner than it feels. Find out what
they actually want, and why, before anything gets built — in software or
out of it (a talk, a business, a renovation).

People often haven't finished working out what they want. Good questions
help them think it through. When you understand the why, you make the
hundred decisions they never mention the way they would have made them.

Do not offer option lists to save effort, fill in silent defaults, explain
the process instead of asking, or build before the full description is
approved. A spike that works is still throwaway until keeping it goes back
through the gate.

## Scope and neighbors

| Job | Route |
| --- | --- |
| Vague idea, what/why, goals, success, design doc | Full session below |
| Intent is settled, technical fork A/B/C | Decide inline in plan mode after the gate; attach a `code-chain` result first if it needs a code trace |
| What existing code does for a click, request, or function | `code-chain` |
| Visual direction, layout, tone, prototype preview | `visualization` |
| Build UI in the open project, including style unification in scope | `designer` |

If the request is really a technical fork with clear intent (structure,
data model, integration A vs B), settle it inline in plan mode with the
stated intent attached. If a neighbor skill is unavailable, continue from
the session record instead of claiming a tool was invoked.

Read an incoming handoff before discovery. Carry forward its supplied goals,
confirmed decisions, delegated choices, and authorization bounds; ask only about
remaining gaps. Do not restart discovery or create another session for the same
task solely because responsibility changed. Working state defaults to
`.oh-my-skills/brainstorming/sessions/`; software specs default to its sibling
`specs/`, unless the user or maintained project convention supplies another doc
location. Authorized documentation outside the working root needs no extra gate.
If all project writes are forbidden, keep the description in chat or use a
permitted host/temporary location; that restriction includes `.oh-my-skills/`.

## Workflow

1. Triage first — what do you actually know? A quick, clear task ("make
   the icon cornflower blue") is the request itself: do it and say what
   you did. Anything non-trivial starts the conversation below.
2. First message, in order: one line letting them skip the questions and
   have you just start (if they take it, this skill is done: state any
   significant how-it-gets-made choice in one plain line, then do the work
   through the normal workflow), then one open concrete question. Read
   [references/conversation.md](references/conversation.md) before writing it.
3. Hold the conversation: each message ends with exactly one
   single-sentence plain-language question. Cover the territory, play back
   each understood part in 200-300 words, mark guesses as guesses, and end
   each chunk by asking what's wrong or missing.
4. Size the work once you understand it. Read
   [references/sizing.md](references/sizing.md): quick task, small change
   described in chat, or project with a written design. Say the size in
   plain words; they can override it.
5. For a project, write the design doc. Read
   [references/design-doc.md](references/design-doc.md) for shape and
   location. Keep working files under `.oh-my-skills/brainstorming/`: `scripts/session.py
   init <slug>`, record per [references/session.md](references/session.md).
6. Run the builder check. Read
   [references/builder-check.md](references/builder-check.md): a fresh
   reviewer reads the doc once, you sort the gaps, and bring back only the
   questions only the partner can answer.
7. Hold the hard gate: nothing gets built until the partner approves the
   full description — in chat for a small change, the document for a
   project. Building includes product code, scaffolding, installing deps,
   creating projects, and invoking an implementation skill. Reading and
   exploring are fine. After approval, software goes to plan mode with the
   approved design; UI work hands off to `designer` with the design
   attached, visual choices to `visualization`.

Look-at-able content (a page, screen, schedule, printout) stays text here:
describe it in words, then ask whether they want 2-3 versions via
`visualization`. Do not start a preview server from this skill.

## Communication

- Every message ends with one question. No lists of example answers
  hanging off it; offer a short menu only when they're stuck.
- Match their vocabulary; never use process jargon. Lead with what
  matters, most important findings first.
- Say sensible defaults out loud. A default they never heard is one they
  couldn't reject. Record your calls as your calls, never as agreed.
- A spike gets no tests or minimal ones, skips plan/implementation/review,
  and feeds its learnings back into the conversation.

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

For compaction, preserve the session directory, size, design doc path,
gate state, pending question, and next action. Include: `Reload
brainstorming; read session.md and conversation.md; builder-check.md
before handoff. Do not build before the full description is approved.`
