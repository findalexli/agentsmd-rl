"""
Task: prime-rl-config-none-toml-serialize
Repo: PrimeIntellect-ai/prime-rl @ 692dfc8a4b9471e65004d8ac154d07ebb73bc61c
PR:   #2093

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import copy
import io
import textwrap
import tomllib
from pathlib import Path

import tomli_w

REPO = "/workspace/prime-rl"
CONFIG_PY = Path(f"{REPO}/src/prime_rl/utils/config.py")
ENTRYPOINTS = ["inference", "rl", "sft"]


def _find_converter():
    """Extract the None-to-string converter from config.py via AST+exec.

    Uses AST extraction so the test is immune to pydantic/pydantic_config
    import failures — the converter is pure Python and needs no imports.
    Returns None if no suitable converter function exists (base commit).
    """
    source = CONFIG_PY.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        # Must accept a dict and return a dict (no heavy deps needed)
        lines = source.splitlines()
        func_src = "\n".join(lines[node.lineno - 1 : node.end_lineno])
        func_src = textwrap.dedent(func_src)
        ns: dict = {}
        try:
            exec(func_src, ns)  # noqa: S102
        except Exception:
            continue
        func = ns.get(node.name)
        if not callable(func):
            continue
        try:
            result = func({"test": None, "ok": 1})
            if (
                isinstance(result, dict)
                and result.get("test") == "None"
                and result.get("ok") == 1
            ):
                return func
        except Exception:
            continue
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files (config.py, all entrypoints) must parse without errors."""
    files = [CONFIG_PY] + [
        Path(f"{REPO}/src/prime_rl/entrypoints/{ep}.py") for ep in ENTRYPOINTS
    ]
    for f in files:
        ast.parse(f.read_text())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_flat_none_conversion():
    """Flat dict None values are converted to 'None' strings."""
    conv = _find_converter()
    assert conv is not None, "No None-to-string conversion function found in config.py"

    assert conv({"a": None, "b": 42, "c": "hello", "d": None}) == {
        "a": "None",
        "b": 42,
        "c": "hello",
        "d": "None",
    }
    assert conv({"x": None}) == {"x": "None"}
    assert conv({"p": 0, "q": None, "r": False}) == {"p": 0, "q": "None", "r": False}


# [pr_diff] fail_to_pass
def test_nested_none_conversion():
    """Nested dict None values are converted recursively."""
    conv = _find_converter()
    assert conv is not None, "No conversion function found"

    result = conv(
        {"top": None, "nested": {"a": None, "b": 1, "deep": {"x": None, "y": "ok"}}}
    )
    assert result["top"] == "None"
    assert result["nested"]["a"] == "None"
    assert result["nested"]["b"] == 1
    assert result["nested"]["deep"]["x"] == "None"
    assert result["nested"]["deep"]["y"] == "ok"

    # Two levels deep, multiple None values
    result2 = conv({"l1": {"l2": {"v": None}}, "other": None})
    assert result2["l1"]["l2"]["v"] == "None"
    assert result2["other"] == "None"


# [pr_diff] fail_to_pass
def test_toml_roundtrip():
    """TOML round-trip preserves None as 'None' string."""
    conv = _find_converter()
    assert conv is not None, "No conversion function found"

    for d in [
        {"model": {"name": "test", "max_len": None}, "seed": None, "lr": 0.001},
        {"a": None, "b": {"c": None, "d": 1}},
        {"top": None},
    ]:
        converted = conv(d)
        buf = io.BytesIO()
        tomli_w.dump(converted, buf)
        buf.seek(0)
        loaded = tomllib.load(buf)
        # Every original None must come back as "None" string
        def check_none(orig, loaded_d):
            for k, v in orig.items():
                if v is None:
                    assert loaded_d[k] == "None", f"{k} not preserved as 'None'"
                elif isinstance(v, dict):
                    check_none(v, loaded_d[k])
                else:
                    assert loaded_d[k] == v, f"{k} changed unexpectedly"
        check_none(d, loaded)


# [pr_diff] fail_to_pass
def test_edge_cases():
    """Handles empty dicts, all-None, bools, lists; does not mutate input."""
    conv = _find_converter()
    assert conv is not None, "No conversion function found"

    assert conv({}) == {}
    assert conv({"a": None}) == {"a": "None"}
    assert conv({"a": {"b": None}}) == {"a": {"b": "None"}}
    # Lists passed through unchanged
    assert conv({"x": [1, 2, 3]}) == {"x": [1, 2, 3]}
    # Bools preserved
    assert conv({"x": True, "y": False}) == {"x": True, "y": False}
    # Ints/strings preserved
    assert conv({"n": 0, "s": ""}) == {"n": 0, "s": ""}

    # Non-mutation check
    original = {"a": None, "b": 1, "nested": {"c": None}}
    original_copy = copy.deepcopy(original)
    conv(original)
    assert original == original_copy, "Function must not mutate input dict"


# [pr_diff] fail_to_pass
def test_entrypoints_no_exclude_none():
    """Entrypoints no longer use exclude_none=True in model_dump calls."""
    for ep in ENTRYPOINTS:
        path = Path(f"{REPO}/src/prime_rl/entrypoints/{ep}.py")
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == "model_dump":
                    for kw in node.keywords:
                        if kw.arg == "exclude_none":
                            if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                raise AssertionError(
                                    f"{ep}.py still uses exclude_none=True in model_dump"
                                )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_non_none_passthrough():
    """Non-None config values serialize identically after conversion."""
    conv = _find_converter()
    assert conv is not None, "No conversion function found"

    for d in [
        {"model": {"name": "Qwen/Qwen3-0.6B", "max_model_len": 4096, "eager": True},
         "seed": 42},
        {"port": 8000, "host": "0.0.0.0"},
        {"x": 1, "y": 2.5, "z": "hello"},
    ]:
        assert conv(d) == d, f"Non-None values changed: {d}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:5 @ 692dfc8a
def test_no_try_except_in_converter():
    """Conversion function must not use try/except (AGENTS.md rule)."""
    source = CONFIG_PY.read_text()
    tree = ast.parse(source)
    # Find the converter function(s) — any FunctionDef that deals with None conversion
    conv = _find_converter()
    if conv is None:
        return  # Not yet added (base commit) — nothing to check
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == conv.__name__:
            tries = [n for n in ast.walk(node) if isinstance(n, ast.Try)]
            assert not tries, (
                f"{node.name} uses try/except (violates AGENTS.md:5 — "
                "avoid try/except unless truly necessary)"
            )


# [agent_config] pass_to_pass — AGENTS.md:7 @ 692dfc8a
def test_no_process_comments():
    """Changed files must not contain comments referring to old code or work process (AGENTS.md rule)."""
    import re

    process_patterns = re.compile(
        r"#.*\b(previously|used to|was changed|old code|removed|replaced with|"
        r"changed from|refactored|updated to|modified to|before this|original)\b",
        re.IGNORECASE,
    )
    files = [CONFIG_PY] + [
        Path(f"{REPO}/src/prime_rl/entrypoints/{ep}.py") for ep in ENTRYPOINTS
    ]
    for f in files:
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if process_patterns.search(line):
                raise AssertionError(
                    f"{f.name}:{i} has process-referencing comment "
                    f"(violates AGENTS.md:7): {line.strip()!r}"
                )
