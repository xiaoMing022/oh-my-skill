import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { c } from './style.js';
import { printBanner } from './banner.js';
import { shouldPrompt, promptMultiSelect, buildSkillChoices } from './prompt.js';

export { c };

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const PKG_ROOT = path.resolve(__dirname, '..');
export const PLUGIN_DIRNAME = 'oh-my-skills';

export const AGENTS = {
  agents: {
    id: 'agents',
    name: 'Universal Agent Skills',
    aliases: ['universal', 'standard', 'cline'],
    type: 'skill',
    always: true,
    global: (home) => path.join(home, '.agents', 'skills'),
    project: (cwd) => path.join(cwd, '.agents', 'skills'),
    detect: () => true,
  },
  grok: {
    id: 'grok',
    name: 'Grok',
    aliases: ['grok-code', 'xai'],
    type: 'skill',
    global: (home) => path.join(home, '.grok', 'skills'),
    project: (cwd) => path.join(cwd, '.grok', 'skills'),
    detect: (home) => exists(path.join(home, '.grok')),
  },
  claude: {
    id: 'claude',
    name: 'Claude Code',
    aliases: ['claude-code', 'anthropic'],
    type: 'skill',
    global: (home) => path.join(home, '.claude', 'skills'),
    project: (cwd) => path.join(cwd, '.claude', 'skills'),
    detect: (home) => exists(path.join(home, '.claude')),
  },
  cursor: {
    id: 'cursor',
    name: 'Cursor',
    type: 'skill',
    global: (home) => path.join(home, '.cursor', 'skills'),
    project: (cwd) => path.join(cwd, '.cursor', 'skills'),
    detect: (home) => exists(path.join(home, '.cursor')),
  },
  codex: {
    id: 'codex',
    name: 'Codex',
    aliases: ['openai'],
    type: 'skill',
    global: (home) => path.join(home, '.codex', 'skills'),
    project: (cwd) => path.join(cwd, '.codex', 'skills'),
    detect: (home) => exists(path.join(home, '.codex')),
  },
  gemini: {
    id: 'gemini',
    name: 'Gemini CLI / Antigravity IDE',
    aliases: ['antigravity', 'google'],
    type: 'plugin',
    global: (home) => path.join(home, '.gemini', 'config', 'plugins', PLUGIN_DIRNAME),
    project: null,
    detect: (home) => exists(path.join(home, '.gemini')),
  },
  'antigravity-cli': {
    id: 'antigravity-cli',
    name: 'Antigravity CLI',
    aliases: ['agy'],
    type: 'plugin',
    global: (home) => path.join(home, '.gemini', 'antigravity-cli', 'plugins', PLUGIN_DIRNAME),
    project: null,
    detect: (home) => exists(path.join(home, '.gemini', 'antigravity-cli')),
  },
  opencode: {
    id: 'opencode',
    name: 'OpenCode',
    aliases: ['open-code'],
    type: 'skill',
    global: (home) => path.join(home, '.config', 'opencode', 'skills'),
    project: (cwd) => path.join(cwd, '.opencode', 'skills'),
    detect: (home) => exists(path.join(home, '.config', 'opencode')) || exists(path.join(home, '.opencode')),
  },
  hermes: {
    id: 'hermes',
    name: 'Hermes',
    aliases: ['hermes-agent', 'nous'],
    type: 'skill',
    global: (home) => path.join(hermesHome(home), 'skills'),
    project: null,
    detect: (home) => exists(hermesHome(home)),
  },
  workbuddy: {
    id: 'workbuddy',
    name: 'WorkBuddy',
    aliases: ['work-buddy', 'wb'],
    type: 'skill',
    global: (home) => path.join(home, '.workbuddy', 'skills'),
    // WorkBuddy also discovers project skills under .agents/skills
    project: (cwd) => path.join(cwd, '.agents', 'skills'),
    detect: (home) => exists(path.join(home, '.workbuddy')),
  },
  pi: {
    id: 'pi',
    name: 'Pi',
    aliases: ['pi-agent', 'pi-coding-agent'],
    type: 'skill',
    global: (home) => path.join(home, '.pi', 'agent', 'skills'),
    project: (cwd) => path.join(cwd, '.pi', 'skills'),
    detect: (home) => exists(path.join(home, '.pi')),
  },
  copilot: {
    id: 'copilot',
    name: 'GitHub Copilot',
    aliases: ['github-copilot'],
    type: 'skill',
    global: (home) => path.join(home, '.copilot', 'skills'),
    project: (cwd) => path.join(cwd, '.github', 'skills'),
    detect: (home) => exists(path.join(home, '.copilot')),
  },
  roo: {
    id: 'roo',
    name: 'Roo Code',
    aliases: ['roo-code'],
    type: 'skill',
    global: (home) => path.join(home, '.roo', 'skills'),
    project: (cwd) => path.join(cwd, '.roo', 'skills'),
    detect: (home) => exists(path.join(home, '.roo')),
  },
  windsurf: {
    id: 'windsurf',
    name: 'Windsurf',
    type: 'skill',
    global: (home) => path.join(home, '.codeium', 'windsurf', 'skills'),
    project: (cwd) => path.join(cwd, '.windsurf', 'skills'),
    detect: (home) => exists(path.join(home, '.codeium', 'windsurf')),
  },
};

