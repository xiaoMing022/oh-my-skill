import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { createContext, listAvailableSkills, run } from '../bin/lib.js';

test('visualization session and static server regressions', () => {
  const result = spawnSync('python3', ['-B', fileURLToPath(new URL('./visualization_test.py', import.meta.url)), '-v'], {
    encoding: 'utf8', timeout: 60000,
  });
  assert.equal(result.status, 0, result.error?.message ?? result.stdout + result.stderr);
});

test('visualization is discoverable and installs its runtime resources', async () => {
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'visualization-install-'));
  try {
    const ctx = createContext({ home, cwd: home, log: () => {} });
    assert.ok(listAvailableSkills(ctx).some((skill) => skill.name === 'visualization'));
    const result = await run(['node', 'cli.js', 'add', 'visualization', '--agent', 'codex'], ctx);
    assert.equal(result, 0);
    const installed = path.join(home, '.codex', 'skills', 'visualization');
    for (const file of [
      'SKILL.md',
      'references/session.md',
      'references/render-kit.md',
      'references/charts.md',
      'references/maps.md',
      'assets/frame.html',
      'assets/visualize.css',
      'assets/visualize.html',
      'scripts/session.py',
      'scripts/serve.py',
    ]) {
      assert.ok(fs.existsSync(path.join(installed, file)), `missing installed resource: ${file}`);
    }
  } finally {
    fs.rmSync(home, { recursive: true, force: true });
  }
});
