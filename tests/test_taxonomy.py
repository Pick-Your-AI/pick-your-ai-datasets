"""Term registration regressions use disposable planning and catalog copies."""
import copy

from test_plan import PlanTestCase
from test_catalog import CatalogTestCase


class TaxonomyTests(PlanTestCase):
    def change(self, update):
        data = self.read('planning/taxonomy.json')
        update(data)
        self.write('planning/taxonomy.json', data)

    def test_missing_vocabulary_rejected(self):
        self.change(lambda data: data['vocabularies'].pop())
        self.assert_rejected('fields differ from Project')

    def test_extra_vocabulary_rejected(self):
        def update(data):
            extra = copy.deepcopy(data['vocabularies'][0])
            extra['field'] = 'Unregistered field'
            data['vocabularies'].append(extra)
        self.change(update)
        self.assert_rejected('fields differ from Project')

    def test_duplicate_vocabulary_rejected(self):
        self.change(lambda data: data['vocabularies'].append(copy.deepcopy(data['vocabularies'][0])))
        self.assert_rejected('duplicate field')

    def test_missing_term_rejected(self):
        self.change(lambda data: data['vocabularies'][0]['terms'].pop())
        self.assert_rejected('terms differ from Project')

    def test_extra_term_rejected(self):
        def update(data):
            term = copy.deepcopy(data['vocabularies'][0]['terms'][0])
            term['value'] = 'Unregistered value'
            data['vocabularies'][0]['terms'].append(term)
        self.change(update)
        self.assert_rejected('terms differ from Project')

    def test_duplicate_term_rejected_even_with_different_definition(self):
        def update(data):
            term = copy.deepcopy(data['vocabularies'][0]['terms'][0])
            term['definition'] = 'A different description does not create a different option.'
            data['vocabularies'][0]['terms'].append(term)
        self.change(update)
        self.assert_rejected('duplicate term')

    def test_blank_or_padded_definition_and_scope_rejected(self):
        original = self.read('planning/taxonomy.json')
        for key in ('definition', 'scope_note'):
            for value in ('', '   ', ' padded '):
                with self.subTest(key=key, value=value):
                    data = copy.deepcopy(original)
                    data['vocabularies'][0]['terms'][0][key] = value
                    self.write('planning/taxonomy.json', data)
                    self.assertTrue(self.errors())

    def test_missing_scope_note_rejected(self):
        self.change(lambda data: data['vocabularies'][0]['terms'][0].pop('scope_note'))
        self.assert_rejected('missing required scope_note')

    def test_proposal_cannot_claim_acceptance(self):
        self.change(lambda data: data.update(status='accepted'))
        self.assert_rejected('must equal')


class RecordTermTests(CatalogTestCase):
    def test_registered_task_and_domain_pass(self):
        record = self.proposal()
        record.update(task_families=['classification'], domains=['software'])
        self.put('terms.json', record)
        self.assertEqual(self.errors(), [])

    def test_unknown_task_or_domain_rejected(self):
        for field in ('task_families', 'domains'):
            with self.subTest(field=field):
                record = self.proposal()
                record[field] = ['not-a-registered-term']
                self.put('terms.json', record)
                self.assert_rejected(f'unknown {field} term')

    def test_unknown_cannot_coexist_with_known_term(self):
        record = self.proposal()
        record['task_families'] = ['unknown', 'classification']
        self.put('terms.json', record)
        self.assert_rejected('unknown must appear alone')

    def test_explicit_unknown_is_not_filled(self):
        record = self.proposal()
        record.update(task_families=['unknown'], domains=['unknown'])
        self.put('terms.json', record)
        self.assertEqual(self.errors(), [])

    def test_record_vocabulary_is_validated_by_catalog_entrypoint(self):
        import json
        path = self.root / 'planning/taxonomy.json'
        data = json.loads(path.read_text())
        data['record_vocabularies'][0]['terms'].append(
            copy.deepcopy(data['record_vocabularies'][0]['terms'][0]))
        path.write_text(json.dumps(data))
        self.assert_rejected('duplicate term')

    def test_unknown_modality_rejected(self):
        record = self.proposal()
        record['modalities'] = ['Unregistered modality']
        self.put('unknown-modality.json', record)
        self.assert_rejected('unknown modality')

    def test_unknown_category_rejected(self):
        record = self.proposal()
        record['category'] = 'Unregistered category'
        self.put('unknown-category.json', record)
        self.assert_rejected('unknown category')
