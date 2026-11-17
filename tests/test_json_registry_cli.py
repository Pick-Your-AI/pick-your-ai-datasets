"""Existing CI entry points must enforce registration, not just the new CLI."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RegistryEntryPointTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='datasets-registry-cli-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in ('planning', 'schemas', 'examples', 'catalog'):
            shutil.copytree(ROOT / name, self.root / name)

    def check(self, expected):
        for entry in ('validate_plan.py', 'validate_catalog.py'):
            with self.subTest(entry=entry):
                run = subprocess.run([sys.executable, str(ROOT / 'scripts' / entry),
                                      '--root', str(self.root)], capture_output=True,
                                     text=True, timeout=30)
                self.assertEqual(run.returncode, 1, run.stderr + run.stdout)
                report = json.loads(run.stdout)
                self.assertEqual(report['status'], 'failed')
                self.assertTrue(any(expected in e for e in report['errors']), report)
                self.assertNotIn('Traceback', run.stderr)

    def test_unregistered_files_fail_both_existing_commands(self):
        for relative in ('unregistered.json', 'planning/unregistered.json',
                         'docs/unregistered.json'):
            with self.subTest(relative=relative):
                path = self.root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{"synthetic": true}\n', encoding='utf-8')
                self.check(relative + ': unregistered JSON artifact')
                path.unlink()

    def test_malformed_schema_fails_without_legacy_loader_traceback(self):
        path = self.root / 'schemas/dataset-record.schema.json'
        path.write_text('{"properties": []}\n', encoding='utf-8')
        self.check('properties must be an object')

    def test_chained_record_constraint_rejects_through_both_entry_points(self):
        path = self.root / 'schemas/dataset-record.schema.json'
        schema = json.loads(path.read_text(encoding='utf-8'))
        schema.setdefault('$defs', {}).update({
            'synthetic_alias': {'$ref': '#/$defs/synthetic_constraint'},
            'synthetic_constraint': {'const': 'SYNTHETIC IMPOSSIBLE TITLE'},
        })
        schema['properties']['title'] = {'$ref': '#/$defs/synthetic_alias'}
        path.write_text(json.dumps(schema), encoding='utf-8')
        self.check('$.title: must equal')


if __name__ == '__main__':
    unittest.main()
