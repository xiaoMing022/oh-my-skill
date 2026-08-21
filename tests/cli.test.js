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
} from '../bin/lib.js';

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
  const parsed = parseArgs(['node', 'cli.js', 'add', 'design-preview', '-a', 'grok,claude', '--all']);
  assert.equal(parsed.command, 'add');
  assert.deepEqual(parsed.rest, ['design-preview']);
  assert.equal(parsed.flags.all, true);
  assert.deepEqual(parsed.flags.agents, ['grok', 'claude']);
});

test('parseArgs rejects unknown flags', () => {
  assert.throws(() => parseArgs(['node', 'cli.js', 'list', '--nope']), /Unknown option/);
});

test('parseFrontmatter reads folded descriptions', () => {
  const content = fs.readFileSync(path.join(PKG_ROOT, 'skills', 'design-preview', 'SKILL.md'), 'utf8');
  const fm = parseFrontmatter(content);
  assert.equal(fm.name, 'design-preview');
  assert.match(fm.description, /Show reference visuals/);
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
  const code = await run(['node', 'cli.js', 'add', 'design-preview', '--agent', 'grok,agents'], ctx);
  assert.equal(code, 0);

  const stored = path.join(storeDir(home), 'skills', 'design-preview', 'SKILL.md');
  const grokLink = path.join(home, '.grok', 'skills', 'design-preview');
  const agentsLink = path.join(home, '.agents', 'skills', 'design-preview');
  assert.equal(fs.existsSync(stored), true);
  assert.equal(fs.lstatSync(grokLink).isSymbolicLink(), true);
  assert.equal(fs.realpathSync(grokLink), fs.realpathSync(path.dirname(stored)));
  assert.equal(fs.lstatSync(agentsLink).isSymbolicLink(), true);
  assert.equal(isManagedPath(grokLink, ctx), true);

  const meta = JSON.parse(fs.readFileSync(path.join(storeDir(home), 'install.json'), 'utf8'));
  assert.deepEqual(meta.installed, ['design-preview']);

  fs.rmSync(home, { recursive: true, force: true });
});

test('remove --agent keeps the store when other agents may still use it', async () => {
  const home = tmpHome();
  fs.mkdirSync(path.join(home, '.grok'));
  fs.mkdirSync(path.join(home, '.cursor'));
  const { log } = collectLog();
  const ctx = createContext({ home, cwd: home, log });
  await run(['node', 'cli.js', 'add', 'design-preview', '--agent', 'grok,cursor'], ctx);
  const code = await run(['node', 'cli.js', 'remove', 'design-preview', '--agent', 'cursor'], ctx);
  assert.equal(code, 0);
  assert.equal(fs.existsSync(path.join(home, '.cursor', 'skills', 'design-preview')), false);
  assert.equal(fs.existsSync(path.join(home, '.grok', 'skills', 'design-preview')), true);
  assert.equal(fs.existsSync(path.join(storeDir(home), 'skills', 'design-preview', 'SKILL.md')), true);
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
  const dest = path.join(home, '.grok', 'skills', 'design-preview');
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
  const dest = path.join(home, '.grok', 'skills', 'design-preview');
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.symlinkSync('/Users/a1021500136/Desktop/oh-my-skills/design-preview', dest);
  const { log } = collectLog();
  const ctx = createContext({ home, cwd: home, log });
  const code = await run(['node', 'cli.js', 'add', 'design-preview', '--agent', 'grok'], ctx);
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
  assert.match(list.stdout, /design-preview/);
  assert.match(list.stdout, /html-prototype/);
});
