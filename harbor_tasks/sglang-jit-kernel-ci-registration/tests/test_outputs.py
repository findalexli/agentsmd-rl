"""
Task: sglang-jit-kernel-ci-registration
Repo: sgl-project/sglang @ 6047d2c690483224b2bb7d70288ea60b0b8e0c7d
PR:   21239

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import subprocess

REPO = "/workspace"

TARGET_FILES = [
    f"{REPO}/python/sglang/jit_kernel/benchmark/bench_cast.py",
    f"{REPO}/python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py",
    f"{REPO}/python/sglang/jit_kernel/tests/test_cast.py",
    f"{REPO}/python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py",
]

BENCHMARK_FILES = TARGET_FILES[:2]
TEST_FILES = TARGET_FILES[2:]

# Snippet to load ci_register.py in isolation (avoids transitive sglang imports)
_LOAD_CI_REGISTER = """
import importlib.util, sys
_spec = importlib.util.spec_from_file_location(
    "ci_register", "{repo}/python/sglang/test/ci/ci_register.py"
)
ci_register = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ci_register)
ut_parse_one_file = ci_register.ut_parse_one_file
collect_tests = ci_register.collect_tests
""".format(repo=REPO)


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All 4 modified files must be valid Python."""
    for filepath in TARGET_FILES:
        with open(filepath) as f:
            source = f.read()
        ast.parse(source, filename=filepath)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_bench_cast_ci_registration():
    """bench_cast.py is discoverable by ci_register AST parser and registered for benchmark suite."""
    filepath = f"{REPO}/python/sglang/jit_kernel/benchmark/bench_cast.py"
    r = _run_py(f"""{_LOAD_CI_REGISTER}
import json
regs = ut_parse_one_file("{filepath}")
print(json.dumps([{{"suite": r.suite, "est_time": r.est_time}} for r in regs]))
""")
    assert r.returncode == 0, f"ut_parse_one_file failed: {r.stderr}"
    regs = json.loads(r.stdout.strip())
    assert regs, "No CI registrations found in bench_cast.py"
    suites = [reg["suite"] for reg in regs]
    assert "stage-b-kernel-benchmark-1-gpu-large" in suites, f"Expected benchmark suite, got {suites}"


# [pr_diff] fail_to_pass
def test_bench_fused_qknorm_rope_ci_registration():
    """bench_fused_qknorm_rope.py is discoverable and registered for benchmark suite."""
    filepath = f"{REPO}/python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py"
    r = _run_py(f"""{_LOAD_CI_REGISTER}
import json
regs = ut_parse_one_file("{filepath}")
print(json.dumps([{{"suite": r.suite, "est_time": r.est_time}} for r in regs]))
""")
    assert r.returncode == 0, f"ut_parse_one_file failed: {r.stderr}"
    regs = json.loads(r.stdout.strip())
    assert regs, "No CI registrations found in bench_fused_qknorm_rope.py"
    suites = [reg["suite"] for reg in regs]
    assert "stage-b-kernel-benchmark-1-gpu-large" in suites, f"Expected benchmark suite, got {suites}"


# [pr_diff] fail_to_pass
def test_cast_ci_registration():
    """test_cast.py is discoverable and registered for kernel unit suite."""
    filepath = f"{REPO}/python/sglang/jit_kernel/tests/test_cast.py"
    r = _run_py(f"""{_LOAD_CI_REGISTER}
import json
regs = ut_parse_one_file("{filepath}")
print(json.dumps([{{"suite": r.suite, "est_time": r.est_time}} for r in regs]))
""")
    assert r.returncode == 0, f"ut_parse_one_file failed: {r.stderr}"
    regs = json.loads(r.stdout.strip())
    assert regs, "No CI registrations found in test_cast.py"
    suites = [reg["suite"] for reg in regs]
    assert "stage-b-kernel-unit-1-gpu-large" in suites, f"Expected unit suite, got {suites}"


