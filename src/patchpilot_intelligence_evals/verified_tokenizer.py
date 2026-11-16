"""Closed reader for one mounted Hugging Face ``tokenizer.json``.

The module uses the standard library. It supports the verified LFM2.5 BPE
file and a tiny synthetic fixture of the same shape. An unsupported model
type or chat-template construct stops before session creation.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

CHAT_TEMPLATE_SHA256 = "f05bf4b967dc993bdc7a2fe6e43759ee218eb0eb340d68b063e1c4f8ad148176"


class MeasurementError(ValueError):
    """Tokenizer construction failed before a session exists."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def sha256_text(value: str) -> str:
    """Return the SHA-256 hex digest of one UTF-8 string."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _bytes_to_unicode() -> dict[int, str]:
    printable = (
        list(range(ord("!"), ord("~") + 1))
        + list(range(ord("¡"), ord("¬") + 1))
        + list(range(ord("®"), ord("ÿ") + 1))
    )
    code_points = list(printable)
    extra = 0
    for byte in range(256):
        if byte not in printable:
            printable.append(byte)
            code_points.append(256 + extra)
            extra += 1
    return {byte: chr(point) for byte, point in zip(printable, code_points, strict=True)}


_BYTES_TO_UNICODE = _bytes_to_unicode()
_UNICODE_TO_BYTE = {symbol: byte for byte, symbol in _BYTES_TO_UNICODE.items()}
_BYTE_PATTERN = re.compile(r"'s|'t|'re|'ve|'m|'ll|'d| ?[\w]+| ?[^\s\w]+|\s+(?!\S)|\s+")


def _category_ok(character: str, classes: str) -> bool:
    category = unicodedata.category(character)
    allowed = {
        "L": category.startswith("L"),
        "N": category.startswith("N"),
        "P": category.startswith("P"),
        "S": category.startswith("S"),
        "Z": category.startswith("Z"),
    }
    return any(allowed[item] for item in classes if item in allowed)


def _scan(pattern: str, text: str) -> list[str]:
    """Scan a GPT-2 unicode class pattern without the ``regex`` package."""
    if r"\p{L}" not in pattern:
        return [match.group(0) for match in _BYTE_PATTERN.finditer(text)]
    pieces: list[str] = []
    index = 0
    contractions = ("'s", "'t", "'re", "'ve", "'m", "'ll", "'d")
    while index < len(text):
        if text.startswith(contractions, index):
            pieces.append(
                text[
                    index : index
                    + len(next(item for item in contractions if text.startswith(item, index)))
                ]
            )
            index += len(pieces[-1])
            continue
        if text[index].isspace():
            end = index + 1
            while end < len(text) and text[end].isspace():
                end += 1
            pieces.append(text[index:end])
            index = end
            continue
        if _category_ok(text[index], "LN"):
            end = index + 1
            while end < len(text) and _category_ok(text[end], "LN"):
                end += 1
            pieces.append(text[index:end])
            index = end
            continue
        end = index + 1
        while end < len(text) and not text[end].isspace() and not _category_ok(text[end], "LN"):
            end += 1
        pieces.append(text[index:end])
        index = end
    return pieces


class VerifiedTokenizer:
    """Encode one chat prompt with a pinned template."""

    def __init__(self, document: dict[str, Any], chat_template: str) -> None:
        model = document.get("model")
        if not isinstance(model, dict) or model.get("type") != "BPE":
            raise MeasurementError("tokenizer-failure")
        vocab = model.get("vocab")
        merges = model.get("merges")
        if not isinstance(vocab, dict) or not isinstance(merges, list):
            raise MeasurementError("tokenizer-failure")
        self.vocab: dict[str, int] = {str(key): int(value) for key, value in vocab.items()}
        self.merges: list[tuple[str, str]] = []
        for item in merges:
            if not isinstance(item, list) or len(item) != 2:
                raise MeasurementError("tokenizer-failure")
            self.merges.append((str(item[0]), str(item[1])))
        added = document.get("added_tokens")
        self.added: list[tuple[str, int]] = []
        if isinstance(added, list):
            for item in added:
                if isinstance(item, dict) and isinstance(item.get("content"), str):
                    self.added.append((str(item["content"]), int(item["id"])))
        self.added.sort(key=lambda item: len(item[0]), reverse=True)
        self.chat_template = chat_template
        self.chat_template_sha256 = sha256_text(chat_template)
        if self.chat_template_sha256 != CHAT_TEMPLATE_SHA256 and "{content}" not in chat_template:
            raise MeasurementError("tokenizer-failure")

    def render(self, content: str) -> str:
        """Render one user turn when the template digest matches."""
        if self.chat_template == "synthetic:{content}":
            return f"synthetic:{content}"
        if self.chat_template_sha256 != CHAT_TEMPLATE_SHA256:
            raise MeasurementError("tokenizer-failure")
        module = _compatibility_module()
        try:
            return str(
                module.render_checked(
                    self.chat_template,
                    expected_digest=CHAT_TEMPLATE_SHA256,
                    content=content,
                )
            )
        except module.TemplateCompatibilityError as exc:
            raise MeasurementError(str(exc.code)) from exc

    def encode(self, text: str) -> list[int]:
        """Encode rendered text. Added tokens are taken before BPE."""
        ids: list[int] = []
        index = 0
        while index < len(text):
            added = next(
                (item for item in self.added if text.startswith(item[0], index)),
                None,
            )
            if added is not None:
                ids.append(added[1])
                index += len(added[0])
                continue
            end = index + 1
            while end < len(text) and not any(
                text.startswith(token, end) for token, _token_id in self.added
            ):
                end += 1
            ids.extend(self._encode_piece(text[index:end]))
            index = end
        return ids

    def _encode_piece(self, text: str) -> list[int]:
        words: list[str] = []
        for piece in _scan(r"\p{L}", text):
            encoded = "".join(_BYTES_TO_UNICODE[byte] for byte in piece.encode("utf-8"))
            words.extend(_bpe(encoded, self.merges))
        try:
            return [self.vocab[word] for word in words]
        except KeyError as exc:
            raise MeasurementError("tokenizer-failure") from exc

    def decode(self, token_ids: list[int]) -> str:
        """Decode generated ids. Added tokens stay their literal text."""
        reverse_added = {token_id: text for text, token_id in self.added}
        reverse_vocab = {token_id: text for text, token_id in self.vocab.items()}
        pieces: list[str] = []
        for token_id in token_ids:
            if token_id in reverse_added:
                pieces.append(reverse_added[token_id])
                continue
            symbol = reverse_vocab.get(token_id)
            if symbol is None:
                raise MeasurementError("tokenizer-failure")
            try:
                raw = bytes(_UNICODE_TO_BYTE[character] for character in symbol)
            except KeyError as exc:
                raise MeasurementError("tokenizer-failure") from exc
            pieces.append(raw.decode("utf-8", errors="replace"))
        return "".join(pieces)


def _bpe(token: str, merges: list[tuple[str, str]]) -> list[str]:
    if len(token) < 2:
        return [token]
    symbols = list(token)
    ranked = {pair: index for index, pair in enumerate(merges)}
    while len(symbols) > 1:
        pairs = [(symbols[index], symbols[index + 1]) for index in range(len(symbols) - 1)]
        best = min(pairs, key=lambda pair: ranked.get(pair, 10**9))
        if best not in ranked:
            break
        merged: list[str] = []
        index = 0
        while index < len(symbols):
            if index < len(symbols) - 1 and (symbols[index], symbols[index + 1]) == best:
                merged.append(symbols[index] + symbols[index + 1])
                index += 2
            else:
                merged.append(symbols[index])
                index += 1
        symbols = merged
    return symbols


def _compatibility_module() -> Any:
    """Load the checker from the package, or from the staged sibling file."""
    try:
        from patchpilot_intelligence_evals import template_compatibility as module
    except ImportError:
        return _load_sibling_compatibility()
    return module


def _load_sibling_compatibility() -> Any:
    path = Path(__file__).with_name("template_compatibility.py")
    spec = importlib.util.spec_from_file_location("template_compatibility", path)
    if spec is None or spec.loader is None:
        raise MeasurementError("tokenizer-failure")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_tokenizer(model_dir: Path) -> VerifiedTokenizer:
    """Load the mounted tokenizer and its chat template."""
    document = json.loads((model_dir / "tokenizer.json").read_text(encoding="utf-8"))
    template = (model_dir / "chat_template.jinja").read_text(encoding="utf-8")
    if not isinstance(document, dict):
        raise MeasurementError("tokenizer-failure")
    return VerifiedTokenizer(document, template)
