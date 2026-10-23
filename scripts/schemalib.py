"""Minimal, network-free JSON Schema subset validator.

Supported keywords are listed in SUPPORTED. A schema using anything else fails
loudly instead of being silently ignored, so a schema can never look stricter
than the validator actually is. Remote references are never resolved.
"""
from __future__ import annotations

import datetime as dt
import re

SUPPORTED = {'$schema', '$id', 'title', 'description', 'type', 'properties', 'required',
             'additionalProperties', 'items', 'enum', 'const', 'pattern', 'minLength', 'maxLength',
             'minItems', 'uniqueItems', 'minimum', 'anyOf', 'format', '$defs', '$ref'}
TYPES = {'object': dict, 'array': list, 'string': str, 'boolean': bool, 'null': type(None)}


def unsupported_keywords(schema, at='schema'):
    problems = []
    if isinstance(schema, dict):
        for key, value in schema.items():
            if key not in SUPPORTED:
                problems.append(f'{at}: unsupported schema keyword {key}')
            if key in ('properties', '$defs'):
                for name, sub in value.items():
                    problems += unsupported_keywords(sub, f'{at}.{key}.{name}')
            elif key in ('items', 'additionalProperties') and isinstance(value, dict):
                problems += unsupported_keywords(value, f'{at}.{key}')
            elif key == 'anyOf':
                for n, sub in enumerate(value):
                    problems += unsupported_keywords(sub, f'{at}.anyOf[{n}]')
            elif key == '$ref' and not str(value).startswith('#/$defs/'):
                problems.append(f'{at}: only local #/$defs references are allowed')
    return problems


def _type_ok(value, expected):
    if expected == 'integer':
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == 'number':
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, TYPES[expected])


def errors(value, schema, at='$', root=None):
    root = root if root is not None else schema
    if '$ref' in schema:
        schema = root['$defs'][schema['$ref'].split('/')[-1]]
    out = []
    if 'anyOf' in schema:
        if not any(not errors(value, sub, at, root) for sub in schema['anyOf']):
            out.append(f'{at}: does not match any allowed shape')
        return out
    expected = schema.get('type')
    if expected is not None:
        options = expected if isinstance(expected, list) else [expected]
        if not any(_type_ok(value, t) for t in options):
            return [f'{at}: expected {"/".join(options)}']
    if 'const' in schema and value != schema['const']:
        out.append(f'{at}: must equal {schema["const"]!r}')
    if 'enum' in schema and value not in schema['enum']:
        out.append(f'{at}: {value!r} is not an allowed value')
    if isinstance(value, str):
        if len(value) < schema.get('minLength', 0):
            out.append(f'{at}: shorter than {schema["minLength"]}')
        if 'maxLength' in schema and len(value) > schema['maxLength']:
            out.append(f'{at}: longer than {schema["maxLength"]}')
        if 'pattern' in schema and not re.fullmatch(schema['pattern'], value):
            out.append(f'{at}: does not match {schema["pattern"]}')
        if schema.get('format') == 'date':
            try:
                dt.date.fromisoformat(value)
            except ValueError:
                out.append(f'{at}: not an ISO date')
        if schema.get('format') == 'uri' and not re.fullmatch(r'https://[^\s/@]+(/[^\s]*)?', value):
            out.append(f'{at}: not an https URL without credentials')
    if isinstance(value, (int, float)) and not isinstance(value, bool) and 'minimum' in schema and value < schema['minimum']:
        out.append(f'{at}: below minimum {schema["minimum"]}')
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            out.append(f'{at}: fewer than {schema["minItems"]} items')
        if schema.get('uniqueItems'):
            seen = [repr(sorted(v.items())) if isinstance(v, dict) else repr(v) for v in value]
            if len(seen) != len(set(seen)):
                out.append(f'{at}: items are not unique')
        if isinstance(schema.get('items'), dict):
            for n, item in enumerate(value):
                out += errors(item, schema['items'], f'{at}[{n}]', root)
    if isinstance(value, dict):
        props = schema.get('properties', {})
        for key in schema.get('required', []):
            if key not in value:
                out.append(f'{at}: missing required {key}')
        for key, item in value.items():
            if key in props:
                out += errors(item, props[key], f'{at}.{key}', root)
            elif schema.get('additionalProperties') is False:
                out.append(f'{at}: unexpected property {key}')
            elif isinstance(schema.get('additionalProperties'), dict):
                out += errors(item, schema['additionalProperties'], f'{at}.{key}', root)
    return out
