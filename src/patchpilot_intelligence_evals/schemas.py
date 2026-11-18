"""Load and validate the closed JSON Schemas. Validation does not fetch URLs."""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

SCHEMA_NAMES: tuple[str, ...] = (
    "finding-explanation-input",
    "finding-explanation-output",
    "evaluation-case",
    "evaluation-result",
    "experiment-manifest",
)

SCHEMA_IDS: tuple[str, ...] = tuple(
    f"urn:patchpilot-intelligence-evals:schema:{name}:v1" for name in SCHEMA_NAMES
)

# Track 3 documents. They stay out of SCHEMA_IDS so baseline manifests remain the five
# Track 2 identifiers.
CANDIDATE_SCHEMA_NAMES: tuple[str, ...] = (
    "candidate-manifest",
    "candidate-request",
    "candidate-response",
    "candidate-execution-result",
    "comparison-result",
    "calibration-record",
)

# Track 4 authorization documents. They stay out of SCHEMA_IDS and out of the
# candidate protocol identifiers so Track 2 manifests and Track 3 fixtures
# keep their closed vocabularies.
AUTHORIZATION_SCHEMA_NAMES: tuple[str, ...] = (
    "candidate-shortlist",
    "real-candidate-authorization",
    "evaluation-hardware-profile",
    "candidate-acquisition-manifest",
    "real-candidate-experiment-plan",
)

# Track 5 real-candidate boundary documents. They stay outside Track 2, Track 3,
# and Track 4 identifiers. Names are appended as each closed schema is added.
TRACK5_SCHEMA_NAMES: tuple[str, ...] = (
    "offline-local-model-manifest",
    "external-artifact-cache-policy",
    "model-artifact-verification",
    "runtime-assessment",
    "runtime-authorization",
    "real-candidate-isolation-profile",
    "candidate-evidence-closure",
    "track6-acquisition-authorization",
    "track5-implementation-review",
)

# Track 6A hardened-execution documents. They stay outside earlier schema groups.
TRACK6A_SCHEMA_NAMES: tuple[str, ...] = (
    "sandbox-capability-report",
    "hardened-execution-profile",
    "hardened-execution-attestation",
    "runtime-security-assessment",
    "runtime-authorization-v2",
    "track6b-readiness",
    "track6a-implementation-review",
)

# Track 6B runtime-staging documents. They stay outside earlier schema groups.
TRACK6B_SCHEMA_NAMES: tuple[str, ...] = (
    "external-runtime-cache-policy",
    "runtime-artifact-verification",
    "runtime-adapter-contract",
    "candidate-format-resolution",
    "onnx-conversion-plan",
    "track6c-readiness",
)

# Track 6C candidate-eligibility documents. They stay outside earlier schema groups.
TRACK6C_SCHEMA_NAMES: tuple[str, ...] = (
    "candidate-eligibility-closure",
    "tokenizer-eligibility",
    "direct-onnx-artifact",
    "candidate-artifact-budget",
    "bounded-subprocess-compatibility",
    "track6d-acquisition-readiness",
)

# Track 7 candidate-landscape documents. They stay outside earlier schema groups.
TRACK7_SCHEMA_NAMES: tuple[str, ...] = (
    "candidate-discovery",
    "finalist-eligibility",
    "finalist-tokenizer",
    "finalist-direct-onnx",
    "finalist-artifact-budget",
    "finalist-explanation-suitability",
    "track7-selection",
    "track8-acquisition-authorization",
    "track7-implementation-review",
)

# Track 7A storage-safety documents. They stay outside earlier schema groups.
TRACK7A_SCHEMA_NAMES: tuple[str, ...] = (
    "artifact-storage-policy",
    "artifact-verification-seal",
    "artifact-promotion-attempt",
    "artifact-promotion-receipt",
    "artifact-recovery-decision",
    "artifact-budget-recalculation",
    "track8a-storage-readiness",
    "track7a-implementation-review",
)

# Track 7B memory and suitability documents. They stay outside earlier schema groups.
TRACK7B_SCHEMA_NAMES: tuple[str, ...] = (
    "candidate-memory-model",
    "candidate-memory-evidence",
    "candidate-memory-budget",
    "explanation-suitability-contract",
    "explanation-suitability-evidence",
    "controlled-measurement-authorization",
    "track8b-readiness",
    "track7b-implementation-review",
)

# Track 8A acquisition documents. They stay outside earlier schema groups.
TRACK8A_SCHEMA_NAMES: tuple[str, ...] = (
    "acquisition-plan",
    "acquisition-allowlist",
    "acquired-runtime-manifest",
    "acquired-candidate-manifest",
    "local-artifact-digests",
    "hardened-load-attestation",
    "acquisition-closeout",
    "track8a-acquisition-evidence",
    "track8a-implementation-review",
    "track8b-measurement-prerequisites",
)

# Track 8B measurement documents. They stay outside earlier schema groups.
TRACK8B_SCHEMA_NAMES: tuple[str, ...] = (
    "measurement-plan",
    "measurement-operator-approval",
    "measurement-preflight",
    "smoke-execution",
    "context-memory-measurement",
    "candidate-behavioral-run",
    "candidate-behavioral-summary",
    "measurement-closeout",
    "track8b-stopped-attempt",
    "track8b-plan-disposition",
    "track8b-template-compatibility-defect",
    "track8b-implementation-review",
    "track9-readiness",
)

# Track 8B-R1 retry documents. They stay outside the consumed Track 8B group.
TRACK8B_R1_SCHEMA_NAMES: tuple[str, ...] = (
    "measurement-retry-plan",
    "measurement-retry-approval",
    "measurement-retry-preflight",
    "template-compatibility-result",
    "retry-smoke-execution",
    "retry-context-memory",
    "retry-behavioral-run",
    "retry-closeout",
    "retry-track9-readiness",
    "track8b-r1-stopped-attempt",
    "track8b-r1-dependency-mount-defect",
    "track8b-r1-memory-conclusion-defect",
    "track8b-r1-corrected-closeout",
    "track8b-r1-plan-disposition",
    "track8b-r1-implementation-review",
)

