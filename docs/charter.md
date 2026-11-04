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

Version 0.1.0, proposed under `DATA-01.01`. Until a decision in
[`planning/decision-register.json`](../planning/decision-register.json) accepts this section, no
dataset record may be accepted.

These rules decide which entity kind a record is and whether it belongs in this repository. They do
not decide rights, quality or publication; those are separate gates in [SOURCE_RIGHTS.md](SOURCE_RIGHTS.md)
and [PUBLICATION_POLICY.md](PUBLICATION_POLICY.md). Entity kinds and identities are defined in
[TAXONOMY.md](TAXONOMY.md), and a record names exactly one kind.

Each kind carries an inclusion rule, an exclusion rule and at least two boundary examples. A boundary
example records the case, the ruling, and the public artifact that makes it a boundary case.

Per `RESEARCH_METHOD.md`, each source names its publisher, its role and the date it was read. The
arXiv identifiers below resolve at `https://arxiv.org/abs/<id>` and were all accessed on 2026-11-04;
the publisher is the paper's authors and the role is the primary paper. Worked cases that cite a
dataset card or repository name that source directly.

### Dataset

**Include** a collection of examples that a publisher names, describes and can be cited for, where
the collection is meaningful without reference to any single scoring protocol.

**Exclude** a collection that exists only as the instrument of a named benchmark's grading protocol,
a re-slice of another dataset, or an aggregation with no publisher identity of its own.

- **SQuAD** is a named, citable collection of reading-comprehension questions, and it is meaningful
  apart from how any system is scored on it. Ruling: included, `dataset.squad`.
  *SQuAD: 100,000+ Questions for Machine Comprehension of Text*, arXiv:1606.05250.
- **GLUE** is introduced as a benchmark and analysis tool that evaluates models "across a diverse set
  of existing NLU tasks", so its task material is reused rather than published by it, and its value
  is the graded comparison. Ruling: excluded as a dataset, recorded as `benchmark.glue` only.
  *GLUE: A Multi-Task Benchmark and Analysis Platform for Natural Language Understanding*,
  arXiv:1804.07461.

### Dataset version

**Include** a state of a dataset that the publisher labels, or an immutable hosting revision where
the publisher gives no label.

**Exclude** a re-host of identical content, which is a `mirrors` relationship on the existing
version, and a change carrying neither a publisher label nor a host revision.

- **SQuAD 2.0** is described by its authors as "the latest version of the Stanford Question Answering
  Dataset" and "combines existing SQuAD data with over 50,000 unanswerable questions". It changes the
  task, not only the contents. Ruling: a version, `dataset.squad@2.0`, recorded separately from
  `dataset.squad@1.1`, each with its own evidence.
  *Know What You Don't Know: Unanswerable Questions for SQuAD*, arXiv:1806.03822.
- The same release distributed from a second host under an identical revision marker is the same version.
  Ruling: not a new version; record the second host with `mirrors`. A differing host revision is a
  distinct version, because that revision is then the only identity the host offers.

  **GSM8K** is the worked case. The authors describe "a dataset of 8.5K high quality linguistically
  diverse grade school math word problems" (publisher: OpenAI; role: primary paper; arXiv:2110.14168;
  accessed 2026-11-04). The same material is distributed from the publisher's repository
  `https://github.com/openai/grade-school-math` (publisher: OpenAI; role: distribution host) and from
  the dataset `https://huggingface.co/datasets/openai/gsm8k` (publisher: Hugging Face; role: hosting
  distributor; accessed 2026-11-04), whose card reports a `main` configuration with 7,473 train and
  1,319 test rows. Ruling: one dataset, and the Hugging Face copy is `mirrors`, not a second version.
  Both row counts are carried as reported and are not reconciled against the paper's "8.5K"; a
  reconciliation is a claim this evidence does not support, so the difference stays visible rather
  than averaged away.

  That dataset card also reports a `socratic` configuration over the same two splits. Whether that is
  the same version with different annotations or a distinct derived artifact is **not settled by this
  evidence**, so it does not count as a version ruling and stays an open question under "Applying the
  rules" below rather than being resolved by assumption.

### Split

**Include** a named partition defined inside exactly one dataset version, such as a train,
validation or test partition that the publisher names.

**Exclude** a partition published as its own citable artifact, which is a dataset in its own right,
and any partition that spans more than one version.

