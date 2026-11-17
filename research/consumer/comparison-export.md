# Proposed comparisons, citations and export — DATA-11.03

Status: **unaccepted proposal; blocked** on DATA-08.03 scoring comparability and DATA-05.04
use-permission matrix. Issue #65 requires independent Rights and Editorial review of the
latest revision. Website review of the receiving interface remains a DATA-10.05 prerequisite.
No reviewed per-field export matrix, generated ranking or production export is supplied here.

Repository sources read at `Pick-Your-AI/pick-your-ai-datasets` commit
`d4d831a5b8e8ad1ef718f3eaff9b6b89d7a2e8f8`:
[`schemas/dataset-record.schema.json`](../../schemas/dataset-record.schema.json),
[`docs/SOURCE_RIGHTS.md`](../../docs/SOURCE_RIGHTS.md),
[`docs/RESEARCH_METHOD.md`](../../docs/RESEARCH_METHOD.md),
[`docs/PUBLICATION_POLICY.md`](../../docs/PUBLICATION_POLICY.md), and
[`planning/project-backlog.json`](../../planning/project-backlog.json) DATA-05.04/DATA-08.03.
Those policies require version/use-scoped evidence; the record schema presently has only
record-level `rights.permissions[]`. This proposal cannot substitute for the missing matrix.

## Comparison preconditions and labels

Require explicit exact version selection, one accepted publication snapshot, permitted display
for every cell, resolved source references and version-specific rights. A version missing any
precondition cannot enter a public comparison. Withdrawal invalidates existing selections and
exports. Identity similarity, matching titles and shared license names are not equivalence.

| Field family | Permitted descriptive comparison after display review | Limits |
| --- | --- | --- |
| Identity/version | `record_id`, `kind`, `title`, `publisher`, selected version ID/label, released date | Display original titles, publisher credit and date unknowns; never compare different versions as one identity. |
| Scope | `modalities`, `category`, formats, split names | Controlled labels and evidence; format does not establish compatibility. Language requires a proposed accepted projection. |
| Split sizes | `splits[].size.value/unit` | Align only matched split meaning, count unit and counting scope with evidence. Show unknown/incompatible beside values; no totals, ratio or “larger” badge when these differ. |
| License/access/use | Version license and accepted version-scoped rights projection | Show separate use decisions, conditions, source and review date if supplied; no combined “open” score. Missing review is “Unknown / not approved for this use”. |
| Benchmark grading | DATA-07.01/DATA-08.03 accepted external grading reference, when supplied | Absent from this schema; no locally transcribed scores or fabricated protocol. |

Descriptive side-by-side metadata is not a scoring claim. For any future externally owned score
comparison, DATA-08.03 must explicitly establish matching benchmark identity/version, split,
metric definition (including direction/unit), prompt/setup, harness/revision and aggregation.
An unknown dimension is not a match. Show “Not comparable — [mismatched or unknown dimensions]”
and source links; suppress score differences, best/worst highlighting, combined plots, sorting
by score and rankings. Even matching dimensions do not authorize rankings in this package.
Results/runs remain referenced at their owner, never stored as dataset-record fields.

## Publisher-credit citation format

Proposed plain-text metadata citation, subject to field display/copy review:

`{publisher.name}. {original title}. Version {version_label} [{version_id}]. {publisher source URL}.
Source: {source publisher}, {source role}; accessed {source accessed_on}. Directory metadata:
{record_id}, snapshot {accepted snapshot revision}; cited {user citation date}.`

For version-specific facts use the relevant version source, not whichever source appears first.
If identity and version sources differ, include both labeled source references. An original
publisher citation supplied and cleared by the rights process takes precedence; keep the
directory metadata attribution separate so the directory is never represented as dataset
publisher. Retain original-language title; a reviewed translation may follow in brackets labeled
with its language. No invented authors, year, DOI, date of release or upstream recommended
citation. Unknown release date is explicitly unknown, not the source access date. The schema
does not contain upstream citation text, title languages or snapshot revision: these are proposed
dependencies, not fields inferred from `external_ids` or the current date.

## Per-field export policy: deny unless reviewed

