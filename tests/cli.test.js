import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';

import {
  PKG_ROOT,
  createContext,
  findAgent,
  parseArgs,
  parseFrontmatter,
  resolveTargets,
  run,
  isManagedPath,
  storeDir,
  buildAgentChoices,
} from '../bin/lib.js';
import { renderBanner } from '../bin/banner.js';
import { shouldPrompt } from '../bin/prompt.js';

const CLI = path.join(PKG_ROOT, 'bin', 'cli.js');

function tmpHome() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'oms-test-'));
}

function collectLog() {
  const lines = [];
  return {
    lines,
    log: (...args) => lines.push(args.join(' ')),
  };
}

test('parseArgs maps -a to --agent, not --all', () => {
  const parsed = parseArgs(['node', 'cli.js', 'add', 'visual-brainstorm', '-a', 'grok,claude', '--all']);
  assert.equal(parsed.command, 'add');
  assert.deepEqual(parsed.rest, ['visual-brainstorm']);
  assert.equal(parsed.flags.all, true);
  assert.deepEqual(parsed.flags.agents, ['grok', 'claude']);
});

test('parseArgs rejects unknown flags', () => {
  assert.throws(() => parseArgs(['node', 'cli.js', 'list', '--nope']), /Unknown option/);
});

test('parseFrontmatter reads folded descriptions', () => {
  const content = fs.readFileSync(path.join(PKG_ROOT, 'skills', 'visual-brainstorm', 'SKILL.md'), 'utf8');
  const fm = parseFrontmatter(content);
  assert.equal(fm.name, 'visual-brainstorm');
  assert.match(fm.description, /Visual brainstorming/);
  assert.doesNotMatch(fm.description, /\n/);
});

test('findAgent resolves aliases', () => {
  assert.equal(findAgent('claude-code').id, 'claude');
  assert.equal(findAgent('cline').id, 'agents');
  assert.equal(findAgent('agy').id, 'antigravity-cli');
  assert.equal(findAgent('nope'), null);
});

test('resolveTargets defaults to detected agents plus universal', () => {
  const home = tmpHome();
  fs.mkdirSync(path.join(home, '.grok'));
  fs.mkdirSync(path.join(home, '.claude'));
  const targets = resolveTargets({ flags: { agents: [], project: false }, home, cwd: home });
  const ids = targets.map((t) => t.id).sort();
  assert.deepEqual(ids, ['agents', 'claude', 'grok']);
  assert.equal(targets.find((t) => t.id === 'claude').path, path.join(home, '.claude', 'skills'));
  fs.rmSync(home, { recursive: true, force: true });
});

test('resolveTargets --agent all includes plugin paths', () => {
  const home = tmpHome();
  const targets = resolveTargets({ flags: { agents: ['all'], project: false }, home, cwd: home });
  assert.ok(targets.some((t) => t.id === 'gemini' && t.type === 'plugin'));
  assert.ok(targets.some((t) => t.id === 'codex'));
  assert.ok(!targets.some((t) => t.path.includes(`${path.sep}plugins${path.sep}`) && t.id === 'claude'));
  fs.rmSync(home, { recursive: true, force: true });
});

test('add copies into store then symlinks agent dirs', async () => {
  const home = tmpHome();
  fs.mkdirSync(path.join(home, '.grok'));
  const { log } = collectLog();
  const ctx = createContext({ home, cwd: home, log });
  const code = await run(['node', 'cli.js', 'add', 'visual-brainstorm', '--agent', 'grok,agents'], ctx);
  assert.equal(code, 0);

  const stored = path.join(storeDir(home), 'skills', 'visual-brainstorm', 'SKILL.md');
  const grokLink = path.join(home, '.grok', 'skills', 'visual-brainstorm');
  const agentsLink = path.join(home, '.agents', 'skills', 'visual-brainstorm');
  assert.equal(fs.existsSync(stored), true);
  assert.equal(fs.lstatSync(grokLink).isSymbolicLink(), true);
  assert.equal(fs.realpathSync(grokLink), fs.realpathSync(path.dirname(stored)));
  assert.equal(fs.lstatSync(agentsLink).isSymbolicLink(), true);
  assert.equal(isManagedPath(grokLink, ctx), true);

  const meta = JSON.parse(fs.readFileSync(path.join(storeDir(home), 'install.json'), 'utf8'));
  assert.deepEqual(meta.installed, ['visual-brainstorm']);

  fs.rmSync(home, { recursive: true, force: true });
});

test('remove --agent keeps the store when other agents may still use it', async () => {
  const home = tmpHome();
  fs.mkdirSync(path.join(home, '.grok'));
  fs.mkdirSync(path.join(home, '.cursor'));
  const { log } = collectLog();
  const ctx = createContext({ home, cwd: home, log });
  await run(['node', 'cli.js', 'add', 'visual-brainstorm', '--agent', 'grok,cursor'], ctx);
  const code = await run(['node', 'cli.js', 'remove', 'visual-brainstorm', '--agent', 'cursor'], ctx);
  assert.equal(code, 0);
  assert.equal(fs.existsSync(path.join(home, '.cursor', 'skills', 'visual-brainstorm')), false);
  assert.equal(fs.existsSync(path.join(home, '.grok', 'skills', 'visual-brainstorm')), true);
  assert.equal(fs.existsSync(path.join(storeDir(home), 'skills', 'visual-brainstorm', 'SKILL.md')), true);
  fs.rmSync(home, { recursive: true, force: true });
});

