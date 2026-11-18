# Schema diagnostic runbook

The manual commands are `schema-diagnostic-preflight` and `schema-diagnostic-execute`. They are not Repository Contracts steps. Validators read the committed plan, the not-approved approval, and the not-executed templates. They do not call Run.

The fresh result root is `/var/tmp/patchpilot-evals-track10a-schema`, mode `0700`. It must be empty, unlinked, and distinct from `/var/tmp/patchpilot-evals-track9a-corpus` and every earlier measurement root. The command rejects every other `--result-root`.

```text
uv run patchpilot-evals schema-diagnostic-preflight \
  --runtime-cache /var/tmp/patchpilot-evals-track8a/runtime-cache \
  --model-cache /var/tmp/patchpilot-evals-track8a/model-cache \
  --result-root /var/tmp/patchpilot-evals-track10a-schema
```

Preflight checks artifact identity, publisher-template compatibility, and the dynamic-link boundary. It does not create a model session and it does not call Run.

Execute requires `--operator-approval` equal to the plan digest `7d90e79de202949231319b2c863a2d99b5aaed4edb1d87e0cf57673cdc9bec75`. Any consumed historical digest is refused before Run:

- `8280ec639abd60edad7d49c1129d691822c17be06d7ef15aa2fcb5425bdbf0a2`
- `572fc9da2bf5c3d378a56764672617849d317df293fdbc29d85b40e70ae27d2b`
- `2133054bea8db11822cc65f6ea9c45f1ba1500f1aef67d314fbccca764155350`
- `6c4a9e6c64a3afe3c1cbb36d19985880beb067fdb9b5634752e8c4d1482560f1`

```text
uv run patchpilot-evals schema-diagnostic-execute \
  --operator-approval 7d90e79de202949231319b2c863a2d99b5aaed4edb1d87e0cf57673cdc9bec75 \
  --runtime-cache /var/tmp/patchpilot-evals-track8a/runtime-cache \
  --model-cache /var/tmp/patchpilot-evals-track8a/model-cache \
  --result-root /var/tmp/patchpilot-evals-track10a-schema
```

The six runs are serial. Each run is sealed before the next starts. A candidate-attributed schema-invalid response does not stop the later cases. An infrastructure, security, identity, telemetry, retention, or cleanup failure stops the diagnostic. There are zero retries. The profile is `linux-bwrap-systemd-v1`.

The approved execution of digest `7d90e79de202949231319b2c863a2d99b5aaed4edb1d87e0cf57673cdc9bec75` has sealed six runs in that result root. A later execute against the same nonempty root is refused as `result-root-reuse`. Do not empty the root to obtain another six runs. The measured conclusion is recorded in [track10a-schema-diagnostic-evidence.md](../provenance/track10a-schema-diagnostic-evidence.md).

The architecture note is [six-run-schema-diagnostic.md](../architecture/six-run-schema-diagnostic.md). Recovery is [schema-diagnostic-recovery.md](schema-diagnostic-recovery.md). Retention is [schema-diagnostic-retention.md](schema-diagnostic-retention.md).
