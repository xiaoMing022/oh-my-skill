# Plan gate and execution

Read when in-scope approach checkpoints are confirmed, deferred, or the
user asks to proceed from the confirmed direction. The plan is a second
gate. Confirmed approaches are inputs to the plan; they are not
permission to edit product files.

## When to enter plan mode

Enter plan mode after the technical direction is settled enough to
schedule work: all in-scope checkpoints confirmed or explicitly deferred,
or the user asks to plan/implement from the current confirmed set.

Do not enter plan mode to explore the original fork. That is still a
figure-out checkpoint. Do not skip this gate because the recommended
approach felt obvious.

## How to enter plan mode

Use the host mechanism that actually switches into a reviewable plan:

- Cursor: `SwitchMode` with `target_mode_id: plan`. Explain that the
  approaches are confirmed and the next deliverable is an implementation
  plan.
- Claude Code and similar: `enter_plan_mode` when that tool exists.
- If no plan-mode tool exists, write the plan in chat as a reviewable
  document and wait. Do not start edits while waiting.

Plan mode is for designing the change. If the host's plan mode is
read-only, stay there until the user approves, then return to the
implementation / agent mode before touching product files.

## What the plan must contain

Derive the plan only from confirmed approaches, explicit deferrals, and
named assumptions. Do not silently revive a rejected option.

Include:

1. Confirmed direction — the chosen approach per checkpoint, in one
   short list.
2. Assumptions and deferred items — what the plan is allowed to decide
   later, and what it must not reopen.
3. Ordered steps — implementation slices with dependency order, not a
   restatement of the architecture essay.
4. Blast radius — files, packages, APIs, data, or operations that change.
5. Risks — migration, compatibility, failure handling, rollback.
6. Verification — how each slice will be checked before calling it done.

The plan should be concrete enough to execute without another
architecture debate. If a leftover fork would change the steps, it is
still a figure-out checkpoint: resolve it before asking for plan
approval.

## Approval and execution

Wait for an explicit plan approval (`按这个计划做`, `执行`, `LGTM`, or
an equivalent). Edits to the plan are a new draft, not approval.

After approval:

1. Set session status to `executing` and record the approved plan in
   `session.md`.
2. Switch back to implementation mode when the host requires it.
3. Execute the approved steps in order. Reuse neighbor skills when the
   remaining work is their job (`my-designer`, `html-prototype`,
   `design-unify`) instead of duplicating them.
4. Do not expand into unplanned refactors. If execution reveals a new
   technical fork, pause, record it, and return to a checkpoint rather
   than improvising a different architecture.

A user request to stop after the plan is approved is a pause, not a
license to keep editing. Finish with what was done, what remains, and
where the session record lives.
