#!/usr/bin/env python3
"""Validate dataset and benchmark proposal records without network access.

Checks schema shape, unique record and version identities, dataset/version ambiguity,
missing or unresolved source metadata, rights and publication states, withdrawals,
relationship endpoints and cycles, synthetic-data placement, and accidental personal data.
Passing does not verify that a source is true or that a license permits a use.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import planlib  # noqa: E402
import schemalib  # noqa: E402

PROPOSALS = 'catalog/proposals'
EXAMPLES = 'examples'
PUBLISHABLE = ('eligible', 'published')
RIGHTS_OK = ('Permitted for Metadata Use', 'Conditional')
ACYCLIC = ('derived_from', 'subset_of', 'superseded_by', 'translated_from')
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
PHONE = re.compile(r'(?<![\w.-])(?:\+\d{1,3}[ .-]?)?(?:\(\d{2,4}\)[ .-]?)?\d{3,4}[ .-]\d{3,4}(?:[ .-]\d{2,4})?(?![\w.-])')


def personal_data(value, at='$'):
    hits = []
    if isinstance(value, dict):
        for key, item in value.items():
            hits += personal_data(item, f'{at}.{key}')
    elif isinstance(value, list):
        for n, item in enumerate(value):
            hits += personal_data(item, f'{at}[{n}]')
    elif isinstance(value, str) and not value.startswith('https://') and (EMAIL.search(value) or PHONE.search(value)):
        hits.append(at)
    return hits


def validate_records(records: dict, today: dt.date, publication: bool, expect_synthetic: bool, root: Path) -> list[str]:
    errors = []
    options = {f['name']: f['options'] for f in planlib.load_json(root / 'planning/project-backlog.json')['project']['fields']}
    ids, version_ids, labels = {}, {}, set()
    for path, record in records.items():
        rid = record['record_id']
        if rid in ids:
            errors.append(f'{path}: duplicate record ID {rid} (also {ids[rid]})')
        ids[rid] = path
        for v in record['versions']:
            if v['version_id'] in version_ids:
                errors.append(f'{path}: duplicate version ID {v["version_id"]}')
            version_ids[v['version_id']] = rid
    for path, record in records.items():
        rid, p = record['record_id'], path + ': '
        if record['synthetic'] != expect_synthetic:
            errors.append(p + ('synthetic records belong in examples/ or tests/, never catalog/proposals/' if record['synthetic']
                               else 'examples must be explicitly synthetic'))
        if not rid.startswith(record['kind'] + '.'):
            errors.append(p + 'record ID prefix does not match its kind')
        sources = {}
        for s in record['sources']:
            if s['source_id'] in sources:
                errors.append(p + 'duplicate source ID ' + s['source_id'])
            sources[s['source_id']] = s
            if dt.date.fromisoformat(s['accessed_on']) > today:
                errors.append(p + f'source {s["source_id"]} has a future access date')

        def need(source_id, what):
            if source_id not in sources:
                errors.append(p + f'{what} cites missing source metadata {source_id}')
        need(record['publisher']['source_id'], 'publisher')
        for m in record['modalities']:
            if m not in options['Dataset Modality'] or m == 'Not Applicable':
                errors.append(p + f'unknown modality {m}')
        if record['category'] not in options['Dataset Category'] or record['category'] == 'Not Applicable':
            errors.append(p + f'unknown category {record["category"]}')
        if record['rights']['access_classification'] not in options['Access Classification']:
            errors.append(p + 'unknown access classification')
        if record['rights']['rights_status'] not in options['License/Rights Status']:
            errors.append(p + 'unknown rights status')
        for v in record['versions']:
            vp = p + v['version_id'] + ': '
            if not v['version_id'].startswith(rid + '@'):
                errors.append(vp + 'version does not belong to this record')
            if v['unversioned'] != (v['version_label'] is None):
                errors.append(vp + 'a version label is required unless the reference is explicitly unversioned')
            if v['version_label'] is not None:
                if (rid, v['version_label']) in labels:
                    errors.append(vp + 'version label is ambiguous: used twice for one dataset')
                labels.add((rid, v['version_label']))
            if v['unversioned'] and record['publication_state'] in PUBLISHABLE:
                errors.append(vp + 'an unversioned reference is ambiguous and cannot be published')
            split_ids = [s['split_id'] for s in v['splits']]
            if len(split_ids) != len(set(split_ids)):
                errors.append(vp + 'duplicate split within a version')
            need(v['license']['source_id'], 'license')
            for sid in v['source_ids']:
                need(sid, 'version')
            if v['released_on'] and dt.date.fromisoformat(v['released_on']) > today:
                errors.append(vp + 'future release date')
        uses = [x['use'] for x in record['rights']['permissions']]
        if len(uses) != len(set(uses)):
            errors.append(p + 'conflicting duplicate permission for one use')
        for perm in record['rights']['permissions']:
            need(perm['source_id'], 'permission')
            if perm['decision'] == 'conditional' and not perm['conditions']:
                errors.append(p + f'conditional {perm["use"]} permission lacks its conditions')
        for rel in record['relationships']:
            need(rel['source_id'], 'relationship')
            if rel['object'] not in ids and rel['object'] not in version_ids:
                errors.append(p + f'relationship {rel["predicate"]} targets unknown record or version {rel["object"]}')
            if rel['object'] == rid or version_ids.get(rel['object']) == rid:
                errors.append(p + 'record relates to itself')
        state = record['publication_state']
        withdrawal = record['withdrawal']
        if (state == 'withdrawn') != (withdrawal is not None):
            errors.append(p + 'withdrawn state and withdrawal event must appear together')
        if withdrawal:
            need(withdrawal['source_id'], 'withdrawal')
            if sources.get(withdrawal['source_id'], {}).get('role') != 'notice':
                errors.append(p + 'withdrawal must cite an authoritative notice source')
        accepted = {r['kind'] for r in record['reviews'] if r['decision'] == 'accepted' and r['reviewer'] != record['proposed_by']}
        for r in record['reviews']:
            if r['reviewer'] == record['proposed_by'] and r['decision'] == 'accepted':
                errors.append(p + f'self-review cannot accept the {r["kind"]} review')
        gated = state in PUBLISHABLE or publication
        if gated:
            if publication and state != 'published' and state != 'eligible':
                errors.append(p + f'publication gate rejects a {state} proposal')
            if record['rights']['rights_status'] not in RIGHTS_OK:
                errors.append(p + 'publication requires reviewed, permitted rights status')
            if record['rights']['access_classification'] == 'Not Assessed':
                errors.append(p + 'publication requires an assessed access classification')
            display = [x for x in record['rights']['permissions'] if x['use'] == 'metadata_display']
            if not display or display[0]['decision'] not in ('allowed', 'conditional') or not display[0]['reviewed']:
                errors.append(p + 'publication requires a reviewed metadata_display permission')
            if any(not x['reviewed'] for x in record['rights']['permissions']):
                errors.append(p + 'publication requires every recorded permission to be reviewed')
            for kind in ('rights', 'editorial', 'evidence'):
                if kind not in accepted:
                    errors.append(p + f'publication requires an independent accepted {kind} review')
        if personal_data(record):
            errors.append(p + 'possible personal contact data at ' + ', '.join(personal_data(record)))
    graph = {}
    for record in records.values():
        for rel in record['relationships']:
            if rel['predicate'] in ACYCLIC:
                target = version_ids.get(rel['object'], rel['object'])
                graph.setdefault(record['record_id'], set()).add(target)
    cycle = planlib.topological_cycle(graph)
    if cycle:
        errors.append('relationships: lineage cycle ' + ' -> '.join(cycle))
    return errors


def load_records(root: Path, directory: str):
    schema = planlib.load_json(root / 'schemas/dataset-record.schema.json')
    problems = schemalib.unsupported_keywords(schema, 'schemas/dataset-record.schema.json')
    records = {}
    for path in sorted((root / directory).glob('*.json')):
        rel = str(path.relative_to(root))
        try:
            data = planlib.load_json(path)
        except (OSError, ValueError) as exc:
            problems.append(f'{rel}: {exc}')
            continue
        shape = schemalib.errors(data, schema)
        problems += [f'{rel}: {e}' for e in shape]
        if not shape:
            records[rel] = data
    return records, problems


def validate(root: Path, publication=False, today=None):
    today = today or dt.date.today()
    errors, stats = [], {}
    for directory, synthetic in ((PROPOSALS, False), (EXAMPLES, True)):
        records, problems = load_records(root, directory)
        errors += problems
        if not problems:
            errors += validate_records(records, today, publication and directory == PROPOSALS, synthetic, root)
        stats[directory] = len(records)
    stray = [str(p.relative_to(root)) for d in ('catalog', 'evidence', 'research') for p in (root / d).rglob('*')
             if p.is_file() and p.suffix.lower() not in ('.json', '.md')]
    errors += [f'{s}: only JSON metadata and Markdown notes are permitted; dataset contents must not be committed' for s in stray]
    return sorted(set(errors)), stats


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--root', type=Path, default=planlib.ROOT)
    parser.add_argument('--publication', action='store_true', help='require every proposal to pass publication gates')
    args = parser.parse_args(argv)
    errors, stats = validate(args.root, args.publication)
    print(json.dumps({'status': 'failed' if errors else 'passed', 'mode': 'publication' if args.publication else 'research',
                      'records': stats, 'errors': errors}, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
