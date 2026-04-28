"""
Task: sglang-getitem-cache-identity
Repo: sglang @ ef2d4013d77cf1267e032d7a7a745dc3a6f74880
PR:   22184

Tests that GenerateReqInput and EmbeddingReqInput cache sub-objects
returned by __getitem__ to ensure identity stability.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/sglang"
PYTHON_DIR = f"{REPO}/python"

# ---------------------------------------------------------------------------
# Mock setup: allows importing io_struct.py without full sglang dependencies
# ---------------------------------------------------------------------------

_MOCK_SETUP = """\
import sys, types, importlib.util

def _m(name, **a):
    m = types.ModuleType(name)
    for k, v in a.items():
        setattr(m, k, v)
    return m

_D = type("_D", (), {})
for p in ["sglang", "sglang.srt", "sglang.srt.lora", "sglang.srt.managers",
          "sglang.srt.multimodal", "sglang.srt.observability", "sglang.srt.sampling"]:
    sys.modules[p] = _m(p)
sys.modules["torch"] = _m("torch")
sys.modules["sglang.srt.lora.lora_registry"] = _m("x", LoRARef=_D)
sys.modules["sglang.srt.managers.schedule_batch"] = _m(
    "x", BaseFinishReason=_D, Modality=_D)
sys.modules["sglang.srt.multimodal.mm_utils"] = _m(
    "x", has_valid_data=lambda x: x is not None)
sys.modules["sglang.srt.observability.req_time_stats"] = _m(
    "x", APIServerReqTimeStats=_D, DPControllerReqTimeStats=_D,
    SchedulerReqTimeStats=_D)
sys.modules["sglang.srt.sampling.sampling_params"] = _m("x", SamplingParams=_D)
sys.modules["sglang.srt.utils"] = _m("x", ImageData=_D)