# [pr_diff] fail_to_pass
def test_fused_qknorm_rope_ci_registration():
    """test_fused_qknorm_rope.py is discoverable and registered for kernel unit suite."""
    filepath = f"{REPO}/python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py"
    r = _run_py(f"""{_LOAD_CI_REGISTER}
import json
regs = ut_parse_one_file("{filepath}")
print(json.dumps([{{"suite": r.suite, "est_time": r.est_time}} for r in regs]))
""")
    assert r.returncode == 0, f"ut_parse_one_file failed: {r.stderr}"
    regs = json.loads(r.stdout.strip())
    assert regs, "No CI registrations found in test_fused_qknorm_rope.py"
    suites = [reg["suite"] for reg in regs]
    assert "stage-b-kernel-unit-1-gpu-large" in suites, f"Expected unit suite, got {suites}"


# [pr_diff] fail_to_pass
def test_collect_tests_no_errors():
    """collect_tests() succeeds on all 4 files without raising ValueError."""
    files_list = json.dumps(TARGET_FILES)
    r = _run_py(f"""{_LOAD_CI_REGISTER}
import json
regs = collect_tests({files_list}, sanity_check=True)
print(json.dumps([{{"filename": r.filename, "suite": r.suite, "est_time": r.est_time}} for r in regs]))
""")
    assert r.returncode == 0, f"collect_tests raised an error: {r.stderr}"
    regs = json.loads(r.stdout.strip())
    assert len(regs) >= 4, f"Expected at least 4 registrations, got {len(regs)}"
    for reg in regs:
        assert reg["est_time"] > 0, f"{reg['filename']} has non-positive est_time: {reg['est_time']}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .claude/skills/
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/add-jit-kernel/SKILL.md:433 @ 6047d2c
def test_literal_registration_values():
    """Registration uses literal values for est_time and suite (AST-parseable)."""
    for filepath in TARGET_FILES:
        with open(filepath) as f:
            source = f.read()
        tree = ast.parse(source)

        found = False
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Name):
                continue
            if not node.func.id.startswith("register_") or not node.func.id.endswith("_ci"):
                continue
            found = True
            assert node.keywords or node.args, (
                f"{filepath}: register_*_ci() called with no arguments (stub)"
            )
            for kw in node.keywords:
                assert isinstance(kw.value, ast.Constant), (
                    f"{filepath}: keyword '{kw.arg}' is not a literal value"
                )
            for arg in node.args:
                assert isinstance(arg, ast.Constant), (
                    f"{filepath}: positional arg is not a literal value"
                )
        assert found, f"{filepath}: no register_*_ci() call found in AST"


# [agent_config] fail_to_pass — .claude/skills/add-jit-kernel/SKILL.md:422 @ 6047d2c
def test_module_level_registration():
    """Registration calls are at module level, not nested inside functions or classes."""
    for filepath in TARGET_FILES:
        with open(filepath) as f:
            source = f.read()
        tree = ast.parse(source)

        top_level_calls = []
        for node in tree.body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                func = call.func
                if isinstance(func, ast.Name) and func.id == "register_cuda_ci":
                    top_level_calls.append(call)
                elif isinstance(func, ast.Attribute) and func.attr == "register_cuda_ci":
                    top_level_calls.append(call)

        assert top_level_calls, (
            f"{filepath}: no top-level register_cuda_ci() call found — "
            "registration must be at module level for AST discovery"
        )


# [agent_config] fail_to_pass — .claude/skills/add-jit-kernel/SKILL.md:425 @ 6047d2c
def test_correct_import_path():
    """Files import register_cuda_ci from sglang.test.ci.ci_register."""
    for filepath in TARGET_FILES:
        with open(filepath) as f:
            source = f.read()
        tree = ast.parse(source)

        found_import = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if (node.module == "sglang.test.ci.ci_register"
                        and any(alias.name == "register_cuda_ci" for alias in node.names)):
                    found_import = True
                    break
        assert found_import, (
            f"{filepath}: missing 'from sglang.test.ci.ci_register import register_cuda_ci'"
        )


