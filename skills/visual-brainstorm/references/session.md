# Session record and recovery

Read when starting or resuming a decision session. Keep one `session.md` in
the session directory created by `scripts/session.py init`. The agent owns
the meaning of decisions; the helper only manages preview files. Do not put
user answers in the record until they actually arrive.

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
```

Checkpoint statuses: `pending`, `waiting`, `confirmed`, `needs-review`,
`deferred`, `skipped`. Only mark a user decision confirmed with conversational
evidence. Record why an item is skipped; record the user's agreement to a
deferral. Preserve old decision meanings instead of rewriting history.

The preview tab manifest (`checkpoints.json`) mirrors these statuses on the
served page. When a status changes here, sync the tab badge with
`session.py mark <session-dir> <checkpoint> <status>`; `session.md` remains
the authoritative decision record.

The server writes the user's latest on-page selection per checkpoint to
`choices.json`. Treat it as preview feedback for resolving what the user
refers to in chat, never as conversational evidence by itself; do not copy it
into the record as a confirmed decision without a chat reply.

After publishing, record the returned revision path before presenting the
question. Read back the current entry: its checkpoint, revision label, source
path, and pending question must agree with the published preview. If publication
succeeds but the record update is interrupted, compare that checkpoint's
`checkpoints/<id>.fragment.html` with the saved revisions and reconcile the
pending question; do not assume the latest file is a confirmed choice.

Recovery: open the known session directory, read this record and the selected
revisions, then check the server using the render-kit procedure. A dead preview
does not lose decisions. A missing/corrupt record is not permission to invent
history: reconstruct only from the conversation and artifacts, and ask about
any decision that cannot be recovered. Never select another session just
because its title matches. A new unrelated task gets a new session directory.

Keep working files outside the project. Preserve source revisions and this
record on completion, pause, or handoff. Stop the server when the user is done
viewing; if leaving a final preview for review, it expires after idle timeout.
Do not bulk-delete old sessions or prune user exports as routine cleanup.