function hermesHome(home) {
  const fromEnv = process.env.HERMES_HOME?.trim();
  if (!fromEnv) return path.join(home, '.hermes');
  if (fromEnv === '~') return home;
  if (fromEnv.startsWith('~/') || fromEnv.startsWith('~\\')) {
    return path.join(home, fromEnv.slice(2));
  }
  return fromEnv;
}

export function exists(p) {
  try {
    fs.accessSync(p);
    return true;
  } catch {
    return false;
  }
}

export function lexists(p) {
  try {
    fs.lstatSync(p);
    return true;
  } catch {
    return false;
  }
}

export function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

export function parseFrontmatter(content) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return {};
  const fm = match[1];
  const name = fm.match(/^name:\s*(.+)$/m)?.[1]?.trim();
  let description = '';
  const folded = fm.match(/^description:\s*>-?\s*\r?\n((?:[ \t]+.+\r?\n?)*)/m);
  if (folded) {
    description = folded[1].replace(/^[ \t]+/gm, '').replace(/\r?\n/g, ' ').trim();
  } else {
    const inline = fm.match(/^description:\s*(.+)$/m);
    if (inline) description = inline[1].replace(/^["']|["']$/g, '').trim();
  }
  return { name, description };
}

export function parseArgs(argv) {
  const args = argv.slice(2);
  const flags = {
    all: false,
    project: false,
    copy: false,
    link: false,
    yes: false,
    dryRun: false,
    force: false,
    help: false,
    agents: [],
  };
  const positional = [];

  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === '--all') flags.all = true;
    else if (a === '--project' || a === '-p') flags.project = true;
    else if (a === '--copy') flags.copy = true;
    else if (a === '--link') flags.link = true;
    else if (a === '--yes' || a === '-y') flags.yes = true;
    else if (a === '--dry-run') flags.dryRun = true;
    else if (a === '--force' || a === '-f') flags.force = true;
    else if (a === '--help' || a === '-h') flags.help = true;
    else if (a === '--agent' || a === '-a') {
      const val = args[++i];
      if (!val || val.startsWith('-')) {
        throw new Error('--agent requires a value, e.g. --agent grok,claude');
      }
      flags.agents.push(...splitList(val));
    } else if (a.startsWith('--agent=')) {
      flags.agents.push(...splitList(a.slice(8)));
    } else if (a.startsWith('-')) {
      throw new Error(`Unknown option: ${a}`);
    } else {
      positional.push(a);
    }
  }

  return {
    command: positional[0] || 'list',
    rest: positional.slice(1),
    flags,
  };
}

function splitList(value) {
  return value.split(',').map((s) => s.trim()).filter(Boolean);
}

