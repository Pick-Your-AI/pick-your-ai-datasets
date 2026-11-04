"""Regression coverage for validator rejection paths that had no test.

`DATA-12.04` requires that validators reject each documented defect class. Before this
file, 24 of the 45 rejection sites in `scripts/validate_plan.py` and
`scripts/validate_catalog.py` had no test asserting them, so a refactor could have
silently removed the check and the suite would still have been green.

Each test mutates the committed baseline in a disposable copy and asserts the specific
message. Extra errors from the same mutation are acceptable and not asserted against, so
these stay stable if unrelated checks are added.
"""
import sys
import unittest
from pathlib import Path

# Allow both `unittest discover -s tests` (CI) and direct invocation.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_plan import PlanTestCase  # noqa: E402


class ItemStructureRejections(PlanTestCase):
    """Hierarchy, identity and shape rules."""

    def test_program_must_not_have_an_internal_parent(self):
        self.mutate(lambda b, _by: b['items'][0].update(parent_id='DATA-01'))
        self.assert_rejected('program cannot have an internal parent')

    def test_parent_must_be_the_declared_type(self):
        # An Epic whose parent is a Work Package rather than the Program.
        self.mutate(lambda b, by: by['DATA-01'].update(parent_id='DATA-01.01'))
        self.assert_rejected('parent must be a Program')

    def test_backlog_requires_exactly_one_declared_program(self):
        # schema pins program_id to "DATA"; making the program item disagree with it is
        # the reachable way to break the one-program rule.
        self.mutate(lambda b, _by: b['items'][0].update(id='DATA-02'))
        self.assert_rejected('exactly one program with the declared program_id is required')

    def test_id_must_match_its_record_type_pattern(self):
        # The schema layer rejects this before validate_backlog's own pattern check runs,
        # so the defect class is covered; the message asserted is the one that fires.
        self.mutate(lambda b, _by: b['items'][1].update(id='DATA-1'))
        self.assert_rejected('$.items[1].id: does not match')

    def test_workstream_must_match_the_parent_epic(self):
        self.mutate(lambda b, by: by['DATA-01.01'].update(workstream='09 Metadata'))
        self.assert_rejected('workstream differs from its epic')

    def test_required_list_must_not_be_blank(self):
        self.mutate(lambda b, by: by['DATA-01.01']['deliverables'].append('   '))
        self.assert_rejected('deliverables must be non-empty and trimmed')

    def test_required_list_must_not_be_empty(self):
        # Schema minItems fires first; assert the message that actually rejects it.
        self.mutate(lambda b, by: by['DATA-01.01'].update(non_goals=[]))
        self.assert_rejected('non_goals: fewer than 1 items')

    def test_artifact_path_must_be_repository_relative(self):
        self.mutate(lambda b, by: by['DATA-01.01']['artifact_paths'].append('/etc/passwd'))
        self.assert_rejected('artifact path must be repository-relative')

    def test_artifact_path_must_not_climb_out(self):
        self.mutate(lambda b, by: by['DATA-01.01']['artifact_paths'].append('../outside.md'))
        self.assert_rejected('artifact path must be repository-relative')

    def test_handoff_must_name_a_known_repository(self):
        self.mutate(lambda b, by: by['DATA-01.01']['handoffs'].append(
            {'repository': 'Pick-Your-AI/not-a-repo', 'artifact': 'x', 'direction': 'outbound'}))
        self.assert_rejected('handoff names an unknown repository')


class DependencyRejections(PlanTestCase):
    """The prerequisite graph, which decides what may start."""

    def test_work_package_cannot_block_itself(self):
        self.mutate(lambda b, by: by['DATA-01.02'].update(blocked_by=['DATA-01.02']))
        self.assert_rejected('cannot block itself')


class DecisionRegisterRejections(PlanTestCase):
    """Rules that keep the register from claiming an approval nobody gave."""

    def test_duplicate_decision_id_is_rejected(self):
        reg = self.read('planning/decision-register.json')
        reg['decisions'].append(dict(reg['decisions'][0]))
        self.write('planning/decision-register.json', reg)
        self.assert_rejected('decisions: duplicate decision ID')

    def test_proposed_decision_cannot_record_acceptance(self):
        reg = self.read('planning/decision-register.json')
        reg['decisions'][0].update(accepted_by='someone-else', accepted_on='2026-11-04')
        self.write('planning/decision-register.json', reg)
        self.assert_rejected('a proposed decision cannot record acceptance')


class CoverageAndManifestRejections(PlanTestCase):
    """Rules protecting the generated manifest and the coverage denominators."""

    def test_duplicate_coverage_row_id_is_rejected(self):
        cov = self.read('planning/coverage-matrix.json')
        cov['rows'].append(dict(cov['rows'][0]))
        self.write('planning/coverage-matrix.json', cov)
        self.assert_rejected('coverage: duplicate row ID')

    def test_denominator_requires_its_source_and_date(self):
        cov = self.read('planning/coverage-matrix.json')
        cov['rows'][0].update(denominator=10, denominator_source=None, denominator_counted_on=None)
        self.write('planning/coverage-matrix.json', cov)
        self.assert_rejected('denominator lacks its source or count date')

    def test_accepted_records_cannot_exceed_candidates(self):
        cov = self.read('planning/coverage-matrix.json')
        cov['rows'][0].update(candidate_records=1, accepted_records=2)
        self.write('planning/coverage-matrix.json', cov)
        self.assert_rejected('accepted records exceed candidates')

    def test_manifest_counts_must_match_the_backlog(self):
        manifest = self.read('planning/release-manifest.json')
        manifest['counts']['Work Package'] = manifest['counts']['Work Package'] + 1
        self.write('planning/release-manifest.json', manifest)
        self.assert_rejected('counts drift from the backlog')

    def test_unreleased_foundation_cannot_publish_records(self):
        manifest = self.read('planning/release-manifest.json')
        manifest.update(publishes_records=True)
        self.write('planning/release-manifest.json', manifest)
        self.assert_rejected('an unreleased foundation cannot publish records')

    def test_unpublished_issue_map_cannot_carry_issue_numbers(self):
        issue_map = self.read('planning/issue-map.json')
        issue_map.update(status='not_published', issues={'DATA': 1})
        self.write('planning/issue-map.json', issue_map)
        self.assert_rejected('unpublished map cannot contain issue numbers')


class ProjectFieldRejections(PlanTestCase):
    """The Project field model that every issue's initial values are checked against."""

    def test_duplicate_project_field_names_are_rejected(self):
        backlog = self.read('planning/project-backlog.json')
        backlog['project']['fields'].append(dict(backlog['project']['fields'][0]))
        self.write('planning/project-backlog.json', backlog)
        self.assert_rejected('project: duplicate field names')

    def test_duplicate_project_view_names_are_rejected(self):
        backlog = self.read('planning/project-backlog.json')
        views = backlog['project']['views']
        if len(views) < 2:
            self.skipTest('baseline has a single view')
        views[1]['name'] = views[0]['name']
        self.write('planning/project-backlog.json', backlog)
        self.assert_rejected('project: duplicate view names')

    def test_view_cannot_reference_an_unknown_field(self):
        backlog = self.read('planning/project-backlog.json')
        backlog['project']['views'][0]['visible_fields'].append('Not A Real Field')
        self.write('planning/project-backlog.json', backlog)
        self.assert_rejected('unknown field Not A Real Field')

    def test_project_value_must_be_a_declared_option(self):
        self.mutate(lambda b, by: by['DATA-01.01'].update(priority='P9'))
        self.assert_rejected('is not an option')


if __name__ == '__main__':
    unittest.main()