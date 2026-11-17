# Proposed discovery protocol

This is offline preparation for `DATA-02.01` ([#9](https://github.com/Pick-Your-AI/pick-your-ai-datasets/issues/9)).
It is **proposed and unaccepted**. DATA-01.01 and DATA-01.04, source-specific terms
checks and the required independent rights review remain outstanding. No source
requests, source inventory or accepted source-use decision is evidenced by this
document. No collector or crawler is implemented here.

## Separate the permissions

Use [SOURCE_RIGHTS.md](SOURCE_RIGHTS.md), [RESEARCH_METHOD.md](RESEARCH_METHOD.md)
and [PUBLICATION_POLICY.md](PUBLICATION_POLICY.md) together. Source-site access,
metadata reuse, dataset use, consent and public display are separate questions.
Record the publisher's statement with its exact version, URL and actual access
date; do not infer any permission from public availability, a checksum, a license
badge or successful authentication. Never download dataset contents to check a claim.

The existing source-class table defines the narrow identity fields that can be
recorded before further review. The proposed method controls below supplement it;
they do not expand those fields or grant permission for a particular site.

## Source-class method table

| Source class | Bounded method proposed for review | Metadata boundary | Methods excluded |
| --- | --- | --- | --- |
| Academic and preprint | Manually inspect the public paper landing page and exact revision metadata | Identity and paper-revision link; original short attributed notes | Bulk paper copying; dataset/sample downloads; treating paper availability as reuse permission |
| Official, government and standards body | Manually inspect the official catalog entry and its linked public terms | Identity, landing page and stated license family, without normalizing uncertain rights | Assuming all official data is public domain; copying standard text; bypassing restricted portals |
| Commercial and vendor | Manually inspect publicly visible product descriptions and terms | Public product metadata only | Purchases, account-gated content, trials, private sales contact or credentialed product APIs |
| Community or open repository | Manually inspect the publisher/host card at an exact revision | Published host identifier and revision; distinguish host from publisher | Repository bulk scraping; executing dataset loaders; inferring license or publisher authority from a mirror |
| Specialized domain | Manually inspect public catalog metadata and access-gate descriptions | Public identity and gate descriptions only | Patient/participant samples, restricted scientific material, applications for access or circumvention |

For every class, a documented public API is only a **candidate method** pending
its own terms, scope and rights review. The campaign does not authorize live paid
or credentialed third-party API calls. Absence of an explicit automated-use limit
means **no automated requests under this proposal**, not an unlimited rate. No
source-specific numerical request limit is invented here.

## Per-source review before research expands

1. Open a proposed note using [source-use-review.md](../templates/source-use-review.md).
   Name the source class, exact public location, revision and bounded metadata
   purpose. Keep an unavailable revision explicit as `unversioned`.
2. Inspect the primary public description and source terms using an allowed manual
   method. Record the actual read date only after reading. If a sign-in, payment,
   restricted-content or permission wall intervenes, record the missing public
   evidence and stop. Do not create accounts, apply for access or contact publishers.
3. Record website/API terms separately from the dataset/version license and any
   metadata-display permission. Record required attribution and known restrictions
   as source statements; preserve conflicting statements and unknowns for review.
4. Propose the smallest allowed fields and method. Any future automation must have
   an evidenced endpoint scope, a source-published limit, a reviewed lower budget,
   concurrency bounds, retry/backoff behavior and an explicit stopping condition.
   An undocumented limit, ambiguous terms or inaccessible policy blocks that method.
5. Obtain the required independent rights review of the exact note. A reviewer
   records actual scope, conditions and evidence; a model-generated note or CI pass
   is not that approval. Keep the note proposed/withheld while acceptance is absent.
6. Only within the separately accepted scope, create candidate metadata records and
   run the repository validators. Rights, editorial, evidence and receiving-owner
   approval remain distinct gates before eligibility or handoff. Do not elevate a
   source-use review into approval of every dataset hosted at the source.

## Conditions for any later automated adapter

This is a proposed adapter contract, not implemented or tested network behavior.
The authorized implementation must fail closed when its reviewed scope is absent
or stale. Its request plan must identify permitted URLs and output fields before
execution. Do not forward credentials across redirects or treat a new host as the
same approved source. A changed endpoint, terms revision, access gate or requested
field set requires renewed review.

Respect the most restrictive applicable reviewed budget and source limit. Do not
parallelize workers to evade a global limit. Stop on 401/403 or an unexplained access
denial; honor explicit 429 retry instructions and stop when no reviewed retry
behavior applies. Record sanitized disposition and request counts, never tokens,
cookies, private payloads or signed URLs. A failed refresh must not make a cached
record appear freshly observed. Do not run a network integration test for this
campaign; use synthetic response fixtures for later adapter tests.

## Offline acceptance scenarios

These are review cases for the proposed protocol, not results of executing a collector.

| Synthetic case | Required disposition |
| --- | --- |
| Public landing page; no terms evidence | Retain permitted identity pointers only; automated collection and publication remain blocked |
| Dataset license is clear; metadata reuse terms are unknown | Keep the metadata permission unknown; do not infer it from the dataset license |
| Public API documentation gives no request budget | No automated requests; ask for a reviewed source-specific disposition without contacting the source automatically |
| A source requires credentials or payment | Stop this campaign's source access; preserve the exact missing evidence without account creation or spending |
| A synthetic 429 response gives a retry time | A future adapter must obey the reviewed retry policy and that time; no immediate retry or parallel-worker evasion |
| Terms or destination host changes during collection | Stop and require a new review of the changed scope |
| Only an agent review exists | Keep source-use acceptance unfulfilled |
| New metadata is proposed from permitted observations | Candidate state only, with actual source dates; all publication and receiving gates remain |

## Remaining acceptance evidence

The source-class methods need source-specific public terms and attribution evidence,
and any rate limits must be recorded from those sources. The current repository has
no such completed source inventory. Accepted charter/governance prerequisites and a
qualifying independent rights review are still required. Reference #9 as partial work;
do not close it from this protocol, a template or passing structural tests alone.
