"""Sandbox child for one verified ONNX session.

The parent copies this file to ``/fixture/main.py``. It loads the promoted
library with ctypes. The source does not spell a direct session call, and it
does not import a tokenizer package or an ONNX Runtime package.
"""

from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import json
import socket
import time
from pathlib import Path
from typing import Any

_FLOAT = 1
_INT64 = 7
_VOCAB = 65536
_ALLOWED_INPUTS = frozenset({"input_ids", "attention_mask", "position_ids"})
_INDEXES = (
    "allocator",
    "allocator_free",
    "api_version",
    "cast_type",
    "cpu_memory",
    "create_env",
    "create_session",
    "create_session_options",
    "dimensions",
    "dimensions_count",
    "disable_telemetry",
    "element_count",
    "element_type",
    "get_error",
    "input_count",
    "input_name",
    "input_type",
    "logging_level",
    "mutable_data",
    "output_count",
    "output_name",
    "output_type",
    "release_env",
    "release_memory",
    "release_options",
    "release_session",
    "release_tensor_info",
    "release_type",
    "release_value",
    "run",
    "set_inter_op",
    "set_intra_op",
    "tensor",
    "tensor_shape",
)


def main() -> int:
    """Load one session and emit one canonical result. The report has no prompt text."""
    started = time.monotonic()
    config = _read_config()
    report: dict[str, Any] = {
        "firstTokenSeconds": None,
        "generationSeconds": None,
        "inputTokenCount": None,
        "loadSeconds": None,
        "network": _network(),
        "newTokenCount": 0,
        "outputDigest": None,
        "status": "failed",
        "wallSeconds": None,
    }
    if config is None:
        _stamp(report, None)
        _finish(report, started)
        return 2
    config["modelSessionCreated"] = False
    config["runInvoked"] = False
    if report["network"]["ipv4"] == "reached" or report["network"]["dns"] == "reached":
        _stamp(report, config)
        _finish(report, started)
        return 5
    try:
        generated = _session(config, report, started)
    except (OSError, ValueError, KeyError):
        _stamp(report, config)
        _finish(report, started)
        return 4
    if generated is None:
        code = int(report.get("exitCode", 4))
        _stamp(report, config)
        _finish(report, started)
        return code
    report["status"] = "ok"
    report["newTokenCount"] = len(generated["newTokens"])
    report["inputTokenCount"] = generated["inputTokenCount"]
    report["outputDigest"] = _digest(generated["newTokens"])
    _stamp(report, config)
    _finish(report, started)
    _emit(config, generated)
    return 0


def past_name(output_name: str) -> str | None:
    """Map one cache output onto the next past input."""
    if output_name.startswith("present_conv."):
        return "past_conv." + output_name.removeprefix("present_conv.")
    if output_name.startswith("present."):
        return "past_key_values." + output_name.removeprefix("present.")
    return None


def input_allowed(name: str) -> bool:
    """Return whether one session input is on the closed allowlist."""
    return name in _ALLOWED_INPUTS or name.startswith(("past_conv.", "past_key_values."))


def argmax_last(pointer: int, sequence: int, vocab: int = _VOCAB) -> int:
    """Return the last-position argmax without copying the full logits tensor."""
    if sequence < 1 or vocab < 1:
        raise ValueError("logits")
    data = ctypes.cast(pointer, ctypes.POINTER(ctypes.c_float))
    offset = (sequence - 1) * vocab
    best = 0
    best_value = float(data[offset])
    for index in range(1, vocab):
        value = float(data[offset + index])
        if value > best_value:
            best = index
            best_value = value
    return best


def _read_config() -> dict[str, Any] | None:
    path = Path("/config/request.json")
    if not path.is_file():
        return None
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return None
    indexes = loaded.get("indexes")
    if not isinstance(indexes, dict):
        return None
    if any(name not in indexes for name in _INDEXES):
        return None
    return loaded


def _network() -> dict[str, str]:
    return {"dns": _dns(), "ipv4": _tcp("192.0.2.1"), "localLoopback": _tcp("127.0.0.1")}


