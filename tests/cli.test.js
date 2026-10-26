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
import { shouldPrompt, truncatePlain, fitPlainWidth, visibleWidth } from '../bin/prompt.js';

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
  const parsed = parseArgs(['node', 'cli.js', 'add', 'oms-visualization', '-a', 'grok,claude', '--all']);
  assert.equal(parsed.command, 'add');
  assert.deepEqual(parsed.rest, ['oms-visualization']);
  assert.equal(parsed.flags.all, true);
  assert.deepEqual(parsed.flags.agents, ['grok', 'claude']);
});

test('parseArgs rejects unknown flags', () => {
  assert.throws(() => parseArgs(['node', 'cli.js', 'list', '--nope']), /Unknown option/);
});

test('parseFrontmatter reads folded descriptions', () => {
  const content = fs.readFileSync(path.join(PKG_ROOT, 'skills', 'oms-visualization', 'SKILL.md'), 'utf8');
  const fm = parseFrontmatter(content);
  assert.equal(fm.name, 'oms-visualization');
  assert.match(fm.description, /Show instead of tell/);
  assert.doesNotMatch(fm.description, /\n/);
});

test('findAgent resolves aliases', () => {
  assert.equal(findAgent('claude-code').id, 'claude');
  assert.equal(findAgent('cline').id, 'agents');
  assert.equal(findAgent('agy').id, 'antigravity-cli');
  assert.equal(findAgent('openai').id, 'codex');
  assert.equal(findAgent('open-code').id, 'opencode');
  assert.equal(findAgent('hermes-agent').id, 'hermes');
  assert.equal(findAgent('nous').id, 'hermes');
  assert.equal(findAgent('work-buddy').id, 'workbuddy');
  assert.equal(findAgent('wb').id, 'workbuddy');
  assert.equal(findAgent('pi-coding-agent').id, 'pi');
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
  assert.ok(targets.some((t) => t.id === 'opencode'));
  assert.ok(targets.some((t) => t.id === 'hermes' && t.path.endsWith(path.join('.hermes', 'skills'))));
  assert.ok(targets.some((t) => t.id === 'workbuddy' && t.path.endsWith(path.join('.workbuddy', 'skills'))));
  assert.ok(targets.some((t) => t.id === 'pi' && t.path.endsWith(path.join('.pi', 'agent', 'skills'))));
  assert.ok(!targets.some((t) => t.path.includes(`${path.sep}plugins${path.sep}`) && t.id === 'claude'));
  fs.rmSync(home, { recursive: true, force: true });
});

test('hermes respects HERMES_HOME and has no project path', () => {
  const home = tmpHome();
  const profile = path.join(home, 'custom-hermes');
  const prev = process.env.HERMES_HOME;
  process.env.HERMES_HOME = profile;
  try {
    const targets = resolveTargets({ flags: { agents: ['hermes'], project: false }, home, cwd: home });
    assert.equal(targets.length, 1);
    assert.equal(targets[0].path, path.join(profile, 'skills'));
    const projectTargets = resolveTargets({ flags: { agents: ['hermes'], project: true }, home, cwd: home });
    assert.equal(projectTargets.length, 0);
  } finally {
    if (prev === undefined) delete process.env.HERMES_HOME;
    else process.env.HERMES_HOME = prev;
    fs.rmSync(home, { recursive: true, force: true });
  }
});

test('add installs into codex, opencode, hermes, workbuddy, and pi', async () => {
  const home = tmpHome();
  for (const dir of [
    path.join(home, '.codex'),
    path.join(home, '.config', 'opencode'),
    path.join(home, '.hermes'),
    path.join(home, '.workbuddy'),
    path.join(home, '.pi'),
  ]) {
    fs.mkdirSync(dir, { recursive: true });
  }
  const { log } = collectLog();
  const ctx = createContext({ home, cwd: home, log });
  const code = await run([
    'node', 'cli.js', 'add', 'oms-designer',
    '--agent', 'codex,opencode,hermes,workbuddy,pi',
  ], ctx);
  assert.equal(code, 0);
  assert.equal(fs.existsSync(path.join(home, '.codex', 'skills', 'oms-designer', 'SKILL.md')), true);
  assert.equal(fs.existsSync(path.join(home, '.config', 'opencode', 'skills', 'oms-designer', 'SKILL.md')), true);
  assert.equal(fs.existsSync(path.join(home, '.hermes', 'skills', 'oms-designer', 'SKILL.md')), true);
  assert.equal(fs.existsSync(path.join(home, '.workbuddy', 'skills', 'oms-designer', 'SKILL.md')), true);
  assert.equal(fs.existsSync(path.join(home, '.pi', 'agent', 'skills', 'oms-designer', 'SKILL.md')), true);
  fs.rmSync(home, { recursive: true, force: true });
});

