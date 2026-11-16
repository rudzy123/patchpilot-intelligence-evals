# Track 8B-R1 measurement evidence

Retry evidence is a separate record from the Track 8B measurement evidence in [track8b-measurement-evidence.md](track8b-measurement-evidence.md). The consumed plan digest remains `8280ec639abd60edad7d49c1129d691822c17be06d7ef15aa2fcb5425bdbf0a2`. The retry plan digest is `572fc9da2bf5c3d378a56764672617849d317df293fdbc29d85b40e70ae27d2b`. The historical disposition stays `consumed`, `reusable: false`, and `replacementPlanDigest: not-issued`.

The committed retry plan file stays `executionStatus: not-executed`. The committed retry approval stays `approvalStatus: not-approved`. The retry plan disposition is `consumed`, `reusable: false`, and `replacementPlanDigest: not-issued`. `measurementPerformed` stays false on the committed records. `realModelExecuted` stays false on those committed records. `measurementAuthorization` stays `not-authorized`.

The stopped attempt is accepted as fail-closed infrastructure evidence. Its outcome is `stopped`, its failure category is `inference-failure`, and its failure authority is measurement infrastructure. Run was not invoked. No model session was created. Short generation, the 4,096-token phase, and the 8,192-token phase stayed withheld. Corpus evaluation did not start. Candidate metrics were not produced. The corrected closeout interpretation is `unavailable`. The observed smoke-scope peak remains smoke evidence and does not establish context-memory eligibility. Track 9 stays `not-ready`.

Observed phase files from a retry stay in a fresh external result root of class `measurement-retry-result`. Validators do not copy that root into this repository. The historical result root `/var/tmp/patchpilot-evals-track8b-approved-8280ec63` stays untouched.

The verified publisher template digest is `f05bf4b967dc993bdc7a2fe6e43759ee218eb0eb340d68b063e1c4f8ad148176`. The synthetic compatibility output digest is `5c61ee0b595fa4c5b295feb233b312c38b779f7840f3f39c82aef51da9061e5d`. That proof does not create a session and does not call Run.

`installationAuthorized` stays false. `selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `comparisonWinner` stays null. `productionReady` stays false. The committed retry Track 9 records stay `not-ready`. Their verdict stays advisory. Another real execution requires a new Session or explicitly reviewed retry authority, a new plan digest, a fresh empty result root, and a new operator checkpoint.
