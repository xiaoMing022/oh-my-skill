# Design doc

Read when the work sizes as a project. Write a plain document a talented
builder in the domain could plan from without going back to your partner.

## Cover

- intent and the why
- goals, non-goals, anti-goals
- constraints
- the parts of the how they decided, as they decided them
- what's left to the builder

Choices you made go in as your calls, never as agreed. Anything the
conversation already answered stays answered — do not re-ask it in the
doc.

## Where it goes

- Software repo: default `.oh-my-skills/brainstorming/specs/YYYY-MM-DD-<topic>-design.md`.
  Use an explicit user location or maintained project spec convention instead
  when supplied. The document is committable; commit only under the user's Git
  instructions. This deliverable is not constrained to the scratch-file root.
- Non-software (talk, business, renovation): ask the partner where to
  keep it. Their preference overrides the default.

## Template skeleton

```markdown
# <Topic> design — YYYY-MM-DD

## Intent and why
## Goals / non-goals / anti-goals
## Constraints
## Decided how (theirs)
## My calls (builder to check)
## Left to the builder
```

## After writing

Tell the partner a reviewer will read it first and you may come back
once with a few questions. Then run
[builder-check.md](builder-check.md). Do not hand over the document
until the check is back.
