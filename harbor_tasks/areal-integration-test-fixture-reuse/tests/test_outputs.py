"""
Task: areal-integration-test-fixture-reuse
Repo: inclusionAI/AReaL @ dfeab6396380f27be96ccb7cb642b57a5a25ef58
PR:   #1068

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: The test modules transitively import torch, sglang, and other
GPU-dependent packages that are not installed in the verification
environment. F2P checks use subprocess to execute Python AST analysis.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/AReaL"

CTRL_FILE = f"{REPO}/tests/experimental/inference_service/test_controller_integration.py"
PROXY_FILE = f"{REPO}/tests/experimental/inference_service/test_data_proxy_integration.py"
GW_FILE = f"{REPO}/tests/experimental/inference_service/test_gateway_integration.py"

ALL_FILES = [CTRL_FILE, PROXY_FILE, GW_FILE]


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via subprocess; return CompletedProcess."""
    script = Path("/tmp/_eval_check.py")
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------


def test_syntax_valid():
    """All three test files must be valid Python."""
    for fpath in ALL_FILES:
        source = Path(fpath).read_text()
        ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------


def test_fixtures_module_scoped():
    """local_scheduler, gateway_controller, gateway_controller_full_init
    must be scoped module or session (not function)."""
    r = _run_py(f'''
import ast
from pathlib import Path

tree = ast.parse(Path({CTRL_FILE!r}).read_text())
scopes = {{}}
for node in ast.walk(tree):
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        continue
    for dec in node.decorator_list:
        if isinstance(dec, ast.Call):
            func = dec.func
            is_fixture = (
                (isinstance(func, ast.Attribute) and func.attr == "fixture")
                or (isinstance(func, ast.Name) and func.id == "fixture")
            )
            if is_fixture:
                scope = None
                for kw in dec.keywords:
                    if kw.arg == "scope" and isinstance(kw.value, ast.Constant):
                        scope = kw.value.value
                scopes[node.name] = scope
        elif isinstance(dec, ast.Attribute) and dec.attr == "fixture":
            scopes[node.name] = None

required = ["local_scheduler", "gateway_controller", "gateway_controller_full_init"]
for name in required:
    scope = scopes.get(name)
    assert scope in ("module", "session"), (
        f"{{name}} has scope={{scope!r}}, expected module or session"
    )
print("PASS")
''')
    assert r.returncode == 0, f"Fixture scope check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_pytestmark_sglang_present():
    """All 3 test files must have module-level pytestmark with
    pytest.mark.sglang."""
    r = _run_py(f'''
import ast
from pathlib import Path


def _has_sglang_mark(node):
    if isinstance(node, ast.Attribute) and node.attr == "sglang":
        return True
    if isinstance(node, ast.Call):
        return _has_sglang_mark(node.func)
    return False


for fpath in {ALL_FILES!r}:
    tree = ast.parse(Path(fpath).read_text())
    found = False
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not (isinstance(target, ast.Name) and target.id == "pytestmark"):
                continue
            val = node.value
            if _has_sglang_mark(val):
                found = True
            elif isinstance(val, (ast.List, ast.Tuple)):
                found = any(_has_sglang_mark(elt) for elt in val.elts)
    assert found, f"{{fpath}} missing pytestmark containing pytest.mark.sglang"
print("PASS")
''')
    assert r.returncode == 0, f"pytestmark check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_slow_marker_removed():
    """No test class should have @pytest.mark.slow decorator."""
    r = _run_py(f'''
import ast
from pathlib import Path

for fpath in {ALL_FILES!r}:
    tree = ast.parse(Path(fpath).read_text())
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for dec in node.decorator_list:
            is_slow = False
            if (
                isinstance(dec, ast.Attribute)
                and dec.attr == "slow"
                and isinstance(dec.value, ast.Attribute)
                and dec.value.attr == "mark"
            ):
                is_slow = True
            if (
                isinstance(dec, ast.Call)
                and isinstance(dec.func, ast.Attribute)
                and dec.func.attr == "slow"
            ):
                is_slow = True
            assert not is_slow, (
                f"{{fpath}} class {{node.name}} still has @pytest.mark.slow"
            )
print("PASS")
''')
    assert r.returncode == 0, f"Slow marker check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_should_accept_fn_tests_removed():
    """Tests referencing should_accept_fn must be removed from controller
    integration tests (incompatible with module-scoped fixtures)."""
    r = _run_py(f'''
import ast
from pathlib import Path

tree = ast.parse(Path({CTRL_FILE!r}).read_text())
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        assert "should_accept_fn" not in node.name, (
            f"Found test method {{node.name}} — should_accept_fn tests must be removed"
        )
print("PASS")
''')
    assert r.returncode == 0, f"should_accept_fn removal check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_controller_settings_loosened():
    """gateway_controller and gateway_controller_full_init must have
    max_head_offpolicyness >= 100 to avoid throttling with module-scoped
    fixtures."""
    r = _run_py(f'''
import ast
from pathlib import Path

tree = ast.parse(Path({CTRL_FILE!r}).read_text())
for node in ast.walk(tree):
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        continue
    if node.name not in ("gateway_controller", "gateway_controller_full_init"):
        continue
    found_mho = False
    for child in ast.walk(node):
        if isinstance(child, ast.keyword) and child.arg == "max_head_offpolicyness":
            if isinstance(child.value, ast.Constant) and isinstance(child.value.value, (int, float)):
                assert child.value.value >= 100, (
                    f"{{node.name}}: max_head_offpolicyness={{child.value.value}}, expected >= 100"
                )
                found_mho = True
    assert found_mho, f"{{node.name}}: max_head_offpolicyness keyword not found"
print("PASS")
''')
    assert r.returncode == 0, f"Controller settings check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — config-derived check via subprocess
