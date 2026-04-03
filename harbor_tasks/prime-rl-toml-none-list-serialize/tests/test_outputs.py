"""
Task: prime-rl-toml-none-list-serialize
Repo: PrimeIntellect-ai/prime-rl @ a25b3e7a18e76999558a888c1ab1f8e5cd0e3831
PR:   2094

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
from pathlib import Path

REPO = "/workspace/prime-rl"
CONFIG_PY = Path(f"{REPO}/src/prime_rl/utils/config.py")


TARGET_FUNCS = {"none_to_none_str", "_convert_none"}


def _load_config_functions():
    """Extract target functions from config.py and exec them.

    AST-only because: config.py imports pydantic_config and pydantic at module level,
    which pull in heavy deps that may not be fully installed in the test env.
    The target functions (none_to_none_str, _convert_none) are pure Python.
    """
    src = CONFIG_PY.read_text()
    tree = ast.parse(src)

    func_sources = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name in TARGET_FUNCS:
            func_sources.append(ast.get_source_segment(src, node))

    namespace = {}
    exec("\n\n".join(func_sources), namespace)
    return namespace


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """config.py must parse without syntax errors."""
    import py_compile

    py_compile.compile(str(CONFIG_PY), doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_none_inside_flat_list():
    """None values inside a flat list are converted to 'None' strings."""
    ns = _load_config_functions()
    none_to_none_str = ns["none_to_none_str"]

    assert none_to_none_str({"k": [None, "a", None]}) == {"k": ["None", "a", "None"]}
    assert none_to_none_str({"x": [1, None, "b", None, 3]}) == {
        "x": [1, "None", "b", "None", 3]
    }
    assert none_to_none_str({"single": [None]}) == {"single": ["None"]}


# [pr_diff] fail_to_pass
def test_none_inside_dict_in_list():
    """None inside a dict nested in a list is converted."""
    ns = _load_config_functions()
    none_to_none_str = ns["none_to_none_str"]

    assert none_to_none_str({"k": [{"n": None, "ok": 1}]}) == {
        "k": [{"n": "None", "ok": 1}]
    }
    assert none_to_none_str({"d": [{"a": None}, {"b": None, "c": 2}]}) == {
        "d": [{"a": "None"}, {"b": "None", "c": 2}]
    }


# [pr_diff] fail_to_pass
def test_deeply_nested_list_of_list():
    """Deeply nested None (list of list) is converted."""
    ns = _load_config_functions()
    none_to_none_str = ns["none_to_none_str"]

    assert none_to_none_str({"k": [[None, 1], [2, None]]}) == {
        "k": [["None", 1], [2, "None"]]
    }
    assert none_to_none_str({"matrix": [[None, None], [None, None]]}) == {
        "matrix": [["None", "None"], ["None", "None"]]
    }
    assert none_to_none_str({"deep": [[[None, 1], [2, None]]]}) == {
        "deep": [[["None", 1], [2, "None"]]]
    }
    assert none_to_none_str({"mixed": [None, [None, 1], [2, [None]]]}) == {
        "mixed": ["None", ["None", 1], [2, ["None"]]]
    }


# [pr_diff] fail_to_pass
def test_toml_roundtrip_with_none_in_list():
    """TOML serialization succeeds after converting None in lists."""
    import tomli_w

    ns = _load_config_functions()
    none_to_none_str = ns["none_to_none_str"]

    # Input 1: flat list with None
    data1 = {"items": [None, "hello", None]}
    toml1 = tomli_w.dumps(none_to_none_str(data1))
    assert toml1.count("None") >= 2

    # Input 2: nested dict+list combo
    data2 = {
        "section": {"items": [None, "hello", None], "nested": {"vals": [1, None]}}
    }
    toml2 = tomli_w.dumps(none_to_none_str(data2))
    assert "None" in toml2

    # Input 3: list of dicts with None values
    data3 = {"configs": [{"timeout": None}, {"name": "main", "val": None}]}
    toml3 = tomli_w.dumps(none_to_none_str(data3))
    assert toml3.count("None") >= 2


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_top_level_none_converted():
    """Top-level None values are still converted (existing behavior)."""
    ns = _load_config_functions()
    none_to_none_str = ns["none_to_none_str"]

    assert none_to_none_str({"a": None, "b": "hello"}) == {"a": "None", "b": "hello"}
    assert none_to_none_str({"x": None, "y": None}) == {"x": "None", "y": "None"}


# [repo_tests] pass_to_pass
def test_nested_dict_none_converted():
    """Nested dict None values are still converted."""
    ns = _load_config_functions()
    none_to_none_str = ns["none_to_none_str"]

    assert none_to_none_str({"outer": {"inner": None, "val": 42}}) == {
        "outer": {"inner": "None", "val": 42}
    }


# [repo_tests] pass_to_pass
def test_non_none_values_unchanged():
    """Non-None values pass through without modification."""
    ns = _load_config_functions()
    none_to_none_str = ns["none_to_none_str"]

    data = {"a": 1, "b": "str", "c": [1, 2], "d": {"e": True}}
    assert none_to_none_str(data) == data


# ---------------------------------------------------------------------------
# Anti-stub (static, pass_to_pass)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """none_to_none_str returns a dict and preserves all keys (not just pass/None)."""
    ns = _load_config_functions()
    none_to_none_str = ns["none_to_none_str"]

    assert callable(none_to_none_str)
    result = none_to_none_str({"a": None, "b": 1, "c": "hello"})
    assert isinstance(result, dict)
    assert set(result.keys()) == {"a", "b", "c"}
    assert result["a"] == "None"
    assert result["b"] == 1
    assert result["c"] == "hello"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:5 @ a25b3e7
def test_no_unnecessary_try_except():
    """No try/except blocks in config.py (AGENTS.md: let errors propagate)."""
    src = CONFIG_PY.read_text()
    tree = ast.parse(src)
    try_blocks = [n for n in ast.walk(tree) if isinstance(n, ast.Try)]
    assert len(try_blocks) == 0, (
        f"Found {len(try_blocks)} try/except — AGENTS.md says avoid unless necessary"
    )


# [agent_config] pass_to_pass — AGENTS.md:7 @ a25b3e7
def test_no_work_process_comments():
    """No comments referencing old code or work process (AGENTS.md: targeted comments only)."""
    content = CONFIG_PY.read_text()
    bad_patterns = [
        r"#.*used to.*but now",
        r"#.*old code",
        r"#.*previous(ly)?",
        r"#.*was originally",
        r"#.*changed from",
        r"#.*refactored",
    ]
    for pat in bad_patterns:
        m = re.search(pat, content, re.IGNORECASE)
        assert m is None, f"Found work-process comment: {m.group()}"
