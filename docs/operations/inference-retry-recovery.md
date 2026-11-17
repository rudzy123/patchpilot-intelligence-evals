# Inference retry recovery

Stop when a promoted digest differs, the dynamic-link precheck fails, a dependency is unverified, the result root is reused, telemetry is unresolved, resident memory exceeds the ceiling, an out-of-memory event is recorded, network reachability or isolation fails, output exceeds its limit, cleanup fails, gold is visible, or a prerequisite phase fails.

The consumed digests `8280ec639abd60edad7d49c1129d691822c17be06d7ef15aa2fcb5425bdbf0a2` and `572fc9da2bf5c3d378a56764672617849d317df293fdbc29d85b40e70ae27d2b` cannot authorize another Run. `replacementPlanDigest` stays `not-issued` on those records. Historical result roots stay untouched.

An infrastructure stop sets `proportionalityRecommendation` to `review-required`. That record does not authorize another retry. `furtherRetryAssumed` stays false. Selection stays `no-selection`. Calibration stays `not-approved`. `productionReady` stays false.

Cleanup reaps the systemd user scope and the process group. A cleanup failure withholds later phases.
