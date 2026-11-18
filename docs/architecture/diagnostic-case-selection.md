# Diagnostic case selection

The selection rule is `minimum-case-id-within-committed-category`. It uses the committed corpus categories in evaluator order and the lexical minimum `caseId` inside each category. The same rule is the Track 10 review oracle. Track 10A writes the result into the diagnostic plan. The Track 10 authorization record keeps `operationalCaseIds` at `not-selected`.

The six selections are:

- `grounding-citation`: `case-ground-001`
- `insufficient-evidence-refusal`: `case-refuse-001`
- `prompt-injection`: `case-inject-001`
- `cross-tenant-negative-control`: `case-tenant-001`
- `contradiction`: `case-contra-001`
- `stale-unavailable-incomparable`: `case-stale-001`

Each case has repetition `1` and run id `{caseId}-r1`. There are six runs and zero retries. The new `case-ground-001-r1` is a new run under the Track 10A plan digest. It does not read or replace the Track 9A run of the same name.

Gold, evaluator fields, and hidden case metadata stay off the candidate input. A missing category, a duplicate case, or any count other than six is rejected.
