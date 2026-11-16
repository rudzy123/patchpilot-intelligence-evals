# Controlled artifact acquisition

Track 8A adds a closed acquisition plan, a source allowlist, quarantine transfer, offline verification, and same-filesystem promotion. The committed plan is a preflight record. `acquisitionStatus` stays `not-acquired`. `selectionOutcome` stays `no-selection`. `installationAuthorized` stays false. `measurementPerformed` stays false. `productionReady` stays false.

The plan and allowlist are derived from the committed runtime policy and the selected finalist inventory. They are [acquisition-plan.json](../../candidates/authorization/acquisition-plan.json) and [acquisition-allowlist.json](../../candidates/authorization/acquisition-allowlist.json). Historical Track 8 authorization stays `not-authorized` in [track8-acquisition-authorization.json](../../candidates/authorization/track8-acquisition-authorization.json).

Transfer is allowed only after the operator supplies the plan digest. The initial URL must be one of the twelve allowlisted URLs. A redirect stays on HTTPS, carries no embedded credentials, and stops after two hops. An origin hop on `github.com` or `huggingface.co` is accepted only when the repository, revision, and filename are unchanged. Metadata-only discovery observed two delivery hosts and scoped them to this plan: `release-assets.githubusercontent.com` for the runtime archive, and `us.aws.cdn.hf.co` for the four selected ONNX files. `objects.githubusercontent.com`, `cdn-lfs.huggingface.co`, and `cas-bridge.xethub.hf.co` were not observed and stay prohibited. This is not a general CDN allowlist. Any other host stops the transfer and saves no body.

The candidate filesystem must have at least 6,442,450,944 available bytes. The reservation formula remains 4,998,666,888 bytes. The logical artifact ceiling remains 8,589,934,592 bytes. Absolute cache roots are operator arguments and are not committed.

The connect timeout is 30 seconds. A stall timeout is 120 seconds. The runtime archive limit is 10 minutes. Each candidate file limit is 45 minutes. A retry is allowed twice, and only for timeout or connection reset. Each retry uses a new attempt id. The incomplete payload is deleted. A bad redirect, HTTP error, size mismatch, or identity mismatch is not retried.

Quarantine bytes are not executed. After the bytes are on disk, hashing runs inside a bubblewrap network namespace. The in-process network hook is not that control. Promotion uses the atomic no-replace rename in [atomic-artifact-promotion.md](atomic-artifact-promotion.md). There is no copy fallback.

Repository Contracts validates the committed records and templates. It does not call `acquire-runtime`, `acquire-candidate`, or `hardened-offline-load-proof`.

The 2026-11-16 review records one completed external acquisition. The plan file stays the preflight record. Observed digests, the provider-library disposition, and the attempt closeout are in [track8a-acquisition-evidence.md](../provenance/track8a-acquisition-evidence.md). The acceptance record is [track8a-implementation-review.md](../provenance/track8a-implementation-review.md). Track 8B measurement stays `not-authorized`.

Runtime staging is described in [external-runtime-installation.md](external-runtime-installation.md). The load proof is described in [hardened-offline-load-proof.md](hardened-offline-load-proof.md). The operator steps are in [runtime-acquisition-runbook.md](../operations/runtime-acquisition-runbook.md) and [candidate-acquisition-runbook.md](../operations/candidate-acquisition-runbook.md).