export function findAgent(id) {
  const key = String(id).toLowerCase();
  if (AGENTS[key]) return AGENTS[key];
  return Object.values(AGENTS).find((agent) => agent.aliases?.includes(key)) ?? null;
}

export function resolveTargets({ flags, home, cwd }) {
  const requested = flags.agents;
  const allAgents = Object.values(AGENTS);
  let selected;
  if (requested.length === 0) {
    selected = allAgents.filter((agent) => agent.always || agent.detect(home));
  } else if (requested.includes('all') || requested.includes('*')) {
    selected = allAgents;
  } else {
    const missing = [];
    selected = [];
    for (const id of requested) {
      const agent = findAgent(id);
      if (!agent) missing.push(id);
      else selected.push(agent);
    }
    if (missing.length) {
      throw new Error(`Unknown agent(s): ${missing.join(', ')}. Run "oh-my-skills agents" to list ids.`);
    }
  }

  const targets = [];
  const seen = new Set();
  for (const agent of selected) {
    const targetPath = flags.project ? agent.project?.(cwd) : agent.global(home);
    if (!targetPath) continue;
    if (seen.has(targetPath)) continue;
    seen.add(targetPath);
    targets.push({
      id: agent.id,
      name: agent.name,
      path: targetPath,
      type: agent.type,
    });
  }
  return targets;
}

export function storeDir(home) {
  return path.join(home, '.local', 'share', 'oh-my-skills');
}

export function buildAgentChoices(ctx, flags) {
  const choices = [];
  for (const agent of Object.values(AGENTS)) {
    const targetPath = flags.project ? agent.project?.(ctx.cwd) : agent.global(ctx.home);
    if (!targetPath) continue;
    const detected = Boolean(agent.always || agent.detect(ctx.home));
    const shortPath = targetPath.startsWith(ctx.home)
      ? `~${targetPath.slice(ctx.home.length)}`
      : targetPath;
    choices.push({
      id: agent.id,
      label: `${agent.name}  ${c.dim}(${agent.id})${c.reset}`,
      hint: detected ? `${c.green}detected${c.reset}  ${c.dim}${shortPath}${c.reset}` : `${c.dim}not found  ${shortPath}${c.reset}`,
      selected: detected,
    });
  }
  return choices;
}

export function createContext({
  home = os.homedir(),
  cwd = process.cwd(),
  pkgRoot = PKG_ROOT,
  log = console.log,
  stdin = process.stdin,
  stdout = process.stdout,
  isTTY = Boolean(process.stdin.isTTY && process.stdout.isTTY),
} = {}) {
  return {
    home,
    cwd,
    pkgRoot,
    skillsDir: path.join(pkgRoot, 'skills'),
    store: storeDir(home),
    log,
    stdin,
    stdout,
    isTTY,
    pkg: readJson(path.join(pkgRoot, 'package.json')),
  };
}

export function listAvailableSkills(ctx) {
  if (!exists(ctx.skillsDir)) return [];
  return fs.readdirSync(ctx.skillsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => {
      const dirPath = path.join(ctx.skillsDir, entry.name);
      const skillMdPath = path.join(dirPath, 'SKILL.md');
      let description = 'No description provided';
      if (exists(skillMdPath)) {
        const fm = parseFrontmatter(fs.readFileSync(skillMdPath, 'utf8'));
        if (fm.description) description = fm.description;
      }
      return { name: entry.name, description, dirPath };
    });
}

export function readStoreMeta(ctx) {
  const file = path.join(ctx.store, 'install.json');
  if (!exists(file)) return { installed: [], version: null, package: ctx.pkg.name };
  try {
    const meta = readJson(file);
    return { installed: [], ...meta };
  } catch {
    return { installed: [], version: null, package: ctx.pkg.name };
  }
}

