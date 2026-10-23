# Datasets contributor and agent instructions

Before changing files, read:
- `CONTRIBUTING.md`
- `docs/charter.md`
- `docs/RESEARCH_METHOD.md`
- `docs/SOURCE_RIGHTS.md`
- `docs/PUBLICATION_POLICY.md`
- the applicable issue

Follow the current [organization rules](https://github.com/Pick-Your-AI/.github/blob/main/CONTRIBUTING.md).

## Scope and authority

- This repository researches dataset and benchmark metadata. It does not authorize downloading, hosting or redistributing datasets. It does not authorize running benchmarks, paid compute, or contacting dataset authors.
- Preserve existing owners. T5 training-dataset research (research #32) and T6 evaluation research (research #36) keep their decision rules. The frozen T0–T6 builder contract changes only through its owning process.
- Inspect current issues, pull requests, native parents, blockers, assignees, Project fields and comments before any remote change. Preserve concurrent human triage. Never assign someone who has not agreed to the work.
- Stable `DATA-*` identifiers are independent of GitHub issue numbers. Read actual issue numbers back from GitHub.

## Evidence integrity

- Never invent dataset names, versions, licenses, sizes, splits, consent statements, checksums, benchmark scores or access grants.
- A dataset, each of its versions, its splits, a benchmark, a benchmark run and a benchmark result are distinct identities.
- Record unknowns explicitly. Missing evidence is not evidence of absence, and an unknown size is never zero.
- Public accessibility is not a license. A license is not consent, and a checksum is not a redistribution grant.
- Never commit dataset contents, samples, personal data, credentials or restricted material. Synthetic fixtures belong in `examples/` or `tests/` and must say so.

## Validation and delivery

Run the four commands in `README.md#validate` and report actual results.

Edit `planning/project-backlog.json`, then run `python3 scripts/render_docs.py`. Never hand-edit generated files.

Use a `contrib/` branch and a pull request. An agent or bot review is analysis, not the required approval from someone other than the author. Do not bypass review, rulesets or required checks.
