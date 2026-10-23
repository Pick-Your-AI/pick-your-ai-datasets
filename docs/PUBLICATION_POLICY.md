# Publication policy

A record moves through these states: `candidate` → `withheld` or `eligible` → `published`. A record can become `withdrawn` from any state.

## Gates for `eligible` and `published`

All of the following are enforced by `scripts/validate_catalog.py`:

1. Every version has a version label. Unversioned references are ambiguous and cannot be published.
2. Rights status is **Permitted for Metadata Use** or **Conditional**, and access classification has been assessed.
3. A reviewed `metadata_display` permission is allowed or conditional, and every recorded permission has been reviewed.
4. Accepted **rights**, **editorial** and **evidence** reviews exist, each by someone other than the proposer.
5. All publisher, license, permission, relationship and withdrawal references resolve to recorded sources.
6. The record contains no personal contact data.

`python3 scripts/validate_catalog.py --publication` rejects every proposal that is not eligible or published. Withheld records can never be released.

## Withdrawals

A withdrawal cites an authoritative notice and is dated. A withdrawn record keeps a tombstone (see `docs/MAINTENANCE.md`) and cannot be republished without a new review.

## What is never published

Dataset contents, samples, hidden test items, answer keys, red-team prompts, personal data, or anything whose display permission is unknown.

## Consumers

Consumers receive only `eligible` or `published` records, together with their display constraints (DATA-10.05). Non-comparable benchmark results must be labeled and never ranked together (DATA-08.03).
