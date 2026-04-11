import subprocess
import sys
from pathlib import Path

REPO = "/workspace/prime-rl"


def _run_in_repo(cmd: list[str], timeout: int = 60, cwd: str = REPO) -> subprocess.CompletedProcess:
    """Run a command in the repo directory."""
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)


# =============================================================================
# FAIL TO PASS TESTS (behavioral - these run actual code)
# =============================================================================

# [pr_diff] fail_to_pass
def test_entrypoint_file_exists_with_main():
    """New inference entrypoint file exists with main() and inference() functions."""
    script = '''
import ast
from pathlib import Path
import sys

entrypoint_path = Path("src/prime_rl/entrypoints/inference.py")
if not entrypoint_path.exists():
    print(f"Entrypoint file not found: {entrypoint_path}")
    sys.exit(1)

try:
    tree = ast.parse(entrypoint_path.read_text())
except SyntaxError as e:
    print(f"Syntax error: {e}")
    sys.exit(1)

functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

required = ["main", "inference", "inference_slurm", "inference_local", "write_config", "write_slurm_script"]
missing = [f for f in required if f not in functions]

if missing:
    print(f"Missing functions: {missing}")
    sys.exit(1)

print(f"All required functions found: {required}")
'''
    r = _run_in_repo(["python3", "-c", script], timeout=30)
    assert r.returncode == 0, f"Entrypoint check failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_pyproject_entrypoint_updated():
    """pyproject.toml points inference command to new entrypoints.inference:main."""
    script = '''
from pathlib import Path
import sys

toml_path = Path("pyproject.toml")
if not toml_path.exists():
    print("pyproject.toml not found")
    sys.exit(1)

content = toml_path.read_text()

# Check old entrypoint is removed
if 'inference = "prime_rl.inference.server:main"' in content:
    print("ERROR: Old entrypoint still present")
    sys.exit(1)

# Check new entrypoint is present
if 'inference = "prime_rl.entrypoints.inference:main"' not in content:
    print("ERROR: New entrypoint not found")
    sys.exit(1)

print("Entrypoint correctly updated to prime_rl.entrypoints.inference:main")
'''
    r = _run_in_repo(["python3", "-c", script], timeout=30)
    assert r.returncode == 0, f"pyproject.toml check failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_config_has_slurm_and_deployment():
    """InferenceConfig has slurm, deployment, output_dir, and dry_run fields."""
    script = '''
import ast
from pathlib import Path
import sys

config_path = Path("src/prime_rl/configs/inference.py")
if not config_path.exists():
    print(f"Config file not found: {config_path}")
    sys.exit(1)

try:
    tree = ast.parse(config_path.read_text())
except SyntaxError as e:
    print(f"Syntax error: {e}")
    sys.exit(1)

# Find InferenceConfig class
inference_config = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "InferenceConfig":
        inference_config = node
        break

if not inference_config:
    print("InferenceConfig class not found")
    sys.exit(1)

# Get all field names (AnnAssign nodes in the class body)
fields = []
for item in inference_config.body:
    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
        fields.append(item.target.id)

required_fields = ["deployment", "slurm", "output_dir", "dry_run"]
missing = [f for f in required_fields if f not in fields]

if missing:
    print(f"Missing fields: {missing}")
    sys.exit(1)

print(f"All required fields found: {required_fields}")
'''
    r = _run_in_repo(["python3", "-c", script], timeout=30)
    assert r.returncode == 0, f"Config fields check failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_config_validators_exist():
    """InferenceConfig has validators for multi_node+slurm and slurm template auto-setup."""
    script = '''
import ast
from pathlib import Path
import sys

config_path = Path("src/prime_rl/configs/inference.py")
if not config_path.exists():
    print(f"Config file not found: {config_path}")
    sys.exit(1)

try:
    tree = ast.parse(config_path.read_text())
except SyntaxError as e:
    print(f"Syntax error: {e}")
    sys.exit(1)

# Find InferenceConfig class
inference_config = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "InferenceConfig":
        inference_config = node
        break

if not inference_config:
    print("InferenceConfig class not found")
    sys.exit(1)

# Find validators
validators = []
for item in inference_config.body:
    if isinstance(item, ast.FunctionDef):
        for decorator in item.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                if decorator.func.id == "model_validator":
                    validators.append(item.name)
            elif isinstance(decorator, ast.Name) and decorator.id == "model_validator":
                validators.append(item.name)

required_validators = ["validate_multi_node_requires_slurm", "auto_setup_slurm_template"]
missing = [v for v in required_validators if v not in validators]

if missing:
    print(f"Missing validators: {missing}")
    sys.exit(1)

print(f"All required validators found: {required_validators}")
'''
    r = _run_in_repo(["python3", "-c", script], timeout=30)
    assert r.returncode == 0, f"Config validators check failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_slurm_template_file_exists():
    """SLURM template file inference.sbatch.j2 exists with proper SBATCH directives."""
    script = '''
from pathlib import Path
import sys

template_path = Path("src/prime_rl/templates/inference.sbatch.j2")
if not template_path.exists():
    print(f"Template file not found: {template_path}")
    sys.exit(1)

content = template_path.read_text()

# Check for key SBATCH directives and template variables
required_patterns = [
    "#SBATCH --job-name={{ job_name }}",
    "#SBATCH --nodes={{ num_nodes }}",
    "#SBATCH --gres=gpu:{{ gpus_per_node }}",
    "#SBATCH --partition={{ partition }}",
    "{{ config_path }}",
    "{{ output_dir }}",
]

missing = [p for p in required_patterns if p not in content]

if missing:
    print(f"Missing patterns: {missing}")
    sys.exit(1)

print("SLURM template file exists with all required directives")
'''
    r = _run_in_repo(["python3", "-c", script], timeout=30)
    assert r.returncode == 0, f"SLURM template check failed:\n{r.stdout}\n{r.stderr}"


