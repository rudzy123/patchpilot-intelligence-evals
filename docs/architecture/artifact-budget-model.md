# Artifact budget model

Track 7A compares each promotion model with the unchanged artifact ceiling of `8589934592` bytes. The comparison uses that model's peak logical-byte reservation. Equality passes. One byte over fails.

Logical size is `st_size` from Linux `stat(2)` and `inode(7)`. Allocated size is `st_blocks * 512`. Allocated blocks, sparse allocation, and compressed transport size leave the reservation unchanged. Hash buffers stay in process memory and contribute `0` disk bytes. Transient acquisition overhead stays `null`. Supplying an acquisition size yields `unresolved`.

The integer domain is `0` through `2**63 - 1`. Booleans, non-integers, negative values, and sums outside that domain fail as `integer-overflow`.

The closed reservations for the 11 selected finalist files are a 65536-byte journal, a 1048576-byte temporary manifest, a 65536-byte receipt, `4096 * 12` bytes of directory metadata, and the published runtime-staging allowance of `11413655` bytes. Together the verification working overhead is `1228800` bytes. The runtime allowance is the published package size already recorded by Track 7.

The peaks are:

| Model | Peak logical bytes | Storage-only result |
| --- | ---: | --- |
| Copy promotion | 9447820409 | `fail`, 857885817 bytes over the ceiling |
| Same-filesystem atomic rename | 4730231432 | `pass` when the atomic contract holds, 3859703160 bytes under the ceiling |
| Cross-filesystem promotion | none | `ineligible` |

The Track 7 record in [finalist-artifact-budget.json](../../candidates/authorization/finalist-artifact-budget.json) stays the historical copy footprint: logical inventory `4717588977`, footprint `9446591609`, and `artifactFit: fail`. A Model B storage pass leaves FP32 peak memory `unknown-fp32`, explanation suitability `unresolved`, `weightedScore` null, `qualifyingCandidateCount` 0, `selectionOutcome` `no-selection`, and Track 8 `authorizationOutcome` `not-authorized`.

The policy command is `artifact-storage-policy-validation`. Promotion semantics are in [atomic-artifact-promotion.md](atomic-artifact-promotion.md). The readiness record is in [track8a-storage-readiness.md](track8a-storage-readiness.md).
