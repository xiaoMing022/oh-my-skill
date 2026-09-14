import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { createContext, listAvailableSkills, run } from '../bin/lib.js';

test('figure-out session isolation and status tracking', () => {
  const result = spawnSync('python3', ['-B', fileURLToPath(new URL('./figure_out_test.py', import.meta.url)), '-v'], {
    encoding: 'utf8', timeout: 30000,
  });
  assert.equal(result.status, 0, result.error?.message ?? result.stdout + result.stderr);
});

test('figure-out is discoverable and installs its runtime resources', async () => {
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'figure-out-install-'));
  try {
    const ctx = createContext({ home, cwd: home, log: () => {} });
    assert.ok(listAvailableSkills(ctx).some((skill) => skill.name === 'figure-out'));
    const result = await run(['node', 'cli.js', 'add', 'figure-out', '--agent', 'codex'], ctx);
    assert.equal(result, 0);
    const installed = path.join(home, '.codex', 'skills', 'figure-out');
    for (const file of [
      'SKILL.md',
      'references/session.md',
      'references/options.md',
      'references/plan-handoff.md',
      'scripts/session.py',
    ]) {
      assert.ok(fs.existsSync(path.join(installed, file)), `missing installed resource: ${file}`);
    }
  } finally {
    fs.rmSync(home, { recursive: true, force: true });
  }
});
