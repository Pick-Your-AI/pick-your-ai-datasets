# Contributing to pick-your-ai-datasets

The [organization contribution policy](https://github.com/Pick-Your-AI/.github/blob/main/CONTRIBUTING.md) sets access, branch, review and merge rules. This page adds this repository's workflow.

## Workflow

1. Pick or open an issue. Work packages are native issues with stable `DATA-NN.NN` IDs. Their tasks and subtasks are the checklist entries inside them.
2. Branch from `main` as `contrib/<your-login>/<topic>`, or work from a fork.
3. Make the change. If you change planning, edit `planning/project-backlog.json` and regenerate with `python3 scripts/render_docs.py`.
4. Run all checks in [README.md#validate](README.md#validate).
5. Open a pull request using the template. Use `Refs #N` for partial work, and use a closing keyword only when the work package's acceptance criteria are fully met.

## Reviews and merging

- Every pull request into `main` needs one approval from someone other than its author.
- An approval must come after the latest push. A push after an approval needs a new approval from someone other than the pusher.
- The `validate` check must pass.
- These rules are enforced by repository rulesets. Bot comments, self-review, passing tests and a mergeable status are not approvals.
- Rights, privacy and evaluation-methodology changes need the reviewer roles named in their work package.

## Proposing a dataset or benchmark record

Use the dataset proposal issue form or `templates/dataset-proposal.md`. Records go in `catalog/proposals/` as JSON matching `schemas/dataset-record.schema.json`.

Each record must:
- cite public sources with access dates;
- keep versions distinct;
- record rights per version and per use;
- start as `candidate`.

Publication needs independent rights, editorial and evidence reviews (see `docs/PUBLICATION_POLICY.md`).

## Corrections

Use the correction form. Cite the evidence that supports the correction. Corrections are reviewed and disclosed; history is never rewritten to hide them.
