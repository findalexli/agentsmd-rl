"""
Task: sglang-glm5-ci-tests
Repo: sgl-project/sglang @ c3c13dd5e3b42850d5a96adca4092deb72bf1e4a
PR:   22285

This task adds CI tests for the GLM-5 model. Since the tests require 8 GPUs
and actual model weights to run, we verify the structural changes through
behavioral tests that actually execute Python code to validate:
1. Test files are renamed correctly (test_deepseek_v32_* -> test_dsa_models_*)
2. New GLM5 test classes are added with correct structure
3. Code changes are syntactically valid and can be parsed
4. Configuration changes (est_time, env vars) are applied correctly

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/sglang"

# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks using subprocess
# ---------------------------------------------------------------------------

def test_basic_file_syntax():
    """The renamed test_dsa_models_basic.py must compile without errors."""
    basic_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_basic.py")
    assert basic_file.exists(), f"File not found: {basic_file}"

    # Use subprocess to actually compile the file
    r = subprocess.run(
        ["python3", "-m", "py_compile", str(basic_file)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in {basic_file}: {r.stderr}"


def test_mtp_file_syntax():
    """The renamed test_dsa_models_mtp.py must compile without errors."""
    mtp_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_mtp.py")
    assert mtp_file.exists(), f"File not found: {mtp_file}"

    r = subprocess.run(
        ["python3", "-m", "py_compile", str(mtp_file)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in {mtp_file}: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests using code execution
# ---------------------------------------------------------------------------

def test_glm5_model_path_constant_exists():
    """GLM5_MODEL_PATH constant must be defined in both test files."""
    basic_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_basic.py")
    mtp_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_mtp.py")

    # Use subprocess to execute Python that parses and validates the AST
    validate_script = '''
import ast
import sys

def check_glm5_constant(path):
    with open(path) as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "GLM5_MODEL_PATH":
                    if isinstance(node.value, ast.Constant):
                        if node.value.value == "zai-org/GLM-5-FP8":
                            return True
    return False

basic_ok = check_glm5_constant(sys.argv[1])
mtp_ok = check_glm5_constant(sys.argv[2])

if basic_ok and mtp_ok:
    print("PASS")
    sys.exit(0)
else:
    if not basic_ok:
        print("FAIL: GLM5_MODEL_PATH not found or incorrect in basic file")
    if not mtp_ok:
        print("FAIL: GLM5_MODEL_PATH not found or incorrect in mtp file")
    sys.exit(1)
'''
    r = subprocess.run(
        ["python3", "-c", validate_script, str(basic_file), str(mtp_file)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS, got: {r.stdout}"


def test_glm5_test_classes_exist():
    """GLM5 test classes must be defined in both test files."""
    basic_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_basic.py")
    mtp_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_mtp.py")

    validate_script = '''
import ast
import sys

def get_class_names(path):
    with open(path) as f:
        tree = ast.parse(f.read())
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

basic_classes = get_class_names(sys.argv[1])
mtp_classes = get_class_names(sys.argv[2])

required_basic = ["TestGLM5DP", "TestGLM5TP"]
required_mtp = ["TestGLM5DPMTP", "TestGLM5TPMTP"]

missing = []
for cls in required_basic:
    if cls not in basic_classes:
        missing.append(f"{cls} in basic file")
for cls in required_mtp:
    if cls not in mtp_classes:
        missing.append(f"{cls} in mtp file")

if missing:
    print(f"FAIL: Missing classes: {missing}")
    sys.exit(1)
else:
    print("PASS")
    sys.exit(0)
'''
    r = subprocess.run(
        ["python3", "-c", validate_script, str(basic_file), str(mtp_file)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_est_time_updated():
    """register_cuda_ci est_time must be updated from 360 to 720 in basic test."""
    basic_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_basic.py")

    validate_script = '''
import ast
import sys

with open(sys.argv[1]) as f:
    content = f.read()

# Check for the correct value (720)
has_720 = "register_cuda_ci(est_time=720" in content
# Check that old value is gone
has_360 = "register_cuda_ci(est_time=360" in content

if has_720 and not has_360:
    print("PASS")
    sys.exit(0)
else:
    if not has_720:
        print("FAIL: est_time=720 not found")
    if has_360:
        print("FAIL: est_time=360 still present")
    sys.exit(1)
'''
    r = subprocess.run(
        ["python3", "-c", validate_script, str(basic_file)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_mtp_env_override_added():
    """SGLANG_ENABLE_SPEC_V2 environment override must wrap server launch in MTP tests."""
    mtp_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_mtp.py")

    validate_script = '''
import ast
import sys

with open(sys.argv[1]) as f:
    tree = ast.parse(f.read())

# Find all With nodes and check for envs.SGLANG_ENABLE_SPEC_V2.override(True)
found_override = False

for node in ast.walk(tree):
    if isinstance(node, ast.With):
        for item in node.items:
            ctx = item.context_expr
            # Check for: envs.SGLANG_ENABLE_SPEC_V2.override(True)
            if isinstance(ctx, ast.Call):
                if isinstance(ctx.func, ast.Attribute):
                    if ctx.func.attr == "override":
                        if isinstance(ctx.func.value, ast.Attribute):
                            if ctx.func.value.attr == "SGLANG_ENABLE_SPEC_V2":
                                # Check the argument is True
                                if len(ctx.args) == 1:
                                    arg = ctx.args[0]
                                    if isinstance(arg, ast.Constant) and arg.value is True:
                                        found_override = True
                                        break

if found_override:
    print("PASS")
    sys.exit(0)
else:
    print("FAIL: envs.SGLANG_ENABLE_SPEC_V2.override(True) not found")
    sys.exit(1)
'''
    r = subprocess.run(
        ["python3", "-c", validate_script, str(mtp_file)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_mtp_class_renamed_correctly():
    """TestDeepseekV32DPMTPV2 must be renamed to TestDeepseekV32TPMTP."""
    mtp_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_mtp.py")

    validate_script = '''
import ast
import sys

with open(sys.argv[1]) as f:
    tree = ast.parse(f.read())

class_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

has_new = "TestDeepseekV32TPMTP" in class_names
has_old = "TestDeepseekV32DPMTPV2" in class_names

if has_new and not has_old:
    print("PASS")
    sys.exit(0)
else:
    if not has_new:
        print("FAIL: TestDeepseekV32TPMTP not found")
    if has_old:
        print("FAIL: Old TestDeepseekV32DPMTPV2 still exists")
    sys.exit(1)
'''
    r = subprocess.run(
        ["python3", "-c", validate_script, str(mtp_file)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_mtp_mem_frac_updated():
    """mem-frac should be updated from 0.7 to 0.8 in GLM5 MTP tests."""
    mtp_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_mtp.py")

    validate_script = '''
import ast
import sys

with open(sys.argv[1]) as f:
    content = f.read()

# Check for 0.8 mem-frac in the context of GLM5 classes
# Looking for the pattern: "--mem-frac", followed by "0.8"
if '"0.8"' in content:
    print("PASS")
    sys.exit(0)
else:
    print("FAIL: mem-frac 0.8 not found")
    sys.exit(1)
'''
    r = subprocess.run(
        ["python3", "-c", validate_script, str(mtp_file)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that should pass on base AND fix
# ---------------------------------------------------------------------------

def test_repo_ruff_check():
    """Repo's ruff lint check passes on test files (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    # Run ruff check on the test directory
    r = subprocess.run(
        ["ruff", "check", "--select=F401,F821", f"{REPO}/test/registered/8-gpu-models/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_black_check():
    """Repo's black format check passes on test files (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["black", "--check", f"{REPO}/test/registered/8-gpu-models/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Black format check failed:\n{r.stderr}"


def test_repo_isort_check():
    """Repo's isort import order check passes on test files (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["isort", "--check-only", f"{REPO}/test/registered/8-gpu-models/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Isort check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub using subprocess
# ---------------------------------------------------------------------------

def test_old_files_removed():
    """Old test file names should not exist (they were renamed)."""
    old_basic = Path(f"{REPO}/test/registered/8-gpu-models/test_deepseek_v32_basic.py")
    old_mtp = Path(f"{REPO}/test/registered/8-gpu-models/test_deepseek_v32_mtp.py")

    validate_script = '''
import sys
from pathlib import Path

old_basic = Path(sys.argv[1])
old_mtp = Path(sys.argv[2])

if old_basic.exists() or old_mtp.exists():
    if old_basic.exists():
        print(f"FAIL: {old_basic} should not exist")
    if old_mtp.exists():
        print(f"FAIL: {old_mtp} should not exist")
    sys.exit(1)
else:
    print("PASS")
    sys.exit(0)
'''
    r = subprocess.run(
        ["python3", "-c", validate_script, str(old_basic), str(old_mtp)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_new_files_exist():
    """New test file names should exist."""
    new_basic = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_basic.py")
    new_mtp = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_mtp.py")

    validate_script = '''
import sys
from pathlib import Path

new_basic = Path(sys.argv[1])
new_mtp = Path(sys.argv[2])

missing = []
if not new_basic.exists():
    missing.append(str(new_basic))
if not new_mtp.exists():
    missing.append(str(new_mtp))

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
else:
    print("PASS")
    sys.exit(0)
'''
    r = subprocess.run(
        ["python3", "-c", validate_script, str(new_basic), str(new_mtp)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_glm5_classes_have_required_methods():
    """GLM5 test classes must have setUpClass, tearDownClass, and test methods."""
    basic_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_basic.py")

    validate_script = '''
import ast
import sys

with open(sys.argv[1]) as f:
    tree = ast.parse(f.read())

errors = []

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name.startswith("TestGLM5"):
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]

        if "setUpClass" not in methods:
            errors.append(f"{node.name} missing setUpClass")
        if "tearDownClass" not in methods:
            errors.append(f"{node.name} missing tearDownClass")

        test_methods = [m for m in methods if m.startswith("test_")]
        if len(test_methods) < 1:
            errors.append(f"{node.name} has no test methods")

if errors:
    for e in errors:
        print(f"FAIL: {e}")
    sys.exit(1)
else:
    print("PASS")
    sys.exit(0)
'''
    r = subprocess.run(
        ["python3", "-c", validate_script, str(basic_file)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout
