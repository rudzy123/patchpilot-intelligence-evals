# Model artifact verification

Verification compares an expected file list with the files observed in one attempt directory. Expected names, sizes, and upstream digests stay in a different list from observed names, sizes, and SHA-256 values. A missing file, an unexpected file, a count mismatch, a size mismatch, or a digest mismatch rejects the attempt. Only `.safetensors` names are approved. An authoritative upstream digest is compared when the expected record has one. A null upstream digest is recorded as `not-provided` and is not treated as a match to a publisher hash.

The verified identity is the SHA-256 of the canonical verification record. Reading the directory again after any changed byte produces a different identity. Locally verified digests are recorded only for a `verified` result. Rejected and not-acquired results keep that array empty. `acquisitionStatus` stays `not-acquired` and `executionStatus` stays `not-executed` for these records, including a synthetic verified inventory. A synthetic pass is not acquisition of a model.

Symlinks are not followed. A remote-code requirement is rejected. Executable sniffing checks the permission bits, a leading shebang, and ELF magic. That sniff is not malware detection and it is not a statement that a file is safe to execute.

The committed template is [model-artifact-verification-template.json](../../candidates/templates/model-artifact-verification-template.json). `artifact-verification-validation` checks it. Tests use temporary synthetic bytes outside the repository. The cache rules are in [external-artifact-cache.md](external-artifact-cache.md).

Principal Systems Architect review on 2026-11-10 accepts these controls with the documented limitation that executable sniffing is not malware detection. The acceptance record is [track5-implementation-review.md](../provenance/track5-implementation-review.md).
