# Tracing a real chain

Read before following calls. The chain is evidence from the open project,
not a reconstructed design.

## Find the entry

Start from what the user already named: a symbol, route, button label,
error string, CLI command, or file. Search for the definition, then
confirm it is the handler that actually runs (the route table, listener,
exported API, or command switch), not a similarly named helper.

**Shared spine.** Several shells, bins, or wrappers that all call the
same function are one behavior. Trace the function they share. Name the
wrappers in Branches instead of asking which shell to follow, and instead
of inventing a merged handler.

**Different chains.** Two unrelated handlers (admin submit vs public
submit) would produce different results. Ask one question; do not merge
them. A combined fictional path is worse than a short question.

## Walk the calls

Read the body. Follow a call when it decides, transforms, writes, or
returns the result the user asked about. Do not tour every import.

Each hop must point to a file and a symbol you opened. If the next step
is another process (HTTP, queue, RPC, subprocess), draw it as a boundary
and say what is sent; do not pretend it is a local function call.

This walk is a **static read** of source. Middleware, generated routes,
and config-driven dispatch may not appear as a direct call; say when the
next hop is selected at runtime and you did not execute it.

Stop when the named behavior's result is produced, or when the next hop
would be a generic library with no project-specific logic. Say where the
trace stopped.

## Trace depth

Use only the phases needed to answer. A simple function or branch may need
2–3 cited steps or fewer and no diagram unless requested. A multi-module trace
usually fits a **5–8 phase overview**, but neither pad a short path nor omit a
critical effect to meet that range. Expand complex branches separately.

One hop is a **phase that changes something**: receive input, decide,
write, or return. Consecutive lines in the same function that only pass
values along are one hop, even if they call a helper.

Include:

- The entry (or the shared spine those entries reach)
- A branch that changes the outcome
- A side effect (store, network, file, job enqueue)
- The value or response handed back

Omit:

- Pure logging and metrics unless that is the question
- Getters that only return a field
- Framework boilerplate that does not change this behavior
- A second hop whose only job is forwarding to the next function

Default to the **main path**. Outcome-changing branches belong on the
diagram or under Branches, not as extra numbered hops.

## Data that crosses a hop

Each hop is one line: the numbered stage name, the source location and symbol,
then what comes in and what leaves (argv, flags, request body, destination
path, return code). Write it as:

```text
**Name** — `path:line` `symbol` · in → out
```

Do not split one hop into separate “does / data / citation” lines. Without the
data, the chain is a list of function names. Keep diagram labels to the same
short stage name.

## Follow-ups

A later question about a flag, wrapper, or branch of the same behavior
reuses the spine already traced when its evidence is current. Check project/
worktree identity and whether relevant source/configuration or line positions
changed since inspection. A commit ID alone misses uncommitted edits. On changes
or unknown freshness, reread the affected files and refresh citations, then
expand only that branch and affected dependencies. Do not repeat unrelated
searches. If there is no reliable old record, say so and reconstruct from source.

## Async and evidence boundaries

Distinguish calls, scheduled callbacks, event publication/delivery, state
subscriptions, and network requests. Name both the producer and the observed
consumer when readable. Describe delay, gating, cleanup, retry, and ordering
only where the code establishes them. A queued event or started request is not
proof of delivery, persistence, or completion. Explain what an early return,
rejection, cancellation, or stale result does when it changes the asked outcome.

Use these evidence labels where uncertainty matters (not on every trivial line):

| Label | Meaning |
| --- | --- |
| `source-confirmed` | Opened code directly establishes the call, transformation, or condition; this does not mean it was executed. |
| `configuration-dependent` | The opened registration/configuration selects a path at runtime; name the condition and alternatives that matter. |
| `unread boundary` | External service, missing source, generated output, or binary prevents further tracing; state the last verified payload/contract and stop. |

An interpretation beyond those facts is an explicit unconfirmed assumption,
never an invented handler or return value. Carry source evidence and limits to
`oms-process-docs` when the user asks for a maintained workflow reference.

## Cite, do not dump

Use the host's supported clickable source citation with the real path and line
number, and name the relevant symbol. Prefer a concise explanation with its
citation; quote a few source lines only when they clarify a condition or data
transformation. Do not dump files or require a host-specific code-fence syntax.
On a saved report, use project-relative source links where supported. Never
reuse stale line numbers after edits without checking them.
