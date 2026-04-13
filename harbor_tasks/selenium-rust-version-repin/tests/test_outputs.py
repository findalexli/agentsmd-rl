"""Test outputs for PR #17320: Fix pre-release dependency update command

This PR ensures that after updating the Rust version, the cargo dependencies
are automatically repinned to prevent Bazel lockfile conflicts.
"""

import subprocess
import os
import re

REPO = "/workspace/selenium"


def test_rust_rake_file_contains_reenable():
    """Test that rust.rake contains the reenable call (f2p test)."""
    rake_file = os.path.join(REPO, "rake_tasks", "rust.rake")
    with open(rake_file, 'r') as f:
        content = f.read()

    # Check for the reenable call - this is the key fix
    assert "Rake::Task['rust:update'].reenable" in content, \
        "rust.rake should contain reenable call for rust:update task"


def test_rust_rake_file_contains_invoke_after_version():
    """Test that rust.rake invokes rust:update after version update (f2p test)."""
    rake_file = os.path.join(REPO, "rake_tasks", "rust.rake")
    with open(rake_file, 'r') as f:
        content = f.read()

    # Check for the invoke call after version task
    assert "Rake::Task['rust:update'].invoke" in content, \
        "rust.rake should invoke rust:update after version update"


def test_rust_rake_has_comment_explaining_fix():
    """Test that the fix has explanatory comment (f2p test)."""
    rake_file = os.path.join(REPO, "rake_tasks", "rust.rake")
    with open(rake_file, 'r') as f:
        content = f.read()

    # Check for the explanatory comment about repinning
    assert "Repin cargo immediately after updating the version" in content, \
        "rust.rake should have comment explaining the repin fix"


def test_rust_rake_comment_mentions_cargo_bazel_repin():
    """Test that comment mentions CARGO_BAZEL_REPIN (f2p test)."""
    rake_file = os.path.join(REPO, "rake_tasks", "rust.rake")
    with open(rake_file, 'r') as f:
        content = f.read()

    # Check for mention of CARGO_BAZEL_REPIN in the comment
    assert "CARGO_BAZEL_REPIN" in content, \
        "rust.rake comment should mention CARGO_BAZEL_REPIN"


def test_rust_rake_comment_mentions_mid_evaluation_conflict():
    """Test that comment explains mid-evaluation conflict (f2p test)."""
    rake_file = os.path.join(REPO, "rake_tasks", "rust.rake")
    with open(rake_file, 'r') as f:
        content = f.read()

    # Check for explanation of mid-evaluation conflict
    assert "mid-evaluation" in content or "file-hash conflict" in content, \
        "rust.rake comment should explain the mid-evaluation file-hash conflict"


def test_workflow_simplified_command():
    """Test that workflow uses simplified update command (f2p test)."""
    workflow_file = os.path.join(REPO, ".github", "workflows", "pre-release.yml")

    if not os.path.exists(workflow_file):
        # Skip if workflow file doesn't exist
        return

    with open(workflow_file, 'r') as f:
        content = f.read()

    # The fix simplifies the command - should just be language:update without conditional rust:update
    # Look for the simplified pattern without the ternary operator
    if "language:update" in content:
        # Check that it does NOT have the old complex pattern with ternary
        old_pattern = "needs.parse-tag.outputs.language == 'all' && ' && ./go rust:update'"
        assert old_pattern not in content, \
            "workflow should not contain the old complex conditional rust:update pattern"


def test_rust_update_task_defined():
    """Test that rust:update task is defined in the Rakefile (p2p test)."""
    rake_file = os.path.join(REPO, "rake_tasks", "rust.rake")
    with open(rake_file, 'r') as f:
        content = f.read()

    # Check that rust:update task is defined
    assert "task :update" in content, \
        "rust:update task should be defined"


def test_version_task_exists():
    """Test that version task exists in rust.rake (p2p test)."""
    rake_file = os.path.join(REPO, "rake_tasks", "rust.rake")
    with open(rake_file, 'r') as f:
        content = f.read()

    # Check that version task is defined
    assert "task :version" in content, \
        "rust:version task should be defined"


def test_rake_file_valid_ruby_syntax():
    """Test that rust.rake has valid Ruby syntax (p2p test)."""
    rake_file = os.path.join(REPO, "rake_tasks", "rust.rake")

    # Use ruby -c to check syntax
    result = subprocess.run(
        ["ruby", "-c", rake_file],
        capture_output=True, text=True
    )
    assert result.returncode == 0, \
        f"rust.rake has invalid Ruby syntax: {result.stderr}"


