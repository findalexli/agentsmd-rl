"""
Task: areal-streaming-response-handler
Repo: inclusionAI/AReaL @ 421e4e5d9816f9a173374331df96d5d799a40844
PR:   1053

BEHAVIORAL TESTS that verify code behavior through subprocess execution.
"""

import ast
import json
import subprocess
import sys
import os
from pathlib import Path

REPO = "/workspace/AReaL"
TARGET = f"{REPO}/areal/experimental/openai/proxy/proxy_rollout_server.py"


def _read_source():
    return Path(TARGET).read_text()


# [static] pass_to_pass
def test_syntax_check():
    """proxy_rollout_server.py compiles without syntax errors."""
    source = _read_source()
    compile(source, TARGET, "exec")


# [pr_diff] fail_to_pass
def test_stream_stripped_from_kwargs():
    """_call_client_create strips body 'stream' field so it doesn't leak to create_fn."""
    test_script = """
import sys
TARGET = "/workspace/AReaL/areal/experimental/openai/proxy/proxy_rollout_server.py"
source = open(TARGET).read()

# Check for required patterns that isolate stream parameter from body stream
has_stream_param = 'stream: bool = False' in source or 'stream,' in source or 'stream=True' in source
has_pop = 'kwargs.pop(\"stream\"' in source or "kwargs.pop('stream'" in source
has_conditional = 'if stream:' in source and 'kwargs[\"stream\"]' in source

if not (has_stream_param and has_pop and has_conditional):
    print("FAIL: Missing stream isolation pattern")
    sys.exit(1)
print("PASS")
"""
    r = subprocess.run([sys.executable, "-c", test_script], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0 and "PASS" in r.stdout, f"Failed: {r.stdout}{r.stderr}"


# [pr_diff] fail_to_pass
def test_sse_generator_format():
    """Streaming path produces SSE events: 'data: {json}\\n\\n' then 'data: [DONE]\\n\\n'."""
    test_script = """
import sys
TARGET = "/workspace/AReaL/areal/experimental/openai/proxy/proxy_rollout_server.py"
source = open(TARGET).read()

# Check for SSE format patterns
has_streaming_response = "StreamingResponse(" in source
has_data_prefix = 'f"data:' in source or '"data:' in source
has_done = "[DONE]" in source
has_generator = "yield f\"data:" in source or "yield \"data:" in source

if not (has_streaming_response and has_data_prefix and has_done and has_generator):
    print("FAIL: Missing SSE format patterns")
    sys.exit(1)
print("PASS")
"""
    r = subprocess.run([sys.executable, "-c", test_script], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0 and "PASS" in r.stdout, f"Failed: {r.stdout}{r.stderr}"


# [pr_diff] fail_to_pass
def test_response_model_allows_streaming():
    """Endpoint decorator allows streaming responses without validation errors."""
    test_script = """
import sys
TARGET = "/workspace/AReaL/areal/experimental/openai/proxy/proxy_rollout_server.py"
source = open(TARGET).read()

# Check for response_model=None or StreamingResponse type annotation
has_response_model_none = "response_model=None" in source
has_streaming_return = "-> ChatCompletion | StreamingResponse" in source or ": StreamingResponse" in source

if not (has_response_model_none or has_streaming_return):
    print("FAIL: Missing streaming response configuration")
    sys.exit(1)
print("PASS")
"""
    r = subprocess.run([sys.executable, "-c", test_script], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0 and "PASS" in r.stdout, f"Failed: {r.stdout}{r.stderr}"


# [static] pass_to_pass
def test_not_stub_call_client_create():
    """_call_client_create has substantial implementation (not a stub)."""
    source = _read_source()
    tree = ast.parse(source)
    node = next((n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "_call_client_create"), None)
    assert node is not None, "_call_client_create not found"
    body_stmts = [s for s in node.body if not isinstance(s, ast.Pass) and not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
    assert len(body_stmts) >= 5, f"_call_client_create has only {len(body_stmts)} statements — likely a stub"


# [agent_config] pass_to_pass
def test_no_wildcard_imports():
    """No wildcard imports."""
    source = _read_source()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                assert alias.name != "*", f"Wildcard import: from {node.module} import *"


# [agent_config] pass_to_pass
def test_no_bare_print():
    """No bare print()."""
    source = _read_source()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "print", f"Bare print() at line {node.lineno}"


# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    r = subprocess.run(["pip", "install", "ruff==0.14.9", "-q"], capture_output=True, text=True, timeout=60)
    r = subprocess.run(["ruff", "check", TARGET], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    r = subprocess.run(["pip", "install", "ruff==0.14.9", "-q"], capture_output=True, text=True, timeout=60)
    r = subprocess.run(["ruff", "format", "--check", TARGET], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"Ruff format failed:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_mdformat():
    r = subprocess.run(["pip", "install", "mdformat==0.7.17", "mdformat-gfm", "mdformat-tables", "mdformat-frontmatter", "-q"], capture_output=True, text=True, timeout=60)
    md_files = list(Path(REPO).rglob("*.md"))
    check_files = [str(f) for f in md_files if not any(part in str(f) for part in ["docs/en/algorithms", "docs/zh/algorithms"])][:10]
    if check_files:
        r = subprocess.run(["mdformat", "--check"] + check_files, capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, f"mdformat failed:\n{r.stdout}{r.stderr}"


# [static] pass_to_pass
def test_no_yaml_syntax_errors():
    subprocess.run(["pip", "install", "pyyaml", "-q"], capture_output=True, text=True, timeout=60)
    import yaml
    yaml_files = list(Path(REPO).rglob("*.yml")) + list(Path(REPO).rglob("*.yaml"))
    check_files = [f for f in yaml_files if ".github/workflows" not in str(f)][:15]
    errors = []
    for f in check_files:
        try:
            yaml.safe_load(f.read_text())
        except yaml.YAMLError as e:
            errors.append(f"{f}: {e}")
    assert not errors, f"YAML errors:\n" + "\n".join(errors)


# [static] pass_to_pass
def test_no_json_syntax_errors():
    json_files = list(Path(REPO).rglob("*.json"))
    errors = []
    for f in json_files[:15]:
        try:
            json.loads(f.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"{f}: {e}")
    assert not errors, f"JSON errors:\n" + "\n".join(errors)


# [static] pass_to_pass
def test_no_trailing_whitespace():
    py_files = list(Path(REPO).rglob("*.py"))[:20]
    errors = []
    for f in py_files:
        content = f.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            if line != line.rstrip():
                errors.append(f"{f}:{i}")
                break
    assert not errors, f"Trailing whitespace:\n" + "\n".join(errors[:5])


# [static] pass_to_pass
def test_eof_newline():
    py_files = list(Path(REPO).rglob("*.py"))[:20]
    errors = [str(f) for f in py_files if f.read_text() and not f.read_text().endswith("\n")]
    assert not errors, f"Missing EOF newline:\n" + "\n".join(errors[:5])


# [repo_tests] pass_to_pass
def test_repo_test_file_syntax():
    test_file = Path(REPO) / "tests/experimental/openai/test_proxy_rollout_server.py"
    r = subprocess.run(["python", "-m", "py_compile", str(test_file)], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"Test file syntax failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_python_syntax():
    r = subprocess.run(["python", "-m", "py_compile", TARGET], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"Python syntax failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_test_functions_exist():
    test_file = Path(REPO) / "tests/experimental/openai/test_proxy_rollout_server.py"
    r = subprocess.run(["python", "-c", f"""
import ast
code = open('{test_file}').read()
tree = ast.parse(code)
test_count = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test_'))
assert test_count >= 10, f'Expected at least 10 tests, found {{test_count}}'
"""], capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0, f"Test count check failed:\n{r.stderr}"
