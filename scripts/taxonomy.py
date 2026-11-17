"""Check the proposed term manifest against the canonical Project vocabulary.

This check does not read live Project fields, accept a vocabulary, or change any
record term. A term is identified by (Project field, option value), so the same
word in different fields retains its distinct meaning.
"""


def validate(taxonomy: dict, backlog: dict) -> list[str]:
    expected = {field['name']: set(field['options']) for field in backlog['project']['fields']}
    actual, errors = {}, []
    record_fields = {v['field'] for v in taxonomy['record_vocabularies']}
    if record_fields != {'task_families', 'domains'}:
        errors.append('taxonomy: record fields must be task_families and domains')
    for vocabulary in taxonomy['vocabularies'] + taxonomy['record_vocabularies']:
        name = vocabulary['field']
        if name in actual:
            errors.append(f'taxonomy: duplicate field {name}')
        terms = [term['value'] for term in vocabulary['terms']]
        if len(terms) != len(set(terms)):
            errors.append(f'taxonomy: duplicate term in {name}')
        actual[name] = set(terms)
        for term in vocabulary['terms']:
            for key in ('value', 'definition', 'scope_note'):
                value = term[key]
                if not value.strip() or value != value.strip():
                    errors.append(f'taxonomy: {name} {key} must be non-empty and trimmed')
    project_actual = {v['field'] for v in taxonomy['vocabularies']}
    missing, extra = set(expected) - project_actual, project_actual - set(expected)
    if missing or extra:
        errors.append(f'taxonomy: fields differ from Project: missing={sorted(missing)}, extra={sorted(extra)}')
    for name in sorted(set(expected) & set(actual)):
        missing, extra = expected[name] - actual[name], actual[name] - expected[name]
        if missing or extra:
            errors.append(f'taxonomy: {name} terms differ from Project: missing={sorted(missing)}, extra={sorted(extra)}')
    return errors


def record_errors(record: dict, manifest: dict) -> list[str]:
    """Validate optional, proposed record terms without filling unknown facts."""
    errors = []
    for vocabulary in manifest['record_vocabularies']:
        field = vocabulary['field']
        values = record.get(field, [])
        known = {term['value'] for term in vocabulary['terms']}
        for value in values:
            if value not in known:
                errors.append(f'unknown {field} term {value}')
        if 'unknown' in values and len(values) != 1:
            errors.append(f'{field}: unknown must appear alone')
    return errors
