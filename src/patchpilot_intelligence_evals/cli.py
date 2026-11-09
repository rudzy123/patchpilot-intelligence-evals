"""Deterministic command line for corpus checks and baseline evaluation."""

from __future__ import annotations

import argparse
import sys

from patchpilot_intelligence_evals.corpus import CorpusError, canonical_dumps, validate_corpus
from patchpilot_intelligence_evals.evaluator import evaluate_baseline
from patchpilot_intelligence_evals.network_guard import (
    BoundaryError,
    assert_inside_repository,
    network_guard,
)
from patchpilot_intelligence_evals.schemas import repo_root


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="patchpilot-evals")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("corpus-validation")
    evaluation = commands.add_parser("baseline-evaluation")
    evaluation.add_argument("--output", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        with network_guard():
            if args.command == "corpus-validation":
                summary = validate_corpus()
                sys.stdout.write(canonical_dumps(summary) + "\n")
                return 0
            result = evaluate_baseline()
            text = canonical_dumps(result) + "\n"
            output = args.output
            if output is not None:
                assert_inside_repository(str(output), repo_root())
                destination = repo_root() / str(output)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(text, encoding="utf-8")
            else:
                sys.stdout.write(text)
            return 0
    except (CorpusError, BoundaryError):
        sys.stdout.write(canonical_dumps({"status": "fail"}) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