_spec = importlib.util.spec_from_file_location(
    "sglang.srt.managers.io_struct",
    "/workspace/sglang/python/sglang/srt/managers/io_struct.py",
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["sglang.srt.managers.io_struct"] = _mod
_spec.loader.exec_module(_mod)
GenerateReqInput = _mod.GenerateReqInput
EmbeddingReqInput = _mod.EmbeddingReqInput
"""


def _run_behavioral(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write mock-setup + test code to a temp script and run it."""
    script = Path(REPO) / "_eval_behavioral.py"
    script.write_text(_MOCK_SETUP + "\n" + code)
    try:
        return subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def _ensure_tool(name):
    """Ensure a Python tool is installed."""
    try:
        subprocess.run([name, "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", name], check=True)


def _get_io_struct_path():
    return Path(f"{REPO}/python/sglang/srt/managers/io_struct.py")


def _get_tokenizer_manager_path():
    return Path(f"{REPO}/python/sglang/srt/managers/tokenizer_manager.py")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified files must parse without errors."""
    import ast
    for p in [_get_io_struct_path(), _get_tokenizer_manager_path()]:
        ast.parse(p.read_text())


def test_ruff_check():
    """Modified files must pass ruff syntax/error checks."""
    _ensure_tool("ruff")
    r = subprocess.run(
        ["ruff", "check",
         str(_get_io_struct_path()), str(_get_tokenizer_manager_path()),
         "--select=E9,F63,F7,F82"],
        capture_output=True, text=True, timeout=60, cwd=PYTHON_DIR,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_ruff_import_check():
    """Modified files must pass ruff import checks."""
    _ensure_tool("ruff")
    r = subprocess.run(
        ["ruff", "check",
         str(_get_io_struct_path()), str(_get_tokenizer_manager_path()),
         "--select=F401,F821"],
        capture_output=True, text=True, timeout=60, cwd=PYTHON_DIR,
    )
    assert r.returncode == 0, f"Ruff import check failed:\n{r.stdout}\n{r.stderr}"


def test_black_format_check():
    """Modified files must be formatted with black."""
    _ensure_tool("black")
    r = subprocess.run(
        ["black", "--check",
         str(_get_io_struct_path()), str(_get_tokenizer_manager_path())],
        capture_output=True, text=True, timeout=60, cwd=PYTHON_DIR,
    )
    assert r.returncode == 0, f"Black format check failed:\n{r.stdout}\n{r.stderr}"


def test_isort_check():
    """Modified files must have sorted imports."""
    _ensure_tool("isort")
    r = subprocess.run(
        ["isort", "--check-only",
         str(_get_io_struct_path()), str(_get_tokenizer_manager_path())],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stdout}\n{r.stderr}"


def test_pyflakes_check():
    """Modified files must pass pyflakes static analysis."""
    _ensure_tool("pyflakes")
    r = subprocess.run(
        ["pyflakes",
         str(_get_io_struct_path()), str(_get_tokenizer_manager_path())],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"pyflakes check failed:\n{r.stdout}\n{r.stderr}"


def test_codespell_check():
    """Modified files must pass codespell spelling check."""
    _ensure_tool("codespell")
    r = subprocess.run(
        ["codespell",
         str(_get_io_struct_path()), str(_get_tokenizer_manager_path())],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"codespell check failed:\n{r.stdout}\n{r.stderr}"


def test_check_ast():
    """Modified Python files must have valid AST."""
    io_p = str(_get_io_struct_path())
    tm_p = str(_get_tokenizer_manager_path())
    r = subprocess.run(
        [sys.executable, "-c",
         f'import ast; from pathlib import Path; '
         f'[ast.parse(Path(f).read_text()) for f in ["{io_p}", "{tm_p}"]]; '
         f'print("OK")'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"AST validation failed:\n{r.stderr}\n{r.stdout}"


def test_no_trailing_whitespace():
    """Modified files must not have trailing whitespace."""
    for p in [_get_io_struct_path(), _get_tokenizer_manager_path()]:
        for i, line in enumerate(p.read_text().splitlines(), 1):
            if line.rstrip() != line and line.strip():
                raise AssertionError(f"{p}:{i}: trailing whitespace")


def test_end_of_file_fixer():
    """Modified files must end with a single newline."""
    for p in [_get_io_struct_path(), _get_tokenizer_manager_path()]:
        content = p.read_bytes()
        assert content.endswith(b"\n"), f"{p}: missing final newline"
        assert not content.endswith(b"\n\n"), f"{p}: multiple trailing newlines"


def test_repo_check_debug_statements():
    """Modified files have no debug statements."""
    patterns = ["breakpoint()", "import pdb", "from pdb import",
                "pdb.set_trace", "console.log", "debugger"]
    for p in [_get_io_struct_path(), _get_tokenizer_manager_path()]:
        for i, line in enumerate(p.read_text().splitlines(), 1):
            if line.strip().startswith("#"):
                continue
            for pat in patterns:
                if pat in line:
                    raise AssertionError(f"{p}:{i}: found '{pat}'")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests
# ---------------------------------------------------------------------------

def test_generate_req_identity():
    """GenerateReqInput.__getitem__ returns the same instance for the same index."""
    r = _run_behavioral("""\
obj = GenerateReqInput(
    text=["hello", "world"],
    image_data=[None, None],
    video_data=[None, None],
    audio_data=[None, None],
    sampling_params=[{}, {}],
    rid=["r1", "r2"],
    return_logprob=[False, False],
    logprob_start_len=[-1, -1],
    top_logprobs_num=[0, 0],
    token_ids_logprob=[None, None],
)

sub0_a = obj[0]
sub0_b = obj[0]
sub1 = obj[1]

assert sub0_a is sub0_b, "req[0] is req[0] must be True (identity caching)"
assert sub0_a is not sub1, "Different indices must return different objects"
assert sub0_a.text == "hello"
assert sub1.text == "world"
print("PASS")
""")
    assert r.returncode == 0, f"Failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_embedding_req_identity():
    """EmbeddingReqInput.__getitem__ returns the same instance for the same index."""
    r = _run_behavioral("""\
obj = EmbeddingReqInput(
    text=["hello", "world"],
    sampling_params=[{}, {}],
    rid=["r1", "r2"],
)

sub0_a = obj[0]
sub0_b = obj[0]
sub1 = obj[1]

assert sub0_a is sub0_b, "req[0] is req[0] must be True (identity caching)"
assert sub0_a is not sub1, "Different indices must return different objects"
assert sub0_a.text == "hello"
assert sub1.text == "world"
print("PASS")
""")
    assert r.returncode == 0, f"Failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_lora_id_propagation_to_cached_subobjects():
    """After lora_id is set on parent, cached sub-objects reflect the update."""
    r = _run_behavioral("""\
import ast

obj = GenerateReqInput(
    text=["hello", "world"],
    lora_path=["path_a", "path_b"],
    image_data=[None, None],
    video_data=[None, None],
    audio_data=[None, None],
    sampling_params=[{}, {}],
    rid=["r1", "r2"],
    return_logprob=[False, False],
    logprob_start_len=[-1, -1],
    top_logprobs_num=[0, 0],
    token_ids_logprob=[None, None],
)

# Access sub-objects to trigger caching
sub0 = obj[0]
sub1 = obj[1]
assert sub0.lora_id is None, "lora_id should be None before resolution"

# Simulate _resolve_lora_path: parent gets lora_id assigned
obj.lora_id = ["id_a", "id_b"]

# Read _resolve_lora_path and extract + execute its propagation logic
tm_path = "/workspace/sglang/python/sglang/srt/managers/tokenizer_manager.py"
tm_src = open(tm_path).read()
tree = ast.parse(tm_src)

func = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == "_resolve_lora_path":
            func = node
            break

assert func is not None, "_resolve_lora_path must exist in tokenizer_manager.py"

# Collect statements after the 'obj.lora_id = await ...' assignment
propagation = []
past_acquire = False
for stmt in func.body:
    s = ast.unparse(stmt)
    if "lora_id" in s and ("acquire" in s or "await" in s):
        past_acquire = True
        continue
    if past_acquire:
        propagation.append(stmt)

assert len(propagation) > 0, (
    "_resolve_lora_path must have propagation logic after lora_id assignment"
)

# Execute the actual propagation code from the codebase
prop_mod = ast.Module(body=propagation, type_ignores=[])
ast.fix_missing_locations(prop_mod)
exec(compile(prop_mod, "<propagation>", "exec"))

# Verify propagation: sub-objects should have updated lora_id
assert sub0.lora_id == "id_a", f"Expected 'id_a', got {sub0.lora_id!r}"
assert sub1.lora_id == "id_b", f"Expected 'id_b', got {sub1.lora_id!r}"
assert obj[0].lora_id == "id_a", "Cached sub-object via __getitem__ should reflect update"
print("PASS")
""")
    assert r.returncode == 0, f"Failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_multimodal_gen_test_1_npu_a3_run_test():
    """pass_to_pass | CI job 'multimodal-gen-test-1-npu-a3' → step 'Run test'"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 sglang/multimodal_gen/test/run_suite.py --suite 1-npu'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_multimodal_gen_test_8_npu_a3_run_test():
    """pass_to_pass | CI job 'multimodal-gen-test-8-npu-a3' → step 'Run test'"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 sglang/multimodal_gen/test/run_suite.py --suite 8-npu'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")