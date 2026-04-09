"""
Task: maui-ci-move-to-aces-dnceng
Repo: dotnet/maui @ bfe8e58dcab8b030d6d87edf30fbe3f53827795d
PR:   34690

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/maui"


def _get_yaml_files():
    """Get list of modified YAML files."""
    return [
        Path(f"{REPO}/eng/pipelines/ci-uitests.yml"),
        Path(f"{REPO}/eng/pipelines/ci-device-tests.yml"),
    ]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_yaml_syntax_valid():
    """Modified YAML files must parse without errors using Python PyYAML."""
    for yaml_file in _get_yaml_files():
        result = subprocess.run(
            ["python3", "-c", f"""
import yaml
with open('{yaml_file}') as f:
    yaml.safe_load(f)
print('PASS')
"""],
            capture_output=True, text=True, timeout=30, cwd=REPO
        )
        assert result.returncode == 0, f"YAML syntax error in {yaml_file}: {result.stderr}"
        assert "PASS" in result.stdout, f"YAML validation failed for {yaml_file}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests with code execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_ci_uitests_pools_split():
    """ci-uitests.yml has separate internal/public pool parameters with correct pool values."""
    result = subprocess.run(
        ["python3", "-c", f"""
import yaml
import json

with open('{REPO}/eng/pipelines/ci-uitests.yml') as f:
    data = yaml.safe_load(f)

# Build a map of parameter names to their default values
param_defaults = {{}}
for p in data.get('parameters', []):
    name = p.get('name')
    default = p.get('default')
    param_defaults[name] = default

errors = []

# Internal pool variants must exist with correct pool names
required_internal = {{
    'androidPoolInternal': 'Azure Pipelines',
    'iosPoolInternal': 'Azure Pipelines',
    'windowsPoolInternal': 'NetCore1ESPool-Internal',
    'windowsBuildPoolInternal': 'NetCore1ESPool-Internal',
    'macosPoolInternal': 'Azure Pipelines',
    'androidPoolLinuxInternal': 'MAUI-DNCENG',
}}

for param, expected_pool in required_internal.items():
    if param not in param_defaults:
        errors.append(f"Missing {{param}} parameter")
    elif param_defaults[param].get('name') != expected_pool:
        errors.append(f"{{param}} should use '{{expected_pool}}', got: {{param_defaults[param].get('name')}}")

# Public pool variants must exist with correct pool names
required_public = {{
    'androidPoolPublic': 'AcesShared',
    'iosPoolPublic': 'AcesShared',
    'windowsPoolPublic': 'NetCore-Public',
    'windowsBuildPoolPublic': 'NetCore-Public',
    'macosPoolPublic': 'Azure Pipelines',
    'androidPoolLinuxPublic': 'MAUI-DNCENG',
}}

for param, expected_pool in required_public.items():
    if param not in param_defaults:
        errors.append(f"Missing {{param}} parameter")
    elif param_defaults[param].get('name') != expected_pool:
        errors.append(f"{{param}} should use '{{expected_pool}}', got: {{param_defaults[param].get('name')}}")

# Old combined pool names should not exist as parameters
old_params = ['androidPool', 'iosPool', 'windowsPool', 'windowsBuildPool', 'macosPool', 'androidPoolLinux']
for old_param in old_params:
    if old_param in param_defaults:
        errors.append(f"Old {{old_param}} parameter should be removed")

if errors:
    print(json.dumps({{'errors': errors}}))
else:
    print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    if "errors" in result.stdout:
        errors = json.loads(result.stdout).get("errors", [])
        assert False, f"Pool split validation failed: {errors}"
    assert "PASS" in result.stdout, f"Unexpected output: {result.stdout}"


