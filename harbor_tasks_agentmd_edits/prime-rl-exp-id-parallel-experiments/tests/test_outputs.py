"""
Task: prime-rl-exp-id-parallel-experiments
Repo: PrimeIntellect-ai/prime-rl @ 49573938857d8834b1917b43ece34f8b52a10fbd
PR:   591

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/prime-rl"


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified Python files must parse without errors."""
    files_to_check = [
        "src/prime_rl/rl.py",
        "src/prime_rl/utils/utils.py",
        "src/prime_rl/orchestrator/config.py",
        "src/prime_rl/orchestrator/client.py",
        "src/prime_rl/orchestrator/orchestrator.py",
        "src/prime_rl/eval/eval.py",
    ]
    for f in files_to_check:
        full = Path(REPO) / f
        try:
            ast.parse(full.read_text())
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in {f}: {e}")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess
# ---------------------------------------------------------------------------

def test_get_free_port_returns_valid_port():
    """get_free_port() must exist and return a valid ephemeral port number."""
    r = subprocess.run(
        [sys.executable, "-c", f"""
import ast, json

src = open("{REPO}/src/prime_rl/utils/utils.py").read()
tree = ast.parse(src)
lines = src.splitlines(keepends=True)

# Extract get_free_port function source
func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_free_port":
        func_src = "".join(lines[node.lineno - 1 : node.end_lineno])
        break

assert func_src is not None, "get_free_port function not found in utils.py"

# Execute the extracted function (it only uses stdlib socket)
exec(func_src, globals())
port = get_free_port()
print(json.dumps({{"port": port}}))
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    port = data["port"]
    assert isinstance(port, int), f"Port should be int, got {type(port)}"
    assert 1024 <= port <= 65535, f"Port {port} not in valid ephemeral range"


def test_get_cuda_visible_devices_respects_env():
    """get_cuda_visible_devices() must parse and sort CUDA_VISIBLE_DEVICES env var."""
    r = subprocess.run(
        [sys.executable, "-c", f"""
import ast, os, json, sys, types

src = open("{REPO}/src/prime_rl/utils/utils.py").read()
tree = ast.parse(src)
lines = src.splitlines(keepends=True)

# Extract get_cuda_visible_devices function source
func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_cuda_visible_devices":
        func_src = "".join(lines[node.lineno - 1 : node.end_lineno])
        break

assert func_src is not None, "get_cuda_visible_devices function not found in utils.py"

# Provide a torch mock (function uses torch.cuda.device_count for fallback)
torch = types.ModuleType("torch")
torch.cuda = types.SimpleNamespace(device_count=lambda: 4)
sys.modules["torch"] = torch
sys.modules["torch.cuda"] = torch.cuda

ns = {{"torch": torch, "os": os}}
exec(func_src, ns)
get_cuda_visible_devices = ns["get_cuda_visible_devices"]

# Test 1: with env var set, should parse and sort
os.environ["CUDA_VISIBLE_DEVICES"] = "3,1,0"
result_with = get_cuda_visible_devices()
print(json.dumps({{"with_env": result_with}}))

# Test 2: without env var, should fall back to device_count
os.environ.pop("CUDA_VISIBLE_DEVICES", None)
result_without = get_cuda_visible_devices()
print(json.dumps({{"no_env": result_without}}))
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    out_lines = r.stdout.strip().split("\n")
    with_env = json.loads(out_lines[0])["with_env"]
    no_env = json.loads(out_lines[1])["no_env"]

    assert with_env == [0, 1, 3], f"With CUDA_VISIBLE_DEVICES=3,1,0 expected [0,1,3], got {with_env}"
    assert no_env == [0, 1, 2, 3], f"Without env var expected [0,1,2,3] (mocked 4 GPUs), got {no_env}"


def test_client_base_url_construction():
    """setup_client() must construct base_url as http://host:port/v1 from config fields."""
    r = subprocess.run(
        [sys.executable, "-c", f"""
import re, json

src = open("{REPO}/src/prime_rl/orchestrator/client.py").read()

# Find the f-string that constructs base_url from host and port
match = re.search(r'base_url\\s*=\\s*f"(http://[^"]+)"', src)
assert match, "No base_url f-string construction found in client.py"

# Create mock config and evaluate the f-string
class MockConfig:
    host = "testhost"
    port = 1234

client_config = MockConfig()
base_url = eval('f"' + match.group(1) + '"')
expected = "http://testhost:1234/v1"
assert base_url == expected, f"Expected {{expected}}, got {{base_url}}"
print(json.dumps({{"url": base_url}}))
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["url"] == "http://testhost:1234/v1"


def test_tmux_log_paths_use_experiment_name():
    """tmux.sh must use experiment-name-based log paths, not hardcoded flat paths."""
    r = subprocess.run(
        ["bash", "-c", f"""
cd {REPO}
# Verify tmux.sh syntax is valid
bash -n tmux.sh || {{ echo "FAIL: tmux.sh has syntax errors"; exit 1; }}

# Old version has hardcoded "logs/orchestrator.log" — should be gone
if grep -q 'logs/orchestrator\\.log' tmux.sh; then
    echo "FAIL: still uses hardcoded logs/orchestrator.log"
    exit 1
fi
if grep -q 'logs/inference\\.log' tmux.sh; then
    echo "FAIL: still uses hardcoded logs/inference.log"
    exit 1
fi

# New version should reference EXPERIMENT_NAME in log paths
if ! grep -q 'EXPERIMENT_NAME' tmux.sh; then
    echo "FAIL: tmux.sh should use EXPERIMENT_NAME variable"
    exit 1
fi

echo "PASS"
"""],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural tests for config/code changes
# ---------------------------------------------------------------------------

def test_client_config_has_host_port():
    """ClientConfig must have separate host and port fields instead of base_url."""
    config_src = (Path(REPO) / "src/prime_rl/orchestrator/config.py").read_text()
    tree = ast.parse(config_src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ClientConfig":
            field_names = set()
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    field_names.add(item.target.id)

            assert "host" in field_names, f"ClientConfig missing 'host' field, has: {field_names}"
            assert "port" in field_names, f"ClientConfig missing 'port' field, has: {field_names}"
            assert "base_url" not in field_names, \
                f"ClientConfig should NOT have 'base_url' field, has: {field_names}"
            break
    else:
        raise AssertionError("ClientConfig class not found in config.py")


def test_rl_config_has_exp_id():
    """RLConfig must have an exp_id field for experiment identification."""
    rl_src = (Path(REPO) / "src/prime_rl/rl.py").read_text()
    tree = ast.parse(rl_src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "RLConfig":
            field_names = set()
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    field_names.add(item.target.id)
            assert "exp_id" in field_names, \
                f"RLConfig missing 'exp_id' field, has: {field_names}"
            break
    else:
        raise AssertionError("RLConfig class not found in rl.py")


def test_rl_auto_setup_exp_validator():
    """RLConfig must have auto_setup_exp validator that appends exp_id to paths."""
    rl_src = (Path(REPO) / "src/prime_rl/rl.py").read_text()
    assert "auto_setup_exp" in rl_src, "auto_setup_exp validator not found"
    assert "self.log.path" in rl_src and "self.exp_id" in rl_src, \
        "Validator should modify log path using exp_id"
    assert "self.trainer.data.path" in rl_src, "Validator should modify trainer data path"
    assert "self.trainer.weights.path" in rl_src, "Validator should modify trainer weights path"


def test_rl_uses_visible_devices_and_free_port():
    """rl() must use get_cuda_visible_devices() and get_free_port() for parallel support."""
    rl_src = (Path(REPO) / "src/prime_rl/rl.py").read_text()
    assert "get_cuda_visible_devices()" in rl_src, \
        "rl() should call get_cuda_visible_devices() instead of range()"
    assert "get_free_port()" in rl_src, \
        "rl() should call get_free_port() for torchrun rendezvous"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — README documentation tests
# ---------------------------------------------------------------------------

def test_readme_multiple_experiments_section():
    """README.md must have a 'Multiple Experiments per Node' section."""
    content = (Path(REPO) / "README.md").read_text()
    assert "Multiple Experiments per Node" in content, \
        "README should have 'Multiple Experiments per Node' section"


def test_readme_exp_id_documented():
    """README.md must document the --exp-id flag with example commands."""
    content = (Path(REPO) / "README.md").read_text()
    assert "--exp-id" in content, "README should document --exp-id flag"
    assert "exp-1" in content, "README should include exp-1 example"


def test_readme_tmux_exp_argument():
    """README.md must show tmux.sh invoked with experiment name argument."""
    content = (Path(REPO) / "README.md").read_text()
    assert "./tmux.sh exp-" in content, \
        "README should show ./tmux.sh called with experiment name"
