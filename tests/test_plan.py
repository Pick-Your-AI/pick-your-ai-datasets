"""Planning validator regressions. All mutations happen in disposable copies."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import planlib  # noqa: E402
import render_docs  # noqa: E402
import validate_plan  # noqa: E402


class PlanTestCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='datasets-plan-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('planning', 'schemas', 'docs'):
            shutil.copytree(ROOT / name, self.root / name)

    def read(self, rel):
        return json.loads((self.root / rel).read_text(encoding='utf-8'))

    def write(self, rel, data):
        (self.root / rel).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    def errors(self):
        docs, errors = validate_plan.load(self.root)
        if errors:
            return errors
        return validate_plan.validate_backlog(docs['planning/project-backlog.json']) + validate_plan.validate_related(docs)

    def mutate(self, change):
        backlog = self.read('planning/project-backlog.json')
        change(backlog, {i['id']: i for i in backlog['items']})
        self.write('planning/project-backlog.json', backlog)

    def assert_rejected(self, text):
        errors = self.errors()
        self.assertTrue(any(text in e for e in errors), f'{text!r} not in {errors}')


class BaselineTests(PlanTestCase):
    def test_committed_baseline_is_valid(self):
        self.assertEqual(self.errors(), [])

    def test_counts_match_mission_hierarchy(self):
        items = self.read('planning/project-backlog.json')['items']
        epics = [i for i in items if i['record_type'] == 'Epic']
        self.assertEqual(len(epics), 12)
        self.assertEqual([e['id'] for e in epics], [f'DATA-{n:02d}' for n in range(1, 13)])
        for epic in epics:
            self.assertGreaterEqual(sum(i['parent_id'] == epic['id'] for i in items), 4, epic['id'])

    def test_every_work_package_has_tasks_with_subtasks(self):
        for item in self.read('planning/project-backlog.json')['items']:
            if item['record_type'] == 'Work Package':
                self.assertGreaterEqual(len(item['tasks']), 2, item['id'])
                for task in item['tasks']:
                    self.assertTrue(task['subtasks'], task['id'])

    def test_no_planned_item_starts_done_or_accepted(self):
        backlog = self.read('planning/project-backlog.json')
        by_id = {i['id']: i for i in backlog['items']}
        for item in backlog['items']:
            values = planlib.project_values(item, by_id)
            self.assertNotEqual(values['Status'], 'Done')
            self.assertEqual(values['Acceptance Status'], 'Not Started')


class HierarchyTests(PlanTestCase):
    def test_duplicate_canonical_id(self):
        self.mutate(lambda b, by: b['items'].append(dict(by['DATA-01.01'])))
        self.assert_rejected('duplicate canonical ID')

    def test_missing_parent(self):
        self.mutate(lambda b, by: by['DATA-01.01'].update(parent_id='DATA-99'))
        self.assert_rejected('does not exist')

    def test_wrong_parent_type(self):
        self.mutate(lambda b, by: by['DATA-01.01'].update(parent_id='DATA'))
        self.assert_rejected('parent must be a Epic')

    def test_id_not_nested_under_parent(self):
        self.mutate(lambda b, by: by['DATA-01.01'].update(parent_id='DATA-02'))
        self.assert_rejected('not nested under its parent')

    def test_work_package_without_tasks(self):
        self.mutate(lambda b, by: by['DATA-01.01'].update(tasks=[]))
        self.assert_rejected('work package has no tasks')

    def test_out_of_sequence_task(self):
        self.mutate(lambda b, by: by['DATA-01.01']['tasks'][0].update(id='DATA-01.01.T9'))
        self.assert_rejected('out of sequence')

    def test_duplicate_subtask_identity(self):
        def change(b, by):
            tasks = by['DATA-01.01']['tasks']
            tasks[1]['subtasks'][0]['id'] = tasks[0]['subtasks'][0]['id']
        self.mutate(change)
        self.assert_rejected('out of sequence')

    def test_missing_acceptance_criteria(self):
        self.mutate(lambda b, by: by['DATA-04.01'].update(acceptance_criteria=[]))
        self.assert_rejected('fewer than 1 items')

    def test_blank_acceptance_criterion(self):
        self.mutate(lambda b, by: by['DATA-04.01'].update(acceptance_criteria=[' padded ']))
        self.assert_rejected('acceptance_criteria must be non-empty and trimmed')

    def test_epic_cannot_carry_checklist_tasks(self):
        self.mutate(lambda b, by: by['DATA-01'].update(tasks=by['DATA-01.01']['tasks']))
        self.assert_rejected('only work packages carry checklist tasks')


class DependencyTests(PlanTestCase):
    def test_cycle(self):
        self.mutate(lambda b, by: by['DATA-01.01']['blocked_by'].append('DATA-01.03'))
        self.assert_rejected('cycle')

    def test_unknown_prerequisite(self):
        self.mutate(lambda b, by: by['DATA-01.01']['blocked_by'].append('DATA-01.99'))
        self.assert_rejected('prerequisite DATA-01.99 does not exist')

    def test_hierarchy_is_not_a_dependency(self):
        self.mutate(lambda b, by: by['DATA-01.01']['blocked_by'].append('DATA-01'))
        self.assert_rejected('prerequisites link work packages only')

    def test_later_phase_prerequisite(self):
        self.mutate(lambda b, by: by['DATA-01.01']['blocked_by'].append('DATA-12.05'))
        self.assert_rejected('from a later release phase')


class ProjectAndDriftTests(PlanTestCase):
    def test_unknown_field_option(self):
        self.mutate(lambda b, by: by['DATA-01.01'].update(effort='Huge'))
        self.assert_rejected("Effort value 'Huge' is not an option")

    def test_view_references_unknown_field(self):
        self.mutate(lambda b, by: b['project']['views'][0]['visible_fields'].append('Nonexistent'))
        self.assert_rejected('unknown field Nonexistent')

    def test_manifest_drift(self):
        self.mutate(lambda b, by: by['DATA-01.01'].update(title='Changed title'))
        self.assert_rejected('backlog hash drift')

    def test_issue_map_must_cover_every_item(self):
        issue_map = self.read('planning/issue-map.json')
        issue_map.update(status='published', issues={'DATA': 1})
        self.write('planning/issue-map.json', issue_map)
        self.assert_rejected('mapped IDs differ from backlog IDs')

    def test_issue_map_duplicate_number(self):
        backlog = self.read('planning/project-backlog.json')
        issue_map = self.read('planning/issue-map.json')
        issue_map.update(status='published', issues={i['id']: 1 for i in backlog['items']})
        self.write('planning/issue-map.json', issue_map)
        self.assert_rejected('an issue number is mapped twice')

    def test_self_accepted_decision(self):
        register = self.read('planning/decision-register.json')
        d = register['decisions'][0]
        d.update(status='accepted', accepted_on='2026-10-23', accepted_by=d['proposed_by'])
        self.write('planning/decision-register.json', register)
        self.assert_rejected('acceptance requires a different, dated acceptor')

    def test_coverage_requires_counted_denominator(self):
        coverage = self.read('planning/coverage-matrix.json')
        coverage['rows'][0].update(status='counted')
        self.write('planning/coverage-matrix.json', coverage)
        self.assert_rejected('requires a denominator')

    def test_coverage_owner_must_be_work_package(self):
        coverage = self.read('planning/coverage-matrix.json')
        coverage['rows'][0].update(owning_work_package='DATA-99.01')
        self.write('planning/coverage-matrix.json', coverage)
        self.assert_rejected('owning work package does not exist')


class GeneratedDocumentTests(PlanTestCase):
    def test_generated_outputs_are_current(self):
        files = render_docs.render(ROOT)
        for path, text in files.items():
            self.assertEqual((ROOT / path).read_text(encoding='utf-8'), text, path)

    def test_hand_edit_is_detected(self):
        shutil.copytree(ROOT / 'planning', self.root / 'planning', dirs_exist_ok=True)
        path = self.root / 'docs/DELIVERY_PLAN.md'
        path.write_text(path.read_text(encoding='utf-8') + 'hand edit\n', encoding='utf-8')
        self.assertEqual(render_docs.main(['--root', str(self.root), '--check']), 1)

    def test_unexpected_issue_body_is_detected(self):
        (self.root / 'planning/issues/DATA-99.md').write_text('stray\n', encoding='utf-8')
        self.assertEqual(render_docs.main(['--root', str(self.root), '--check']), 1)


if __name__ == '__main__':
    unittest.main()
