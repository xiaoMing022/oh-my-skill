# oh-my-skills

Cross-agent skills for **oms-brainstorming**, **oms-visualization**, **oms-designer**, **oms-code-chain**, and **oms-process-docs**. Installed skills keep the `oms-` prefix so they do not collide with same-named skills from other sources. Invoke them as `/oms-code-chain`, `/oms-designer`, and so on; the shorter names (`add code-chain`) work only as installer aliases.

First-class install targets include **Codex**, **OpenCode**, **Hermes**, **WorkBuddy**, and **Pi**, plus Grok, Claude Code, Cursor, Gemini / Antigravity, Copilot, Roo, Windsurf, and any agent that reads Agent Skills (`SKILL.md`).

| Skill                                         | What it does                                                                                      |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| [oms-visualization](skills/oms-visualization/) | Plan visual decisions, compare options, confirm across rounds, and retain resumable previews; also charts, maps, and labs |
| [oms-brainstorming](skills/oms-brainstorming/) | Brainstorm before creative work: uncover goals with one-question-at-a-time conversation, play back, size, write a design doc with approval gate |
| [oms-code-chain](skills/oms-code-chain/) | Trace what existing code does; cite meaningful phases and data, with Mermaid when useful or requested |
| [oms-process-docs](skills/oms-process-docs/) | Turn source code into concise Chinese workflow and prompt references for APIs, triggers, outcomes, and failure paths |
| [oms-designer](skills/oms-designer/) | Design and build interaction UI for Web and mobile/mini-program/desktop clients in one design language; contract + native tokens; a subject-specific theme fork when the baseline is missing, not a generic template |

Requires **Node.js 18+** to install. Preview servers need **python3**.

`oms-designer` reuses each client's active theme and shared components under one
design language with per-client adaptation (Web, mobile, mini-program,
desktop). If no usable design baseline exists, it uses `oms-visualization`
for one theme choice before implementation. A new direction comes from the
subject's audience and job, with task-appropriate hierarchy and expressive
emphasis when useful. Decisions live in a short
design contract that points to runtime sources; production styles remain
in each client's native theme source so builds do not depend on an
agent's local cache. An external `design.md` working record is only used
when the project has no design-doc home. Broad rebrands are handled by
`oms-designer` itself within the authorized scope.

`oms-brainstorming` is for 头脑风暴: uncover what to build and why before
anything gets built, in software or out of it. When intent is settled,
decide the remaining technical approach inline in plan mode and hand UI
work to `oms-designer` with the approved direction.

`oms-code-chain` traces a named behavior through the open project: real
entry, cited steps sized to the question, and Mermaid when useful or requested. It explains
what already happens; it does not choose a new design. UI changes traced
this way hand off to `oms-designer` with the traced path.

`oms-process-docs` turns real code into concise Chinese workflow and prompt references, with API inputs and responses, trigger rules, visible copy, and failure behavior.


---

## Install

The unscoped name `oh-my-skills` is already taken on npm. Use the scoped package, or install from GitHub.

### npm / npx

```bash
# Interactive install: pick skills and agents in the terminal
npx @lxy10086/oh-my-skills add

# Skip prompts; install every skill into detected agents
npx @lxy10086/oh-my-skills add --all -y

# One skill, selected agents
npx @lxy10086/oh-my-skills add oms-visualization --agent grok,claude,cursor

# Short aliases still work when unambiguous
npx @lxy10086/oh-my-skills add visualization --agent grok,claude,cursor

# Codex / OpenCode / Hermes / WorkBuddy / Pi
npx @lxy10086/oh-my-skills add --all --agent codex,opencode,hermes,workbuddy,pi

# Copy into the current project (committed with the repo)
npx @lxy10086/oh-my-skills add oms-designer --project
```

In a real terminal, `add` without `--agent` prints a pixel banner, then a checkbox list. Detected agents are pre-checked. Space toggles, arrow keys move, `a` selects all, Enter confirms. Pass `-y` or `--agent` to skip the picker (CI / scripts).

### Agent Skills CLI

The repo layout is `skills/<name>/SKILL.md`, so the ecosystem installer works too:

