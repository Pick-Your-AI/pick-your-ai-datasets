"""Offline identity checks for DATA-04.01/02; never infer entity equivalence.

Call after schema validation. Local child IDs are scoped by their containing version.
The functions do not rewrite issued identifiers, titles, source claims or nulls.
"""
from __future__ import annotations

COUNT_UNITS = frozenset(('examples', 'records', 'rows', 'documents', 'tokens', 'images',
                         'frames', 'clips', 'utterances', 'speakers', 'bytes', 'nodes',
                         'edges', 'pairs', 'trajectories', 'episodes'))
EVIDENCE_ROLES = {
    'publisher_version': frozenset(('publisher_page', 'dataset_card', 'paper')),
    'immutable_host_revision': frozenset(('host_page', 'dataset_card')),
}


def child_identity(version_id: str, kind: str, local_id: str) -> str:
    """A canonical address, not a minted external ID or a claim of equivalence."""
    if kind not in ('subset', 'config', 'split'):
        raise ValueError('child kind must be subset, config or split')
    return f'{version_id}#{kind}/{local_id}'


def identity_basis(version: dict) -> str:
    """Distinguish legacy/unclassified data from an explicit unknown."""
    if version['unversioned']:
        return 'unversioned'
    if 'identity_evidence' not in version:
        return 'legacy_unclassified'
    evidence = version['identity_evidence']
    return evidence['kind'] if evidence is not None else 'unknown'


def errors(record: dict, publication: bool = False) -> list[str]:
    """Validate source and containment semantics of a schema-valid record."""
    out = []
    sources = {s['source_id']: s for s in record['sources']}
    versions = {v['version_id'] for v in record['versions']}
    gated = publication or record['publication_state'] in ('eligible', 'published')

    def source(source_id, what, version=None):
        if source_id not in sources:
            out.append(f'{what} cites missing source metadata {source_id}')
        if version is not None and source_id not in version['source_ids']:
            out.append(f'{what} source must belong to the containing version')

    for role in ('maintainers', 'hosts'):
        seen = set()
        for party in record.get(role, []):
            source(party['source_id'], role)
            key = (party['name'], party['source_id'])
            if key in seen:
                out.append(f'duplicate {role} entry')
            seen.add(key)
    external = set()
    for identifier in record['external_ids']:
        version_id = identifier.get('version_id')
        key = (identifier['kind'], identifier['issuer'], identifier['value'], version_id)
        if key in external:
            out.append('duplicate external identifier in the same scope')
        external.add(key)
        if version_id is not None and version_id not in versions:
            out.append('external identifier targets unknown version')
        if 'source_id' in identifier:
            version = next((v for v in record['versions'] if v['version_id'] == version_id), None)
            source(identifier['source_id'], 'external identifier', version)

    for version in record['versions']:
        vid = version['version_id']
        evidence = version.get('identity_evidence')
        if evidence is not None:
            source(evidence['source_id'], f'{vid} identity evidence', version)
            if version['unversioned'] or evidence['marker'] != version['version_label']:
                out.append(f'{vid}: identity marker must equal the exact version label of a versioned reference')
            cited = sources.get(evidence['source_id'], {})
            if cited.get('role') not in EVIDENCE_ROLES[evidence['kind']]:
                out.append(f'{vid}: identity evidence has an incompatible source role')
            if evidence['kind'] == 'immutable_host_revision' and not any(
                    h['source_id'] == evidence['source_id'] for h in record.get('hosts', [])):
                out.append(f'{vid}: immutable revision must cite a recorded host')
        if gated and identity_basis(version) == 'unknown':
            out.append(f'{vid}: explicitly unknown identity evidence cannot be published')
        if 'unknown' in version['formats'] and len(version['formats']) != 1:
            out.append(f'{vid}: unknown format cannot be mixed with stated formats')
        if 'other' in version['formats'] and not version.get('format_notes', '').strip():
            out.append(f'{vid}: other format requires format_notes with the stated format')

        children = {}
        for kind, field in (('subset', 'subsets'), ('config', 'configs')):
            children[kind] = {}
            for child in version.get(field, []):
                local = child[f'{kind}_id']
                if local in children[kind]:
                    out.append(f'{vid}: duplicate {kind} ID {local}')
                children[kind][local] = child
                source(child['source_id'], child_identity(vid, kind, local), version)
        for config in children['config'].values():
            subset = config.get('subset_id')
            if subset is not None and subset not in children['subset']:
                out.append(f'{vid}: config targets unknown subset in this version')
        split_scopes = set()
        for split in version['splits']:
            subset, config = split.get('subset_id'), split.get('config_id')
            for kind, local in (('subset', subset), ('config', config)):
                if local is not None and local not in children[kind]:
                    out.append(f'{vid}: split targets unknown {kind} in this version')
            selected = children['config'].get(config, {})
            config_subset = selected.get('subset_id')
            if subset is not None and config_subset is not None and subset != config_subset:
                out.append(f'{vid}: split subset conflicts with its config subset')
            key = (subset if subset is not None else config_subset, config, split['name'])
            if key in split_scopes:
                out.append(f'{vid}: split name is ambiguous in one subset/config scope')
            split_scopes.add(key)
            if 'source_id' in split:
                source(split['source_id'], child_identity(vid, 'split', split['split_id']), version)
            size = split['size']
            if size['unit'] == 'other' and not size.get('unit_notes', '').strip():
                out.append(f'{vid}: other size unit requires unit_notes with the stated unit')
            if size['unit'] == 'unknown' and size['value'] is not None:
                out.append(f'{vid}: unknown size unit requires a null value')
            if size['unit'] in COUNT_UNITS and size['value'] is not None and not isinstance(size['value'], int):
                out.append(f'{vid}: count size units require an integer value')
    return out
