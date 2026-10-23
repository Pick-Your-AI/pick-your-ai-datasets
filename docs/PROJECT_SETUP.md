# Project setup

## Resources

| Resource | Value |
| --- | --- |
| Repository | [Pick-Your-AI/pick-your-ai-datasets](https://github.com/Pick-Your-AI/pick-your-ai-datasets) (public; default branch `main`) |
| Project | [#11 Pick Your AI — Datasets & Benchmark Research](https://github.com/orgs/Pick-Your-AI/projects/11) |
| Coordinating parent | [research #509](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/509) |
| Issue map | [planning/issue-map.json](../planning/issue-map.json) (stable ID → issue number, read back from GitHub) |

## Hierarchy

- **Native issues:** the program (`DATA`), 12 epics (`DATA-NN`) and 60 work packages (`DATA-NN.NN`). Each is a native sub-issue of its parent.
- **Checklists:** tasks (`DATA-NN.NN.Tn`) and subtasks (`…Tn.Sm`) are nested entries in their work package's issue body.
- **Blockers:** native blocked-by links mirror `blocked_by` in the backlog. Handoffs and informational links are never blockers.

Issue bodies are generated in `planning/issues/`. `validate_plan.py --live` reports any drift in titles, bodies, parents, blockers or Project items.

## Project fields

The fifteen single-select fields, with their options, are defined in `planning/project-backlog.json`:

Status, Priority, Record Type, Workstream, Readiness, Dataset Modality, Dataset Category, Access Classification, License/Rights Status, Evidence Confidence, Source Freshness, Dependency Status, Effort, Release Phase, Acceptance Status.

Ownership uses native **Assignees**. Every item starts unassigned, and nobody is assigned without their agreement.

### How initial values are reconciled

Initial values come from `scripts/planlib.py:project_values`. Reconciliation **fills empty values only**. A live value that differs from the initial value is human triage: it is preserved and reported, never reset.

## Saved views

Ten views are defined in `planning/project-backlog.json`:
- Program Overview
- Epic Hierarchy
- Research Coverage
- By Modality
- Licensing and Rights
- Evidence Verification
- Blocked Dependencies
- Active Research
- Publication Readiness
- Unassigned Work

The GitHub API sets a view's name, layout, filter and visible fields. Grouping and sorting are set in the Project UI. They are verified separately from the API configuration.

## Governance

All of the following were read back from GitHub on 2026-10-23.

**Team grants:**

| Team | Permission |
| --- | --- |
| Maintainers | Triage |
| Research | Triage |
| Research Maintainers | Write |
| Research Lead Maintainers | Admin |

**Rulesets (all active):**

| Ruleset | Effect |
| --- | --- |
| Contributor boundary: default branch | Only maintainers and admins can update `main` |
| Contributor boundary: branches | Branches outside `contrib/` and `dependabot/` are maintainer-only |
| Contributor boundary: tags | Only maintainers and admins can create, move or delete tags |
| Review required: default branch | Blocks deletion and force-push of `main`; requires one approval, approval of the latest push and the `validate` check; no bypass actors |

**Other settings:**

- Actions limited to GitHub-owned actions
- Default workflow token read-only
- Private vulnerability reporting enabled
- Secret scanning and push protection enabled

## Bootstrap history

The repository was created with GitHub's initial README commit on `main`. All foundation content arrives through the `contrib/CompleteDotTech/datasets-foundation` pull request, under the rulesets above. Nothing was pushed directly to `main` after the rulesets were applied.
