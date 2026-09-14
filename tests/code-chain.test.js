import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { createContext, listAvailableSkills, run } from '../bin/lib.js';

test('code-chain is discoverable and installs its runtime resources', async () => {
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'code-chain-install-'));
  try {
    const ctx = createContext({ home, cwd: home, log: () => {} });
    assert.ok(listAvailableSkills(ctx).some((skill) => skill.name === 'code-chain'));
    const result = await run(['node', 'cli.js', 'add', 'code-chain', '--agent', 'codex'], ctx);
    assert.equal(result, 0);
    const installed = path.join(home, '.codex', 'skills', 'code-chain');
    for (const file of [
      'SKILL.md',
      'references/trace.md',
      'references/mermaid.md',
    ]) {
      assert.ok(fs.existsSync(path.join(installed, file)), `missing installed resource: ${file}`);
    }
  } finally {
    fs.rmSync(home, { recursive: true, force: true });
  }
});
