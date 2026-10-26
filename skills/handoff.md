# Handoff contract

Use these six fields whenever responsibility passes between skills or an
interrupted task resumes. Each skill embeds the compact contract so installing
one skill alone does not require a sibling or a parent-directory resource.
Keep the field names consistent when editing those copies.

```markdown
## Handoff
Scope: <project/app/client, task boundaries, and actions already authorized>
Confirmed: <user-supplied requirements or approved decisions; evidence refs>
Delegated: <choices entrusted to the agent, actual choices made and rationale; refs>
Pending: <unanswered questions, unconfirmed assumptions, blockers or none>
Evidence: <source paths/symbols, record/preview revisions, freshness and verification limits>
Next action: <receiving skill/workflow and concrete action; continue or wait, with reason>
```

Use `none` or `unknown` where appropriate rather than inventing missing facts.
For a short task this can be six brief lines in the conversation. For an
existing session/design record, update a `Handoff` section there and pass its
path; do not create a second authoritative record. A handoff is not required
for every ordinary response or every internal step.

## Sending

- Preserve project/app identity, output restrictions, and the scope of
  implementation authorization. A preview approval alone does not authorize a
  build, and an already authorized build needs no repeated permission question.
- Keep supplied/approved facts distinct from agent choices. Delegation is
  permission to decide within bounds, not evidence that the user saw and
  selected a particular option. Keep unconfirmed assumptions under `Pending`.
- Reference the actual answer and the option's meaning plus checkpoint/revision
  when relevant; `B` without a version or meaning is insufficient.
- Include source evidence for traced behavior and design authority, with the
  revision or freshness information available. A commit ID alone does not cover
  uncommitted changes. Distinguish static inspection from executed checks.
- State what is ready to continue and which specific unresolved question, if
  any, blocks the next step. Preserve independent work that can proceed.

## Receiving

- Read the supplied record and relevant evidence before asking questions or
  initializing another session. Continue the known session for the same task;
  create a new one only for an unrelated task, a distinct scoped experiment,
  or when reconstruction is necessary and disclosed.
- Revalidate referenced runtime sources when the branch, worktree, files,
  configuration, or line locations changed or freshness is unknown. Reuse
  current evidence; reopen only conclusions affected by changes.
- Carry forward confirmations and delegated authority unless the latest user
  instruction supersedes them. Do not repeat theme selection, intent discovery,
  or a code trace whose evidence is still current.
- Ask only about missing information that changes the next action. Continue
  independent authorized work while an answer is pending.
- If a sibling skill or host feature is unavailable, follow the authorized
  workflow with this record; do not claim an unavailable skill/tool was invoked.

## Example: trace to UI implementation

```markdown
## Handoff
Scope: /repo, apps/admin, Web; fix the save feedback already requested by user.
Confirmed: Keep the current blue theme; user instruction in this conversation.
Delegated: Use the existing inline error pattern; chosen to match adjacent forms.
Pending: none.
Evidence: SaveForm.tsx onSave -> api/settings.ts updateSettings; current working
  files inspected, including local edits; static read only. Existing error
  component: FormError.tsx. No runtime behavior check performed.
Next action: oms-designer — reuse the trace and theme, implement save/error feedback;
  continue within the requested fix scope.
```
