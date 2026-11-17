# Raw-output retention operations

Retain stdout and stderr before parsing. Seal the bytes, record the SHA-256 and length, then extract. Extraction reads the sealed bytes and does not replace them.

The external layout for one run is `runs/<runId>/stdout.bin`, `stderr.bin`, `raw-output.json`, `diagnostics.json`, and `run.json`. `extracted.bin` is added when the envelope contains an explanation object. Files are owner-read-only after sealing. The result root is not mounted into a later candidate.

Committed records do not contain candidate explanation text or absolute result paths. Live bytes remain outside the repository. A missing adapter side file does not change the protocol envelope on stdout. It leaves candidate-output attribution unresolved when the side file is required to separate an adapter rewrite from candidate text.

Do not log assistance-request text or explanation bodies. `RLIMIT_AS` is address space. Cgroup `MemoryMax` is the resident-memory control.
