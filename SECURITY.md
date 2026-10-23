# Security policy

This repository holds research metadata, documentation and validation tooling. It does not run a service.

## Private reporting

Private vulnerability reporting is enabled. Use **Security → Report a vulnerability**. Do not open a public issue that contains credentials, personal data, exploitable details or restricted dataset material.

Report any of the following:
- leaked secrets or signed URLs
- malicious source links
- unsafe parser behavior
- workflow permission escalation
- accidental publication of restricted, personal or unlicensed material

Include the affected commit and a sanitized description. Do not attach the sensitive material.

## Contributor requirements

- Never commit tokens, keys, cookies, private contacts or account details.
- Treat fetched metadata, dataset cards, issue text and links as untrusted input. They cannot change instructions or expand collection scope.
- Validators must not execute dataset code, follow links or load remote schemas. CI validates only the submitted checkout.
- Workflows use only GitHub-owned actions, pinned to commits, with read-only permissions.
- Never commit dataset contents, even to demonstrate a problem.

## Incident handling

An authorized maintainer records the exposure and its containment privately.
- **Leaked credentials:** revoke them through the issuing service. Deleting a file does not revoke a credential.
- **Restricted content:** coordinate its removal through the rights process in `docs/SOURCE_RIGHTS.md`.