# [pr_diff] fail_to_pass
def test_ci_uitests_conditional_pool_selection():
    """ci-uitests.yml uses System.TeamProject conditional for pool selection."""
    result = subprocess.run(
        ["python3", "-c", f"""
with open('{REPO}/eng/pipelines/ci-uitests.yml') as f:
    content = f.read()

errors = []

# Must have conditional selection using System.TeamProject
if "${{{{ if eq(variables['System.TeamProject'], 'internal') }}}}:" not in content:
    errors.append("Missing internal conditional for pool selection")
if "${{{{ else }}}}:" not in content:
    errors.append("Missing else branch for public pool selection")

# Template invocation should use conditional syntax with all pool mappings
required_mappings = [
    "androidPool: ${{{{ parameters.androidPoolInternal }}}}",
    "androidPool: ${{{{ parameters.androidPoolPublic }}}}",
    "iosPool: ${{{{ parameters.iosPoolInternal }}}}",
    "iosPool: ${{{{ parameters.iosPoolPublic }}}}",
    "windowsPool: ${{{{ parameters.windowsPoolInternal }}}}",
    "windowsPool: ${{{{ parameters.windowsPoolPublic }}}}",
]

for mapping in required_mappings:
    if mapping not in content:
        errors.append(f"Missing mapping: {{mapping}}")

import json
if errors:
    print(json.dumps({{'errors': errors}}))
else:
    print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    if "errors" in result.stdout:
        errors = json.loads(result.stdout).get("errors", [])
        assert False, f"Conditional selection validation failed: {errors}"
    assert "PASS" in result.stdout


# [pr_diff] fail_to_pass
def test_no_hardcoded_netcore_public():
    """Internal pool parameters do not use NetCore-Public pool which doesn't exist in dnceng/internal."""
    result = subprocess.run(
        ["python3", "-c", f"""
import yaml

with open('{REPO}/eng/pipelines/ci-uitests.yml') as f:
    data = yaml.safe_load(f)

errors = []

# Build a map of parameter names to their default pool names
for p in data.get('parameters', []):
    name = p.get('name', '')
    default = p.get('default', {{}})
    # Internal pools should NEVER use NetCore-Public (that's the bug fix)
    if 'Internal' in name and isinstance(default, dict):
        pool_name = default.get('name', '')
        if pool_name == 'NetCore-Public':
            errors.append(f"Internal parameter '{{name}}' incorrectly uses NetCore-Public pool")

import json
if errors:
    print(json.dumps({{'errors': errors}}))
else:
    print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    if "errors" in result.stdout:
        errors = json.loads(result.stdout).get("errors", [])
        assert False, f"NetCore-Public check failed: {errors}"
    assert "PASS" in result.stdout


# [pr_diff] fail_to_pass
def test_ci_device_tests_conditional_windows():
    """ci-device-tests.yml uses conditional pool selection for Windows Device Tests."""
    result = subprocess.run(
        ["python3", "-c", f"""
with open('{REPO}/eng/pipelines/ci-device-tests.yml') as f:
    content = f.read()

errors = []

# Must have conditional selection for Windows Device Tests
if "${{{{ if eq(variables['System.TeamProject'], 'internal') }}}}:" not in content:
    errors.append("Missing internal conditional in ci-device-tests.yml")
if "${{{{ else }}}}:" not in content:
    errors.append("Missing else branch in ci-device-tests.yml")
if "windowsPool: ${{{{ parameters.windowsPoolInternal }}}}" not in content:
    errors.append("Missing internal windowsPool mapping in ci-device-tests.yml")
if "windowsPool: ${{{{ parameters.windowsPoolPublic }}}}" not in content:
    errors.append("Missing public windowsPool mapping in ci-device-tests.yml")

import json
if errors:
    print(json.dumps({{'errors': errors}}))
else:
    print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    if "errors" in result.stdout:
        errors = json.loads(result.stdout).get("errors", [])
        assert False, f"ci-device-tests conditional check failed: {errors}"
    assert "PASS" in result.stdout


# [pr_diff] fail_to_pass
def test_aces_shared_pool_for_public_android_ios():
    """AcesShared pool with correct image is used for public Android/iOS tests."""
    result = subprocess.run(
        ["python3", "-c", f"""
import yaml

with open('{REPO}/eng/pipelines/ci-uitests.yml') as f:
    data = yaml.safe_load(f)

errors = []

# Find androidPoolPublic and iosPoolPublic and verify they use AcesShared
for p in data.get('parameters', []):
    name = p.get('name', '')
    if name in ('androidPoolPublic', 'iosPoolPublic'):
        default = p.get('default', {{}})
        pool_name = default.get('name')
        if pool_name != 'AcesShared':
            errors.append(f"{{name}} should use AcesShared pool, got: {{pool_name}}")
        demands = default.get('demands', [])
        has_tahoe = any('ACES_VM_SharedPool_Tahoe' in str(d) for d in demands)
        if not has_tahoe:
            errors.append(f"{{name}} should have ACES_VM_SharedPool_Tahoe image override in demands")

import json
if errors:
    print(json.dumps({{'errors': errors}}))
else:
    print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    if "errors" in result.stdout:
        errors = json.loads(result.stdout).get("errors", [])
        assert False, f"AcesShared pool check failed: {errors}"
    assert "PASS" in result.stdout


# [pr_diff] fail_to_pass
def test_netcore1espool_internal_for_internal_windows():
    """Internal Windows pools use NetCore1ESPool-Internal, not NetCore-Public."""
    result = subprocess.run(
        ["python3", "-c", f"""
import yaml

with open('{REPO}/eng/pipelines/ci-uitests.yml') as f:
    data = yaml.safe_load(f)

errors = []

for p in data.get('parameters', []):
    name = p.get('name', '')
    if name in ('windowsPoolInternal', 'windowsBuildPoolInternal'):
        default = p.get('default', {{}})
        pool_name = default.get('name')
        if pool_name != 'NetCore1ESPool-Internal':
            errors.append(f"{{name}} should use NetCore1ESPool-Internal, got: {{pool_name}}")
        demands = default.get('demands', [])
        has_windows_2022 = any('1es-windows-2022' in str(d) for d in demands)
        if not has_windows_2022:
            errors.append(f"{{name}} should have 1es-windows-2022 image override in demands")

import json
if errors:
    print(json.dumps({{'errors': errors}}))
else:
    print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    if "errors" in result.stdout:
        errors = json.loads(result.stdout).get("errors", [])
        assert False, f"NetCore1ESPool-Internal check failed: {errors}"
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) - regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified files contain actual changes, not just comments."""
    result = subprocess.run(
        ["python3", "-c", f"""
with open('{REPO}/eng/pipelines/ci-uitests.yml') as f:
    content = f.read()

# Should have substantial YAML structure changes
lines = content.split('\\n')
non_empty = [l for l in lines if l.strip() and not l.strip().startswith('#')]
if len(non_empty) > 50:
    print('PASS')
else:
    print(f'TOO_SHORT: {{len(non_empty)}} lines')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "PASS" in result.stdout, "YAML file appears to be a stub or empty"


# [static] pass_to_pass
def test_yaml_structure_valid():
    """YAML structure is valid and contains expected sections."""
    result = subprocess.run(
        ["python3", "-c", f"""
import yaml

with open('{REPO}/eng/pipelines/ci-uitests.yml') as f:
    data = yaml.safe_load(f)

errors = []

# Should have parameters section
if 'parameters' not in data:
    errors.append("Missing parameters section")
elif not isinstance(data['parameters'], list):
    errors.append("Parameters should be a list")
elif len(data['parameters']) == 0:
    errors.append("Parameters list is empty")

# Should have stages section
if 'stages' not in data:
    errors.append("Missing stages section")

import json
if errors:
    print(json.dumps({{'errors': errors}}))
else:
    print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    if "errors" in result.stdout:
        errors = json.loads(result.stdout).get("errors", [])
        assert False, f"YAML structure check failed: {errors}"
    assert "PASS" in result.stdout


# [static] pass_to_pass
def test_internal_public_pool_counts_match():
    """Number of internal and public pool parameters should be equal."""
    result = subprocess.run(
        ["python3", "-c", f"""
import yaml

with open('{REPO}/eng/pipelines/ci-uitests.yml') as f:
    data = yaml.safe_load(f)

param_names = [p.get('name', '') for p in data.get('parameters', [])]
internal_pools = [n for n in param_names if 'PoolInternal' in n]
public_pools = [n for n in param_names if 'PoolPublic' in n]

errors = []
if len(internal_pools) < 6:
    errors.append(f"Expected at least 6 internal pool params, got {{len(internal_pools)}}")
if len(public_pools) < 6:
    errors.append(f"Expected at least 6 public pool params, got {{len(public_pools)}}")
if len(internal_pools) != len(public_pools):
    errors.append(f"Mismatch: {{len(internal_pools)}} internal vs {{len(public_pools)}} public pools")

import json
if errors:
    print(json.dumps({{'errors': errors}}))
else:
    print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    if "errors" in result.stdout:
        errors = json.loads(result.stdout).get("errors", [])
        assert False, f"Pool counts check failed: {errors}"
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - repo CI/CD validation
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_template_files_exist():
    """All referenced template files exist in the repository (pass_to_pass)."""
    templates = [
        Path(f"{REPO}/eng/pipelines/common/ui-tests.yml"),
        Path(f"{REPO}/eng/pipelines/common/device-tests.yml"),
        Path(f"{REPO}/eng/pipelines/common/variables.yml"),
        Path(f"{REPO}/eng/pipelines/common/provision.yml"),
    ]
    for template in templates:
        assert template.exists(), f"Template file does not exist: {template}"


# [repo_tests] pass_to_pass
def test_repo_device_tests_yaml_valid():
    """ci-device-tests.yml is valid YAML with required sections (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", f"""
import yaml

with open('{REPO}/eng/pipelines/ci-device-tests.yml') as f:
    data = yaml.safe_load(f)

errors = []

# Should have required sections
if 'parameters' not in data:
    errors.append("Missing parameters section in ci-device-tests.yml")
if 'stages' not in data:
    errors.append("Missing stages section in ci-device-tests.yml")

# Should have key parameters defined
params = {{p['name'] for p in data.get('parameters', [])}}
if 'targetFrameworkVersions' not in params:
    errors.append("Missing targetFrameworkVersions parameter")

import json
if errors:
    print(json.dumps({{'errors': errors}}))
else:
    print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    if "errors" in result.stdout:
        errors = json.loads(result.stdout).get("errors", [])
        assert False, f"ci-device-tests YAML check failed: {errors}"
    assert "PASS" in result.stdout


# [repo_tests] pass_to_pass
def test_repo_device_tests_windows_pool_params_exist():
    """ci-device-tests.yml has Windows pool parameters defined (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", f"""
import yaml

with open('{REPO}/eng/pipelines/ci-device-tests.yml') as f:
    data = yaml.safe_load(f)

params = {{p['name'] for p in data.get('parameters', [])}}

# Should have Windows pool parameters (these exist in base commit)
if not ('windowsPoolInternal' in params or 'windowsPoolPublic' in params or 'windowsPool' in params):
    print("MISSING: No Windows pool parameter found")
else:
    print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "PASS" in result.stdout, "Missing Windows pool parameter in ci-device-tests.yml"


# [repo_tests] pass_to_pass
def test_repo_common_templates_yaml_valid():
    """Common template YAML files are syntactically valid (pass_to_pass)."""
    templates = [
        Path(f"{REPO}/eng/pipelines/common/ui-tests.yml"),
        Path(f"{REPO}/eng/pipelines/common/device-tests.yml"),
        Path(f"{REPO}/eng/pipelines/common/variables.yml"),
    ]
    for template in templates:
        result = subprocess.run(
            ["python3", "-c", f"""
import yaml
with open('{template}') as f:
    yaml.safe_load(f)
print('PASS')
"""],
            capture_output=True, text=True, timeout=30, cwd=REPO
        )
        assert result.returncode == 0, f"Invalid YAML in {template}: {result.stderr}"
        assert "PASS" in result.stdout


# [repo_tests] pass_to_pass
def test_repo_no_duplicate_parameter_names():
    """All parameter names in ci-uitests.yml are unique (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", f"""
import yaml
from collections import Counter

with open('{REPO}/eng/pipelines/ci-uitests.yml') as f:
    data = yaml.safe_load(f)

param_names = [p.get('name') for p in data.get('parameters', []) if p.get('name')]
duplicates = [name for name, count in Counter(param_names).items() if count > 1]

if duplicates:
    print(f"DUPLICATES: {{duplicates}}")
else:
    print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "PASS" in result.stdout, f"Duplicate parameter names found"


# [repo_tests] pass_to_pass
def test_repo_eng_common_templates_exist():
    """All eng/common template files referenced in variables exist (pass_to_pass)."""
    templates = [
        Path(f"{REPO}/eng/common/templates/variables/pool-providers.yml"),
    ]
    for template in templates:
        assert template.exists(), f"Common template file does not exist: {template}"


# [repo_tests] pass_to_pass
def test_repo_arcade_templates_exist():
    """All arcade template files exist in the repository (pass_to_pass)."""
    templates = [
        Path(f"{REPO}/eng/pipelines/arcade/variables.yml"),
        Path(f"{REPO}/eng/pipelines/arcade/setup-test-env.yml"),
    ]
    for template in templates:
        assert template.exists(), f"Arcade template file does not exist: {template}"


# [repo_tests] pass_to_pass
def test_repo_all_pipeline_templates_yaml_valid():
    """All YAML template files in eng/pipelines are syntactically valid (pass_to_pass)."""
    templates = [
        Path(f"{REPO}/eng/pipelines/common/device-tests-jobs.yml"),
        Path(f"{REPO}/eng/pipelines/common/device-tests-steps.yml"),
        Path(f"{REPO}/eng/pipelines/common/device-tests.yml"),
        Path(f"{REPO}/eng/pipelines/common/ui-tests-steps.yml"),
        Path(f"{REPO}/eng/pipelines/common/ui-tests.yml"),
        Path(f"{REPO}/eng/pipelines/common/variables.yml"),
    ]
    for template in templates:
        result = subprocess.run(
            ["python3", "-c", f"""
import yaml
with open('{template}') as f:
    yaml.safe_load(f)
print('PASS')
"""],
            capture_output=True, text=True, timeout=30, cwd=REPO
        )
        assert result.returncode == 0, f"Invalid YAML in {template}: {result.stderr}"
        assert "PASS" in result.stdout


# [repo_tests] pass_to_pass
def test_repo_ci_uitests_has_stages():
    """ci-uitests.yml has a valid stages section with at least one stage (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", f"""
import yaml

with open('{REPO}/eng/pipelines/ci-uitests.yml') as f:
    data = yaml.safe_load(f)

errors = []

if 'stages' not in data:
    errors.append("Missing stages section in ci-uitests.yml")
else:
    stages = data.get('stages', [])
    if not isinstance(stages, list):
        errors.append("stages should be a list")
    elif len(stages) == 0:
        errors.append("stages list should not be empty")

import json
if errors:
    print(json.dumps({{'errors': errors}}))
else:
    print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    if "errors" in result.stdout:
        errors = json.loads(result.stdout).get("errors", [])
        assert False, f"Stages check failed: {errors}"
    assert "PASS" in result.stdout


# [repo_tests] pass_to_pass
def test_repo_ci_device_tests_has_stages():
    """ci-device-tests.yml has a valid stages section with at least one stage (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", f"""
import yaml

with open('{REPO}/eng/pipelines/ci-device-tests.yml') as f:
    data = yaml.safe_load(f)

errors = []

if 'stages' not in data:
    errors.append("Missing stages section in ci-device-tests.yml")
else:
    stages = data.get('stages', [])
    if not isinstance(stages, list):
        errors.append("stages should be a list")
    elif len(stages) == 0:
        errors.append("stages list should not be empty")

import json
if errors:
    print(json.dumps({{'errors': errors}}))
else:
    print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    if "errors" in result.stdout:
        errors = json.loads(result.stdout).get("errors", [])
        assert False, f"Stages check failed: {errors}"
    assert "PASS" in result.stdout


# [repo_tests] pass_to_pass
def test_repo_trigger_and_pr_sections_exist():
    """Both pipeline files have trigger and pr sections defined (pass_to_pass)."""
    files = [
        Path(f"{REPO}/eng/pipelines/ci-uitests.yml"),
        Path(f"{REPO}/eng/pipelines/ci-device-tests.yml"),
    ]
    for yaml_file in files:
        result = subprocess.run(
            ["python3", "-c", f"""
import yaml
with open('{yaml_file}') as f:
    data = yaml.safe_load(f)
errors = []
if 'trigger' not in data:
    errors.append("Missing trigger section")
if 'pr' not in data:
    errors.append("Missing pr section")
import json
if errors:
    print(json.dumps({{'errors': errors}}))
else:
    print('PASS')
"""],
            capture_output=True, text=True, timeout=30, cwd=REPO
        )
        assert result.returncode == 0, f"Test failed for {yaml_file}: {result.stderr}"
        if "errors" in result.stdout:
            errors = json.loads(result.stdout).get("errors", [])
            assert False, f"Missing sections in {yaml_file}: {errors}"
        assert "PASS" in result.stdout


# [repo_tests] pass_to_pass
def test_repo_common_ui_tests_template_has_parameters():
    """Common UI tests template has required parameter definitions (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", f"""
import yaml

with open('{REPO}/eng/pipelines/common/ui-tests.yml') as f:
    data = yaml.safe_load(f)

errors = []

# Should have parameters section (can be dict or list depending on template type)
if 'parameters' not in data:
    errors.append("Missing parameters section in common/ui-tests.yml")
else:
    params = data.get('parameters', {{}})
    if len(params) == 0:
        errors.append("parameters should not be empty")
    # Should have key pool parameters
    if 'androidPool' not in params:
        errors.append("Missing androidPool parameter in common/ui-tests.yml")
    if 'iosPool' not in params:
        errors.append("Missing iosPool parameter in common/ui-tests.yml")

import json
if errors:
    print(json.dumps({{'errors': errors}}))
else:
    print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    if "errors" in result.stdout:
        errors = json.loads(result.stdout).get("errors", [])
        assert False, f"UI tests template check failed: {errors}"
    assert "PASS" in result.stdout


# [repo_tests] pass_to_pass
def test_repo_common_device_tests_template_has_parameters():
    """Common device tests template has required parameter definitions (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", f"""
import yaml

with open('{REPO}/eng/pipelines/common/device-tests.yml') as f:
    data = yaml.safe_load(f)

errors = []

# Should have parameters section (can be dict or list depending on template type)
if 'parameters' not in data:
    errors.append("Missing parameters section in common/device-tests.yml")
else:
    params = data.get('parameters', {{}})
    if len(params) == 0:
        errors.append("parameters should not be empty")
    # Should have key pool parameters
    if 'androidPool' not in params:
        errors.append("Missing androidPool parameter in common/device-tests.yml")
    if 'windowsPool' not in params:
        errors.append("Missing windowsPool parameter in common/device-tests.yml")

import json
if errors:
    print(json.dumps({{'errors': errors}}))
else:
    print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    if "errors" in result.stdout:
        errors = json.loads(result.stdout).get("errors", [])
        assert False, f"Device tests template check failed: {errors}"
    assert "PASS" in result.stdout


# [repo_tests] pass_to_pass
def test_repo_device_tests_has_target_framework_versions():
    """ci-device-tests.yml has targetFrameworkVersions parameter with valid structure (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", f"""
import yaml

with open('{REPO}/eng/pipelines/ci-device-tests.yml') as f:
    data = yaml.safe_load(f)

errors = []

params = {{p['name']: p for p in data.get('parameters', [])}}
if 'targetFrameworkVersions' not in params:
    errors.append("Missing targetFrameworkVersions parameter")
else:
    param = params['targetFrameworkVersions']
    if param.get('type') != 'object':
        errors.append("targetFrameworkVersions should be type object")
    if 'default' not in param:
        errors.append("targetFrameworkVersions should have a default value")

import json
if errors:
    print(json.dumps({{'errors': errors}}))
else:
    print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    if "errors" in result.stdout:
        errors = json.loads(result.stdout).get("errors", [])
        assert False, f"targetFrameworkVersions check failed: {errors}"
    assert "PASS" in result.stdout


# [repo_tests] pass_to_pass
def test_repo_no_duplicate_parameter_names_device_tests():
    """All parameter names in ci-device-tests.yml are unique (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", f"""
import yaml
from collections import Counter

with open('{REPO}/eng/pipelines/ci-device-tests.yml') as f:
    data = yaml.safe_load(f)

param_names = [p.get('name') for p in data.get('parameters', []) if p.get('name')]
duplicates = [name for name, count in Counter(param_names).items() if count > 1]

if duplicates:
    print(f"DUPLICATES: {{duplicates}}")
else:
    print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "PASS" in result.stdout, f"Duplicate parameter names found in ci-device-tests.yml"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) - rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

# Note: The dotnet/maui repo has .github/skills/* files but the task is about
# CI pipeline configuration. No specific config-derived tests apply to YAML changes.
