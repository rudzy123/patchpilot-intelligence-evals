"""Runtime classification and header parsing. No archive is downloaded."""

from __future__ import annotations

import pytest

from patchpilot_intelligence_evals.runtime_staging import (
    RuntimeStagingError,
    load_runtime_manifest_template,
    logging_level_error,
    member_disposition,
    not_acquired_runtime_manifest,
    ort_api_indices,
    ort_api_version,
    require_library,
    require_license,
    require_notice,
)

_HEADER = """
#define ORT_API_VERSION 21
ORT_LOGGING_LEVEL_ERROR = 3
struct OrtApi {
ORT_API_STATUS(ORT_API_CALL *CreateEnv)();
ORT_API_STATUS(ORT_API_CALL *CreateSession)();
ORT_API_STATUS(ORT_API_CALL *CreateSessionOptions)();
ORT_API_STATUS(ORT_API_CALL *DisableTelemetryEvents)();
ORT_API_STATUS(ORT_API_CALL *GetErrorMessage)();
ORT_API_STATUS(ORT_API_CALL *ReleaseEnv)();
ORT_API_STATUS(ORT_API_CALL *ReleaseSession)();
ORT_API_STATUS(ORT_API_CALL *ReleaseSessionOptions)();
ORT_API_STATUS(ORT_API_CALL *SessionGetInputCount)();
ORT_API_STATUS(ORT_API_CALL *SessionGetOutputCount)();
};
"""


def test_runtime_template_is_not_acquired() -> None:
    manifest = load_runtime_manifest_template()
    assert manifest == not_acquired_runtime_manifest()
    assert manifest["manifestState"] == "not-acquired"
    assert manifest["telemetry"] == "absent"
    assert manifest["archiveMembers"] == []
    assert manifest["installationAuthorized"] is False


def test_member_classification() -> None:
    library = "libonnxruntime.so.1.31.1"
    assert member_disposition(f"dist/lib/{library}", "regular") == "promotion-library"
    assert member_disposition("dist/lib/libonnxruntime.so", "symlink") == "excluded"
    assert member_disposition("dist/lib/libextra.so", "regular") == "rejected"
    assert (
        member_disposition("dist/lib/libonnxruntime_providers_shared.so", "regular") == "excluded"
    )
    assert member_disposition("dist/LICENSE", "regular") == "promotion-license"
    assert member_disposition("dist/ThirdPartyNotices.txt", "regular") == "promotion-notice"
    assert member_disposition("dist/include/api.h", "regular") == "excluded"
    assert member_disposition("dist/include", "directory") == "excluded"
    assert member_disposition("dist/fifo", "other") == "rejected"
    assert member_disposition("../escape", "regular") == "rejected"


def test_logging_level_reads_an_unassigned_enum() -> None:
    header = """
typedef enum OrtLoggingLevel {
  ORT_LOGGING_LEVEL_VERBOSE,  ///< Verbose informational messages (least severe).
  ORT_LOGGING_LEVEL_INFO,
  ORT_LOGGING_LEVEL_WARNING,
  ORT_LOGGING_LEVEL_ERROR,    ///< Error messages.
  ORT_LOGGING_LEVEL_FATAL,
} OrtLoggingLevel;
"""
    assert logging_level_error(header) == 3


def test_header_parser_fails_closed() -> None:
    assert ort_api_version(_HEADER) == 21
    assert logging_level_error(_HEADER) == 3
    indexes = ort_api_indices(_HEADER)
    assert indexes["CreateSession"] == 1
    assert "Run" not in indexes
    with pytest.raises(RuntimeStagingError) as caught:
        ort_api_indices("struct OrtApi { int unused; };")
    assert caught.value.code == "api-layout"


def test_library_license_and_notice_checks() -> None:
    require_library(b"\x7fELFsynthetic")
    with pytest.raises(RuntimeStagingError) as caught:
        require_library(b"not-elf")
    assert caught.value.code == "unsupported-executable-format"
    require_license(b"MIT\nPermission is hereby granted\n")
    with pytest.raises(RuntimeStagingError):
        require_license(b"not a grant")
    require_notice(b"notices\n")
    with pytest.raises(RuntimeStagingError):
        require_notice(b" \n")
