# Bounded raw-output retention

Each corpus run seals stdout and stderr before extraction. The bytes, SHA-256 digests, lengths, truncation flags, and output-limit status are written under the external result root. The JSON record stores digests and lengths. It does not store a host path.

The files are mode `0400` after the read-back check. A later run does not receive the result root as a mount. Gold fields and evaluator records stay out of the child config. A retention failure stops the continuation. Output past the stdout or stderr limit is not given a larger file; the captured prefix is kept only when the launcher already truncated it inside the limit, and that run is `excessive-output`.

Committed templates use `not-retained` and do not contain candidate bytes. Live bytes stay in the external root. The in-process network hook is not an operating-system sandbox. The hardened fixture launcher is the bubblewrap and systemd-user-scope boundary.
