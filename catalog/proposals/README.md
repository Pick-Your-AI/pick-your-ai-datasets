# Catalog proposals

Real dataset and benchmark proposal records go here, one JSON file per record, matching [`schemas/dataset-record.schema.json`](../../schemas/dataset-record.schema.json) (draft 0.1.0). There are none yet.

Records must be real, sourced and non-synthetic. Synthetic examples belong in [`examples/`](../../examples/). Only JSON metadata and Markdown notes are allowed here. The validator rejects any other file type, so dataset contents cannot be committed.

Records must be direct children of this directory and use the lowercase `.json` extension. Nested JSON, `.JSON` files and JSON anywhere else under `catalog/`, `evidence/`, `research/` or `examples/` subdirectories are rejected rather than skipped, so no record can bypass validation or the publication gates. Markdown notes may be nested.
