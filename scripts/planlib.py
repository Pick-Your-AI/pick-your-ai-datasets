"""Shared, network-free helpers for the datasets planning baseline.

The canonical inputs are planning/project-backlog.json and the files it is checked
against. Derived Project field values live here so validators, renderers and
GitHub reconciliation all compute them the same way.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'Pick-Your-AI/pick-your-ai-datasets'
RECORD_TYPES = ('Program', 'Epic', 'Work Package')
PARENT_TYPE = {'Program': None, 'Epic': 'Program', 'Work Package': 'Epic'}
ID_PATTERN = {
    'Program': re.compile(r'DATA'),
    'Epic': re.compile(r'DATA-\d{2}'),
    'Work Package': re.compile(r'DATA-\d{2}\.\d{2}'),
}
TASK_ID = re.compile(r'(DATA-\d{2}\.\d{2})\.T(\d+)')
SUBTASK_ID = re.compile(r'(DATA-\d{2}\.\d{2}\.T\d+)\.S(\d+)')
REQUIRED_LISTS = ('deliverables', 'artifact_paths', 'evidence_requirements', 'acceptance_criteria',
                  'non_goals', 'review_requirements')


def _no_duplicate_keys(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError('duplicate JSON key: ' + key)
        out[key] = value
    return out


def load_json(path: Path):
    """Load UTF-8 JSON, rejecting duplicate keys and non-finite numbers."""
    def bad_constant(value):
        raise ValueError('non-finite JSON number: ' + value)
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=_no_duplicate_keys,
                      parse_constant=bad_constant)


def canonical_sha256(value) -> str:
    data = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def project_values(item: dict, items_by_id: dict) -> dict:
    """Initial Project field values for a planning item.

    These are setup values only. Live Status, Readiness, Acceptance and similar fields
    belong to people triaging the work once the item exists, so reconciliation fills
    empty values and never overwrites a different live value.
    """
    process = item['modality'] == 'Not Applicable'
    if item['record_type'] == 'Work Package':
        waiting = bool(item['blocked_by'])
    else:
        children = [c for c in items_by_id.values() if c['parent_id'] == item['id']]
        leaves = [c for c in children if c['record_type'] == 'Work Package'] or children
        waiting = bool(leaves) and all(c['blocked_by'] for c in leaves)
    return {
        'Status': 'Backlog',
        'Priority': item['priority'],
        'Record Type': item['record_type'],
        'Workstream': item['workstream'],
        'Readiness': 'Blocked' if waiting else 'Ready',
        'Dataset Modality': item['modality'],
        'Dataset Category': item['category'],
        'Access Classification': 'Not Applicable' if process else 'Not Assessed',
        'License/Rights Status': 'Not Applicable' if process else 'Not Assessed',
        'Evidence Confidence': 'Unverified',
        'Source Freshness': 'Not Applicable' if process else 'Not Collected',
        'Dependency Status': 'Waiting' if waiting else 'Unblocked',
        'Effort': item['effort'],
        'Release Phase': item['release_phase'],
        'Acceptance Status': 'Not Started',
    }


def issue_title(item: dict) -> str:
    return f"[{item['id']}] {item['title']}"


def topological_cycle(nodes: dict) -> list | None:
    """Return one dependency cycle as a list of IDs, or None. nodes: id -> iterable of prerequisite ids."""
    state, stack = {}, []

    def visit(node):
        state[node] = 1
        stack.append(node)
        for dep in sorted(nodes.get(node, ())):
            if state.get(dep) == 1:
                return stack[stack.index(dep):] + [dep]
            if dep in nodes and not state.get(dep):
                found = visit(dep)
                if found:
                    return found
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(nodes):
        if not state.get(node):
            found = visit(node)
            if found:
                return found
    return None