```bash
npx skills add xiaoMing022/oh-my-skill --skill oms-visualization -g
npx skills add xiaoMing022/oh-my-skill --all -g
```

### From a local clone

```bash
git clone https://github.com/xiaoMing022/oh-my-skill.git
cd oh-my-skill
./install.sh
# or: node bin/cli.js add --all --link
```

`--link` points agent directories at this checkout so skill edits apply immediately.

---

## Commands

```bash
npx @lxy10086/oh-my-skills list
npx @lxy10086/oh-my-skills agents
npx @lxy10086/oh-my-skills add              # interactive picker
npx @lxy10086/oh-my-skills add <name...> [--all] [--agent <ids>] [--project] [-y]
npx @lxy10086/oh-my-skills remove <name...> [--all] [--agent <ids>]
npx @lxy10086/oh-my-skills update
npx @lxy10086/oh-my-skills info oms-visualization
npx @lxy10086/oh-my-skills doctor
```

| Option                | Meaning                                                                                                                                                                                   |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--all`             | Every skill in the package                                                                                                                                                                |
| `-a, --agent <ids>` | `codex`, `opencode`, `hermes`, `workbuddy`, `pi`, `grok`, `claude`, `cursor`, `gemini`, `antigravity-cli`, `copilot`, `roo`, `windsurf`, `agents`, or `all` |
| `-p, --project`     | Write into the current workspace (copies files)                                                                                                                                           |
| `--copy`            | Copy instead of symlink (global installs default to symlink)                                                                                                                              |
| `--link`            | Symlink to this package directory (development)                                                                                                                                           |
| `--force`           | Replace existing files                                                                                                                                                                    |
| `--dry-run`         | Print actions without writing                                                                                                                                                             |
| `-y, --yes`         | Skip prompts; install to detected agents                                                                                                                                                  |

Global installs copy skills into `~/.local/share/oh-my-skills`, then symlink from there. That survives `npx` cache cleanup. `--project` copies into the repo so teammates do not need the store.

### Uninstall

```bash
npx @lxy10086/oh-my-skills remove oms-visualization
npx @lxy10086/oh-my-skills remove --all --agent cursor
```

---

## Agent paths (skills install via CLI)

Interactive `add` lets you tick agents; detected ones start checked. `remove` and `-y` still default to detected agents plus `~/.agents/skills`. Use `--agent all` to create every known path.

| Agent                    | Global                                             | Project              |
| ------------------------ | -------------------------------------------------- | -------------------- |
| Universal / Cline        | `~/.agents/skills`                               | `.agents/skills`   |
| Codex                    | `~/.codex/skills`                                | `.codex/skills`    |
| OpenCode                 | `~/.config/opencode/skills`                      | `.opencode/skills` |
| Hermes                   | `$HERMES_HOME/skills` or `~/.hermes/skills`    | —                   |
| WorkBuddy                | `~/.workbuddy/skills`                            | `.agents/skills`   |
| Pi                       | `~/.pi/agent/skills`                             | `.pi/skills`       |
| Grok                     | `~/.grok/skills`                                 | `.grok/skills`     |
| Claude Code              | `~/.claude/skills`                               | `.claude/skills`   |
| Cursor                   | `~/.cursor/skills`                               | `.cursor/skills`   |
| Gemini / Antigravity IDE | `~/.gemini/config/plugins/oh-my-skills`          | —                   |
| Antigravity CLI          | `~/.gemini/antigravity-cli/plugins/oh-my-skills` | —                   |
| GitHub Copilot           | `~/.copilot/skills`                              | `.github/skills`   |
| Roo Code                 | `~/.roo/skills`                                  | `.roo/skills`      |
| Windsurf                 | `~/.codeium/windsurf/skills`                     | `.windsurf/skills` |

---

## Plugin & marketplace mechanisms

**Skills** (`SKILL.md`) are the portable unit. **Plugins / marketplaces** are how some hosts *distribute* a bundle of skills (and sometimes hooks / MCP). This repo ships both: `npx @lxy10086/oh-my-skills add` for skill dirs, and native manifests where the host has a real plugin system.

| Host                                        | Mechanism                                                          | Manifest in this repo                                               | How to install as plugin                                                                                  |
| ------------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| **Claude Code**                       | Plugin + marketplace                                               | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | `/plugin marketplace add xiaoMing022/oh-my-skill` then `/plugin install oh-my-skills@oh-my-skills`    |
| **Codex**                             | Plugin + marketplace                                               | `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json` | `codex plugin marketplace add xiaoMing022/oh-my-skill` then `/plugins` (or install `oh-my-skills`)  |
| **Grok Build**                        | Plugin + marketplace                                               | `.grok-plugin/marketplace.json`                                   | `grok plugin marketplace add xiaoMing022/oh-my-skill` then `grok plugin install oh-my-skills --trust` |
| **Gemini / Antigravity**              | Plugin package                                                     | root`plugin.json` (`$schema` = Antigravity)                     | `npx @lxy10086/oh-my-skills add --agent gemini,antigravity-cli`                                         |
| **OpenCode**                          | Skills dirs*(plugins here are JS/TS modules, not skill bundles)* | —                                                                  | `npx @lxy10086/oh-my-skills add --agent opencode`                                                       |
| **Hermes**                            | Skills dirs (+ Skills Hub)                                         | —                                                                  | `npx @lxy10086/oh-my-skills add --agent hermes`                                                         |
| **WorkBuddy**                         | Skills dirs                                                        | —                                                                  | `npx @lxy10086/oh-my-skills add --agent workbuddy`                                                      |
| **Pi**                                | Skills dirs                                                        | —                                                                  | `npx @lxy10086/oh-my-skills add --agent pi`                                                             |
| **Cursor / Copilot / Roo / Windsurf** | Skills dirs                                                        | —                                                                  | `npx @lxy10086/oh-my-skills add --agent cursor,copilot,…`                                              |

```bash
# Universal skills path (works across most hosts that read Agent Skills)
npx @lxy10086/oh-my-skills add --all -y

