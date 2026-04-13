"""
Task: vllm-eagle-fullcudagraph-stale-attn
Repo: vllm-project/vllm @ 44a6528028ad79951de08b6a7928f6c05788d00d
PR:   #38311

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

The speculator.py requires torch/CUDA at import time, so behavioral
tests use subprocess to run AST-based control-flow analysis.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/repo"
FILE = Path(REPO) / "vllm/v1/worker/gpu/spec_decode/eagle/speculator.py"


def _parse_file():
    """Parse the speculator file and return (source, tree)."""
    src = FILE.read_text()
    tree = ast.parse(src)
    return src, tree


def _find_method(tree, class_name, method_name):
    """Find a method inside a class."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in ast.walk(node):
                if isinstance(child, ast.FunctionDef) and child.name == method_name:
                    return child
    return None


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

SCRIPT_NO_EARLY_RETURN = r"""
import ast, sys

src = open("vllm/v1/worker/gpu/spec_decode/eagle/speculator.py").read()
tree = ast.parse(src)

# Find propose() in EagleSpeculator
propose = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "EagleSpeculator":
        for child in ast.walk(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == "propose":
                propose = child
                break
        break

if propose is None:
    print("FAIL: propose() not found in EagleSpeculator")
    sys.exit(1)

def get_call_name(node):
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    elif isinstance(node.func, ast.Name):
        return node.func.id
    return None

def is_attn_build(name):
    if name is None:
        return False
    nl = name.lower()
    return ("attn" in nl or "attention" in nl) and \
           any(w in nl for w in ("build", "metadata", "prepare", "create"))

# Collect all attn metadata build call lines in propose()
attn_build_lines = []
for node in ast.walk(propose):
    if isinstance(node, ast.Call):
        name = get_call_name(node)
        if is_attn_build(name):
            attn_build_lines.append(node.lineno)

# Find FULL cudagraph if-blocks and check for returns before attn build
for node in ast.walk(propose):
    if not isinstance(node, ast.If):
        continue
    test_src = ast.get_source_segment(src, node.test) or ""
    if "FULL" not in test_src:
        continue
    if "cg_mode" not in test_src and "cudagraph" not in test_src.lower():
        continue
    # Found a FULL cudagraph mode check — look for returns in its body
    for stmt in node.body:
        if isinstance(stmt, ast.Return):
            builds_before = [l for l in attn_build_lines if l < stmt.lineno]
            if not builds_before:
                print(f"FAIL: FULL cudagraph early return at line {stmt.lineno} "
                      f"before any attn metadata build")
                sys.exit(1)

print("PASS")
"""


