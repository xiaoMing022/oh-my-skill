# Session record and recovery

Read when starting or resuming a decision session. Keep one `session.md`
in the session directory created by `scripts/session.py init` under
`<project-root>/.oh-my-skills/visualization/`. The agent owns the meaning of
decisions; the helper only manages preview files. Do not put user
answers in the record until they actually arrive.

Use this compact structure and update it after each answer and publication:

```markdown
# <Task title>
Status: exploring | waiting | reviewing | complete | paused | handed-off
Scope: full-session | single-fork | explainer; <agreed boundaries>
Purpose / audience / platform:
Constraints and assumptions: <distinguish supplied facts from defaults>
Preview: <session directory, current revision, URL if running>
Current: <checkpoint ID + revision + exact pending question, or none>

## Decision plan
| ID | Question / why it matters | Depends on | Status | Completion evidence |
| --- | --- | --- | --- | --- |
| D1 | ... | — | pending | selected option at revision ... |

## Decisions and revisions
- D1 / <revision>: A = <meaning>, B = <meaning>; recommendation and tradeoff.
- User answer: <quote or faithful summary>; selected <revision / option>;
  rationale / constraints; supersedes <earlier decision if applicable>.

## Next actions
<Next checkpoint, or ordered prototype/implementation tasks after handoff.>
Deferred / unresolved: <item, reason, and downstream consequence>.

## Handoff (when transferring or resuming work)
Scope: <project/app/client, boundaries, actions already authorized>
Confirmed: <supplied requirements or approved decisions, with refs>
Delegated: <entrusted choices, actual choices made and rationale, with refs>
Pending: <unanswered questions, unconfirmed assumptions, blockers or none>
Evidence: <source paths/symbols, record/preview revisions, freshness and check limits>
Next action: <receiving skill/workflow, concrete step, continue or wait and why>
```

Checkpoint statuses: `pending`, `waiting`, `confirmed`, `needs-review`,
`deferred`, `skipped`. Only mark a user decision confirmed with
conversational evidence — a chat reply. On-page buttons are visual only
and confirm nothing; there is no `choices.json`. Record why an item is
skipped; record the user's agreement to a deferral. Preserve old
decision meanings instead of rewriting history.

The session manifest (`checkpoints.json`) mirrors these statuses in
`index.html` badges. When a status changes here, sync it with
`session.py mark <session-dir> <checkpoint> <status>`; `session.md`
remains the authoritative decision record.

After publishing, record the returned revision label before presenting
the question. Read back the current entry: its checkpoint, revision
label, source path, and pending question must agree with the published
preview. If publication succeeds but the record update is interrupted,
compare that checkpoint's `checkpoints/<id>.fragment.html` with the
saved revisions and reconcile the pending question; do not assume the
latest file is a confirmed choice.

Recovery: open the known session directory, read this record and the
selected revisions, then re-serve with `scripts/serve.py` if the preview
is down. A dead preview does not lose decisions. A missing/corrupt
record is not permission to invent history: reconstruct only from the
conversation and artifacts, and ask about any decision that cannot be
recovered. Never select another session just because its title matches.
A new unrelated task gets a new session directory (`session.py list`
shows existing ones).

These files may be committed: `session.md`, `checkpoints.json`,
`checkpoints/`, `revisions/`. Never commit `serve.json`. Cleanup is
manual only (`session.py prune ... --force`); do not bulk-delete old
sessions or prune user exports as routine cleanup.
