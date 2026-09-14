import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { createContext, listAvailableSkills, run } from '../bin/lib.js';

test('frontend design context isolation and preservation', () => {
  const result = spawnSync('python3', ['-B', fileURLToPath(new URL('./frontend_design_test.py', import.meta.url)), '-v'], {
    encoding: 'utf8', timeout: 30000,
  });
  assert.equal(result.status, 0, result.error?.message ?? result.stdout + result.stderr);
});

test('my-designer is discoverable and installs its runtime resources', async () => {
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'my-designer-install-'));
  try {
    const ctx = createContext({ home, cwd: home, log: () => {} });
    assert.ok(listAvailableSkills(ctx).some((skill) => skill.name === 'my-designer'));
    const result = await run(['node', 'cli.js', 'add', 'my-designer', '--agent', 'codex'], ctx);
    assert.equal(result, 0);
    const installed = path.join(home, '.codex', 'skills', 'my-designer');
    for (const file of ['SKILL.md', 'references/design-context.md', 'references/implementation.md', 'scripts/design_context.py']) {
      assert.ok(fs.existsSync(path.join(installed, file)), `missing installed resource: ${file}`);
    }
  } finally {
    fs.rmSync(home, { recursive: true, force: true });
  }
});
