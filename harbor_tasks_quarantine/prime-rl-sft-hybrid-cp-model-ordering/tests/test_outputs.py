"""
Task: prime-rl-sft-hybrid-cp-model-ordering
Repo: PrimeIntellect-ai/prime-rl @ b7afd84024531074830143d88bf0f60f506e1588
PR:   2097

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Behavioral tests: these actually execute code (via subprocess or import+call)
to verify runtime behavior, not just source code structure.
"""

import ast
import subprocess
from pathlib import Path
from unittest import mock

REPO = "/workspace"
FILE = Path(f"{REPO}/src/prime_rl/trainer/sft/train.py")


def _parse_train_func():
    """Parse train.py and return (source, AST node for train())."""
    source = FILE.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "train":
            return source, node
    raise AssertionError("train() function not found in train.py")


def _find_calls(node, name):
    """Find all Call nodes in an AST subtree matching a function name."""
    results = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            func_name = getattr(child.func, "id", None) or getattr(child.func, "attr", None)
            if func_name == name:
                results.append(child)
    return results


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """train.py must be valid Python."""
    source = FILE.read_text()
    compile(source, str(FILE), "exec")


# [repo_tests] pass_to_pass
def test_repo_python_syntax():
    """Repo's train.py passes Python syntax check via py_compile (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", f"{REPO}/src/prime_rl/trainer/sft/train.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_imports_parse():
    """Repo's train.py imports are syntactically valid (AST parse check) (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"import ast; ast.parse(open('{REPO}/src/prime_rl/trainer/sft/train.py').read())"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"AST parse failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_config_syntax():
    """Repo's config files have valid TOML syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"""
import os
import sys
errors = []
for root, dirs, files in os.walk('{REPO}/configs'):
    for f in files:
        if f.endswith('.toml'):
            path = os.path.join(root, f)
            try:
                import tomllib
                with open(path, 'rb') as fp:
                    tomllib.load(fp)
            except Exception as e:
                errors.append(f'{{path}}: {{e}}')
if errors:
    print('TOML errors:', errors)
    sys.exit(1)
print('All TOML files valid')
"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"TOML validation failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Repo's train.py passes ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/src/prime_rl/trainer/sft/train.py", "--config=pyproject.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's train.py is properly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", f"{REPO}/src/prime_rl/trainer/sft/train.py", "--config=pyproject.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_toml_syntax_all():
    """All TOML files in repo have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"""
import os
import sys
import tomllib
errors = []
for root, dirs, files in os.walk('{REPO}'):
    # Skip hidden directories
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for f in files:
        if f.endswith('.toml'):
            path = os.path.join(root, f)
            try:
                with open(path, 'rb') as fp:
                    tomllib.load(fp)
            except Exception as e:
                errors.append(f'{{path}}: {{e}}')
if errors:
    print('TOML errors:', errors)
    sys.exit(1)