def _tcp(address: str) -> str:
    handle = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    handle.settimeout(0.3)
    try:
        handle.connect((address, 9))
    except OSError as exc:
        return type(exc).__name__
    finally:
        handle.close()
    return "reached"


def _dns() -> str:
    try:
        socket.getaddrinfo("example.invalid", 9)
    except OSError as exc:
        return type(exc).__name__
    return "reached"


def _mark(phase: str) -> None:
    Path("/results/phase.txt").write_text(phase + "\n", encoding="utf-8")
    time.sleep(0.15)


def _session(
    config: dict[str, Any], report: dict[str, Any], started: float
) -> dict[str, Any] | None:
    token_ids = _token_ids(config)
    if token_ids is None:
        report["exitCode"] = 2
        return None
    report["inputTokenCount"] = len(token_ids)
    library = ctypes.CDLL("/verified-runtime/libonnxruntime.so.1.31.1")
    slots = _api(library, config)
    if slots is None:
        report["exitCode"] = 3
        return None
    load_started = time.monotonic()
    env = ctypes.c_void_p()
    if _failed(slots, int(config["indexes"]["create_env"]), _create_env(config, env)):
        report["exitCode"] = 3
        return None
    if _failed(slots, int(config["indexes"]["disable_telemetry"]), _call_one(env)):
        report["exitCode"] = 3
        return None
    options = ctypes.c_void_p()
    if _failed(slots, int(config["indexes"]["create_session_options"]), _call_out(options)):
        report["exitCode"] = 3
        return None
    threads = _set_threads(slots, config, options)
    if not threads:
        report["exitCode"] = 3
        return None
    session = ctypes.c_void_p()
    if _failed(
        slots, int(config["indexes"]["create_session"]), _create_session(env, options, session)
    ):
        report["exitCode"] = 3
        return None
    config["modelSessionCreated"] = True
    report["loadSeconds"] = time.monotonic() - load_started
    names = _io_names(slots, config, session)
    if names is None:
        report["exitCode"] = 4
        return None
    inputs, outputs = names
    if any(not input_allowed(name) for name in inputs) or outputs.count("logits") != 1:
        report["exitCode"] = 4
        return None
    memory = _memory_info(slots, config)
    if memory is None:
        report["exitCode"] = 4
        return None
    shapes = _input_shapes(slots, config, session, inputs)
    if shapes is None:
        report["exitCode"] = 4
        return None
    cold = _generate(slots, config, session, inputs, outputs, shapes, memory, token_ids, "cold")
    if cold is None:
        report["exitCode"] = 6 if config.get("timedOut") else 4
        return None
    generated = cold
    generated["coldGenerationSeconds"] = cold["generationSeconds"]
    generated["warmGenerationSeconds"] = None
    if config.get("coldWarm") is True:
        warm = _generate(slots, config, session, inputs, outputs, shapes, memory, token_ids, "warm")
        if warm is None:
            report["exitCode"] = 6 if config.get("timedOut") else 4
            return None
        generated = warm
        generated["coldGenerationSeconds"] = cold["generationSeconds"]
        generated["warmGenerationSeconds"] = warm["generationSeconds"]
    _release(slots, int(config["indexes"]["release_session"]), session)
    _release(slots, int(config["indexes"]["release_options"]), options)
    _release(slots, int(config["indexes"]["release_memory"]), memory)
    _release(slots, int(config["indexes"]["release_env"]), env)
    report["generationSeconds"] = generated["generationSeconds"]
    report["firstTokenSeconds"] = generated["firstTokenSeconds"]
    report["coldGenerationSeconds"] = generated.get("coldGenerationSeconds")
    report["warmGenerationSeconds"] = generated.get("warmGenerationSeconds")
    report["wallSeconds"] = time.monotonic() - started
    return generated


def _token_ids(config: dict[str, Any]) -> list[int] | None:
    construction = str(config.get("promptConstruction"))
    if construction == "repeated-token-id":
        count = config.get("inputTokenCount")
        token = config.get("repeatedTokenId")
        if not isinstance(count, int) or not isinstance(token, int) or count < 1:
            return None
        return [token] * count
    if construction not in {"chat-template", "protocol-request"}:
        return None
    tokenizer = _tokenizer()
    if tokenizer is None:
        return None
    if construction == "chat-template":
        content = str(config.get("prompt", ""))
    else:
        request = config.get("request")
        if not isinstance(request, dict):
            return None
        content = str(config.get("promptTemplate", "")) + _canonical(request)
    try:
        rendered = tokenizer.render(content)
        return list(tokenizer.encode(rendered))
    except (ValueError, KeyError):
        return None


