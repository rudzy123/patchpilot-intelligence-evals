# Artifact cleanup

Cleanup stays inside the operator-supplied cache root. It does not delete a verified attempt. A rejected attempt keeps `rejection.json` and deletes the payload. A quarantine attempt can be deleted, including by a second call that finds the attempt already gone.

`candidates/local-records/` is gitignored. Redacted acquisition evidence may be committed when it contains no host path, address, or credential. The Track 8A evidence and implementation review are those records. They are [track8a-acquisition-evidence.json](../../candidates/authorization/track8a-acquisition-evidence.json) and [track8a-implementation-review.json](../../candidates/authorization/track8a-implementation-review.json).

Closeout records `storageReclaimedBytes` as a count. The committed closeout template is not closed, has reclaimed zero bytes, and has `gitTrackedArtifact` false. The observed closeout reclaimed 31,938,441 payload bytes and is recorded in the evidence document. No model or runtime blob is committed.

The closeout command reads that template. It does not transfer and it does not delete a verified root.
