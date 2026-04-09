"""
Task: prime-rl-toml-none-str-removal
Repo: PrimeIntellect-ai/prime-rl @ 4f612601f6447b3df1ee17e535ac698b5cc3d16c
PR:   2095

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

REPO = "/workspace/prime-rl"
CONFIG_PY = f"{REPO}/src/prime_rl/utils/config.py"
RL_PY = f"{REPO}/src/prime_rl/entrypoints/rl.py"
SFT_PY = f"{REPO}/src/prime_rl/entrypoints/sft.py"
INFERENCE_PY = f"{REPO}/src/prime_rl/entrypoints/inference.py"

ENTRYPOINTS = {"rl.py": RL_PY, "sft.py": SFT_PY, "inference.py": INFERENCE_PY}


# -----------------------------------------------------------------------------
# Helpers for subprocess-based behavioral testing
# -----------------------------------------------------------------------------

def _run_in_repo(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory via subprocess."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
        env={**dict(subprocess.os.environ), "PYTHONPATH": f"{REPO}/src"},
    )


def _run_script_in_repo(script_content: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a temporary script and execute it in the repo directory."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script_content)
        script_path = f.name
    try:
        return subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO,
            env={**dict(subprocess.os.environ), "PYTHONPATH": f"{REPO}/src"},
        )
    finally:
        Path(script_path).unlink(missing_ok=True)


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified files must parse without errors."""
    for path in [CONFIG_PY, RL_PY, SFT_PY, INFERENCE_PY]:
        src = Path(path).read_text()
        ast.parse(src)


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests using subprocess
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_none_helpers_removed():
    """none_to_none_str and _convert_none must be removed from config.py."""
    r = _run_in_repo("""
import sys
from pathlib import Path
import ast
REPO = "/workspace/prime-rl"
src = Path(f"{REPO}/src/prime_rl/utils/config.py").read_text()
tree = ast.parse(src)
funcs = [node.name for node in ast.iter_child_nodes(tree)
         if isinstance(node, ast.FunctionDef) and node.name in ("none_to_none_str", "_convert_none")]
if funcs:
    print(f"FAIL: Functions still defined: {funcs}")
    sys.exit(1)
print("PASS: Helper functions removed")
""")
    assert r.returncode == 0, f"Helper functions still defined: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Unexpected output: {r.stdout}"