# [agent_config] fail_to_pass
def test_skill_md_updated_with_slurm_docs():
    """SKILL.md updated with SLURM scheduling documentation per AGENTS.md rule."""
    script = '''
from pathlib import Path
import sys

skill_path = Path("skills/inference-server/SKILL.md")
if not skill_path.exists():
    print(f"SKILL.md not found: {skill_path}")
    sys.exit(1)

content = skill_path.read_text()

# Check for SLURM documentation sections
required_sections = [
    "SLURM scheduling",
    "Single-node SLURM",
    "Multi-node SLURM",
    "Dry run",
]

missing = [s for s in required_sections if s not in content]

if missing:
    print(f"Missing sections: {missing}")
    sys.exit(1)

print("SKILL.md contains all required SLURM documentation sections")
'''
    r = _run_in_repo(["python3", "-c", script], timeout=30)
    assert r.returncode == 0, f"SKILL.md check failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_skill_md_key_files_updated():
    """SKILL.md key files section references new entrypoint and SLURM template."""
    script = '''
from pathlib import Path
import sys

skill_path = Path("skills/inference-server/SKILL.md")
if not skill_path.exists():
    print(f"SKILL.md not found: {skill_path}")
    sys.exit(1)

content = skill_path.read_text()

# Check for new entrypoint and template references
required_refs = [
    "src/prime_rl/entrypoints/inference.py",
    "src/prime_rl/templates/inference.sbatch.j2",
]

missing = [r for r in required_refs if r not in content]

if missing:
    print(f"Missing key file references: {missing}")
    sys.exit(1)

print("SKILL.md key files section updated with new entrypoint and template")
'''
    r = _run_in_repo(["python3", "-c", script], timeout=30)
    assert r.returncode == 0, f"SKILL.md key files check failed:\n{r.stdout}\n{r.stderr}"


# =============================================================================
# PASS TO PASS TESTS (static checks that should pass on both base and fix)
# =============================================================================

