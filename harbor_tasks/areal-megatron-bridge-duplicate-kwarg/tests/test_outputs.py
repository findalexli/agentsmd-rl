"""
Task: areal-megatron-bridge-duplicate-kwarg
Repo: inclusionAI/AReaL @ 722e235a37e4a9f3e288e54629179befa494156b
PR:   #1107

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import py_compile
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/AReaL")
FILE = REPO / "areal/engine/megatron_engine.py"


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via subprocess (isolated from this process)."""
    preamble = f"FILE = Path({str(FILE)!r})\nREPO = Path({str(REPO)!r})\n"
    return subprocess.run(
        ["python3", "-c", "from pathlib import Path\n" + preamble + code],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# -----------------------------------------------------------------------------
# Fail-to-pass — subprocess-based behavioral tests
# -----------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_file_parses():
    """megatron_engine.py compiles without SyntaxError (duplicate kwarg = SyntaxError on base)."""
    r = _run_python("import py_compile; py_compile.compile(FILE, doraise=True)")
    assert r.returncode == 0, f"Compile failed: {r.stderr}"


# [pr_diff] fail_to_pass
def test_no_duplicate_kwargs():
    """No function call in the file has duplicate keyword arguments."""
    r = _run_python(
        """\
import ast
tree = ast.parse(open(FILE).read())
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        names = [kw.arg for kw in node.keywords if kw.arg is not None]
        seen = set()
        for k in names:
            assert k not in seen, 'Duplicate keyword argument at line ' + str(node.lineno)
            seen.add(k)
"""
    )
    assert r.returncode == 0, f"Duplicate kwargs found: {r.stderr}"


# [pr_diff] fail_to_pass
def test_from_hf_pretrained_trust_remote_code():
    """from_hf_pretrained() passes trust_remote_code exactly once."""
    r = _run_python(
        """\
import ast
tree = ast.parse(open(FILE).read())
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and hasattr(node.func, 'attr') and node.func.attr == 'from_hf_pretrained':
        found = True
        count = sum(1 for kw in node.keywords if kw.arg == 'trust_remote_code')
        assert count == 1, 'Expected trust_remote_code exactly once, found ' + str(count)
assert found, 'from_hf_pretrained call not found'
"""
    )
    assert r.returncode == 0, f"Check failed: {r.stderr}"


# [pr_diff] fail_to_pass
def test_from_hf_pretrained_has_dtype():
    """from_hf_pretrained() passes a dtype argument."""
    r = _run_python(
        """\
import ast
tree = ast.parse(open(FILE).read())
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and hasattr(node.func, 'attr') and node.func.attr == 'from_hf_pretrained':
        found = True
        has_dtype = any(kw.arg == 'dtype' for kw in node.keywords)
        assert has_dtype, 'from_hf_pretrained missing dtype argument'
assert found, 'from_hf_pretrained call not found'
"""
    )
    assert r.returncode == 0, f"Check failed: {r.stderr}"


# -----------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — text-based, works on both base and fix
# -----------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_mbridge_path_has_trust_remote_code():
    """mbridge from_pretrained call still passes trust_remote_code (text-based)."""
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


# -----------------------------------------------------------------------------
# Config-derived (agent_config)
# -----------------------------------------------------------------------------


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


# -----------------------------------------------------------------------------
# Repo CI/CD pass-to-pass gates (ensure fix doesn't break existing functionality)
# -----------------------------------------------------------------------------


# [repo_ci] pass_to_pass — pyproject.toml syntax validation
def test_repo_pyproject_toml_valid():
    """pyproject.toml is valid TOML syntax (pass_to_pass)."""
    r = _run_python(
        """\
import tomllib
with open(REPO / 'pyproject.toml', 'rb') as f:
    tomllib.load(f)
print('pyproject.toml is valid TOML')
"""
    )
    assert r.returncode == 0, f"pyproject.toml TOML validation failed:\n{r.stderr}"


# [repo_ci] pass_to_pass — ruff linter check (when syntax is valid)
def test_repo_ruff_lint():
    """Ruff linter passes on megatron_engine.py (pass_to_pass)."""
    # First ensure file compiles (syntax is valid) - this will be tested by test_file_parses
    r = _run_python("import py_compile; py_compile.compile(FILE, doraise=True)")
    if r.returncode != 0:
        pytest.skip("File has syntax errors - skipping ruff lint")
    # Try to install ruff
    subprocess.run(
        ["pip", "install", "ruff==0.14.9", "-q"],
        capture_output=True,
        timeout=60,
    )
    r = subprocess.run(
        ["python3", "-m", "ruff", "check", "--output-format=concise", str(FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_ci] pass_to_pass — ruff format check (when syntax is valid)
def test_repo_ruff_format():
    """Ruff format check passes on megatron_engine.py (pass_to_pass)."""
    # First ensure file compiles (syntax is valid)
    r = _run_python("import py_compile; py_compile.compile(FILE, doraise=True)")
    if r.returncode != 0:
        pytest.skip("File has syntax errors - skipping ruff format check")
    r = subprocess.run(
        ["python3", "-m", "ruff", "format", "--check", str(FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_ci] pass_to_pass — Python syntax validation for all areal/engine files
def test_repo_engine_syntax_valid():
    """All Python files in areal/engine have valid syntax (pass_to_pass)."""
    r = _run_python(
        """\
import py_compile
import os
engine_dir = REPO / 'areal/engine'
errors = []
for root, dirs, files in os.walk(engine_dir):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                py_compile.compile(filepath, doraise=True)
            except py_compile.PyCompileError as e:
                errors.append(f'{filepath}: {e}')
if errors:
    print('Syntax errors found:')
    for e in errors:
        print(e)
    exit(1)
print('All engine files have valid syntax')
"""
    )
    assert r.returncode == 0, f"Engine syntax check failed:\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass — check no trailing whitespace
def test_repo_no_trailing_whitespace():
    """megatron_engine.py has no trailing whitespace (pass_to_pass)."""
    source = FILE.read_text()
    for i, line in enumerate(source.splitlines(), 1):
        if line != line.rstrip():
            assert False, f"Trailing whitespace found at line {i}"


# [repo_ci] pass_to_pass — check file ends with newline
def test_repo_file_ends_with_newline():
    """megatron_engine.py ends with a single newline (pass_to_pass)."""
    content = FILE.read_bytes()
    if not content:
        assert False, "File is empty"
    if not content.endswith(b'\n'):
        assert False, "File does not end with newline"
    # Check for multiple trailing newlines (more than 1)
    if content.endswith(b'\n\n'):
        assert False, "File has multiple trailing newlines"


import pytest
