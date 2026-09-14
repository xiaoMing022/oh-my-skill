# Comparing and evaluating approaches

Read before presenting options for a checkpoint. The user is choosing an
implementation direction, not a slogan.

## What counts as a task

A checkpoint is a requirement slice with a real fork: system boundary,
data model, consistency, failure handling, integration, or a hard
algorithm. Sequential file edits, ticket-sized chores, and visual layout
are not checkpoints here.

If several requested features share one fork, fold them into that
checkpoint. If a later step is fully determined by an earlier choice, it
belongs in the plan, not as a new comparison.

## Writing the options

Show 2-3 approaches that would actually work under the stated constraints.
They must differ in structure or operational consequences, not in
wording. Ground each option in the current codebase when one exists:
name the modules, stores, or boundaries it would touch.

For each option use this shape:

```markdown
**A. <short name>**
- How it works here: <mechanism in this system, not a generic pattern>
- Fits / changes: <what can stay; what must move>
- Tradeoffs: <complexity, blast radius, operability>
- Risks: <failure modes, migration, irreversibility>
```

Then a compact evaluation of the set, then one recommendation:

```markdown
**Evaluation**
| Criterion | A | B | C |
| Fit with current code | ... | ... | ... |
| Blast radius | ... | ... | ... |
| Failure modes | ... | ... | ... |
| Reversibility | ... | ... | ... |

**Recommend <label>.** <one to three sentences: why it wins here, what it
gives up, and when a different option would be better.>
```

Use qualitative judgments (`high` / `medium` / `low`, or a short phrase).
Do not invent numeric scores. Drop a criterion that does not apply rather
than filling it with noise.

## Honest comparison

- Prefer the smallest change that satisfies the constraint. A greenfield
  rewrite is an option only when the existing structure cannot absorb the
  work, and that cost must be explicit.
- Do not pad the list with a strawman. Two strong options beat three
  where the third is “do nothing” unless doing nothing is a real choice.
- If the user already constrained the approach, do not re-open it as an
  option set. Record it as supplied.
- Diagrams (Mermaid) help when the fork is about structure or data flow.
  Keep them small and paired with the same A/B/C labels. A diagram does
  not replace the evaluation.

## Recommendation discipline

Recommend one option every time a comparison is shown, even when the
tradeoff is close. Say what would change the recommendation. “It depends”
is not a recommendation; name the default and the condition.

The recommendation is advice. It becomes the decision only when the user
confirms it in conversation (`A`, `选你推荐的`, or an equivalent).
