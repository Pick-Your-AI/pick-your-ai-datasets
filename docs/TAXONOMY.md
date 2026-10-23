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

| Kind | Identity |
| --- | --- |
| Dataset | `dataset.<slug>` |
| Dataset version | `dataset.<slug>@<label>`, using the publisher's version marker or an immutable host revision |
| Split | A split ID within exactly one version |
| Benchmark | `benchmark.<slug>`, with versions like datasets |
| Benchmark run / result | Owned outside this repository; referenced, never stored here |

## Relationships

`derived_from`, `subset_of`, `superseded_by`, `translated_from`, `mirrors`, `evaluates_with`. Each relationship cites a source. The lineage predicates must not form cycles. Work package DATA-04.03 extends this vocabulary.
