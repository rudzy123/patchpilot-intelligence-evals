# External runtime staging

The authorized runtime identity is `onnxruntime` `v1.31.1` at `6af1a932e2286d5c58166085d24c68783033edee`. Authorization is not installation. This boundary records how a future CPU archive named `onnxruntime-linux-x64-1.31.1.tgz` would be staged. No archive, wheel, shared library, or container image is present.

The staging root is an argument to the checker. The committed policy records rules only. It does not record a host path, a user name, or a host name. The root must be absolute, must stay outside this repository, and must stay outside sibling paths named `patchpilot` and `neural-from-scratch`. Those sibling prefixes are compared as paths. Their contents are not listed. A symlink root, a `..` segment, or a root whose device or inode changes during the check is rejected. The root must also stay distinct from the model-artifact cache and from the output directory.

Attempts use three directories under that root: `quarantine`, `verified`, and `rejected`. Quarantine and rejected attempts cannot be executed. Promotion copies an attempt to `verified` only after the inventory check returns `verified`. A rejected attempt id stays rejected. Cleanup deletes rejected payload files and keeps `rejection.json`.

Git does not track an in-repository `runtime-cache/` directory. CI does not upload a runtime cache. Tests use temporary synthetic bytes. The checks are not an operating-system sandbox.

The policy command is `external-runtime-cache-policy-validation`. Inventory rules sit in [runtime-staging-provenance.md](../provenance/runtime-staging-provenance.md).
