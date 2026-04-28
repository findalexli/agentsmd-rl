"""
Task: prime-rl-remove-tp-trainer-config
Repo: PrimeIntellect-ai/prime-rl @ 80a52899ea6a74e0738c15228181ef7b9775dfe9
PR:   2109

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/prime-rl"
BASE = f"{REPO}/src/prime_rl"
TRAINER_CFG = f"{BASE}/configs/trainer.py"
RL_CFG = f"{BASE}/configs/rl.py"
PARALLEL_DIMS = f"{BASE}/trainer/parallel_dims.py"
SFT_TRAIN = f"{BASE}/trainer/sft/train.py"
CHANGELOG = f"{REPO}/CHANGELOG.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse(path: str) -> tuple[str, ast.Module]:
    src = Path(path).read_text()
    return src, ast.parse(src)


def _find_class(tree: ast.Module, name: str) -> ast.ClassDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    raise AssertionError(f"Class {name!r} not found")


def _class_fields(cls: ast.ClassDef) -> set[str]:
    return {
        item.target.id
        for item in cls.body
        if isinstance(item, ast.AnnAssign)
        and isinstance(item.target, ast.Name)
        and not item.target.id.startswith("_")
    }


def _class_methods(cls: ast.ClassDef) -> set[str]:
    return {item.name for item in cls.body if isinstance(item, ast.FunctionDef)}


def _extract_method_body(source: str, cls: ast.ClassDef, method_name: str) -> str:
    """Extract a method's source, stripping decorators."""
    for item in cls.body:
        if isinstance(item, ast.FunctionDef) and item.name == method_name:
            lines = source.splitlines(keepends=True)
            func_src = "".join(lines[item.lineno - 1 : item.end_lineno])
            body_lines = [l for l in func_src.splitlines(keepends=True)
                          if not l.strip().startswith("@")]
            return "".join(body_lines)
    raise AssertionError(f"Method {method_name!r} not found in {cls.name}")


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python code snippet in a subprocess via temp file."""
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

# [static] pass_to_pass
def test_syntax_check():
    """All modified files must parse without errors."""
    for path in [TRAINER_CFG, RL_CFG, PARALLEL_DIMS, SFT_TRAIN]:
        src = Path(path).read_text()
        ast.parse(src)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_py_compile():
    """Repo's modified Python files compile successfully (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "src/prime_rl/configs/trainer.py",
         "src/prime_rl/configs/rl.py", "src/prime_rl/trainer/parallel_dims.py",
         "src/prime_rl/trainer/sft/train.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_parallel_dims_ast():
    """ParallelDims class structure is valid (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import ast; tree = ast.parse(open('src/prime_rl/trainer/parallel_dims.py').read()); " +
         "cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == 'ParallelDims'); " +
         "fields = [item.target.id for item in cls.body if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)]; " +
         "required = ['dp_replicate', 'dp_shard', 'cp', 'pp', 'ep', 'world_size']; " +
         "missing = [f for f in required if f not in fields]; " +
         "assert not missing, f'Missing fields: {missing}'; " +
         "print('OK')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"AST check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_model_config_ast():
    """ModelConfig class retains required fields (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import ast; tree = ast.parse(open('src/prime_rl/configs/trainer.py').read()); " +
         "cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == 'ModelConfig'); " +
         "fields = [item.target.id for item in cls.body if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)]; " +
         "required = ['cp', 'dp_replicate', 'ep']; " +
         "missing = [f for f in required if f not in fields]; " +
         "assert not missing, f'Missing required fields: {missing}'; " +
         "print('OK')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ModelConfig AST check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_changelog_exists():
    """CHANGELOG.md exists and has content (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import os; size = os.path.getsize('CHANGELOG.md'); " +
         "assert size > 1000, f'CHANGELOG.md too small: {size} bytes'; " +
         "print(f'CHANGELOG.md: {size} bytes')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"CHANGELOG check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_no_stubbed_files():
    """Key modified files are not stubbed/hollowed out (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import os; files = ['src/prime_rl/trainer/parallel_dims.py', 'src/prime_rl/configs/trainer.py']; " +
         "sizes = {f: os.path.getsize(f) for f in files}; " +
         "assert sizes['src/prime_rl/trainer/parallel_dims.py'] > 5000, 'parallel_dims.py too small'; " +
         "assert sizes['src/prime_rl/configs/trainer.py'] > 15000, 'trainer.py too small'; " +
         "print('OK:', sizes)"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"File size check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff linter passes on modified files (pass_to_pass)."""
    # First install ruff and tomli (needed for ruff config)
    r = subprocess.run(
        ["pip", "install", "ruff", "tomli", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"
    # Then run ruff check
    r = subprocess.run(
        ["python3", "-m", "ruff", "check",
         "src/prime_rl/configs/trainer.py",
         "src/prime_rl/configs/rl.py",
         "src/prime_rl/trainer/parallel_dims.py",
         "src/prime_rl/trainer/sft/train.py",
         "--config=pyproject.toml"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_toml_configs_valid():
    """All TOML config files parse without errors (pass_to_pass)."""
    toml_script = '''
import tomli
import os
import sys

errors = []
for root, dirs, files in os.walk("configs"):
    for f in files:
        if f.endswith(".toml"):
            p = os.path.join(root, f)
            try:
                with open(p, "rb") as fp:
                    tomli.load(fp)
            except Exception as e:
                errors.append(f"{p}: {e}")

print(f"Checked TOML files, errors: {len(errors)}")
for e in errors[:3]:
    print(e)
if errors:
    sys.exit(1)
'''
    r = subprocess.run(
        ["python3", "-c", toml_script],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"TOML validation failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_parallel_dims_imports():
    """ParallelDims module has valid Python imports (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import ast; tree = ast.parse(open('src/prime_rl/trainer/parallel_dims.py').read()); " +
         "imports = [(n.module, [a.name for a in n.names]) for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module]; " +
         "print(f'Found {len(imports)} import statements'); print('OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Import check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "ruff", "format", "--check",
         "src/prime_rl/configs/trainer.py",
         "src/prime_rl/configs/rl.py",
         "src/prime_rl/trainer/parallel_dims.py",
         "src/prime_rl/trainer/sft/train.py",
         "--config=pyproject.toml"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_trainer_config_no_syntax_errors():
    """Trainer config has valid Python syntax and imports (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import ast; tree = ast.parse(open('src/prime_rl/configs/trainer.py').read()); " +
         "classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]; " +
         "assert 'ModelConfig' in classes, 'ModelConfig not found'; " +
         "assert 'TrainerConfig' in classes, 'TrainerConfig not found'; " +
         "print('OK: Found', len(classes), 'classes')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Trainer config check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_rl_config_valid():
    """RL config module has valid structure (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import ast; tree = ast.parse(open('src/prime_rl/configs/rl.py').read()); " +
         "funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]; " +
         "assert 'auto_setup_deployment' in funcs, 'auto_setup_deployment not found'; " +
         "print('OK: Found', len(funcs), 'functions')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"RL config check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_sft_train_valid():
    """SFT train module has valid structure (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import ast; tree = ast.parse(open('src/prime_rl/trainer/sft/train.py').read()); " +
         "funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]; " +
         "assert 'train' in funcs, 'train function not found'; " +
         "print('OK: Found', len(funcs), 'functions')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"SFT train check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_configs_dir_readable():
    """Configs directory exists and contains TOML files (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import os; files = list(os.walk('configs')); " +
         "toml_count = sum([len([f for f in filenames if f.endswith('.toml')]) for _, _, filenames in files]); " +
         "assert toml_count > 0, 'No TOML files found in configs'; " +
         "print(f'OK: Found {toml_count} TOML config files')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Configs dir check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_non_data_parallel_size_excludes_tp():
    """non_data_parallel_size must return cp*pp, not cp*tp*pp.

    Extracts the property via AST then runs it in a subprocess with mock
    objects whose tp is set high — any leaked tp reference produces wrong results.
    """
    src, tree = _parse(PARALLEL_DIMS)
    cls = _find_class(tree, "ParallelDims")
    func_src = textwrap.dedent(_extract_method_body(src, cls, "non_data_parallel_size"))

    test_code = (
        func_src +
        "\n"
        "for cp, pp, tp in [(4, 2, 8), (1, 1, 16), (2, 4, 4), (3, 3, 7)]:\n"
        "    mock = type('M', (), {'cp': cp, 'pp': pp, 'tp': tp})()\n"
        "    result = non_data_parallel_size(mock)\n"
        "    expected = cp * pp\n"
        "    assert result == expected, 'Got %d, expected %d' % (result, expected)\n"
        "print('PASS')\n"
    )

    r = _run_python(test_code)
    assert r.returncode == 0, f"non_data_parallel_size failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_seq_len_divisor_excludes_tp():
    """seq_len_divisor must return cp*2, not tp*cp*2.

    Extracts the property via AST then runs it in a subprocess with mock
    objects whose tp is set high — any leaked tp reference produces wrong results.
    """
    src, tree = _parse(PARALLEL_DIMS)
    cls = _find_class(tree, "ParallelDims")
    func_src = textwrap.dedent(_extract_method_body(src, cls, "seq_len_divisor"))

    test_code = (
        func_src +
        "\n"
        "for cp, tp in [(4, 8), (1, 16), (3, 5), (6, 3)]:\n"
        "    mock = type('M', (), {'cp': cp, 'tp': tp})()\n"
        "    result = seq_len_divisor(mock)\n"
        "    expected = cp * 2\n"
        "    assert result == expected, 'Got %d, expected %d' % (result, expected)\n"
        "print('PASS')\n"
    )

    r = _run_python(test_code)
    assert r.returncode == 0, f"seq_len_divisor failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_model_config_no_tp_field():
    """ModelConfig must not have a tp field — it should be fully removed."""
    _, tree = _parse(TRAINER_CFG)
    cls = _find_class(tree, "ModelConfig")
    fields = _class_fields(cls)
    assert "tp" not in fields, f"ModelConfig still has tp (fields: {fields})"


# [pr_diff] fail_to_pass
def test_parallel_dims_no_tp():
    """ParallelDims must have no tp field and no tp_enabled property."""
    _, tree = _parse(PARALLEL_DIMS)
    cls = _find_class(tree, "ParallelDims")
    assert "tp" not in _class_fields(cls), "ParallelDims still has tp field"
    assert "tp_enabled" not in _class_methods(cls), "ParallelDims still has tp_enabled"


# [pr_diff] fail_to_pass
def test_sft_train_no_tp_multiplication():
    """SFT train.py must not reference model.tp in computations."""
    src, tree = _parse(SFT_TRAIN)
    tp_refs = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Attribute) and node.attr == "tp"
                and isinstance(node.value, ast.Attribute)
                and node.value.attr == "model"):
            segment = ast.get_source_segment(src, node) or f"line {node.lineno}"
            tp_refs.append(segment)
    assert not tp_refs, f"sft/train.py still references model.tp: {tp_refs}"


# [pr_diff] fail_to_pass
def test_rl_deployment_no_tp():
    """auto_setup_deployment must not reference model.tp."""
    src, tree = _parse(RL_CFG)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "auto_setup_deployment":
            for n in ast.walk(node):
                if (isinstance(n, ast.Attribute) and n.attr == "tp"
                        and isinstance(n.value, ast.Attribute)
                        and n.value.attr == "model"):
                    raise AssertionError("auto_setup_deployment still references .model.tp")
            return
    raise AssertionError("auto_setup_deployment function not found")


# [pr_diff] fail_to_pass
def test_changelog_documents_tp_removal():
    """CHANGELOG.md must document the removal of the tp config field."""
    changelog = Path(CHANGELOG).read_text()
    lower = changelog.lower()
    has_documentation = any(
        "model.tp" in line.lower() and "removed" in line.lower()
        for line in changelog.splitlines()
    )
    assert has_documentation, "CHANGELOG.md does not document the removal of model.tp"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_parallel_dims_core_fields():
    """ParallelDims must retain dp_replicate, dp_shard, cp, pp, ep, world_size."""
    _, tree = _parse(PARALLEL_DIMS)
    cls = _find_class(tree, "ParallelDims")
    fields = _class_fields(cls)
    required = {"dp_replicate", "dp_shard", "cp", "pp", "ep", "world_size"}
    missing = required - fields
    assert not missing, f"ParallelDims missing fields: {missing}"


# [pr_diff] pass_to_pass
def test_parallel_dims_methods_intact():
    """Key properties/methods must still exist on ParallelDims."""
    _, tree = _parse(PARALLEL_DIMS)
    cls = _find_class(tree, "ParallelDims")
    methods = _class_methods(cls)
    required = {
        "dp_enabled", "cp_enabled", "pp_enabled", "ep_enabled",
        "non_data_parallel_size", "seq_len_divisor", "build_mesh",
    }
    missing = required - methods
    assert not missing, f"ParallelDims missing methods: {missing}"


# [static] pass_to_pass
def test_model_config_retains_fields():
    """ModelConfig must still have cp, dp_replicate, ep and >=5 fields."""
    _, tree = _parse(TRAINER_CFG)
    cls = _find_class(tree, "ModelConfig")
    fields = _class_fields(cls)
    for req in ("cp", "dp_replicate", "ep"):
        assert req in fields, f"ModelConfig missing required field {req}"
    assert len(fields) >= 5, f"ModelConfig has only {len(fields)} fields (stubbed?)"


# [static] pass_to_pass
def test_parallel_dims_not_stubbed():
    """parallel_dims.py must not be hollowed out."""
    src, tree = _parse(PARALLEL_DIMS)
    cls = _find_class(tree, "ParallelDims")
    method_count = sum(1 for item in cls.body if isinstance(item, ast.FunctionDef))
    assert method_count >= 8, f"ParallelDims has only {method_count} methods (stubbed?)"
    non_blank = [l for l in src.splitlines() if l.strip() and not l.strip().startswith("#")]
    assert len(non_blank) >= 80, f"parallel_dims.py only {len(non_blank)} substantive lines"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:5 @ 80a52899ea6a74e0738c15228181ef7b9775dfe9
def test_no_excessive_try_except():
    """Changed files must not introduce unnecessary try/except blocks (AGENTS.md:5)."""
    for path in [PARALLEL_DIMS, TRAINER_CFG]:
        _, tree = _parse(path)
        try_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Try))
        assert try_count <= 2, (
            f"{Path(path).name} has {try_count} try/except blocks (excessive)"
        )
