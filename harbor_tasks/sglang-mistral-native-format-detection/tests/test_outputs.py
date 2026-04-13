"""
Task: sglang-mistral-native-format-detection
Repo: sgl-project/sglang @ b2462694441412ad209c361dfa87f3f37a3d29f3
PR:   21620

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import os
import subprocess
import tempfile
import textwrap
import types
from pathlib import Path

REPO = "/repo"
TARGET_FILE = f"{REPO}/python/sglang/srt/server_args.py"


def _build_check_script(model_name: str, has_params: bool, has_config: bool) -> str:
    """Build a Python script that extracts and calls _is_mistral_native_format."""
    lines = [
        "import ast, os, tempfile, textwrap, types",
        "from pathlib import Path",
        "",
        f"TARGET = {TARGET_FILE!r}",
        "source = Path(TARGET).read_text()",
        "src_lines = source.splitlines(keepends=True)",
        "tree = ast.parse(source)",
        "for node in ast.walk(tree):",
        "    if isinstance(node, ast.FunctionDef) and node.name == '_is_mistral_native_format':",
        "        func_src = textwrap.dedent(''.join(src_lines[node.lineno - 1 : node.end_lineno]))",
        "        break",
        "else:",
        "    raise RuntimeError('_is_mistral_native_format not found')",
        "",
        "tmpdir = tempfile.mkdtemp()",
        f"model_dir = os.path.join(tmpdir, 'models', {model_name!r})",
        "os.makedirs(model_dir, exist_ok=True)",
    ]
    if has_params:
        lines.append("Path(os.path.join(model_dir, 'params.json')).write_text('{}')")
    if has_config:
        lines.append("Path(os.path.join(model_dir, 'config.json')).write_text('{}')")
    lines += [
        "",
        "ns = {'os': os, 're': __import__('re'), '__builtins__': __builtins__}",
        "exec(compile('import os, re\\n' + func_src, '<test>', 'exec'), ns)",
        "func = ns['_is_mistral_native_format']",
        "mock = types.SimpleNamespace(model_path=model_dir)",
        "result = func(mock)",
        "print('NATIVE_RESULT:', result)",
    ]
    return "\n".join(lines)


def _run_native_format_check(model_name: str, has_params: bool, has_config: bool) -> bool:
    """Run _is_mistral_native_format in a subprocess and return the boolean result."""
    script_path = Path(REPO) / "_eval_tmp.py"
    script_path.write_text(_build_check_script(model_name, has_params, has_config))
    try:
        r = subprocess.run(
            ["python3", str(script_path)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Script failed:\n{r.stderr}"
        output = r.stdout.strip()
        if "NATIVE_RESULT: True" in output:
            return True
        if "NATIVE_RESULT: False" in output:
            return False
        raise AssertionError(f"Unexpected output: {output}")
    finally:
        script_path.unlink(missing_ok=True)


def _extract_function(filepath, funcname):
    """Extract a method's source from a file using AST."""
    source = Path(filepath).read_text()
    lines = source.splitlines(keepends=True)
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == funcname:
            return textwrap.dedent("".join(lines[node.lineno - 1 : node.end_lineno]))
    raise RuntimeError(f"{funcname} not found in {filepath}")


def _call_is_mistral_native(model_name, has_params, has_config):
    """Create a temp model dir and invoke _is_mistral_native_format (in-process)."""
    func_src = _extract_function(TARGET_FILE, "_is_mistral_native_format")

    tmpdir = tempfile.mkdtemp()
    model_dir = os.path.join(tmpdir, "models", model_name)
    os.makedirs(model_dir, exist_ok=True)
    if has_params:
        Path(os.path.join(model_dir, "params.json")).write_text("{}")
    if has_config:
        Path(os.path.join(model_dir, "config.json")).write_text("{}")

    exec_ns = {"os": os, "re": __import__("re"), "__builtins__": __builtins__}
    exec(compile("import os, re\n" + func_src, "<test>", "exec"), exec_ns)
    func = exec_ns["_is_mistral_native_format"]

    mock_self = types.SimpleNamespace(model_path=model_dir)
    return func(mock_self)


# [static] pass_to_pass
def test_syntax_check():
    """server_args.py must parse without syntax errors."""
    source = Path(TARGET_FILE).read_text()
    ast.parse(source)


# [pr_diff] fail_to_pass
def test_mistral_small_4_both_files_returns_true():
    assert _run_native_format_check("Mistral-Small-4-119B-2603", True, True) is True


def test_mistral_large_3_both_files_returns_true():
    assert _run_native_format_check("Mistral-Large-3-2503", True, True) is True


def test_leanstral_both_files_returns_true():
    assert _run_native_format_check("Leanstral-22B-v0.1", True, True) is True


def test_mistral_small_4_variant_both_files_returns_true():
    assert _run_native_format_check("Mistral-Small-4-Base", True, True) is True


# [pr_diff] pass_to_pass
def test_params_only_returns_true():
    assert _call_is_mistral_native("SomeMistralModel", True, False) is True


def test_mistral_7b_params_only_returns_true():
    assert _call_is_mistral_native("Mistral-7B-Instruct-v0.3", True, False) is True


def test_mistral_7b_both_files_returns_false():
    assert _call_is_mistral_native("Mistral-7B-Instruct-v0.3", True, True) is False


def test_codestral_mamba_both_files_returns_false():
    assert _call_is_mistral_native("Codestral-Mamba-22B-v0.1", True, True) is False


