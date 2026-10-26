"""Project-local framed sessions and static preview regressions (stdlib only)."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.request import urlopen

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/oms-visualization/scripts'
sys.path.insert(0, str(SCRIPTS))
from session import _prune_candidates, initialize, list_sessions, mark, prune, publish


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='visualization-test-')
        self.root = Path(self.temp.name).resolve() / '.oh-my-skills' / 'visualization'
        self.directory = initialize('support-ui', self.root)
        self.source = self.directory / 'draft.fragment.html'
        self.source.write_text('<h1>D1 导航</h1><button data-choice="A">A</button>')

    def tearDown(self):
        self.temp.cleanup()

    def test_init_is_deterministic_under_project_root(self):
        self.assertEqual(self.directory.parent, self.root)
        self.assertEqual(self.directory.name, 'support-ui')
        second = initialize('support-ui', self.root)
        self.assertEqual(second.name, 'support-ui-2')
        self.assertTrue((self.root / '.gitignore').is_file())
        self.assertIn('serve.json', (self.root / '.gitignore').read_text())
        with self.assertRaises(ValueError):
            initialize('../escape', self.root)

    def test_publish_wraps_frame_and_snapshot_sequence(self):
        published = publish(self.directory, self.source, checkpoint='D1', title='导航')
        self.assertEqual(published['revision_label'], 'R1')
        page = (self.directory / 'checkpoints' / 'D1.html').read_text()
        self.assertIn('OH-MY SKILLS', page)
        self.assertIn('LOGO SLOT', page)
        self.assertIn('请在对话里回复确认', page)
        self.assertIn('D1', page)
        self.assertNotIn('postMessage', page)
        self.assertNotIn('__choice', page)
        fragment = (self.directory / 'checkpoints' / 'D1.fragment.html').read_text()
        self.assertIn('data-choice="A"', fragment)
        self.assertTrue((self.directory / 'revisions' / 'D1-01.html').is_file())
        self.assertTrue((self.directory / 'revisions' / 'D1-01.fragment.html').is_file())
        published2 = publish(self.directory, self.source, checkpoint='D1', title='导航')
        self.assertEqual(published2['revision_label'], 'R2')
        self.assertTrue((self.directory / 'revisions' / 'D1-02.html').is_file())
        manifest = json.loads((self.directory / 'checkpoints.json').read_text())
        self.assertEqual(manifest['checkpoints'][0]['file'], 'checkpoints/D1.html')
        index = (self.directory / 'index.html').read_text()
        self.assertIn('checkpoints/D1.html', index)
        self.assertIn('待选择', index)
        self.assertFalse((self.directory / 'choices.json').exists())

    def test_publish_validation(self):
        bad = self.directory / 'bad.fragment.html'
        bad.write_text('<!doctype html><html></html>')
        with self.assertRaises(ValueError):
            publish(self.directory, bad, checkpoint='D1')
        bad.write_text('   ')
        with self.assertRaises(ValueError):
            publish(self.directory, bad, checkpoint='D1')
        with self.assertRaises(ValueError):
            publish(self.directory, self.source, checkpoint='1bad')
        self.assertFalse((self.directory / 'checkpoints' / 'D1.html').exists())

    def test_mark_regenerates_index_badges(self):
        publish(self.directory, self.source, checkpoint='D1', title='导航')
        mark(self.directory, 'D1', 'confirmed')
        index = (self.directory / 'index.html').read_text()
        self.assertIn('已确认', index)
        with self.assertRaises(ValueError):
            mark(self.directory, 'missing', 'confirmed')

    def test_cli_errors_are_clear(self):
        failed = subprocess.run(
            [sys.executable, '-B', str(SCRIPTS / 'session.py'), 'init', 'Not A Slug'],
            capture_output=True, text=True, cwd=self.temp.name,
        )
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn('Session error:', failed.stderr)
        self.assertNotIn('Traceback', failed.stderr)

    def test_list_and_prune(self):
        publish(self.directory, self.source, checkpoint='D1')
        other = initialize('other-flow', self.root)
        sessions = list_sessions(self.root)
        self.assertEqual({s['slug'] for s in sessions}, {'support-ui', 'other-flow'})
        listed = subprocess.run(
            [sys.executable, '-B', str(SCRIPTS / 'session.py'), 'prune', str(other)],
            capture_output=True, text=True, cwd=self.temp.name,
        )
        self.assertEqual(listed.returncode, 0)
        self.assertIn('candidates', listed.stdout)
        self.assertTrue(other.is_dir())
        removed = subprocess.run(
            [sys.executable, '-B', str(SCRIPTS / 'session.py'), 'prune', str(other), '--force'],
            capture_output=True, text=True, cwd=self.temp.name,
        )
        self.assertEqual(removed.returncode, 0)
        self.assertIn('removed', removed.stdout)
        self.assertFalse(other.exists())
        self.assertTrue(self.directory.is_dir())
        self.assertEqual(_prune_candidates(self.directory, self.root, None), [self.directory])


class StaticServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='visualization-serve-')
        self.root = Path(self.temp.name).resolve() / '.oh-my-skills' / 'visualization'
        self.directory = initialize('serve-check', self.root)
        source = self.directory / 'draft.fragment.html'
        source.write_text('<h1>hello</h1>')
        publish(self.directory, source, checkpoint='D1', title='页')
        self.info = self.directory / 'serve.json'
        self.process = None

    def tearDown(self):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            self.process.communicate(timeout=5)
        self.temp.cleanup()

    def test_static_serve_returns_no_store(self):
        self.process = subprocess.Popen(
            [sys.executable, '-B', str(SCRIPTS / 'serve.py'),
             '--root', str(self.directory), '--port', '0',
             '--info', str(self.info)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        deadline = time.monotonic() + 5
        url = None
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                self.fail(self.process.communicate()[1])
            if self.info.is_file():
                url = json.loads(self.info.read_text())['url']
                break
            time.sleep(0.05)
        self.assertIsNotNone(url)
        for path in ('', 'checkpoints/D1.html'):
            with urlopen(url + path) as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(response.headers.get('Cache-Control'), 'no-store')
                body = response.read().decode('utf-8')
                self.assertIn('OH-MY SKILLS', body)
        self.assertFalse((self.directory / 'choices.json').exists())


if __name__ == '__main__':
    unittest.main()
