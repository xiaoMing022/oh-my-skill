# Tracing a real chain

Read before following calls. The chain is evidence from the open project,
not a reconstructed design.

## Find the entry

Start from what the user already named: a symbol, route, button label,
error string, or file. Search for the definition, then confirm it is the
handler that actually runs for that behavior (the route table, listener,
or exported API), not a similarly named helper.

If several entries could match, stop and ask which one. A merged chain
from two handlers is worse than a short question.

## Walk the calls

Read the body. Follow a call when it decides, transforms, writes, or
returns the result the user asked about. Do not tour every import.

Each hop must point to a file and a symbol you opened. If the next step
is another process (HTTP, queue, RPC, subprocess), draw it as a boundary
and say what is sent; do not pretend it is a local function call.

Stop when the named behavior's result is produced, or when the next hop
would be a generic library with no project-specific logic. Say where the
trace stopped.

## What counts as a hop

Include:

- The entry that receives the user action or request
- A branch that changes the outcome (auth, empty, error, feature flag)
- A side effect (store, network, file, job enqueue)
- The value or response handed back

Omit:

- Pure logging and metrics unless that is the question
- Getters that only return a field
- Framework boilerplate that does not change this behavior

Default to the **main path**. Outcome-changing branches belong on the
diagram and in the list; the rest can be one line under Branches.

## Cite, do not dump

Use the host citation format with real line numbers:

```12:18:app/api/save.ts
export async function POST(req: Request) {
  const body = await req.json()
  return saveDraft(body)
}
```

Quote the few lines that do the work. Do not paste the whole file, and
do not rewrite the code as a paraphrase that hides the actual call.

If a hop was inferred (generated code, missing source, opaque binary),
label it `assumed` and say what was not readable.
