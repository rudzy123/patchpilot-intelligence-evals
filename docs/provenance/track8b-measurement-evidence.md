# Track 8B measurement evidence

Measurement evidence is a separate record from the Track 8A acquisition evidence. The committed plan, operator approval, templates, and Track 9 recommendation describe the session boundary. `executionStatus` stays `not-executed` on the plan file. `approvalStatus` stays `not-approved`. `measurementPerformed` stays false on those committed records. `realModelExecuted` stays false on those committed records.

The 2026-11-16 attempt stopped with `tokenizer-failure` before Run. The approved plan digest is consumed and is not reusable. Another Run requires a new plan and a new operator approval. No replacement plan digest is issued by this correction. The stopped attempt, observed closeout, template-compatibility defect, and prepared review are committed records. They do not copy the external result root.

Observed phase files from that attempt stay in the external result root. Validators do not rewrite them. The historical preflight omitted `calibrationStatus`. Calibration remained `not-approved` in every authority-bearing record, and no calibration decision changed. Future preflight records include `calibrationStatus`.

Historical `candidates/authorization/track8b-measurement-prerequisites.json` stays `measurementAuthorization: not-authorized`. The 2026-11-12 readiness record is not permission to run. The 2026-11-16 Track 8A review does not authorize measurement.

`installationAuthorized` stays false. `selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `productionReady` stays false. Track 9 readiness stays `not-ready`.
