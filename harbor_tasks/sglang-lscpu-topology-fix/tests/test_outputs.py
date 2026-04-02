"""
Task: sglang-lscpu-topology-fix
Repo: sgl-project/sglang @ 069c7e4188aca6ef69c0b81dfa05abba49685946
PR:   18520

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import textwrap
import unittest.mock
from pathlib import Path

REPO = "/workspace/sglang"
TARGET = f"{REPO}/python/sglang/srt/utils/common.py"


def _get_parse_func():
    """Extract parse_lscpu_topology from source and return a callable."""
    import logging

    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger("test")

    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "parse_lscpu_topology":
            func_node = node
            break

    assert func_node is not None, "parse_lscpu_topology not found in source"

    lines = source.splitlines(keepends=True)
    func_src = textwrap.dedent("".join(lines[func_node.lineno - 1 : func_node.end_lineno]))

    ns = {"subprocess": subprocess, "logger": logger, "__builtins__": __builtins__}
    exec(func_src, ns)
    return ns["parse_lscpu_topology"]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without syntax errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)  # raises SyntaxError on failure


# [static] pass_to_pass
def test_not_stub():
    """parse_lscpu_topology has real logic, not just pass/return."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "parse_lscpu_topology":
            stmts = [
                s
                for s in ast.walk(node)
                if isinstance(s, (ast.Assign, ast.AugAssign, ast.For, ast.If, ast.Return, ast.Call, ast.Try))
            ]
            assert len(stmts) >= 8, f"Function too short ({len(stmts)} AST nodes), likely stubbed"
            func_source = ast.get_source_segment(source, node) or ""
            assert "subprocess" in func_source or "check_output" in func_source, (
                "No subprocess call found -- function likely stubbed"
            )
            return

    raise AssertionError("parse_lscpu_topology not found")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_malformed_lines_skipped():
    """Lines with != 4 fields must be skipped, not crash."""
    parse = _get_parse_func()

    mock_output = (
        "# CPU,Core,Socket,Node\n"
        "0,0,0,0\n"
        "1,1,0,0\n"
        "bad_line_no_commas\n"
        "2,2\n"
        "3,3,1,1,extra_field\n"
        "\n"
    )

    with unittest.mock.patch("subprocess.check_output", return_value=mock_output):
        result = parse()

    assert result is not None, "Function returned None"
    assert len(result) >= 2, f"Expected at least 2 entries from valid lines, got {len(result)}"
    values = [(e[0], e[1], e[2], e[3]) for e in result]
    assert (0, 0, 0, 0) in values, f"(0,0,0,0) not in {values}"
    assert (1, 1, 0, 0) in values, f"(1,1,0,0) not in {values}"


# [pr_diff] fail_to_pass
def test_empty_fields_default_to_zero():
    """Lines like '0,1,,0' must not raise ValueError on int('')."""
    parse = _get_parse_func()

    mock_output = (
        "# CPU,Core,Socket,Node\n"
        "0,1,,0\n"
        "1,,,\n"
        "2,2,1,1\n"
    )

    with unittest.mock.patch("subprocess.check_output", return_value=mock_output):
        result = parse()

    assert result is not None, "Function returned None"
    values = [(e[0], e[1], e[2], e[3]) for e in result]
    # Empty fields must default to 0
    assert (0, 1, 0, 0) in values, f"(0,1,,0) should parse as (0,1,0,0), got {values}"
    assert (1, 0, 0, 0) in values, f"(1,,,) should parse as (1,0,0,0), got {values}"
    assert (2, 2, 1, 1) in values, f"Valid line (2,2,1,1) not in {values}"


# [pr_diff] fail_to_pass
def test_mixed_valid_invalid_input():
    """Valid lines parse correctly even when surrounded by bad lines."""
    parse = _get_parse_func()

    mock_output = (
        "# CPU,Core,Socket,Node\n"
        "0,0,0,0\n"
        "only_text\n"
        "1,1,0,0\n"
        ",,\n"
        "2,2,1,1\n"
        "4,4,1,1\n"
        "5,5,2\n"
    )

    with unittest.mock.patch("subprocess.check_output", return_value=mock_output):
        result = parse()

    assert result is not None, "Function returned None"
    assert len(result) >= 4, f"Expected at least 4 valid entries, got {len(result)}"
    values = [(e[0], e[1], e[2], e[3]) for e in result]
    assert (0, 0, 0, 0) in values, f"(0,0,0,0) not in {values}"
    assert (1, 1, 0, 0) in values, f"(1,1,0,0) not in {values}"
    assert (2, 2, 1, 1) in values, f"(2,2,1,1) not in {values}"
    assert (4, 4, 1, 1) in values, f"(4,4,1,1) not in {values}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_normal_input_parsed():
    """Normal 4-field input is parsed with correct values."""
    parse = _get_parse_func()

    mock_output = (
        "# CPU,Core,Socket,Node\n"
        "0,0,0,0\n"
        "1,1,0,0\n"
        "2,2,1,1\n"
        "3,3,1,1\n"
    )

    with unittest.mock.patch("subprocess.check_output", return_value=mock_output):
        result = parse()

    assert result is not None and len(result) == 4, f"Expected 4 entries, got {result}"
    assert result[0] == (0, 0, 0, 0), f"Entry 0 wrong: {result[0]}"
    assert result[2] == (2, 2, 1, 1), f"Entry 2 wrong: {result[2]}"
    assert result[3] == (3, 3, 1, 1), f"Entry 3 wrong: {result[3]}"


# [pr_diff] pass_to_pass
def test_multi_socket_topology():
    """8-CPU multi-socket topology parses correctly."""
    parse = _get_parse_func()

    mock_output = (
        "# CPU,Core,Socket,Node\n"
        "0,0,0,0\n"
        "1,0,0,0\n"
        "2,1,0,0\n"
        "3,1,0,0\n"
        "4,2,1,1\n"
        "5,2,1,1\n"
        "6,3,1,1\n"
        "7,3,1,1\n"
    )

    with unittest.mock.patch("subprocess.check_output", return_value=mock_output):
        result = parse()

    assert result is not None and len(result) == 8, f"Expected 8 entries, got {len(result) if result else None}"
    assert result[0][:3] == (0, 0, 0), f"Entry 0 wrong: {result[0]}"
    assert result[4] == (4, 2, 1, 1), f"Entry 4 wrong: {result[4]}"
    assert result[7][:2] == (7, 3), f"Entry 7 wrong: {result[7]}"
