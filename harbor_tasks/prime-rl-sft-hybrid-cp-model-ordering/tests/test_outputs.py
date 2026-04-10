"""
Task: prime-rl-sft-hybrid-cp-model-ordering
Repo: PrimeIntellect-ai/prime-rl @ b7afd84024531074830143d88bf0f60f506e1588
PR:   2097

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_model_assigned_before_hybrid_cp():
    """model must be assigned (via setup_model) before setup_hybrid_cp(model, ...) is called.

    Executes a dataflow simulation: walks train() body in execution order,
    tracking when 'model' is assigned and when setup_hybrid_cp(model, ...) is
    called. Catches the base-commit bug where model is used before definition.
    """
    script = Path(REPO) / "_eval_flow_check.py"
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

# Walk function body in statement order, tracking model assignment and
# setup_hybrid_cp usage. Recurse into if/for/while/with/try blocks.
state = {"model_assigned": None, "hybrid_cp_called": None}

def scan(stmts):
    for stmt in stmts:
        # Check for model assignment at this statement level
        if isinstance(stmt, ast.Assign):
            for t in stmt.targets:
                names = []
                if isinstance(t, ast.Name):
                    names.append(t.id)
                elif isinstance(t, ast.Tuple):
                    names.extend(e.id for e in t.elts if isinstance(e, ast.Name))
                if "model" in names and state["model_assigned"] is None:
                    state["model_assigned"] = stmt.lineno

        # Check for setup_hybrid_cp call anywhere in this statement's subtree
        for child in ast.walk(stmt):
            if isinstance(child, ast.Call):
                name = getattr(child.func, "id", None) or getattr(child.func, "attr", None)
                if name == "setup_hybrid_cp" and state["hybrid_cp_called"] is None:
                    state["hybrid_cp_called"] = child.lineno

        # Recurse into control flow bodies
        if isinstance(stmt, ast.If):
            scan(stmt.body)
            scan(stmt.orelse)
        elif isinstance(stmt, (ast.For, ast.While)):
            scan(stmt.body)
        elif isinstance(stmt, ast.With):
            scan(stmt.body)
        elif isinstance(stmt, ast.Try):
            scan(stmt.body)
            for h in stmt.handlers:
                scan(h.body)
            scan(stmt.orelse)
            scan(stmt.finalbody)

scan(train_func.body)

assert state["model_assigned"], "model never assigned in train()"
assert state["hybrid_cp_called"], "setup_hybrid_cp never called in train()"

if state["hybrid_cp_called"] < state["model_assigned"]:
    print(f"FAIL: setup_hybrid_cp at line {state['hybrid_cp_called']} before model assigned at line {state['model_assigned']}")
    sys.exit(1)
print("PASS")
''')
    try:
        r = subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_hybrid_cp_after_model_init():
    """setup_hybrid_cp() must be called AFTER setup_model() in train().

    Executes a script that compares line numbers of setup_model() and
    setup_hybrid_cp() calls to verify correct initialization ordering.
    """
    script = Path(REPO) / "_eval_call_order.py"
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

setup_model_lines = []
setup_hybrid_cp_lines = []
for node in ast.walk(train_func):
    if isinstance(node, ast.Call):
        name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
        if name == "setup_model":
            setup_model_lines.append(node.lineno)
        elif name == "setup_hybrid_cp":
            setup_hybrid_cp_lines.append(node.lineno)

assert setup_model_lines, "setup_model() not found in train()"
assert setup_hybrid_cp_lines, "setup_hybrid_cp() not found in train()"

sm = min(setup_model_lines)
shcp = min(setup_hybrid_cp_lines)

if shcp <= sm:
    print(f"FAIL: setup_hybrid_cp (line {shcp}) before setup_model (line {sm})")
    sys.exit(1)
print(f"PASS: setup_model (line {sm}) before setup_hybrid_cp (line {shcp})")
''')
    try:
        r = subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_setup_hybrid_cp_retained():
    """setup_hybrid_cp call must still exist — not deleted to dodge NameError."""
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


# [static] pass_to_pass
def test_train_not_stub():
    """train() must have >= 20 top-level statements (reject total rewrites)."""
    _, train_node = _parse_train_func()
    assert len(train_node.body) >= 20, (
        f"train() has only {len(train_node.body)} statements — likely a stub"
    )


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
    """setup_hybrid_cp must be inside a cp_enabled conditional (not called unconditionally)."""
    _, train_node = _parse_train_func()
    for node in ast.walk(train_node):
        if isinstance(node, ast.If):
            test_src = ast.dump(node.test)
            if "cp_enabled" in test_src:
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        name = getattr(child.func, "id", None) or getattr(child.func, "attr", None)
                        if name == "setup_hybrid_cp":
                            return
    raise AssertionError(
        "setup_hybrid_cp() is not guarded by a cp_enabled check — "
        "it must only run when context parallelism is enabled"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:5 @ b7afd84024531074830143d88bf0f60f506e1588
def test_no_try_except_around_hybrid_cp():
    """setup_hybrid_cp must not be wrapped in try/except (AGENTS.md: avoid unnecessary try/except)."""
    source = FILE.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    name = getattr(child.func, "id", None) or getattr(child.func, "attr", None)
                    if name == "setup_hybrid_cp":
                        raise AssertionError(
                            "setup_hybrid_cp is inside a try/except block — "
                            "AGENTS.md says avoid unnecessary try/except"
                        )
