#!/usr/bin/env python3
"""Validate the datasets planning baseline; optionally audit live GitHub drift (read-only).

Offline checks: schemas, unique canonical IDs, parent/child hierarchy, task and subtask
completeness, required acceptance content, prerequisites and cycles, Project field
options and views, coverage ownership, decisions, release manifest and issue map.

--live additionally reads GitHub through the authenticated `gh` CLI and reports drift
between the plan and actual issues, native parents, blockers and Project items. It never
writes to GitHub. Differing live Project values are reported as triage, not errors.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import planlib  # noqa: E402
import schemalib  # noqa: E402

FILES = {
    'planning/project-backlog.json': 'planning-backlog',
    'planning/coverage-matrix.json': 'planning-coverage',
    'planning/decision-register.json': 'planning-decisions',
    'planning/release-manifest.json': 'planning-release',
    'planning/issue-map.json': 'planning-issue-map',
}
ORG_REPOSITORIES = {'Pick-Your-AI/' + name for name in (
    'pick-your-ai-research', 'pick-your-ai-catalog-pipeline', 'pick-your-ai-applications', 'pick-your-ai-papers',
    'pick-your-ai-website', 'pick-your-ai-datasets', 'pick-your-ai-android', 'pick-your-ai-apple')}


def load(root: Path):
    docs, problems = {}, []
    for path, schema_name in FILES.items():
        try:
            schema = planlib.load_json(root / 'schemas' / f'{schema_name}.schema.json')
            problems += schemalib.unsupported_keywords(schema, f'schemas/{schema_name}.schema.json')
            data = planlib.load_json(root / path)
            problems += [path + ': ' + e for e in schemalib.errors(data, schema)]
            docs[path] = data
        except (OSError, ValueError) as exc:
            problems.append(f'{path}: {exc}')
    return docs, problems


def validate_backlog(backlog: dict) -> list[str]:
    errors = []
    items = backlog['items']
    by_id = {}
    for item in items:
        if item['id'] in by_id:
            errors.append(item['id'] + ': duplicate canonical ID')
        by_id[item['id']] = item
    programs = [i for i in items if i['record_type'] == 'Program']
    if len(programs) != 1 or programs[0]['id'] != backlog['program_id']:
        errors.append('backlog: exactly one program with the declared program_id is required')
    seen_steps = set()
    for item in items:
        iid, kind = item['id'], item['record_type']
        if not planlib.ID_PATTERN[kind].fullmatch(iid):
            errors.append(f'{iid}: ID does not match the {kind} pattern')
        parent = by_id.get(item['parent_id']) if item['parent_id'] else None
        if planlib.PARENT_TYPE[kind] is None:
            if item['parent_id'] is not None:
                errors.append(f'{iid}: program cannot have an internal parent')
        elif not parent:
            errors.append(f'{iid}: parent {item["parent_id"]} does not exist')
        elif parent['record_type'] != planlib.PARENT_TYPE[kind]:
            errors.append(f'{iid}: parent must be a {planlib.PARENT_TYPE[kind]}')
        elif not iid.startswith(parent['id'] + ('-' if kind == 'Epic' else '.')):
            errors.append(f'{iid}: ID is not nested under its parent {parent["id"]}')
        for key in planlib.REQUIRED_LISTS:
            if not item[key] or any(not str(v).strip() or str(v) != str(v).strip() for v in item[key]):
                errors.append(f'{iid}: {key} must be non-empty and trimmed')
        if kind == 'Work Package':
            if not item['tasks']:
                errors.append(f'{iid}: work package has no tasks')
            if parent and item['workstream'] != parent['workstream']:
                errors.append(f'{iid}: workstream differs from its epic')
        elif item['tasks']:
            errors.append(f'{iid}: only work packages carry checklist tasks')
        for n, task in enumerate(item['tasks'], 1):
            if task['id'] != f'{iid}.T{n}':
                errors.append(f'{iid}: task {task["id"]} is out of sequence (expected {iid}.T{n})')
            for m, sub in enumerate(task['subtasks'], 1):
                if sub['id'] != f'{task["id"]}.S{m}':
                    errors.append(f'{task["id"]}: subtask {sub["id"]} is out of sequence')
            for step in [task, *task['subtasks']]:
                if step['id'] in seen_steps or step['id'] in by_id:
                    errors.append(step['id'] + ': duplicate task identity')
                seen_steps.add(step['id'])
        for handoff in item['handoffs']:
            if handoff['repository'] not in ORG_REPOSITORIES:
                errors.append(f'{iid}: handoff names an unknown repository {handoff["repository"]}')
        for path in item['artifact_paths']:
            if path.startswith('/') or '..' in Path(path).parts:
                errors.append(f'{iid}: artifact path must be repository-relative: {path}')
    graph = {}
    for item in items:
        deps = item['blocked_by']
        graph[item['id']] = deps
        for dep in deps:
            target = by_id.get(dep)
            if not target:
                errors.append(f'{item["id"]}: prerequisite {dep} does not exist')
            elif dep == item['id']:
                errors.append(f'{item["id"]}: cannot block itself')
            elif item['record_type'] != 'Work Package' or target['record_type'] != 'Work Package':
                errors.append(f'{item["id"]}: prerequisites link work packages only; hierarchy is not a dependency')
            elif target['parent_id'] == item['id'] or item['parent_id'] == dep:
                errors.append(f'{item["id"]}: prerequisite duplicates the parent relationship')
    cycle = planlib.topological_cycle(graph)
    if cycle:
        errors.append('dependencies: cycle ' + ' -> '.join(cycle))
    fields = {f['name']: f for f in backlog['project']['fields']}
    if len(fields) != len(backlog['project']['fields']):
        errors.append('project: duplicate field names')
    phases = fields.get('Release Phase', {}).get('options', [])
    for item in items:
        for dep in item['blocked_by']:
            if dep in by_id and phases and by_id[dep]['release_phase'] in phases and item['release_phase'] in phases \
                    and phases.index(by_id[dep]['release_phase']) > phases.index(item['release_phase']):
                errors.append(f'{item["id"]}: depends on {dep} from a later release phase')
        for name, value in planlib.project_values(item, by_id).items():
            if name not in fields:
                errors.append(f'project: derived field {name} is not defined')
            elif value not in fields[name]['options']:
                errors.append(f'{item["id"]}: {name} value {value!r} is not an option')
    builtin = {'Title', 'Assignees', 'Labels', 'Parent issue', 'Sub-issues progress', 'Repository', 'Milestone', 'Linked pull requests'}
    names = [v['name'] for v in backlog['project']['views']]
    if len(names) != len(set(names)):
        errors.append('project: duplicate view names')
    for view in backlog['project']['views']:
        for ref in [*view['visible_fields'], *view['sort_by'], *([view['group_by']] if view['group_by'] else [])]:
            if ref not in fields and ref not in builtin:
                errors.append(f'view {view["name"]}: unknown field {ref}')
    return errors


def validate_related(docs: dict) -> list[str]:
    errors = []
    backlog = docs['planning/project-backlog.json']
    items = backlog['items']
    by_id = {i['id']: i for i in items}
    rows = docs['planning/coverage-matrix.json']['rows']
    if len({r['id'] for r in rows}) != len(rows):
        errors.append('coverage: duplicate row ID')
    for row in rows:
        owner = by_id.get(row['owning_work_package'])
        if not owner or owner['record_type'] != 'Work Package':
            errors.append(f'{row["id"]}: owning work package does not exist')
        if row['denominator'] is None and (row['denominator_source'] or row['denominator_counted_on'] or row['status'] in ('counted', 'accepted')):
            errors.append(f'{row["id"]}: a counted status or denominator source requires a denominator')
        if row['denominator'] is not None and not (row['denominator_source'] and row['denominator_counted_on']):
            errors.append(f'{row["id"]}: denominator lacks its source or count date')
        if row['accepted_records'] > row['candidate_records']:
            errors.append(f'{row["id"]}: accepted records exceed candidates')
    decisions = docs['planning/decision-register.json']['decisions']
    if len({d['id'] for d in decisions}) != len(decisions):
        errors.append('decisions: duplicate decision ID')
    for d in decisions:
        if d['status'] == 'accepted' and (not d['accepted_by'] or not d['accepted_on'] or d['accepted_by'] == d['proposed_by']):
            errors.append(f'{d["id"]}: acceptance requires a different, dated acceptor')
        if d['status'] == 'proposed' and (d['accepted_by'] or d['accepted_on']):
            errors.append(f'{d["id"]}: a proposed decision cannot record acceptance')
    manifest = docs['planning/release-manifest.json']
    expected = {t: sum(i['record_type'] == t for i in items) for t in planlib.RECORD_TYPES}
    expected.update(tasks=sum(len(i['tasks']) for i in items), subtasks=sum(len(t['subtasks']) for i in items for t in i['tasks']),
                    prerequisites=sum(len(i['blocked_by']) for i in items), internal_parents=sum(i['parent_id'] is not None for i in items),
                    project_field_values=len(items) * len(backlog['project']['fields']))
    if manifest['counts'] != expected:
        errors.append('release manifest: counts drift from the backlog')
    if manifest['backlog_items_sha256'] != planlib.canonical_sha256(items):
        errors.append('release manifest: backlog hash drift')
    if manifest['publishes_records'] and manifest['status'] != 'released':
        errors.append('release manifest: an unreleased foundation cannot publish records')
    issue_map = docs['planning/issue-map.json']
    mapped = issue_map['issues']
    if issue_map['status'] == 'published':
        if set(mapped) != set(by_id):
            errors.append('issue map: mapped IDs differ from backlog IDs: missing=%s extra=%s'
                          % (sorted(set(by_id) - set(mapped)), sorted(set(mapped) - set(by_id))))
        if len(set(mapped.values())) != len(mapped):
            errors.append('issue map: an issue number is mapped twice')
    elif mapped:
        errors.append('issue map: unpublished map cannot contain issue numbers')
    return errors


def gh_json(args):
    out = subprocess.run(['gh', *args], capture_output=True, text=True, timeout=120)
    if out.returncode:
        raise RuntimeError(out.stderr.strip() or 'gh failed')
    return json.loads(out.stdout)


def live_drift(root: Path, docs: dict) -> dict:
    """Read-only comparison of the plan with GitHub issues, relationships and Project items."""
    backlog = docs['planning/project-backlog.json']
    by_id = {i['id']: i for i in backlog['items']}
    mapped = docs['planning/issue-map.json']['issues']
    number_to_id = {n: i for i, n in mapped.items()}
    repo = planlib.REPOSITORY
    issues = {}
    for page in gh_json(['api', '--paginate', '--slurp', f'repos/{repo}/issues?state=all&per_page=100']):
        for issue in page:
            if 'pull_request' not in issue:
                issues[issue['number']] = issue
    report = {'issues_read': len(issues), 'problems': [], 'triage_differences': [], 'project_items': 0}
    for sid, number in mapped.items():
        issue = issues.get(number)
        if not issue:
            report['problems'].append(f'{sid}: mapped issue #{number} not found')
            continue
        item = by_id[sid]
        if issue['title'] != planlib.issue_title(item):
            report['problems'].append(f'{sid}: title drift on #{number}')
        body = (root / 'planning/issues' / f'{sid}.md').read_text(encoding='utf-8')
        if (issue.get('body') or '').strip() != body.strip():
            report['problems'].append(f'{sid}: body drift on #{number}')
        expected_parent = mapped.get(item['parent_id']) if item['parent_id'] else None
        try:
            parent = gh_json(['api', f'repos/{repo}/issues/{number}/parent'])
            actual_parent = parent['number'] if parent['repository_url'].endswith(repo) else parent['html_url']
        except RuntimeError:
            actual_parent = None
        if item['parent_id'] is None:
            if actual_parent != backlog['external_parent']:
                report['problems'].append(f'{sid}: external parent is {actual_parent!r}, expected {backlog["external_parent"]}')
        elif actual_parent != expected_parent:
            report['problems'].append(f'{sid}: native parent is {actual_parent!r}, expected #{expected_parent}')
        blockers = {b['number'] for b in gh_json(['api', '--paginate', f'repos/{repo}/issues/{number}/dependencies/blocked_by'])}
        wanted = {mapped[d] for d in item['blocked_by']}
        if blockers != wanted:
            report['problems'].append(f'{sid}: blockers {sorted(blockers)} differ from planned {sorted(wanted)}')
    extra = sorted(n for n in issues if n not in number_to_id)
    if extra:
        report['problems'].append(f'unmapped repository issues: {extra}')
    live_items = project_items(backlog['project']['number'])
    report['project_items'] = len(live_items)
    for sid, number in mapped.items():
        values = live_items.get(number)
        if values is None:
            report['problems'].append(f'{sid}: #{number} is not a Project item')
            continue
        for name, want in planlib.project_values(by_id[sid], by_id).items():
            have = values.get(name)
            if have is None:
                report['problems'].append(f'{sid}: Project field {name} is empty')
            elif have != want:
                report['triage_differences'].append(f'{sid}: {name} is {have!r} (initial {want!r})')
    stray = sorted(set(live_items) - set(number_to_id))
    if stray:
        report['problems'].append(f'Project items outside the plan: {stray}')
    return report


PROJECT_QUERY = '''query($n:Int!,$c:String){organization(login:"Pick-Your-AI"){projectV2(number:$n){items(first:100,after:$c){
 pageInfo{hasNextPage endCursor} nodes{content{... on Issue{number repository{nameWithOwner}}}
 fieldValues(first:50){nodes{... on ProjectV2ItemFieldSingleSelectValue{name field{... on ProjectV2FieldCommon{name}}}}}}}}}}'''


def project_items(number: int) -> dict:
    """Map issue number -> {field name: single-select value} for every Project item in this repository."""
    out, cursor = {}, None
    while True:
        args = ['api', 'graphql', '-f', 'query=' + PROJECT_QUERY, '-F', f'n={number}']
        if cursor:
            args += ['-f', f'c={cursor}']
        page = gh_json(args)['data']['organization']['projectV2']['items']
        for node in page['nodes']:
            content = node['content'] or {}
            if (content.get('repository') or {}).get('nameWithOwner') == planlib.REPOSITORY:
                out[content['number']] = {v['field']['name']: v['name'] for v in node['fieldValues']['nodes'] if v.get('field')}
        if not page['pageInfo']['hasNextPage']:
            return out
        cursor = page['pageInfo']['endCursor']


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--root', type=Path, default=planlib.ROOT)
    parser.add_argument('--live', action='store_true', help='also read GitHub (read-only) and report drift')
    args = parser.parse_args(argv)
    docs, errors = load(args.root)
    if not errors:
        errors += validate_backlog(docs['planning/project-backlog.json'])
        errors += validate_related(docs)
    result = {'status': 'failed' if errors else 'passed', 'errors': sorted(set(errors))}
    if not errors:
        items = docs['planning/project-backlog.json']['items']
        result['counts'] = docs['planning/release-manifest.json']['counts']
        if args.live:
            result['live'] = live_drift(args.root, docs)
            if result['live']['problems']:
                result['status'] = 'drift'
        result['items'] = len(items)
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
