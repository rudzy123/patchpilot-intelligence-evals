"""Synthetic decimal tolerance checks. No conversion is run."""

from __future__ import annotations

import pytest

from patchpilot_intelligence_evals.conversion_equivalence import (
    EquivalenceError,
    distinct_artifact_digests,
    vectors_match,
    within_tolerance,
)


def test_tolerance_uses_absolute_and_relative_bounds() -> None:
    assert within_tolerance("1.0000", "1.0000")
    assert within_tolerance("0.0001", "0")
    assert not within_tolerance("0.0001001", "0")
    assert within_tolerance("1.0011", "1")
    assert not within_tolerance("1.0011001", "1")
    assert within_tolerance("-1.0001", "-1")
    assert vectors_match(["0.0001", "1.0011"], ["0", "1"])
    assert not vectors_match(["0"], ["0", "0"])
    source = "a" * 64
    converted = "b" * 64
    assert distinct_artifact_digests(source, converted)
    assert not distinct_artifact_digests(source, source)
    assert not distinct_artifact_digests("short", converted)


def test_non_finite_and_invalid_decimals_fail() -> None:
    with pytest.raises(EquivalenceError) as caught:
        within_tolerance("NaN", "0")
    assert caught.value.code == "non-finite"
    with pytest.raises(EquivalenceError) as caught:
        within_tolerance("Infinity", "1")
    assert caught.value.code == "non-finite"
    with pytest.raises(EquivalenceError) as caught:
        within_tolerance("not-a-number", "1")
    assert caught.value.code == "decimal"
    with pytest.raises(EquivalenceError) as caught:
        within_tolerance("1", "1", atol="-0.0001")
    assert caught.value.code == "tolerance"
