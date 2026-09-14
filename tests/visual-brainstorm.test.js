import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

test('visual brainstorm file and server lifecycle regressions', () => {
  const result = spawnSync('python3', ['-B', fileURLToPath(new URL('./visual_brainstorm_test.py', import.meta.url)), '-v'], {
    encoding: 'utf8', timeout: 60000,
  });
  assert.equal(result.status, 0, result.error?.message ?? result.stdout + result.stderr);
});
