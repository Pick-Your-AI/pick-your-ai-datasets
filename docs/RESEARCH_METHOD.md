# Research method

## Evidence levels

| Level | Meaning |
| --- | --- |
| Unverified | Proposed; sources not yet checked |
| Low | One source, or sources that disagree, recorded as stated |
| Medium | Publisher primary source checked for the exact version |
| High | Publisher primary source plus independent corroboration, reviewed |

These map to the Project field **Evidence Confidence**. A level applies to a specific claim about a specific version, not to a dataset as a whole.

## Rules

1. **Cite primary sources.** Use the publisher landing page, dataset card, paper revision or license text. Record its URL, publisher, role and access date.
2. **Bind to versions.** Every claim attaches to a version. A reference without a version is recorded as `unversioned`, is ambiguous, and cannot be published.
3. **Attribute claims.** Write "the publisher states 120k examples", not "has 120k examples". Third-party analyses stay attributed to their authors.
4. **Keep unknowns explicit.** An unknown size is `null`, never 0. Absence of a consent statement is "unknown", not consent. A reproduction that was not attempted is not a failed reproduction.
5. **Do not collect contents.** Metadata only. Do not download datasets to verify claims.
6. **Use permitted methods.** Discovery methods and source terms follow `docs/SOURCE_RIGHTS.md` and work package DATA-02.01.
7. **Merge only with evidence.** Matching names are candidate signals. Merges and splits need a logged rationale and a reviewer (DATA-04.04).

## Coverage

Coverage is reported per row of [planning/coverage-matrix.json](../planning/coverage-matrix.json). Each row declares its owning work package, its existing research owners and a denominator. A denominator stays `null` until it is counted from a named source on a recorded date. "Not counted" is never reported as zero or as complete. Work package DATA-01.03 defines the measures.

## Benchmarks and comparability

A benchmark result is comparable to another only if they share the same benchmark version, split, metric definition, harness and aggregation (DATA-08.03). This repository records grading semantics. It does not produce or rank scores.

## Validation boundary

The validators check consistency: identity, sourcing, rights gates and plan integrity. They cannot confirm that a source is true or that a license permits a use. That needs the reviews in `docs/PUBLICATION_POLICY.md`.
