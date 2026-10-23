# Integrations

Every integration is an explicit, versioned handoff with a named artifact, format, owner and review. Each is listed in [DEPENDENCIES.md](DEPENDENCIES.md#cross-repository-handoffs). Nothing here changes another repository; the receiving owners acknowledge each handoff on their own issues.

| Partner | Existing owner | Exchange | Package |
| --- | --- | --- | --- |
| Research T5 training dataset | [research #32](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/32) | Dataset identity, version and use-permission fields, cross-walked to contract v1 `training_dataset` without modifying it | DATA-10.01 |
| Research T6 evaluation | [research #36](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/36) | Benchmark grading semantics and contamination evidence, cross-walked to contract v1 `evaluation_suite` | DATA-10.01 |
| Research T1 models | [research #5–#7](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/6) | `evaluated_on` links by benchmark version | DATA-10.02 |
| Research T3 retrieval | [research #13–#16](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/14) | Retrieval and embedding benchmark identities | DATA-10.02 |
| Catalog pipeline | [catalog-pipeline](https://github.com/Pick-Your-AI/pick-your-ai-catalog-pipeline) | Accepted, rights-reviewed dataset records for normalization | DATA-10.03 |
| Papers | [papers](https://github.com/Pick-Your-AI/pick-your-ai-papers) | Dataset-introducing paper revisions; `uses_dataset` and `evaluated_on` endpoints | DATA-10.04 |
| Applications | [applications](https://github.com/Pick-Your-AI/pick-your-ai-applications) | Application-to-dataset links | DATA-10.04 |
| Website | [website](https://github.com/Pick-Your-AI/pick-your-ai-website) | Eligible-subset directory artifact with display constraints | DATA-10.05 |

## Rules

- Hand off only `eligible` or `published` records.
- Identifiers follow each partner's identity rules. A link never implies endorsement, compatibility or performance.
- The frozen T0–T6 contract is read, never written. Proposed contract changes go through the research contract process (research #40).
- Upstream findings are cited by repository, path and commit, never restated as new research.
