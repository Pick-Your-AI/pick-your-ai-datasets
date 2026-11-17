#!/usr/bin/env python3
"""Fail-closed, offline registration and schema checks for checkout JSON artifacts."""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import re
import stat

import schemalib

PLAN_SCHEMAS = {
    'planning/project-backlog.json': 'schemas/planning-backlog.schema.json',
    'planning/coverage-matrix.json': 'schemas/planning-coverage.schema.json',
    'planning/decision-register.json': 'schemas/planning-decisions.schema.json',
    'planning/release-manifest.json': 'schemas/planning-release.schema.json',
    'planning/issue-map.json': 'schemas/planning-issue-map.schema.json',
}
RECORD_SCHEMA = 'schemas/dataset-record.schema.json'
SCHEMA_FILES = frozenset((*PLAN_SCHEMAS.values(), RECORD_SCHEMA))
LOCAL_SCHEMA = '@local-schema-subset-v1'
RECORD_PATH = re.compile(r'(catalog/proposals|examples)/[a-z0-9][a-z0-9._-]*\.json')


def obj(properties, required=None, additional=False):
    return {'type': 'object', 'properties': properties,
            'required': list(properties) if required is None else required,
            'additionalProperties': additional}


def array(items, minimum=0):
    return {'type': 'array', 'items': items, 'minItems': minimum}


TEXT = {'type': 'string', 'minLength': 1}
HASH = {'type': 'string', 'pattern': '[a-f0-9]{64}'}
NATURAL = {'type': 'integer', 'minimum': 0}
COMMAND = {'anyOf': [TEXT, array(TEXT, 1)]}
PASEO_SCHEMA = obj({
    'worktree': obj({'setup': COMMAND, 'teardown': COMMAND}),
    'scripts': {'type': 'object', 'additionalProperties': obj({'command': TEXT})},
})
CHIP = obj({'box': array({'type': 'number'}, 4), 'kind': TEXT, 'source': TEXT, 'text': TEXT})
IMAGE = obj({'bytes': NATURAL, 'chips': array(CHIP), 'icon_source': TEXT,
             'px': array(NATURAL, 2), 'repository_id': NATURAL,
             'scale': {'type': 'number', 'minimum': 0}, 'sha256': HASH})
SHOWCASE_SCHEMA = obj({
    'config_sha256': HASH, 'fingerprint': HASH,
    'inputs': obj({**{k: TEXT for k in ('description', 'language', 'license', 'owner', 'repo',
                                      'type', 'visibility')},
                   'icon_sha256': HASH, 'override_sha256': HASH, 'topics': array(TEXT)}),
    'outputs': obj({'banner.png': IMAGE,
                    'card.svg': obj({'bytes': NATURAL, 'repository_id': NATURAL, 'sha256': HASH})}),
    'schema': {'type': 'integer', 'const': 1}, 'skill_version': TEXT,
    'standard': {'type': 'string', 'const': 'ct-std-v1'},
})
# Exact optional configuration paths proposed by pending PRs #76 and #80.
CONFIG_SCHEMAS = {'paseo.json': PASEO_SCHEMA, 'docs/images/.showcase.json': SHOWCASE_SCHEMA}


def registration(relative: str) -> str | None:
    """Return the explicit schema identifier; never infer one from file contents."""
    if relative in PLAN_SCHEMAS:
        return PLAN_SCHEMAS[relative]
    if relative in SCHEMA_FILES:
        return LOCAL_SCHEMA
    if relative in CONFIG_SCHEMAS:
        return '@config/' + relative
    if RECORD_PATH.fullmatch(relative):
        return RECORD_SCHEMA
    return None


