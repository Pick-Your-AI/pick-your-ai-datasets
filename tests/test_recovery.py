"""Offline recovery tests; every Git repository and file here is synthetic."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    'recovery_drill', Path(__file__).resolve().parents[1] / 'scripts/recovery_drill.py')
recovery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(recovery)


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='synthetic-recovery-test-')
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name) / 'source'
        self.repo.mkdir()
        self.git('init', '--quiet')
        self.git('config', 'user.name', 'Synthetic Test')
        self.git('config', 'user.email', 'synthetic@example.invalid')
        (self.repo / 'metadata.txt').write_bytes(b'Synthetic metadata\x00fixture\n')
        (self.repo / 'empty.txt').write_bytes(b'')
        self.git('add', '.')
        self.git('commit', '--quiet', '-m', 'Synthetic fixture')
        self.commit = self.git('rev-parse', 'HEAD').strip()

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], check=True,
                              capture_output=True, env=recovery.local_environment()).stdout.decode()

    def drill(self, **kwargs):
        return recovery.run_drill(self.repo, kwargs.pop('ref', self.commit),
                                  kwargs.pop('path', 'metadata.txt'), **kwargs)

    def test_restores_exact_bytes_without_source_worktree_or_ref_changes(self):
        (self.repo / 'metadata.txt').write_bytes(b'Synthetic uncommitted live edit\n')
        (self.repo / 'untracked.txt').write_text('Synthetic untracked fixture\n')
        before_status = self.git('status', '--porcelain=v1', '--untracked-files=all')
        before_refs = self.git('show-ref')
        before_files = {p.name: p.read_bytes() for p in self.repo.iterdir() if p.is_file()}
        report = self.drill(validate=False)
        self.assertTrue(report['restored_equals_source'])
        self.assertEqual(report['source_commit'], self.commit)
        self.assertEqual(report['source_sha256'], report['restored_sha256'])
        self.assertNotEqual(report['source_sha256'], report['corrupted_sha256'])
        self.assertIsNone(report['checks_passed'])
        self.assertEqual(report['checks'], [])
        self.assertEqual(before_status, self.git('status', '--porcelain=v1', '--untracked-files=all'))
        self.assertEqual(before_refs, self.git('show-ref'))
        self.assertEqual(before_files, {p.name: p.read_bytes() for p in self.repo.iterdir() if p.is_file()})
        self.assertNotIn(str(self.repo), str(report))
        self.assertNotIn('synthetic@example.invalid', str(report))

    def test_empty_file_can_be_corrupted_and_restored(self):
        report = self.drill(path='empty.txt', validate=False)
        self.assertEqual(report['source_sha256'], recovery.digest(b''))
        self.assertTrue(report['restored_equals_source'])

    def test_missing_pinned_commit_is_rejected(self):
        with self.assertRaises(recovery.DrillError):
            self.drill(ref='0' * 40, validate=False)

    def test_missing_path_is_rejected(self):
        with self.assertRaisesRegex(recovery.DrillError, 'tracked regular file'):
            self.drill(path='missing.txt', validate=False)

    def test_moving_ref_is_rejected(self):
        with self.assertRaisesRegex(recovery.DrillError, 'full lowercase commit'):
            self.drill(ref='HEAD', validate=False)

    def test_unsafe_paths_are_rejected(self):
        for path in ('../metadata.txt', '/metadata.txt', '.git/config', './metadata.txt',
                     'folder/../metadata.txt', 'folder//file', 'folder\\file'):
            with self.subTest(path=path), self.assertRaises(recovery.DrillError):
                self.drill(path=path, validate=False)

    def test_symlink_is_rejected(self):
        os.symlink('metadata.txt', self.repo / 'link.txt')
        self.git('add', 'link.txt')
        self.git('commit', '--quiet', '-m', 'Synthetic symlink fixture')
        with self.assertRaisesRegex(recovery.DrillError, 'tracked regular file'):
            self.drill(ref=self.git('rev-parse', 'HEAD').strip(), path='link.txt', validate=False)

    def test_failed_checks_are_reported_and_cli_fails(self):
        # This is a real failing local process, not production or repo validation evidence.
        with patch.object(recovery, 'CHECKS', (('python3', '-c', 'raise SystemExit(7)'),)):
            report = self.drill()
            self.assertFalse(report['checks_passed'])
            self.assertEqual(report['checks'][0]['exit_code'], 7)
        with patch.object(recovery, 'run_drill', return_value=report), patch('builtins.print'):
            self.assertEqual(recovery.main(['--repo', str(self.repo), '--ref', self.commit,
                                           '--path', 'metadata.txt']), 1)

    def test_all_four_repository_checks_are_configured(self):
        self.assertEqual(recovery.CHECKS, (
            ('python3', 'scripts/validate_plan.py'),
            ('python3', 'scripts/validate_catalog.py'),
            ('python3', 'scripts/render_docs.py', '--check'),
            ('python3', '-m', 'unittest', 'discover', '-s', 'tests', '-v'),
        ))


if __name__ == '__main__':
    unittest.main()