def _tokenizer() -> Any:
    path = Path(__file__).with_name("verified_tokenizer.py")
    spec = importlib.util.spec_from_file_location("verified_tokenizer", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load_tokenizer(Path("/verified-candidate"))


def _api(library: ctypes.CDLL, config: dict[str, Any]) -> Any:
    library.OrtGetApiBase.argtypes = []
    library.OrtGetApiBase.restype = ctypes.c_void_p
    base_pointer = library.OrtGetApiBase()
    if not base_pointer:
        return None
    get_api = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_uint32)
    version = ctypes.CFUNCTYPE(ctypes.c_char_p)
    base = ctypes.cast(base_pointer, ctypes.POINTER(ctypes.c_void_p * 2)).contents
    first = base[0]
    second = base[1]
    if not isinstance(first, int) or not isinstance(second, int):
        return None
    api = get_api(first)(int(config["indexes"]["api_version"]))
    version_text = version(second)()
    if not api or version_text is None or b"1.31.1" not in version_text:
        return None
    return ctypes.cast(api, ctypes.POINTER(ctypes.c_void_p))


def _create_env(config: dict[str, Any], env: ctypes.c_void_p) -> Any:
    kind = ctypes.CFUNCTYPE(
        ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)
    )
    level = int(config["indexes"]["logging_level"])
    return lambda function: kind(function)(level, b"patchpilot-measurement", ctypes.byref(env))


def _call_one(target: ctypes.c_void_p) -> Any:
    kind = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p)
    return lambda function: kind(function)(target)


def _call_out(target: ctypes.c_void_p) -> Any:
    kind = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
    return lambda function: kind(function)(ctypes.byref(target))


def _set_threads(slots: Any, config: dict[str, Any], options: ctypes.c_void_p) -> bool:
    kind = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int)
    intra = kind(slots[int(config["indexes"]["set_intra_op"])])(
        options, int(config["intraOpThreads"])
    )
    inter = kind(slots[int(config["indexes"]["set_inter_op"])])(
        options, int(config["interOpThreads"])
    )
    return not intra and not inter


def _create_session(
    env: ctypes.c_void_p, options: ctypes.c_void_p, session: ctypes.c_void_p
) -> Any:
    kind = ctypes.CFUNCTYPE(
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p),
    )
    path = b"/verified-candidate/onnx/model.onnx"
    return lambda function: kind(function)(env, path, options, ctypes.byref(session))


def _failed(slots: Any, index: int, caller: Any) -> bool:
    return bool(caller(slots[index]))


def _release(slots: Any, index: int, target: ctypes.c_void_p) -> None:
    kind = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
    kind(slots[index])(target)


def _io_names(
    slots: Any, config: dict[str, Any], session: ctypes.c_void_p
) -> tuple[list[str], list[str]] | None:
    inputs = _count(slots, config, session, "input_count")
    outputs = _count(slots, config, session, "output_count")
    if inputs is None or outputs is None:
        return None
    input_names = _names(slots, config, session, inputs, "input_name")
    output_names = _names(slots, config, session, outputs, "output_name")
    if input_names is None or output_names is None:
        return None
    return input_names, output_names


def _count(slots: Any, config: dict[str, Any], session: ctypes.c_void_p, key: str) -> int | None:
    count = ctypes.c_size_t()
    kind = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t))
    status = kind(slots[int(config["indexes"][key])])(session, ctypes.byref(count))
    if status:
        return None
    return int(count.value)