test('add copies into store then symlinks agent dirs', async () => {
  const home = tmpHome();
  fs.mkdirSync(path.join(home, '.grok'));
  const { log } = collectLog();
  const ctx = createContext({ home, cwd: home, log });
  const code = await run(['node', 'cli.js', 'add', 'oms-visualization', '--agent', 'grok,agents'], ctx);
  assert.equal(code, 0);

  const stored = path.join(storeDir(home), 'skills', 'oms-visualization', 'SKILL.md');
  const grokLink = path.join(home, '.grok', 'skills', 'oms-visualization');
  const agentsLink = path.join(home, '.agents', 'skills', 'oms-visualization');
  assert.equal(fs.existsSync(stored), true);
  assert.equal(fs.lstatSync(grokLink).isSymbolicLink(), true);
  assert.equal(fs.realpathSync(grokLink), fs.realpathSync(path.dirname(stored)));
  assert.equal(fs.lstatSync(agentsLink).isSymbolicLink(), true);
  assert.equal(isManagedPath(grokLink, ctx), true);

  const meta = JSON.parse(fs.readFileSync(path.join(storeDir(home), 'install.json'), 'utf8'));
  assert.deepEqual(meta.installed, ['oms-visualization']);

  fs.rmSync(home, { recursive: true, force: true });
});

test('remove --agent keeps the store when other agents may still use it', async () => {
  const home = tmpHome();
  fs.mkdirSync(path.join(home, '.grok'));
  fs.mkdirSync(path.join(home, '.cursor'));
  const { log } = collectLog();
  const ctx = createContext({ home, cwd: home, log });
  await run(['node', 'cli.js', 'add', 'oms-visualization', '--agent', 'grok,cursor'], ctx);
  const code = await run(['node', 'cli.js', 'remove', 'oms-visualization', '--agent', 'cursor'], ctx);
  assert.equal(code, 0);
  assert.equal(fs.existsSync(path.join(home, '.cursor', 'skills', 'oms-visualization')), false);
  assert.equal(fs.existsSync(path.join(home, '.grok', 'skills', 'oms-visualization')), true);
  assert.equal(fs.existsSync(path.join(storeDir(home), 'skills', 'oms-visualization', 'SKILL.md')), true);
  fs.rmSync(home, { recursive: true, force: true });
});

test('--project copies instead of symlinking', async () => {
  const home = tmpHome();
  const project = fs.mkdtempSync(path.join(os.tmpdir(), 'oms-proj-'));
  const { log } = collectLog();
  const ctx = createContext({ home, cwd: project, log });
  const code = await run(['node', 'cli.js', 'add', 'oms-designer', '--project', '--agent', 'agents'], ctx);
  assert.equal(code, 0);
  const dest = path.join(project, '.agents', 'skills', 'oms-designer');
  assert.equal(fs.existsSync(path.join(dest, 'SKILL.md')), true);
  assert.equal(fs.lstatSync(dest).isSymbolicLink(), false);
  fs.rmSync(home, { recursive: true, force: true });
  fs.rmSync(project, { recursive: true, force: true });
});

test('doctor reports broken grok links', async () => {
  const home = tmpHome();
  const dest = path.join(home, '.grok', 'skills', 'oms-visualization');
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
  const dest = path.join(home, '.grok', 'skills', 'oms-visualization');
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.symlinkSync(path.join(home, 'missing-visualization'), dest);
  const { log } = collectLog();
  const ctx = createContext({ home, cwd: home, log });
  const code = await run(['node', 'cli.js', 'add', 'oms-visualization', '--agent', 'grok'], ctx);
  assert.equal(code, 0);
  assert.equal(fs.existsSync(path.join(dest, 'SKILL.md')), true);
  fs.rmSync(home, { recursive: true, force: true });
});

test('short skill aliases resolve to oms- names', async () => {
  const home = tmpHome();
  fs.mkdirSync(path.join(home, '.grok'));
  const { log } = collectLog();
  const ctx = createContext({ home, cwd: home, log });
  const code = await run(['node', 'cli.js', 'add', 'visualization', '--agent', 'grok'], ctx);
  assert.equal(code, 0);
  assert.equal(fs.existsSync(path.join(home, '.grok', 'skills', 'oms-visualization', 'SKILL.md')), true);
  assert.equal(fs.existsSync(path.join(home, '.grok', 'skills', 'visualization')), false);
  fs.rmSync(home, { recursive: true, force: true });
});