export function writeStoreMeta(ctx, installed, { dryRun } = {}) {
  if (dryRun) return;
  fs.mkdirSync(ctx.store, { recursive: true });
  const pluginSrc = path.join(ctx.pkgRoot, 'plugin.json');
  if (exists(pluginSrc)) {
    fs.copyFileSync(pluginSrc, path.join(ctx.store, 'plugin.json'));
  }
  fs.writeFileSync(path.join(ctx.store, 'install.json'), `${JSON.stringify({
    package: ctx.pkg.name,
    version: ctx.pkg.version,
    installed: [...new Set(installed)].sort(),
    updatedAt: new Date().toISOString(),
  }, null, 2)}\n`);
}

export function isManagedPath(dest, ctx) {
  try {
    const st = fs.lstatSync(dest);
    if (!st.isSymbolicLink()) return false;
    const target = fs.readlinkSync(dest);
    const resolved = path.resolve(path.dirname(dest), target);
    return resolved === ctx.store
      || resolved.startsWith(ctx.store + path.sep)
      || resolved === ctx.pkgRoot
      || resolved.startsWith(ctx.pkgRoot + path.sep)
      || resolved.includes(`${path.sep}oh-my-skills${path.sep}`)
      || resolved.endsWith(`${path.sep}oh-my-skills`);
  } catch {
    return false;
  }
}

function skillSource(ctx, skillName, flags) {
  if (flags.link) return path.join(ctx.skillsDir, skillName);
  return path.join(ctx.store, 'skills', skillName);
}

export function syncSkillToStore(ctx, skillName, { dryRun } = {}) {
  const src = path.join(ctx.skillsDir, skillName);
  const dest = path.join(ctx.store, 'skills', skillName);
  if (dryRun) return dest;
  fs.mkdirSync(path.join(ctx.store, 'skills'), { recursive: true });
  if (lexists(dest)) fs.rmSync(dest, { recursive: true, force: true });
  fs.cpSync(src, dest, { recursive: true });
  return dest;
}

function cleanupLegacyClaudePlugin(ctx, flags) {
  const legacy = path.join(ctx.home, '.claude', 'plugins', PLUGIN_DIRNAME);
  if (!lexists(legacy)) return;
  if (!isManagedPath(legacy, ctx) && !fs.lstatSync(legacy).isSymbolicLink()) return;
  if (flags.dryRun) {
    ctx.log(`  ${c.dim}• would remove legacy Claude plugin link ${legacy}${c.reset}`);
    return;
  }
  fs.rmSync(legacy, { recursive: true, force: true });
  ctx.log(`  ${c.dim}Removed legacy ~/.claude/plugins/${PLUGIN_DIRNAME} (Claude skills go in ~/.claude/skills)${c.reset}`);
}

export function placePath(src, dest, { copy, dryRun, force, ctx, label, log }) {
  if (dryRun) {
    log(`  ${c.dim}• ${copy ? 'copy' : 'link'} ${label}${c.reset}`);
    return 'dry-run';
  }

  fs.mkdirSync(path.dirname(dest), { recursive: true });

  if (lexists(dest)) {
    const st = fs.lstatSync(dest);
    if (st.isSymbolicLink() || force || (ctx && isManagedPath(dest, ctx))) {
      fs.rmSync(dest, { recursive: true, force: true });
    } else {
      log(`  ${c.yellow}⚠️  Skip ${label}: path exists (use --force to replace)${c.reset}`);
      return 'skipped';
    }
  }

  if (copy) fs.cpSync(src, dest, { recursive: true });
  else fs.symlinkSync(src, dest, 'junction');
  log(`  ${c.green}✅ ${copy ? 'Copied' : 'Linked'} ${label}${c.reset}`);
  return 'ok';
}

export function isSkillInstalled(target, skillName, ctx) {
  if (target.type === 'plugin') {
    if (!lexists(target.path)) return false;
    return exists(path.join(ctx.store, 'skills', skillName)) || exists(path.join(target.path, 'skills', skillName));
  }
  const dest = path.join(target.path, skillName);
  if (!lexists(dest)) return false;
  try {
    const st = fs.lstatSync(dest);
    if (st.isSymbolicLink()) return exists(dest);
    return exists(path.join(dest, 'SKILL.md'));
  } catch {
    return false;
  }
}