# [agent_config] fail_to_pass — .claude/skills/write-sglang-test/SKILL.md:8 @ 6047d2c
def test_suite_file_type_consistency():
    """Benchmark files use benchmark suite, test files use unit suite (not swapped)."""
    bench_json = json.dumps(BENCHMARK_FILES)
    test_json = json.dumps(TEST_FILES)
    r = _run_py(f"""{_LOAD_CI_REGISTER}
import json
results = {{}}
for filepath in {bench_json}:
    regs = ut_parse_one_file(filepath)
    results[filepath] = [{{"suite": r.suite}} for r in regs]
for filepath in {test_json}:
    regs = ut_parse_one_file(filepath)
    results[filepath] = [{{"suite": r.suite}} for r in regs]
print(json.dumps(results))
""")
    assert r.returncode == 0, f"ut_parse_one_file failed: {r.stderr}"
    results = json.loads(r.stdout.strip())

    for bench_file in BENCHMARK_FILES:
        for reg in results[bench_file]:
            assert "kernel-unit" not in reg["suite"], (
                f"{bench_file}: benchmark file incorrectly registered for unit suite '{reg['suite']}'"
            )

    for test_file in TEST_FILES:
        suites = [reg["suite"] for reg in results[test_file]]
        has_unit = any("kernel-unit" in s for s in suites)
        assert has_unit, f"{test_file}: test file not registered for any kernel unit suite, got {suites}"


# ---------------------------------------------------------------------------
# Repo CI checks (pass_to_pass) — repo's own CI pipeline must not break
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Target files pass ruff linting for F401 (unused imports) and F821 (undefined names)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"
    r = subprocess.run(
        ["ruff", "check", "--select=F401,F821"] + TARGET_FILES,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_isort_check():
    """Target files have correctly sorted imports."""
    r = subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install isort: {r.stderr}"
    r = subprocess.run(
        ["isort", "--check-only"] + TARGET_FILES,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_black_format():
    """Target files are correctly formatted with black."""
    r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install black: {r.stderr}"
    r = subprocess.run(
        ["black", "--check"] + TARGET_FILES,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"black format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_codespell():
    """Target files have no spelling errors."""
    r = subprocess.run(
        ["pip", "install", "codespell", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install codespell: {r.stderr}"
    r = subprocess.run(
        ["codespell", "--config", ".codespellrc"] + TARGET_FILES,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"codespell check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ci_register_importable():
    """CI registration module is importable and functional (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import importlib.util
import sys
_spec = importlib.util.spec_from_file_location(
    "ci_register", "/workspace/python/sglang/test/ci/ci_register.py"
)
ci_register = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ci_register)
# Verify key functions exist
assert hasattr(ci_register, 'ut_parse_one_file')
assert hasattr(ci_register, 'collect_tests')
assert hasattr(ci_register, 'register_cuda_ci')
print("ci_register module verified")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"ci_register import test failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_py_compile():
    """Target files compile to bytecode without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile"] + TARGET_FILES,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_hooks_yaml():
    """Pre-commit YAML hooks pass on target files (pass_to_pass)."""
    # Install pre-commit and run check-yaml hook equivalent
    r = subprocess.run(
        ["pip", "install", "PyYAML", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install PyYAML: {r.stderr}"
    r = subprocess.run(
        ["python3", "-c", """
import yaml
import sys
# Validate .pre-commit-config.yaml is valid YAML
with open('/workspace/.pre-commit-config.yaml') as f:
    yaml.safe_load(f)
print('pre-commit-config.yaml is valid')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"YAML validation failed:\n{r.stderr[-500:]}"



# [repo_tests] pass_to_pass
def test_repo_end_of_file_fixer():
    """Target files end with exactly one newline (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
files = [
    "/workspace/python/sglang/jit_kernel/benchmark/bench_cast.py",
    "/workspace/python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py",
    "/workspace/python/sglang/jit_kernel/tests/test_cast.py",
    "/workspace/python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py",
]
errors = []
for f in files:
    with open(f, 'rb') as fp:
        content = fp.read()
    if not content:
        continue
    if not content.endswith(b'\\n'):
        errors.append(f"{f}: missing final newline")
    elif content.endswith(b'\\n\\n'):
        errors.append(f"{f}: multiple trailing newlines")
if errors:
    for e in errors:
        print(e)
    sys.exit(1)
print("All files have proper ending newlines")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"End-of-file check failed:\n{r.stdout[-500:]}"