def schema_errors(schema, at='schema') -> list[str]:
    """Validate the schema artifact against the supported local schema contract.

    This is deliberately narrower than the full 2020-12 metaschema. In particular,
    schemalib replaces a $ref node and returns early for anyOf, so validation siblings
    of those keywords would silently lose constraints and must be rejected here.
    """
    problems, references = [], []
    definitions = schema.get('$defs', {}) if isinstance(schema, dict) else {}
    types = set(schemalib.TYPES) | {'integer', 'number'}
    annotations = {'$schema', '$id', 'title', 'description', '$defs'}

    def error(where, message):
        problems.append(f'{where}: {message}')

    def walk(node, where, owner=None):
        if not isinstance(node, dict):
            error(where, 'schema must be an object (boolean schemas are unsupported)')
            return
        for key in node:
            if key not in schemalib.SUPPORTED:
                error(where, f'unsupported schema keyword {key}')
        for key in ('$schema', '$id', 'title', 'description'):
            if key in node and not isinstance(node[key], str):
                error(where, f'{key} must be a string')
        if '$schema' in node and node['$schema'] != 'https://json-schema.org/draft/2020-12/schema':
            error(where, 'only the declared 2020-12 dialect is supported locally')
        for key in ('$ref', 'anyOf'):
            if key in node and set(node) - annotations - {key}:
                error(where, f'{key} validation siblings are unsupported by schemalib')
        if '$ref' in node:
            ref = node['$ref']
            if not isinstance(ref, str) or not re.fullmatch(r'#/\$defs/[A-Za-z0-9._-]+', ref):
                error(where, 'only local #/$defs/name references are allowed')
            else:
                target = ref.removeprefix('#/$defs/')
                references.append((owner, target))
                if not isinstance(definitions, dict) or target not in definitions:
                    error(where, f'dangling local reference {ref}')
        if 'type' in node:
            options = node['type'] if isinstance(node['type'], list) else [node['type']]
            if not options or any(not isinstance(t, str) or t not in types for t in options):
                error(where, 'type must name supported JSON types')
            elif len(set(options)) != len(options):
                error(where, 'type options must be unique')
        for key in ('properties', '$defs'):
            if key in node:
                if not isinstance(node[key], dict):
                    error(where, f'{key} must be an object')
                else:
                    for name, sub in node[key].items():
                        child_owner = name if key == '$defs' and node is schema else owner
                        walk(sub, f'{where}.{key}.{name}', child_owner)
        if 'required' in node:
            req = node['required']
            if not isinstance(req, list) or any(not isinstance(v, str) for v in req):
                error(where, 'required must be an array of strings')
            elif len(req) != len(set(req)):
                error(where, 'required names must be unique')
        for key in ('items', 'additionalProperties'):
            if key in node:
                if key == 'additionalProperties' and isinstance(node[key], bool):
                    continue
                walk(node[key], where + '.' + key, owner)
        if 'anyOf' in node:
            if not isinstance(node['anyOf'], list) or not node['anyOf']:
                error(where, 'anyOf must be a non-empty array of schemas')
            else:
                for n, sub in enumerate(node['anyOf']):
                    walk(sub, f'{where}.anyOf[{n}]', owner)
        for key in ('minLength', 'maxLength', 'minItems'):
            if key in node and (type(node[key]) is not int or node[key] < 0):
                error(where, f'{key} must be a non-negative integer')
        if all(type(node.get(k)) is int for k in ('minLength', 'maxLength')):
            if node['minLength'] > node['maxLength']:
                error(where, 'minLength exceeds maxLength')
        if 'minimum' in node and (type(node['minimum']) not in (int, float)
                                  or (type(node['minimum']) is float and not math.isfinite(node['minimum']))):
            error(where, 'minimum must be a finite number')
        if 'uniqueItems' in node and type(node['uniqueItems']) is not bool:
            error(where, 'uniqueItems must be boolean')
        if 'enum' in node and (not isinstance(node['enum'], list) or not node['enum']):
            error(where, 'enum must be a non-empty array')
        if 'format' in node and node['format'] not in ('date', 'uri'):
            error(where, 'only date and uri formats are supported')
        if 'pattern' in node:
            try:
                if not isinstance(node['pattern'], str):
                    raise TypeError
                re.compile(node['pattern'])
            except (TypeError, re.error, OverflowError):
                error(where, 'pattern must be a valid regular expression')

    walk(schema, at)
    # Reject cycles even in unused definitions: the local evaluator has no recursion guard.
    if isinstance(definitions, dict):
        graph = {name: set() for name in definitions}
        for owner, target in references:
            if owner in graph:
                graph[owner].add(target)
        active, done = set(), set()

        def visit(name):
            if name in active:
                error(at, f'cyclic local reference involving {name}')
                return
            if name in done or name not in graph:
                return
            active.add(name)
            for target in sorted(graph[name]):
                visit(target)
            active.remove(name)
            done.add(name)

        for name in sorted(graph):
            visit(name)
    return problems


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key {key}')
        result[key] = value
    return result


