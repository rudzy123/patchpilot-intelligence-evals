# Artifact cache recovery

Recovery classifies one attempt as `resumable-quarantine`, `rejected`, `verified`, or `indeterminate`. A verified result requires the seal, the inventory identity, and a consistent journal together. The directory name is not proof.

Interruption points cover the hash, the seal, the rename, the verified-parent sync, and the receipt, together with an inconsistent journal and a modified inventory. A crash after rename is explicit proof when the journal already says `promoting` and the seal still matches. A sealed journal found under the verified path stays `indeterminate`.

A mutated verified tree keeps the original seal bytes, loses execution eligibility, and recovers as `indeterminate` with operator review required. The same content change inside quarantine is `rejected` with `changed-after-seal`. Indeterminate results stay idempotent. A second classification of an unchanged tree returns the same decision.

Cleanup is explicit. It walks with `lstat`, refuses links, special files, and anything outside the cache root, and refuses a verified attempt. Rejected cleanup keeps `rejection.json`. A partial delete fails closed and reports the logical bytes already reclaimed. A second call on an empty quarantine or a rejection record that has already been reduced is `already-clean`. There is no background deletion.

Link and name checks reject absolute paths, `..`, non-UTF-8 names, casefold collisions, duplicate normalized paths, symlinks, dangling links, a link count other than 1, a repeated inode, FIFOs, sockets, and device files. The seal rules live in [atomic-artifact-promotion.md](atomic-artifact-promotion.md).