def test_no_fullgraph_early_return():
    """FULL cudagraph path must NOT return before attention metadata is built.

    The bug: an if-block checking CUDAGraphMode.FULL contains a `return`
    that fires before any attention metadata build call. The fix removes
    this early return or moves attn metadata building before it.
    """
    r = subprocess.run(
        ["python3", "-c", SCRIPT_NO_EARLY_RETURN],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "PASS" in r.stdout


SCRIPT_ATTN_BEFORE_FULL = r"""
import ast, sys

src = open("vllm/v1/worker/gpu/spec_decode/eagle/speculator.py").read()
tree = ast.parse(src)

# Find propose() in EagleSpeculator
propose = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "EagleSpeculator":
        for child in ast.walk(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == "propose":
                propose = child
                break
        break

if propose is None:
    print("FAIL: propose() not found in EagleSpeculator")
    sys.exit(1)

def get_call_name(node):
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    elif isinstance(node.func, ast.Name):
        return node.func.id
    return None

def is_attn_build(name):
    if name is None:
        return False
    nl = name.lower()
    return ("attn" in nl or "attention" in nl) and \
           any(w in nl for w in ("build", "metadata", "prepare", "create"))

# Collect attn build lines, FULL check lines, and fullgraph call lines
attn_build_lines = []
full_check_lines = []
fullgraph_call_lines = []

for node in ast.walk(propose):
    if isinstance(node, ast.Call):
        name = get_call_name(node)
        if is_attn_build(name):
            attn_build_lines.append(node.lineno)
        if name and "fullgraph" in name.lower():
            fullgraph_call_lines.append(node.lineno)
    if isinstance(node, ast.If):
        test_src = ast.get_source_segment(src, node.test) or ""
        if "FULL" in test_src and ("cg_mode" in test_src or "cudagraph" in test_src.lower()):
            full_check_lines.append(node.lineno)

# Determine the line of FULL cudagraph execution
full_exec_line = None
if full_check_lines:
    full_exec_line = min(full_check_lines)
elif fullgraph_call_lines:
    full_exec_line = min(fullgraph_call_lines)

if full_exec_line is None:
    if attn_build_lines:
        print("PASS: attn metadata built, no explicit FULL path")
        sys.exit(0)
    print("FAIL: no FULL path and no attn metadata building found")
    sys.exit(1)

if not attn_build_lines:
    print(f"FAIL: no attn metadata build found; FULL execution at line {full_exec_line}")
    sys.exit(1)

before_full = [l for l in attn_build_lines if l < full_exec_line]
if not before_full:
    print(f"FAIL: attn metadata built at {attn_build_lines} but FULL path at line {full_exec_line}")
    sys.exit(1)

print(f"PASS: attn metadata at line {min(before_full)} before FULL path at line {full_exec_line}")
"""


def test_attn_metadata_before_fullgraph_execution():
    """Attention metadata must be built before FULL cudagraph execution.

    The fix ensures build_attn_metadata (or _build_draft_attn_metadata)
    is called before the if-block that dispatches FULL cudagraph.
    """
    r = subprocess.run(
        ["python3", "-c", SCRIPT_ATTN_BEFORE_FULL],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# pass_to_pass (static / pr_diff) — gates and regression checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified file must parse without errors."""
    src = FILE.read_text()
    ast.parse(src)


def test_slot_mappings_computed():
    """Slot mappings must be computed in propose() for all cudagraph modes."""
    _, tree = _parse_file()
    propose = _find_method(tree, "EagleSpeculator", "propose")
    assert propose is not None, "propose() method not found in EagleSpeculator"

    slot_calls = []
    for node in ast.walk(propose):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                name = node.func.attr
            elif isinstance(node.func, ast.Name):
                name = node.func.id
            else:
                continue
            if "slot_mapping" in name.lower():
                slot_calls.append(node.lineno)

    assert slot_calls, "No slot mapping computation found in propose()"


def test_core_class_structure():
    """EagleSpeculator class retains all required methods."""
    _, tree = _parse_file()

    eagle_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "EagleSpeculator":
            eagle_class = node
            break

    assert eagle_class is not None, "EagleSpeculator class not found"

    methods = {n.name for n in ast.walk(eagle_class) if isinstance(n, ast.FunctionDef)}
    required = {"propose", "generate_draft", "capture_model", "run_model", "load_model", "set_attn"}
    missing = required - methods
    assert not missing, f"Missing methods: {missing}"


def test_propose_not_stub():
    """propose() must have real logic — conditionals, calls, self attribute access."""
    _, tree = _parse_file()
    propose = _find_method(tree, "EagleSpeculator", "propose")
    assert propose is not None, "propose() not found"

    body_stmts = len(propose.body)
    assert body_stmts >= 15, f"propose() has only {body_stmts} statements — likely stubbed"

    ifs = sum(1 for n in ast.walk(propose) if isinstance(n, ast.If))
    assert ifs >= 3, f"propose() has only {ifs} if-statements — likely stubbed"

    calls = sum(1 for n in ast.walk(propose) if isinstance(n, ast.Call))
    assert calls >= 8, f"propose() has only {calls} calls — likely stubbed"

    self_attrs = set()
    for n in ast.walk(propose):
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "self":
            self_attrs.add(n.attr)

    required_attrs = {"input_buffers", "block_tables", "draft_tokens"}
    found = required_attrs & self_attrs
    assert len(found) >= 2, f"propose() only references {found} of {required_attrs} — likely stubbed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

def test_no_bare_pip():
    """No bare pip usage in modified file (AGENTS.md:42)."""
    src = FILE.read_text()
    for i, line in enumerate(src.splitlines(), 1):
        stripped = line.strip()
        assert not stripped.startswith("pip install"), \
            f"Bare pip usage at line {i}: {stripped}"


def test_no_wildcard_imports():
    """No wildcard imports in modified file."""
    _, tree = _parse_file()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                assert alias.name != "*", f"Wildcard import from {node.module}"


# ---------------------------------------------------------------------------
# Repo CI tests (repo_tests) — pass_to_pass gates from actual CI
# ---------------------------------------------------------------------------

def test_repo_ruff_check():
    """Repo ruff linter passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # ruff install is best-effort, continue even if it has issues

    r = subprocess.run(
        ["ruff", "check", str(FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """Repo ruff format check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )

    r = subprocess.run(
        ["ruff", "format", "--check", str(FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_typos():
    """Repo typos checker passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "typos", "--quiet"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )

    r = subprocess.run(
        ["typos", str(FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"typos check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_py_compile():
    """Modified file compiles without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", str(FILE)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr}"


def test_repo_ast_parse():
    """Modified file parses as valid Python AST (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"import ast; ast.parse(open('{FILE}').read())"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"AST parse failed:\n{r.stderr}"


def test_repo_mypy():
    """Repo mypy type checker passes on modified file (pass_to_pass)."""
    # Install mypy and dependencies
    r = subprocess.run(
        ["pip", "install", "mypy", "pydantic", "regex", "types-setuptools",
         "types-PyYAML", "types-requests", "types-torch", "--quiet"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )

    r = subprocess.run(
        ["python", "tools/pre_commit/mypy.py", "0", "3.10", str(FILE)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"mypy check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_spdx_header():
    """Modified file has SPDX license header (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "regex", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )

    r = subprocess.run(
        ["python", "tools/pre_commit/check_spdx_header.py", str(FILE)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"SPDX header check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_forbidden_imports():
    """Modified file has no forbidden imports (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "regex", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )

    r = subprocess.run(
        ["python", "tools/pre_commit/check_forbidden_imports.py", str(FILE)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Forbidden imports check failed:\n{r.stdout}\n{r.stderr}"