# Track 8B-R2 inference retry documents. They stay outside both consumed plans.
TRACK8B_R2_SCHEMA_NAMES: tuple[str, ...] = (
    "inference-retry-plan",
    "inference-retry-approval",
    "inference-retry-preflight",
    "dynamic-link-precheck",
    "inference-retry-smoke",
    "inference-retry-context-memory",
    "inference-retry-behavioral-run",
    "inference-retry-closeout",
    "inference-retry-track9-readiness",
    "inference-retry-unclassified-launch",
    "track8b-r2-stopped-attempt",
    "track8b-r2-cgroup-sampling-defect",
    "track8b-r2-schema-forensics",
    "track8b-r2-behavioral-interpretation",
    "track8b-r2-memory-conclusion",
    "track8b-r2-plan-disposition",
    "track8b-r2-proportionality-review",
    "track8b-r2-implementation-review",
)

# Track 9 evidence-review documents. They do not authorize execution.
TRACK9_SCHEMA_NAMES: tuple[str, ...] = (
    "evaluation-evidence-inventory",
    "memory-evidence-review",
    "behavioral-evidence-review",
    "proportionality-decision",
    "corpus-continuation-authorization",
    "candidate-disposition",
    "track9-implementation-review",
)

# Track 9A corpus-continuation documents. Validators do not call Run.
TRACK9A_SCHEMA_NAMES: tuple[str, ...] = (
    "corpus-continuation-plan",
    "corpus-continuation-approval",
    "corpus-continuation-preflight",
    "bounded-raw-output",
    "run-diagnostics",
    "corpus-continuation-run",
    "corpus-continuation-summary",
    "corpus-continuation-closeout",
    "track10-readiness",
    "track9a-stopped-attempt",
    "track9a-telemetry-finalization-defect",
    "track9a-schema-forensics",
    "track9a-corrected-interpretation",
    "track9a-plan-disposition",
    "track9a-proportionality-review",
    "track9a-track10-not-ready",
    "track9a-implementation-review",
)

# Track 10 disposition documents. Validators do not call Run.
TRACK10_SCHEMA_NAMES: tuple[str, ...] = (
    "attributed-response-evidence",
    "schema-invariant-review",
    "diagnostic-proportionality",
    "six-run-diagnostic-authorization",
    "investment-stop-decision",
    "track10-candidate-disposition",
    "track10-implementation-review",
)

# Track 10A diagnostic documents. Validators do not call Run.
TRACK10A_SCHEMA_NAMES: tuple[str, ...] = (
    "schema-diagnostic-plan",
    "schema-diagnostic-approval",
    "schema-diagnostic-preflight",
    "schema-diagnostic-run",
    "schema-diagnostic-summary",
    "schema-diagnostic-closeout",
    "track11-readiness",
    "track10a-implementation-review",
)

_ALL_SCHEMA_NAMES: tuple[str, ...] = (
    SCHEMA_NAMES
    + CANDIDATE_SCHEMA_NAMES
    + AUTHORIZATION_SCHEMA_NAMES
    + TRACK5_SCHEMA_NAMES
    + TRACK6A_SCHEMA_NAMES
    + TRACK6B_SCHEMA_NAMES
    + TRACK6C_SCHEMA_NAMES
    + TRACK7_SCHEMA_NAMES
    + TRACK7A_SCHEMA_NAMES
    + TRACK7B_SCHEMA_NAMES
    + TRACK8A_SCHEMA_NAMES
    + TRACK8B_SCHEMA_NAMES
    + TRACK8B_R1_SCHEMA_NAMES
    + TRACK8B_R2_SCHEMA_NAMES
    + TRACK9_SCHEMA_NAMES
    + TRACK9A_SCHEMA_NAMES
    + TRACK10_SCHEMA_NAMES
    + TRACK10A_SCHEMA_NAMES
)


class SchemaValidationError(Exception):
    """A document failed a closed schema. The message omits document values."""

    def __init__(self, schema_name: str) -> None:
        super().__init__(f"schema validation failed for {schema_name}")
        self.schema_name = schema_name


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def schema_path(schema_name: str) -> Path:
    known = _ALL_SCHEMA_NAMES
    if schema_name not in known:
        raise KeyError(schema_name)
    return repo_root() / "schemas" / f"{schema_name}.schema.json"


@cache
def load_schema(schema_name: str) -> dict[str, Any]:
    raw = schema_path(schema_name).read_text(encoding="utf-8")
    loaded = cast(dict[str, Any], json.loads(raw))
    Draft202012Validator.check_schema(loaded)
    return loaded


@cache
def validator(schema_name: str) -> Draft202012Validator:
    return Draft202012Validator(load_schema(schema_name))


def error_paths(schema_name: str, instance: object) -> list[str]:
    paths: list[str] = []
    for error in validator(schema_name).iter_errors(instance):
        paths.append("/" + "/".join(str(part) for part in error.path))
    return sorted(paths)


def validate(schema_name: str, instance: object) -> None:
    if error_paths(schema_name, instance):
        raise SchemaValidationError(schema_name)


def assert_schemas_closed() -> None:
    for name in _ALL_SCHEMA_NAMES:
        document = load_schema(name)
        if document.get("additionalProperties") is not False:
            raise SchemaError(f"{name} is not closed")
        if document.get("$id") != f"urn:patchpilot-intelligence-evals:schema:{name}:v1":
            raise SchemaError(f"{name} identifier drifted")
