"""Catalog validator regressions using only synthetic records in disposable copies."""
import copy
import datetime as dt
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import validate_catalog  # noqa: E402

TODAY = dt.date(2026, 10, 23)


class CatalogTestCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='datasets-catalog-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('planning', 'schemas', 'examples'):
            shutil.copytree(ROOT / name, self.root / name)
        (self.root / 'catalog/proposals').mkdir(parents=True)
        self.example = json.loads((ROOT / 'examples/synthetic-dataset-record.json').read_text(encoding='utf-8'))

    def proposal(self, **changes):
        """A non-synthetic-shaped copy placed in proposals; content remains test-only."""
        record = copy.deepcopy(self.example)
        record['synthetic'] = False
        record.update(changes)
        return record

    def put(self, name, record, directory='catalog/proposals'):
        (self.root / directory / name).write_text(json.dumps(record, indent=2), encoding='utf-8')

    def errors(self, publication=False):
        return validate_catalog.validate(self.root, publication, TODAY)[0]

    def assert_rejected(self, text, publication=False):
        errors = self.errors(publication)
        self.assertTrue(any(text in e for e in errors), f'{text!r} not in {errors}')

    def eligible(self):
        record = self.proposal(publication_state='eligible')
        record['rights'].update(access_classification='Open', rights_status='Permitted for Metadata Use')
        record['rights']['permissions'][0].update(decision='allowed', reviewed=True)
        record['reviews'] = [{'kind': k, 'reviewer': 'independent-reviewer', 'decision': 'accepted', 'reviewed_on': '2026-10-23'}
                             for k in ('rights', 'editorial', 'evidence')]
        return record


class BaselineTests(CatalogTestCase):
    def test_repository_baseline_is_valid(self):
        errors, stats = validate_catalog.validate(ROOT, today=TODAY)
        self.assertEqual(errors, [])
        self.assertEqual(stats['examples'], 1)

    def test_candidate_proposal_is_valid_in_research_mode(self):
        self.put('a.json', self.proposal())
        self.assertEqual(self.errors(), [])

    def test_fully_reviewed_eligible_proposal_passes_publication(self):
        self.put('a.json', self.eligible())
        self.assertEqual(self.errors(publication=True), [])


class IdentityTests(CatalogTestCase):
    def test_synthetic_record_cannot_be_a_proposal(self):
        record = self.proposal()
        record['synthetic'] = True
        self.put('a.json', record)
        self.assert_rejected('synthetic records belong in examples/')

    def test_duplicate_record_id(self):
        self.put('a.json', self.proposal())
        self.put('b.json', self.proposal())
        self.assert_rejected('duplicate record ID')

    def test_unversioned_reference_needs_explicit_flag(self):
        record = self.proposal()
        record['versions'][0]['version_label'] = None
        self.put('a.json', record)
        self.assert_rejected('a version label is required unless the reference is explicitly unversioned')

    def test_duplicate_version_label_is_ambiguous(self):
        record = self.proposal()
        second = copy.deepcopy(record['versions'][0])
        second['version_id'] = record['record_id'] + '@1.0.0-copy'
        record['versions'].append(second)
        self.put('a.json', record)
        self.assert_rejected('version label is ambiguous')

    def test_unversioned_cannot_be_published(self):
        record = self.eligible()
        record['versions'][0].update(version_label=None, unversioned=True)
        self.put('a.json', record)
        self.assert_rejected('unversioned reference is ambiguous')

    def test_version_must_belong_to_record(self):
        record = self.proposal()
        record['versions'][0]['version_id'] = 'dataset.other@1.0.0'
        self.put('a.json', record)
        self.assert_rejected('version does not belong to this record')

    def test_duplicate_split(self):
        record = self.proposal()
        record['versions'][0]['splits'][1]['split_id'] = 'test'
        self.put('a.json', record)
        self.assert_rejected('duplicate split within a version')


class SourceTests(CatalogTestCase):
    def test_missing_license_source(self):
        record = self.proposal()
        record['versions'][0]['license']['source_id'] = 'source.missing'
        self.put('a.json', record)
        self.assert_rejected('license cites missing source metadata source.missing')

    def test_source_requires_access_date(self):
        record = self.proposal()
        del record['sources'][0]['accessed_on']
        self.put('a.json', record)
        self.assert_rejected('missing required accessed_on')

    def test_future_access_date(self):
        record = self.proposal()
        record['sources'][0]['accessed_on'] = '2027-01-01'
        self.put('a.json', record)
        self.assert_rejected('future access date')

    def test_credentialed_url_rejected(self):
        record = self.proposal()
        record['sources'][0]['url'] = 'https://user:secret@example.org/data'
        self.put('a.json', record)
        self.assert_rejected('not an https URL without credentials')

    def test_personal_contact_data_rejected(self):
        record = self.proposal(title='Contact maintainer@example.org for access')
        self.put('a.json', record)
        self.assert_rejected('possible personal contact data')

    def test_dataset_contents_cannot_be_committed(self):
        (self.root / 'catalog/proposals/sample.csv').write_text('a,b\n1,2\n', encoding='utf-8')
        self.assert_rejected('dataset contents must not be committed')


