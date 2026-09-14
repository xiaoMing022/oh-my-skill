"""External design-context isolation and non-destructive recovery checks."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/my-designer/scripts'
sys.path.insert(0, str(SCRIPTS))
from design_context import locate


class DesignContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='my-designer-test-')
        self.root = Path(self.temp.name).resolve()
        self.project = self.root / 'repo'
        self.project.mkdir()
        self.cache = self.root / 'contexts'

    def tearDown(self):
        self.temp.cleanup()

    def test_lookup_is_read_only_and_initialization_preserves_record(self):
        initial = locate(self.project, root=self.cache)
        self.assertFalse(initial['exists'])
        self.assertFalse(self.cache.exists())
        created = locate(self.project, root=self.cache, initialize=True)
        self.assertEqual(created['directory'], initial['directory'])
        record = Path(created['record'])
        record.write_text('confirmed project decisions')
        repeated = locate(self.project, root=self.cache, initialize=True)
        self.assertEqual(record.read_text(), 'confirmed project decisions')
        self.assertTrue(repeated['source_revalidation_required'])
        self.assertEqual(list(self.project.iterdir()), [])

    def test_apps_repositories_and_worktrees_do_not_share_records(self):
        (self.project / 'apps/admin').mkdir(parents=True)
        (self.project / 'apps/store').mkdir()
        worktree = self.root / 'worktree'
        worktree.mkdir()
        other = self.root / 'other/repo'
        other.mkdir(parents=True)
        identities = [locate(self.project, root=self.cache)['directory'],
                      locate(self.project, app='apps/admin', root=self.cache)['directory'],
                      locate(self.project, app='apps/store', root=self.cache)['directory'],
                      locate(worktree, root=self.cache)['directory'],
                      locate(other, root=self.cache)['directory']]
        self.assertEqual(len(set(identities)), 5)

    def test_symlink_alias_resolves_to_same_project(self):
        alias = self.root / 'alias'
        alias.symlink_to(self.project, target_is_directory=True)
        self.assertEqual(locate(alias, root=self.cache), locate(self.project, root=self.cache))

    def test_storage_inside_project_and_escaped_apps_are_rejected(self):
        with self.assertRaises(ValueError):
            locate(self.project, root=self.project / '.hidden', initialize=True)
        for app in ['..', str(self.project)]:
            with self.assertRaises(ValueError):
                locate(self.project, app=app, root=self.cache, initialize=True)
        (self.project / 'escape').symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            locate(self.project, app='escape', root=self.cache, initialize=True)
        self.assertFalse(self.cache.exists())

    def test_partial_or_foreign_context_is_not_silently_adopted(self):
        created = locate(self.project, root=self.cache, initialize=True)
        directory = Path(created['directory'])
        metadata = directory / 'context.json'
        original = metadata.read_text()
        metadata.write_text('{"project": "another-project"}')
        with self.assertRaises(ValueError):
            locate(self.project, root=self.cache, initialize=True)
        self.assertEqual(metadata.read_text(), '{"project": "another-project"}')
        metadata.write_text(original)
        Path(created['record']).unlink()
        with self.assertRaises(ValueError):
            locate(self.project, root=self.cache, initialize=True)
        self.assertFalse(Path(created['record']).exists())

    def test_environment_root_and_cli_error_are_clear(self):
        command = [sys.executable, '-B', str(SCRIPTS / 'design_context.py'), str(self.project)]
        result = subprocess.run(command + ['--init'], env={**os.environ, 'AGENT_DESIGN_CONTEXTS_DIR': str(self.cache)},
                                capture_output=True, text=True, check=True)
        self.assertEqual(Path(json.loads(result.stdout)['directory']).parent, self.cache)
        failed = subprocess.run(command + ['--app', 'missing', '--root', str(self.cache)],
                                capture_output=True, text=True)
        self.assertNotEqual(failed.returncode, 0)
        self.assertNotIn('Traceback', failed.stderr)


if __name__ == '__main__':
    unittest.main()