- The named partitions of SQuAD 2.0 belong to `dataset.squad@2.0` and not to `dataset.squad@1.1`,
  even where the two versions share underlying examples. Ruling: split IDs are scoped to one version.
  arXiv:1806.03822.
- A held-out partition released later as a standalone, separately citable artifact is a dataset, not a
  split. Ruling: give it its own `dataset.<slug>` and record `subset_of` back to the parent, so the
  lineage stays visible without asserting the partition is still internal.

  **BIG-Bench Hard (BBH)** is the worked case. Its authors describe "a suite of 23 challenging
  BIG-Bench tasks which we call BIG-Bench Hard (BBH)", being the tasks "for which prior language model
  evaluations did not outperform the average human-rater" (publisher: the BBH authors; role: primary
  paper; arXiv:2210.09261, *Challenging BIG-Bench Tasks and Whether Chain-of-Thought Can Solve Them*;
  accessed 2026-11-04). Ruling: BBH is not 23 splits of `benchmark.big-bench`, because a task selection
  that others can cite, score and compare on its own has its own identity. It is recorded as its own
  benchmark with `subset_of` back to BIG-bench, and the parent's task list is not decomposed into child
  splits.

### Benchmark

**Include** a named evaluation instrument with a described task, a stated scoring or grading
protocol, and a citable description.

**Exclude** a bare collection of examples with no protocol, which is a dataset, and any set of
produced scores, which is a run or a result.

- **MMLU** is introduced as "a new test to measure a text model's multitask accuracy" covering 57
  tasks. The questions are meaningful through that test and its accuracy measure. Ruling:
  `benchmark.mmlu`; the question material is cited through the paper and is not entered as a separate
  dataset record.
  *Measuring Massive Multitask Language Understanding*, arXiv:2009.03300.
- **BIG-bench** "consists of 204 tasks, contributed by 450 authors across 132 institutions". Despite
  the many contributors it is one instrument with a shared purpose. Ruling: one benchmark,
  `benchmark.big-bench`; its contributing tasks do not each become datasets here.
  *Beyond the Imitation Game*, arXiv:2206.04615.

### Benchmark run

**Include** an evaluation of a specific system on a specific benchmark version that produces
measurements.

**Exclude** from this repository's storage: runs are owned outside it and are referenced, never
stored.

- **MLPerf Inference** "prescribes a set of rules and best practices to ensure comparability across
  systems", and its first call for submissions produced "more than 600 reproducible
  inference-performance measurements from 14 organizations". Each submitted measurement set is a run
  against those rules. Ruling: referenced through `evaluates_with`; the run is not stored here.
  *MLPerf Inference Benchmark*, arXiv:1911.02549.
- A paper reporting its own model's performance on **GSM8K**, introduced as "a dataset of 8.5K high
  quality linguistically diverse grade school math word problems", reports a run. GSM8K is both a
  dataset and the instrument of an evaluation, so the record carries `dataset.gsm8k` and the
  evaluation is described as a run against it. Ruling: the artifact is entered once, as the dataset.
  *Training Verifiers to Solve Math Word Problems*, arXiv:2110.14168.

### Benchmark result

**Include** a reported score or measurement attributed to a run, a benchmark version and a system.

**Exclude** from this repository's storage, for the same reason as runs: results are owned by the
benchmark or the reporting publication, and a local copy would become a second, drifting source.

- A per-system row in an MLPerf Inference results table is a result. Ruling: linked to the published
  table by reference, never transcribed into a record. arXiv:1911.02549.
- A single reported accuracy for one model on one benchmark version, in a paper, is a result.
  Ruling: referenced by source and access date so a reader can check it, without a local copy that can
  fall out of date. arXiv:2110.14168.

### Applying the rules

A record enters as `candidate` and must name exactly one kind. A disagreement about kind is resolved
before the record is admitted; a reviewer who believes a `benchmark` should be a `dataset`, or the
reverse, records the disagreement rather than admitting both.

Where these rules do not settle a case, the case goes to the decision register as an open question
and the record waits. An unsettled boundary is not an inclusion by default, and an unknown is never
treated as evidence of absence.

## Decisions

Decisions are recorded in [planning/decision-register.json](../planning/decision-register.json). A decision is accepted only when someone other than its proposer approves it.

Proposer, reviewer and approver roles per decision type, the independent-review rule and the escalation
path are defined in [GOVERNANCE.md](GOVERNANCE.md).
