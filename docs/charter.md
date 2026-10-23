# Charter

## Purpose

Research AI datasets and benchmarks well enough that Pick Your AI can show people the following, each with evidence:
- what a dataset or benchmark is;
- which exact version they are looking at;
- what they may do with it;
- where it came from;
- whether results reported on it can be compared.

## Origin and ownership

[Research #509](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/509) routing row G11 proposes a standalone `pick-your-ai-datasets` repository for a broad, versioned, rights-aware dataset and benchmark corpus. Existing owners keep their scope:

| Owner | Keeps |
| --- | --- |
| `pick-your-ai-research` T5 training dataset ([#32](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/32)) | Training-dataset decision rules for the stack builder |
| `pick-your-ai-research` T6 evaluation ([#36](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/36)) | Evaluation-suite decision rules for the stack builder |
| `pick-your-ai-research` contracts v1 | The frozen T0–T6 builder contract |
| `pick-your-ai-papers` | Scholarly identities of papers that introduce or use datasets |
| `pick-your-ai-catalog-pipeline` | Normalization and release of accepted records |
| `pick-your-ai-website` | Public pages and consumer implementation |

This repository owns the cross-project dataset and benchmark directory research described in the [delivery plan](DELIVERY_PLAN.md).

## In scope

- Identity and versions of datasets, subsets, splits and benchmarks
- Licensing, access, consent, privacy and use permissions
- Provenance, annotation, quality, bias, contamination and reproducibility evidence
- Benchmark grading semantics and evaluation-integrity rules
- Coverage measured against declared denominators
- Handoffs to research, catalog pipeline, papers, applications and website

## Out of scope

- Hosting, mirroring or redistributing dataset contents or samples
- Running benchmarks, reporting model scores or producing leaderboards
- Legal advice or certifying anyone's compliance
- Changing the frozen T0–T6 contract outside its owning process
- Production deployment

## Inclusion and exclusion

Work package DATA-01.01 defines and approves the inclusion and exclusion rules, with boundary examples. Until then, no dataset record may be accepted.

## Decisions

Decisions are recorded in [planning/decision-register.json](../planning/decision-register.json). A decision is accepted only when someone other than its proposer approves it.