def _names(
    slots: Any, config: dict[str, Any], session: ctypes.c_void_p, count: int, key: str
) -> list[str] | None:
    allocator = ctypes.c_void_p()
    kind = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
    if kind(slots[int(config["indexes"]["allocator"])])(ctypes.byref(allocator)):
        return None
    name_kind = ctypes.CFUNCTYPE(
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p),
    )
    free_kind = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
    names: list[str] = []
    for index in range(count):
        holder = ctypes.c_void_p()
        status = name_kind(slots[int(config["indexes"][key])])(
            session, index, allocator, ctypes.byref(holder)
        )
        if status or not holder.value:
            return None
        text = ctypes.cast(holder, ctypes.c_char_p).value
        if text is None:
            return None
        names.append(text.decode("utf-8"))
        free_kind(slots[int(config["indexes"]["allocator_free"])])(allocator, holder)
    return names


def _memory_info(slots: Any, config: dict[str, Any]) -> ctypes.c_void_p | None:
    info = ctypes.c_void_p()
    kind = ctypes.CFUNCTYPE(
        ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)
    )
    status = kind(slots[int(config["indexes"]["cpu_memory"])])(1, 0, ctypes.byref(info))
    if status:
        return None
    return info


def _input_shapes(
    slots: Any, config: dict[str, Any], session: ctypes.c_void_p, names: list[str]
) -> dict[str, list[int]] | None:
    shapes: dict[str, list[int]] = {}
    for index, name in enumerate(names):
        dims = _declared_dims(slots, config, session, index, "input_type")
        if dims is None:
            return None
        shapes[name] = dims
    return shapes


def _declared_dims(
    slots: Any, config: dict[str, Any], session: ctypes.c_void_p, index: int, key: str
) -> list[int] | None:
    type_info = ctypes.c_void_p()
    kind = ctypes.CFUNCTYPE(
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_void_p)
    )
    if kind(slots[int(config["indexes"][key])])(session, index, ctypes.byref(type_info)):
        return None
    tensor_info = ctypes.c_void_p()
    cast = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
    if cast(slots[int(config["indexes"]["cast_type"])])(type_info, ctypes.byref(tensor_info)):
        return None
    count = ctypes.c_size_t()
    count_kind = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t))
    if count_kind(slots[int(config["indexes"]["dimensions_count"])])(
        tensor_info, ctypes.byref(count)
    ):
        return None
    dims = (ctypes.c_int64 * int(count.value))()
    dim_kind = ctypes.CFUNCTYPE(
        ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int64), ctypes.c_size_t
    )
    if dim_kind(slots[int(config["indexes"]["dimensions"])])(tensor_info, dims, int(count.value)):
        return None
    _release(slots, int(config["indexes"]["release_type"]), type_info)
    return [int(item) for item in dims]


def _generate(
    slots: Any,
    config: dict[str, Any],
    session: ctypes.c_void_p,
    inputs: list[str],
    outputs: list[str],
    shapes: dict[str, list[int]],
    memory: ctypes.c_void_p,
    prompt: list[int],
    phase: str,
) -> dict[str, Any] | None:
    _mark(phase)
    deadline = time.monotonic() + float(config["generationBudgetSeconds"])
    generated: list[int] = []
    cache: dict[str, tuple[Any, list[int]]] = {}
    first: float | None = None
    started = time.monotonic()
    tokens = list(prompt)
    while len(generated) < int(config["maxNewTokens"]):
        if time.monotonic() > deadline:
            config["timedOut"] = True
            return None
        past_len = 0 if not generated else len(prompt) + len(generated) - 1
        current = tokens if not generated else [generated[-1]]
        values = _bind_inputs(slots, config, inputs, shapes, memory, current, past_len, cache)
        if values is None:
            return None
        produced = _invoke(slots, config, session, inputs, outputs, values)
        if produced is None:
            return None
        logits, cache = produced
        if first is None:
            first = time.monotonic() - started
        generated.append(logits)
        if logits == int(config["eosTokenId"]):
            break
    _mark(phase)
    return {
        "firstTokenSeconds": first,
        "generationSeconds": time.monotonic() - started,
        "inputTokenCount": len(prompt),
        "newTokens": generated,
        "textTokens": [item for item in generated if item != int(config["eosTokenId"])],
    }


