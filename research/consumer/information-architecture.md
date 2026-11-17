# Proposed directory information architecture — DATA-11.01

Status: **unaccepted proposal; blocked**. Addresses issue #63 as an offline specification,
not implemented pages or an accepted Website contract. DATA-10.05 must supply the reviewed,
versioned publication artifact and Website acknowledgement. A Website maintainer other than
the author must review the latest revision. Rights and Editorial review of display constraints
remain prerequisite through DATA-10.05; this document grants no publication permission.

## Baseline and boundary

Repository sources read: `Pick-Your-AI/pick-your-ai-datasets` at
`d4d831a5b8e8ad1ef718f3eaff9b6b89d7a2e8f8`,
[`schemas/dataset-record.schema.json`](../../schemas/dataset-record.schema.json),
[`docs/INTEGRATIONS.md`](../../docs/INTEGRATIONS.md),
[`docs/PUBLICATION_POLICY.md`](../../docs/PUBLICATION_POLICY.md),
[`docs/MAINTENANCE.md`](../../docs/MAINTENANCE.md), and
[`planning/project-backlog.json`](../../planning/project-backlog.json) (DATA-10.05, DATA-11).
Mappings below describe existing schema paths, not an implemented consumer interface.

The ordinary directory receives only the eligible/published subset with reviewed display
constraints. It must not expose proposal files, reviews, proposer identities, internal notes,
dataset contents, samples, hidden tests or scores. All proposed routes below are logical page
types; Website owns URL design. Stable record and version IDs are link keys, never titles.

## Pages, fields and evidence

For every displayed claim provide a nearby source link or a labeled evidence expansion with
`sources[].publisher`, `role`, `url`, `accessed_on`, and the exact version scope. Do not imply
that a source's access date is a release date or that source existence verifies a claim.
Source lookup joins `source_id`; unresolved references block display of the affected claim.

| Proposed page | Visible fields from existing schema | Provenance and constraints |
| --- | --- | --- |
| Directory / browse / search | `title`, `record_id`, `kind`, `publisher.name`, `modalities`, `category`; explicitly selected `versions[].version_id` and `version_label`; access/rights labels | Publisher credit links through `publisher.source_id`; version claims through `versions[].source_ids`. Each result identifies its version. Rights labels retain scope and a link to permission evidence. No inferred recommended/latest version. |
| Dataset identity | `record_id`, original `title`, `kind=dataset`, `publisher`, `external_ids`, `modalities`, `category`; versions list; `relationships` | Identity source follows publisher; list each known version with its own evidence and release-date unknowns. Relationship label, target ID and `source_id` stay together. Unresolved targets show an ID and explanation, never a fabricated page. |
| Exact version | Parent identity plus one `version_id`, `version_label`, `released_on`, `formats`, `splits` (ID, name, size value/unit), `license.name`, `license.spdx`; rights/use conditions | `source_ids` support the version section; license links to `license.source_id`. Every permission cites its `source_id` and retains conditions and review status. `size.value=null` is “Unknown”, never zero; do not sum incompatible units. |
| Benchmark identity and version | Same identity/version fields with `kind=benchmark`; sourced `evaluates_with`/lineage links | Clearly call it a benchmark. Grading protocol, metric definition, harness, prompt and aggregation are **proposed dependencies** of DATA-07.01/DATA-08.03, absent from this schema; omit unsupported claims and state “Grading details not supplied”. No scores or rankings. |
| Withdrawal / supersession tombstone | Stable ID, minimal reviewed title/credit if permitted, state label, `withdrawal.announced_on`, permitted reason, authoritative notice; `superseded_by` target | Only a separately reviewed tombstone handoff may expose it. Cite `withdrawal.source_id` or relationship source; withhold unapproved reason text. Preserve old links and identity, but remove ordinary search inclusion and export actions. |

The current schema has record-level `publication_state`, `withdrawal` and `rights`, but version
arrays. It cannot express differing version rights/publication/withdrawal states or claim-level
citations for title, modality, category, formats and split counts. DATA-10.05 must provide an
approved version-scoped projection with claim-to-source mappings and field display constraints;
do not silently apply a record's permission to every version. Until available, these fields are
blocked from public display when their source/scope cannot be resolved. The schema's source
list is not itself proof that every field is covered by every source.

## Navigation and state rules

Proposed browse hierarchy: directory → controlled modality/category → identity → exact version.
Provide search as a second discovery route, breadcrumbs back to directory and identity, and
cross-links to cited publisher pages, version siblings and sourced relationships. A benchmark
is a separate kind, not a dataset's score tab. Paper/application links require the accepted
DATA-10.04 endpoints; an external ID alone does not establish such a relationship.

- An identity page lists versions rather than merging their licenses, sizes or splits. A
  version switch preserves the parent identity and names the destination version before use.
- A version missing a label or marked `unversioned=true` cannot enter public pages. Never
  resolve an old version link to a different version without a visible explanation.
- Withdrawal supersedes cached ordinary eligibility. Removal of normal cards, comparison and
  exports must accompany a reviewed tombstone update; an absent record is not proof of withdrawal.
- A `superseded_by` relationship does not mean withdrawal, endorsement or compatible scores.
  Keep the older identity visible as a reviewed tombstone per maintenance policy.
- Candidate/withheld records have no public preview route. A public missing-ID response must
  not reveal whether an internal candidate exists.

Tombstone payloads, withdrawal invalidation, snapshot revision, source-to-field mappings,
version state, and constraints are **proposed DATA-10.05 interface requirements**, not existing
fields. The normal eligible-subset rule is not an authorization to publish withdrawn records.

## Offline review scenarios

Use only synthetic paper sketches/metadata fixtures; no UI execution is claimed here.

| Scenario | Expected review result |
| --- | --- |
| One synthetic identity has v1 with 10 rows and v2 with unknown size and a different license | Two version pages; v2 shows “Unknown”; neither size nor license leaks across versions. Each displayed count/license has its own evidence. |
| A version has only general sources, no mapping for its split count | Reviewer marks count display blocked, even if all referenced URLs resolve. |
| A bookmarked v1 becomes withdrawn while v2 remains eligible | v1 resolves only to its reviewed tombstone, has no export/add-to-compare action, and is absent from ordinary results; v2 remains explicitly v2. Requires version-scoped handoff before release. |
| A benchmark's title matches a dataset's title | Kind and stable IDs distinguish cards/pages; no merge and no implied score comparison. |
| An unknown ID and a withheld internal ID are requested | Same public absence treatment; no private proposal or reviewer details. |
| A relationship target is absent | Display reviewed target ID/source with unavailable-destination text; do not invent a target or follow an arbitrary redirect. |

Acceptance remains open: resolve DATA-10.05, agree field constraints/tombstones with Rights and
Editorial, record independent Website review and actual receiving contract revision. These
scenarios are review material, not test results. See [search](search.md),
[comparison/export](comparison-export.md) and [accessibility/localization](accessibility-localization.md).