function resolveSkillNames(ctx, names, flags) {
  const available = listAvailableSkills(ctx).map((s) => s.name);
  if (flags.all || names.includes('all')) return available;
  const wanted = names.filter((name) => {
    if (!available.includes(name)) {
      ctx.log(`  ${c.red}✖ Skill "${name}" does not exist.${c.reset}`);
      return false;
    }
    return true;
  });
  return wanted;
}

export function cmdList(ctx, flags) {
  const skills = listAvailableSkills(ctx);
  const targets = resolveTargets({ flags, home: ctx.home, cwd: ctx.cwd });
  const meta = readStoreMeta(ctx);

  ctx.log(`\n${c.bold}${c.cyan}oh-my-skills${c.reset} ${c.dim}${ctx.pkg.version}${c.reset}`);
  if (meta.version) ctx.log(`${c.dim}Store: ${ctx.store} (${meta.version})${c.reset}`);
  ctx.log('');

  if (skills.length === 0) {
    ctx.log(`  ${c.yellow}No skills found in package.${c.reset}\n`);
    return 0;
  }

  for (const skill of skills) {
    ctx.log(`  ${c.bold}${c.green}✦ ${skill.name}${c.reset}`);
    ctx.log(`    ${c.dim}${truncate(skill.description, 110)}${c.reset}`);
    const status = targets.map((target) => {
      const installed = isSkillInstalled(target, skill.name, ctx);
      return installed
        ? `${c.green}✓ ${target.id}${c.reset}`
        : `${c.dim}○ ${target.id}${c.reset}`;
    });
    ctx.log(`    ${status.join('  ')}\n`);
  }

  ctx.log(`${c.dim}Use "oh-my-skills add <name>" or "oh-my-skills add --all".${c.reset}\n`);
  return 0;
}

export function cmdAgents(ctx, flags) {
  ctx.log(`\n${c.bold}Supported agents${c.reset}\n`);
  ctx.log(`${pad('id', 18)} ${pad('scope', 8)} ${pad('detected', 10)} path`);
  for (const agent of Object.values(AGENTS)) {
    const targetPath = flags.project ? agent.project?.(ctx.cwd) : agent.global(ctx.home);
    const detected = agent.always || agent.detect(ctx.home) ? `${c.green}yes${c.reset}` : `${c.dim}no${c.reset}`;
    ctx.log(`${pad(agent.id, 18)} ${pad(agent.type, 8)} ${padVisible(detected, 10)} ${targetPath || c.dim + '(no project path)' + c.reset}`);
  }
  ctx.log(`\n${c.dim}Default install targets detected agents plus ~/.agents/skills.${c.reset}`);
  ctx.log(`${c.dim}Pass --agent all to create every known path, or --agent grok,claude to pick.${c.reset}\n`);
  return 0;
}

