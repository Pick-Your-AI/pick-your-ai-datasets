# Backup and recovery runbook

This is partial offline work for `DATA-09.04` ([#55](https://github.com/Pick-Your-AI/pick-your-ai-datasets/issues/55)).
It provides a repository-file recovery drill and a proposed reconciliation procedure for
GitHub state. The storage-layout prerequisite `DATA-09.01` (#52) and acceptance by a
research lead maintainer remain outstanding. No issue, native relationship or Project
recovery has been performed or accepted by this drill. No production service is deployed.

Git history is a recovery source for tracked repository files. It is not a backup of
uncommitted files, deleted unreachable Git objects, GitHub comments, issue identifiers,
Project item identifiers, audit history, permissions or other live GitHub state. Planning
files describe intended structure and initial values; they do not capture every later
human decision. This work does not operate backup infrastructure or establish retention
or recovery-time guarantees.

## Before recovery

1. Identify the affected scope and a known-good full commit object ID from available
   local history. Check that the commit contains the intended record/version and is
   appropriate under the current rights, publication and withdrawal policies. Do not
   restore withdrawn or restricted material merely because it exists in history; use
   `SECURITY.md` for sensitive incidents.
2. Preserve the current state for comparison in an approved location. Record only
   sanitized metadata needed for review; keep credentials, personal data and private
   incident material out of public commits, issues and logs. Do not overwrite the only
   remaining copy of evidence.
3. Separate the desired baseline from current human changes. A recovery proposal must
   show what is missing, what changed after the baseline, what will be preserved and
   which conflicts require an owner decision. An unavailable or inaccessible value is
   unknown, never proof that it is empty or deleted.
4. Work in a disposable local clone or isolated contributor branch. Keep real repository
   files, GitHub issues and Projects unchanged during the drill and dry run. A real
   recovery requires the applicable owner's authorization, independent review and
   current required checks; never bypass rulesets or rewrite history to hide changes.

## Repository recovery

The offline drill is implemented by [`scripts/recovery_drill.py`](../scripts/recovery_drill.py).
Run it from a trusted local checkout, using an exact commit object ID and a tracked
regular-file path:

```bash
python3 scripts/recovery_drill.py \
  --repo . \
  --ref d4d831a5b8e8ad1ef718f3eaff9b6b89d7a2e8f8 \
  --path planning/release-manifest.json
```

The script resolves the commit and file without fetching. It copies the local Git
repository into a temporary clone without hardlinks or source working-tree edits,
removes that clone's remote and creates a disposable `recovery-drill` branch at the
pinned commit. It appends an explicitly synthetic corruption marker to the disposable
file, verifies that its bytes differ, restores bytes from the Git blob in that clone,
and checks byte equality and SHA-256 equality against the source commit. It runs all
four repository checks in the restored clone, captures their exit codes, then removes
the temporary clone. It creates no commit, source branch, remote issue or Project item.

Only local paths and full commit IDs are accepted. Traversal paths, symlinks, submodules,
missing files and moving branch/tag names are rejected. Git hooks and inherited Git
configuration are disabled for the Git operations, and no Git network transport is
used. Validation executes code from the pinned commit, so use a reviewed, trusted
repository and commit; the script is not a sandbox for untrusted code. No check uses
`--live`. Its JSON report contains commit/path/blob IDs, hashes and exit codes rather
than local absolute paths, user identities, process output or credentials.

Exit status `0` means the requested drill completed; `1` means at least one requested
repository check failed; `2` means a precondition or local operation failed. With
`--skip-checks`, only file restoration is attempted: `checks_requested` is false and
`checks_passed` is null. That mode cannot supply repository-validation evidence.
A failure is a stopped recovery proposal, not permission to weaken validation.

For a real file correction after owner authorization, first reproduce the desired
restoration in an isolated `contrib/` branch, inspect the complete diff against the
current branch and retain valid intervening changes. Restore the smallest reviewed
scope; do not replace all planning files with an old snapshot. Edit canonical planning
JSON and regenerate generated documents where necessary, rather than hand-editing
`planning/issues/` or generated delivery documentation. Run the four checks below and
submit a pull request referencing the incident and pinned source commit. Obtain the
required approval after the latest push. The drill intentionally offers no automatic
application to a real checkout.

```bash
python3 scripts/validate_plan.py
python3 scripts/validate_catalog.py
python3 scripts/render_docs.py --check
python3 -m unittest discover -s tests -v
```

## Issue, native parent and blocker recovery: dry run first

Remote replay is not implemented by this script. The following procedure is a proposed
runbook for an authorized owner, not evidence that GitHub state can be fully restored.
If required snapshots or API capabilities are absent, stop at a reconciliation report
and obtain an owner decision. Never infer a deleted issue from a failed API read.

1. Use the reviewed pinned `planning/project-backlog.json`, generated
   `planning/issues/` bodies and `planning/issue-map.json` as the intended baseline.
   Validate that local snapshot with the repository checks. Retain every stable
   `DATA-*` identity independently of its issue number.
2. When read access is separately authorized and available, inspect current issues,
   titles, bodies, comments, native parents, native blocked-by links, assignees and
   relevant Project state. Use read-only `python3 scripts/validate_plan.py --live`
   to identify drift; this is a live network operation and was not run for this drill.
   Preserve human triage, evidence and comments. Planning checklist tasks are not
   automatically separate native issues.
3. Build a dry-run change table before any write. Include stable ID, recorded issue
   number, verified current issue number, baseline value, current value, proposed
   action, evidence and unresolved conflict. Use explicit dispositions such as
   `preserve`, `missing confirmed`, `conflict` and `unknown`. Do not copy private
   comments, user identities or credentials into a public report.
4. Reuse surviving issues. Never overwrite a body containing later human additions
   with the generated baseline. If an owner confirms an issue must be recreated,
   propose its minimal body/title separately, retain a sanitized mapping from old
   stable ID/number to replacement, and read the actual new number back after the
   authorized operation. GitHub issue numbers and original audit/comment history
   cannot be recreated by this repository's planning files.
5. Propose native parent relationships only after both endpoints have verified live
   identifiers. Reconcile blockers separately from parents: baseline `blocked_by`
   means native blocked-by links; handoffs or informational links do not. Report
   conflicting or additional live parents/blockers for review; never remove them
   automatically. A textual link is not proof of a native relationship.
6. Review the complete dry run with the owner. No assignee is added without agreement.
   Any later replay needs explicit authorization for those concrete remote writes,
   supported tooling and a separate acceptance record. After authorized replay,
   re-read actual identifiers, parents and blockers, update `planning/issue-map.json`
   through a reviewed repository change, and compare a fresh read-only drift report.
   Record unresolved differences rather than declaring recovery complete.

## Project recovery: preserve live fields

The fifteen single-select fields, allowed options and proposed saved views are described
in `planning/project-backlog.json` and [`PROJECT_SETUP.md`](PROJECT_SETUP.md).
`project_values` in `scripts/planlib.py` supplies initial values, not current truth.

1. After separately authorized read access, inventory current Project identity, field
   and option identities, issue membership, item identities, populated/empty values
   and saved views. Record inaccessible fields as unknown. Reconcile against surviving
   issues using verified issue identifiers and stable IDs; never attach guessed numbers.
2. Produce a dry-run table per item and field. Include the baseline initial value,
   observed current value, proposed action and reason. Preserve every populated live
   value, even if it differs from the initial value: that is human triage. Fill an
   observed empty field only with the reviewed initial value. Unknown values stay
   unresolved; missing options or renamed fields require an owner decision, not
   silent remapping.
3. Propose missing membership, field/option definitions and views separately from
   field-value changes. Preserve existing configuration and additional items. Existing
   Project/item/field/option IDs may not survive recreation and must be read back;
   old IDs are evidence pointers, not reusable write targets. Grouping and sorting
   require separate UI verification per `PROJECT_SETUP.md`.
4. Have an owner approve the concrete proposal before any remote replay. Immediately
   before each authorized write, re-read its target and skip/report any concurrent
   change. Re-read the result afterward and compare only the agreed scope. A local
   snapshot cannot prove restoration of original audit history or deleted live values.
   Unsupported replay remains blocked pending supported tooling and separate human
   acceptance; never mark Project recovery complete from this offline drill.

## Recorded local drill — 2026-11-17 UTC

This drill ran against an available local checkout. Its only mutation was synthetic
corruption inside a temporary clone on branch `recovery-drill`. The source commit
contained the real tracked metadata manifest below; no dataset contents were used.

| Evidence | Observed result |
| --- | --- |
| Pinned source commit | `d4d831a5b8e8ad1ef718f3eaff9b6b89d7a2e8f8` |
| Source/restored path | `planning/release-manifest.json` |
| Source Git blob | `ac272b42c604c54da69996625e2520c8e28fc816` |
| Source SHA-256 | `090fa933d422124f70f41168524c1bec6bfd491c3e49c231dc0cf499b20b17be` |
| Synthetic corrupted SHA-256 | `1b571a2469c1f97c7c14db03698504ded1a9af0977dce73979a0179c4c7dff74` |
| Restored SHA-256 | `090fa933d422124f70f41168524c1bec6bfd491c3e49c231dc0cf499b20b17be` |
| Restored bytes equal pinned source | `true` |
| `python3 scripts/validate_plan.py` | Completed, exit `0` |
| `python3 scripts/validate_catalog.py` | Completed, exit `0` |
| `python3 scripts/render_docs.py --check` | Completed, exit `0` |
| `python3 -m unittest discover -s tests -v` | Completed, exit `0` |
| Drill command exit | `0` |
| Temporary clone | Removed when the drill returned |

The exact command is the invocation in the repository-recovery section above. These
four checks executed the pinned baseline's code and tests after restoration. They did
not include the new recovery regression tests, which are checked separately on the
contributor branch. `tests/test_recovery.py` uses temporary synthetic Git repositories
to exercise restoration, empty files, invalid refs/paths, symlinks, source working-tree
and ref preservation, and failed-check reporting.

Evidence level: **executed local file-recovery drill**. This demonstrates restoration
of one file from reachable local Git history and consistency of that restored baseline.
It does not demonstrate disaster recovery from a lost clone, remote backup availability,
issue/comment recovery, native relationship recovery, Project replay, live permissions,
production behavior or independent human acceptance. Keep #55 open with partial
`Refs #55` linkage until the prerequisite and required acceptance are resolved.
