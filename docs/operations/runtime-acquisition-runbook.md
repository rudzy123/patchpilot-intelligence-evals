# Runtime acquisition runbook

This runbook does not transfer an archive. The 2026-11-16 review records one completed transfer in [track8a-implementation-review.md](../provenance/track8a-implementation-review.md). The operator approves the exact plan in chat before any command below is run with a real cache root.

1. Confirm [acquisition-plan.json](../../candidates/authorization/acquisition-plan.json) still has `acquisitionStatus` `not-acquired` and `operatorApproval` `required`.
2. Choose two absolute cache roots outside this repository, outside `patchpilot` and `neural-from-scratch`, and outside `/home`, `/Users`, `.venv`, `build`, `dist`, and a CI workspace. The runtime root and the model root must differ. The candidate filesystem needs at least 6,442,450,944 free bytes. The reservation formula remains 4,998,666,888 bytes, and the logical artifact ceiling remains 8,589,934,592 bytes. Do not commit the absolute roots.
3. Run `uv run patchpilot-evals acquisition-preflight --runtime-cache <runtime-root> --model-cache <model-root>`. The report must show `transfer` `not-started` and `freeSpaceSufficient` true. It must not contain a host path.
4. After explicit approval of the plan digest, run `uv run patchpilot-evals acquire-runtime --runtime-cache <runtime-root> --operator-approval <planDigest>`.
5. The command writes one quarantine attempt, then hashes the archive with network-namespace denial. A mismatch leaves the attempt unpromoted. A timeout deletes the incomplete payload and may retry twice with a new attempt id.
6. Promotion, when the inventory matches, renames the flat verified set into the verified root. The verified set is the versioned library, `LICENSE`, `ThirdPartyNotices.txt`, and the local `runtime-identity.json`.

Stop on an identity, license, size, digest, redirect, or filesystem failure. Do not execute the quarantine archive. Recovery is [acquisition-recovery.md](acquisition-recovery.md). Cleanup is [artifact-cleanup.md](artifact-cleanup.md). The architecture is [external-runtime-installation.md](../architecture/external-runtime-installation.md).
