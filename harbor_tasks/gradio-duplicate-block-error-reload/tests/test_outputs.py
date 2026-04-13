"""
Task: gradio-duplicate-block-error-reload
Repo: gradio-app/gradio @ a17eb7888b48cbd98b1e0feb17e2614bf3853d66
PR:   13013

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"
TARGET = f"{REPO}/gradio/utils.py"

# Common preamble: extract the post-exec code region from utils.py and test it.
_EXTRACT_PREAMBLE = """\
import sys, textwrap, types
from pathlib import Path

source = Path("/workspace/gradio/gradio/utils.py").read_text()
lines = source.splitlines()

exec_idx = end_idx = None
for i, line in enumerate(lines):
    if "exec(no_reload_source_code" in line:
        exec_idx = i
    if exec_idx is not None and i > exec_idx:
        if line.strip().startswith("sys.modules[") or line.strip().startswith("while "):
            end_idx = i
            break

assert exec_idx is not None, "exec(no_reload_source_code) not found in utils.py"
if end_idx is None:
    end_idx = min(exec_idx + 30, len(lines))

region = textwrap.dedent("\\n".join(lines[exec_idx + 1 : end_idx]))

def _run_with_mocks(Context_id, blocks, demo_exists=True):
    class Context:
        id = Context_id

    class Reloader:
        demo_name = "demo"

    module = types.ModuleType("test_module")
    if demo_exists and blocks is not None:
        class Demo:
            def __init__(self, blks):
                self.blocks = blks
        module.demo = Demo(blocks)

    reloader = Reloader()
    ns = {
        "Context": Context, "module": module, "reloader": reloader,
        "getattr": getattr, "hasattr": hasattr, "max": max, "len": len,
        "list": list, "set": set, "dict": dict, "int": int,
        "print": print, "type": type, "__builtins__": __builtins__,
    }
    exec(region, ns)
    return Context.id
"""


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo environment via subprocess."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _ensure_ruff():
    """Ensure ruff is installed."""
    r = subprocess.run(
        ["python", "-m", "ruff", "--version"],
        capture_output=True, text=True, timeout=60,
    )
    if r.returncode != 0:
        # Install ruff if not available
        subprocess.run(
            ["pip", "install", "ruff", "-q"],
            capture_output=True, text=True, timeout=120,
        )


def _ensure_pytest_deps():
    """Ensure pytest and gradio dependencies are installed."""
    # Check if gradio is installed by trying to import it
    r = subprocess.run(
        ["python", "-c", "import gradio"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    if r.returncode != 0:
        # Install gradio from source along with test dependencies
        subprocess.run(
            ["pip", "install", "-e", ".", "-q"],
            capture_output=True, text=True, timeout=300, cwd=REPO,
        )
        subprocess.run(
            ["pip", "install", "pytest", "hypothesis", "-q"],
            capture_output=True, text=True, timeout=180,
        )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


def test_syntax_check():
    """gradio/utils.py must parse without syntax errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