# Explicit skills into the five you care about most
npx @lxy10086/oh-my-skills add --all --agent codex,opencode,hermes,workbuddy,pi
```

OpenCode’s “plugin” system is **executable JS/TS hooks/tools**, not a `SKILL.md` marketplace. Hermes / WorkBuddy / Pi likewise consume **skills folders**, not Claude/Codex-style plugin packages. For those hosts, the supported mechanism is the skills install above.

---

## Layout

```text
oh-my-skills/
├── package.json
├── plugin.json                 # Gemini / Antigravity plugin manifest
├── .claude-plugin/             # Claude Code plugin + marketplace
├── .codex-plugin/              # Codex plugin manifest
├── .agents/plugins/            # Codex marketplace catalog
├── .grok-plugin/               # Grok marketplace
├── bin/cli.js                  # npx @lxy10086/oh-my-skills
└── skills/
    ├── oms-visualization/
    ├── oms-brainstorming/
    ├── oms-code-chain/
    ├── oms-designer/
    ├── oms-process-docs/
    ├── outputs.md              # working files vs project deliverables
    └── handoff.md              # shared six-field handoff contract
```

Skill working files default to `<project>/.oh-my-skills/` — see
[`skills/outputs.md`](skills/outputs.md) for all five skills. Product code and
requested documentation use the project's normal source/doc locations within
the authorized task. Small corrections and chat explanations need no new session.
Design specs and visualization previews are committable; session state, fallback
contexts, and server metadata should stay local. Check the target project's
ignore rules; this checkout's rules do not configure installed projects.
`OH_MY_SKILLS_DIR` changes the working root; legacy `AGENT_*` overrides retain
precedence for their corresponding skill. Neither moves runtime source or docs.

[`skills/handoff.md`](skills/handoff.md) defines the shared six-field handoff:
scope, confirmed decisions, delegated choices, pending questions/assumptions,
evidence, and next action. Each skill embeds the compact format so an individual
installation is self-contained. Reuse current evidence and existing sessions,
recheck changed sources, and carry forward the user's authorization.

`oms-designer` chooses a workflow for local fixes, page additions, new baselines,
staged migrations, or additional clients; platform and migration guidance loads
only when needed. `oms-code-chain` sizes the explanation to the actual behavior,
uses diagrams when useful/requested, and distinguishes async/configuration paths
from directly evidenced calls.