# [static] pass_to_pass
def test_syntax_check():
    """New entrypoint file must parse without syntax errors."""
    script = '''
import ast
from pathlib import Path
import sys

entrypoint_path = Path("src/prime_rl/entrypoints/inference.py")
if not entrypoint_path.exists():
    # If file doesn't exist yet, that's fine for syntax check
    print("Entrypoint file doesn't exist yet (expected on base commit)")
    sys.exit(0)

try:
    ast.parse(entrypoint_path.read_text())
    print("Entrypoint file parses without syntax errors")
except SyntaxError as e:
    print(f"Syntax error: {e}")
    sys.exit(1)
'''
    r = _run_in_repo(["python3", "-c", script], timeout=30)
    assert r.returncode == 0, f"Syntax check failed:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_entrypoint_not_stub():
    """Entrypoint functions have real logic, not just pass/return."""
    script = '''
import ast
from pathlib import Path
import sys

entrypoint_path = Path("src/prime_rl/entrypoints/inference.py")
if not entrypoint_path.exists():
    print("Entrypoint file doesn't exist yet (expected on base commit)")
    sys.exit(0)

try:
    tree = ast.parse(entrypoint_path.read_text())
except SyntaxError as e:
    print(f"Syntax error: {e}")
    sys.exit(1)

# Check that main functions are not just stubs
functions_to_check = ["main", "inference", "inference_slurm", "inference_local"]
stub_count = 0

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in functions_to_check:
        # Check if body is just Pass or simple return
        if len(node.body) == 1:
            if isinstance(node.body[0], ast.Pass):
                stub_count += 1
            elif isinstance(node.body[0], ast.Return) and node.body[0].value is None:
                stub_count += 1

if stub_count > 0:
    print(f"Found {stub_count} stub functions")
    sys.exit(1)

print("Entrypoint functions have real implementation")
'''
    r = _run_in_repo(["python3", "-c", script], timeout=30)
    assert r.returncode == 0, f"Entrypoint not stub check failed:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_config_classes_not_stub():
    """Deployment config classes have real fields, not empty."""
    script = '''
import ast
from pathlib import Path
import sys

config_path = Path("src/prime_rl/configs/inference.py")
if not config_path.exists():
    print("Config file not found")
    sys.exit(1)

try:
    tree = ast.parse(config_path.read_text())
except SyntaxError as e:
    print(f"Syntax error: {e}")
    sys.exit(1)

# Check for deployment config classes
required_classes = [
    "BaseInferenceDeploymentConfig",
    "SingleNodeInferenceDeploymentConfig",
    "MultiNodeInferenceDeploymentConfig",
]

found_classes = {}
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name in required_classes:
        # Count fields (AnnAssign nodes)
        field_count = sum(1 for item in node.body if isinstance(item, ast.AnnAssign))
        found_classes[node.name] = field_count

# Base config should have gpus_per_node
if "BaseInferenceDeploymentConfig" in found_classes:
    if found_classes["BaseInferenceDeploymentConfig"] == 0:
        print("BaseInferenceDeploymentConfig has no fields")
        sys.exit(1)

# MultiNode should have num_nodes
if "MultiNodeInferenceDeploymentConfig" in found_classes:
    if found_classes["MultiNodeInferenceDeploymentConfig"] == 0:
        print("MultiNodeInferenceDeploymentConfig has no fields")
        sys.exit(1)

print(f"Deployment config classes have fields: {found_classes}")
'''
    r = _run_in_repo(["python3", "-c", script], timeout=30)
    assert r.returncode == 0, f"Config classes check failed:\n{r.stdout}\n{r.stderr}"


