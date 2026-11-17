# Corpus continuation runbook

Validators read committed records and do not call Run:

- `corpus-continuation-plan-validation`
- `corpus-continuation-approval-validation`
- `corpus-continuation-preflight-validation`
- `bounded-raw-output-validation`
- `run-diagnostics-validation`
- `corpus-continuation-run-validation`
- `corpus-continuation-summary-validation`
- `corpus-continuation-closeout-validation`
- `track10-readiness-validation`
- `track9a-stopped-attempt-validation`
- `track9a-telemetry-finalization-defect-validation`
- `track9a-schema-forensics-validation`
- `track9a-corrected-interpretation-validation`
- `track9a-plan-disposition-validation`
- `track9a-proportionality-review-validation`
- `track9a-track10-not-ready-validation`
- `track9a-implementation-review-validation`

Manual commands stay out of CI:

```text
uv run patchpilot-evals corpus-continuation-preflight \
  --runtime-cache /var/tmp/patchpilot-evals-track8a/runtime-cache \
  --model-cache /var/tmp/patchpilot-evals-track8a/model-cache \
  --result-root /var/tmp/patchpilot-evals-track9a-corpus

uv run patchpilot-evals corpus-continuation-execute \
  --operator-approval <plan-digest> \
  --runtime-cache /var/tmp/patchpilot-evals-track8a/runtime-cache \
  --model-cache /var/tmp/patchpilot-evals-track8a/model-cache \
  --result-root /var/tmp/patchpilot-evals-track9a-corpus
```

The Track 9A plan digest `6c4a9e6c64a3afe3c1cbb36d19985880beb067fdb9b5634752e8c4d1482560f1` is consumed and non-reusable. No replacement corpus plan digest is issued. Execute refuses that digest before Run. The external result root is the immutable stopped attempt and must not be rewritten or replaced. The committed approval record stays `not-approved`. Execute also refuses the three historical consumed plan digests.

Preflight may recompute artifact identity, template compatibility, and the dynamic-link check. Those checks do not call Run. The stopped attempt did not rerun the memory phases. Another corpus execution requires a new plan and a new operator checkpoint. This correction does not create either.
