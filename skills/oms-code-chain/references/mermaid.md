# Mermaid for a code chain

Read before drawing. Draw the main diagram **after** the hop list, as its
visual index. The main diagram is the **shared spine**. Extra diagrams only
when a branch changes the outcome enough that one figure cannot show it (for
example `--link` vs copy, or a second process).

## Pick a diagram

| Shape of the chain | Diagram |
| --- | --- |
| Calls across modules, handlers, or processes | `sequenceDiagram` |
| Branching decisions on one path | `flowchart TD` |
| Explicit state machine | `stateDiagram-v2` |

Prefer `sequenceDiagram` when the question is “who calls whom”. Prefer
`flowchart TD` when the question is “which branch runs”. Do not mix both
**inside one figure**. A second figure may use the other type if the
asked branch is a decision the spine did not show.

## Make hops match the list

Every main-chain node or numbered message reuses the hop's exact stage name
and number: `1 点击保存`, `2 提交请求`. In a flowchart, number phase nodes like
the numbered chain section. In a sequence diagram, participants are stable actors;
number the relevant messages/notes to match the list. Do not invent a
participant for every step performed by the same actor.

Delete any node that has no matching numbered hop. Branches stay out of the
numbered spine: show them as labeled edges or a separate figure, never as
extra phase numbers.

Keep labels to the stage name. Put data flow and explanation in the hop list,
not inside the node. Optional edge labels may name a flag or payload
(`"--link"`, `"argv"`); they are not a second hop list.

Wrappers that funnel into the same spine can be a single entry node with
a Branch note, not three numbered hops.

## Stay renderable

- Node and participant IDs: camelCase, no spaces (`saveHandler`, not
  `save handler`).
- Labels with spaces, punctuation, or colons: wrap in double quotes.
- Edge labels that contain parentheses or brackets: wrap in quotes.
- No `style`, `classDef`, `click`, or HTML entities.
- No spaces in subgraph IDs; use `subgraph id [Label]`.
- Do not name a node `end`.

Cross-process hops are explicit boundaries (`participant api` then
`participant worker`), not a local arrow that hides the network.
Label network, queue, event, and timer edges with their actual transport or
trigger. Distinguish an async send from its later consumer and a reply from a
new event. Use only syntax supported by the host renderer. Put unknown external
work beyond a labeled boundary; do not draw an invented downstream chain.

## Size

A multi-module overview usually has **5–8 phases**. That is guidance, not a node
quota; actor count in a sequence diagram can differ from phase count. A simple
function needs no diagram unless requested; if requested, draw its actual small
path. Split a dense branch into a separate figure only when it aids the answer.
