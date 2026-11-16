# Acquisition recovery

A failed transfer stays fail closed.

- Timeout or connection reset deletes the incomplete payload. A later retry, at most two, uses a new attempt id.
- An unauthorized redirect, HTTP error, size mismatch, digest mismatch, or identity mismatch is not retried. The payload from a rejected identity stays available for inspection until cleanup, and it is not executed.
- A promotion failure moves the attempt to the rejected directory and writes a reason code. The reason record does not store a host path or a credential.
- A partial unpack that exceeds the 256 MiB allowance stops before promotion.
- Missing bubblewrap during hashing or during the offline load proof stops the session. The in-process network hook is not a substitute.

Do not copy a quarantine directory into this repository. Do not promote with a userspace copy. The supported promotion is the no-replace rename in [atomic-artifact-promotion.md](../architecture/atomic-artifact-promotion.md). Cleanup of an incomplete attempt is [artifact-cleanup.md](artifact-cleanup.md).