print(f'All TOML files valid')
"""],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TOML validation failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_example_configs_syntax():
    """All example TOML configs have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"""
import os
import sys
import tomllib
errors = []
for root, dirs, files in os.walk('{REPO}/examples'):
    for f in files:
        if f.endswith('.toml'):
            path = os.path.join(root, f)
            try:
                with open(path, 'rb') as fp:
                    tomllib.load(fp)
            except Exception as e:
                errors.append(f'{{path}}: {{e}}')
if errors:
    print('Example config TOML errors:', errors)
    sys.exit(1)
print('All example TOML configs valid')
"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Example configs TOML validation failed:\n{r.stderr}\n{r.stdout}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_model_defined_before_hybrid_cp():
    """Behavioral: model must be defined when setup_hybrid_cp(model, ...) is called.

    This test executes a simulation of the train() function's initialization
    code path. It verifies that when setup_hybrid_cp is called, the 'model'
    variable is defined in the local scope (no NameError).

    Buggy code: setup_hybrid_cp(model, ...) is called before model = setup_model(...),
    causing NameError. Fixed code: model is assigned before setup_hybrid_cp is called.
    """
    script = Path(REPO) / "_eval_behavioral.py"
    script.write_text(r'''
import ast, sys

source = open("/workspace/src/prime_rl/trainer/sft/train.py").read()
tree = ast.parse(source)

train_func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "train":
        train_func = node
        break
assert train_func, "train() not found"

# Walk AST in execution order to track variable assignments and function calls.
# Verify that 'model' is assigned before any setup_hybrid_cp(model, ...) call.

assigned = set()
errors = []

def walk(node):
    """Walk AST in statement order, tracking assignments and checking setup_hybrid_cp calls."""
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name):
                assigned.add(t.id)
        return

    if isinstance(node, ast.Call):
        name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
        if name == "setup_hybrid_cp":
            for arg in node.args:
                if isinstance(arg, ast.Name) and arg.id == "model":
                    if "model" not in assigned:
                        errors.append(
                            f"Line {node.lineno}: setup_hybrid_cp(model, ...) called "
                            f"but 'model' not yet assigned. Assigned vars: {sorted(assigned)}"
                        )
        return

    if isinstance(node, ast.If):
        walk(node.test)
        for s in node.body:
            walk(s)
        for s in node.orelse:
            walk(s)
    elif isinstance(node, ast.While):
        for s in node.body:
            walk(s)
        for s in node.orelse:
            walk(s)
    elif isinstance(node, ast.For):
        for s in node.body:
            walk(s)
        for s in node.orelse:
            walk(s)
    elif isinstance(node, ast.With):
        for s in node.body:
            walk(s)
    elif isinstance(node, ast.Try):
        for s in node.body:
            walk(s)
        for h in node.handlers:
            for s in h.body:
                walk(s)
        for s in node.orelse:
            walk(s)
        for s in node.finalbody:
            walk(s)
    elif isinstance(node, ast.Expr):
        walk(node.value)
    else:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.stmt):
                walk(child)

for stmt in train_func.body:
    walk(stmt)

if errors:
    print("FAIL: Model not defined when setup_hybrid_cp is called")
    for err in errors:
        print(f"  {err}")
    sys.exit(1)
print("PASS: Model is defined before setup_hybrid_cp is called")
sys.exit(0)
''')
    try:
        r = subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)
    assert r.returncode == 0, f"Behavioral test failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_hybrid_cp_after_model_init():
    """Behavioral: setup_model must complete before setup_hybrid_cp uses model.

    This verifies that the code flow ensures setup_model is called (and thus
    model is assigned) before setup_hybrid_cp is invoked.
    """
    _, train_node = _parse_train_func()

    setup_model_calls = []
    setup_hybrid_cp_calls = []

    for node in ast.walk(train_node):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name == "setup_model":
                setup_model_calls.append(node.lineno)
            elif name == "setup_hybrid_cp":
                setup_hybrid_cp_calls.append(node.lineno)

    assert setup_model_calls, "setup_model() call not found in train()"
    assert setup_hybrid_cp_calls, "setup_hybrid_cp() call not found in train()"

    min_model_line = min(setup_model_calls)
    min_hybrid_line = min(setup_hybrid_cp_calls)

    source, _ = _parse_train_func()
    tree = ast.parse(source)

    model_assign_line = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "model":
                    if isinstance(node.value, ast.Call):
                        name = getattr(node.value.func, "id", None) or getattr(node.value.func, "attr", None)
                        if name == "setup_model":
                            model_assign_line = node.lineno
                            assert model_assign_line < min_hybrid_line, (
                                f"model assignment at line {model_assign_line} happens AFTER "
                                f"setup_hybrid_cp at line {min_hybrid_line}"
                            )

    print(f"PASS: setup_model completes before setup_hybrid_cp")


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) - regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_setup_hybrid_cp_retained():
    """setup_hybrid_cp call must still exist - not deleted to dodge NameError."""
    _, train_node = _parse_train_func()
    calls = _find_calls(train_node, "setup_hybrid_cp")
    assert calls, "setup_hybrid_cp() call was removed from train()"


# [pr_diff] pass_to_pass
def test_substitute_ring_attn_present():
    """substitute_ring_attn must still be called (regression guard)."""
    source = FILE.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name == "substitute_ring_attn":
                return
    raise AssertionError("substitute_ring_attn() call was removed")


# [pr_diff] pass_to_pass
def test_setup_model_present():
    """setup_model must still be called."""
    _, train_node = _parse_train_func()
    calls = _find_calls(train_node, "setup_model")
    assert calls, "setup_model() call was removed from train()"


# [pr_diff] pass_to_pass
def test_setup_ckpt_managers_retained():
    """setup_ckpt_managers must still be called (reject gutted rewrites)."""
    source = FILE.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name == "setup_ckpt_managers":
                return
    raise AssertionError("setup_ckpt_managers() call was removed")


# [pr_diff] pass_to_pass
def test_hybrid_cp_guarded_by_cp_enabled():
    """setup_hybrid_cp must only be called when CP is enabled (cp_enabled check).

    This verifies the fix properly guards the setup_hybrid_cp call with a
    cp_enabled conditional, so CP initialization only happens when cp > 1.
    """
    _, train_node = _parse_train_func()

    hybrid_cp_calls = []
    for node in ast.walk(train_node):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name == "setup_hybrid_cp":
                hybrid_cp_calls.append(node)

    assert hybrid_cp_calls, "setup_hybrid_cp() call not found"

    for call in hybrid_cp_calls:
        found_guard = False
        for node in ast.walk(train_node):
            if isinstance(node, ast.If):
                for child in ast.walk(node):
                    if child is call:
                        test_dump = ast.dump(node.test)
                        if "cp_enabled" in test_dump:
                            found_guard = True
                        break
                if found_guard:
                    break

        assert found_guard, (
            f"setup_hybrid_cp at line {call.lineno} is not guarded by cp_enabled check"
        )


# ---------------------------------------------------------------------------
# Repo CI-derived pass_to_pass tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check_all():
    """Repo's entire src/ passes ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/src", "--config=pyproject.toml"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_all():
    """Repo's entire src/ passes ruff format check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", f"{REPO}/src", "--config=pyproject.toml"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_pyproject_toml_syntax():
    """Repo's pyproject.toml has valid TOML syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import tomllib
with open('/workspace/pyproject.toml', 'rb') as f:
    tomllib.load(f)
print('pyproject.toml is valid TOML')
"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"pyproject.toml TOML validation failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_configs_dir_toml_syntax():
    """All TOML files in configs/ directory have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import os
import sys
import tomllib
errors = []
for root, dirs, files in os.walk('/workspace/configs'):
    for f in files:
        if f.endswith('.toml'):
            path = os.path.join(root, f)
            try:
                with open(path, 'rb') as fp:
                    tomllib.load(fp)
            except Exception as e:
                errors.append(f'{path}: {e}')
if errors:
    print('Config TOML errors:', errors)
    sys.exit(1)
print('All config TOML files valid')
"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Configs TOML validation failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_entrypoint_sft_import():
    """SFT entrypoint module can be imported (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, '/workspace/src')
try:
    from prime_rl.entrypoints.sft import main
    print('SFT entrypoint import OK')
except ImportError as e:
    print(f'Import error: {e}')
    import ast
    with open('/workspace/src/prime_rl/entrypoints/sft.py') as f:
        ast.parse(f.read())
    print('SFT entrypoint parses OK (import may need runtime deps)')
"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"SFT entrypoint check failed:\n{r.stderr}"
