# Run failure attribution

A failed run has one failure authority: `candidate-output`, `adapter`, `protocol`, `evaluator`, `measurement-infrastructure`, `security-boundary`, or `unresolved`. A successful run has none.

Raw bytes, the extracted envelope, the parse result, and the schema result stay distinct. A later failure does not delete an earlier stage. `candidate-output` is used for a malformed or schema-invalid response only when the raw output was retained, extraction and parse behavior are known, schema errors are recorded, and the adapter did not fall back, truncate, or leave trailing bytes. Otherwise the authority is `adapter` or `unresolved`.

Network violation, gold visibility, and isolation failure are `security-boundary`. Memory, telemetry, cleanup, identity, and retention failures are `measurement-infrastructure` unless the pinned stop list classifies the exit as `protocol`. `excessive-output` is `protocol` when the bounded bytes were retained, and it stops later runs. A candidate-attributed malformed response is a measured result and does not by itself stop the next case.

An unsealable launch that still has child output writes `recordKind` `unclassified-launch` and stops. The raw file from the retention step remains.