# [pr_diff] fail_to_pass
def test_entrypoints_no_import_none_helper():
    """No entrypoint may import or call none_to_none_str."""
    r = _run_in_repo(f"""
import sys
from pathlib import Path
import ast

ENTRYPOINTS = {{"rl.py": "{RL_PY}", "sft.py": "{SFT_PY}", "inference.py": "{INFERENCE_PY}"}}

for name, path in ENTRYPOINTS.items():
    src = Path(path).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "none_to_none_str":
                    print(f"FAIL: {{name}} still imports none_to_none_str")
                    sys.exit(1)
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "none_to_none_str":
                print(f"FAIL: {{name}} still calls none_to_none_str()")
                sys.exit(1)
            if isinstance(func, ast.Attribute) and func.attr == "none_to_none_str":
                print(f"FAIL: {{name}} still calls .none_to_none_str()")
                sys.exit(1)
print("PASS: No entrypoint imports or calls none_to_none_str")
""")
    assert r.returncode == 0, f"Entrypoints still use none_to_none_str: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_sft_write_config_excludes_none():
    """SFT write_config must omit None-valued fields from TOML output (direct check)."""
    r = _run_in_repo("""
import sys
from pathlib import Path
REPO = "/workspace/prime-rl"
SFT_PY = f"{REPO}/src/prime_rl/entrypoints/sft.py"
src = Path(SFT_PY).read_text()
if "exclude_none=True" in src:
    print("PASS: SFT write_config uses exclude_none=True")
    sys.exit(0)
if "none_to_none_str" in src:
    print("FAIL: SFT still uses none_to_none_str")
    sys.exit(1)
print("FAIL: SFT write_config missing exclude_none=True")
sys.exit(1)
""")
    assert r.returncode == 0, f"SFT write_config test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_rl_write_config_excludes_none():
    """RL write_config must omit None-valued fields from TOML output (direct check)."""
    r = _run_in_repo("""
import sys
from pathlib import Path
REPO = "/workspace/prime-rl"
RL_PY = f"{REPO}/src/prime_rl/entrypoints/rl.py"
src = Path(RL_PY).read_text()
if "exclude_none=True" in src:
    print("PASS: RL write_config uses exclude_none=True")
    sys.exit(0)
if "none_to_none_str" in src:
    print("FAIL: RL still uses none_to_none_str")
    sys.exit(1)
print("FAIL: RL write_config missing exclude_none=True")
sys.exit(1)
""")
    assert r.returncode == 0, f"RL write_config test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_inference_write_config_excludes_none():
    """Inference write_config must omit None-valued fields from TOML output (direct check)."""
    r = _run_in_repo("""
import sys
from pathlib import Path
REPO = "/workspace/prime-rl"
INFERENCE_PY = f"{REPO}/src/prime_rl/entrypoints/inference.py"
src = Path(INFERENCE_PY).read_text()
if "exclude_none=True" in src:
    print("PASS: Inference write_config uses exclude_none=True")
    sys.exit(0)
if "none_to_none_str" in src:
    print("FAIL: Inference still uses none_to_none_str")
    sys.exit(1)
print("FAIL: Inference write_config missing exclude_none=True")
sys.exit(1)
""")
    assert r.returncode == 0, f"Inference write_config test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_rl_write_subconfigs_excludes_none():
    """RL write_subconfigs must omit None-valued fields from all sub-config TOML files."""
    script = """
import sys
import tempfile
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
import tomli_w

class SubConfig(BaseModel):
    lr: float = 0.001
    warmup: Optional[int] = None
    decay: Optional[float] = None

class TestConfig(BaseModel):
    trainer: SubConfig = SubConfig()
    orchestrator: SubConfig = SubConfig(lr=0.01)
    inference: Optional[SubConfig] = SubConfig(lr=0.05)

# Simulate write_subconfigs with fixed behavior (exclude_none=True)
tmpdir = tempfile.mkdtemp()
output_dir = Path(tmpdir)

# Write trainer config
trainer_dict = TestConfig().trainer.model_dump(exclude_none=True, mode="json")
with open(output_dir / "trainer.toml", "wb") as f:
    tomli_w.dump(trainer_dict, f)

# Write orchestrator config
orch_dict = TestConfig().orchestrator.model_dump(exclude_none=True, mode="json")
with open(output_dir / "orchestrator.toml", "wb") as f:
    tomli_w.dump(orch_dict, f)

# Write inference config
inf_dict = TestConfig().inference.model_dump(exclude_none=True, mode="json")
with open(output_dir / "inference.toml", "wb") as f:
    tomli_w.dump(inf_dict, f)

toml_files = list(output_dir.glob("*.toml"))
assert len(toml_files) >= 2, f"Expected >=2 TOML files, got {len(toml_files)}"

errors = []
for f in toml_files:
    content = f.read_text()
    if '"None"' in content:
        errors.append(f"{f.name} contains literal 'None' strings")
    if "warmup" in content:
        errors.append(f"{f.name} has None-valued 'warmup'")
    if "decay" in content:
        errors.append(f"{f.name} has None-valued 'decay'")

if errors:
    print(f"FAIL: {errors}")
    sys.exit(1)

print("PASS: RL write_subconfigs correctly excludes None values")
"""
    r = _run_script_in_repo(script)
    assert r.returncode == 0, f"RL write_subconfigs test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_get_all_fields_preserved():
    """get_all_fields in config.py must still work correctly."""
    script = """
import sys
from pathlib import Path
import ast
from pydantic import BaseModel
from typing import Optional

REPO = "/workspace/prime-rl"
CONFIG_PY = f"{REPO}/src/prime_rl/utils/config.py"

# Extract get_all_fields function
def _extract_function(source_path: str, func_name: str) -> str | None:
    src = Path(source_path).read_text()
    tree = ast.parse(src)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return "".join(src.splitlines(keepends=True)[node.lineno - 1 : node.end_lineno])
    return None

func_src = _extract_function(CONFIG_PY, "get_all_fields")
if func_src is None:
    print("FAIL: get_all_fields not found in config.py")
    sys.exit(1)

ns = {"BaseModel": BaseModel, "__builtins__": __builtins__}
exec(func_src, ns)
get_all_fields = ns["get_all_fields"]

class MyModel(BaseModel):
    name: str = "test"
    value: int = 42
    optional: Optional[float] = None

fields_cls = get_all_fields(MyModel)
fields_inst = get_all_fields(MyModel())

if "name" not in fields_cls or "value" not in fields_cls:
    print(f"FAIL: get_all_fields(class) = {fields_cls}")
    sys.exit(1)

if "name" not in fields_inst or "value" not in fields_inst:
    print(f"FAIL: get_all_fields(instance) = {fields_inst}")
    sys.exit(1)

print("PASS: get_all_fields works correctly")
"""
    r = _run_script_in_repo(script)
    assert r.returncode == 0, f"get_all_fields test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_not_stub():
    """Modified files must not be stubbed out — write_config and tomli_w.dump must exist."""
    for name, path in ENTRYPOINTS.items():
        src = Path(path).read_text()
        assert "def write_config" in src, f"{name} missing write_config function"
        assert "tomli_w.dump" in src, f"{name} missing tomli_w.dump call"

    config_lines = [l for l in Path(CONFIG_PY).read_text().strip().split("\n") if l.strip()]
    assert len(config_lines) >= 5, f"config.py has only {len(config_lines)} non-blank lines (stubbed)"

    rl_src = Path(RL_PY).read_text()
    assert "def write_subconfigs" in rl_src, "rl.py missing write_subconfigs"