test('--project copies instead of symlinking', async () => {
  const home = tmpHome();
  const project = fs.mkdtempSync(path.join(os.tmpdir(), 'oms-proj-'));
  const { log } = collectLog();
  const ctx = createContext({ home, cwd: project, log });
  const code = await run(['node', 'cli.js', 'add', 'html-prototype', '--project', '--agent', 'agents'], ctx);
  assert.equal(code, 0);
  const dest = path.join(project, '.agents', 'skills', 'html-prototype');
  assert.equal(fs.existsSync(path.join(dest, 'SKILL.md')), true);
  assert.equal(fs.lstatSync(dest).isSymbolicLink(), false);
  fs.rmSync(home, { recursive: true, force: true });
  fs.rmSync(project, { recursive: true, force: true });
});

test('doctor reports broken grok links', async () => {
  const home = tmpHome();
  const dest = path.join(home, '.grok', 'skills', 'visual-brainstorm');
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.symlinkSync(path.join(home, 'missing-target'), dest);
  const { log, lines } = collectLog();
  const ctx = createContext({ home, cwd: home, log });
  const code = await run(['node', 'cli.js', 'doctor', '--agent', 'grok'], ctx);
  assert.equal(code, 1);
  assert.ok(lines.some((line) => line.includes('broken link')));
  fs.rmSync(home, { recursive: true, force: true });
});

test('add --force repairs a broken symlink', async () => {
  const home = tmpHome();
  const dest = path.join(home, '.grok', 'skills', 'visual-brainstorm');
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.symlinkSync('/Users/a1021500136/Desktop/oh-my-skills/visual-brainstorm', dest);
  const { log } = collectLog();
  const ctx = createContext({ home, cwd: home, log });
  const code = await run(['node', 'cli.js', 'add', 'visual-brainstorm', '--agent', 'grok'], ctx);
  assert.equal(code, 0);
  assert.equal(fs.existsSync(path.join(dest, 'SKILL.md')), true);
  fs.rmSync(home, { recursive: true, force: true });
});

test('CLI help and list exit 0', () => {
  const help = spawnSync(process.execPath, [CLI, 'help'], { encoding: 'utf8' });
  assert.equal(help.status, 0);
  assert.match(help.stdout, /oh-my-skills/);
  const list = spawnSync(process.execPath, [CLI, 'list', '--agent', 'agents'], {
    encoding: 'utf8',
    env: { ...process.env, HOME: tmpHome() },
  });
  assert.equal(list.status, 0);
  assert.match(list.stdout, /visual-brainstorm/);
  assert.match(list.stdout, /html-prototype/);
});

test('renderBanner is a large pixel wordmark', () => {
  const banner = renderBanner({ columns: 80, version: '0.1.1' });
  assert.match(banner, /PIXEL SKILLS FOR EVERY AGENT/);
  assert.match(banner, /█/);
  assert.ok(banner.split('\n').length >= 16);
});

test('shouldPrompt only in an interactive TTY without -y', () => {
  assert.equal(shouldPrompt({ isTTY: true }, { yes: false, dryRun: false }), true);
  assert.equal(shouldPrompt({ isTTY: false }, { yes: false, dryRun: false }), false);
  assert.equal(shouldPrompt({ isTTY: true }, { yes: true, dryRun: false }), false);
  assert.equal(shouldPrompt({ isTTY: true }, { yes: false, dryRun: true }), false);
});

test('buildAgentChoices pre-selects detected agents', () => {
  const home = tmpHome();
  fs.mkdirSync(path.join(home, '.grok'));
  const ctx = createContext({ home, cwd: home, isTTY: false });
  const choices = buildAgentChoices(ctx, { project: false });
  const grok = choices.find((item) => item.id === 'grok');
  const cursor = choices.find((item) => item.id === 'cursor');
  assert.equal(grok.selected, true);
  assert.equal(cursor.selected, false);
  fs.rmSync(home, { recursive: true, force: true });
});

test('add --all -y prints the pixel banner and skips the picker', () => {
  const home = tmpHome();
  const result = spawnSync(process.execPath, [CLI, 'add', '--all', '-y', '--agent', 'agents', '--dry-run'], {
    encoding: 'utf8',
    env: { ...process.env, HOME: home },
  });
  assert.equal(result.status, 0);
  assert.match(result.stdout, /PIXEL SKILLS FOR EVERY AGENT/);
  assert.match(result.stdout, /visual-brainstorm/);
  fs.rmSync(home, { recursive: true, force: true });
});

