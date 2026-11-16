# Hardened offline load proof

The load proof runs only after a verified runtime and a verified candidate exist. It uses the `linux-bwrap-systemd-v1` profile through the hardened launcher. Bubblewrap supplies the network namespace. That namespace is the offline control. The in-process network hook is not an operating-system sandbox. Seccomp, Podman, Docker, `unshare`, and direct cgroup delegation are not described as enforced here.

The proof mounts the verified runtime and the verified model read-only. It does not copy the model into the repository. The child loads `libonnxruntime.so.1.31.1` by its absolute sandbox path, creates an environment, disables telemetry, creates a session, and reads input and output counts. It parses `tokenizer.json` locally and requires a vocabulary object. It does not call session Run. It does not import an `onnxruntime` or `tokenizers` distribution. It does not run the 24-case corpus or a 4,096-token or 8,192-token measurement.

`realModelExecuted` stays false. A separate attestation field records the offline load. `inferencePerformed` and `generationPerformed` stay false. `measurementPerformed` stays false.

The committed hardened profile keeps the synthetic 256 MiB resident limit and the 2 GiB address-space limit. This invocation alone sets both the cgroup `MemoryMax` and `RLIMIT_AS` to the existing 12 GiB ceiling, 12,884,901,888 bytes, so the FP32 graph can be mapped. `RLIMIT_AS` is address space. `MemoryMax` is the resident-memory control. The ceiling is not raised. Crossing it, or failing to reap the process tree, stops the session.

The attestation template stays `not-performed`. The 2026-11-16 observed load is recorded in [track8a-acquisition-evidence.md](../provenance/track8a-acquisition-evidence.md). That observation did not call session Run. The boundary is [hardened-execution.md](hardened-execution.md). The prerequisite record is [track8b-measurement-prerequisites.md](track8b-measurement-prerequisites.md).
