"""Offline registration fixtures. Every mutation is in a disposable checkout copy."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import json_registry  # noqa: E402


def synthetic_showcase():
    """Synthetic branding configuration, never a dataset or a generated-image claim."""
    digest = '0' * 64
    return {
        'config_sha256': digest, 'fingerprint': digest,
        'inputs': {**{k: 'synthetic' for k in ('description', 'language', 'license',
                                              'owner', 'repo', 'type', 'visibility')},
                   'icon_sha256': digest, 'override_sha256': digest, 'topics': []},
        'outputs': {
            'banner.png': {'bytes': 0, 'chips': [{'box': [0, 0, 1, 1], 'kind': 'key',
                                                'source': 'synthetic', 'text': 'fixture'}],
                           'icon_source': 'synthetic', 'px': [1, 1], 'repository_id': 0,
                           'scale': 1, 'sha256': digest},
            'card.svg': {'bytes': 0, 'repository_id': 0, 'sha256': digest}},
        'schema': 1, 'skill_version': 'synthetic', 'standard': 'ct-std-v1',
    }


class RegistryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='datasets-json-registry-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for name in ('planning', 'schemas', 'examples'):
            shutil.copytree(ROOT / name, self.root / name)
        self.example = json.loads((ROOT / 'examples/synthetic-dataset-record.json').read_text())

    def put(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding='utf-8')
        return path

    def rejected(self, text):
        errors = json_registry.validate(self.root)
        self.assertTrue(any(text in e for e in errors), f'{text!r} not in {errors}')

    def test_current_checkout_and_disposable_copy_pass(self):
        self.assertEqual(json_registry.validate(ROOT), [])
        self.assertEqual(json_registry.validate(self.root), [])

    def test_direct_proposal_and_example_paths_are_validated(self):
        self.put('catalog/proposals/new-fixture.json', self.example)
        self.put('examples/new-fixture.json', self.example)
        self.assertEqual(json_registry.validate(self.root), [])
        self.put('catalog/proposals/new-fixture.json', {'synthetic': True})
        self.rejected('catalog/proposals/new-fixture.json: $: missing required record_id')
        self.put('examples/new-fixture.json', {})
        self.rejected('examples/new-fixture.json: $: missing required record_id')

    def test_unregistered_json_in_every_previous_gap_is_rejected(self):
        for relative in ('extra.json', 'docs/nested/extra.json', 'planning/extra.json',
                         'schemas/extra.schema.json', 'tests/extra.json',
                         'catalog/proposals/nested/extra.json', 'evidence/extra.json',
                         'research/extra.json', '.hidden/extra.json', 'examples/Upper.json'):
            with self.subTest(relative=relative):
                path = self.put(relative, {})
                self.rejected(relative + ': unregistered JSON artifact')
                path.unlink()

    def test_case_variant_extension_is_rejected_everywhere(self):
        for relative in ('extra.JSON', 'planning/extra.Json', 'examples/extra.JSON'):
            with self.subTest(relative=relative):
                self.put(relative, {})
                self.rejected(relative + ': JSON artifacts must use the lowercase .json')

    def test_git_administrative_storage_is_not_scanned(self):
        self.put('.git/worktrees/fixture/disposable.json', {'not': 'metadata'})
        self.assertEqual(json_registry.validate(self.root), [])

    def test_cache_like_directories_cannot_hide_json_artifacts(self):
        for directory in ('.venv/lib', 'node_modules/pkg', 'tests/__pycache__',
                          '.pytest_cache', '.mypy_cache', '.ruff_cache'):
            with self.subTest(directory=directory):
                path = self.put(directory + '/unregistered.json', {})
                self.rejected(directory + '/unregistered.json: unregistered JSON artifact')
                path.unlink()

    def test_missing_required_registration_is_rejected(self):
        (self.root / 'schemas/dataset-record.schema.json').unlink()
        self.rejected('schemas/dataset-record.schema.json: required registered artifact is missing')

    def test_json_and_directory_symlinks_are_rejected_without_reading_targets(self):
        with tempfile.TemporaryDirectory(prefix='datasets-outside-') as outside:
            target = Path(outside) / 'outside.json'
            target.write_text('not valid JSON', encoding='utf-8')
            (self.root / 'paseo.json').symlink_to(target)
            (self.root / 'linked-directory').symlink_to(outside, target_is_directory=True)
            self.rejected('paseo.json: JSON symlinks are not permitted')
            self.rejected('linked-directory: directory symlinks are not permitted')
            self.assertFalse(any('not valid JSON' in e for e in json_registry.validate(self.root)))

    def test_nonregular_json_is_rejected_without_opening_it(self):
        os.mkfifo(self.root / 'paseo.json')
        self.rejected('paseo.json: JSON artifacts must be regular files')

    def test_even_internal_json_symlinks_are_rejected(self):
        (self.root / 'examples/linked.json').symlink_to(self.root / 'examples/synthetic-dataset-record.json')
        self.rejected('examples/linked.json: JSON symlinks are not permitted')

    def test_invalid_json_duplicate_keys_and_nonfinite_numbers_are_rejected(self):
        for text in ('{', '{"worktree": {}, "worktree": {}}', '{"x": NaN}', '{"x": 1e999}'):
            with self.subTest(text=text):
                self.put('paseo.json', {}).write_text(text, encoding='utf-8')
                self.rejected('paseo.json: invalid or unreadable JSON')

    def test_optional_configuration_is_explicitly_registered_and_checked(self):
        for schema in json_registry.CONFIG_SCHEMAS.values():
            self.assertEqual(json_registry.schema_errors(schema), [])
        paseo = {'worktree': {'setup': ['echo synthetic'], 'teardown': 'echo synthetic'},
                 'scripts': {'validate': {'command': 'echo synthetic'}}}
        self.put('paseo.json', paseo)
        self.put('docs/images/.showcase.json', synthetic_showcase())
        # Commands remain inert strings. The validator has no process/network hook.
        with patch.object(subprocess, 'run', side_effect=AssertionError('must not execute')):
            self.assertEqual(json_registry.validate(self.root), [])
        paseo['scripts']['validate']['command'] = 1
        self.put('paseo.json', paseo)
        self.rejected('paseo.json: $.scripts.validate.command: expected string')
        showcase = synthetic_showcase()
        showcase['outputs']['banner.png']['sha256'] = 'invalid'
        self.put('docs/images/.showcase.json', showcase)
        self.rejected('docs/images/.showcase.json: $.outputs.banner.png.sha256: does not match')

    def test_configuration_has_no_blanket_unknown_property_exemption(self):
        for relative, value in (('paseo.json', {'dataset_contents': []}),
                                ('docs/images/.showcase.json', {'dataset_contents': []})):
            with self.subTest(relative=relative):
                self.put(relative, value)
                self.rejected(relative + ': $: unexpected property dataset_contents')

    def test_all_schema_artifacts_are_checked_even_without_matching_data(self):
        for relative in sorted(json_registry.SCHEMA_FILES):
            original = json_registry.read_json(self.root / relative)
            changed = copy.deepcopy(original)
            changed['unsupported'] = True
            self.put(relative, changed)
            self.rejected(relative + ': unsupported schema keyword unsupported')
            self.put(relative, original)

    def test_malformed_schema_constructs_fail_closed(self):
        fixtures = (
            ([], 'schema must be an object'),
            ({'properties': []}, 'properties must be an object'),
            ({'required': 'name'}, 'required must be an array'),
            ({'items': True}, 'schema must be an object'),
            ({'type': 'unknown'}, 'type must name supported'),
            ({'type': []}, 'type must name supported'),
            ({'anyOf': []}, 'anyOf must be a non-empty'),
            ({'pattern': '['}, 'pattern must be a valid'),
            ({'pattern': 'a{999999999999999999999999}'}, 'pattern must be a valid'),
            ({'minLength': True}, 'minLength must be a non-negative'),
            ({'minimum': '0'}, 'minimum must be a finite'),
            ({'enum': []}, 'enum must be a non-empty'),
            ({'format': 'email'}, 'only date and uri formats'),
            ({'uniqueItems': 'true'}, 'uniqueItems must be boolean'),
            ({'$schema': 'https://example.invalid/schema'}, 'only the declared 2020-12'),
            ({'anyOf': [{}], 'required': ['name']}, 'anyOf validation siblings'),
            ({'$ref': '#/$defs/item', '$defs': {'item': {}}, 'type': 'string'}, '$ref validation siblings'),
            ({'$ref': 'https://example.invalid/schema'}, 'only local #/$defs/name'),
            ({'$ref': '#/$defs/missing'}, 'dangling local reference'),
            ({'$ref': '#/$defs/a/b', '$defs': {'a/b': {}}}, 'only local #/$defs/name'),
            ({'$defs': {'a': {'$ref': '#/$defs/b'}, 'b': {'$ref': '#/$defs/a'}}}, 'cyclic local reference'),
        )
        for schema, message in fixtures:
            with self.subTest(schema=schema):
                self.put('schemas/planning-release.schema.json', schema)
                self.rejected(message)

    def test_const_only_schema_nodes_are_supported(self):
        self.put('schemas/planning-release.schema.json', {'const': {'synthetic': True}})
        self.put('planning/release-manifest.json', {'synthetic': True})
        self.assertEqual(json_registry.validate(self.root), [])
        self.put('planning/release-manifest.json', {'synthetic': False})
        self.rejected('planning/release-manifest.json: $: must equal')

    def test_dotted_definition_names_do_not_create_false_reference_cycles(self):
        self.assertEqual(json_registry.schema_errors({
            '$defs': {'a': {'type': 'integer'}, 'a.b': {'$ref': '#/$defs/a'}},
            '$ref': '#/$defs/a.b',
        }), [])

    def test_local_definition_reference_is_evaluated_offline(self):
        self.put('schemas/planning-release.schema.json', {
            '$defs': {'value': {'type': 'integer'}},
            'type': 'object', 'properties': {'value': {'$ref': '#/$defs/value'}},
            'required': ['value'], 'additionalProperties': False,
        })
        self.put('planning/release-manifest.json', {'value': 1})
        self.assertEqual(json_registry.validate(self.root), [])
        self.put('planning/release-manifest.json', {'value': 'wrong'})
        self.rejected('planning/release-manifest.json: $.value: expected integer')

    def test_chained_local_references_enforce_the_terminal_constraint(self):
        self.put('schemas/planning-release.schema.json', {
            '$defs': {'alias': {'$ref': '#/$defs/value'}, 'value': {'type': 'integer'}},
            'type': 'object', 'properties': {'value': {'$ref': '#/$defs/alias'}},
            'required': ['value'], 'additionalProperties': False,
        })
        self.put('planning/release-manifest.json', {'value': 1})
        self.assertEqual(json_registry.validate(self.root), [])
        self.put('planning/release-manifest.json', {'value': 'synthetic-invalid-number'})
        self.rejected('planning/release-manifest.json: $.value: expected integer')

    def test_evaluator_stops_direct_reference_cycles_and_missing_targets(self):
        for definitions, expected in (({'a': {'$ref': '#/$defs/a'}}, 'cyclic local reference'),
                                      ({}, 'unresolved local reference')):
            with self.subTest(definitions=definitions):
                schema = {'$ref': '#/$defs/a', '$defs': definitions}
                self.assertTrue(any(expected in error for error in
                                    json_registry.schemalib.errors(1, schema)))


if __name__ == '__main__':
    unittest.main()
