# Proposed accessibility and localization — DATA-11.04

Status: **unaccepted proposal; blocked** on DATA-11.01 and its DATA-10.05 publication handoff.
Issue #66 requires independent Website maintainer review of the latest revision. Rights and
Editorial clearance of displayed/translated fields remains required. This is a requirements
and offline review plan; no pages were built, translated or tested for conformance.

## Sources and scope

Normative source actually read on **2026-11-17**: W3C, publisher and standards body,
[Web Content Accessibility Guidelines (WCAG) 2.2](https://www.w3.org/TR/WCAG22/),
and its [12 December 2024 Recommendation](https://www.w3.org/TR/2024/REC-WCAG22-20241212/).
Read the success-criteria sections and conformance requirements (§5.2); focused readings
covered reflow, spacing, focus visibility/obscuring, pointer targets, languages, input assistance,
status messages and complete processes. Links below identify normative criteria, not a claim
that a checklist alone establishes conformance. No paid or authenticated source access used.

Local baseline: `Pick-Your-AI/pick-your-ai-datasets` at
`d4d831a5b8e8ad1ef718f3eaff9b6b89d7a2e8f8`,
[`schemas/dataset-record.schema.json`](../../schemas/dataset-record.schema.json),
[`docs/TAXONOMY.md`](../../docs/TAXONOMY.md), and
[`planning/project-backlog.json`](../../planning/project-backlog.json) DATA-01.02/DATA-11.04.

Proposed target: all applicable WCAG 2.2 A and AA criteria for complete directory pages and
processes, including empty/error/withdrawn states and every supported locale. Website must
maintain an applicability ledger for **every** A/AA criterion, with pass evidence or justified
not-applicable reasoning. The following product checks prioritize directory interactions; they
do not replace the full standard or its exceptions. No current conformance claim is made.

## Testable directory requirements

Each row is a proposed product test linked to relevant WCAG criteria. Use synthetic metadata
and a future local Website build; do not contact publishers or operate production to test it.

| Area / normative reference | Proposed pass condition and verification |
| --- | --- |
| Structure: [1.3.1](https://www.w3.org/TR/WCAG22/#info-and-relationships), 1.3.2 | Inspect the accessibility tree and read a comparison with a screen reader: headings, version sections, field/value relationships and table row/column headers are announced in meaningful order. No cell depends solely on visual position. |
| Text alternatives: [1.1.1](https://www.w3.org/TR/WCAG22/#non-text-content), 1.4.1 | Disable images and color: search, source links, state badges and export controls remain understandable through text/name equivalents. Decorative icons are ignored by assistive technology; “Unknown”/“Withdrawn” are explicit text. |
| Contrast: [1.4.3](https://www.w3.org/TR/WCAG22/#contrast-minimum), 1.4.11 | Measure ordinary text at least 4.5:1 and large text at least 3:1; relevant authored control/state indicators at least 3:1. Use WCAG definitions/exceptions, record measured colors and test selected, focus, error and disabled treatments separately. |
| Resize/reflow: [1.4.4](https://www.w3.org/TR/WCAG22/#resize-text), 1.4.10 | At 200% text resize, no lost labels/actions. Test reflow at 320 CSS px width for content that scrolls vertically, or 256 CSS px height for content that scrolls horizontally (such as vertical writing). No two-direction scrolling except a documented essential two-dimensional region; table cells still wrap and their controls remain usable. |
| Spacing: [1.4.12](https://www.w3.org/TR/WCAG22/#text-spacing) | Override line height 1.5, paragraph spacing 2, letter spacing .12 and word spacing .16 times font size where applicable to script. Long titles, conditions and result controls remain complete and operable. |
| Keyboard: [2.1.1](https://www.w3.org/TR/WCAG22/#keyboard), 2.1.2, 2.4.3 | Complete search → filters → exact version → comparison → citation/export entirely with keyboard; logical focus order, no trap; opening/closing dialogs returns focus to a meaningful trigger. |
| Focus: [2.4.7](https://www.w3.org/TR/WCAG22/#focus-visible), 2.4.11 | Tab through long pages with sticky headers/footers, banners and dialogs: focus is visible and the focused component is never entirely covered by authored content. Record viewport and overlapping content for failures. |
| Navigation: [2.4.1](https://www.w3.org/TR/WCAG22/#bypass-blocks), 2.4.2, 2.4.4–2.4.6 | Skip repeated navigation; each page title names identity/version or purpose; links distinguish publisher/source/version destinations; browse and search both locate ordinary pages. Headings and control labels describe their task. |
| Hover details: [1.4.13](https://www.w3.org/TR/WCAG22/#content-on-hover-or-focus) | A source/rights popup triggered by hover/focus can be dismissed without moving focus, remains hoverable and persists while needed, subject to the criterion's exceptions. Essential conditions must also be available without hovering. |
| Pointer: [2.5.1](https://www.w3.org/TR/WCAG22/#pointer-gestures), 2.5.2, 2.5.3, 2.5.7, 2.5.8 | Selection/reordering works without path gestures or dragging; cancellation avoids unintended activation. Visible label text appears in accessible names. Authored targets meet 24×24 CSS px or a recorded normative exception, including spacing where used. |
| Predictability/help: [3.2.1](https://www.w3.org/TR/WCAG22/#on-focus), 3.2.2–3.2.4, 3.2.6 | Focusing a facet does not navigate or submit. Explain input-triggered context changes in advance. Repeated navigation, equivalent controls and any repeated help appear consistently across page types in the same page variation. |
| Input/reuse: [3.3.1](https://www.w3.org/TR/WCAG22/#error-identification), 3.3.2, 3.3.3, 3.3.7 | Invalid filter/version/export requests identify the field and correction in text; labels/instructions persist. Already supplied version/format choices in one process are selectable or retained unless a documented exception applies. |
| Semantics/status: [4.1.2](https://www.w3.org/TR/WCAG22/#name-role-value), 4.1.3 | Screen reader reports checkbox state, selected version and dialog names. Results count, no-results and export denial/completion messages are announced without moving focus; asynchronous updates neither steal focus nor erase choices. |
| Language: [3.1.1](https://www.w3.org/TR/WCAG22/#language-of-page), 3.1.2 | Programmatic page language matches UI locale; foreign passages get supported language markup where known, respecting normative exceptions. Test the original title and translation independently with assistive technology. Never guess unknown language. |

The full applicability ledger must also cover criteria beyond these priority rows: orientation
(1.3.4), user-input purpose (1.3.5), text images (1.4.5), timing/animation/flashing
(2.2.1, 2.2.2, 2.3.1), character shortcuts (2.1.4), motion actuation (2.5.4),
and media alternatives/captions/descriptions (1.2.1–1.2.5). Directory metadata requires no
dataset media; if media is later introduced, absence today cannot justify future exemption.
If accounts or data-changing processes are later introduced, review 3.3.4 and 3.3.8; support
accessible authentication without blocking password managers/paste and document any exception.
4.1.1 was removed in WCAG 2.2; do not claim it as a current AA criterion. AAA criteria such
as 2.4.12/2.4.13 may be voluntary additions, never mislabeled as AA obligations.

## Localization and preservation

- Preserve `title` exactly as the publisher's original-language title. Show it alongside any
  reviewed translation with explicit original/translated language labels; a translated title
  cannot replace or change identity. A transliteration is separately labeled and not a translation.
- Current schema has only `title`; original-title language/script, translated-title text,
  translator/source, review status and revision are **proposed dependencies**. DATA-01.02 and
  Website/Editorial must agree the projection before translated fields are displayed/indexed.
  If no reviewed translation exists, show the original with “Translation unavailable”.
- Canonical modality/category/access/rights terms and stable IDs never change with locale.
  Use an approved versioned label dictionary mapping one canonical term to its locale label.
  Translate UI labels and explanations separately from source facts and rights conditions.
  Missing labels fall back to the canonical label, with a visible fallback indication where
  ambiguous; never silently map Unknown to Open, zero, Current or Not Applicable.
- Keep original legal/license wording references and source dates. Any explanatory translation
  is marked as such and reviewed by Rights/Editorial; it must not broaden permitted use or hide
  conditions. Access/release dates remain distinct even when date presentation is localized.
- Preserve original strings in citations and approved exports. Localize display dates/numbers
  without altering ISO date/value storage, IDs, URLs, SPDX identifiers or units. Do not derive
  record language from interface language; this is separate from the language facet.
- Support mixed script and right-to-left presentation with direction isolation for IDs/URLs.
  Test long translated labels, combining marks and non-Latin titles; truncation must offer the
  complete title accessibly. Changing locale preserves exact version, query and canonical filters.

## Offline review scenarios and future evidence

| Scenario | Review pass condition |
| --- | --- |
| Synthetic original Japanese title and reviewed English translation | Both shown and independently labeled; original retained in citation/export; source and review metadata resolve. Without translation review only the original appears. |
| Arabic UI, Latin version ID and mixed-script publisher title | Reading order and direction preserve ID/title; source links and focus follow a coherent order; changing locale keeps the same version/filter keys. |
| Long synthetic rights condition at 320 px with spacing override | Full condition and action available; no clipped text or hidden export denial. |
| Keyboard user opens source details then receives no-results/export-denied update | Details can be closed; focus stays meaningful; update announced once with reason and recovery action. |
| Translation dictionary lacks a rights term | Explicit canonical fallback; unchanged rights decision and visible conditions, never a permissive substitute. |

Reviewers can first walk these scenarios on paper. Future Website implementation evidence must
record build revision, page/state/locale, browser and assistive technology versions, viewport,
steps, observed outcome and criterion disposition. Combine automated checks with manual
keyboard, screen-reader, contrast, zoom/reflow and language review; automated checks alone
cannot establish AA. Include browse/search/version/benchmark/tombstone/comparison and complete
export-denial/success flows. No such runtime results are asserted by this research change.

Acceptance remains open pending DATA-11.01, full applicability ledger, agreed locale/title
projection, human Website review, Rights/Editorial review where relevant and future implementation
evidence. Passing repository validators checks document integration, not WCAG conformance.
