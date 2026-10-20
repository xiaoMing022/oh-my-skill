# Skill outputs — working files and deliverables

Put skill-managed working files under `<project-root>/.oh-my-skills/` by
default. This rule covers scratch notes, session state, previews, and local
design records. It does not relocate product source or requested documentation.
Write those deliverables in the project's established locations within the
user's authorized scope; no extra permission is needed just because they are
outside `.oh-my-skills/`.

## Locations for all five skills

| Skill | Working files | User-facing deliverables |
| --- | --- | --- |
| `brainstorming` | `brainstorming/sessions/<slug>-*/` for `session.md` and `checkpoints.json` | Default software design doc: `brainstorming/specs/YYYY-MM-DD-<topic>-design.md`; an explicit user/project documentation convention may override it. For non-software work, use the agreed location. |
| `visualization` | `visualization/<slug>/` for session, checkpoints, revisions, index, and server metadata | Preview HTML and decision record remain in that session; requested exports go to the agreed output location. |
| `designer` | `designer/contexts/<hash>/design.md` only when no maintained design-doc home exists; experiments belong to `visualization` | Runtime themes, components, and screens belong in the app's native source locations; maintained design contracts belong in existing project design docs. |
| `code-chain` | None required for a normal explanation; optional scratch notes under `code-chain/<slug>/` | Cited explanation and optional Mermaid in chat by default; save a requested report in the agreed documentation location. Do not edit product code. |
| `process-docs` | None required; optional scratch notes under `process-docs/<slug>/` | Workflow/prompt reference docs and necessary index links belong in the existing documentation tree; use a requested location or choose and state a suitable project docs location. Do not edit product code. |

Working paths in the table are relative to `.oh-my-skills/`. A read-only
explanation or tiny change does not require a new directory, session, or record.
Handoffs reuse the current record or conversation; see [handoff.md](handoff.md).

## Persistence and scope

- Brainstorming specs and visualization HTML/decision records are committable;
  this is not an instruction to commit automatically. Follow the user's Git
  instructions.
- Keep brainstorming session state and designer fallback contexts local and
  ignored. Optional trace/doc scratch directories are local too. Check the
  target project's ignore rules before staging; this repository's `.gitignore`
  does not configure other projects. Prefer existing local exclude rules for
  scratch paths and do not change shared ignore policy without task scope.
- Never commit `serve.json` or `serve.stale-*.json`. Do not bulk-delete old
  sessions or prune user exports as routine cleanup.
- Product builds must not import preview assets, local contexts, or an agent
  cache. Runtime sources stay in the project or a declared shared package.
- Reuse an explicit user-supplied working/output location. Otherwise use the
  default working root; ask before introducing an unrelated location. This
  does not add an approval gate for authorized source/doc changes.
- If the user forbids all project-file writes, that includes `.oh-my-skills/`
  inside the project. Use an available host preview or a permitted temporary
  location and disclose persistence limits. A restriction on product source
  alone still allows authorized working previews.

`OH_MY_SKILLS_DIR` changes the working root: relative values resolve under the
project root; absolute values are used as-is. Legacy
`AGENT_BRAINSTORMING_DIR` / `AGENT_DESIGN_CONTEXTS_DIR` override the corresponding
skill's working location when set. These settings do not move product source,
existing docs, or explicitly requested exports. Treat configured locations as
intentional within the host's filesystem permissions; do not ask again merely
because they differ from the default.