export async function cmdAdd(ctx, names, flags) {
  printBanner(ctx);

  let skillNames = names;
  if (shouldPrompt(ctx, flags) && !flags.all && skillNames.length === 0) {
    try {
      skillNames = await promptMultiSelect(ctx, {
        title: 'Which skills do you want to install?',
        items: buildSkillChoices(listAvailableSkills(ctx)),
      });
    } catch (err) {
      if (err.code === 'CANCELED') return 1;
      throw err;
    }
    if (skillNames.length === 0) {
      ctx.log(`\n${c.yellow}No skills selected.${c.reset}\n`);
      return 1;
    }
  }

  const toInstall = resolveSkillNames(ctx, skillNames, flags);
  if (toInstall.length === 0) {
    ctx.log(`\n${c.yellow}No valid skills specified to add.${c.reset}`);
    ctx.log(`Run ${c.cyan}oh-my-skills add${c.reset} in a terminal to pick interactively, or pass --all.\n`);
    return 1;
  }

  let agentFlags = flags;
  if (shouldPrompt(ctx, flags) && flags.agents.length === 0) {
    try {
      const picked = await promptMultiSelect(ctx, {
        title: 'Install into which agents?',
        items: buildAgentChoices(ctx, flags),
      });
      if (picked.length === 0) {
        ctx.log(`\n${c.yellow}No agents selected.${c.reset}\n`);
        return 1;
      }
      agentFlags = { ...flags, agents: picked };
    } catch (err) {
      if (err.code === 'CANCELED') return 1;
      throw err;
    }
  }

  const targets = resolveTargets({ flags: agentFlags, home: ctx.home, cwd: ctx.cwd });
  if (targets.length === 0) {
    ctx.log(`\n${c.yellow}No matching agent directories.${c.reset} Try --agent all\n`);
    return 1;
  }

  cleanupLegacyClaudePlugin(ctx, agentFlags);

  ctx.log(`\n${c.bold}Installing: ${toInstall.map((s) => c.cyan + s + c.reset).join(', ')}${c.reset}`);
  ctx.log(`${c.dim}→ ${targets.map((t) => t.id).join(', ')}${c.reset}\n`);

  const copyToAgent = flags.project || flags.copy;
  const meta = readStoreMeta(ctx);
  const installed = new Set(meta.installed);

  if (!flags.link) {
    for (const skillName of toInstall) {
      syncSkillToStore(ctx, skillName, flags);
      installed.add(skillName);
    }
    writeStoreMeta(ctx, [...installed], flags);
  }

  for (const target of targets) {
    if (target.type === 'plugin') {
      if (flags.link) {
        placePath(ctx.pkgRoot, target.path, {
          copy: false, dryRun: flags.dryRun, force: flags.force, ctx, log: ctx.log,
          label: `plugin ${target.name}`,
        });
      } else {
        placePath(ctx.store, target.path, {
          copy: copyToAgent, dryRun: flags.dryRun, force: flags.force, ctx, log: ctx.log,
          label: `plugin ${target.name}`,
        });
      }
      continue;
    }

    for (const skillName of toInstall) {
      const src = skillSource(ctx, skillName, flags);
      const dest = path.join(target.path, skillName);
      placePath(src, dest, {
        copy: copyToAgent, dryRun: flags.dryRun, force: flags.force, ctx, log: ctx.log,
        label: `"${skillName}" → ${target.name}`,
      });
    }
  }

  ctx.log(`\n${c.green}${c.bold}Done.${c.reset} ${c.dim}python3 is required to serve previews.${c.reset}\n`);
  return 0;
}

export function cmdRemove(ctx, names, flags) {
  const available = listAvailableSkills(ctx).map((s) => s.name);
  const toRemove = (flags.all || names.includes('all')) ? available : names;
  if (toRemove.length === 0) {
    ctx.log(`\n${c.yellow}No skills specified to remove.${c.reset}\n`);
    return 1;
  }

  const targets = resolveTargets({ flags, home: ctx.home, cwd: ctx.cwd });
  const meta = readStoreMeta(ctx);
  const pruneStore = !flags.project && flags.agents.length === 0;
  const remaining = (meta.installed.length ? meta.installed : available)
    .filter((name) => !toRemove.includes(name));
  ctx.log(`\n${c.bold}Removing: ${toRemove.map((s) => c.yellow + s + c.reset).join(', ')}${c.reset}\n`);

  for (const target of targets) {
    if (target.type === 'plugin') {
      if (pruneStore && remaining.length === 0) {
        if (lexists(target.path) && (flags.force || isManagedPath(target.path, ctx) || fs.lstatSync(target.path).isSymbolicLink())) {
          if (!flags.dryRun) fs.rmSync(target.path, { recursive: true, force: true });
          ctx.log(`  ${c.green}✅ Removed plugin from ${target.name}${c.reset}`);
        }
      }
      continue;
    }

    for (const skillName of toRemove) {
      const dest = path.join(target.path, skillName);
      if (!lexists(dest)) continue;
      if (!flags.force && !isManagedPath(dest, ctx)) {
        const st = fs.lstatSync(dest);
        if (!st.isSymbolicLink()) {
          ctx.log(`  ${c.yellow}⚠️  Skip "${skillName}" in ${target.name}: not an oh-my-skills link (use --force)${c.reset}`);
          continue;
        }
      }
      if (!flags.dryRun) fs.rmSync(dest, { recursive: true, force: true });
      ctx.log(`  ${c.green}✅ Removed "${skillName}" from ${target.name}${c.reset}`);
    }
  }

  if (pruneStore) {
    if (!flags.dryRun) {
      for (const skillName of toRemove) {
        const dest = path.join(ctx.store, 'skills', skillName);
        if (lexists(dest)) fs.rmSync(dest, { recursive: true, force: true });
      }
    }
    writeStoreMeta(ctx, remaining, flags);
  }

  ctx.log(`\n${c.green}${c.bold}Removal completed.${c.reset}\n`);
  return 0;
}