def _constant(value):
    raise ValueError(f'non-finite JSON constant {value}')


def _float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError('non-finite JSON number')
    return number


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=_pairs,
                      parse_constant=_constant, parse_float=_float)


def validate(root: Path) -> list[str]:
    """Check all checkout JSON; no network, subprocesses or metadata execution.

    Schema checks precede data evaluation, including for schemas with no current data.
    Directory and JSON-file symlinks are rejected without reading their targets.
    """
    root = Path(root).resolve()
    problems, found, data = [], set(), {}

    def onerror(exc):
        problems.append(f'JSON inventory: cannot enumerate checkout ({exc.strerror})')

    for directory, dirs, files in os.walk(root, followlinks=False, onerror=onerror):
        parent = Path(directory)
        kept = []
        for name in sorted(dirs):
            if parent == root and name == '.git':
                continue
            child = parent / name
            if child.is_symlink():
                problems.append(f'{child.relative_to(root).as_posix()}: directory symlinks are not permitted in the JSON inventory')
            else:
                kept.append(name)
        dirs[:] = kept
        for name in sorted(files):
            path = parent / name
            if path.suffix.lower() != '.json':
                continue
            rel = path.relative_to(root).as_posix()
            found.add(rel)
            if path.is_symlink():
                problems.append(f'{rel}: JSON symlinks are not permitted')
                continue
            try:
                regular = stat.S_ISREG(path.stat(follow_symlinks=False).st_mode)
            except OSError:
                regular = False
            if not regular:
                problems.append(f'{rel}: JSON artifacts must be regular files')
                continue
            if path.suffix != '.json':
                problems.append(f'{rel}: JSON artifacts must use the lowercase .json extension')
                continue
            if registration(rel) is None:
                problems.append(f'{rel}: unregistered JSON artifact; add an explicit schema registration')
                continue
            try:
                data[rel] = read_json(path)
            except (OSError, ValueError, RecursionError) as exc:
                problems.append(f'{rel}: invalid or unreadable JSON ({exc})')
    for rel in sorted(SCHEMA_FILES | PLAN_SCHEMAS.keys()):
        if rel not in found:
            problems.append(f'{rel}: required registered artifact is missing')
    schemas = {}
    for rel in sorted(SCHEMA_FILES):
        if rel not in data:
            continue
        try:
            errors = schema_errors(data[rel], rel)
        except RecursionError:
            errors = [f'{rel}: schema nesting exceeds the local validation limit']
        problems += errors
        if not errors:
            schemas[rel] = data[rel]
    for rel, value in sorted(data.items()):
        key = registration(rel)
        if key == LOCAL_SCHEMA:
            continue
        schema = CONFIG_SCHEMAS.get(rel) if rel in CONFIG_SCHEMAS else schemas.get(key)
        if schema is None:
            problems.append(f'{rel}: registered schema is unavailable or invalid ({key})')
            continue
        try:
            problems += [f'{rel}: {e}' for e in schemalib.errors(value, schema)]
        except (RecursionError, ValueError, TypeError, KeyError, OverflowError) as exc:
            problems.append(f'{rel}: local schema evaluation failed ({type(exc).__name__})')
    return sorted(set(problems))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    errors = validate(args.root)
    print(json.dumps({'status': 'failed' if errors else 'passed', 'errors': errors}, indent=2))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
