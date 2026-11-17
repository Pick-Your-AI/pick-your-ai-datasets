# Proposed search and facets — DATA-11.02

Status: **unaccepted proposal; blocked** on DATA-01.02 taxonomy and DATA-11.01 architecture,
including its DATA-10.05 publication prerequisite. Issue #64 requires independent Website
maintainer review of the latest revision. No search engine, index or relevance test exists here.

Baseline: `Pick-Your-AI/pick-your-ai-datasets` at
`d4d831a5b8e8ad1ef718f3eaff9b6b89d7a2e8f8`,
[`schemas/dataset-record.schema.json`](../../schemas/dataset-record.schema.json),
[`docs/TAXONOMY.md`](../../docs/TAXONOMY.md),
[`planning/project-backlog.json`](../../planning/project-backlog.json) `project.fields`
(Dataset Modality, Dataset Category, Access Classification, License/Rights Status, Source
Freshness), and DATA-01.02/DATA-12.02. Current option lists are provisional, not accepted taxonomy.

## Candidate set and controlled facets

Each logical search result represents an exact eligible/published version with its parent ID.
Facets and snippets use only fields cleared for display by DATA-10.05. Unknown handling never
overrides publication gates. Count version results, label that unit, and use the same snapshot
for counts, pagination and results. No live source fetching, popularity or model-score ranking.

| Facet | Existing mapping / controlled values | Unknown and dependency |
| --- | --- | --- |
| Kind | `kind`: `dataset`, `benchmark` | Required; invalid/missing kind rejects ingestion, not an unknown entity type. |
| Modality | `modalities[]`: Text; Code; Image; Video; Speech & Audio; Multimodal; Time Series; Tabular; Geospatial; Robotics; Scientific; Graph & Structured | Values from Dataset Modality, excluding planning-only Cross-modal and Not Applicable. New/missing terms block public ingestion pending DATA-01.02 disposition; no guessing from title. A future approved unknown modality must have an explicit taxonomy term. |
| Category | `category`: Training Corpus; Fine-tuning & Instruction; Evaluation Benchmark; Retrieval & Embedding Corpus; Safety & Red-team; Synthetic; Domain/Specialized | Dataset Category excluding Cross-category/Not Applicable. Invalid/missing values block ingestion; a permitted unknown term needs DATA-01.02 approval. |
| Access | `rights.access_classification`: Open; Registration Required; Gated/Approval; Restricted/Sensitive; Commercial/Paid; Mixed; Not Assessed | Unknown bucket maps exactly to Not Assessed. Not Applicable is planning-only. Missing/invalid values are validation errors, not Open. Version scope depends on DATA-10.05. |
| Rights | `rights.rights_status`: Not Assessed; Under Review; Permitted for Metadata Use; Conditional; Restricted; Withdrawn/Disputed | Not Assessed maps to Unknown; Under Review stays distinct. Publication gates still exclude unapproved records. Never interpret metadata use as training permission. |
| Language | **Absent from record schema.** Proposed controlled language codes/unknown term from DATA-01.02 and DATA-03.01 | Do not infer language from title, UI locale or publisher location. Feature disabled until accepted codes, record mapping, evidence and multilingual semantics exist; then missing assessed data maps to explicit Unknown. |
| Freshness | **Absent from record schema.** Proposed projection using Source Freshness options: Not Collected; Current; Due for Refresh; Stale | Unknown maps to Not Collected. Not Applicable excluded. DATA-12.02 must supply source-class targets, as-of date, derivation and source scope before this facet activates; `sources[].accessed_on` alone cannot establish Current. |

“Unknown” is a proposed consumer label, not a new schema value or a synonym for `unknown` in
permission decisions. Every enabled facet uses a versioned mapping from canonical terms to
labels; new terms fail closed until reviewed. Missing, invalid, not applicable and not assessed
remain distinct in ingestion diagnostics. In the public filter UI, Unknown is explicitly
selectable wherever the accepted vocabulary permits it; zero matches must still be explainable.
Reject incomplete required taxonomy fields rather than laundering them into an unknown bucket.

Within a facet selected values are OR; between facets they are AND. A multimodal version may
match each of its declared components. Unknown is OR-selectable with a known value and never
matches a known-only filter. Clearing filters restores the eligible version set. Facet counts
apply the query and other facets, omitting that facet's own selections (disjunctive counts).
Deduplicate each version within a bucket; do not claim sums equal total for multi-valued facets.

## Relevance contract proposed for Website review

Search matching uses display-cleared IDs, original title, approved translated titles (when
available), publisher name and approved taxonomy labels only. No license/source document full
text, reviewer identity, dataset samples or withdrawn data enters the searchable corpus.
Display original text unchanged. Search-only normalization may case-fold and normalize Unicode;
keep stable ID punctuation significant. Diacritic folding, tokenization and transliteration
require locale-specific reviewed rules; no automatic cross-language expansion is assumed.

Apply this ordered match tier, then ascending canonical `record_id`, then `version_id` for ties:

1. Exact version ID; return that version first if eligible.
2. Exact record ID; return eligible versions of that identity before weaker matches.
3. Exact normalized full original or approved translated title.
4. All query tokens present in title (original or one approved translation).
5. All query tokens present across approved publisher/taxonomy labels.

Lower-tier matches cannot outrank a higher-tier match through repetition, record size, freshness,
rights class or publisher prominence. No hidden quality recommendation. Blank query lists the
filtered set in ID order. Unsupported expressions are literal input or get an accessible,
documented validation error; no arbitrary query execution. No-result text preserves query and
filters and offers explicit clear actions; it does not claim no such dataset exists globally.
Same snapshot, query, locale and filters must yield stable ordering across pagination.

## Offline acceptance scenarios (synthetic; not executed search tests)

| ID | Given / query | Required result |
| --- | --- | --- |
| S1 | Eligible `dataset.fixture-a@v1`, exact ID query, and another title containing that ID | Exact version ranks first. A withdrawn exact ID is absent; no stale snippet. |
| S2 | A title exactly “Orchid”; B title “Orchid Notes”; C publisher “Orchid”; query “orchid” | A before B before C, regardless of B's repeated title tokens or C's newer release. |
| S3 | A and B share an exact title and each has two versions | Stable parent-ID/version-ID order; page boundaries neither skip nor duplicate versions. No implicit newest-version preference. |
| S4 | Text-only A, Text+Image B, Image-only C; select Text OR Image plus category Training Corpus | Only versions matching the category and either modality; B counted once per matching bucket. |
| S5 | Synthetic enabled language projection: A known code, B explicit Unknown; select known then Unknown then both | A only, B only, then both; never infer B from its title. Until the projection is accepted, no language facet is shown as operational. |
| S6 | Source checked today but freshness target/derivation absent | Not labeled Current; freshness facet remains blocked, or Unknown after an accepted mapping permits it. |
| S7 | Display-cleared conditional metadata, prohibited training permission | Search may find the reviewed metadata; it never labels the record “training allowed”. |
| S8 | Candidate, withheld and eligible records share query tokens | Only eligible/published subset contributes result text and facet counts. |

Outstanding: accepted taxonomy/unknown mappings; language/freshness projections; rights-cleared
index fields; Website agreement on tiers, locale matching and snapshot pagination. Resolve these
and record Website review before calling DATA-11.02 accepted.
