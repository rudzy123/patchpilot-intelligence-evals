# External artifact cache

Real-candidate bytes stay outside this Git repository. The cache root is an argument to the checker. The committed policy records rules only. It does not record a host path, a user name, or a host name.

The root is rejected when it is relative, contains `..`, sits inside this repository, or sits inside a sibling path named `patchpilot` or `neural-from-scratch`. Those sibling prefixes are compared as paths. Their contents are not listed. A root that is a symlink is rejected. A root whose device or inode changes during the check is rejected.

Attempts use three directories under that root: `quarantine`, `verified`, and `rejected`. Quarantine cannot be executed, and it cannot load a tokenizer or a model. Promotion copies an attempt to `verified` only after the inventory check returns `verified`. A rejected attempt id stays rejected until a different attempt id is submitted. Cleanup deletes rejected payload files and keeps `rejection.json`. Reason records contain reason codes, not file bytes.

Git does not track an in-repository `artifact-cache/` directory or weight and tokenizer file names. CI does not upload a cache. No persistent model cache is created by the tests. The checks are not an operating-system sandbox.

The policy command is `artifact-cache-policy-validation`. The state rules sit beside [model-artifact-verification.md](model-artifact-verification.md) and [real-candidate-boundary.md](real-candidate-boundary.md).
