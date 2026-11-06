# Governance, roles and decision process

Version 0.1.0, proposed under `DATA-01.04`. Until a decision in
[`planning/decision-register.json`](../planning/decision-register.json) accepts this page, it
records a proposal and not established authority.

This page answers three questions: who may do what here, who proposes, reviews and accepts each
kind of decision, and how a decision is recorded so that it can be checked later. It implements
the [organization contribution policy](https://github.com/Pick-Your-AI/.github/blob/main/CONTRIBUTING.md)
at revision `ce32a4f1f7586886da81b421baefeb15974868bb` (2026-10-30) and does not extend it.

## Access roles

Access roles come from the organization policy. They grant permission to act on files and
pull requests; they do not appoint anyone to decide research questions.

| Access role | Who | Here |
| --- | --- | --- |
| Contributor | Anyone with a GitHub account | Open issues and pull requests from a fork. Propose a record with the proposal form. |
| Early contributor | Members of the organization `early-contributors` team | Push branches under `contrib/`, open issues and pull requests, and review pull requests. Cannot push to `main` or merge. |
| Maintainer | The repository maintainer team | Push any branch and merge approved pull requests. |
| Organization admin | Organization owners | Everything above, including bypassing the review requirement. Reserved for emergencies, and the bypass must be explained in the pull request. |

A team name is not a permission. GitHub team and repository grants remain authoritative, and the
`Research Maintainers` and `Lead Maintainers - Datasets & Benchmarks` teams are the current
organization teams for this area. Membership, team-management status and repository access do not
by themselves establish accepted operational ownership of a work package.

## Decision roles

Decision roles are separate from access roles. Someone may hold merge permission and still not be
the right approver for a decision; conversely, a contributor may propose a decision they cannot
merge.

| Decision role | Filled by |
| --- | --- |
| Proposer | The person, or the agent acting for a person, who writes the decision, its rationale and its evidence. Recorded in `proposed_by`. |
| Independent reviewer | Someone other than the proposer or author, with the subject knowledge the decision needs. May comment and may approve a pull request, but does not set `accepted_by`. |
| Approver | A maintainer for the affected area, recorded in `accepted_by` with `accepted_on`. Must be neither the proposer nor the author of the pull request that carries the change. |

## Decision types

Each decision type names its proposer, independent reviewer and approver.

| Decision type | Proposer | Independent reviewer | Approver |
| --- | --- | --- | --- |
| Repository charter and scope | Maintainer | Independent research reviewer | Lead maintainer, Datasets & Benchmarks |
| Taxonomy vocabulary, including entity kinds and relationships | Maintainer | Reviewer for each affected workstream | Lead maintainer, Datasets & Benchmarks |
| Inclusion and exclusion rules | Maintainer | Independent research reviewer | Lead maintainer, Datasets & Benchmarks |
| Evidence, rights or publication policy | Maintainer | Independent rights reviewer | Lead maintainer, Datasets & Benchmarks |
| Record admission, `candidate` to `accepted` | The researcher proposing the record | Rights reviewer and evidence reviewer | Lead maintainer, Datasets & Benchmarks |
| Record publication | Maintainer | Rights, editorial and evidence reviewers | Lead maintainer, Datasets & Benchmarks |
| Correction or retraction | Anyone, through the correction form | Independent reviewer of the affected claim | Lead maintainer, Datasets & Benchmarks |
| This page: governance and process | Maintainer | Independent maintainer | Lead maintainer, Datasets & Benchmarks |
| Emergency or bypass | Any maintainer | Organization admin | Organization admin |

Where a work package names further reviewer roles in its own review requirements, those roles
also apply. This table does not remove a requirement; it names the minimum.

### Vacant specialties, delegation and placeholders

Until a specialty lead team is staffed, its gate is **not** satisfied merely by "any GitHub approver."
Use the organization owner's explicitly recorded approval for the affected scope, with an account
that is neither the proposer nor the PR author. If an interim shared Research aide narrows the actual
scope afterward, keep that narrower evidence tied to its actual decision.

DEC-006 and DEC-007's literal `Lead Maintainers - Datasets & Benchmarks` requirement was too narrow:
that specialty stage is empty and CompleteDotTech was removed from that team under `.github#18`,
while remaining the organization owner and repository admin. The earlier acceptance was correctly
reviewed as a general code PR, but this literal role was not established. I am therefore proposing
the corrected role-disposition below, with DEC-006 and DEC-007 returned to `proposed` and null
acceptance fields until the required acceptance is actually evidenced. PR #79 is where that
reconciliation is reviewed; no silent corrective merge is implied.

## Independent review

An approval satisfies the independent-review requirement only when all of the following hold:

1. The approver is not the author of the pull request and not the proposer of the decision.
2. The approver is a person. An automation account, GitHub App, or a delegate acting for a person
   is analysis, not approval, and cannot satisfy this requirement.
3. The approval was submitted after the most recent push to the branch.

`AGENTS.md` already states the second rule for contributors: an agent or bot review is analysis,
not the required approval from someone other than the author. This page makes it binding for the
decision register as well.

Where the separated specialty team has too few human members to carry the role, do not silently
assign that role to a wider team, a placeholder account or an automation credential. Record its
vacancy and escalate to the organization owner, who supplies the required scope-specific approval
without pretending to be a specialist. `Research Maintainers` supplies independent evidence review,
not specialty approval by itself.

Two mechanisms enforce parts of this. The `Review required: default branch` ruleset requires one
approving review and approval of the most recent push, and only an organization admin can bypass
it. `python3 scripts/validate_plan.py` rejects a decision that is marked `accepted` while recording
no acceptor, an acceptor equal to its proposer, a missing acceptance date, or an acceptor that is
an automation account.

Neither mechanism can verify that a human approved: an automation account writing a review through
a person's credentials is indistinguishable from the person at the API. Rules 1 and 3 are enforced
by tooling; rule 2 is enforced at the register for automation accounts and otherwise depends on the
maintainer merging the change.

## Decision register

Decisions live in `planning/decision-register.json` and are validated against
`schemas/planning-decisions.schema.json` by `scripts/validate_plan.py`.

| Field | Meaning |
| --- | --- |
| `id` | `DEC-NNN`, unique and never reused. |
| `title` | One line, stated as the decision, not as the topic. |
| `rationale` | Why this decision, in one or two sentences. |
| `status` | `proposed`, `accepted`, `superseded` or `rejected`. |
| `proposed_on`, `proposed_by` | Date and proposer. |
| `accepted_on`, `accepted_by` | Date and approver, or `null` while proposed. |
| `evidence` | At least one pointer to a public artifact. Paths in this repository or public URLs. |
| `acceptance_requirement` | The gate this decision must clear before `accepted`. |

A decision moves from `proposed` to `accepted` in a later commit that names the approver and the
date, once that approval exists. It is not accepted by the pull request that proposes it, and a
proposed decision that records an acceptor is rejected by the validator.

Superseding a decision adds a new decision and sets `status` to `superseded` on the old one; the
old entry keeps its text. History is not rewritten, and corrections follow the same rule.

## Escalation

Use the organization [escalation guide](https://github.com/Pick-Your-AI/.github/blob/main/docs/governance/ESCALATION.md)
and its [routing policy](https://github.com/Pick-Your-AI/.github/blob/main/governance/escalation-policy.json)
rather than a copied contact list. The order is repository team, repository maintainer, repository
lead maintainer, applicable parent teams, then CompleteDotTech.

Routing identifies a contact for an unresolved decision. It does not grant access, appoint an owner,
authorize publication, or waive a review, evidence or release requirement. Record the disposition at
each level, including roles that are vacant, unresolved or inaccessible, and do not treat a proposed
mapping as an accepted one.

Keep private rosters, snapshots and raw API responses out of this repository and out of public
issues. A public issue carries only the decision needed, the current responsible role, the prior
disposition and the proposed next recipient.

## Changing this page

Governance changes are a decision of their own. Open a pull request that proposes the change, add
the corresponding register entry, and let an independent maintainer approve it. This page and the
register change together; a change to one without the other is incomplete.