# ONNX conversion boundary

Conversion authorization, runtime installation, and model execution are separate decisions. This session authorizes none of them. The toolchain evidence is in [conversion-toolchain-evidence.md](../provenance/conversion-toolchain-evidence.md).

Equivalence uses the decimal comparison `abs(a - b) <= atol + rtol * abs(b)`. The harness thresholds are absolute `0.0001` and relative `0.001`. Those are harness thresholds, not a publisher guarantee. Compared vectors must have equal length. A non-finite value fails. Source and converted digests stay distinct. Converted provenance is `locally-converted`, and converted output is not publisher-provided.

Opset, precision, axes, and external-data layout stay unresolved because no assessed pin fixes them. Determinism is recorded as variation that a later session must characterize before any conversion runs. No conversion was run. The numeric tests use synthetic decimals only.

`authorizationOutcome` is `not-authorized`. `conversionStatus` is `not-performed`. `equivalenceMeasured` is false. `offlineClosed` is false. `realModelExecuted` and `productionReady` stay false.

The command is `onnx-conversion-plan-validation`.
