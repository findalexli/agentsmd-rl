"""
Task: gradio-ci-venv-cache-symlink
Repo: gradio-app/gradio @ 30af84cdd100855999281de8720cbb6d58b48556
PR:   13029

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

import yaml

REPO = "/workspace/gradio"
ACTION_FILE = f"{REPO}/.github/actions/install-all-deps/action.yml"
TEST_FILE = f"{REPO}/js/textbox/Textbox.test.ts"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via a temp script in the repo directory."""
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
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_action_yaml_valid():
    """action.yml must be valid YAML."""
    data = yaml.safe_load(Path(ACTION_FILE).read_text())
    assert isinstance(data, dict), "action.yml did not parse to a dict"
    assert "runs" in data, "action.yml missing 'runs' key"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_venv_created_after_cache_restore():
    """Venv creation (uv venv) must execute AFTER the cache restore step.

    If venv is created before cache restore, the cache overwrites
    the freshly created venv with stale symlinks.
    """
    r = _run_py(
        """
import yaml
from pathlib import Path

data = yaml.safe_load(
    Path("/workspace/gradio/.github/actions/install-all-deps/action.yml").read_text()
)
steps = data["runs"]["steps"]

create_env_idx = None
cache_idx = None
for i, step in enumerate(steps):
    run_cmd = str(step.get("run", ""))
    uses = str(step.get("uses", ""))
    if create_env_idx is None and "uv venv" in run_cmd:
        create_env_idx = i
    if cache_idx is None and "actions/cache" in uses:
        cache_idx = i

assert create_env_idx is not None, 'No step with "uv venv" found'
assert cache_idx is not None, "No actions/cache step found"
assert create_env_idx > cache_idx, (
    f"venv creation (step {create_env_idx}) runs BEFORE "
    f"cache restore (step {cache_idx})"
)
print("PASS")
"""
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_cache_key_includes_exact_python_version():
    """Cache key must include the EXACT installed Python version.

    Using only inputs.python_version (e.g. 3.12) is insufficient — the cache
    key must distinguish patch releases (3.12.7 vs 3.12.8) to avoid stale
    symlinks. Accepts: step outputs with python-version, env.pythonLocation,
    hashFiles referencing a .python-version file.
    """
    r = _run_py(
        r"""
import re
from pathlib import Path

raw = Path("/workspace/gradio/.github/actions/install-all-deps/action.yml").read_text()

key_line = ""
in_cache = False
for line in raw.splitlines():
    s = line.strip()
    if "actions/cache" in s:
        in_cache = True
    if in_cache and s.startswith("key:"):
        key_line = s
        break

assert key_line, "No cache key found in action.yml"

patterns = [
    r"steps\.\w[\w-]*\.outputs\.python-version",
    r"steps\.\w[\w-]*\.outputs\.\w*version",
    r"env\.pythonLocation",
    r"hashFiles.*\.python-version",
]
matched = any(re.search(pat, key_line, re.IGNORECASE) for pat in patterns)
assert matched, f"Cache key has no exact-version reference: {key_line[:200]}"
print("PASS")
"""
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] pass_to_pass
def test_step_output_refs_resolve():
    """If cache key references steps.<id>.outputs.*, that step id must exist."""
    raw = Path(ACTION_FILE).read_text()
    data = yaml.safe_load(raw)
    steps = data["runs"]["steps"]

    step_refs = set(re.findall(r"steps\.(\w[\w-]*)\.outputs", raw))
    if not step_refs:
        return  # env-var or hashFiles approach, no id needed

    step_ids = {str(s.get("id", "")) for s in steps if s.get("id")}
    missing = [ref for ref in step_refs if ref not in step_ids]
    assert not missing, (
        f"References step(s) {missing} but no step has that id. "
        f"Existing ids: {sorted(step_ids)}"
    )


# [pr_diff] fail_to_pass
def test_textbox_await_tick_active():
    """await tick() must be active (not commented) in the textbox copy test.

    The Svelte component needs an event-loop tick to process the click event
    before assertions can check the emitted value.
    """
    r = _run_py(
        r"""
import re
from pathlib import Path

content = Path("/workspace/gradio/js/textbox/Textbox.test.ts").read_text()
lines = content.splitlines()

# Find the copy test block boundaries
start = None
end = None
for i, line in enumerate(lines):
    if "copy: emitted when copy button is clicked" in line:
        start = i
    elif start is not None and re.match(r'^\t\}\);', line):
        # Top-level test closer (one tab indent) ends the block
        end = i
        break

assert start is not None, "Copy test block not found"
block = lines[start:(end or len(lines))]

# Find await tick() in the block — must be present and not commented
for line in block:
    stripped = line.strip()
    if "await tick()" in stripped:
        assert not stripped.startswith("//"), "await tick() is commented out"
        print("PASS")
        exit(0)

raise AssertionError("await tick() not found in copy test block")
"""
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_core_ci_steps_present():
    """Core CI action steps must still be present and functional."""
    data = yaml.safe_load(Path(ACTION_FILE).read_text())
    steps = data["runs"]["steps"]
    step_names = [str(s.get("name", "")) for s in steps]
    step_uses = [str(s.get("uses", "")) for s in steps]
    all_runs = " ".join(str(s.get("run", "")) for s in steps)

    for req in ["Install Python", "Install ffmpeg"]:
        assert any(req in name for name in step_names), (
            f'Required step "{req}" missing'
        )

    all_uses_str = " ".join(step_uses)
    for action in ["actions/cache", "setup-python"]:
        assert action in all_uses_str, f"{action} no longer used"

    assert "uv venv" in all_runs, "uv venv creation step missing"


# [repo_tests] pass_to_pass
def test_textbox_copy_test_exists():
    """Textbox copy test case must still exist with its assertion."""
    content = Path(TEST_FILE).read_text()
    assert "copy: emitted when copy button is clicked" in content, (
        "Copy test case was removed"
    )
    assert "toHaveBeenCalledTimes(1)" in content, (
        "Copy assertion was removed"
    )


# [pr_diff] pass_to_pass
def test_cache_key_includes_hashfiles():
    """Cache key must still include hashFiles for dependency tracking."""
    raw = Path(ACTION_FILE).read_text()
    assert "hashFiles" in raw, (
        "Cache key no longer includes hashFiles for dependency tracking"
    )


# [pr_diff] pass_to_pass
def test_cache_paths_include_venv():
    """Cache paths must still include the venv directory."""
    data = yaml.safe_load(Path(ACTION_FILE).read_text())
    steps = data["runs"]["steps"]
    for step in steps:
        if "actions/cache" in str(step.get("uses", "")):
            path = str(step.get("with", {}).get("path", ""))
            assert "venv" in path, f"Cache paths do not include venv: {path}"
            return
    raise AssertionError("Cache step not found")
