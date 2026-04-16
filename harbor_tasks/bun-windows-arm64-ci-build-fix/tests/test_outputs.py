"""
Task: bun-windows-arm64-ci-build-fix
Repo: bun @ cd4459476a5f0af4e45b8594ac88732ba6d79afb
PR:   28922

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import os
import re
import tempfile

REPO = "/workspace/bun"


def run_ci_mjs(commit_message=None, env_extra=None):
    """Run ci.mjs and return the path to generated ci.yml"""
    env = os.environ.copy()
    
    # Create mock buildkite-agent if needed (for skipSizeCheck testing)
    if commit_message and 'skip size' in commit_message:
        # Create temp directory for mock buildkite-agent
        mock_dir = tempfile.mkdtemp()
        mock_agent = os.path.join(mock_dir, "buildkite-agent")
        with open(mock_agent, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('# Mock buildkite-agent - handles various commands\n')
            f.write('case "$*" in\n')
            f.write('    *"secret get GITHUB_TOKEN"*)\n')
            f.write('        echo "dummy-token-12345"\n')
            f.write('        exit 0\n')
            f.write('        ;;\n')
            f.write('    *"artifact upload"*)\n')
            f.write('        # Mock artifact upload - do nothing\n')
            f.write('        exit 0\n')
            f.write('        ;;\n')
            f.write('    *"meta-data get"*/"binary-size:"*)\n')
            f.write('        # Return empty for binary-size metadata\n')
            f.write('        exit 0\n')
            f.write('        ;;\n')
            f.write('    *"meta-data set"*/"binary-size:"*)\n')
            f.write('        # Mock meta-data set - do nothing\n')
            f.write('        exit 0\n')
            f.write('        ;;\n')
            f.write('    *"annotate"*)\n')
            f.write('        # Mock annotate - do nothing\n')
            f.write('        exit 0\n')
            f.write('        ;;\n')
            f.write('    *)\n')
            f.write('        exit 0\n')
            f.write('        ;;\n')
            f.write('esac\n')
            f.write('exit 0\n')
        os.chmod(mock_agent, 0o755)
        # Prepend mock directory to PATH
        env['PATH'] = mock_dir + ':' + env.get('PATH', '')
        # Set BUILDKITE to trigger using BUILDKITE_MESSAGE
        env['BUILDKITE'] = 'true'
    
    if commit_message:
        env["BUILDKITE_MESSAGE"] = commit_message
    if env_extra:
        env.update(env_extra)

    # Run ci.mjs to generate pipeline
    r = subprocess.run(
        ["node", ".buildkite/ci.mjs"],
        capture_output=True,
        text=True,
        cwd=REPO,
        env=env,
        timeout=120,
    )
    assert r.returncode == 0, f"ci.mjs failed: {r.stderr}"

    ci_yml_path = os.path.join(REPO, ".buildkite/ci.yml")
    assert os.path.exists(ci_yml_path), f"ci.yml not generated"
    return ci_yml_path


def find_step_in_yml(yml_content, step_key):
    """Find a step in the YAML and return (start_idx, end_idx) of the step section.
    Returns (None, None) if step not found.
    """
    # Find the step by its key
    key_pattern = rf'key:\s+{re.escape(step_key)}'
    key_match = re.search(key_pattern, yml_content)
    if not key_match:
        return None, None
    
    # Start of step is the key line (include the newline after it)
    step_start = key_match.start()
    
    # Find the next step or end of steps
    # Next step pattern: newline, 2 spaces, newline, dash, space, newline, 4 spaces, key:
    remaining = yml_content[key_match.end():]
    next_step_match = re.search(r'\n  \n- \n    key:', remaining)
    
    if next_step_match:
        step_end = key_match.end() + next_step_match.start()
    else:
        step_end = len(yml_content)
    
    return step_start, step_end


def step_exists_in_yml(yml_content, step_key):
    """Check if a step with given key exists"""
    start, end = find_step_in_yml(yml_content, step_key)
    return start is not None


def get_step_attr_in_yml(yml_content, step_key, attr):
    """Get an attribute value for a step by key"""
    start, end = find_step_in_yml(yml_content, step_key)
    if start is None:
        return None
    
    step_section = yml_content[start:end]
    
    # Special case for key - it's at the beginning
    if attr == 'key':
        key_match = re.search(rf'key:\s+({re.escape(step_key)})\s*(?:\n|$)', step_section)
        if key_match:
            return key_match.group(1)
        return None
    
    # Look for the attribute in the step section
    attr_pattern = rf'{attr}:\s*(.*?)(?:\n|$)'
    attr_match = re.search(attr_pattern, step_section)
    if attr_match:
        return attr_match.group(1).strip()
    return None


def get_step_command_in_yml(yml_content, step_key):
    """Get the command for a step"""
    start, end = find_step_in_yml(yml_content, step_key)
    if start is None:
        return None
    
    step_section = yml_content[start:end]
    
    # Find command - it may span multiple lines and contain JSON
    cmd_match = re.search(r'command:\s*(.*?)(?:\n\s*\n|\n\s*-\s*\n|\Z)', step_section, re.DOTALL)
    if cmd_match:
        cmd = cmd_match.group(1).strip()
        # Remove leading dash and whitespace
        cmd = re.sub(r'^[\-\s]+', '', cmd).strip()
        return cmd
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    r = subprocess.run(
        ["node", "--check", f"{REPO}/.buildkite/ci.mjs"],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax check failed: {r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_windows_arm64_uses_bun_runtime():
    """
    Test that Windows ARM64 builds use 'bun' runtime instead of 'node'.

    Behavioral test: we run ci.mjs to generate the pipeline, then check
    that the windows-aarch64-build-bun step's command starts with 'bun',
    not 'node --experimental-strip-types'.
    """
    ci_yml_path = run_ci_mjs()
    with open(ci_yml_path) as f:
        yml_content = f.read()

    # Find the windows-aarch64 build step's command
    cmd = get_step_command_in_yml(yml_content, "windows-aarch64-build-bun")
    assert cmd is not None, "windows-aarch64-build-bun step not found in pipeline"

    # The fix changes the runtime from 'node --experimental-strip-types' to 'bun'
    # Check that 'bun' is in the command AND 'node --experimental-strip-types' is NOT
    assert "bun" in cmd, f"windows-aarch64 build command should use 'bun', got: {cmd}"
    assert "node --experimental-strip-types" not in cmd, \
        f"windows-aarch64 build should NOT use node, got: {cmd}"

    print(f"OK: windows-aarch64 uses bun runtime: {cmd[:60]}...")


# [pr_diff] fail_to_pass
def test_skip_size_check_option_parsed():
    """
    Test that [skip size check] in commit message sets soft_fail on binary-size step.

    Behavioral test: we run ci.mjs with BUILDKITE_MESSAGE containing '[skip size check]',
    then check that the binary-size step has soft_fail: true.
    """
    ci_yml_path = run_ci_mjs(commit_message="Test commit [skip size check]")
    with open(ci_yml_path) as f:
        yml_content = f.read()

    # Find the binary-size step
    assert step_exists_in_yml(yml_content, "binary-size"), \
        "binary-size step not found in pipeline"

    # Check soft_fail is set based on skipSizeCheck option
    soft_fail = get_step_attr_in_yml(yml_content, "binary-size", "soft_fail")
    assert soft_fail is not None, "binary-size step should have soft_fail attribute"
    # soft_fail should be True/true when skipSizeCheck is set
    assert soft_fail.lower() == "true", \
        f"binary-size step should have soft_fail: true when skipSizeCheck is set, got: {soft_fail}"

    # Also verify the step has command with binary-size
    cmd = get_step_command_in_yml(yml_content, "binary-size")
    assert cmd is not None, "binary-size step should have command"
    assert "binary-size" in cmd, f"binary-size command should contain 'binary-size', got: {cmd}"

    print(f"OK: binary-size step has soft_fail=True when skipSizeCheck is set")


# [pr_diff] fail_to_pass
def test_binary_size_step_function_exists():
    """
    Test that getBinarySizeStep produces a step with correct structure.

    Behavioral test: we run ci.mjs, find the binary-size step, and verify
    it has all required properties (key, command, depends_on, etc).
    """
    ci_yml_path = run_ci_mjs()
    with open(ci_yml_path) as f:
        yml_content = f.read()

    # Find the binary-size step
    assert step_exists_in_yml(yml_content, "binary-size"), \
        "binary-size step not found in pipeline"

    # Verify required properties exist
    key = get_step_attr_in_yml(yml_content, "binary-size", "key")
    assert key == "binary-size", f"step key should be 'binary-size', got: {key}"

    # Command should run bun scripts/binary-size.ts
    cmd = get_step_command_in_yml(yml_content, "binary-size")
    assert cmd is not None, "binary-size step should have command"
    assert "bun" in cmd, f"binary-size command should use bun, got: {cmd}"
    assert "binary-size" in cmd, f"binary-size command should reference binary-size script, got: {cmd}"

    # Should have depends_on
    depends_on = get_step_attr_in_yml(yml_content, "binary-size", "depends_on")
    assert depends_on is not None, "binary-size step should have depends_on"

    # Should have agents
    agents = get_step_attr_in_yml(yml_content, "binary-size", "agents")
    assert agents is not None, "binary-size step should have agents"

    print(f"OK: binary-size step exists with proper structure")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) -- regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """
    Verify getBuildCommand is not a stub - has meaningful implementation.
    """
    ci_mjs_path = os.path.join(REPO, ".buildkite/ci.mjs")
    with open(ci_mjs_path) as f:
        ci_mjs = f.read()

    # Find getBuildCommand function
    match = re.search(
        r'function getBuildCommand\([^)]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}',
        ci_mjs
    )
    assert match, "Could not find getBuildCommand function"
    func_body = match.group(1)

    # Check it's not a stub - should have multiple meaningful lines
    meaningful_lines = [
        line for line in func_body.split('\n')
        if line.strip()
        and not line.strip().startswith('//')
        and not line.strip().startswith('*')
        and not line.strip().startswith('/*')
    ]
    assert len(meaningful_lines) >= 2, "getBuildCommand function body is too simple (stub-like)"
    assert 'runtime' in func_body or 'bun' in func_body or 'node' in func_body, \
        "Function doesn't reference runtime"


# [static] pass_to_pass
def test_other_platforms_use_node():
    """
    Verify that non-Windows-ARM64 platforms still use node runtime.
    """
    ci_yml_path = run_ci_mjs()
    with open(ci_yml_path) as f:
        yml_content = f.read()

    # Find darwin-aarch64 build step - should use node (not bun)
    cmd = get_step_command_in_yml(yml_content, "darwin-aarch64-build-bun")
    if cmd:
        assert "node" in cmd, f"darwin-aarch64 should use node, got: {cmd}"
        assert "experimental-strip-types" in cmd, \
            f"darwin-aarch64 should use --experimental-strip-types flag, got: {cmd}"

    # Find linux-x64 build step - should use node
    cmd = get_step_command_in_yml(yml_content, "linux-x64-build-bun")
    if cmd:
        assert "node" in cmd, f"linux-x64 should use node, got: {cmd}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) -- CI/CD regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    r = subprocess.run(
        ["bun", "lint"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    r = subprocess.run(
        ["bunx", "tsc@6.0.2", "--noEmit"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_banned_words():
    install = subprocess.run(
        ["bun", "install"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert install.returncode == 0, f"bun install failed: {install.stderr}"
    r = subprocess.run(
        ["bun", "./test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Banned words check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_package_json_lint():
    r = subprocess.run(
        ["bun", "test", "test/package-json-lint.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Package JSON lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_node_syntax_ci():
    r = subprocess.run(
        ["node", "--check", f"{REPO}/.buildkite/ci.mjs"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"CI script syntax check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_node_syntax_utils():
    r = subprocess.run(
        ["node", "--check", f"{REPO}/scripts/utils.mjs"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Utils script syntax check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_bun_build_ci_ts():
    r = subprocess.run(
        ["bun", "build", "scripts/build/ci.ts", "--target=bun"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"bun build ci.ts failed:\n{r.stderr[-500:]}"
