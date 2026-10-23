# Maintenance

## Freshness

Each source records an access date. Work package DATA-12.02 sets the refresh target for each source class. A record whose sources are past their target is "Due for Refresh" or "Stale" in the **Source Freshness** field. A refresh never overwrites a value without a new, dated check.

## Corrections

Corrections arrive through the correction form. They are reviewed by someone other than the correction's author and disclosed with a date (DATA-12.03). Shared history is never rewritten to hide a correction.

## Retention and withdrawals

A withdrawn or superseded record is kept as a tombstone. The tombstone records the reason, the date and the authoritative source. Aliases and superseded IDs are never reused. Git history is rewritten only for legal or security removals approved through `SECURITY.md`.

## Recovery

| What | How to recover |
| --- | --- |
| Repository contents | Restore from Git history through a reviewed pull request |
| Issues and relationships | Recreate them from `planning/project-backlog.json` and `planning/issues/`, reconciled against `planning/issue-map.json` |
| Project values | Recreate them using the empty-values-only rule in `docs/PROJECT_SETUP.md` |

Work package DATA-09.04 records a recovery drill.

## Ownership

Workstreams are owned by team roles, not named individuals. Work package DATA-12.06 records the rotation and the criteria for archiving. Team membership changes follow the organization policy.
