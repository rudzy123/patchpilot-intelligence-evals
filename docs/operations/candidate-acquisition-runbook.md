# Candidate acquisition runbook

Candidate transfer starts only after a runtime promotion receipt exists and the operator has approved the same plan digest used for the runtime. The 2026-11-16 review records one completed candidate promotion. This runbook does not itself transfer a file.

The selected inventory is the eleven files in the acquisition plan. FP16 and Q4 files are unselected and are not transferred. The license text must contain the LFM Open License name. The selected inventory has no separate notice file.

1. Confirm the runtime verified root contains a promotion receipt.
2. Run `uv run patchpilot-evals acquire-candidate --runtime-cache <runtime-root> --model-cache <model-root> --operator-approval <planDigest>`.
3. Each file uses its own attempt budget of 45 minutes. A redirect is followed only when it preserves the artifact and the next host is the origin or a delivery host scoped to that artifact in this plan. Any other host stops the transfer with no body saved.
4. After the network namespace is in place, every selected file is hashed locally. A published digest must match. A file without a published digest still requires a local digest, the listed size, and a selected path.
5. Promotion renames that quarantine directory. A path outside the eleven files stops promotion.

The command does not run the corpus, does not generate tokens, and does not set `measurementPerformed`. The load proof is a separate command described in [hardened-offline-load-proof.md](../architecture/hardened-offline-load-proof.md).
