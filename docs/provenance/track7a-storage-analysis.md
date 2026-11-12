# Track 7A storage analysis

This note derives the Track 7A storage figures from the committed Track 7 finalist records. It adds no new retrieval, no model bytes, and no runtime package.

The logical inventory is `4717588977` bytes across 11 selected files. The historical Track 7 footprint is `9446591609` bytes and remains `artifactFit: fail` in [finalist-artifact-budget.json](../../candidates/authorization/finalist-artifact-budget.json). The ceiling stays `8589934592`.

Track 7A adds the closed verification reservation of `1228800` bytes and keeps the published runtime-staging allowance of `11413655` bytes. Copy promotion therefore peaks at `9447820409` bytes and fails storage-only. Same-filesystem atomic rename peaks at `4730231432` bytes and passes storage-only. Cross-filesystem promotion is ineligible because the promoter has no copy fallback.

The readiness record is [track8a-storage-readiness.json](../../candidates/authorization/track8a-storage-readiness.json). Its outcome is `not-ready`. Selection stays `no-selection`. Track 8 authorization stays `not-authorized`. FP32 peak memory stays `unknown-fp32`. Explanation suitability stays `unresolved`. Locally observed artifact digests stay empty.

The model is described in [artifact-budget-model.md](../architecture/artifact-budget-model.md) and [track8a-storage-readiness.md](../architecture/track8a-storage-readiness.md).
