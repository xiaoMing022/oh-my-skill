# Design authority, storage, and continuity

Read before creating or resuming a design baseline. The goal is a portable
product and a recoverable design process, with one runtime authority per role.

## Source precedence

Use the latest explicit user instruction within the task's scope. Otherwise
prefer the target app's maintained design documentation and active shared theme,
then its established component/screen patterns. External records and previews
are evidence of earlier choices, not permission to overwrite newer project code.
If docs and active code disagree, inspect which source is intended/current;
record the conflict and clarify only when it materially affects the task.

A theme may live in a shared package, provider configuration, CSS variables,
utility theme, CSS-in-JS theme, or an app stylesheet. Trace the actual import or
provider path. Finding a token file that no rendered screen consumes is not
proof of a working design system. Do not search only for a file named global.css.

## Three different kinds of file

| Material | Home and lifecycle |
| --- | --- |
| Visual experiments and rejected variants | `visual-brainstorm` session outside the project; preserve references, never import its renderer or styles into production. |
| Decisions, rationale, pending questions | Existing project design docs when maintained there; otherwise external `design.md` below. It points to runtime sources rather than duplicating their entire contents. |
| Styles and component code required to render the app | Inside the project or its declared shared package, using its existing conventions; versioned and available to ordinary builds and teammates. |

Keeping all runtime styles outside the project makes builds depend on one
machine. Adding a second global stylesheet for the agent creates competing
sources and cascade problems. Prefer to reuse the current authority; introduce
one only when no suitable mechanism exists. Do not add a reset, provider, or
app-wide selectors to accomplish a small local feature.

If the user explicitly forbids product-file changes, remain in the external
preview/plan stage. Explain that integrating working UI requires changing its
runtime sources; do not make hidden runtime links or claim integration happened.

## External working record

Use this only when durable design notes do not already have a project home.
A read-only review or tiny correction can use the existing contract without
creating new records. For new baselines and multi-page work, locate the record:

```bash
python3 <skill-dir>/scripts/design_context.py <project-root> --app <relative-app-path>
```

Use the repo/workspace root plus the explicit app root; omit `--app` for a
single-app project. The command is read-only by default. Add `--init` to create
the external directory and starter record when needed. It uses
`AGENT_DESIGN_CONTEXTS_DIR` or `~/.agent-skills/design-contexts/`, resolved outside
the project. It keys records by canonical project/app paths, so same-named apps
in unrelated repos are isolated, symlink aliases agree, and separate worktrees
remain separate. It prints the paths and existence state; it does not infer
that the saved theme still matches current source code.

Before using a record, verify its project/app identity and read its referenced
runtime files. If the repo moved, the cache is missing, or a branch changed its
theme, reconstruct from project sources and conversation evidence. Import an old
record only after checking it belongs to the intended project; never pick by
folder title alone. The helper does not auto-copy records across worktrees.

Use one writer per app record. When updating `design.md`, write a sibling
temporary file, read it back, and atomically replace the record; retain earlier
confirmed choices in its history. Missing or partial initialization is reported
as an error, not silently adopted. If external storage is unavailable, continue
using project sources and conversation state, disclose the persistence limit,
and do not write scratch files into the repo as an unannounced fallback.

Keep the working record short:

```markdown
# <App> design contract
Status: proposed | confirmed | delegated | implementing | paused | complete
Project/app: <canonical roots>
Task/scope: <requested surfaces, not every app in a monorepo>
Visual thesis: <task-based principle>
Evidence: <user instruction or chosen visual checkpoint/revision>
Runtime authority: <actual theme/provider/package paths and import location>
Foundation rules: <semantic roles, type hierarchy, spacing/density, surfaces>
Shared grammar: <component sources and approved variants>
Responsive/state rules: <relevant behavior, modes, motion>
Exceptions/assumptions: <scope, reason, not silently confirmed>
Verification: <what was actually run/seen; limitations>
Pending: <exact unresolved question or none>
Next action: <specific next implementation or decision step>
History: <prior decision, change reason, affected consumers>
```

For changes to shared themes, record the affected app/component consumers and
verify them within scope. Do not mirror a full CSS file in this record. Runtime
values are read from their authoritative source, preventing two token catalogs
from drifting apart. Keep cache paths out of product UI, source imports, package
scripts, and committed machine-specific configuration.

If the team wants a shareable design guide, use its documentation convention
and relative source paths; migrate useful decisions there without creating a
second active contract. Keep external records as references or mark superseded.
