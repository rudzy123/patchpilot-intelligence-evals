# Track 6 acquisition boundary

Track 6 may be authorized only when every prerequisite passes: one qualifying candidate, one authorized runtime, cache and verification, isolation with no acquisition blocker, hardware inside the Track 4 envelope, an immutable revision and source, resolved tokenizer provenance, resolved weight license and commercial use, redistribution that is unnecessary, and no gate change.

The committed decision is [track6-acquisition-authorization.json](../../candidates/authorization/track6-acquisition-authorization.json). It is `not-authorized`. No pinned candidate passes every mandatory criterion, the runtime decision is no-runtime, and the isolation profile still has acquisition blockers. Cache validation, artifact verification, hardware fit, and unchanged fixture gates are present, and they do not authorize acquisition by themselves.

An in-memory example can validate an authorized decision. That example is not a selection. Authorization still leaves acquisition at `not-acquired`, execution at `not-executed`, local digests empty, and `productionReady` false. This record does not download a model, install a runtime, or execute inference.
