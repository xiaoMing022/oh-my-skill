---
name: oms-code-chain
description: >
  Trace what existing code actually does: locate the entry, follow the real
  call chain, cite key logic and data at each hop, and use Mermaid when the
  structure benefits from a diagram or the user asks for one. Use when the user
  asks what happens when, 会发生什么,
  调用链, 执行流程, 这段代码怎么走, 这条命令怎么实现, 安装是怎么做的,
  request path, click handler, how this command works, or /oms-code-chain. Do
  not use for how we should implement a change (oms-brainstorming or
  oms-designer), visual layout (oms-visualization), or clickable previews
  (oms-visualization).
metadata:
  short-description: "Trace real behavior with current evidence and proportional detail"
---

# Code Chain

Explain what already happens in the open project for one named behavior.
Find the entry, follow the real calls, keep a short hop list, cite the
code, and diagram the path when useful or requested. Do not invent a chain,
edit product files, or turn the question into a redesign.

## Scope and neighbors

| Job | Route |
| --- | --- |
| What existing code does for a click, request, event, command, or function | Full session below |
| How we should implement or restructure it | UI change goes to `oms-designer` with the traced path; unclear intent goes to `oms-brainstorming`; settled non-UI work uses the normal planning workflow in proportion to scope |
| Visual direction, layout, tone, prototype preview | `oms-visualization` |
| Build UI in the open project | `oms-designer` |
| Save workflow/API/user-feedback reference docs from code | `oms-process-docs`, with the current traced evidence |

If the user asks both “what happens now” and “how should we change it”,
finish the chain first, then hand off with the traced path as above.

## Match depth to the question

- A small function or single branch can be explained in 2–3 cited steps (or
  fewer when sufficient), without a diagram unless asked. Do not pad it.
- A multi-module behavior usually fits a 5–8 phase overview with one diagram.
  This is a readability guide, not a minimum or maximum. Expand a critical
  branch separately instead of hiding its failure or async behavior to fit.
- A follow-up expands only the relevant branch of current evidence. A full
  report or new session is not required for every question.

Normal output is in chat; no working directory or product edits are needed.
Optional scratch notes belong under `.oh-my-skills/code-chain/<slug>/`. Save a
report only when requested, using the agreed documentation path; that authorized
deliverable may be outside the working root. Honor a no-file-writes restriction.

## Trace the behavior

1. Name the behavior in one line. Reuse any file, symbol, URL, or command
   they already supplied. Read [references/trace.md](references/trace.md).
   - Same behavior, several shells or wrappers that funnel into one
     function: trace that shared spine; put the wrappers in Branches.
   - Two unrelated handlers that would produce different chains: ask
     one question; do not merge them.
2. Locate the real definition, then follow imports and calls only as far
   as the behavior requires. Stay inside the open project. This is a
   static read unless they asked to run it; if dispatch is generated or
   config-driven, say so.
3. Choose the depth above. Collapse consecutive steps in the same function
   unless a decision or side effect happens. Skip pass-through getters
   and logging unless they are the question.
4. For each hop, name the data that crosses it (argv, flags, body, path,
   return) and cite the actual source. Distinguish direct calls from scheduling,
   events, subscriptions, and network boundaries; do not imply immediate or
   guaranteed execution. Mark configuration-dependent or unread edges explicitly.
   When drawing, read [references/mermaid.md](references/mermaid.md), put the
   hop list first and the diagram after it, and reuse the same numbered
   stage names in both.
5. On a follow-up (“那 `--link` 呢”), reuse the traced spine after checking
   evidence freshness. If the worktree, branch, relevant files/configuration, or
   line locations changed, or freshness is unknown, reread the affected sources
   and update their citations. Expand only the asked branch plus dependencies
   affected by changes; do not restart unrelated parts of the trace.

Do not edit product files while tracing. If the user also requested changes,
handoff to the authorized implementation/planning workflow with the current
evidence and keep proposed behavior distinct from the traced behavior.

## Reply shape

Answer first. The first screen must state the outcome, not the search or the
diagram. Use the user's language for headings and labels.

For a simple answer, give a one-to-three sentence result followed by 2–3
one-line cited steps; no diagram and no section headings. Use the fuller shape
below for a multi-module trace; omit empty sections. Include a diagram whenever
the user asks for one. State static-read limits at the relevant boundary rather
than implying runtime verification. The headings below are examples in Chinese;
render them in the user's language.

~~~~markdown
## 结论
<1–3 sentences: trigger → final result or side effect. Do not repeat the diagram.>

## 调用链
1. **<stage>** — `path:line` `symbol` · <input> → <output/effect>
2. ...

## 结构图
```mermaid
...
```

## 分支与副作用
- <wrappers, flags, failure branches, unread edges>

## 证据边界
- <configuration-selected paths, unexecuted behavior, unread external code>
~~~~

One line per hop. Keep the stage name, the source location, and what crosses
the hop on that single line; add a short parenthetical only when the effect is
not clear from the arrow. Do not split a hop into separate “does / data /
citation” lines.

The hop list is the answer; the diagram is its visual index. Use the same
stage names and numbers in both. Delete any diagram node with no matching hop.
Branches stay out of the numbered main chain and are not drawn as if they were
spine nodes.

Do not retell the diagram in prose. Finish when the named behavior is covered.

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

For compaction, preserve: named behavior, confirmed entry or shared
spine, hop list with data/citations, evidence limits and freshness, unexpanded
branches, and the six-field handoff when needed.
`Reload oms-code-chain; read trace.md before following calls; mermaid.md
before drawing. Continue from the traced spine; do not edit product files.`
