# Corpus policy

Committed cases are original synthetic fixtures. They are not tenant exports, customer records, production prompts, SBOMs, or advisory payloads.

## Identifiers

- Organizations start with `org-synthetic-`.
- Findings start with `finding-synthetic-`.
- Assets start with `asset-synthetic-`.
- Evidence starts with `evidence-synthetic-`.
- Advisories match `PP-SYN-ADV-` plus four digits.
- Packages use the `pkg:synthetic/` namespace.
- Documentation URLs use `http` or `https` with a host ending in `.invalid`.

`org-synthetic-south` is a negative-control organization. No case authorizes it. North cases use north package names. East cases use `east-relay`.

## Counts

The corpus has 24 cases: 6 grounding and citation, 4 insufficient-evidence refusals, 4 prompt-injection, 4 cross-tenant controls, 3 contradictions, and 3 stale, unavailable, or incomparable evidence cases.

Prompt-injection markers and negative controls are required arrays. They are empty except on the cases in those two categories.

## Digests

Canonical JSON is UTF-8, object keys sorted, separators `,` and `:`, and no trailing newline. A case digest is SHA-256 of that form after `caseDigest` is removed. The corpus digest is SHA-256 of the canonical array of `{caseId, caseDigest}` sorted by case ID.

## Prohibited material

Do not add real names, email addresses, IP addresses, credentials, connection strings, or vulnerability prose copied from a published advisory. Pattern checks reject probable secrets. They do not prove that every real-world identifier would be recognized.
