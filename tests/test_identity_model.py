"""DATA-04.01/02 contracts; every record and source below is synthetic."""
import copy
import datetime as dt
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import identity_model  # noqa: E402
import schemalib  # noqa: E402
import validate_catalog  # noqa: E402


class IdentityModelTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / 'examples/synthetic-dataset-record.json').read_text())
        self.version = self.record['versions'][0]
        self.sid = 'source.synthetic.landing'
        self.version.update(identity_evidence={'kind': 'publisher_version', 'marker': '1.0.0', 'source_id': self.sid},
                            subsets=[{'subset_id': 'selection', 'name': 'Synthetic selection', 'source_id': self.sid}],
                            configs=[{'config_id': 'main', 'name': 'Synthetic main', 'subset_id': 'selection', 'source_id': self.sid}])
        self.version['splits'][0].update(subset_id='selection', config_id='main', source_id=self.sid)
        self.record.update(maintainers=[{'name': 'Synthetic maintainer', 'source_id': self.sid}],
                           hosts=[{'name': 'Synthetic host', 'source_id': self.sid}])

    def errors(self):
        return identity_model.errors(self.record)

    def rejected(self, phrase):
        self.assertTrue(any(phrase in e for e in self.errors()), self.errors())

    def test_schema_accepts_new_fields_and_existing_example(self):
        schema = json.loads((ROOT / 'schemas/dataset-record.schema.json').read_text())
        self.assertEqual(schemalib.unsupported_keywords(schema), [])
        self.assertEqual(schemalib.errors(self.record, schema), [])
        self.assertEqual(self.errors(), [])
        self.assertEqual(validate_catalog.validate_records({'synthetic': self.record}, dt.date(2026, 11, 17), False, True, ROOT), [])

    def test_catalog_integrates_identity_checks_without_merging_matching_titles(self):
        second = copy.deepcopy(self.record)
        second['record_id'] = 'dataset.synthetic-other'
        second['versions'][0]['version_id'] = 'dataset.synthetic-other@1.0.0'
        records = {'first': self.record, 'second': second}
        self.assertEqual(validate_catalog.validate_records(records, dt.date(2026, 11, 17), False, True, ROOT), [])
        self.version['identity_evidence']['marker'] = 'different'
        errors = validate_catalog.validate_records(records, dt.date(2026, 11, 17), False, True, ROOT)
        self.assertTrue(any('identity marker must equal' in e for e in errors), errors)

    def test_legacy_and_explicit_unknown_stay_distinct(self):
        del self.version['identity_evidence']
        self.assertEqual(identity_model.identity_basis(self.version), 'legacy_unclassified')
        self.assertEqual(self.errors(), [])
        self.version['identity_evidence'] = None
        self.assertEqual(identity_model.identity_basis(self.version), 'unknown')
        self.assertEqual(self.errors(), [])
        self.record['publication_state'] = 'eligible'
        self.rejected('explicitly unknown identity evidence cannot be published')

    def test_unversioned_cannot_claim_version_evidence(self):
        self.version.update(version_label=None, unversioned=True)
        self.assertEqual(identity_model.identity_basis(self.version), 'unversioned')
        self.rejected('identity marker must equal the exact version label')

    def test_identity_evidence_matches_exact_marker_and_source_role(self):
        self.version['identity_evidence']['marker'] = '1.0'
        self.rejected('exact version label')
        self.version['identity_evidence'].update(marker='1.0.0', source_id='source.synthetic.license')
        self.rejected('incompatible source role')
        self.rejected('source must belong to the containing version')

    def test_missing_identity_and_party_sources_are_rejected(self):
        self.version['identity_evidence']['source_id'] = 'source.missing'
        self.record['maintainers'][0]['source_id'] = 'source.missing'
        self.record['hosts'][0]['source_id'] = 'source.missing'
        self.rejected('identity evidence cites missing source metadata')
        self.rejected('maintainers cites missing source metadata')
        self.rejected('hosts cites missing source metadata')

    def test_immutable_host_revision_requires_host_and_host_source_role(self):
        self.version['identity_evidence']['kind'] = 'immutable_host_revision'
        self.rejected('incompatible source role')
        self.record['sources'][0]['role'] = 'host_page'
        self.assertEqual(self.errors(), [])
        self.record['hosts'] = []
        self.rejected('immutable revision must cite a recorded host')

    def test_external_identifiers_keep_issued_values_kind_issuer_and_scope(self):
        value = 'SYNTHETIC:Case/Sensitive'
        self.record['external_ids'] = [{'kind': kind, 'issuer': 'Synthetic issuer', 'value': value,
                                       'source_id': self.sid, 'version_id': self.version['version_id']}
                                      for kind in ('doi', 'host_id', 'arxiv')]
        before = copy.deepcopy(self.record)
        self.assertEqual(self.errors(), [])
        self.assertEqual(self.record, before)
        duplicate = copy.deepcopy(self.record['external_ids'][0])
        duplicate.pop('source_id')
        self.record['external_ids'].append(duplicate)
        self.rejected('duplicate external identifier in the same scope')
        self.record['external_ids'][0]['version_id'] = 'dataset.other@release'
        self.rejected('external identifier targets unknown version')

    def test_children_are_scoped_to_one_version_and_kind(self):
        vid = self.version['version_id']
        for kind in ('subset', 'config', 'split'):
            self.assertNotEqual(identity_model.child_identity(vid, kind, 'main'),
                                identity_model.child_identity(vid + '-second', kind, 'main'))
        self.assertNotEqual(identity_model.child_identity(vid, 'subset', 'main'),
                            identity_model.child_identity(vid, 'config', 'main'))
        with self.assertRaises(ValueError):
            identity_model.child_identity(vid, 'dataset', 'main')
        for field in ('subsets', 'configs'):
            self.version[field].append(copy.deepcopy(self.version[field][0]))
        self.rejected('duplicate subset ID')
        self.rejected('duplicate config ID')

    def test_cross_version_child_reference_and_source_are_rejected(self):
        second = copy.deepcopy(self.version)
        second.update(version_id=self.record['record_id'] + '@second', subsets=[], configs=[])
        self.record['versions'].append(second)
        self.rejected('split targets unknown subset in this version')
        self.rejected('split targets unknown config in this version')
        self.version['configs'][0]['subset_id'] = 'absent'
        self.rejected('config targets unknown subset')
        self.version['subsets'][0]['source_id'] = 'source.synthetic.license'
        self.rejected('source must belong to the containing version')

    def test_split_config_subset_must_agree_and_split_names_are_scoped(self):
        self.version['subsets'].append({'subset_id': 'other', 'name': 'Synthetic other', 'source_id': self.sid})
        self.version['splits'][0]['subset_id'] = 'other'
        self.rejected('split subset conflicts with its config subset')
        self.version['splits'][0]['subset_id'] = 'selection'
        duplicate = copy.deepcopy(self.version['splits'][0])
        duplicate['split_id'] = 'different-id'
        self.version['splits'].append(duplicate)
        self.rejected('split name is ambiguous')
        self.version['configs'].append({'config_id': 'other', 'name': 'Synthetic other', 'source_id': self.sid})
        duplicate['config_id'] = 'other'
        self.assertEqual(self.errors(), [])

    def test_formats_size_units_and_null_do_not_imply_equivalence(self):
        size = self.version['splits'][0]['size']
        size.update(value=1.5, unit='hours')
        schema = json.loads((ROOT / 'schemas/dataset-record.schema.json').read_text())
        self.assertEqual(schemalib.errors(self.record, schema), [])
        self.assertEqual(self.errors(), [])
        size['unit'] = 'examples'
        self.rejected('count size units require an integer')
        size.update(value=None, unit='unknown')
        self.assertEqual(self.errors(), [])
        size['value'] = 0
        self.rejected('unknown size unit requires a null')
        self.version['formats'] = ['unknown', 'jsonl']
        self.rejected('unknown format cannot be mixed')
        self.version['formats'] = ['other']
        size['unit'] = 'other'
        self.rejected('other format requires format_notes')
        self.rejected('other size unit requires unit_notes')
        self.version['format_notes'] = 'Synthetic unusual format'
        size['unit_notes'] = 'Synthetic unusual unit'
        self.assertEqual(self.errors(), [])

    def test_schema_rejects_wrong_types_uncontrolled_units_and_formats(self):
        schema = json.loads((ROOT / 'schemas/dataset-record.schema.json').read_text())
        for path, value in (('formats', ['imaginary']), ('configs', [{'config_id': 1}])):
            with self.subTest(path=path):
                record = copy.deepcopy(self.record)
                record['versions'][0][path] = value
                self.assertTrue(schemalib.errors(record, schema))
        for value, unit in ((True, 'examples'), (-1, 'bytes'), (1, 'imaginary')):
            with self.subTest(value=value, unit=unit):
                self.version['splits'][0]['size'].update(value=value, unit=unit)
                self.assertTrue(schemalib.errors(self.record, schema))


if __name__ == '__main__':
    unittest.main()
