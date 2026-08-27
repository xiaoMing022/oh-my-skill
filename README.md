# oh-my-skills

Cross-agent skills for **visual brainstorming**, **clickable HTML prototypes**, and **design unify**.

First-class install targets include **Codex**, **OpenCode**, **Hermes**, **WorkBuddy**, and **Pi**, plus Grok, Claude Code, Cursor, Gemini / Antigravity, Copilot, Roo, Windsurf, and any agent that reads Agent Skills (`SKILL.md`).

| Skill | What it does |
| --- | --- |
| [visual-brainstorm](skills/visual-brainstorm/) | See-and-pick UI direction: 2–3 mid-fidelity options on a local port; also charts, maps, and labs |
| [html-prototype](skills/html-prototype/) | PRD / Feishu doc / screenshot → clickable HTML prototype, preview, optional export |
| [design-unify](skills/design-unify/) | Inventory the project's UI stack, confirm a baseline, plan if large, then unify styles |

Requires **Node.js 18+** to install. Preview servers need **python3**.

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
npx @lxy10086/oh-my-skills add visual-brainstorm --agent grok,claude,cursor

# Codex / OpenCode / Hermes / WorkBuddy / Pi
npx @lxy10086/oh-my-skills add --all --agent codex,opencode,hermes,workbuddy,pi

# Copy into the current project (committed with the repo)
npx @lxy10086/oh-my-skills add html-prototype --project
```

In a real terminal, `add` without `--agent` prints a pixel banner, then a checkbox list. Detected agents are pre-checked. Space toggles, arrow keys move, `a` selects all, Enter confirms. Pass `-y` or `--agent` to skip the picker (CI / scripts).

### Agent Skills CLI

The repo layout is `skills/<name>/SKILL.md`, so the ecosystem installer works too:

```bash
npx skills add xiaoMing022/oh-my-skill --skill visual-brainstorm -g
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
npx @lxy10086/oh-my-skills info visual-brainstorm
npx @lxy10086/oh-my-skills doctor
```

| Option | Meaning |
| --- | --- |
| `--all` | Every skill in the package |
| `-a, --agent <ids>` | `codex`, `opencode`, `hermes`, `workbuddy`, `pi`, `grok`, `claude`, `cursor`, `gemini`, `antigravity-cli`, `copilot`, `roo`, `windsurf`, `agents`, or `all` |
| `-p, --project` | Write into the current workspace (copies files) |
| `--copy` | Copy instead of symlink (global installs default to symlink) |
| `--link` | Symlink to this package directory (development) |
| `--force` | Replace existing files |
| `--dry-run` | Print actions without writing |
| `-y, --yes` | Skip prompts; install to detected agents |

Global installs copy skills into `~/.local/share/oh-my-skills`, then symlink from there. That survives `npx` cache cleanup. `--project` copies into the repo so teammates do not need the store.

### Uninstall

```bash
npx @lxy10086/oh-my-skills remove visual-brainstorm
npx @lxy10086/oh-my-skills remove --all --agent cursor
```

---

## Agent paths (skills install via CLI)

Interactive `add` lets you tick agents; detected ones start checked. `remove` and `-y` still default to detected agents plus `~/.agents/skills`. Use `--agent all` to create every known path.

| Agent | Global | Project |
| --- | --- | --- |
| Universal / Cline | `~/.agents/skills` | `.agents/skills` |
| Codex | `~/.codex/skills` | `.codex/skills` |
| OpenCode | `~/.config/opencode/skills` | `.opencode/skills` |
| Hermes | `$HERMES_HOME/skills` or `~/.hermes/skills` | — |
| WorkBuddy | `~/.workbuddy/skills` | `.agents/skills` |
| Pi | `~/.pi/agent/skills` | `.pi/skills` |
| Grok | `~/.grok/skills` | `.grok/skills` |
| Claude Code | `~/.claude/skills` | `.claude/skills` |
| Cursor | `~/.cursor/skills` | `.cursor/skills` |
| Gemini / Antigravity IDE | `~/.gemini/config/plugins/oh-my-skills` | — |
| Antigravity CLI | `~/.gemini/antigravity-cli/plugins/oh-my-skills` | — |
| GitHub Copilot | `~/.copilot/skills` | `.github/skills` |
| Roo Code | `~/.roo/skills` | `.roo/skills` |
| Windsurf | `~/.codeium/windsurf/skills` | `.windsurf/skills` |

---

## Plugin & marketplace mechanisms

**Skills** (`SKILL.md`) are the portable unit. **Plugins / marketplaces** are how some hosts *distribute* a bundle of skills (and sometimes hooks / MCP). This repo ships both: `npx @lxy10086/oh-my-skills add` for skill dirs, and native manifests where the host has a real plugin system.

| Host | Mechanism | Manifest in this repo | How to install as plugin |
| --- | --- | --- | --- |
| **Claude Code** | Plugin + marketplace | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | `/plugin marketplace add xiaoMing022/oh-my-skill` then `/plugin install oh-my-skills@oh-my-skills` |
| **Codex** | Plugin + marketplace | `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json` | `codex plugin marketplace add xiaoMing022/oh-my-skill` then `/plugins` (or install `oh-my-skills`) |
| **Grok Build** | Plugin + marketplace | `.grok-plugin/marketplace.json` | `grok plugin marketplace add xiaoMing022/oh-my-skill` then `grok plugin install oh-my-skills --trust` |
| **Gemini / Antigravity** | Plugin package | root `plugin.json` (`$schema` = Antigravity) | `npx @lxy10086/oh-my-skills add --agent gemini,antigravity-cli` |
| **OpenCode** | Skills dirs *(plugins here are JS/TS modules, not skill bundles)* | — | `npx @lxy10086/oh-my-skills add --agent opencode` |
| **Hermes** | Skills dirs (+ Skills Hub) | — | `npx @lxy10086/oh-my-skills add --agent hermes` |
| **WorkBuddy** | Skills dirs | — | `npx @lxy10086/oh-my-skills add --agent workbuddy` |
| **Pi** | Skills dirs | — | `npx @lxy10086/oh-my-skills add --agent pi` |
| **Cursor / Copilot / Roo / Windsurf** | Skills dirs | — | `npx @lxy10086/oh-my-skills add --agent cursor,copilot,…` |

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
    ├── visual-brainstorm/
    ├── html-prototype/
    └── design-unify/
```
