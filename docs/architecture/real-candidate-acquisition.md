# Real candidate acquisition

Track 4 does not acquire a candidate. The acquisition manifest template records `authorizationState` as `not-authorized`, `acquisitionStatus` as `not-acquired`, and `executionStatus` as `not-executed`. Expected files, observed files, and locally observed artifact digests are empty. `productionReady` remains false.

The template fixes the controls a later track would have to satisfy before any download:

- one official URL pinned to one revision
- an empty quarantine directory outside the Git work tree
- no loader import and no file execution during download
- separate expected and observed file names, sizes, and SHA-256 digests
- safetensors weights plus the named tokenizer and configuration files
- rejection of unexpected files, symlinks, executable bits, pickle headers, and `torch.load` checkpoints
- `trust_remote_code` left disabled
- a later load test that uses local paths, with network fallback and telemetry disabled
- no commit of weights and no CI upload of weights
- no redistribution

Those controls are design requirements. They are not permission to download. The current authorization is [selected-candidate-authorization.md](../provenance/selected-candidate-authorization.md). Isolation limits are in [real-candidate-isolation.md](real-candidate-isolation.md).