Metadata display permission is not redistribution permission. DATA-05.04 must deliver the
reviewed, per-version rights matrix with source clause/statement references. DATA-10.05 must
bind that matrix to the exact snapshot. Export remains disabled until a Rights reviewer has
accepted a field/path allowlist and an Editorial reviewer has accepted attribution/wording.

Proposed matrix row key: `(snapshot revision, record_id, version_id, exact field path, output
format, redistribution use)`. Each row must name decision, source/clause locator, conditions,
attribution requirements and review evidence/revision. These are proposed interface attributes;
they are not existing schema fields or a claim of accepted rights. Do not use broad wildcard
grants or a record-wide `redistribution=allowed` alone to authorize every child field.

| Exact field/path family requiring its own reviewed matrix rows | Default export decision | Additional gate |
| --- | --- | --- |
| `record_id`, `kind`, selected version ID/label, `external_ids[].kind/value/issuer` | Deny | Rights review must distinguish directory-authored IDs from third-party identifiers. |
| `title`, `publisher.name`, `modalities[]`, `category`, version dates/formats | Deny | Approved wording, translation status and publisher attribution travel with each permitted field. |
| `versions[].splits[].split_id/name/size.value/size.unit` | Deny | Per-field scope, unit and evidence; no content or samples. Unknown remains null, never zero. |
| `versions[].license.name/spdx/source_id`; rights labels, decisions and conditions | Deny | Source-clause reference and conditions preserved. Permission to export metadata does not grant dataset redistribution. |
| `relationships[].predicate/object/source_id`; cited `sources[].url/publisher/role/accessed_on` | Deny | Review both relation wording and linked attribution; source pointers also need an explicit export disposition. |
| Proposed translated titles, grading references, freshness or other extensions | Deny | New field cannot inherit an earlier path grant; repeat Rights/Editorial review. |
| `proposed_by`, `reviews[]`, synthetic/debug/internal fields, unreviewed withdrawal text | Deny; excluded from proposed public export | No internal identity/review data in public payload. Tombstone fields need a separate reviewed policy. |

Evaluation order: reject ineligible/withdrawn versions → locate exact reviewed row → reject
unknown/prohibited/unreviewed/missing row → for conditional rows verify every condition for this
format and use → include only approved value and required provenance/credit. “Allowed” without
source/review evidence fails. A conflict or stale revision fails closed. Never drop attribution
to make an export fit: if mandatory credit/source fields are denied or unavailable, block that
field's export (or the whole requested citation when inseparable) and explain the omission.

Proposed JSON/CSV exports must name snapshot, exact version IDs, export time and the applied
matrix revision in a reviewed manifest. CSV omits denied columns/cells with an explicit omission
manifest; JSON omits denied keys. Distinguish denied/omitted from permitted-but-unknown null.
Plain-text copy/citation is also export and follows the same gates. No download URL, embedded
HTML, dataset file, sample, answer key or signed URL can be exported through this specification.

## Offline review scenarios

| Scenario (synthetic metadata only) | Required disposition |
| --- | --- |
| Two benchmark references differ only in prompt or harness revision | Not comparable; identify the differing dimension; no difference, score sort or winner. |
| Versions have identical benchmark names but unknown split/aggregation | Not comparable; unknown is not equality. |
| Split A has 100 rows; split B has unknown examples or a different scope | Show attributed values/unknowns; no size ranking or computed ratio. |
| Reviewed metadata_display allowed, redistribution unknown | Display may proceed under its constraints; all export/copy/citation remains denied. |
| Synthetic matrix permits ID but title has no row | Export only ID if its required credit/provenance can also be exported; omission names title denial, no title fallback. |
| Conditional title export requires publisher credit, but credit row denied | Title and complete citation export blocked; cannot strip credit. |
| v1 has allowed matrix rows; v2 has no reviewed rows | v2 denied; neither a common parent nor v1 permission fills the gap. |
| A selected version withdraws or matrix snapshot changes before export | Invalidate selection/authorization and re-evaluate; cached permission cannot authorize the export. |

No external dataset rights have been assessed. Acceptance remains open until the actual
DATA-05.04 matrix and DATA-08.03 rule revision are cited, these scenarios are reviewed with
Rights/Editorial, and the receiving Website contract and human reviews are recorded.