def test_pixtral_both_files_returns_false():
    assert _call_is_mistral_native("Pixtral-12B-2409", True, True) is False


def test_mistral_small_3_both_files_returns_false():
    assert _call_is_mistral_native("Mistral-Small-3-24B", True, True) is False


def test_mistral_nemo_both_files_returns_false():
    assert _call_is_mistral_native("Mistral-Nemo-Instruct-2407", True, True) is False


def test_no_params_json_returns_false():
    assert _call_is_mistral_native("SomeModel", False, True) is False


def test_neither_file_returns_false():
    assert _call_is_mistral_native("EmptyModel", False, False) is False


# [static] pass_to_pass
def test_no_debug_statements():
    """server_args.py has no debug statements (pass_to_pass)."""
    import re
    source = Path(TARGET_FILE).read_text()
    debug_pattern = re.compile(
        r"^\s*(import pdb|from pdb|import ipdb|from ipdb|breakpoint\s*\(|pdb\.set_trace)",
        re.MULTILINE
    )
    matches = debug_pattern.findall(source)
    assert len(matches) == 0, f"Found debug statements: {matches}"


def test_no_trailing_whitespace():
    """server_args.py has no trailing whitespace (pass_to_pass)."""
    source = Path(TARGET_FILE).read_text()
    lines = source.splitlines(keepends=True)
    issues = []
    for i, line in enumerate(lines, 1):
        stripped = line.rstrip("\n\r")
        if stripped != stripped.rstrip():
            issues.append(f"Line {i}")
    assert len(issues) == 0, f"Found trailing whitespace in {len(issues)} lines: {issues[:5]}"


def test_ends_with_newline():
    """server_args.py ends with newline (pass_to_pass)."""
    content = Path(TARGET_FILE).read_bytes()
    assert content.endswith(b"\n"), "File does not end with newline"


# [repo_tests] pass_to_pass
def test_repo_py_compile():
    """Repo's server_args.py compiles with Python (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "python/sglang/srt/server_args.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr[-500:]}"


def test_repo_ast_parse():
    """Repo's server_args.py parses as valid AST (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import ast; ast.parse(open('python/sglang/srt/server_args.py').read()); print('AST OK')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"AST parse failed:\n{r.stderr[-500:]}"


def test_repo_file_exists():
    """Repo's server_args.py file exists (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"import os; exit(0 if os.path.exists('{TARGET_FILE}') else 1)"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"server_args.py does not exist at {TARGET_FILE}"


def test_repo_precommit_check_ast():
    """Repo's server_args.py passes pre-commit check-ast hook (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["pre-commit", "run", "check-ast", "--files", "python/sglang/srt/server_args.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"pre-commit check-ast failed:\n{r.stderr[-500:]}"


def test_repo_precommit_debug_statements():
    """Repo's server_args.py has no debug statements (pre-commit) (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["pre-commit", "run", "debug-statements", "--files", "python/sglang/srt/server_args.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"pre-commit debug-statements failed:\n{r.stderr[-500:]}"


def test_repo_precommit_trailing_whitespace():
    """Repo's server_args.py has no trailing whitespace (pre-commit) (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["pre-commit", "run", "trailing-whitespace", "--files", "python/sglang/srt/server_args.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"pre-commit trailing-whitespace failed:\n{r.stderr[-500:]}"


def test_repo_precommit_end_of_file():
    """Repo's server_args.py ends with newline (pre-commit) (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["pre-commit", "run", "end-of-file-fixer", "--files", "python/sglang/srt/server_args.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"pre-commit end-of-file-fixer failed:\n{r.stderr[-500:]}"


def test_repo_check_yaml():
    """Repo's pre-commit YAML check passes on workflow files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["pre-commit", "run", "check-yaml", "--files", ".github/workflows/lint.yml"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"pre-commit check-yaml failed:\n{r.stderr[-500:]}"


def test_repo_check_toml():
    """Repo's pyproject.toml passes pre-commit TOML check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["pre-commit", "run", "check-toml", "--files", "python/pyproject.toml"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"pre-commit check-toml failed:\n{r.stderr[-500:]}"


def test_repo_unit_test_ast_valid():
    """Repo's unit test file for server_args parses as valid AST (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import ast; ast.parse(open('test/registered/unit/server_args/test_server_args.py').read()); print('AST OK')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit test AST parse failed:\n{r.stderr[-500:]}"


def test_repo_unit_test_py_compile():
    """Repo's unit test file for server_args.py compiles (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "test/registered/unit/server_args/test_server_args.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit test py_compile failed:\n{r.stderr[-500:]}"


def test_repo_ruff_check():
    """Repo's server_args.py passes ruff linter (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", "python/sglang/srt/server_args.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_black_format():
    """Repo's server_args.py passes black format check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["black", "--check", "python/sglang/srt/server_args.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"black format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_isort_check():
    """Repo's server_args.py passes isort import sorting check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["isort", "--check-only", "python/sglang/srt/server_args.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [static] pass_to_pass
def test_not_stub():
    """_is_mistral_native_format has real logic, not just pass/return."""
    source = Path(TARGET_FILE).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_is_mistral_native_format":
            stmts = [
                s
                for s in ast.walk(node)
                if isinstance(s, (ast.If, ast.For, ast.Call, ast.Assign, ast.Return))
            ]
            assert len(stmts) >= 3, "Function body looks like a stub"
            return
    raise AssertionError("_is_mistral_native_format not found")