class MaterialLocationTests(CatalogTestCase):
    """PR #74 review: every JSON path the material rules permit must be validated or rejected."""

    def nested(self, name, text, directory='catalog/proposals/nested'):
        (self.root / directory).mkdir(parents=True, exist_ok=True)
        (self.root / directory / name).write_text(text, encoding='utf-8')

    def test_nested_proposal_cannot_escape_publication_gates(self):
        self.put('a.json', self.proposal())
        direct = self.errors(publication=True)
        self.assertTrue(any('publication gate rejects a candidate proposal' in e for e in direct), direct)
        record = (self.root / 'catalog/proposals/a.json').read_text(encoding='utf-8')
        (self.root / 'catalog/proposals/a.json').unlink()
        self.nested('record.json', record)
        self.assert_rejected('JSON outside a validated record location', publication=True)

    def test_malformed_nested_json_is_rejected(self):
        self.nested('broken.json', '{not json')
        self.assert_rejected('catalog/proposals/nested/broken.json: JSON outside a validated record location')

    def test_uppercase_extension_is_rejected(self):
        (self.root / 'catalog/proposals/broken.JSON').write_text('{not json', encoding='utf-8')
        self.assert_rejected('must use the lowercase .json extension')
        (self.root / 'catalog/proposals/broken.JSON').unlink()
        (self.root / 'catalog/proposals/record.Json').write_text(json.dumps(self.proposal()), encoding='utf-8')
        self.assert_rejected('must use the lowercase .json extension')

    def test_malformed_direct_json_is_rejected(self):
        (self.root / 'catalog/proposals/broken.json').write_text('{not json', encoding='utf-8')
        self.assertTrue(self.errors())

    def test_nested_synthetic_record_cannot_evade_placement(self):
        self.nested('synthetic.json', json.dumps(self.example))
        self.assert_rejected('JSON outside a validated record location')

    def test_json_outside_record_directories_is_rejected(self):
        for directory in ('catalog', 'evidence', 'research/sources', 'examples/nested'):
            with self.subTest(directory=directory):
                self.nested('stray.json', '{}', directory)
                self.assert_rejected(f'{directory}/stray.json: JSON outside a validated record location')

    def test_controls_are_preserved(self):
        self.put('a.json', self.proposal())
        self.nested('notes.md', '# Research note\n')
        self.assertEqual(self.errors(), [])
        self.nested('sample.csv', 'a,b\n')
        self.assert_rejected('dataset contents must not be committed')


class RightsAndPublicationTests(CatalogTestCase):
    def test_withheld_proposal_fails_publication_gate(self):
        self.put('a.json', self.proposal(publication_state='withheld'))
        self.assert_rejected('publication gate rejects a withheld proposal', publication=True)

    def test_unassessed_rights_cannot_be_eligible(self):
        record = self.eligible()
        record['rights']['rights_status'] = 'Not Assessed'
        self.put('a.json', record)
        self.assert_rejected('publication requires reviewed, permitted rights status')

    def test_unreviewed_permission_blocks_publication(self):
        record = self.eligible()
        record['rights']['permissions'].append({'use': 'training', 'decision': 'unknown', 'conditions': [],
                                                'source_id': 'source.synthetic.license', 'reviewed': False})
        self.put('a.json', record)
        self.assert_rejected('every recorded permission to be reviewed')

    def test_self_review_cannot_accept(self):
        record = self.eligible()
        for review in record['reviews']:
            review['reviewer'] = record['proposed_by']
        self.put('a.json', record)
        self.assert_rejected('self-review cannot accept')
        self.assert_rejected('independent accepted rights review')

    def test_conditional_permission_needs_conditions(self):
        record = self.proposal()
        record['rights']['permissions'][0]['decision'] = 'conditional'
        self.put('a.json', record)
        self.assert_rejected('lacks its conditions')

    def test_withdrawal_requires_notice(self):
        record = self.proposal(publication_state='withdrawn', withdrawal={'announced_on': '2026-10-01', 'source_id': 'source.synthetic.landing', 'reason': 'Synthetic test'})
        self.put('a.json', record)
        self.assert_rejected('withdrawal must cite an authoritative notice source')

    def test_withdrawn_state_requires_event(self):
        self.put('a.json', self.proposal(publication_state='withdrawn'))
        self.assert_rejected('withdrawn state and withdrawal event must appear together')


class RelationshipTests(CatalogTestCase):
    def test_unknown_relationship_target(self):
        record = self.proposal(relationships=[{'predicate': 'derived_from', 'object': 'dataset.unknown', 'source_id': 'source.synthetic.landing'}])
        self.put('a.json', record)
        self.assert_rejected('targets unknown record or version')

    def test_lineage_cycle(self):
        first = self.proposal(record_id='dataset.first')
        first['versions'][0]['version_id'] = 'dataset.first@1.0.0'
        second = self.proposal(record_id='dataset.second')
        second['versions'][0]['version_id'] = 'dataset.second@1.0.0'
        first['relationships'] = [{'predicate': 'derived_from', 'object': 'dataset.second', 'source_id': 'source.synthetic.landing'}]
        second['relationships'] = [{'predicate': 'derived_from', 'object': 'dataset.first@1.0.0', 'source_id': 'source.synthetic.landing'}]
        self.put('a.json', first)
        self.put('b.json', second)
        self.assert_rejected('lineage cycle')


if __name__ == '__main__':
    unittest.main()