test('add migrates a managed legacy bare-name install', async () => {
  const home = tmpHome();
  const store = storeDir(home);
  const legacyStore = path.join(store, 'skills', 'visualization');
  fs.mkdirSync(legacyStore, { recursive: true });
  fs.writeFileSync(path.join(legacyStore, 'SKILL.md'), '---\nname: visualization\n---\n');
  fs.writeFileSync(path.join(store, 'install.json'), JSON.stringify({
    package: '@lxy10086/oh-my-skills', version: '0.1.6', installed: ['visualization'],
  }));
  const legacyDest = path.join(home, '.grok', 'skills', 'visualization');
  fs.mkdirSync(path.dirname(legacyDest), { recursive: true });
  fs.symlinkSync(legacyStore, legacyDest);

  const { log } = collectLog();
  const ctx = createContext({ home, cwd: home, log });
  const code = await run(['node', 'cli.js', 'add', 'oms-visualization', '--agent', 'grok'], ctx);
  assert.equal(code, 0);
  assert.equal(fs.existsSync(legacyDest), false);
  assert.equal(fs.existsSync(legacyStore), false);
  assert.equal(fs.existsSync(path.join(home, '.grok', 'skills', 'oms-visualization', 'SKILL.md')), true);
  fs.rmSync(home, { recursive: true, force: true });
});

test('add leaves an unrelated bare-name skill alone', async () => {
  const home = tmpHome();
  const unrelated = path.join(home, '.grok', 'skills', 'designer');
  fs.mkdirSync(unrelated, { recursive: true });
  fs.writeFileSync(path.join(unrelated, 'SKILL.md'), '---\nname: designer\n---\n');

  const { log } = collectLog();
  const ctx = createContext({ home, cwd: home, log });
  const code = await run(['node', 'cli.js', 'add', 'oms-designer', '--agent', 'grok'], ctx);
  assert.equal(code, 0);
  assert.equal(fs.existsSync(path.join(unrelated, 'SKILL.md')), true);
  assert.equal(fs.existsSync(path.join(home, '.grok', 'skills', 'oms-designer', 'SKILL.md')), true);
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
  assert.match(list.stdout, /oms-visualization/);
  assert.match(list.stdout, /oms-brainstorming/);
  assert.match(list.stdout, /oms-code-chain/);
  assert.match(list.stdout, /oms-designer/);
});

test('renderBanner is a large pixel wordmark', () => {
  const banner = renderBanner({ columns: 80, version: '0.1.1' });
  assert.match(banner, /PIXEL SKILLS FOR EVERY AGENT/);
  assert.match(banner, /oms-designer/);
  assert.match(banner, /█/);
  assert.ok(banner.split('\n').length >= 16);
});

test('shouldPrompt only in an interactive TTY without -y', () => {
  assert.equal(shouldPrompt({ isTTY: true }, { yes: false, dryRun: false }), true);
  assert.equal(shouldPrompt({ isTTY: false }, { yes: false, dryRun: false }), false);
  assert.equal(shouldPrompt({ isTTY: true }, { yes: true, dryRun: false }), false);
  assert.equal(shouldPrompt({ isTTY: true }, { yes: false, dryRun: true }), false);
});

test('picker line helpers keep rows within terminal width', () => {
  assert.equal(truncatePlain('abcdefghij', 7), 'abcdef…');
  assert.ok(visibleWidth(fitPlainWidth(`${'\x1b[32m'}◉${'\x1b[0m'}  ` + 'x'.repeat(120), 40)) <= 40);
});

test('picker line helpers count CJK characters as two columns', () => {
  assert.equal(visibleWidth('业务流程'), 8);
  assert.equal(visibleWidth('a，b'), 4);
  const hint = '根据实际源码编写简洁的业务流程与用户提示文档，整理接口参数和响应、触发规则、状态反馈';
  const cut = truncatePlain(hint, 21);
  assert.ok(visibleWidth(cut) <= 21);
  assert.ok(cut.endsWith('…'));
  assert.ok(visibleWidth(fitPlainWidth(`  oms-process-docs  ${hint}`, 60)) <= 60);
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
  assert.match(result.stdout, /oms-visualization/);
  fs.rmSync(home, { recursive: true, force: true });
});
