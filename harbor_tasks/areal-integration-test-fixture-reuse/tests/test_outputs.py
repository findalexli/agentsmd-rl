"""
Task: areal-integration-test-fixture-reuse
Repo: inclusionAI/AReaL @ dfeab6396380f27be96ccb7cb642b57a5a25ef58
PR:   #1068

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: The test modules transitively import torch, sglang, and other
GPU-dependent packages that are not installed in the verification
environment. F2P checks use subprocess to evaluate code fragments
(decorator expressions, assignments) in a mock environment.
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
# Gate (pass_to_pass, static) — syntax + byte-compilation check
# ---------------------------------------------------------------------------


def test_syntax_valid():
    """All three test files must be valid Python that compiles to bytecode."""
    r = _run_py(f'''
from pathlib import Path

for fpath in {ALL_FILES!r}:
    source = Path(fpath).read_text()
    # compile() verifies both syntax AND byte-compilation (unlike ast.parse)
    compile(source, fpath, "exec")
print("PASS")
''')
    assert r.returncode == 0, f"Syntax/compilation check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------


def test_fixtures_module_scoped():
    """Evaluate fixture decorator expressions with a mock pytest.fixture
    to verify scope is 'module' or 'session' at runtime."""
    r = _run_py(f'''
import ast, types
from pathlib import Path

# Mock pytest.fixture that records the scope kwarg when called
recorded = {{}}
def mock_fixture(**kwargs):
    def wrap(name):
        recorded[name] = kwargs
    return wrap

source = Path({CTRL_FILE!r}).read_text()
tree = ast.parse(source)

TARGET = ("local_scheduler", "gateway_controller", "gateway_controller_full_init")

for node in ast.walk(tree):
    if not isinstance(node, ast.FunctionDef):
        continue
    if node.name not in TARGET:
        continue
    for dec in node.decorator_list:
        if isinstance(dec, ast.Call):
            dec_src = ast.get_source_segment(source, dec)
            if dec_src and "fixture" in dec_src:
                ns = {{"pytest": types.SimpleNamespace(fixture=mock_fixture)}}
                wrapper = eval(dec_src, ns)
                wrapper(node.name)

for name in TARGET:
    assert name in recorded, (
        f"{{name}}: fixture decorator not evaluated "
        f"(bare @pytest.fixture without scope?)"
    )
    scope = recorded[name].get("scope")
    assert scope in ("module", "session"), (
        f"{{name}}: scope={{scope!r}}, expected 'module' or 'session'"
    )

# Also verify parameter lists are compatible with module scope
params = {{}}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in TARGET:
        params[node.name] = [a.arg for a in node.args.args]

assert "tmp_path_factory" in params.get("local_scheduler", []), (
    f"local_scheduler missing tmp_path_factory, got: {{params.get('local_scheduler')}}"
)
for name in ("gateway_controller", "gateway_controller_full_init"):
    assert "tmp_path" not in params.get(name, []), (
        f"{{name}} still has function-scoped tmp_path param"
    )
print("PASS")
''')
    assert r.returncode == 0, f"Fixture scope check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_pytestmark_sglang_present():
    """Execute the pytestmark assignment in each file with a mock pytest
    module and verify it evaluates to pytest.mark.sglang at runtime."""
    r = _run_py(f'''
import ast, types
from pathlib import Path

SENTINEL = object()

for fpath in {ALL_FILES!r}:
    source = Path(fpath).read_text()
    tree = ast.parse(source)
    found = False

    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not (isinstance(target, ast.Name) and target.id == "pytestmark"):
                continue
            # Build mock pytest where mark.sglang is a sentinel
            mock_mark = types.SimpleNamespace(sglang=SENTINEL)
            mock_pytest = types.SimpleNamespace(mark=mock_mark)

            assign_src = ast.get_source_segment(source, node)
            ns = {{"pytest": mock_pytest}}
            exec(assign_src, ns)

            val = ns.get("pytestmark")
            if val is SENTINEL:
                found = True
            elif isinstance(val, (list, tuple)):
                found = any(v is SENTINEL for v in val)
            break

    assert found, f"{{fpath}}: pytestmark does not evaluate to pytest.mark.sglang"
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


def test_consumer_batch_size_increased():
    """gateway_controller fixture must have consumer_batch_size >= 3
    (increased from 2 to accommodate module-scoped fixture reuse)."""
    r = _run_py(f'''
import ast
from pathlib import Path

tree = ast.parse(Path({CTRL_FILE!r}).read_text())
for node in ast.walk(tree):
    if not isinstance(node, ast.FunctionDef):
        continue
    if node.name != "gateway_controller":
        continue
    found = False
    for child in ast.walk(node):
        if isinstance(child, ast.keyword) and child.arg == "consumer_batch_size":
            if isinstance(child.value, ast.Constant) and isinstance(child.value.value, (int, float)):
                assert child.value.value >= 3, (
                    f"consumer_batch_size={{child.value.value}}, expected >= 3 (was 2)"
                )
                found = True
    assert found, "gateway_controller: consumer_batch_size keyword not found"
    break
print("PASS")
''')
    assert r.returncode == 0, f"consumer_batch_size check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — config-derived check via subprocess
# ---------------------------------------------------------------------------


def test_fixture_no_tmp_path():
    """Module-scoped local_scheduler must not use function-scoped tmp_path.
    Must use tmp_path_factory instead (module-scoped fixture)."""
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
        # Behavioral: verify the module-scoped replacement IS present
        assert "tmp_path_factory" in params, (
            f"local_scheduler must accept tmp_path_factory for module scope. "
            f"Parameters: {{params}}"
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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repo CI/CD checks via AST analysis
# These verify static code quality matching the repo's pre-commit/CI standards
# ---------------------------------------------------------------------------


def test_repo_test_classes_follow_naming():
    """All test classes must follow Test* naming convention (pass_to_pass).

    Matches ruff/pre-commit check: test classes should be named Test*.
    """
    for fpath in ALL_FILES:
        tree = ast.parse(Path(fpath).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a test class (contains test methods)
                has_test_methods = any(
                    isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and n.name.startswith("test_")
                    for n in ast.walk(node)
                )
                if has_test_methods:
                    assert node.name.startswith("Test"), (
                        f"{fpath}: Test class {node.name} should start with 'Test'"
                    )


def test_repo_no_bare_excepts():
    """No bare 'except:' clauses in test files (pass_to_pass).

    Matches ruff E722: do not use bare except.
    """
    for fpath in ALL_FILES:
        tree = ast.parse(Path(fpath).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    if handler.type is None:
                        assert False, (
                            f"{fpath}: Bare 'except:' found at line {handler.lineno}, "
                            f"use 'except Exception:' instead"
                        )


def test_repo_no_unused_imports():
    """No obviously unused standard library imports in test files (pass_to_pass).

    Checks that imported names are referenced somewhere in the module.
    Only checks standard library imports (not pytest, torch, etc.).
    """
    stdlib_modules = {
        "os", "sys", "time", "json", "subprocess", "socket", "threading",
        "pathlib", "typing", "collections", "itertools", "functools",
        "datetime", "random", "string", "re", "hashlib", "base64",
        "contextlib", "dataclasses", "enum", "inspect", "types",
        "warnings", "traceback", "tempfile", "shutil", "glob",
    }

    for fpath in ALL_FILES:
        source = Path(fpath).read_text()
        tree = ast.parse(source)

        # Collect all imports
        imports = {}  # name -> (module, node)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports[alias.asname or alias.name] = (alias.name, node)
            elif isinstance(node, ast.ImportFrom):
                if node.module in stdlib_modules:
                    for alias in node.names:
                        imports[alias.asname or alias.name] = (node.module, node)

        # Collect all name references (simple heuristic)
        referenced = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                referenced.add(node.id)
            elif isinstance(node, ast.Attribute):
                # For attribute access like os.path, reference 'os'
                if isinstance(node.value, ast.Name):
                    referenced.add(node.value.id)

        # Check for unused imports (with some exclusions)
        for name, (module, node) in imports.items():
            if name not in referenced and not name.startswith("_"):
                # Only flag stdlib imports that are clearly unused
                assert False, (
                    f"{fpath}: Unused import '{name}' from {module} at line {node.lineno}"
                )


def test_repo_yaml_files_valid():
    """All YAML files in the repo must be valid (pass_to_pass).

    Matches pre-commit check-yaml hook.
    """
    import yaml

    repo_yaml_files = [
        f"{REPO}/.pre-commit-config.yaml",
    ]

    # Find all YAML files in examples directory
    examples_yaml = list(Path(f"{REPO}/examples").rglob("*.yaml")) + list(Path(f"{REPO}/examples").rglob("*.yml"))

    for fpath in repo_yaml_files + [str(p) for p in examples_yaml]:
        path = Path(fpath)
        if path.exists():
            try:
                yaml.safe_load(path.read_text())
            except yaml.YAMLError as e:
                assert False, f"{fpath}: Invalid YAML - {e}"


def test_repo_pyproject_toml_valid():
    """pyproject.toml must be valid TOML (pass_to_pass).

    Basic syntax check for the repo's main config file.
    """
    import tomllib

    pyproject_path = Path(f"{REPO}/pyproject.toml")
    if pyproject_path.exists():
        try:
            tomllib.loads(pyproject_path.read_text())
        except Exception as e:
            assert False, f"pyproject.toml: Invalid TOML - {e}"
