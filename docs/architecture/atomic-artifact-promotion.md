# Atomic artifact promotion

Track 7A promotes a sealed quarantine directory by renaming it on the same filesystem. Linux `rename(2)` makes a same-filesystem directory rename atomic. A different mount returns `EXDEV`. `renameat2` with `RENAME_NOREPLACE` (flag value 1) fails with `EEXIST` when the destination exists. A filesystem that rejects the flag fails the promotion as `filesystem-capability-unsupported`.

Linux `fsync(2)` persists file data and does not persist the directory entry. The parent directory is synced separately. Python `os.lstat` does not follow links. `O_NOFOLLOW` rejects a final symlink. Records store `sameFilesystem: true` after a device comparison. They omit the host path, the device number, the hostname, and the address.

Promotion order:

1. Validate both parents with the cache-root rules: absolute, no `..`, outside this repository, and outside a sibling prefix named `patchpilot` or `neural-from-scratch`.
2. Require equal device identity for the source, the cache root, and the verified parent.
3. Require a sealed manifest and unchanged post-seal metadata.
4. Require the verified destination to be absent.
5. Sync every artifact file opened `O_RDONLY | O_NOFOLLOW`, then the sealed manifest, then the quarantine directory.
6. `renameat2` the attempt directory with `RENAME_NOREPLACE`.
7. Sync the verified parent.
8. Write the receipt beside the attempt, then sync that parent again.

The receipt path is `verified/<attempt-id>.promotion-receipt.json`. It stays outside the sealed file set. A sync or rename failure before the rename leaves the attempt sealed and unmoved. A parent-sync failure after a successful rename leaves the attempt `indeterminate`. The tree is not copied back, and the call does not report success.

The authorized edges are `quarantine-open` to `quarantine-closed`, `quarantine-closed` to `verifying`, `verifying` to `sealed` or `rejected`, `sealed` to `promoting` or `rejected`, `promoting` to `verified` or `indeterminate`, and `indeterminate` to `rejected` or, with explicit recovery proof, `verified`. Direct edges from quarantine or verifying to verified, from rejected to verified, and from verified to rejected by silent mutation are absent. Execution stays prohibited in every state.

The Track 5 copy promoter remains available to its existing tests. The Track 7A promoter does not call it. Cross-filesystem promotion has no copy-and-delete fallback. The budget numbers are in [artifact-budget-model.md](artifact-budget-model.md). Crash classes are in [artifact-cache-recovery.md](artifact-cache-recovery.md).
