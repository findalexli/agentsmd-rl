"""
Task: prime-rl-toml-none-list-serialize
Repo: PrimeIntellect-ai/prime-rl @ a25b3e7a18e76999558a888c1ab1f8e5cd0e3831
PR:   2094

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import subprocess
from pathlib import Path

REPO = "/workspace/prime-rl"
CONFIG_PY = Path(f"{REPO}/src/prime_rl/utils/config.py")

TARGET_FUNCS = {"none_to_none_str"}


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo environment."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _load_config_functions():
    """Extract all top-level functions from config.py and exec them.

    Used by pass_to_pass tests that don't need subprocess isolation.
    Extracting every function ensures helpers are available even if the
    fix refactors into a shared inner function. Imports are executed
    first so type annotations resolve.
    """
    src = CONFIG_PY.read_text()
    tree = ast.parse(src)

    import_sources = []
    func_sources = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            import_sources.append(ast.get_source_segment(src, node))
        elif isinstance(node, ast.FunctionDef):
            func_sources.append(ast.get_source_segment(src, node))

    namespace = {}
    exec("\n".join(import_sources), namespace)
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
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_none_inside_flat_list():
    """None values inside a flat list are converted to 'None' strings."""
    r = _run_py("""
from prime_rl.utils.config import none_to_none_str
r1 = none_to_none_str({"k": [None, "a", None]})
assert r1 == {"k": ["None", "a", "None"]}, f"Expected None converted, got {r1}"
r2 = none_to_none_str({"x": [1, None, "b", None, 3]})
assert r2 == {"x": [1, "None", "b", "None", 3]}, f"Got {r2}"
r3 = none_to_none_str({"single": [None]})
assert r3 == {"single": ["None"]}, f"Got {r3}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_none_inside_dict_in_list():
    """None inside a dict nested in a list is converted."""
    r = _run_py("""
from prime_rl.utils.config import none_to_none_str
r1 = none_to_none_str({"k": [{"n": None, "ok": 1}]})
assert r1 == {"k": [{"n": "None", "ok": 1}]}, f"Got {r1}"
r2 = none_to_none_str({"d": [{"a": None}, {"b": None, "c": 2}]})
assert r2 == {"d": [{"a": "None"}, {"b": "None", "c": 2}]}, f"Got {r2}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_deeply_nested_list_of_list():
    """Deeply nested None (list of list) is converted."""
    r = _run_py("""
from prime_rl.utils.config import none_to_none_str
assert none_to_none_str({"k": [[None, 1], [2, None]]}) == {"k": [["None", 1], [2, "None"]]}
assert none_to_none_str({"matrix": [[None, None], [None, None]]}) == {"matrix": [["None", "None"], ["None", "None"]]}
assert none_to_none_str({"deep": [[[None, 1], [2, None]]]}) == {"deep": [[["None", 1], [2, "None"]]]}
assert none_to_none_str({"mixed": [None, [None, 1], [2, [None]]]}) == {"mixed": ["None", ["None", 1], [2, ["None"]]]}
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_toml_roundtrip_with_none_in_list():
    """TOML serialization succeeds after converting None in lists."""
    r = _run_py("""
import tomli_w
from prime_rl.utils.config import none_to_none_str

# Flat list with None — must not raise TypeError from tomli_w
data1 = {"items": [None, "hello", None]}
toml1 = tomli_w.dumps(none_to_none_str(data1))
assert toml1.count("None") >= 2, f"Expected >=2 'None', got: {toml1}"

# Nested dict+list combo
data2 = {"section": {"items": [None, "hello", None], "nested": {"vals": [1, None]}}}
toml2 = tomli_w.dumps(none_to_none_str(data2))
assert "None" in toml2

# List of dicts with None values
data3 = {"configs": [{"timeout": None}, {"name": "main", "val": None}]}
toml3 = tomli_w.dumps(none_to_none_str(data3))
assert toml3.count("None") >= 2

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD verification (p2p_enrichment)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_syntax_all():
    """All Python files in the repo must have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import ast
import os
from pathlib import Path

src_dir = Path("src")
errors = []

for root, _, files in os.walk(src_dir):
    for file in files:
        if file.endswith(".py"):
            path = Path(root) / file
            try:
                ast.parse(path.read_text())
            except SyntaxError as e:
                errors.append(f"{path}: {e}")

if errors:
    print("Syntax errors found:")
    for e in errors[:10]:
        print(f"  {e}")
    exit(1)
else:
    print("All Python files have valid syntax")
"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_config_module_loads():
    """Config module can be imported and executed without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, "src")
from prime_rl.utils.config import none_to_none_str

# Test basic functionality
result = none_to_none_str({"a": None, "b": "hello"})
assert result == {"a": "None", "b": "hello"}, f"Basic test failed: {result}"

# Test nested dict
result = none_to_none_str({"outer": {"inner": None}})
assert result == {"outer": {"inner": "None"}}, f"Nested dict test failed: {result}"

# Test non-None values pass through unchanged
result = none_to_none_str({"a": 1, "b": [1, 2], "c": {"d": True}})
assert result == {"a": 1, "b": [1, 2], "c": {"d": True}}, f"Pass-through test failed: {result}"

print("Config module tests passed!")
"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Config module test failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Ruff linter passes on the modified config.py (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # pip install may show warnings but should still work

    r = subprocess.run(
        ["ruff", "check", "--config=pyproject.toml", "src/prime_rl/utils/config.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Ruff format check passes on the modified config.py (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )

    r = subprocess.run(
        ["ruff", "format", "--check", "--config=pyproject.toml", "src/prime_rl/utils/config.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_imports_check():
    """Ruff import check (I rules) passes on the modified config.py (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )

    r = subprocess.run(
        ["ruff", "check", "--select", "I", "--config=pyproject.toml", "src/prime_rl/utils/config.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff import check failed:\n{r.stderr}\n{r.stdout}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_unit_tests_run_tests():
    """pass_to_pass | CI job 'Unit tests' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'PYTEST_OUTPUT_DIR=/tmp/outputs uv run pytest tests/unit -m "not gpu"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")