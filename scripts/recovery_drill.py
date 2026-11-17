#!/usr/bin/env python3
"""Restore one tracked regular file in a disposable local clone; never fetch or push.

Only run this on a trusted local repository: the four validation commands execute
code from the pinned commit. The synthetic corruption and restoration occur only
inside TemporaryDirectory; neither the source checkout nor its refs are changed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile


CHECKS = (
    ('python3', 'scripts/validate_plan.py'),
    ('python3', 'scripts/validate_catalog.py'),
    ('python3', 'scripts/render_docs.py', '--check'),
    ('python3', '-m', 'unittest', 'discover', '-s', 'tests', '-v'),
)


class DrillError(Exception):
    """A sanitized, user-facing precondition or execution failure."""


def local_environment():
    # Ignore inherited Git routing/configuration and disable implicit remote reads.
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
               GIT_TERMINAL_PROMPT='0', GIT_ALLOW_PROTOCOL='file',
               GIT_NO_LAZY_FETCH='1', GIT_NO_REPLACE_OBJECTS='1',
               PYTHONDONTWRITEBYTECODE='1')
    return env


def git(repo, *args):
    command = ['git', '-c', f'core.hooksPath={os.devnull}',
               '-c', 'core.fsmonitor=false', '-c', 'protocol.allow=never',
               '-c', 'protocol.file.allow=always', '-C', str(repo), *args]
    try:
        result = subprocess.run(command, capture_output=True, env=local_environment(),
                                timeout=120, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DrillError('Local Git operation could not complete.') from exc
    if result.returncode:
        # Git's stderr may include local paths, identities or credential-bearing URLs.
        raise DrillError('Local Git operation failed; verify the repository, commit and path.')
    return result.stdout


def digest(data):
    return hashlib.sha256(data).hexdigest()


def checked_path(value):
    path = PurePosixPath(value)
    if (not value or '\\' in value or '\x00' in value or path.is_absolute()
            or any(part in ('', '.', '..', '.git') for part in value.split('/'))):
        raise DrillError('Path must be a normalized repository-relative file path.')
    return path


def run_drill(repo, ref, path, *, validate=True):
    """Return a sanitized report. `validate=False` is only a file-restore drill.

    The repository must be local and the reference a full immutable commit ID.
    Failed checks are reported as failures, not converted to successful recovery.
    """
    if not re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', ref):
        raise DrillError('Ref must be a full lowercase commit object ID, not a branch or tag.')
    relative = checked_path(path)
    source = Path(repo).resolve(strict=True)
    if not source.is_dir():
        raise DrillError('Repository must be an existing local directory.')
    commit = git(source, 'rev-parse', '--verify', f'{ref}^{{commit}}').decode().strip()
    if commit != ref:
        raise DrillError('Ref must identify a commit object directly.')
    entry = git(source, 'ls-tree', '-z', commit, '--', path)
    entries = entry.rstrip(b'\0').split(b'\0')
    if len(entries) != 1 or not entries[0]:
        raise DrillError('Path is not a tracked regular file at the pinned commit.')
    metadata, name = entries[0].split(b'\t', 1)
    mode, kind, blob = metadata.split()
    if mode not in (b'100644', b'100755') or kind != b'blob' or os.fsdecode(name) != path:
        raise DrillError('Path is not a tracked regular file at the pinned commit.')
    expected = git(source, 'cat-file', 'blob', blob.decode())

    with tempfile.TemporaryDirectory(prefix='dataset-recovery-') as temporary:
        clone = Path(temporary) / 'checkout'
        # --local + an existing directory cannot select an SSH/HTTP transport.
        # No hardlinks, source hooks, global config, or source working-tree data.
        git(source, 'clone', '--local', '--no-hardlinks', '--no-checkout',
            '--template=', '--', str(source), str(clone))
        git(clone, 'config', '--remove-section', 'remote.origin')
        git(clone, 'checkout', '--quiet', '-b', 'recovery-drill', commit)
        target = clone.joinpath(*relative.parts)
        if target.is_symlink() or not target.resolve().is_relative_to(clone.resolve()):
            raise DrillError('Disposable target escapes the checkout or is a symlink.')
        # Always differ, including for an empty tracked file.
        corrupted = expected + b'\nSYNTHETIC LOCAL RECOVERY DRILL CORRUPTION\n'
        target.write_bytes(corrupted)
        if target.read_bytes() == expected:
            raise DrillError('Synthetic corruption did not change the disposable file.')
        # Recover bytes from Git history in the disposable branch, not a saved copy.
        restored_blob = git(clone, 'cat-file', 'blob', f'{commit}:{path}')
        target.write_bytes(restored_blob)
        restored = target.read_bytes()
        equal = restored == expected
        if not equal:
            raise DrillError('Restored bytes differ from the pinned source blob.')
        checks = []
        if validate:
            for command in CHECKS:
                try:
                    result = subprocess.run(command, cwd=clone, capture_output=True,
                                            env=local_environment(), timeout=120, check=False)
                    checks.append({'command': ' '.join(command),
                                   'exit_code': result.returncode, 'status': 'completed'})
                except subprocess.TimeoutExpired:
                    checks.append({'command': ' '.join(command),
                                   'exit_code': None, 'status': 'timed_out'})
                except OSError:
                    checks.append({'command': ' '.join(command),
                                   'exit_code': None, 'status': 'could_not_start'})
        return {
            'evidence_scope': 'local disposable clone; synthetic file corruption only',
            'source_commit': commit, 'source_path': path,
            'source_blob': blob.decode(), 'source_sha256': digest(expected),
            'corrupted_sha256': digest(corrupted), 'restored_sha256': digest(restored),
            'restored_equals_source': equal, 'disposable_branch': 'recovery-drill',
            'checks_requested': validate, 'checks': checks,
            'checks_passed': all(c['exit_code'] == 0 for c in checks) if validate else None,
            'temporary_clone_removed_on_return': True,
        }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, help='Trusted existing local repository directory')
    parser.add_argument('--ref', required=True, help='Full pinned commit object ID')
    parser.add_argument('--path', required=True, help='Tracked repository-relative regular file')
    parser.add_argument('--skip-checks', action='store_true',
                        help='File drill only; report repository checks as not attempted')
    args = parser.parse_args(argv)
    try:
        report = run_drill(args.repo, args.ref, args.path, validate=not args.skip_checks)
    except (DrillError, OSError) as exc:
        message = str(exc) if isinstance(exc, DrillError) else 'Local filesystem operation failed.'
        print(json.dumps({'error': message}), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report['checks_passed'] is False else 0


if __name__ == '__main__':
    raise SystemExit(main())
