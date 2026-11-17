# Metadata layout and JSON registration (proposed)

This is the structural draft for DATA-09.01 (#52). It preserves the existing record
schema and identity rules. DATA-04.01 (#23), the identifier and publisher model,
remains a prerequisite. This draft does not accept either work package, settle
schema evolution, or substitute for independent dataset research review.

## Record layout

| Location | Artifact and ownership |
| --- | --- |
| `catalog/proposals/<slug>.json` | One dataset or benchmark proposal, matching `schemas/dataset-record.schema.json`; existing candidate, evidence, rights and publication gates still apply. |
| `examples/<slug>.json` | Explicitly synthetic examples of the same record schema. |
| `schemas/` | The six explicitly registered schema files listed below; no automatic registration by extension. |
| `planning/` | The five explicitly registered planning artifacts listed below. |
| `evidence/`, `research/` | Markdown evidence pointers and research notes under the current validators; new JSON requires a reviewed schema and registry change. |
| `docs/` | Markdown documentation and the exact optional branding manifest below; other JSON requires registration. |
| `tests/` | Python regression tests; disposable synthetic JSON fixtures are created outside the checkout at test time. Committed JSON fixtures require explicit registration. |

Proposal and example files are direct children, not nested directories. Their
filename is a lowercase slug: `[a-z0-9][a-z0-9._-]*.json`. The filename is a locator;
record and version identities remain the fields validated by the current catalog
validator. This draft does not introduce a second identity convention ahead of #23.
All JSON artifacts use the lowercase `.json` extension; `.JSON` and `.Json` fail.

Dataset and benchmark records share the existing schema and distinguish their
kind in the record. Versions and splits remain inside their parent record, and
rights and permissions remain attached there with source references. This draft
does not create separate version, split or rights stores. A future separate store
needs its own schema, explicit path registration, semantic validation and review.
Benchmark runs and results remain external references under the charter.

## Explicit registry

`scripts/json_registry.py` is the registry. Registration is selected by the exact
repository-relative path or the two direct-child patterns above, never by a
schema declaration in untrusted metadata. Every discovered JSON path must resolve
to one of these registrations.

| JSON artifact | Schema or local contract |
| --- | --- |
| `planning/project-backlog.json` | `schemas/planning-backlog.schema.json` |
| `planning/coverage-matrix.json` | `schemas/planning-coverage.schema.json` |
| `planning/decision-register.json` | `schemas/planning-decisions.schema.json` |
| `planning/release-manifest.json` | `schemas/planning-release.schema.json` |
| `planning/issue-map.json` | `schemas/planning-issue-map.schema.json` |
| `catalog/proposals/<slug>.json`, `examples/<slug>.json` | `schemas/dataset-record.schema.json` |
| Each of the six schema files named above | Embedded `@local-schema-subset-v1` structural contract, enforced by `schema_errors`. |
| Optional `paseo.json` | Embedded `@config/paseo.json` schema: worktree setup/teardown command strings or arrays, and named scripts with command strings. |
| Optional `docs/images/.showcase.json` | Embedded `@config/docs/images/.showcase.json` schema: version 1 CT branding manifest with inputs, output metadata and SHA-256 fields. |

The optional configuration registrations anticipate the exact paths in pending
PRs #80 and #76. They are configuration, not dataset records. They have explicit
required fields and reject unknown properties; there is no configuration directory
exemption. Command strings are parsed only as data, never executed. Registration
does not authorize running Paseo lifecycle commands or generating branding assets.

The five planning files and six schema files are required. Every schema artifact
is checked even when there are no data records using it. The embedded schema
contract checks keyword names, value types, regular expressions, supported formats
and local reference resolution before data evaluation. Only the implemented
`schemalib` subset of the declared 2020-12 dialect is supported. Unsupported
keywords, boolean schemas, remote or dangling references, reference cycles, and
validation siblings that `schemalib` would ignore beside `$ref` or `anyOf` fail.
The dialect URL is an identifier, never a network fetch. This is a local subset
contract, not a claim of full JSON Schema 2020-12 conformance.

Acyclic local reference chains are resolved through their final constraint by the
evaluator. The registry rejects cycles across the complete definition graph before
evaluation, and the evaluator also stops a repeated direct reference or a missing
target. CLI regressions verify that a chained record constraint cannot be skipped.

The inventory covers hidden files and all checkout directories except root
`.git`, including its administrative worktree storage. Other cache-like directory
names provide no exemption: JSON committed under `.venv`, `node_modules` or
`__pycache__` must still be registered. Python bytecode and other non-JSON cache
files are skipped by extension without reading their contents. Keep disposable
JSON caches outside the checkout. This repository needs no installed dependencies.
Directory symlinks and JSON symlinks are rejected without following them, including
links within the checkout. JSON must be a regular file, without duplicate keys or
non-finite numbers. The validator makes no network requests and executes no
metadata, commands or dataset code.

## Validation and schema changes

Run `python3 scripts/json_registry.py` to inspect registration and structural
validation directly. Both existing planning and catalog commands run the registry
before loading schemas or records, so the current CI entry points enforce it.
Existing planning and catalog semantic checks still run after registration passes;
registration cannot establish evidence truth, permission, consent or publication
eligibility. The four README validation commands remain required.

For a new JSON artifact, propose its schema, its exact registry path (or narrowly
bounded pattern), ownership and semantic checks together. Add positive and negative
disposable fixtures, including malformed data at the newly registered path. Do not
add a blanket allowance for a directory. Schema or identity evolution is proposed
until the owning process and independent human review accept it.