def test_repo_ruff_check():
    """Repo's ruff lint check passes on utils.py (pass_to_pass)."""
    _ensure_ruff()
    r = subprocess.run(
        ["python", "-m", "ruff", "check", "gradio/utils.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_ruff_format():
    """Repo's ruff format check passes on utils.py (pass_to_pass)."""
    _ensure_ruff()
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", "gradio/utils.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_pytest_reload():
    """Repo's reload tests pass (pass_to_pass)."""
    _ensure_pytest_deps()
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_reload.py", "-v"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Reload tests failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_pytest_utils_configs():
    """Repo's utils config equivalence tests pass (pass_to_pass)."""
    _ensure_pytest_deps()
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_utils.py::test_assert_configs_are_equivalent", "-v"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Utils config tests failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_pytest_utils_ner():
    """Repo's utils NER format tests pass (pass_to_pass)."""
    _ensure_pytest_deps()
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_utils.py::TestFormatNERList", "-v"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Utils NER tests failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_pytest_utils_extension():
    """Repo's utils file extension tests pass (pass_to_pass)."""
    _ensure_pytest_deps()
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_utils.py::test_get_extension_from_file_path_or_url", "-v"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Utils extension tests failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_pytest_utils_is_in_or_equal():
    """Repo's utils path comparison tests pass (pass_to_pass)."""
    _ensure_pytest_deps()
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_utils.py::test_is_in_or_equal", "-v"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Utils is_in_or_equal tests failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_pytest_utils_file_size():
    """Repo's utils file size parsing tests pass (pass_to_pass)."""
    _ensure_pytest_deps()
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_utils.py::test_parse_file_size", "-v"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Utils file size tests failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------


def test_context_id_bumped_past_block_ids():
    """After module re-exec, Context.id must exceed max existing block ID."""
    r = _run_py(_EXTRACT_PREAMBLE + """
cid = _run_with_mocks(
    Context_id=3,
    blocks={0: "b0", 1: "b1", 5: "b5", 10: "b10"},
)
assert cid >= 11, f"Context.id = {cid}, expected >= 11 (max block key was 10)"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_context_id_varied_block_distributions():
    """Fix handles sequential, sparse, and single-block ID distributions."""
    r = _run_py(_EXTRACT_PREAMBLE + """
scenarios = [
    ({0: "x", 1: "x", 2: "x"}, 0, 3, "sequential 0-2"),
    ({0: "x", 5: "x", 100: "x"}, 2, 101, "sparse up to 100"),
    ({42: "x"}, 0, 43, "single block at 42"),
]
for blocks, init_id, min_expected, desc in scenarios:
    cid = _run_with_mocks(Context_id=init_id, blocks=blocks)
    assert cid >= min_expected, f"[{desc}] Context.id={cid}, expected >= {min_expected}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_context_id_preserved_when_already_high():
    """Fix must bump Context.id when max(blocks)+1 exceeds current Context.id."""
    r = _run_py(_EXTRACT_PREAMBLE + """
# Test the actual bumping logic: when Context.id starts low but max(blocks)+1 is higher
# the fix should bump Context.id to max(blocks)+1
# Before fix: Context.id would stay at its initial value (e.g., 5)
# After fix: Context.id should be bumped to max(blocks)+1 (e.g., 101)
cid = _run_with_mocks(
    Context_id=5,
    blocks={0: "x", 50: "x", 100: "x"},
)
assert cid >= 101, f"Context.id={cid}, expected >= 101 (max block was 100, should bump past it)"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_no_crash_when_demo_absent():
    """Fix must handle missing/None/empty demo gracefully AND bump Context.id when blocks exist."""
    r = _run_py(_EXTRACT_PREAMBLE + """
# Test 1: demo attribute not set on module - should not crash, Context.id unchanged
cid = _run_with_mocks(blocks=None, Context_id=5, demo_exists=False)
assert cid == 5, f"Context.id changed to {cid} when demo absent (expected 5)"

# Test 2: demo is None (not set on module, blocks=None) - should not crash
# This tests that the hasattr check doesn't fail when demo attr exists but is None
class Reloader2:
    demo_name = "demo"

module2 = types.ModuleType("test_module2")
module2.demo = None  # demo exists but is None

class Context2:
    id = 7

reloader2 = Reloader2()
ns2 = {
    "Context": Context2, "module": module2, "reloader": reloader2,
    "getattr": getattr, "hasattr": hasattr, "max": max, "len": len,
    "list": list, "set": set, "dict": dict, "int": int,
    "print": print, "type": type, "__builtins__": __builtins__,
}
exec(region, ns2)
assert Context2.id == 7, f"Context.id changed to {Context2.id} when demo is None (expected 7)"

# Test 3: demo has empty blocks dict - should not crash, Context.id unchanged
cid = _run_with_mocks(blocks={}, Context_id=9, demo_exists=True)
assert cid == 9, f"Context.id changed to {cid} when blocks empty (expected 9)"

# Test 4: CRITICAL fail-to-pass check - fix bumps Context.id when blocks exist
# This is the actual behavior that distinguishes buggy from fixed code
cid = _run_with_mocks(
    Context_id=0,
    blocks={5: "x", 10: "x", 15: "x"},
)
assert cid >= 16, f"Context.id={cid}, expected >= 16 after fix (max block was 15)"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression
# ---------------------------------------------------------------------------


def test_watchfn_structure_preserved():
    """Core watchfn landmarks must still be present."""
    source = Path(TARGET).read_text()
    assert "exec(no_reload_source_code" in source, "exec() call missing"
    assert "Context.id = 0" in source, "Context.id = 0 reset missing"
    assert "reloader.should_watch" in source, "reloader.should_watch loop missing"


def test_context_reset_precedes_exec():
    """Context.id = 0 must appear before exec(no_reload_source_code)."""
    lines = Path(TARGET).read_text().splitlines()
    reset_line = next((i for i, l in enumerate(lines) if "Context.id = 0" in l), None)
    exec_line = next((i for i, l in enumerate(lines) if "exec(no_reload_source_code" in l), None)
    assert reset_line is not None, "Context.id = 0 not found"
    assert exec_line is not None, "exec(no_reload_source_code) not found"
    assert reset_line < exec_line, (
        f"Context.id=0 (line {reset_line+1}) must precede exec() (line {exec_line+1})"
    )


def test_not_stub():
    """utils.py must not be a stub — needs substantial content."""
    source = Path(TARGET).read_text()
    assert len(source.splitlines()) >= 500, "File too short to be real"
    tree = ast.parse(source)
    funcs = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
    assert funcs >= 20, f"Only {funcs} functions — file appears to be a stub"