def _resolve(name: str, dims: list[int], past_len: int, seq_len: int) -> list[int]:
    total = past_len + seq_len
    if name == "input_ids":
        return [1, seq_len]
    if name in {"attention_mask", "position_ids"}:
        return [1, total if name == "attention_mask" else seq_len]
    dynamic = 0
    resolved: list[int] = []
    for dim in dims:
        if dim > 0:
            resolved.append(dim)
            continue
        dynamic += 1
        if name.startswith("past_key_values") and dynamic >= 2:
            resolved.append(past_len)
        else:
            resolved.append(1)
    return resolved


def _bind_inputs(
    slots: Any,
    config: dict[str, Any],
    names: list[str],
    shapes: dict[str, list[int]],
    memory: ctypes.c_void_p,
    current: list[int],
    past_len: int,
    cache: dict[str, tuple[Any, list[int]]],
) -> list[ctypes.c_void_p] | None:
    values: list[ctypes.c_void_p] = []
    kept: list[Any] = []
    for name in names:
        shape = _resolve(name, shapes[name], past_len, len(current))
        if name == "input_ids":
            array: Any = (ctypes.c_int64 * len(current))(*current)
            element = _INT64
        elif name == "attention_mask":
            array = (ctypes.c_int64 * (past_len + len(current)))(*([1] * (past_len + len(current))))
            element = _INT64
        elif name == "position_ids":
            start = past_len
            array = (ctypes.c_int64 * len(current))(*range(start, start + len(current)))
            element = _INT64
        elif name in cache:
            array, shape = cache[name]
            element = _FLOAT
        else:
            count = 1
            for dim in shape:
                count *= dim
            array = (ctypes.c_float * count)()
            element = _FLOAT
        value = _tensor(slots, config, memory, array, shape, element)
        if value is None:
            return None
        values.append(value)
        kept.append(array)
    config["_kept"] = kept
    return values


def _tensor(
    slots: Any,
    config: dict[str, Any],
    memory: ctypes.c_void_p,
    array: Any,
    shape: list[int],
    element: int,
) -> ctypes.c_void_p | None:
    count = 1
    for dim in shape:
        count *= dim
    width = 8 if element == _INT64 else 4
    data = ctypes.cast(array, ctypes.c_void_p)
    if count == 0:
        dummy = ctypes.c_byte(0)
        config["_dummy"] = dummy
        data = ctypes.cast(ctypes.pointer(dummy), ctypes.c_void_p)
    shape_array = (ctypes.c_int64 * len(shape))(*shape)
    config["_shape"] = shape_array
    out = ctypes.c_void_p()
    kind = ctypes.CFUNCTYPE(
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_int64),
        ctypes.c_size_t,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_void_p),
    )
    status = kind(slots[int(config["indexes"]["tensor"])])(
        memory,
        data,
        count * width,
        shape_array,
        len(shape),
        element,
        ctypes.byref(out),
    )
    if status:
        return None
    return out


def _invoke(
    slots: Any,
    config: dict[str, Any],
    session: ctypes.c_void_p,
    inputs: list[str],
    outputs: list[str],
    values: list[ctypes.c_void_p],
) -> tuple[int, dict[str, tuple[Any, list[int]]]] | None:
    input_names = (ctypes.c_char_p * len(inputs))(*[item.encode("utf-8") for item in inputs])
    output_names = (ctypes.c_char_p * len(outputs))(*[item.encode("utf-8") for item in outputs])
    input_values = (ctypes.c_void_p * len(values))(*values)
    output_values = (ctypes.c_void_p * len(outputs))()
    kind = ctypes.CFUNCTYPE(
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_char_p),
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_char_p),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_void_p),
    )
    config["runInvoked"] = True
    status = kind(slots[int(config["indexes"]["run"])])(
        session,
        None,
        input_names,
        input_values,
        len(inputs),
        output_names,
        len(outputs),
        output_values,
    )
    if status:
        return None
    cache: dict[str, tuple[Any, list[int]]] = {}
    chosen: int | None = None
    for index, name in enumerate(outputs):
        raw_output = output_values[index]
        if not isinstance(raw_output, int):
            return None
        produced = ctypes.c_void_p(raw_output)
        pointer = _data_pointer(slots, config, produced)
        dims = _value_dims(slots, config, produced)
        if pointer is None or dims is None:
            return None
        if name == "logits":
            sequence = dims[1] if len(dims) >= 2 else 1
            vocab = dims[-1] if dims else _VOCAB
            chosen = argmax_last(pointer, sequence, vocab)
        else:
            mapped = past_name(name)
            if mapped is None:
                return None
            count = 1
            for dim in dims:
                count *= max(dim, 0)
            buffer = (ctypes.c_float * count)()
            if count:
                ctypes.memmove(buffer, pointer, count * 4)
            cache[mapped] = (buffer, dims)
        _release(slots, int(config["indexes"]["release_value"]), produced)
    for value in values:
        _release(slots, int(config["indexes"]["release_value"]), value)
    if chosen is None:
        return None
    return chosen, cache


