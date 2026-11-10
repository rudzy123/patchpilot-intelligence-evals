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


class SchemaValidationError(Exception):
    """A document failed a closed schema. The message omits document values."""

    def __init__(self, schema_name: str) -> None:
        super().__init__(f"schema validation failed for {schema_name}")
        self.schema_name = schema_name


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def schema_path(schema_name: str) -> Path:
    known = SCHEMA_NAMES + CANDIDATE_SCHEMA_NAMES + AUTHORIZATION_SCHEMA_NAMES + TRACK5_SCHEMA_NAMES
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
    names = SCHEMA_NAMES + CANDIDATE_SCHEMA_NAMES + AUTHORIZATION_SCHEMA_NAMES + TRACK5_SCHEMA_NAMES
    for name in names:
        document = load_schema(name)
        if document.get("additionalProperties") is not False:
            raise SchemaError(f"{name} is not closed")
        if document.get("$id") != f"urn:patchpilot-intelligence-evals:schema:{name}:v1":
            raise SchemaError(f"{name} identifier drifted")
