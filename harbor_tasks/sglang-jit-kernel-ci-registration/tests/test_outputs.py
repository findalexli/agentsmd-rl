"""
Task: sglang-jit-kernel-ci-registration
Repo: sgl-project/sglang @ 6047d2c690483224b2bb7d70288ea60b0b8e0c7d
PR:   21239

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import importlib.util
import sys

REPO = "/workspace"

# Helper: load ci_register without importing the full sglang package
_spec = importlib.util.spec_from_file_location(
    "ci_register", f"{REPO}/python/sglang/test/ci/ci_register.py"
)
_ci_register = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ci_register)
ut_parse_one_file = _ci_register.ut_parse_one_file
collect_tests = _ci_register.collect_tests

TARGET_FILES = [
    f"{REPO}/python/sglang/jit_kernel/benchmark/bench_cast.py",
    f"{REPO}/python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py",
    f"{REPO}/python/sglang/jit_kernel/tests/test_cast.py",
    f"{REPO}/python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py",
]

BENCHMARK_FILES = TARGET_FILES[:2]
TEST_FILES = TARGET_FILES[2:]


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
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_bench_cast_ci_registration():
    """bench_cast.py is discoverable by ci_register AST parser and registered for benchmark suite."""
    regs = ut_parse_one_file(f"{REPO}/python/sglang/jit_kernel/benchmark/bench_cast.py")
    assert regs, "No CI registrations found in bench_cast.py"
    suites = [r.suite for r in regs]
    assert "stage-b-kernel-benchmark-1-gpu-large" in suites, f"Expected benchmark suite, got {suites}"


# [pr_diff] fail_to_pass
def test_bench_fused_qknorm_rope_ci_registration():
    """bench_fused_qknorm_rope.py is discoverable and registered for benchmark suite."""
    regs = ut_parse_one_file(f"{REPO}/python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py")
    assert regs, "No CI registrations found in bench_fused_qknorm_rope.py"
    suites = [r.suite for r in regs]
    assert "stage-b-kernel-benchmark-1-gpu-large" in suites, f"Expected benchmark suite, got {suites}"


# [pr_diff] fail_to_pass
def test_cast_ci_registration():
    """test_cast.py is discoverable and registered for kernel unit suite."""
    regs = ut_parse_one_file(f"{REPO}/python/sglang/jit_kernel/tests/test_cast.py")
    assert regs, "No CI registrations found in test_cast.py"
    suites = [r.suite for r in regs]
    assert "stage-b-kernel-unit-1-gpu-large" in suites, f"Expected unit suite, got {suites}"


# [pr_diff] fail_to_pass
def test_fused_qknorm_rope_ci_registration():
    """test_fused_qknorm_rope.py is discoverable and registered for kernel unit suite."""
    regs = ut_parse_one_file(f"{REPO}/python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py")
    assert regs, "No CI registrations found in test_fused_qknorm_rope.py"
    suites = [r.suite for r in regs]
    assert "stage-b-kernel-unit-1-gpu-large" in suites, f"Expected unit suite, got {suites}"


# [pr_diff] fail_to_pass
def test_collect_tests_no_errors():
    """collect_tests() succeeds on all 4 files without raising ValueError."""
    regs = collect_tests(TARGET_FILES, sanity_check=True)
    assert len(regs) >= 4, f"Expected at least 4 registrations, got {len(regs)}"
    for r in regs:
        assert r.est_time > 0, f"{r.filename} has non-positive est_time: {r.est_time}"


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
    # AST-only because: verifying AST node depth is inherently structural
    for filepath in TARGET_FILES:
        with open(filepath) as f:
            source = f.read()
        tree = ast.parse(source)

        # Only check top-level statements (module body)
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
    for bench_file in BENCHMARK_FILES:
        regs = ut_parse_one_file(bench_file)
        for r in regs:
            assert "kernel-unit" not in r.suite, (
                f"{bench_file}: benchmark file incorrectly registered for unit suite '{r.suite}'"
            )

    for test_file in TEST_FILES:
        regs = ut_parse_one_file(test_file)
        suites = [r.suite for r in regs]
        has_unit = any("kernel-unit" in s for s in suites)
        assert has_unit, f"{test_file}: test file not registered for any kernel unit suite, got {suites}"
