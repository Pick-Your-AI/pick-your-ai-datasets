# Taxonomy

These are the initial controlled vocabularies used by Project fields and proposal records. They are the starting point for work package DATA-01.02, which refines and approves them; they are not yet accepted research results. The canonical option lists live in `planning/project-backlog.json` (`project.fields`), and validators reject values outside them.

## Proposed term definitions and registration

[`planning/taxonomy.json`](../planning/taxonomy.json) gives each of the 96 current
options across 15 Project fields a definition and a scope note. The identity of a
term is its `(field, value)` pair: `Blocked` in Status, Readiness and Dependency
Status has a different context in each field. Repeated words are not merged into
one cross-field concept.

[`schemas/taxonomy.schema.json`](../schemas/taxonomy.schema.json) validates the
manifest. The planning validator also requires exactly one entry per canonical
Project field and option, rejects missing, extra or duplicate mappings, and
rejects blank or padded definitions and scope notes. Record modality/category
validation continues to use the canonical Project options. No live Project value
is read or changed by these offline checks.

This is a **proposed vocabulary**, not an acceptance decision. The definitions
describe current repository terms; they do not introduce deadlines, freshness
thresholds, access grants, dataset facts or appointments. The schema deliberately
requires `status: proposed`; acceptance requires a later reviewed change with its
decision evidence. DEC-006 and DEC-007 remain unchanged.

The same manifest defines proposed `task_families` and `domains` in a separate
record namespace. These optional record arrays must be nonempty when present,
contain unique registered terms, and use `unknown` alone when unassessed. Omission
also means unassessed; it is not converted to `general`. The catalog entrypoint
checks the vocabulary itself as well as each record term. No legacy record is
silently assigned a task or domain. The definitions are original local proposals,
not imported taxonomies or accepted source facts.

DATA-01.02 still needs accepted scope, independent review, acceptance of these
conventions and external mappings, and the papers receiving-owner acknowledgement.
Language/region code-list adoption needs a permitted source and rights review as
described below. No decision or cross-repository handoff is marked complete.

## Proposed language and region conventions

Use a sourced ISO 639 language identifier, preserving its explicitly named set
and registry revision; do not infer language from a publisher's country. Prefer
the shortest applicable identifier only after a reviewed mapping establishes
equivalence. Preserve multiple evidenced languages individually. Unknown is a
separate null state, not an invented identifier, an empty-language claim or a
default to English. Writing system, locale and translation status are separate
claims; a display translation cannot change the source language.

Use sourced ISO 3166 identifiers with the declared part and registry revision for
geographic coverage. The proposed country representation is alpha-2. Preserve
historical identifiers as dated claims; do not silently rewrite historical scope
to current boundaries. Geographic coverage, publisher location, subject identity
and legal access restrictions are different fields. Unknown geography does not
mean worldwide availability, and a code is not a jurisdictional rights ruling.

Reference pages: [ISO 639](https://www.iso.org/iso-639-language-code) and
[ISO 3166](https://www.iso.org/iso-3166-country-codes.html), publisher ISO, role
standards reference, accessed 2026-11-17. Source-use status: the inspected site
contains an AI-use restriction; no code list or substantive ISO text is imported.
A rights reviewer must identify a permitted registry source before code-list
adoption. These proposed conventions do not assert validation of real codes.
The record schema does not yet accept language/region fields; regex shape alone
would not establish that a code exists, is current or has the claimed meaning.

## External task comparisons (reference only, proposed)

The comparisons below are small original summaries, not copied taxonomies.
Similar names are candidate correspondences; they do not establish equivalence
of task definition, data identity, rights or grading protocol.

| Primary source and observed distinction | Proposed local mapping and rationale |
| --- | --- |
| Hugging Face's task index distinguishes text, image and tabular classification entries. | Reference those entries as narrower candidates for `classification`; keep local modality separate so a modality change does not create a new task family. |
| Hugging Face lists question answering and summarization as separate tasks. | Retain separate `question-answering` and `summarization` families; do not merge them because both can generate text. |
| OpenML describes task types including classification and clustering, with task instances binding data and evaluation context. | Reference `classification` and `clustering` as family candidates, but keep a local benchmark version and its grading contract distinct from a family label. |

Sources read 2026-11-17: [Hugging Face task index](https://huggingface.co/tasks)
(publisher Hugging Face, role primary task directory),
[OpenML task concepts](https://docs.openml.org/concepts/tasks/) and
[OpenML task reference](https://docs.openml.org/reference/tasks/)
(publisher OpenML, role primary task documentation).

Terms references read on the same date:
[Hugging Face terms](https://huggingface.co/terms-of-service) and
[OpenML terms](https://docs.openml.org/intro/terms/). Status for both: terms
inspected, bulk taxonomy reuse permission **not established**; no content license
or collection grant is inferred. Only links and this original bounded comparison
are proposed. External mappings remain reference-only until independent research
and rights review records a disposition. No models, datasets, samples or benchmark
results were downloaded or executed.

## Modality

Text · Code · Image · Video · Speech & Audio · Multimodal · Time Series · Tabular · Geospatial · Robotics · Scientific · Graph & Structured.

`Cross-modal` marks planning work spanning modalities. `Not Applicable` marks process work. A record lists every modality it contains; a multimodal record also lists its component modalities.

## Category

Training Corpus · Fine-tuning & Instruction · Evaluation Benchmark · Retrieval & Embedding Corpus · Safety & Red-team · Synthetic · Domain/Specialized.

## Access classification

Open · Registration Required · Gated/Approval · Restricted/Sensitive · Commercial/Paid · Mixed · Not Assessed.

## License and rights status

Not Assessed · Under Review · Permitted for Metadata Use · Conditional · Restricted · Withdrawn/Disputed.

**Permitted for Metadata Use** means only that describing the dataset is permitted. It says nothing about training or redistribution, which are recorded separately as per-use permissions.

## Entity kinds

A record names exactly one kind. Which kind a boundary case belongs to is decided by the inclusion
and exclusion rules in [charter.md](charter.md#inclusion-and-exclusion).

| Kind | Identity | Stored here |
| --- | --- | --- |
| Dataset | `dataset.<slug>` | Yes |
| Dataset version | `dataset.<slug>@<label>`, using the publisher's version marker or an immutable host revision | Yes |
| Split | A split ID within exactly one version | Yes |
| Benchmark | `benchmark.<slug>`, with versions like datasets | Yes |
| Benchmark run | Owned outside this repository; referenced by the benchmark version and the evaluated system, never stored here | No |
| Benchmark result | Owned by the benchmark or the reporting publication; referenced by source and access date, never stored here | No |

A run and a result are separate kinds. A run is the act of evaluating one system on one benchmark
version; a result is a reported measurement attributed to that run. Because both are owned outside
this repository, a record that appears to store either one is a kind error, not a record.

## Relationships

`derived_from`, `subset_of`, `superseded_by`, `translated_from`, `mirrors`, `evaluates_with`. Each relationship cites a source. The lineage predicates must not form cycles. Work package DATA-04.03 extends this vocabulary.
