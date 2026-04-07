"""
Task: posthog-featcloudagent-added-sandboxenvironmentid-ext-caller
Repo: PostHog/posthog @ a65a8fd19c2bed0c06c111f1d65b0deb87f31313
PR:   53163

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/posthog"
MODELS_PY = "products/tasks/backend/models.py"
DOCS_MD = "docs/published/handbook/engineering/ai/sandboxed-agents.md"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory via a temp script."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified files must parse without errors."""
    r = _run_py(f"""
import py_compile
py_compile.compile("{MODELS_PY}", doraise=True)
print("PASS")
""")
    assert r.returncode == 0, f"Syntax error in models.py: {r.stderr}"
    assert "PASS" in r.stdout


def test_not_stub_create_and_run():
    """create_and_run() must have real logic, not just pass/return."""
    r = _run_py(f"""
import ast
src = open("{MODELS_PY}").read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "create_and_run":
        body = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))]
        assert len(body) >= 5, f"Only {{len(body)}} statements — looks like a stub"
        print("PASS")
        break
else:
    raise AssertionError("create_and_run not found")
""")
    assert r.returncode == 0, f"Stub check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

def test_create_and_run_accepts_sandbox_environment_id():
    """create_and_run() must accept a sandbox_environment_id parameter."""
    r = _run_py(f"""
import ast
src = open("{MODELS_PY}").read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "create_and_run":
        params = [a.arg for a in node.args.args + node.args.kwonlyargs]
        assert "sandbox_environment_id" in params, f"Parameters: {{params}}"
        print("PASS")
        break
else:
    raise AssertionError("create_and_run not found")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_sandbox_env_validated_against_team():
    """create_and_run() must validate sandbox_environment_id is scoped to the team."""
    r = _run_py(f"""
import ast, re
src = open("{MODELS_PY}").read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "create_and_run":
        lines = src.splitlines()
        fn_src = "\\n".join(lines[node.lineno - 1 : node.end_lineno])
        assert "SandboxEnvironment" in fn_src, "Must reference SandboxEnvironment model"
        assert re.search(r"(filter|get)\\(.*team", fn_src), "Must scope lookup by team"
        print("PASS")
        break
else:
    raise AssertionError("create_and_run not found")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_invalid_sandbox_env_raises_error():
    """create_and_run() must raise an error when sandbox_environment_id is invalid."""
    r = _run_py(f"""
import ast
src = open("{MODELS_PY}").read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "create_and_run":
        lines = src.splitlines()
        fn_src = "\\n".join(lines[node.lineno - 1 : node.end_lineno])
        has_error = "ValueError" in fn_src or "ValidationError" in fn_src
        assert has_error, "Must raise error for invalid sandbox_environment_id"
        assert "sandbox_environment_id" in fn_src or "sandbox_env" in fn_src, \\
            "Error context must reference sandbox"
        print("PASS")
        break
else:
    raise AssertionError("create_and_run not found")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_sandbox_env_id_stored_in_extra_state():
    """sandbox_environment_id must be stored in extra_state for the task run."""
    r = _run_py(f"""
import ast, re
src = open("{MODELS_PY}").read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "create_and_run":
        lines = src.splitlines()
        fn_src = "\\n".join(lines[node.lineno - 1 : node.end_lineno])
        assert "extra_state" in fn_src, "Must use extra_state"
        assert re.search(r'"sandbox_environment_id"', fn_src), \\
            "Must store sandbox_environment_id key in extra_state"
        print("PASS")
        break
else:
    raise AssertionError("create_and_run not found")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — documentation tests
# ---------------------------------------------------------------------------

def test_docs_parameter_table_includes_sandbox_env_id():
    """sandboxed-agents.md parameters table must include sandbox_environment_id."""
    r = _run_py(f"""
content = open("{DOCS_MD}").read()
found = any(
    "sandbox_environment_id" in line and "|" in line
    for line in content.splitlines()
)
assert found, "sandbox_environment_id not found in parameters table"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_docs_has_sandbox_env_usage_example():
    """sandboxed-agents.md must have a code example showing sandbox_environment_id with create_and_run."""
    r = _run_py(f"""
import re
content = open("{DOCS_MD}").read()
blocks = re.findall(r'```python(.*?)```', content, re.DOTALL)
found = any(
    "sandbox_environment_id" in b and "create_and_run" in b
    for b in blocks
)
assert found, "No Python code block showing sandbox_environment_id with create_and_run"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout
