"""Locate a project/app-specific design record without modifying product files."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile


def atomic_write(path: Path, text: str) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def locate(project: Path, app: str = '.', root: Path | None = None, initialize: bool = False) -> dict:
    project = project.expanduser().resolve(strict=True)
    if not project.is_dir():
        raise ValueError('project must be a directory')
    if Path(app).is_absolute():
        raise ValueError('--app must be relative to the project root')
    target = (project / app).resolve(strict=True)
    if not target.is_dir() or not target.is_relative_to(project):
        raise ValueError('--app must resolve to a directory inside the project')
    root = (root if root is not None else Path(os.environ.get(
        'AGENT_DESIGN_CONTEXTS_DIR', '~/.agent-skills/design-contexts'))).expanduser().resolve()
    if root.is_relative_to(project):
        raise ValueError('design context storage must be outside the project; select another --root')
    identity = {'schema_version': 1, 'project': str(project), 'app': str(target)}
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode('utf-8')).hexdigest()[:24]
    directory = root / key
    if directory.is_symlink():
        raise ValueError('context directory is a symlink; refusing to adopt it')
    if initialize:
        root.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            directory.mkdir(mode=0o700)
        except FileExistsError:
            pass
        else:
            atomic_write(directory / 'context.json', json.dumps(identity, indent=2) + '\n')
            atomic_write(directory / 'design.md',
                         '# Design contract\n\nStatus: proposed\n'
                         f'Project: {project}\nApp: {target}\n'
                         'Runtime authority: not yet inspected\n'
                         'Next action: inspect current project sources before selecting a baseline.\n')
    exists = directory.exists()
    if exists:
        metadata = directory / 'context.json'
        record = directory / 'design.md'
        if metadata.is_symlink() or record.is_symlink():
            raise ValueError('context files are symlinks; refusing to adopt them')
        if not metadata.is_file() or not record.is_file():
            raise ValueError(f'incomplete design context at {directory}; recover it explicitly before reuse')
        if json.loads(metadata.read_text(encoding='utf-8')) != identity:
            raise ValueError(f'design context identity mismatch at {directory}')
    return {**identity, 'directory': str(directory), 'record': str(directory / 'design.md'),
            'exists': exists, 'source_revalidation_required': True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--app', default='.', help='app directory relative to project root')
    parser.add_argument('--root', type=Path, help='external cache root')
    parser.add_argument('--init', action='store_true', help='create a missing record; never overwrite one')
    args = parser.parse_args()
    print(json.dumps(locate(args.project, args.app, args.root, args.init), ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(f'Design context error: {error}')
