"""Isolated session directories and checkpoint status tracking (stdlib only)."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/figure-out/scripts'
sys.path.insert(0, str(SCRIPTS))
from session import add_checkpoint, initialize, mark, set_status


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='figure-out-test-')
        self.root = Path(self.temp.name).resolve()
        self.directory = initialize('order-reconciliation', self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_sessions_are_isolated_and_environment_root_is_used(self):
        second = initialize('order-reconciliation', self.root)
        self.assertNotEqual(self.directory, second)
        result = subprocess.run(
            [sys.executable, '-B', str(SCRIPTS / 'session.py'), 'init', 'order-reconciliation'],
            env={**os.environ, 'AGENT_FIGURE_OUT_DIR': str(self.root)},
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(Path(json.loads(result.stdout)['session']).parent, self.root)
        with self.assertRaises(ValueError):
            initialize('../escape', self.root)

    def test_init_writes_record_outside_any_project_files(self):
        self.assertTrue((self.directory / 'session.md').is_file())
        self.assertTrue((self.directory / 'checkpoints.json').is_file())
        self.assertIn('Status: exploring', (self.directory / 'session.md').read_text())
        self.assertTrue(self.directory.is_relative_to(self.root))
        self.assertEqual(sorted(path.name for path in self.directory.iterdir()), ['checkpoints.json', 'session.md'])

    def test_add_and_mark_checkpoints(self):
        added = add_checkpoint(self.directory, 'T1', title='回调对账边界', status='waiting')
        self.assertEqual(added['status'], 'waiting')
        marked = mark(self.directory, 'T1', 'confirmed')
        self.assertEqual(marked['status'], 'confirmed')
        manifest = json.loads((self.directory / 'checkpoints.json').read_text())
        self.assertEqual(manifest['checkpoints'][0]['id'], 'T1')
        self.assertEqual(manifest['checkpoints'][0]['title'], '回调对账边界')
        self.assertEqual(manifest['checkpoints'][0]['status'], 'confirmed')
        add_checkpoint(self.directory, 'T2', title='失败补偿')
        self.assertEqual(len(json.loads((self.directory / 'checkpoints.json').read_text())['checkpoints']), 2)

    def test_checkpoint_and_status_validation(self):
        for bad in ['../evil', 'has space', '', '1leading', 'x' * 33]:
            with self.assertRaises(ValueError):
                add_checkpoint(self.directory, bad)
        with self.assertRaises(ValueError):
            add_checkpoint(self.directory, 'T1', status='done')
        with self.assertRaises(ValueError):
            mark(self.directory, 'missing', 'confirmed')
        add_checkpoint(self.directory, 'T1')
        with self.assertRaises(ValueError):
            mark(self.directory, 'T1', 'done')

    def test_session_status_and_corrupt_manifest(self):
        result = set_status(self.directory, 'planning')
        self.assertEqual(result['status'], 'planning')
        manifest = json.loads((self.directory / 'checkpoints.json').read_text())
        self.assertEqual(manifest['status'], 'planning')
        with self.assertRaises(ValueError):
            set_status(self.directory, 'approved')
        (self.directory / 'checkpoints.json').write_text('{')
        with self.assertRaises(ValueError):
            mark(self.directory, 'T1', 'confirmed')

    def test_cli_errors_are_clear(self):
        failed = subprocess.run(
            [sys.executable, '-B', str(SCRIPTS / 'session.py'), 'init', 'Not A Slug'],
            env={**os.environ, 'AGENT_FIGURE_OUT_DIR': str(self.root)},
            capture_output=True, text=True,
        )
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn('Session error:', failed.stderr)
        self.assertNotIn('Traceback', failed.stderr)

    def test_mark_does_not_rewrite_session_record(self):
        record = self.directory / 'session.md'
        record.write_text('# order-reconciliation\n\nUser answer: 选 A\n')
        add_checkpoint(self.directory, 'T1', title='状态机')
        mark(self.directory, 'T1', 'confirmed')
        self.assertEqual(record.read_text(), '# order-reconciliation\n\nUser answer: 选 A\n')


if __name__ == '__main__':
    unittest.main()
