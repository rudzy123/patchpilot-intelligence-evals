# External runtime installation

The ONNX Runtime archive is staged outside this repository. `installationAuthorized` stays false. `pyproject.toml` and `uv.lock` do not gain a runtime dependency. The runtime is not installed into the project environment or installed globally by this repository.

The approved archive is `onnxruntime-linux-x64-1.31.1.tgz`, 11,413,655 bytes, from the `v1.31.1` release at revision `6af1a932e2286d5c58166085d24c68783033edee`. The license is MIT. `ThirdPartyNotices.txt` is required. The only regular shared library admitted to the verified root is `libonnxruntime.so.1.31.1`.

The downloaded object is the archive. After the network namespace is in place, the archive is unpacked inside the quarantine attempt. Every member is hashed. The seal checker accepts `libonnxruntime.so.1.31.1` and `onnxruntime-linux-x64-1.31.1.tgz` in addition to the Track 7A exact names `LICENSE` and `README.md`. The Track 7A storage policy array stays those two names. The verified directory is the flat set accepted by the runtime verifier:

- `libonnxruntime.so.1.31.1`
- `LICENSE`
- `ThirdPartyNotices.txt`
- `runtime-identity.json`

`runtime-identity.json` is written locally after verification with telemetry disabled. It is not an upstream member. Headers, the upstream README, and other archive members are excluded from the verified root. `libonnxruntime_providers_shared.so` is one of those excluded members. ONNX Runtime `v1.31.1` does not link it into the CPU library, so it is not required for the authorized CPU-only path. Extracted copies were deleted after that disposition. It does not remain available as a transport-attempt library. Symlinks are recorded and are not followed into the verified root. Any other regular `.so`, a missing license, a missing notice, a missing versioned library, or a size, digest, or license failure stops promotion.

Cache roots are operator arguments. They must be absolute, outside this repository, outside `patchpilot` and `neural-from-scratch`, and outside `.venv`, `build`, `dist`, and a GitHub Actions workspace. A path under `/home` or `/Users` is rejected. The runtime root and the model root are distinct. Quarantine, verified, rejected, and output directories are distinct. Promotion stays on one filesystem.

The reservation formula is 4,998,666,888 bytes. That is the selected inventory, the runtime archive, 1,228,800 bytes of verification overhead, and a 256 MiB unpack allowance. The candidate-artifact filesystem must also have at least 6,442,450,944 available bytes. The logical artifact ceiling stays 8,589,934,592 bytes. Promotion does not reserve a second full copy because the rename does not copy. Unpack above the allowance stops before promotion. Absolute cache roots are not written into the plan.

The provenance for the pinned release is [runtime-staging-provenance.md](../provenance/runtime-staging-provenance.md). The acquisition plan is [controlled-artifact-acquisition.md](controlled-artifact-acquisition.md).
