"""Closed chat-template compatibility check. It does not create a session.

The checker accepts one explicit Jinja subset. Compatibility is the parsed
shape of that subset, so spaces around operators do not decide the result.
The verified publisher template is accepted only when its digest matches.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

CHAT_TEMPLATE_SHA256 = "f05bf4b967dc993bdc7a2fe6e43759ee218eb0eb340d68b063e1c4f8ad148176"
BOS_TOKEN = "<|startoftext|>"
_USER_TURN = "<|im_start|>user\n"
_TURN_END = "<|im_end|>\n"
_ASSISTANT_PROMPT = "<|im_start|>assistant\n"
_FAILURES = frozenset(
    {
        "identity-mismatch",
        "invalid-rendered-prompt",
        "rendering-failure",
        "tokenizer-failure",
        "unsupported-template-language",
    }
)
_FILTERS = frozenset({"default", "tojson", "trim"})
_TESTS = frozenset({"string"})
_KEYWORDS = frozenset({"and", "else", "false", "if", "in", "is", "none", "not", "or", "true"})


class TemplateCompatibilityError(ValueError):
    """One closed compatibility failure. The message is a code."""

    def __init__(self, code: str) -> None:
        if code not in _FAILURES:
            code = "unsupported-template-language"
        super().__init__(code)
        self.code = code


class _Undefined:
    """A missing name. It is false and cannot be rendered."""

    def __bool__(self) -> bool:
        return False

    def __str__(self) -> str:
        raise TemplateCompatibilityError("rendering-failure")


class _Namespace:
    """Jinja namespace object. Attribute writes stay on this object."""

    def __init__(self, values: dict[str, Any]) -> None:
        self.values = dict(values)


class _Loop:
    def __init__(self, index0: int, last: bool) -> None:
        self.index0 = index0
        self.last = last


def validate_chat_template(
    template: str,
    *,
    expected_digest: str | None,
    content: str,
) -> dict[str, Any]:
    """Parse and render one bounded user turn. Digest mismatch returns first."""
    record, _rendered = _checked(template, expected_digest=expected_digest, content=content)
    return record


def render_checked(template: str, *, expected_digest: str | None, content: str) -> str:
    """Return the rendered prompt after the same closed checks."""
    _record, rendered = _checked(template, expected_digest=expected_digest, content=content)
    return rendered


def _checked(
    template: str,
    *,
    expected_digest: str | None,
    content: str,
) -> tuple[dict[str, Any], str]:
    observed = hashlib.sha256(template.encode("utf-8")).hexdigest()
    if expected_digest is not None and observed != expected_digest:
        raise TemplateCompatibilityError("identity-mismatch")
    program = _parse_template(template)
    rendered = _render_nodes(
        program,
        {
            "add_generation_prompt": True,
            "bos_token": BOS_TOKEN,
            "messages": [{"role": "user", "content": content}],
        },
    )
    if rendered != _expected_prompt(content):
        raise TemplateCompatibilityError("invalid-rendered-prompt")
    record = {
        "compatibility": "supported",
        "renderedDigest": hashlib.sha256(rendered.encode("utf-8")).hexdigest(),
        "renderedShape": "user-turn-with-generation-prompt",
        "runInvoked": False,
        "sessionCreated": False,
        "templateDigest": observed,
    }
    return record, rendered


def _expected_prompt(content: str) -> str:
    return f"{BOS_TOKEN}{_USER_TURN}{content}{_TURN_END}{_ASSISTANT_PROMPT}"


def _parse_template(template: str) -> list[Any]:
    try:
        return _Parser(_blocks(template)).parse_body(frozenset())
    except TemplateCompatibilityError:
        raise
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise TemplateCompatibilityError("unsupported-template-language") from exc


def _blocks(template: str) -> list[tuple[Any, ...]]:
    blocks: list[tuple[Any, ...]] = []
    index = 0
    length = len(template)
    while index < length:
        start = template.find("{", index)
        if start < 0:
            blocks.append(("text", template[index:], False, False))
            break
        if start > index:
            blocks.append(("text", template[index:start], False, False))
        if start + 1 >= length or template[start + 1] not in {"%", "{", "#"}:
            raise TemplateCompatibilityError("unsupported-template-language")
        kind = template[start + 1]
        cursor = start + 2
        lstrip = False
        if cursor < length and template[cursor] == "-":
            lstrip = True
            cursor += 1
        closer = {"%": "%}", "{": "}}", "#": "#}"}[kind]
        end, rstrip = _find_closer(template, cursor, closer)
        inner_end = end - 1 if rstrip else end
        inner = template[cursor:inner_end].strip()
        index = end + len(closer)
        if kind == "#":
            blocks.append(("text", "", lstrip, rstrip))
        else:
            blocks.append(("expr" if kind == "{" else "stmt", inner, lstrip, rstrip))
    return blocks


def _find_closer(template: str, start: int, closer: str) -> tuple[int, bool]:
    quote: str | None = None
    escape = False
    index = start
    while index < len(template):
        char = template[index]
        if quote is not None:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char in {"'", '"'}:
            quote = char
            index += 1
            continue
        if template.startswith(closer, index):
            rstrip = index > start and template[index - 1] == "-"
            return index, rstrip
        index += 1
    raise TemplateCompatibilityError("unsupported-template-language")


class _Parser:
    def __init__(self, blocks: list[tuple[Any, ...]]) -> None:
        self.blocks = blocks
        self.index = 0

    def parse_body(self, stop: frozenset[str]) -> list[Any]:
        nodes: list[Any] = []
        while self.index < len(self.blocks):
            kind, payload, lstrip, rstrip = self.blocks[self.index]
            if kind == "text":
                nodes.append(("text", payload, lstrip, rstrip))
                self.index += 1
                continue
            if kind == "expr":
                nodes.append(("output", _expression(payload), lstrip, rstrip))
                self.index += 1
                continue
            keyword = payload.split(None, 1)[0] if payload else ""
            if keyword in stop:
                return nodes
            self.index += 1
            if keyword == "if":
                nodes.append(self._parse_if(payload, lstrip, rstrip))
            elif keyword == "for":
                nodes.append(self._parse_for(payload, lstrip, rstrip))
            elif keyword == "set":
                nodes.append(("set", _assignment(payload), lstrip, rstrip))
            else:
                raise TemplateCompatibilityError("unsupported-template-language")
        if stop:
            raise TemplateCompatibilityError("unsupported-template-language")
        return nodes

    def _parse_if(self, header: str, lstrip: bool, rstrip: bool) -> tuple[Any, ...]:
        condition = _expression(header.removeprefix("if").strip())
        body = self.parse_body(frozenset({"elif", "else", "endif"}))
        first = body
        _mark_open(body, rstrip)
        arms: list[tuple[Any, list[Any]]] = []
        else_body: list[Any] = []
        while self.index < len(self.blocks):
            kind, payload, left, right = self.blocks[self.index]
            if kind != "stmt":
                break
            word = payload.split(None, 1)[0]
            if word == "elif":
                self.index += 1
                _mark_close(body, left)
                arm = self.parse_body(frozenset({"elif", "else", "endif"}))
                _mark_open(arm, right)
                arms.append((_expression(payload.removeprefix("elif").strip()), arm))
                body = arm
            elif word == "else":
                self.index += 1
                _mark_close(body, left)
                else_body = self.parse_body(frozenset({"endif"}))
                _mark_open(else_body, right)
                body = else_body
            elif word == "endif":
                self.index += 1
                _mark_close(body, left)
                return ("if", condition, first, arms, else_body, lstrip, right)
            else:
                break
        raise TemplateCompatibilityError("unsupported-template-language")

    def _parse_for(self, header: str, lstrip: bool, rstrip: bool) -> tuple[Any, ...]:
        match = re.fullmatch(r"for\s+([A-Za-z_][A-Za-z0-9_]*)\s+in\s+(.+)", header.strip())
        if match is None:
            raise TemplateCompatibilityError("unsupported-template-language")
        body = self.parse_body(frozenset({"endfor"}))
        _mark_open(body, rstrip)
        if self.index >= len(self.blocks):
            raise TemplateCompatibilityError("unsupported-template-language")
        kind, payload, left, right = self.blocks[self.index]
        if kind != "stmt" or payload.split(None, 1)[0] != "endfor":
            raise TemplateCompatibilityError("unsupported-template-language")
        self.index += 1
        _mark_close(body, left)
        return ("for", match.group(1), _expression(match.group(2)), body, lstrip, right)


def _mark_open(body: list[Any], rstrip: bool) -> None:
    if rstrip and body and body[0][0] == "text":
        kind, payload, left, right = body[0]
        body[0] = (kind, str(payload).lstrip(), left, right)


def _mark_close(body: list[Any], lstrip: bool) -> None:
    if lstrip and body and body[-1][0] == "text":
        kind, payload, left, right = body[-1]
        body[-1] = (kind, str(payload).rstrip(), left, right)


def _assignment(header: str) -> tuple[Any, Any]:
    body = header.removeprefix("set").strip()
    name, expr = _split_assignment(body)
    target = name.strip()
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", target):
        return (("name", target), _expression(expr.strip()))
    attribute = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)", target)
    if attribute is None:
        raise TemplateCompatibilityError("unsupported-template-language")
    return (("attr", attribute.group(1), attribute.group(2)), _expression(expr.strip()))


def _split_assignment(body: str) -> tuple[str, str]:
    quote: str | None = None
    escape = False
    index = 0
    while index < len(body):
        char = body[index]
        if quote is not None:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char in {"'", '"'}:
            quote = char
            index += 1
            continue
        if body.startswith(("==", "!="), index):
            index += 2
            continue
        if char == "=":
            return body[:index], body[index + 1 :]
        index += 1
    raise TemplateCompatibilityError("unsupported-template-language")


def _expression(text: str) -> Any:
    tokens = _tokenize(text)
    parser = _Expr(tokens)
    node = parser.parse_if()
    if parser.index != len(tokens):
        raise TemplateCompatibilityError("unsupported-template-language")
    return node


def _tokenize(text: str) -> list[tuple[str, str]]:
    tokens: list[tuple[str, str]] = []
    index = 0
    while index < len(text):
        if text[index].isspace():
            index += 1
            continue
        if text[index] in {"'", '"'}:
            value, index = _string(text, index)
            tokens.append(("string", value))
            continue
        if text.startswith(("==", "!="), index):
            tokens.append(("op", text[index : index + 2]))
            index += 2
            continue
        if text[index] in "()[].,|:+-=":
            tokens.append(("punct", text[index]))
            index += 1
            continue
        if text[index].isdigit():
            end = index + 1
            while end < len(text) and text[end].isdigit():
                end += 1
            tokens.append(("number", text[index:end]))
            index = end
            continue
        if text[index].isalpha() or text[index] == "_":
            end = index + 1
            while end < len(text) and (text[end].isalnum() or text[end] == "_"):
                end += 1
            tokens.append(("name", text[index:end]))
            index = end
            continue
        raise TemplateCompatibilityError("unsupported-template-language")
    return tokens


def _string(text: str, start: int) -> tuple[str, int]:
    quote = text[start]
    index = start + 1
    chars: list[str] = []
    while index < len(text):
        char = text[index]
        if char == "\\":
            if index + 1 >= len(text):
                raise TemplateCompatibilityError("unsupported-template-language")
            escaped = text[index + 1]
            chars.append(
                {"n": "\n", "t": "\t", "\\": "\\", "'": "'", '"': '"'}.get(escaped, escaped)
            )
            index += 2
            continue
        if char == quote:
            return "".join(chars), index + 1
        chars.append(char)
        index += 1
    raise TemplateCompatibilityError("unsupported-template-language")


class _Expr:
    def __init__(self, tokens: list[tuple[str, str]]) -> None:
        self.tokens = tokens
        self.index = 0

    def parse_if(self) -> Any:
        node = self.parse_or()
        if self._matches("name", "if"):
            condition = self.parse_or()
            self._expect_name("else")
            return ("ifexp", node, condition, self.parse_if())
        return node

    def parse_or(self) -> Any:
        node = self.parse_and()
        while self._matches("name", "or"):
            node = ("or", node, self.parse_and())
        return node

    def parse_and(self) -> Any:
        node = self.parse_not()
        while self._matches("name", "and"):
            node = ("and", node, self.parse_not())
        return node

    def parse_not(self) -> Any:
        if self._matches("name", "not"):
            return ("not", self.parse_not())
        return self.parse_comparison()

    def parse_comparison(self) -> Any:
        node = self.parse_sum()
        if self._matches("name", "is"):
            negated = self._matches("name", "not")
            name = self._take("name")
            if name in _KEYWORDS or name not in _TESTS:
                raise TemplateCompatibilityError("unsupported-template-language")
            return ("test", node, name, negated)
        if self._matches("name", "in"):
            return ("in", node, self.parse_sum())
        if self._matches("name", "not") and self._matches("name", "in"):
            return ("not", ("in", node, self.parse_sum()))
        token = self._peek()
        if token is not None and token[0] == "op":
            operator = self._take("op")
            return ("cmp", operator, node, self.parse_sum())
        return node

    def parse_sum(self) -> Any:
        node = self.parse_filter()
        while self._matches("punct", "+"):
            node = ("add", node, self.parse_filter())
        return node

    def parse_filter(self) -> Any:
        node = self.parse_unary()
        while self._matches("punct", "|"):
            name = self._take("name")
            if name not in _FILTERS:
                raise TemplateCompatibilityError("unsupported-template-language")
            arguments: list[Any] = []
            if self._matches("punct", "("):
                if not self._matches("punct", ")"):
                    arguments.append(self.parse_if())
                    while self._matches("punct", ","):
                        arguments.append(self.parse_if())
                    self._expect("punct", ")")
            node = ("filter", name, node, arguments)
        return node

    def parse_unary(self) -> Any:
        if self._matches("punct", "-"):
            return ("neg", self.parse_unary())
        return self.parse_postfix()

    def parse_postfix(self) -> Any:
        node = self.parse_primary()
        while True:
            if self._matches("punct", "."):
                node = ("attr", node, self._take("name"))
            elif self._matches("punct", "("):
                node = ("call", node, self._arguments())
            elif self._matches("punct", "["):
                node = self._subscript(node)
            else:
                return node

    def parse_primary(self) -> Any:
        token = self._peek()
        if token is None:
            raise TemplateCompatibilityError("unsupported-template-language")
        if token == ("punct", "("):
            self.index += 1
            node = self.parse_if()
            self._expect("punct", ")")
            return node
        if token[0] == "string":
            self.index += 1
            return ("lit", token[1])
        if token[0] == "number":
            self.index += 1
            return ("lit", int(token[1]))
        if token[0] == "name":
            self.index += 1
            if token[1] == "true":
                return ("lit", True)
            if token[1] == "false":
                return ("lit", False)
            if token[1] == "none":
                return ("lit", None)
            if token[1] in _KEYWORDS:
                raise TemplateCompatibilityError("unsupported-template-language")
            return ("name", token[1])
        raise TemplateCompatibilityError("unsupported-template-language")

    def _arguments(self) -> list[Any]:
        if self._matches("punct", ")"):
            return []
        arguments = [self._argument()]
        while self._matches("punct", ","):
            arguments.append(self._argument())
        self._expect("punct", ")")
        return arguments

    def _argument(self) -> Any:
        token = self._peek()
        following = self.tokens[self.index + 1] if self.index + 1 < len(self.tokens) else None
        if token is not None and token[0] == "name" and following == ("punct", "="):
            self.index += 2
            return ("kw", token[1], self.parse_if())
        return self.parse_if()

    def _subscript(self, node: Any) -> Any:
        if self._matches("punct", ":"):
            end = None if self._matches("punct", "]") else self.parse_if()
            if end is not None:
                self._expect("punct", "]")
            return ("slice", node, None, end)
        start = self.parse_if()
        if self._matches("punct", ":"):
            end = None if self._peek() == ("punct", "]") else self.parse_if()
            self._expect("punct", "]")
            return ("slice", node, start, end)
        self._expect("punct", "]")
        return ("index", node, start)

    def _peek(self) -> tuple[str, str] | None:
        if self.index >= len(self.tokens):
            return None
        return self.tokens[self.index]

    def _matches(self, kind: str, value: str) -> bool:
        if self._peek() == (kind, value):
            self.index += 1
            return True
        return False

    def _expect(self, kind: str, value: str) -> None:
        if not self._matches(kind, value):
            raise TemplateCompatibilityError("unsupported-template-language")

    def _expect_name(self, value: str) -> None:
        self._expect("name", value)

    def _take(self, kind: str) -> str:
        token = self._peek()
        if token is None or token[0] != kind:
            raise TemplateCompatibilityError("unsupported-template-language")
        self.index += 1
        return token[1]


def _render_nodes(nodes: list[Any], env: dict[str, Any]) -> str:
    try:
        return _render(nodes, env)
    except TemplateCompatibilityError:
        raise
    except (AttributeError, IndexError, KeyError, TypeError, ValueError) as exc:
        raise TemplateCompatibilityError("rendering-failure") from exc


def _render(nodes: list[Any], env: dict[str, Any]) -> str:
    parts: list[str] = []
    for node in _prepare(nodes):
        if node[0] == "text":
            parts.append(str(node[1]))
        elif node[0] == "output":
            parts.append(_text(_evaluate(node[1], env)))
        elif node[0] == "set":
            _assign(node[1], env)
        elif node[0] == "if":
            parts.append(_render_if(node, env))
        elif node[0] == "for":
            parts.append(_render_for(node, env))
        else:
            raise TemplateCompatibilityError("unsupported-template-language")
    return "".join(parts)


def _prepare(nodes: list[Any]) -> list[Any]:
    prepared = list(nodes)
    for index, node in enumerate(nodes):
        lstrip = bool(node[-2])
        rstrip = bool(node[-1])
        if lstrip and index > 0 and prepared[index - 1][0] == "text":
            previous = prepared[index - 1]
            prepared[index - 1] = ("text", str(previous[1]).rstrip(), False, False)
        if rstrip and index + 1 < len(prepared) and prepared[index + 1][0] == "text":
            following = prepared[index + 1]
            prepared[index + 1] = ("text", str(following[1]).lstrip(), False, False)
    return prepared


def _render_if(node: tuple[Any, ...], env: dict[str, Any]) -> str:
    _condition, body, arms, else_body = node[1], node[2], node[3], node[4]
    if _true(_evaluate(node[1], env)):
        return _render(body, env)
    for condition, arm in arms:
        if _true(_evaluate(condition, env)):
            return _render(arm, env)
    return _render(else_body, env)


def _render_for(node: tuple[Any, ...], env: dict[str, Any]) -> str:
    name = str(node[1])
    values = _evaluate(node[2], env)
    if isinstance(values, str) or not isinstance(values, list):
        raise TemplateCompatibilityError("rendering-failure")
    rendered: list[str] = []
    last = len(values) - 1
    for index, item in enumerate(values):
        frame = dict(env)
        frame[name] = item
        frame["loop"] = _Loop(index, index == last)
        rendered.append(_render(node[3], frame))
    return "".join(rendered)


def _assign(assignment: tuple[Any, Any], env: dict[str, Any]) -> None:
    target, expr = assignment
    value = _evaluate(expr, env)
    if target[0] == "name":
        env[str(target[1])] = value
        return
    owner = env.get(str(target[1]), _Undefined())
    if not isinstance(owner, _Namespace):
        raise TemplateCompatibilityError("rendering-failure")
    owner.values[str(target[2])] = value


def _evaluate(node: Any, env: dict[str, Any]) -> Any:
    kind = node[0]
    if kind == "lit":
        return node[1]
    if kind == "name":
        if node[1] == "namespace":
            return ("namespace",)
        value = env.get(str(node[1]), _Undefined())
        return value
    if kind == "attr":
        owner = _evaluate(node[1], env)
        name = str(node[2])
        if isinstance(owner, _Namespace):
            return owner.values.get(name, _Undefined())
        if isinstance(owner, _Loop) and name in {"index0", "last"}:
            return getattr(owner, name)
        raise TemplateCompatibilityError("rendering-failure")
    if kind == "index":
        return _index(_evaluate(node[1], env), _evaluate(node[2], env))
    if kind == "slice":
        value = _evaluate(node[1], env)
        if not isinstance(value, list):
            raise TemplateCompatibilityError("rendering-failure")
        start = 0 if node[2] is None else int(_evaluate(node[2], env))
        end = None if node[3] is None else int(_evaluate(node[3], env))
        return value[start:end]
    if kind == "add":
        return _add(_evaluate(node[1], env), _evaluate(node[2], env))
    if kind == "and":
        left = _evaluate(node[1], env)
        return _evaluate(node[2], env) if _true(left) else left
    if kind == "or":
        left = _evaluate(node[1], env)
        return left if _true(left) else _evaluate(node[2], env)
    if kind == "not":
        return not _true(_evaluate(node[1], env))
    if kind == "neg":
        value = _evaluate(node[1], env)
        if not isinstance(value, int):
            raise TemplateCompatibilityError("rendering-failure")
        return -value
    if kind == "cmp":
        return _compare(node[1], _evaluate(node[2], env), _evaluate(node[3], env))
    if kind == "in":
        return _contains(_evaluate(node[2], env), _evaluate(node[1], env))
    if kind == "test":
        passed = _test(_evaluate(node[1], env), str(node[2]))
        return (not passed) if node[3] else passed
    if kind == "ifexp":
        return _evaluate(node[1] if _true(_evaluate(node[2], env)) else node[3], env)
    if kind == "filter":
        return _filter(str(node[1]), _evaluate(node[2], env), node[3], env)
    if kind == "call":
        return _call(node[1], node[2], env)
    raise TemplateCompatibilityError("unsupported-template-language")


def _index(value: Any, item: Any) -> Any:
    if isinstance(value, list) and isinstance(item, int):
        return value[item]
    if isinstance(value, dict) and isinstance(item, str):
        return value[item]
    if isinstance(value, str) and isinstance(item, int):
        return value[item]
    raise TemplateCompatibilityError("rendering-failure")


def _add(left: Any, right: Any) -> Any:
    if isinstance(left, str) and isinstance(right, str):
        return left + right
    if isinstance(left, int) and isinstance(right, int):
        return left + right
    raise TemplateCompatibilityError("rendering-failure")


def _compare(operator: str, left: Any, right: Any) -> bool:
    if isinstance(left, _Undefined) or isinstance(right, _Undefined):
        return False
    if operator == "==":
        return bool(left == right)
    if operator == "!=":
        return bool(left != right)
    raise TemplateCompatibilityError("unsupported-template-language")


def _contains(container: Any, item: Any) -> bool:
    if isinstance(container, str) and isinstance(item, str):
        return item in container
    if isinstance(container, list):
        return item in container
    raise TemplateCompatibilityError("rendering-failure")


def _test(value: Any, name: str) -> bool:
    if name == "string":
        return isinstance(value, str)
    raise TemplateCompatibilityError("unsupported-template-language")


def _filter(name: str, value: Any, arguments: list[Any], env: dict[str, Any]) -> Any:
    evaluated = [_evaluate(item, env) for item in arguments]
    if name == "default":
        if len(evaluated) != 1:
            raise TemplateCompatibilityError("rendering-failure")
        if isinstance(value, _Undefined) or value is None:
            return evaluated[0]
        return value
    if name == "trim":
        if not isinstance(value, str) or evaluated:
            raise TemplateCompatibilityError("rendering-failure")
        return value.strip()
    if name == "tojson":
        if evaluated:
            raise TemplateCompatibilityError("rendering-failure")
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    raise TemplateCompatibilityError("unsupported-template-language")


def _call(callee: Any, arguments: list[Any], env: dict[str, Any]) -> Any:
    if isinstance(callee, tuple) and callee[0] == "name" and callee[1] == "namespace":
        values: dict[str, Any] = {}
        for item in arguments:
            if not isinstance(item, tuple) or item[0] != "kw":
                raise TemplateCompatibilityError("rendering-failure")
            values[str(item[1])] = _evaluate(item[2], env)
        return _Namespace(values)
    if isinstance(callee, tuple) and callee[0] == "attr" and callee[2] == "split":
        owner = _evaluate(callee[1], env)
        evaluated = [_evaluate(item, env) for item in arguments]
        if not isinstance(owner, str) or len(evaluated) != 1 or not isinstance(evaluated[0], str):
            raise TemplateCompatibilityError("rendering-failure")
        return owner.split(evaluated[0])
    raise TemplateCompatibilityError("rendering-failure")


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value
    raise TemplateCompatibilityError("rendering-failure")


def _true(value: Any) -> bool:
    if isinstance(value, _Undefined):
        return False
    return bool(value)
