"""Numeric equivalence checks for a future conversion. No conversion is run."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

ATOL = "0.0001"
RTOL = "0.001"
COMPARISON = "allclose"
CONVERTED_PROVENANCE = "locally-converted"


class EquivalenceError(ValueError):
    """A tolerance input was not a finite decimal. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def within_tolerance(
    left: str,
    right: str,
    *,
    atol: str = ATOL,
    rtol: str = RTOL,
) -> bool:
    """Return whether abs(left - right) is within atol + rtol * abs(right)."""
    observed = _decimal(left)
    expected = _decimal(right)
    tolerance = _decimal(atol)
    relative = _decimal(rtol)
    if tolerance < 0 or relative < 0:
        raise EquivalenceError("tolerance")
    return abs(observed - expected) <= tolerance + relative * abs(expected)


def vectors_match(
    left: list[str],
    right: list[str],
    *,
    atol: str = ATOL,
    rtol: str = RTOL,
) -> bool:
    """Compare two equal-length decimal vectors. A length mismatch fails."""
    if len(left) != len(right):
        return False
    return all(
        within_tolerance(item, other, atol=atol, rtol=rtol)
        for item, other in zip(left, right, strict=True)
    )


def distinct_artifact_digests(source: str, converted: str) -> bool:
    """Converted output keeps an identity separate from the source artifact."""
    if source == converted:
        return False
    return _digest(source) and _digest(converted)


def _decimal(value: str) -> Decimal:
    try:
        number = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise EquivalenceError("decimal") from exc
    if not number.is_finite():
        raise EquivalenceError("non-finite")
    return number


def _digest(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)
