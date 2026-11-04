# Taxonomy

These are the initial controlled vocabularies used by Project fields and proposal records. They are the starting point for work package DATA-01.02, which refines and approves them; they are not yet accepted research results. The canonical option lists live in `planning/project-backlog.json` (`project.fields`), and validators reject values outside them.

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
