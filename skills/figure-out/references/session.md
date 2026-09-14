# Session record and recovery

Read when starting or resuming a technical decision session. Keep one
`session.md` in the directory created by `scripts/session.py init`. The
agent owns the meaning of decisions; the helper only creates the isolated
directory and checkpoint statuses. Do not put user answers in the record
until they actually arrive.

Working root: `~/.agent-skills/figure-out/`, or the expanded
`AGENT_FIGURE_OUT_DIR`. Keep it outside the project.

```bash
python scripts/session.py init <slug>
python scripts/session.py add <session-dir> <checkpoint-id> --title "..." --status pending
python scripts/session.py mark <session-dir> <checkpoint-id> confirmed
```

Use this compact structure and update it after each answer:

```markdown
# <Task title>
Status: exploring | waiting | planning | executing | complete | paused | handed-off
Scope: <agreed boundaries>
Purpose / constraints:
Assumptions: <distinguish supplied facts from defaults>
Session: <directory>
Current: <checkpoint ID + exact pending question, or none>

## Decision plan
| ID | Question / why it matters | Depends on | Status | Completion evidence |
| --- | --- | --- | --- | --- |
| T1 | ... | — | pending | selected approach ... |

## Approaches and revisions
- T1 / R1: A = <meaning>, B = <meaning>; recommendation and key tradeoff.
- User answer: <quote or faithful summary>; selected <option>;
  rationale / constraints; supersedes <earlier decision if applicable>.

## Confirmed approach
<Only after the in-scope checkpoints are confirmed: the combined direction
the later plan must follow.>

## Plan
<Filled after plan mode. Empty until then.>

## Next actions
<Next checkpoint, plan gate, or execution step.>
Deferred / unresolved: <item, reason, and downstream consequence>.
```

Checkpoint statuses: `pending`, `waiting`, `confirmed`, `needs-review`,
`deferred`, `skipped`. Only mark a user decision confirmed with
conversational evidence. Record why an item is skipped; record the user's
agreement to a deferral. Preserve old decision meanings instead of
rewriting history.

`checkpoints.json` mirrors these statuses. When a status changes here,
sync it with `session.py mark`; `session.md` remains the authoritative
record.

Recovery: open the known session directory, read this record, then
continue the pending checkpoint. A missing/corrupt record is not
permission to invent history: reconstruct only from the conversation and
artifacts, and ask about any decision that cannot be recovered. Never
select another session just because its title matches. A new unrelated
task gets a new session directory.

Keep working files outside the project. Preserve this record on
completion, pause, handoff, or execution. Do not bulk-delete old sessions
as routine cleanup.
