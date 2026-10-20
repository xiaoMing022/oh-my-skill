# Session record and recovery

Read when starting or resuming a brainstorming session. Keep one
`session.md` in the directory created by `scripts/session.py init`. The
agent owns the meaning of decisions; the helper only creates the isolated
directory and checkpoint statuses. Do not put user answers in the record
until they actually arrive.

Working root: `<project-root>/.oh-my-skills/brainstorming/sessions/` (override with `OH_MY_SKILLS_DIR`; legacy `AGENT_BRAINSTORMING_DIR` still wins when set). Keep all working files under `.oh-my-skills/`.

```bash
python scripts/session.py init <slug>
python scripts/session.py add <session-dir> <checkpoint-id> --title "..." --status pending
python scripts/session.py mark <session-dir> <checkpoint-id> confirmed
python scripts/session.py status <session-dir> planning
```

Use this compact structure and update it after each answer:

```markdown
# <Topic>
Status: exploring | waiting | planning | executing | complete | paused | handed-off
Size: quick | small | project (or undecided)
Scope: <agreed boundaries>
Purpose / why:
Success: <what success looks like to them>
Assumptions: <distinguish supplied facts from defaults>
Session: <directory>
Design doc: <path or none>
Gate: pending | approved | opted-out
Current: <exact pending question, or none>

## Discovery areas
| ID | Area / why it matters | Status |
| --- | --- | --- |
| D1 | kind + specialness | pending |
| D2 | goals / non-goals / anti-goals | pending |

## Playback
- <chunk summary>; guess vs theirs; what's still missing.

## Confirmed direction
<Only after sizing + approval: the direction the later plan must follow.>

## Next actions
<Next question, sizing, doc, check, gate, or execution step.>
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
conversational evidence. Preserve old meanings instead of rewriting
history. Checkpoints here track discovery areas, not A/B option
comparisons — keep them as a flat discovery list, not an options matrix.

`checkpoints.json` mirrors these statuses. When a status changes here,
sync it with `session.py mark`; `session.md` remains the authoritative
record.

Recovery: open the known session directory, read this record, then
continue the pending question. A missing/corrupt record is not
permission to invent history: reconstruct only from the conversation and
artifacts, and ask about any decision that cannot be recovered. Never
select another session just because its title matches. A new unrelated
topic gets a new session directory.

Keep working files under `.oh-my-skills/`. Preserve this record on
completion, pause, handoff, or execution. Do not bulk-delete old sessions
as routine cleanup.