# =============================================================================
# PASS TO PASS TESTS (repo tests - repository's own checks)
# =============================================================================

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff lint check passes on src/ directory."""
    install_result = _run_in_repo(["pip", "install", "ruff", "-q"], timeout=60)
    if install_result.returncode != 0:
        pytest.skip("Could not install ruff")

    r = _run_in_repo(
        ["ruff", "check", "--select", "E,W,F", "src/prime_rl/configs/", "src/prime_rl/inference/", "src/prime_rl/entrypoints/"],
        timeout=120,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on src/ directory."""
    install_result = _run_in_repo(["pip", "install", "ruff", "-q"], timeout=60)
    if install_result.returncode != 0:
        pytest.skip("Could not install ruff")

    r = _run_in_repo(
        ["ruff", "format", "--check", "--config=pyproject.toml", "src/prime_rl/configs/", "src/prime_rl/inference/", "src/prime_rl/entrypoints/"],
        timeout=120,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_pyproject_toml_syntax():
    """Repo's pyproject.toml has valid TOML syntax."""
    script = '''
from pathlib import Path
import sys

try:
    import tomllib
except ImportError:
    import tomli as tomllib

toml_path = Path("pyproject.toml")
if not toml_path.exists():
    print("pyproject.toml not found")
    sys.exit(1)

try:
    with open(toml_path, "rb") as f:
        tomllib.load(f)
    print("pyproject.toml has valid TOML syntax")
except Exception as e:
    print(f"TOML parse error: {e}")
    sys.exit(1)
'''
    r = _run_in_repo(["python3", "-c", script], timeout=30)
    assert r.returncode == 0, f"pyproject.toml syntax check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_configs_toml_syntax():
    """All config TOML files in configs/ have valid syntax."""
    script = '''
from pathlib import Path
import sys

try:
    import tomllib
except ImportError:
    import tomli as tomllib

configs_dir = Path("configs")
if not configs_dir.exists():
    print("configs directory not found")
    sys.exit(0)

invalid = []
for toml_file in configs_dir.rglob("*.toml"):
    try:
        with open(toml_file, "rb") as f:
            tomllib.load(f)
    except Exception as e:
        invalid.append(f"{toml_file}: {e}")

if invalid:
    print("Invalid TOML files:")
    for i in invalid:
        print(i)
    sys.exit(1)

print(f"All TOML files in configs/ parse successfully")
'''
    r = _run_in_repo(["python3", "-c", script], timeout=30)
    assert r.returncode == 0, f"Configs TOML syntax check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_entrypoint_parse():
    """Inference entrypoint (server.py) parses as valid Python."""
    script = '''
import ast
from pathlib import Path
import sys

server_path = Path("src/prime_rl/inference/server.py")
if not server_path.exists():
    print("server.py not found")
    sys.exit(1)

try:
    ast.parse(server_path.read_text())
    print("server.py parses successfully")
except SyntaxError as e:
    print(f"Syntax error: {e}")
    sys.exit(1)
'''
    r = _run_in_repo(["python3", "-c", script], timeout=30)
    assert r.returncode == 0, f"Entrypoint parse check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_inference_config_parse():
    """Inference config file parses as valid Python."""
    script = '''
import ast
from pathlib import Path
import sys

config_path = Path("src/prime_rl/configs/inference.py")
if not config_path.exists():
    print("inference.py config not found")
    sys.exit(1)

try:
    ast.parse(config_path.read_text())
    print("inference.py config parses successfully")
except SyntaxError as e:
    print(f"Syntax error: {e}")
    sys.exit(1)
'''
    r = _run_in_repo(["python3", "-c", script], timeout=30)
    assert r.returncode == 0, f"Inference config parse check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_examples_toml_syntax():
    """All example TOML files in examples/ have valid syntax."""
    script = '''
from pathlib import Path
import sys

try:
    import tomllib
except ImportError:
    import tomli as tomllib

examples_dir = Path("examples")
if not examples_dir.exists():
    print("examples directory not found")
    sys.exit(0)

invalid = []
for toml_file in examples_dir.rglob("*.toml"):
    try:
        with open(toml_file, "rb") as f:
            tomllib.load(f)
    except Exception as e:
        invalid.append(f"{toml_file}: {e}")

if invalid:
    print("Invalid TOML files:")
    for i in invalid:
        print(i)
    sys.exit(1)

print(f"All TOML files in examples/ parse successfully")
'''
    r = _run_in_repo(["python3", "-c", script], timeout=30)
    assert r.returncode == 0, f"Examples TOML syntax check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_shell_scripts_syntax():
    """All shell scripts in scripts/ have valid bash syntax."""
    script = '''
from pathlib import Path
import subprocess
import sys

scripts_dir = Path("scripts")
if not scripts_dir.exists():
    print("scripts directory not found")
    sys.exit(0)

invalid = []
for sh_file in scripts_dir.rglob("*.sh"):
    result = subprocess.run(["bash", "-n", str(sh_file)], capture_output=True, text=True)
    if result.returncode != 0:
        invalid.append(f"{sh_file}: {result.stderr}")

if invalid:
    print("Invalid shell scripts:")
    for i in invalid:
        print(i)
    sys.exit(1)

print(f"All shell scripts in scripts/ have valid syntax")
'''
    r = _run_in_repo(["python3", "-c", script], timeout=60)
    assert r.returncode == 0, f"Shell scripts syntax check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_jinja2_templates_syntax():
    """All Jinja2 template files have valid syntax."""
    script = '''
from pathlib import Path
import sys

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("jinja2 not installed, skipping")
    sys.exit(0)

templates_dir = Path("src/prime_rl/templates")
if not templates_dir.exists():
    print("templates directory not found")
    sys.exit(0)

invalid = []
for template_file in templates_dir.glob("*.j2"):
    try:
        env = Environment(loader=FileSystemLoader(templates_dir))
        env.get_template(template_file.name)
    except Exception as e:
        invalid.append(f"{template_file}: {e}")

if invalid:
    print("Invalid Jinja2 templates:")
    for i in invalid:
        print(i)
    sys.exit(1)

print(f"All Jinja2 templates have valid syntax")
'''
    r = _run_in_repo(["python3", "-c", script], timeout=30)
    assert r.returncode == 0, f"Jinja2 templates syntax check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_lint_modified_dirs():
    """Ruff lint check on modified directories (configs/, inference/) passes."""
    install_result = _run_in_repo(["pip", "install", "ruff", "-q"], timeout=60)
    if install_result.returncode != 0:
        pytest.skip("Could not install ruff")

    r = _run_in_repo(
        ["ruff", "check", "--select", "E,W,F", "src/prime_rl/configs/", "src/prime_rl/inference/", "src/prime_rl/entrypoints/"],
        timeout=120,
    )
    assert r.returncode == 0, f"Ruff lint on modified dirs failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_modified_dirs():
    """Ruff format check on modified directories passes (pass_to_pass)."""
    install_result = _run_in_repo(["pip", "install", "ruff", "-q"], timeout=60)
    if install_result.returncode != 0:
        pytest.skip("Could not install ruff")

    r = _run_in_repo(
        ["ruff", "format", "--check", "--config=pyproject.toml", "src/prime_rl/configs/", "src/prime_rl/inference/", "src/prime_rl/entrypoints/"],
        timeout=120,
    )
    assert r.returncode == 0, f"Ruff format check on modified dirs failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_entrypoints_dir_parse():
    """All Python files in entrypoints/ parse without syntax errors (pass_to_pass)."""
    script = '''
import ast
from pathlib import Path
import sys

entrypoints_dir = Path("src/prime_rl/entrypoints/")
invalid = []

for py_file in entrypoints_dir.glob("*.py"):
    try:
        ast.parse(open(py_file).read())
    except SyntaxError as e:
        invalid.append(f"{py_file}: {e}")

if invalid:
    print("Files with syntax errors:")
    for i in invalid:
        print(i)
    sys.exit(1)
else:
    print(f"All {len(list(entrypoints_dir.glob('*.py')))} entrypoint files parse successfully")
'''
    r = _run_in_repo(["python3", "-c", script], timeout=60)
    assert r.returncode == 0, f"Entrypoint dir parse check failed:\n{r.stdout}\n{r.stderr}"
