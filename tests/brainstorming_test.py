"""Isolated session directories and checkpoint status tracking (stdlib only)."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/brainstorming/scripts'
sys.path.insert(0, str(SCRIPTS))
from session import add_checkpoint, initialize, mark, set_status


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='brainstorming-test-')
        self.root = Path(self.temp.name).resolve()
        self.directory = initialize('order-reconciliation', self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_sessions_are_isolated_and_environment_root_is_used(self):
        second = initialize('order-reconciliation', self.root)
        self.assertNotEqual(self.directory, second)
        result = subprocess.run(
            [sys.executable, '-B', str(SCRIPTS / 'session.py'), 'init', 'order-reconciliation'],
            env={**os.environ, 'AGENT_BRAINSTORMING_DIR': str(self.root)},
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(Path(json.loads(result.stdout)['session']).parent, self.root)
        with self.assertRaises(ValueError):
            initialize('../escape', self.root)

    def test_init_writes_record_under_converged_working_root(self):
        self.assertTrue((self.directory / 'session.md').is_file())
        self.assertTrue((self.directory / 'checkpoints.json').is_file())
        self.assertIn('Status: exploring', (self.directory / 'session.md').read_text())
        self.assertTrue(self.directory.is_relative_to(self.root))
        self.assertEqual(sorted(path.name for path in self.directory.iterdir()), ['checkpoints.json', 'session.md'])

    def test_add_and_mark_checkpoints(self):
        added = add_checkpoint(self.directory, 'D1', title='意图与成功标准', status='waiting')
        self.assertEqual(added['status'], 'waiting')
        marked = mark(self.directory, 'D1', 'confirmed')
        self.assertEqual(marked['status'], 'confirmed')
        manifest = json.loads((self.directory / 'checkpoints.json').read_text())
        self.assertEqual(manifest['checkpoints'][0]['id'], 'D1')
        self.assertEqual(manifest['checkpoints'][0]['title'], '意图与成功标准')
        self.assertEqual(manifest['checkpoints'][0]['status'], 'confirmed')
        add_checkpoint(self.directory, 'D2', title='非目标与反目标')
        self.assertEqual(len(json.loads((self.directory / 'checkpoints.json').read_text())['checkpoints']), 2)

    def test_checkpoint_and_status_validation(self):
        for bad in ['../evil', 'has space', '', '1leading', 'x' * 33]:
            with self.assertRaises(ValueError):
                add_checkpoint(self.directory, bad)
        with self.assertRaises(ValueError):
            add_checkpoint(self.directory, 'D1', status='done')
        with self.assertRaises(ValueError):
            mark(self.directory, 'missing', 'confirmed')
        add_checkpoint(self.directory, 'D1')
        with self.assertRaises(ValueError):
            mark(self.directory, 'D1', 'done')

    def test_session_status_and_corrupt_manifest(self):
        result = set_status(self.directory, 'planning')
        self.assertEqual(result['status'], 'planning')
        manifest = json.loads((self.directory / 'checkpoints.json').read_text())
        self.assertEqual(manifest['status'], 'planning')
        with self.assertRaises(ValueError):
            set_status(self.directory, 'approved')
        (self.directory / 'checkpoints.json').write_text('{')
        with self.assertRaises(ValueError):
            mark(self.directory, 'D1', 'confirmed')

    def test_cli_errors_are_clear(self):
        failed = subprocess.run(
            [sys.executable, '-B', str(SCRIPTS / 'session.py'), 'init', 'Not A Slug'],
            env={**os.environ, 'AGENT_BRAINSTORMING_DIR': str(self.root)},
            capture_output=True, text=True,
        )
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn('Session error:', failed.stderr)
        self.assertNotIn('Traceback', failed.stderr)

    def test_mark_does_not_rewrite_session_record(self):
        record = self.directory / 'session.md'
        record.write_text('# order-reconciliation\n\nUser answer: 做什么\n')
        add_checkpoint(self.directory, 'D1', title='意图')
        mark(self.directory, 'D1', 'confirmed')
        self.assertEqual(record.read_text(), '# order-reconciliation\n\nUser answer: 做什么\n')


if __name__ == '__main__':
    unittest.main()
