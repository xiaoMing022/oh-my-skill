---
name: code-chain
description: >
  Trace what existing code actually does: locate the entry, follow the real
  call chain, list key logic at each hop with citations, and visualize the
  flow in Mermaid. Use when the user asks what happens when, 会发生什么,
  调用链, 执行流程, 这段代码怎么走, request path, click handler, or
  /code-chain. Do not use for how we should implement a change (figure-out),
  visual layout (visual-brainstorm), or clickable prototypes (html-prototype).
metadata:
  short-description: "Trace a behavior through real code and show the chain in Mermaid"
---

# Code Chain

Explain what already happens in the open project for one named behavior.
Find the entry, follow the real calls, list the hops that change anything,
cite the code, and show the whole path in Mermaid. Do not invent a chain,
edit product files, or turn the question into a redesign.

## Scope and neighbors

| Job | Route |
| --- | --- |
| What existing code does for a click, request, event, or function | Full session below |
| How we should implement or restructure it | `figure-out` |
| Visual direction, layout, tone | `visual-brainstorm` |
| Build UI in the open project | `my-designer` |
| Clickable HTML prototype | `html-prototype` |

If the user asks both “what happens now” and “how should we change it”,
finish the chain first, then hand off to `figure-out` with the traced path.

## Trace the behavior

1. Name the behavior in one line (the click, route, event, error, or
   function the user asked about). Reuse any file, symbol, or URL they
   already supplied. If two plausible entries would produce different
   chains, ask one question; do not merge them.
2. Read [references/trace.md](references/trace.md). Locate the real
   definition, then follow imports and calls only as far as the behavior
   requires. Stay inside the open project.
3. Keep hops that have a consequence: entry, a branch that changes the
   result, a write/IO/network side effect, or the value returned to the
   caller. Skip pass-through getters and logging unless they are the
   question.
4. Read [references/mermaid.md](references/mermaid.md) and draw **one**
   diagram of the whole chain before the hop list. Number hops in the
   diagram to match the list.
5. For each hop: one-line job, a short citation of the real code, and
   what this step changes. Mark unread or inferred edges as assumptions.

Do not edit product files. Do not propose a new architecture unless the
user asked to change it after seeing the chain.

## Reply shape

~~~~markdown
## What happens: <the named behavior>

```mermaid
...
```

## Chain
1. **Entry** — `path` `symbol`
   - What this hop does
   - Why it matters for the behavior
   - citation of the real code
2. ...

## Branches / effects
- Side effects, unread edges, and branches not taken on the main path.
~~~~

Lead with the answer (the diagram and the chain), not a tour of the
search. Finish when the named behavior is covered; do not keep walking
into unrelated helpers.

For compaction: `Reload code-chain; read trace.md before following calls;
mermaid.md before drawing. Cite real hops; do not edit product files.`