# ---------------------------------------------------------------------------


def test_fixture_no_tmp_path():
    """Module-scoped local_scheduler must not use function-scoped tmp_path.
    Should use tmp_path_factory or tempfile.mkdtemp instead."""
    r = _run_py(f'''
import ast
from pathlib import Path

tree = ast.parse(Path({CTRL_FILE!r}).read_text())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "local_scheduler":
        params = [a.arg for a in node.args.args]
        assert "tmp_path" not in params, (
            f"local_scheduler uses tmp_path (function-scoped), "
            f"incompatible with module scope. Parameters: {{params}}"
        )
        break
else:
    raise AssertionError("local_scheduler fixture not found")
print("PASS")
''')
    assert r.returncode == 0, f"tmp_path check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------


def test_core_test_classes_preserved():
    """All non-removed test classes must still exist in their respective files."""
    checks = {
        CTRL_FILE: [
            "TestControllerLifecycle", "TestControllerVersioning",
            "TestControllerPauseResume", "TestControllerRolloutBatch",
            "TestControllerPrepareBatch", "TestControllerSubmitWait",
            "TestControllerFullInitialization",
        ],
        PROXY_FILE: [
            "TestChatCompletionsIntegration", "TestPauseResumeIntegration",
            "TestConcurrentPauseDuringGeneration",
        ],
        GW_FILE: [
            "TestGatewayStackHealth", "TestGatewayChatCompletions",
            "TestGatewaySessionLifecycle", "TestGatewayAuth",
            "TestGatewayPauseContinue",
        ],
    }
    for fpath, required in checks.items():
        tree = ast.parse(Path(fpath).read_text())
        classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
        for cls in required:
            assert cls in classes, f"Missing class {cls} in {fpath}"


def test_fake_dataloader_preserved():
    """_FakeDataLoader helper class must not be removed from controller tests."""
    tree = ast.parse(Path(CTRL_FILE).read_text())
    classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    assert "_FakeDataLoader" in classes, "_FakeDataLoader removed from controller tests"


def test_files_not_stubbed():
    """Test files must have substantial content — not stubbed out or emptied."""
    min_lines = 100
    min_methods = 3
    for fpath in ALL_FILES:
        source = Path(fpath).read_text()
        lines = len(source.splitlines())
        assert lines >= min_lines, f"{fpath} has only {lines} lines (min {min_lines})"

        tree = ast.parse(source)
        test_methods = [
            n for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and n.name.startswith("test_")
        ]
        assert len(test_methods) >= min_methods, (
            f"{fpath} has only {len(test_methods)} test methods (min {min_methods})"
        )

        stub_count = 0
        for m in test_methods:
            if len(m.body) <= 1:
                stmt = m.body[0] if m.body else None
                if isinstance(stmt, ast.Pass):
                    stub_count += 1
                elif (isinstance(stmt, ast.Expr)
                      and isinstance(stmt.value, ast.Constant)
                      and isinstance(stmt.value.value, str)):
                    stub_count += 1
        assert stub_count <= len(test_methods) // 2, (
            f"{fpath} has {stub_count}/{len(test_methods)} stub test methods"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — config-derived regression
# ---------------------------------------------------------------------------


def test_gpu_skipif_has_reason():
    """All @pytest.mark.skipif decorators that check GPU availability must
    have an explicit reason= argument (AGENTS.md: 'GPU: skip gracefully')."""
    for fpath in ALL_FILES:
        tree = ast.parse(Path(fpath).read_text())
        for node in ast.walk(tree):
            if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for dec in node.decorator_list:
                if not (
                    isinstance(dec, ast.Call)
                    and isinstance(dec.func, ast.Attribute)
                    and dec.func.attr == "skipif"
                ):
                    continue
                dec_src = ast.unparse(dec)
                if "has_gpu" not in dec_src and "_has_gpu" not in dec_src:
                    continue
                has_reason = any(
                    kw.arg == "reason"
                    and isinstance(kw.value, ast.Constant)
                    and kw.value.value
                    for kw in dec.keywords
                )
                assert has_reason, (
                    f"{fpath}: {node.name} has @pytest.mark.skipif with GPU check "
                    f"but no non-empty reason= argument"
                )


def test_no_wildcard_imports():
    """No wildcard imports (from x import *) in any test file."""
    for fpath in ALL_FILES:
        tree = ast.parse(Path(fpath).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    assert alias.name != "*", (
                        f"Wildcard import in {fpath}: from {node.module} import *"
                    )
