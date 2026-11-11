# Runtime staging provenance

No ONNX Runtime binary, wheel, shared library, or container image was downloaded or installed for this record. `runtimeInstalled` stays false and `installationAuthorized` stays false.

The distribution identity is the official CPU archive `onnxruntime-linux-x64-1.31.1.tgz` for `onnxruntime` tag `v1.31.1` at commit `6af1a932e2286d5c58166085d24c68783033edee`, license MIT. CUDA and GPU archives are a different distribution. The approved shared library name is `libonnxruntime.so.1.31.1`. Any other `.so` name is unapproved. This name is the versioned library identity for that tag. The archive itself was not unpacked here, so no local digest is recorded.

Official `docs/Privacy.md` at that commit says telemetry is on by default in official Linux builds. The runtime disable is `ORT_DISABLE_TELEMETRY=1` before initialization. A verified inventory requires `runtime-identity.json` to say `telemetry` is `disabled`. An enabled or unreadable telemetry configuration is rejected.

Executable classification is ELF magic and permission bits. It is not malware detection. `malwareDetectionClaimed` stays false. Verified files must not be writable. Expected and observed names, sizes, and SHA-256 values stay separate. The committed template is `not-staged` and its observed digest list is empty.

The verification command is `runtime-artifact-verification-validation`.