def test_rust_bazel_build():
    """Repo's Rust Bazel build passes (pass_to_pass)."""
    r = subprocess.run(
        ["bazel", "build", "//rust:selenium-manager"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Rust Bazel build failed:\n{r.stderr[-500:]}"


def test_rust_unit_fmt():
    """Repo's Rust code formatting check passes (pass_to_pass)."""
    r = subprocess.run(
        ["bazel", "test", "//rust:unit-fmt"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Rust format check failed:\n{r.stderr[-500:]}"


def test_bazel_query_rust_target():
    """Bazel can query Rust target (pass_to_pass)."""
    r = subprocess.run(
        ["bazel", "query", "//rust:selenium-manager"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Bazel query failed:\n{r.stderr[-500:]}"
    assert "//rust:selenium-manager" in r.stdout, "Expected target not found in query output"


def test_rust_rake_file_has_cargo_toml_reference():
    """rust.rake references Cargo.toml (p2p test)."""
    rake_file = os.path.join(REPO, "rake_tasks", "rust.rake")
    with open(rake_file, 'r') as f:
        content = f.read()

    # Check that the rake file references Cargo.toml
    assert "Cargo.toml" in content, \
        "rust.rake should reference Cargo.toml for version updates"


def test_reenable_comes_before_invoke():
    """Test that reenable is called before invoke (f2p test)."""
    rake_file = os.path.join(REPO, "rake_tasks", "rust.rake")
    with open(rake_file, 'r') as f:
        content = f.read()

    # Find positions
    reenable_pos = content.find("Rake::Task['rust:update'].reenable")
    invoke_pos = content.find("Rake::Task['rust:update'].invoke")

    assert reenable_pos != -1, "reenable call should exist"
    assert invoke_pos != -1, "invoke call should exist"
    assert reenable_pos < invoke_pos, \
        "reenable should be called before invoke"


def test_invoke_in_version_task_block():
    """Test that invoke is inside the version task block (f2p test)."""
    rake_file = os.path.join(REPO, "rake_tasks", "rust.rake")
    with open(rake_file, 'r') as f:
        content = f.read()

    # Extract the version task block
    version_match = re.search(
        r"task :version.*?do.*?_task, arguments\|(.*?)end\s*$",
        content,
        re.DOTALL
    )

    if version_match:
        block_content = version_match.group(1)
        assert "Rake::Task['rust:update'].invoke" in block_content, \
            "invoke should be inside the version task block"
    else:
        # Fallback: just check invoke exists somewhere
        assert "Rake::Task['rust:update'].invoke" in content, \
            "invoke call should exist in the file"


def test_pre_release_workflow_yaml_valid():
    """Repo's pre-release workflow YAML is valid (pass_to_pass)."""
    workflow_file = os.path.join(REPO, ".github", "workflows", "pre-release.yml")
    r = subprocess.run(
        ["python3", "-c", f"import yaml; yaml.safe_load(open('{workflow_file}')); print('YAML valid')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"YAML validation failed:\n{r.stderr}"


def test_rakefile_valid_ruby_syntax():
    """Repo's main Rakefile has valid Ruby syntax (pass_to_pass)."""
    rakefile = os.path.join(REPO, "Rakefile")
    r = subprocess.run(
        ["ruby", "-c", rakefile],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Rakefile has invalid Ruby syntax:\n{r.stderr}"


def test_bazel_analyze_rust_target():
    """Bazel can analyze Rust target without building (pass_to_pass)."""
    r = subprocess.run(
        ["bazel", "build", "--nobuild", "//rust:selenium-manager"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Bazel analysis failed:\n{r.stderr[-500:]}"


def test_bazel_query_rust_targets():
    """Bazel can query all Rust targets (pass_to_pass)."""
    r = subprocess.run(
        ["bazel", "query", "//rust/..."],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Bazel query failed:\n{r.stderr[-500:]}"
    assert "//rust:selenium-manager" in r.stdout, "Expected rust targets not found in query output"


# ===== Enrichment: Additional p2p tests using repo CI commands =====


def test_ruby_syntax_bazel_rake():
    """Repo's bazel.rake has valid Ruby syntax (pass_to_pass)."""
    rake_file = os.path.join(REPO, "rake_tasks", "bazel.rake")
    r = subprocess.run(
        ["ruby", "-c", rake_file],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"bazel.rake has invalid Ruby syntax:\n{r.stderr}"


def test_bazel_analyze_rust_library():
    """Bazel can analyze Rust library target without building (pass_to_pass)."""
    r = subprocess.run(
        ["bazel", "build", "--nobuild", "//rust:selenium_manager"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Bazel analysis of rust library failed:\n{r.stderr[-500:]}"


def test_rust_cargo_toml_valid():
    """Rust Cargo.toml has valid TOML syntax (pass_to_pass)."""
    cargo_toml = os.path.join(REPO, "rust", "Cargo.toml")
    r = subprocess.run(
        ["python3", "-c", f"import tomllib; tomllib.load(open('{cargo_toml}', 'rb')); print('TOML valid')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo.toml has invalid TOML syntax:\n{r.stderr}"


def test_bazel_query_rust_library_target():
    """Bazel can query Rust library target (pass_to_pass)."""
    r = subprocess.run(
        ["bazel", "query", "//rust:selenium_manager"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Bazel query for library target failed:\n{r.stderr[-500:]}"
    assert "//rust:selenium_manager" in r.stdout, "Expected library target not found in query output"


def test_bazel_version():
    """Bazel version command works (pass_to_pass)."""
    r = subprocess.run(
        ["bazel", "version"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Bazel version failed:\n{r.stderr[-500:]}"
    assert "Build label" in r.stdout, "Expected version info in output"
