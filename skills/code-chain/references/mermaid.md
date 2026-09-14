# Mermaid for a code chain

Read before drawing. One diagram for the whole named behavior. Extra
diagrams only when a single branch is too dense to share the main figure.

## Pick a diagram

| Shape of the chain | Diagram |
| --- | --- |
| Calls across modules, handlers, or processes | `sequenceDiagram` |
| Branching decisions on one path | `flowchart TD` |
| Explicit state machine | `stateDiagram-v2` |

Prefer `sequenceDiagram` when the question is “who calls whom”. Prefer
`flowchart TD` when the question is “which branch runs”. Do not mix both
for the same hop list.

## Make hops match the list

Number participants or nodes like the Chain section: `1 Entry`, `2
Validate`, `3 Persist`. A reader should map a box in the figure to the
same numbered hop and citation.

Keep labels short. Put the explanation in the hop list, not inside the
node.

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

## Size

Aim for the hops you listed, not the entire module graph. Five to twelve
nodes is enough for most questions. If the chain is one function with no
callees, still draw a tiny flowchart so the entry and return are visible.