export function cmdUpdate(ctx, names, flags) {
  const meta = readStoreMeta(ctx);
  const available = listAvailableSkills(ctx).map((s) => s.name);
  let toUpdate = names.length ? names.filter((n) => available.includes(n)) : meta.installed.filter((n) => available.includes(n));
  if (flags.all) toUpdate = available;
  if (toUpdate.length === 0) {
    ctx.log(`\n${c.yellow}Nothing to update. Install a skill first.${c.reset}\n`);
    return 1;
  }
  ctx.log(`\n${c.bold}Updating ${toUpdate.join(', ')} from ${ctx.pkg.name}@${ctx.pkg.version}${c.reset}\n`);
  return cmdAdd(ctx, toUpdate, { ...flags, all: false, force: true, yes: true });
}

export function cmdInfo(ctx, skillName) {
  if (!skillName) {
    ctx.log(`${c.red}Please specify a skill name. Example: oh-my-skills info visual-brainstorm${c.reset}`);
    return 1;
  }
  const skillMdPath = path.join(ctx.skillsDir, skillName, 'SKILL.md');
  if (!exists(skillMdPath)) {
    ctx.log(`${c.red}Skill "${skillName}" not found.${c.reset}`);
    return 1;
  }
  ctx.log(`\n${c.bold}${c.cyan}=== Skill: ${skillName} ===${c.reset}\n`);
  ctx.log(fs.readFileSync(skillMdPath, 'utf8'));
  return 0;
}

export function cmdDoctor(ctx, flags) {
  const targets = resolveTargets({ flags, home: ctx.home, cwd: ctx.cwd });
  const skills = listAvailableSkills(ctx);
  const meta = readStoreMeta(ctx);
  let issues = 0;

  ctx.log(`\n${c.bold}oh-my-skills doctor${c.reset}\n`);
  ctx.log(`  package: ${ctx.pkg.name}@${ctx.pkg.version}`);
  ctx.log(`  store:   ${ctx.store}${meta.version ? ` (${meta.version})` : ''}`);
  ctx.log(`  node:    ${process.version}`);

  const py = spawnSync('python3', ['--version'], { encoding: 'utf8' });
  if (py.status === 0) ctx.log(`  python3: ${(py.stdout || py.stderr).trim()}`);
  else {
    ctx.log(`  ${c.red}python3: not found (preview servers need it)${c.reset}`);
    issues += 1;
  }

  ctx.log('');
  for (const skill of skills) {
    for (const target of targets) {
      if (target.type === 'plugin') {
        if (!lexists(target.path)) continue;
        if (!exists(target.path) && fs.lstatSync(target.path).isSymbolicLink()) {
          ctx.log(`  ${c.red}✖ broken plugin link: ${target.path}${c.reset}`);
          issues += 1;
        }
        continue;
      }
      const dest = path.join(target.path, skill.name);
      if (!lexists(dest)) continue;
      const st = fs.lstatSync(dest);
      if (st.isSymbolicLink() && !exists(dest)) {
        ctx.log(`  ${c.red}✖ broken link: ${dest}${c.reset}`);
        issues += 1;
      }
    }
  }

  if (issues === 0) ctx.log(`  ${c.green}No broken installs found on current targets.${c.reset}`);
  else ctx.log(`\n  ${c.yellow}Run "oh-my-skills add --all --force" to repair.${c.reset}`);
  ctx.log('');
  return issues === 0 ? 0 : 1;
}

