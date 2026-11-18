# Schema diagnostic retention

Each sealed run keeps raw stdout and stderr before extraction. The external layout is `runs/<runId>/stdout.bin`, `stderr.bin`, and `run.json`. `extracted.bin` is added when the envelope contains an explanation object. Files are owner-read-only after sealing.

The run record keeps raw digests, extraction status, parse status, schema status, evidence-id paths, and the attribution booleans as separate fields. A later diagnostic failure does not erase the raw files. If sealing cannot finish after bytes were retained, the run record is `unclassified-launch` and the raw files stay.

Committed records do not contain explanation text, gold, absolute result paths, or host identity. Live bytes remain outside the repository. One run's output is not mounted into a later run.

Stdout is limited to 65,536 bytes and stderr to 16,384 bytes. Output past either limit stops the diagnostic and is not counted as a candidate-output schema failure.

The threshold is [systematic-schema-failure.md](../architecture/systematic-schema-failure.md).