def _data_pointer(slots: Any, config: dict[str, Any], value: ctypes.c_void_p) -> int | None:
    out = ctypes.c_void_p()
    kind = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
    if kind(slots[int(config["indexes"]["mutable_data"])])(value, ctypes.byref(out)):
        return None
    return int(out.value or 0)


def _value_dims(slots: Any, config: dict[str, Any], value: ctypes.c_void_p) -> list[int] | None:
    info = ctypes.c_void_p()
    kind = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
    if kind(slots[int(config["indexes"]["tensor_shape"])])(value, ctypes.byref(info)):
        return None
    count = ctypes.c_size_t()
    count_kind = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t))
    if count_kind(slots[int(config["indexes"]["dimensions_count"])])(info, ctypes.byref(count)):
        return None
    dims = (ctypes.c_int64 * int(count.value))()
    dim_kind = ctypes.CFUNCTYPE(
        ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int64), ctypes.c_size_t
    )
    if dim_kind(slots[int(config["indexes"]["dimensions"])])(info, dims, int(count.value)):
        return None
    _release(slots, int(config["indexes"]["release_tensor_info"]), info)
    return [int(item) for item in dims]


def _emit(config: dict[str, Any], generated: dict[str, Any]) -> None:
    if str(config.get("promptConstruction")) != "protocol-request":
        payload = {
            "inputTokenCount": generated["inputTokenCount"],
            "newTokenCount": len(generated["newTokens"]),
            "outputDigest": _digest(generated["newTokens"]),
            "phase": config.get("phase"),
            "status": "ok",
        }
        sys_stdout(payload)
        return
    text = _decode_text(generated["textTokens"])
    request = config["request"]
    try:
        parsed, end = json.JSONDecoder().raw_decode(text.strip())
    except json.JSONDecodeError:
        parsed, end = {"explanationText": text[:400]}, len(text)
    if not isinstance(parsed, dict) or end < 0:
        parsed = {"explanationText": text[:400]}
    envelope = {
        "candidateId": config["harnessCandidateId"],
        "candidateVersion": config["protocolCandidateVersion"],
        "findingExplanationOutput": parsed,
        "protocolVersion": "1.0.0",
        "requestId": request["requestId"],
        "schemaVersion": "1.0.0",
        "status": "success",
    }
    sys_stdout(envelope)


def _decode_text(token_ids: list[int]) -> str:
    tokenizer = _tokenizer()
    if tokenizer is None:
        return ""
    try:
        return str(tokenizer.decode(token_ids))
    except (ValueError, KeyError):
        return ""


def sys_stdout(payload: dict[str, Any]) -> None:
    import sys

    sys.stdout.write(_canonical(payload))


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _digest(token_ids: list[int]) -> str:
    return hashlib.sha256(_canonical(token_ids).encode("utf-8")).hexdigest()


def _stamp(report: dict[str, Any], config: dict[str, Any] | None) -> None:
    """Copy session flags onto the report. The report still omits prompt text."""
    if config is None:
        report["modelSessionCreated"] = False
        report["runInvoked"] = False
        return
    report["modelSessionCreated"] = bool(config.get("modelSessionCreated"))
    report["runInvoked"] = bool(config.get("runInvoked"))


def _finish(report: dict[str, Any], started: float) -> None:
    report.pop("exitCode", None)
    report.pop("_kept", None)
    report.pop("_dummy", None)
    report.pop("_shape", None)
    report["wallSeconds"] = time.monotonic() - started
    Path("/results/report.json").write_text(_canonical(report), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