export function showHelp(log = console.log) {
  log(`
${c.bold}${c.cyan}oh-my-skills${c.reset} — install skills into AI agents (Codex, OpenCode, Hermes, WorkBuddy, Pi, …)

${c.bold}USAGE${c.reset}
  $ npx @lxy10086/oh-my-skills <command> [options]

${c.bold}COMMANDS${c.reset}
  ${c.cyan}list, ls${c.reset}               List skills and install status
  ${c.cyan}add, install <name...>${c.reset} Install skill(s); prompts for agents in a terminal
  ${c.cyan}remove, rm <name...>${c.reset}   Uninstall skill(s)
  ${c.cyan}update [name...]${c.reset}       Refresh installed skills from this package
  ${c.cyan}info <name>${c.reset}            Print a skill's SKILL.md
  ${c.cyan}agents${c.reset}                 Show supported agent ids and paths
  ${c.cyan}doctor${c.reset}                 Check python3 and broken links
  ${c.cyan}help${c.reset}                   Show this message

${c.bold}OPTIONS${c.reset}
  ${c.yellow}--all${c.reset}                 Apply to every skill in the package
  ${c.yellow}-a, --agent <ids>${c.reset}     codex,opencode,hermes,workbuddy,pi,grok,claude,... or all
  ${c.yellow}-p, --project${c.reset}         Install into the current workspace (copies files)
  ${c.yellow}--copy${c.reset}                Copy files instead of symlinking
  ${c.yellow}--link${c.reset}                Link directly to this package (local development)
  ${c.yellow}--force, -f${c.reset}           Replace existing files
  ${c.yellow}--dry-run${c.reset}             Print actions without writing
  ${c.yellow}-y, --yes${c.reset}             Skip prompts; install to detected agents

${c.bold}EXAMPLES${c.reset}
  $ npx @lxy10086/oh-my-skills add
  $ npx @lxy10086/oh-my-skills add --all -y
  $ npx @lxy10086/oh-my-skills add --all --agent codex,opencode,hermes,workbuddy,pi
  $ npx @lxy10086/oh-my-skills add visual-brainstorm --agent grok,claude
  $ npx @lxy10086/oh-my-skills add html-prototype --project
  $ npx @lxy10086/oh-my-skills remove visual-brainstorm --agent cursor
  $ npx @lxy10086/oh-my-skills update
`);
}

export async function run(argv, options = {}) {
  let parsed;
  try {
    parsed = parseArgs(argv);
  } catch (err) {
    console.error(`${c.red}${err.message}${c.reset}`);
    showHelp();
    return 1;
  }

  const ctx = createContext(options);
  const { command, rest, flags } = parsed;

  if (flags.help || command === 'help') {
    showHelp(ctx.log);
    return 0;
  }

  try {
    switch (command) {
      case 'list':
      case 'ls':
        return cmdList(ctx, flags);
      case 'agents':
        return cmdAgents(ctx, flags);
      case 'add':
      case 'install':
      case 'i':
        return cmdAdd(ctx, rest, flags);
      case 'remove':
      case 'rm':
      case 'uninstall':
        return cmdRemove(ctx, rest, flags);
      case 'update':
        return cmdUpdate(ctx, rest, flags);
      case 'info':
        return cmdInfo(ctx, rest[0]);
      case 'doctor':
        return cmdDoctor(ctx, flags);
      default:
        ctx.log(`${c.red}Unknown command: ${command}${c.reset}`);
        showHelp(ctx.log);
        return 1;
    }
  } catch (err) {
    ctx.log(`${c.red}${err.message}${c.reset}`);
    return 1;
  }
}

function truncate(text, max) {
  if (!text) return '';
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

function pad(text, width) {
  return String(text).padEnd(width);
}

function padVisible(text, width) {
  const visible = text.replace(/\x1b\[[0-9;]*m/g, '');
  return text + ' '.repeat(Math.max(0, width - visible.length));
}
