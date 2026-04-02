"""
Task: areal-megatron-bridge-duplicate-kwarg
Repo: inclusionAI/AReaL @ 722e235a37e4a9f3e288e54629179befa494156b
PR:   #1107

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
from pathlib import Path

FILE = Path("/workspace/AReaL/areal/engine/megatron_engine.py")


def _parse_file():
    """Helper: parse the file into an AST. Raises on SyntaxError."""
    # AST-only because: module requires torch, megatron-core, GPU libs — cannot be imported
    return ast.parse(FILE.read_text())


# ---------------------------------------------------------------------------
# Fail-to-pass — file must parse (duplicate kwarg = SyntaxError on base)
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_file_parses():
    """megatron_engine.py must be valid Python syntax."""
    import py_compile

    py_compile.compile(str(FILE), doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_no_duplicate_kwargs():
    """No function call in the file has duplicate keyword arguments."""
    # AST-only because: module requires torch/megatron-core, cannot be imported
    tree = _parse_file()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            kwarg_names = [kw.arg for kw in node.keywords if kw.arg is not None]
            seen = set()
            for k in kwarg_names:
                assert k not in seen, (
                    f"Duplicate keyword argument '{k}' at line {node.lineno}"
                )
                seen.add(k)


# [pr_diff] fail_to_pass
def test_from_hf_pretrained_trust_remote_code():
    """from_hf_pretrained() passes trust_remote_code exactly once."""
    # AST-only because: module requires torch/megatron-core, cannot be imported
    tree = _parse_file()
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if hasattr(node.func, "attr") and node.func.attr == "from_hf_pretrained":
                found = True
                count = sum(
                    1 for kw in node.keywords if kw.arg == "trust_remote_code"
                )
                assert count == 1, (
                    f"Expected trust_remote_code exactly once, found {count}"
                )
    assert found, "from_hf_pretrained call not found"


# [pr_diff] fail_to_pass
def test_from_hf_pretrained_has_dtype():
    """from_hf_pretrained() passes a dtype argument."""
    # AST-only because: module requires torch/megatron-core, cannot be imported
    tree = _parse_file()
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if hasattr(node.func, "attr") and node.func.attr == "from_hf_pretrained":
                found = True
                has_dtype = any(kw.arg == "dtype" for kw in node.keywords)
                assert has_dtype, "from_hf_pretrained missing dtype argument"
    assert found, "from_hf_pretrained call not found"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_mbridge_path_has_trust_remote_code():
    """mbridge from_pretrained call still passes trust_remote_code (text-based)."""
    # Text-based so it works even when file has SyntaxError (base commit).
    source = FILE.read_text()
    assert "mbridge" in source, "mbridge reference missing"
    assert "from_pretrained" in source, "from_pretrained call missing"
    lines = source.splitlines()
    for i, line in enumerate(lines):
        if "mbridge" in line and "from_pretrained" in line:
            block = "\n".join(lines[i : i + 5])
            assert "trust_remote_code" in block, (
                "mbridge from_pretrained missing trust_remote_code"
            )
            return
    assert False, "mbridge from_pretrained call not found"


# [pr_diff] pass_to_pass
def test_megatron_bridge_path_exists():
    """The 'megatron-bridge' code path is still present in the file."""
    source = FILE.read_text()
    assert '"megatron-bridge"' in source or "'megatron-bridge'" in source, (
        "megatron-bridge code path was deleted instead of fixed"
    )


# [static] pass_to_pass
def test_method_not_stubbed():
    """_build_hf_mcore_bridge exists and has substantial content (text-based)."""
    source = FILE.read_text()
    assert "def _build_hf_mcore_bridge" in source, (
        "_build_hf_mcore_bridge method not found"
    )
    lines = source.splitlines()
    in_method = False
    body_lines = 0
    method_indent = 0
    for line in lines:
        if "def _build_hf_mcore_bridge" in line:
            in_method = True
            method_indent = len(line) - len(line.lstrip())
            continue
        if in_method:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(line) - len(line.lstrip())
            if indent <= method_indent and stripped:
                break
            body_lines += 1
    assert body_lines >= 5, (
        f"Method has only {body_lines} body lines — looks stubbed"
    )


# [static] pass_to_pass
def test_file_not_gutted():
    """File has not been gutted (must have > 300 lines)."""
    line_count = len(FILE.read_text().splitlines())
    assert line_count > 300, f"File has only {line_count} lines — suspiciously small"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:30 @ 722e235
def test_no_wildcard_imports():
    """No wildcard imports (from x import *)."""
    source = FILE.read_text()
    for i, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        assert not re.match(r"from\s+\S+\s+import\s+\*", stripped), (
            f"Wildcard import found at line {i}: {stripped}"
        )


# [agent_config] pass_to_pass — AGENTS.md:90 @ 722e235
def test_no_bare_print_in_method():
    """_build_hf_mcore_bridge uses self.logger, not bare print() calls."""
    # AGENTS.md:90 — "Logging: areal.utils.logging.getLogger(name) ... never print"
    # Text-based so it works even on base (SyntaxError).
    source = FILE.read_text()
    lines = source.splitlines()
    in_method = False
    method_indent = 0
    for i, line in enumerate(lines, 1):
        if "def _build_hf_mcore_bridge" in line:
            in_method = True
            method_indent = len(line) - len(line.lstrip())
            continue
        if in_method:
            stripped = line.strip()
            indent = len(line) - len(line.lstrip())
            if indent <= method_indent and stripped and not stripped.startswith("#"):
                break
            if re.match(r"print\s*\(", stripped):
                assert False, (
                    f"Bare print() at line {i} — use self.logger instead (AGENTS.md:90)"
                )