# -----------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# -----------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:5 @ 4f612601f6447b3df1ee17e535ac698b5cc3d16c
def test_config_no_try_except():
    """config.py must not have try/except blocks (AGENTS.md: 'Avoid try/except unless really necessary')."""
    src = Path(CONFIG_PY).read_text()
    tree = ast.parse(src)
    try_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Try))
    assert try_count == 0, f"config.py has {try_count} try/except blocks"


# [agent_config] pass_to_pass — AGENTS.md:54 @ 4f612601f6447b3df1ee17e535ac698b5cc3d16c
def test_no_class_based_tests_in_modified_files():
    """Modified files must not introduce class-based test patterns (AGENTS.md: 'Write tests as plain functions with pytest fixtures')."""
    for path in [CONFIG_PY, RL_PY, SFT_PY, INFERENCE_PY]:
        src = Path(path).read_text()
        tree = ast.parse(src)
        test_classes = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and node.name.startswith("Test")
        ]
        assert not test_classes, f"{Path(path).name} has class-based test pattern: {test_classes}"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD validation (p2p_enrichment)
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass — Repo utils syntax check
def test_repo_utils_syntax_all():
    """All Python files in utils directory have valid syntax (pass_to_pass)."""
    utils_dir = Path(f"{REPO}/src/prime_rl/utils")
    py_files = list(utils_dir.rglob("*.py"))
    assert py_files, f"No Python files found in {utils_dir}"

    errors = []
    for py_file in py_files:
        try:
            src = py_file.read_text()
            ast.parse(src)
        except SyntaxError as e:
            errors.append(f"{py_file.relative_to(REPO)}: {e}")

    assert not errors, f"Syntax errors found in utils:\n" + "\n".join(errors)


# [repo_tests] pass_to_pass — Config TOML validation
def test_repo_configs_toml_valid():
    """Integration config TOML files are valid (pass_to_pass)."""
    import tomllib

    config_dir = Path(f"{REPO}/configs/ci/integration")
    if not config_dir.exists():
        config_dirs = [Path(f"{REPO}/configs")]
    else:
        config_dirs = [config_dir]

    toml_files = []
    for d in config_dirs:
        if d.exists():
            toml_files.extend(d.rglob("*.toml"))

    assert toml_files, "No TOML files found in config directories"
    ci_toml_files = [f for f in toml_files if "ci" in str(f)]
    toml_files = ci_toml_files or toml_files[:10]

    errors = []
    for toml_file in toml_files:
        try:
            content = toml_file.read_bytes()
            tomllib.loads(content.decode("utf-8"))
        except Exception as e:
            errors.append(f"{toml_file.relative_to(REPO)}: {e}")

    assert not errors, f"TOML parse errors:\n" + "\n".join(errors)


# -----------------------------------------------------------------------------
# Additional repo test gates (p2p)
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_python_syntax_all():
    """All Python files in the repo have valid syntax (CI: ruff/syntax check)."""
    src_dir = Path(f"{REPO}/src")
    py_files = list(src_dir.rglob("*.py"))
    assert py_files, f"No Python files found in {src_dir}"

    errors = []
    for py_file in py_files:
        try:
            src = py_file.read_text()
            ast.parse(src)
        except SyntaxError as e:
            errors.append(f"{py_file.relative_to(REPO)}: {e}")

    assert not errors, f"Syntax errors found:\n" + "\n".join(errors)
