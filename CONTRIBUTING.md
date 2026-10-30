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

## Routing decisions

For an unresolved decision, first read the existing issue, its assignees, relevant
decision record and related pull requests. Preserve accepted ownership and local
review, evidence, security and release requirements. Routing identifies a contact;
it does not grant access, appoint an owner, authorize publication or waive a gate.

Use the canonical [escalation guide](https://github.com/Pick-Your-AI/.github/blob/main/docs/governance/ESCALATION.md) and
[versioned routing policy](https://github.com/Pick-Your-AI/.github/blob/main/governance/escalation-policy.json). These links depend on the organization
governance change merging; until then, use its reviewed checkout and describe the
route as provisional. Do not claim the central tooling is installed or active.

The order is repository team → repository maintainer → repository lead maintainer
→ applicable parent teams → CompleteDotTech. Record a disposition at each level,
including unresolved, vacant, pending-acceptance or inaccessible roles; membership,
team-management status and repository permissions do not establish accepted
operational ownership. Keep owner placeholders for the final fallback. Do not
silently skip an unresolved role or treat a proposed mapping as accepted.

An operator with read access must refresh the private snapshot before resolving:

```sh
python /path/to/org-checkout/governance/router.py refresh --policy /path/to/org-checkout/governance/escalation-policy.json --snapshot /private/path/routing-snapshot.json --status /private/path/routing-status.json
python /path/to/org-checkout/governance/router.py resolve --policy /path/to/org-checkout/governance/escalation-policy.json --snapshot /private/path/routing-snapshot.json --repo Pick-Your-AI/pick-your-ai-datasets --max-age-seconds 86400 --status /private/path/routing-status.json
```

Here `86400` is an **operator-selected example**, not an approved default. Select
an appropriate explicit maximum age; a proposed policy value does not supply one.
Check that refresh succeeded. If refresh fails, stop recipient selection and
report the failure; the last successful snapshot is retained for diagnosis, not
as a current route. Report stale or incomplete coverage explicitly. Keep snapshots,
raw API responses, rosters and private
identities outside public Git and public issues. Share only the necessary public
team destination and a sanitized decision summary.

When escalation is needed, include the decision needed, current responsible role,
prior disposition and proposed next recipient. Reuse information already in the
issue or PR; routine contributions need no full escalation history. Send nothing
and change no assignment automatically. Sensitive reports follow the existing
private security/support process.

The owner-selected scope of [organization issue #14](https://github.com/Pick-Your-AI/.github/issues/14)
is all changes in Research, Sustainability, Applications, Papers, Catalog Pipeline
and Datasets. This records scope only: current independent-review and branch/check
requirements remain in force. Any proposed enforcement change requires separate
approval; no review exception or CODEOWNERS change is established here.
