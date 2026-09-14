"""Observable preview lifecycle, tabbed-session, and file-preservation regressions (stdlib only)."""
import concurrent.futures
import html
import json
import os
import socket
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/visual-brainstorm/scripts'
sys.path.insert(0, str(SCRIPTS))
from render import atomic_write, render, render_checkpoint, render_session, server_request
from session import initialize, mark, publish


class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='visual-brainstorm-test-')
        self.root = Path(self.temp.name).resolve()
        self.directory = initialize('support-ui', self.root)
        self.source = self.directory / 'draft.fragment.html'
        self.source.write_text('<h1>D1 — 导航</h1><button data-choice="A">A</button>')
        published = publish(self.directory, self.source, checkpoint='D1', title='导航')
        self.fragment = Path(published['fragment'])
        self.info = self.directory / 'serve.json'
        self.processes = []

    def tearDown(self):
        for process in self.processes:
            if process.poll() is None:
                process.terminate()
            process.communicate(timeout=5)
        self.temp.cleanup()

    def command(self, *args, source=None):
        return [sys.executable, '-B', str(SCRIPTS / 'render.py'),
                str(source or self.directory), *map(str, args)]

    def start(self, idle=60, info=None):
        process = subprocess.Popen(self.command('--serve', '--info', info or self.info,
                                                '--idle-timeout', idle),
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.processes.append(process)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if process.poll() is not None:
                self.fail(process.communicate()[1])
            try:
                result = server_request(info or self.info, self.directory)
                return process, result['url']
            except (OSError, ValueError):
                time.sleep(.03)
        self.fail('preview did not become ready')

    def test_sessions_are_isolated_and_environment_root_is_used(self):
        second = initialize('support-ui', self.root)
        self.assertNotEqual(self.directory, second)
        result = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'session.py'), 'init', 'support-ui'],
                                env={**os.environ, 'AGENT_VISUALIZATIONS_DIR': str(self.root)},
                                capture_output=True, text=True, check=True)
        self.assertEqual(Path(json.loads(result.stdout)['session']).parent, self.root)
        with self.assertRaises(ValueError):
            initialize('../escape', self.root)

    def test_revision_history_invalid_publish_and_restore(self):
        first = next(iter((self.directory / 'revisions').iterdir()))
        original = self.fragment.read_bytes()
        for content in [b'', b'\xff', b'<html><body>wrong</body></html>', b'x' * 1_000_001]:
            self.source.write_bytes(content)
            with self.assertRaises(ValueError):
                publish(self.directory, self.source, checkpoint='D1')
            self.assertEqual(self.fragment.read_bytes(), original)
        self.source.write_text('<h1>D2 density</h1>')
        second = publish(self.directory, self.source, checkpoint='D2', title='密度')
        # Publishing another checkpoint never touches earlier tabs or snapshots.
        self.assertEqual(self.fragment.read_bytes(), original)
        self.assertEqual(first.read_bytes(), original)
        self.assertEqual(Path(second['fragment']).read_text(), '<h1>D2 density</h1>')
        self.assertTrue(Path(second['revision']).name.startswith('D2-'))
        restored = publish(self.directory, first, checkpoint='D1')
        self.assertEqual(Path(restored['fragment']).read_bytes(), original)
        self.assertEqual(first.read_bytes(), original)

    def test_checkpoint_and_status_validation(self):
        for bad in ['../evil', 'has space', '', '1leading', 'x' * 33]:
            with self.assertRaises(ValueError):
                publish(self.directory, self.source, checkpoint=bad)
        with self.assertRaises(ValueError):
            publish(self.directory, self.source, checkpoint='D1', status='done')
        with self.assertRaises(ValueError):
            mark(self.directory, 'missing', 'confirmed')
        with self.assertRaises(ValueError):
            mark(self.directory, 'D1', 'done')

    def test_tabs_accumulate_and_same_url_updates(self):
        process, url = self.start()
        with urlopen(url) as response:
            self.assertEqual(response.headers['Cache-Control'], 'no-store')
            body = html.unescape(response.read().decode())
            self.assertIn('role="tablist"', body)
            self.assertIn('待选择', body)
            # Live shell loads checkpoints on demand instead of inlining them.
            self.assertIn('src="/checkpoint/D1"', body)
            self.assertNotIn('D1 — 导航', body)
            self.assertIn('sandbox="allow-scripts"', body)
        with urlopen(url + 'checkpoint/D1') as response:
            frame = html.unescape(response.read().decode())
            self.assertIn('D1 — 导航', frame)
            self.assertEqual(frame.count('点选会记录为预选参考'), 1)
        with urlopen(url + '__version') as response:
            state = json.loads(response.read())
            first_etag = state['etag']
            self.assertEqual([cp['id'] for cp in state['checkpoints']], ['D1'])
            self.assertEqual(state['checkpoints'][0]['statusLabel'], '待选择')
        self.source.write_text('<h1>D2 density</h1>')
        publish(self.directory, self.source, checkpoint='D2', title='密度')
        mark(self.directory, 'D1', 'confirmed')
        with urlopen(url) as response:
            body = html.unescape(response.read().decode())
            # Both checkpoints stay viewable on the same URL, each in its own tab.
            self.assertEqual(body.count('role="tab"'), 2)
            self.assertIn('已确认', body)
            # The newest publication is the default active tab.
            self.assertIn('aria-selected="true" data-vb-tab="D2"', body)
        with urlopen(url + 'checkpoint/D2') as response:
            self.assertIn('D2 density', response.read().decode())
        with urlopen(url + '__version') as response:
            self.assertNotEqual(json.loads(response.read())['etag'], first_etag)
        for suffix in ['session.md', '../session.md', 'serve.json', 'checkpoints.json',
                       'checkpoints/D1.fragment.html', 'checkpoint/missing',
                       'checkpoint/../session.md']:
            with self.assertRaises(HTTPError) as raised:
                urlopen(url + suffix)
            self.assertEqual(raised.exception.code, 404)
            raised.exception.close()
        server_request(self.info, self.directory, stop=True)
        process.wait(timeout=5)
        self.assertFalse(self.info.exists())
        self.assertTrue(self.fragment.exists())
        _, new_url = self.start()
        with urlopen(new_url + 'checkpoint/D1') as response:
            self.assertIn('D1 — 导航', html.unescape(response.read().decode()))

    def test_on_page_choice_is_recorded_as_preview_feedback(self):
        _, url = self.start()
        choices = self.directory / 'choices.json'
        request = Request(url + '__choice', method='POST',
                          headers={'Content-Type': 'application/json'},
                          data=json.dumps({'checkpoint': 'D1', 'choice': 'A'}).encode())
        with urlopen(request) as response:
            self.assertTrue(json.loads(response.read())['ok'])
        recorded = json.loads(choices.read_text())
        self.assertEqual(recorded['D1']['choice'], 'A')
        self.assertIn('at', recorded['D1'])
        for bad in [{'checkpoint': 'missing', 'choice': 'A'},
                    {'checkpoint': 'D1', 'choice': ''},
                    {'checkpoint': 'D1', 'choice': 'x' * 300},
                    {'checkpoint': 'D1'}, 'not-a-dict']:
            with self.assertRaises(HTTPError) as raised:
                urlopen(Request(url + '__choice', method='POST',
                                data=json.dumps(bad).encode()))
            self.assertEqual(raised.exception.code, 400)
            raised.exception.close()
        # Later selections replace the checkpoint's entry, not the whole file.
        request = Request(url + '__choice', method='POST',
                          data=json.dumps({'checkpoint': 'D1', 'choice': 'B'}).encode())
        with urlopen(request):
            pass
        self.assertEqual(json.loads(choices.read_text())['D1']['choice'], 'B')

    def test_wrong_identity_cannot_stop_service_even_with_live_pid(self):
        process, url = self.start()
        original = json.loads(self.info.read_text())
        foreign = self.directory / 'foreign.json'
        foreign.write_text(json.dumps({**original, 'token': '0' * 64, 'pid': os.getpid()}))
        with self.assertRaises(ValueError):
            server_request(foreign, self.directory, stop=True)
        self.assertIsNone(process.poll())
        with self.assertRaises(HTTPError) as raised:
            urlopen(Request(url + '__stop', method='POST'))
        self.assertEqual(raised.exception.code, 403)
        raised.exception.close()
        foreign.write_text(json.dumps({**original, 'source': '/other/session'}))
        with self.assertRaises(ValueError):
            server_request(foreign, self.directory)
        self.assertIsNone(process.poll())

    def test_duplicate_start_preserves_owner(self):
        process, _ = self.start()
        original = self.info.read_bytes()
        duplicate = subprocess.run(self.command('--serve', '--info', self.info),
                                   capture_output=True, text=True, timeout=5)
        self.assertNotEqual(duplicate.returncode, 0)
        self.assertEqual(self.info.read_bytes(), original)
        self.assertIsNone(process.poll())
        self.assertEqual(server_request(self.info, self.directory)['status'], 'running')

    def test_idle_expiry_and_sigterm_remove_only_metadata(self):
        process, _ = self.start(idle=1)
        process.wait(timeout=5)
        self.assertFalse(self.info.exists())
        self.assertTrue(self.fragment.exists())
        process, _ = self.start()
        process.terminate()
        process.wait(timeout=5)
        self.assertFalse(self.info.exists())
        self.assertTrue((self.directory / 'session.md').exists())
        self.assertTrue((self.directory / 'checkpoints.json').exists())

    def test_startup_errors_and_invalid_utf8_are_clear(self):
        for port in [-1, 65536]:
            failed = subprocess.run(self.command('--serve', '--port', port),
                                    capture_output=True, text=True, timeout=5)
            self.assertNotEqual(failed.returncode, 0)
            self.assertNotIn('Traceback', failed.stderr)
        self.fragment.write_bytes(b'\xff')
        failed = subprocess.run(self.command('--serve', '--info', self.info),
                                capture_output=True, text=True, timeout=5)
        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse(self.info.exists())
        self.assertNotIn('Traceback', failed.stderr)
        not_a_session = subprocess.run(self.command('--serve', source=self.root),
                                       capture_output=True, text=True, timeout=5)
        self.assertNotEqual(not_a_session.returncode, 0)
        self.assertNotIn('Traceback', not_a_session.stderr)

    def test_port_collision_releases_metadata_reservation(self):
        with socket.socket() as occupied:
            occupied.bind(('127.0.0.1', 0))
            occupied.listen()
            failed = subprocess.run(self.command('--serve', '--info', self.info,
                                                 '--port', occupied.getsockname()[1]),
                                    capture_output=True, text=True, timeout=5)
        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse(self.info.exists())
        self.assertNotIn('Traceback', failed.stderr)

    def test_stale_metadata_recovery_and_corrupt_json(self):
        process, _ = self.start()
        process.kill()
        process.wait(timeout=5)
        self.assertTrue(self.info.exists())
        with self.assertRaises((OSError, ValueError)):
            server_request(self.info, self.directory)
        self.info.rename(self.directory / 'serve.stale.json')
        self.start()
        corrupt = self.directory / 'corrupt.json'
        for content in ['[]', '{', '{}']:
            corrupt.write_text(content)
            failed = subprocess.run(self.command('--status', '--info', corrupt),
                                    capture_output=True, text=True, timeout=5)
            self.assertNotEqual(failed.returncode, 0)
            self.assertNotIn('Traceback', failed.stderr)

    def test_export_protects_source_and_existing_destination(self):
        before = self.fragment.read_bytes()
        same = subprocess.run(self.command(self.fragment, '--force', source=self.fragment),
                              capture_output=True, timeout=5)
        self.assertNotEqual(same.returncode, 0)
        self.assertEqual(self.fragment.read_bytes(), before)
        export = self.root / 'export.html'
        export.write_text('user content')
        denied = subprocess.run(self.command(export, source=self.fragment),
                                capture_output=True, timeout=5)
        self.assertNotEqual(denied.returncode, 0)
        self.assertEqual(export.read_text(), 'user content')
        subprocess.run(self.command(export, '--force', source=self.fragment),
                       capture_output=True, check=True, timeout=5)
        self.assertIn('<!doctype html>', export.read_text())
        self.assertEqual(self.fragment.read_bytes(), before)
        # A session directory exports the whole tabbed document: offline,
        # self-contained (checkpoints inlined), and without live polling.
        self.source.write_text('<h1>D2 density</h1>')
        publish(self.directory, self.source, checkpoint='D2', title='密度')
        tabbed = self.root / 'session-export.html'
        subprocess.run(self.command(tabbed), capture_output=True, check=True, timeout=5)
        exported = html.unescape(tabbed.read_text())
        self.assertIn('role="tablist"', exported)
        self.assertIn('D1 — 导航', exported)
        self.assertIn('D2 density', exported)
        self.assertNotIn('__version', exported)
        self.assertNotIn('__choice', exported)
        self.assertNotIn('src="/checkpoint/', exported)

    def test_atomic_updates_never_serve_partial_documents(self):
        _, url = self.start()
        variants = ['<p>' + character * 40_000 + '</p>' for character in ['A', 'B']]
        atomic_write(self.fragment, variants[0])
        expected = {render_checkpoint(self.directory, 'D1')}
        shell = {render_session(self.directory, live=True)}
        atomic_write(self.fragment, variants[1])
        expected.add(render_checkpoint(self.directory, 'D1'))
        def writer():
            for i in range(30):
                atomic_write(self.fragment, variants[i % 2])
        with concurrent.futures.ThreadPoolExecutor() as executor:
            writing = executor.submit(writer)
            for _ in range(15):
                with urlopen(url + 'checkpoint/D1') as response:
                    self.assertIn(response.read().decode(), expected)
            writing.result()
        # The live shell itself does not embed fragment bytes.
        with urlopen(url) as response:
            self.assertIn(response.read().decode(), shell)


if __name__ == '__main__':
    unittest.main()
