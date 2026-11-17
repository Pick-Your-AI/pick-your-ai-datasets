# Dataset identity and version model

Proposed implementation for DATA-04.01 (#23) and DATA-04.02 (#24). This is an offline,
metadata-only contract with synthetic tests, not accepted research or a publication grant.
DATA-04.01 remains blocked by DATA-01.01 acceptance; DATA-04.02 remains blocked by
DATA-04.01 acceptance. Independent dataset research review and the repository's current
publication, rights and source-use reviews still apply. No datasets are downloaded.

## Stable internal identity

Keep existing `dataset.<token>` and `benchmark.<token>` IDs and their `<record_id>@<token>`
version IDs. Tokens are stable local allocations, independent of titles. Do not rename an
ID when a title changes or derive equivalence from a shared title, filename, size, DOI or
host identifier. Dataset, benchmark, version and split identities remain distinct. Existing
catalog validation rejects duplicate record and version IDs within each catalog collection.
Examples and proposals are separate validation collections; synthetic examples are not claims.

External identifiers retain their exact issued `value`, `issuer` and `kind`. `doi`, `host_id`,
`arxiv`, `url` and `other` are distinct kinds. A paper DOI or arXiv ID identifies a paper,
not a dataset version. Record that distinction in the issuer/kind and cite its context;
never use it as evidence of dataset equivalence. Optional `version_id` scopes an external
identifier to a version in this record; absent or null means record-level scope. Optional
`source_id` resolves locally, and a version-scoped citation must also be in that version's
`source_ids`. Duplicate kind/issuer/value tuples in the same scope are rejected. Cross-record
identifier matches are candidate signals for DATA-04.04 review, never an automatic merge.

`publisher` is the organization or group issuing the dataset. Optional `maintainers` name
those stated to maintain it; optional `hosts` name its distribution hosts. Each party cites
a recorded source. The same party may hold more than one role, but a host is never inferred
to be the publisher or maintainer. Missing optional lists mean unrecorded, not none.

## Version identity evidence

Optional `identity_evidence` is an object with `kind`, `marker` and `source_id`, or null.
A stated marker is copied exactly into `version_label`; the internal version token need
not reproduce it. Allowed kinds are `publisher_version` and `immutable_host_revision`.
The citation must belong to the version and resolve to a recorded source:

| Evidence kind | Source roles | Additional condition |
| --- | --- | --- |
| `publisher_version` | `publisher_page`, `dataset_card`, `paper` | The source must state the publisher's own marker; reviewer verifies attribution |
| `immutable_host_revision` | `host_page`, `dataset_card` | The same source is cited by a recorded host; reviewer verifies immutability |

The validator checks declared shape, exact marker equality and reference/role consistency.
It cannot verify the source's truth, issuer authority or the immutability of a revision.
A moving branch such as `main`, a filename or a timestamp inferred locally is not sufficient
identity evidence. Sources describing two releases do not establish their equivalence.

`unversioned: true` requires a null label under existing validation and forbids a non-null
identity evidence claim. It remains ambiguous and cannot be published. Explicitly null
`identity_evidence` records unknown evidence and also blocks eligibility/publication.
An absent field is `legacy_unclassified`: existing labels and `source_ids` remain usable
under existing gates, without being reclassified as publisher-marker evidence. A separate
reviewed migration/acceptance decision is needed before requiring classified evidence on all
legacy records. Passing validation is not completion of that migration or issue acceptance.

## Subsets, configurations and splits

Optional version-contained `subsets` have `subset_id`, `name`, `source_id`; `configs` have
`config_id`, `name`, `source_id` and optional nullable `subset_id`. They describe selections
and publisher configurations, respectively, and do not create standalone dataset records.
Separately citable artifacts use their own record and reviewed lineage under DATA-04.03.
Each child citation belongs to the containing version; each local ID is unique within its
kind and version. A subset or configuration in another version never resolves a local ref.

Existing split IDs remain local to the containing version. Their canonical addresses are
`<version_id>#split/<split_id>`; subsets and configs use `#subset/` and `#config/`.
Splits may cite `source_id` and nullable `subset_id` / `config_id`. References resolve in
one version, a split's subset must agree with its config's stated subset, and two splits
cannot share a name in the same effective subset/config scope. Repeated names across
configs need different split IDs. Containment assigns exactly one version; it never asserts
that similarly named partitions across releases contain identical examples.

## Formats and reported sizes

The schema lists controlled serialization/container formats, including JSON, JSONL, CSV,
TSV, Parquet, Arrow, common media formats, scientific formats and archives. Values use exact
lowercase schema tokens. `other` requires `format_notes` preserving the stated format;
`unknown` cannot be combined with stated formats. An empty legacy format list stays
unrecorded. Format equality never establishes version or content equality.

Split sizes carry a nonnegative `value` or null and an explicit controlled `unit`. Counts
(examples, records, rows, documents, tokens, images, frames, clips, utterances, speakers,
bytes, nodes, edges, pairs, trajectories, episodes) require integers. Duration units
(seconds, milliseconds, hours) and scaled storage units accept fractional values. Decimal
kilobytes/megabytes/gigabytes and binary kibibytes/mebibytes/gibibytes stay distinct; no
conversion or reconciliation is performed. `other` requires `unit_notes`; `unknown`
requires a null value. Null is unknown, never zero. Zero is only an explicitly reported value.
Size and format claims remain attributed metadata, not measured or verified contents.
