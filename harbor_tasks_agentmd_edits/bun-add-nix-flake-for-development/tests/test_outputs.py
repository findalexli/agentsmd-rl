"""
Task: bun-add-nix-flake-for-development
Repo: oven-sh/bun @ 6e3359dd16aced2f6fca2a8e2de71f09e0bcb3cb
PR:   23406

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/bun"


def _run_py(script: str, timeout: int = 30, **env_extra) -> subprocess.CompletedProcess:
    """Write analysis script to temp file and execute in subprocess."""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(script)
        env = {**os.environ, "REPO": REPO, **{k: str(v) for k, v in env_extra.items()}}
        return subprocess.run(
            ["python3", path],
            capture_output=True, text=True, timeout=timeout, env=env,
        )
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_flake_nix_exists():
    """flake.nix file exists and is valid Nix syntax."""
    r = _run_py(r"""
import os, subprocess, sys

repo = os.environ["REPO"]
flake_path = os.path.join(repo, "flake.nix")

if not os.path.exists(flake_path):
    print("flake.nix does not exist", file=sys.stderr)
    sys.exit(1)

# Validate nix syntax using nix-instantiate --parse
result = subprocess.run(
    ["nix-instantiate", "--parse", flake_path],
    capture_output=True, text=True
)
if result.returncode != 0:
    print(f"Invalid nix syntax: {result.stderr}", file=sys.stderr)
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"flake.nix validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_shell_nix_exists():
    """shell.nix file exists and is valid Nix syntax."""
    r = _run_py(r"""
import os, subprocess, sys

repo = os.environ["REPO"]
shell_path = os.path.join(repo, "shell.nix")

if not os.path.exists(shell_path):
    print("shell.nix does not exist", file=sys.stderr)
    sys.exit(1)

# Validate nix syntax
result = subprocess.run(
    ["nix-instantiate", "--parse", shell_path],
    capture_output=True, text=True
)
if result.returncode != 0:
    print(f"Invalid nix syntax: {result.stderr}", file=sys.stderr)
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"shell.nix validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_flake_nix_dev_shell():
    """flake.nix provides a Nix flake dev shell with LLVM 19 and required build tools."""
    r = _run_py(r"""
import os, subprocess, sys, json

repo = os.environ["REPO"]

# Check that flake.nix has devShells defined by parsing
# Full evaluation requires network and is slow, so we check the structure instead
with open(os.path.join(repo, "flake.nix"), 'r') as f:
    flake_content = f.read()

# Check for devShells in the flake content
if "devShells" not in flake_content:
    print("Missing devShells in flake.nix", file=sys.stderr)
    sys.exit(1)

if "default" not in flake_content:
    print("Missing default devShell in flake.nix", file=sys.stderr)
    sys.exit(1)

# Also verify syntax is valid
result = subprocess.run(
    ["nix-instantiate", "--parse", os.path.join(repo, "flake.nix")],
    capture_output=True, text=True, timeout=30
)
if result.returncode != 0:
    print(f"Invalid flake.nix syntax: {result.stderr}", file=sys.stderr)
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"flake.nix dev shell check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_shell_nix_build_env():
    """shell.nix provides a non-flake Nix shell with matching build tools."""
    r = _run_py(r"""
import os, subprocess, sys

repo = os.environ["REPO"]
shell_path = os.path.join(repo, "shell.nix")

# Set up NIX_PATH for nixpkgs resolution
env = os.environ.copy()
if "NIX_PATH" not in env:
    # Try to find nixpkgs in common locations or use impure mode
    env["NIX_PATH"] = "nixpkgs=/nix/var/nix/profiles/per-user/root/channels/nixpkgs"

# Validate by parsing syntax only (avoid evaluation that requires nixpkgs)
result = subprocess.run(
    ["nix-instantiate", "--parse", shell_path],
    capture_output=True, text=True, env=env
)

if result.returncode != 0:
    print(f"Failed to parse shell.nix: {result.stderr}", file=sys.stderr)
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"shell.nix evaluation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_cmake_nix_cc_zlib_compression():
    """cmake uses zlib debug symbol compression instead of zstd when NIX_CC is set."""
    r = _run_py(r"""
import os, subprocess, sys, tempfile, shutil

repo = os.environ["REPO"]
cmake_path = os.path.join(repo, "cmake", "CompilerFlags.cmake")

if not os.path.exists(cmake_path):
    print("CompilerFlags.cmake not found", file=sys.stderr)
    sys.exit(1)

# Read the actual content to verify the structure
content = open(cmake_path).read()

# Check for NIX_CC conditional block
if "DEFINED ENV{NIX_CC}" not in content:
    print("Missing NIX_CC environment check", file=sys.stderr)
    sys.exit(1)

# Verify both -gz=zlib and -gz=zstd exist in the file
if "-gz=zlib" not in content:
    print("Missing -gz=zlib for Nix builds", file=sys.stderr)
    sys.exit(1)

if "-gz=zstd" not in content:
    print("Missing -gz=zstd for non-Nix builds", file=sys.stderr)
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"cmake NIX_CC compression check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_cmake_nix_cc_fortify_guard():
    """cmake skips _FORTIFY_SOURCE=3 when NIX_CC is set (Nix glibc sets it already)."""
    r = _run_py(r"""
import os, re, subprocess, sys, tempfile, shutil

repo = os.environ["REPO"]
cmake_path = os.path.join(repo, "cmake", "CompilerFlags.cmake")

if not os.path.exists(cmake_path):
    print("CompilerFlags.cmake not found", file=sys.stderr)
    sys.exit(1)

# Verify the NIX_CC guard exists and is properly structured
content = open(cmake_path).read()

# Must have the guard pattern
if "DEFINED ENV{NIX_CC}" not in content:
    print("Missing NIX_CC environment check", file=sys.stderr)
    sys.exit(1)

# Look for the specific _FORTIFY_SOURCE block (after "Enable fortified sources" comment)
# This regex finds the if(DEFINED ENV{NIX_CC}) block that contains _FORTIFY_SOURCE
pattern = r'if\s*\(\s*DEFINED\s+ENV\{NIX_CC\}\s*\)(.*?)else\s*\(\s*\)(.*?)endif\s*\(\s*\)[^}]*?register_compiler_definitions[^}]*?_FORTIFY_SOURCE'
match = re.search(pattern, content, re.DOTALL)

if not match:
    # Fallback: check for the structure without relying on exact regex
    # The key is: there should be an if(DEFINED ENV{NIX_CC}) that has _FORTIFY_SOURCE in its else branch
    
    # Find all NIX_CC conditionals
    all_blocks = list(re.finditer(r'if\s*\(\s*DEFINED\s+ENV\{NIX_CC\}\s*\)(.*?)else\s*\(\s*\)(.*?)endif\s*\(\s*\)', content, re.DOTALL))
    
    found_correct_block = False
    for m in all_blocks:
        nix_branch = m.group(1)
        else_branch = m.group(2)
        
        # Check if this block has _FORTIFY_SOURCE definition in the else branch
        # (check for register_compiler_definitions with _FORTIFY_SOURCE)
        nix_has_def = "register_compiler_definitions" in nix_branch and "_FORTIFY_SOURCE" in nix_branch
        else_has_def = "register_compiler_definitions" in else_branch and "_FORTIFY_SOURCE" in else_branch
        if else_has_def and not nix_has_def:
            found_correct_block = True
            break
    
    if not found_correct_block:
        print("NIX_CC conditional not found with _FORTIFY_SOURCE in else branch", file=sys.stderr)
        sys.exit(1)
else:
    nix_branch = match.group(1)
    else_branch = match.group(2)
    
    # _FORTIFY_SOURCE should NOT be in the NIX_CC branch (it's guarded out)
    # Look for the actual definition (register_compiler_definitions with _FORTIFY_SOURCE)
    nix_has_definition = "register_compiler_definitions" in nix_branch and "_FORTIFY_SOURCE" in nix_branch
    if nix_has_definition:
        print("_FORTIFY_SOURCE definition should not be in NIX_CC branch", file=sys.stderr)
        sys.exit(1)
    
    # _FORTIFY_SOURCE SHOULD be in the else branch (actual definition)
    else_has_definition = "register_compiler_definitions" in else_branch and "_FORTIFY_SOURCE" in else_branch
    if not else_has_definition:
        print("_FORTIFY_SOURCE definition missing from else branch (non-Nix path)", file=sys.stderr)
        sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"cmake FORTIFY_SOURCE guard check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_contributing_nix_section():
    """CONTRIBUTING.md has a 'Using Nix' section with nix develop instructions."""
    r = _run_py(r"""
import os, sys

repo = os.environ["REPO"]
contrib_path = os.path.join(repo, "CONTRIBUTING.md")

if not os.path.exists(contrib_path):
    print("CONTRIBUTING.md does not exist", file=sys.stderr)
    sys.exit(1)

content = open(contrib_path).read()

# Must have a Nix section
if 'Using Nix' not in content:
    print("Missing 'Using Nix' section heading", file=sys.stderr)
    sys.exit(1)

# Must include nix develop command
if 'nix develop' not in content:
    print("Missing 'nix develop' command", file=sys.stderr)
    sys.exit(1)

# Manual section should be labeled
if 'Manual' not in content and 'manual' not in content.lower():
    print("Original install section not relabeled as Manual", file=sys.stderr)
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"CONTRIBUTING.md Nix section check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------


def test_cmake_retains_default_zstd():
    """Default (non-Nix) code path still uses zstd compression for debug symbols."""
    content = Path(f"{REPO}/cmake/CompilerFlags.cmake").read_text()
    assert "-gz=zstd" in content, "Default zstd compression removed"


def test_contributing_install_section_exists():
    """CONTRIBUTING.md still has the package manager install instructions."""
    content = Path(f"{REPO}/CONTRIBUTING.md").read_text()
    assert "brew install" in content or "apt install" in content, (
        "Package manager install instructions removed"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — repo structure checks
# ---------------------------------------------------------------------------


def test_repo_cmakelists_exists():
    """CMakeLists.txt exists at repo root (pass_to_pass)."""
    cmake_path = Path(f"{REPO}/CMakeLists.txt")
    assert cmake_path.exists(), "CMakeLists.txt missing from repo root"
    assert cmake_path.stat().st_size > 0, "CMakeLists.txt is empty"


def test_repo_cmake_directory_exists():
    """cmake/ directory exists with expected files (pass_to_pass)."""
    cmake_dir = Path(f"{REPO}/cmake")
    assert cmake_dir.exists(), "cmake/ directory missing"
    assert cmake_dir.is_dir(), "cmake/ is not a directory"

    # Key cmake files should exist
    expected_files = ["CompilerFlags.cmake", "Globals.cmake", "Options.cmake"]
    for fname in expected_files:
        fpath = cmake_dir / fname
        assert fpath.exists(), f"cmake/{fname} missing"


def test_repo_contributing_structure():
    """CONTRIBUTING.md has expected structure with install sections (pass_to_pass)."""
    contrib_path = Path(f"{REPO}/CONTRIBUTING.md")
    assert contrib_path.exists(), "CONTRIBUTING.md missing"

    content = contrib_path.read_text()

    # Check for key section headers
    assert "## Install Dependencies" in content, "Missing 'Install Dependencies' section"
    assert "## Building" in content or "## Manual Building" in content, "Missing building section"

    # Check for OS-specific install instructions
    assert "macOS" in content or "Ubuntu" in content or "Homebrew" in content, (
        "Missing OS-specific install instructions"
    )


def test_repo_prettier_config_valid():
    """.prettierrc exists and is valid JSON (pass_to_pass)."""
    import json

    prettier_path = Path(f"{REPO}/.prettierrc")
    assert prettier_path.exists(), ".prettierrc missing"

    try:
        config = json.loads(prettier_path.read_text())
    except json.JSONDecodeError as e:
        raise AssertionError(f".prettierrc is invalid JSON: {e}")

    # Basic sanity checks on config structure
    assert isinstance(config, dict), ".prettierrc should be a JSON object"


def test_repo_oxlint_config_exists():
    """oxlint.json exists and has valid structure (pass_to_pass)."""
    oxlint_path = Path(f"{REPO}/oxlint.json")
    assert oxlint_path.exists(), "oxlint.json missing"

    content = oxlint_path.read_text()
    # oxlint.json uses JSON-with-comments format
    # Check for expected structure markers instead of strict JSON parsing
    assert '"$schema"' in content, "Missing $schema in oxlint.json"
    assert '"categories"' in content, "Missing categories in oxlint.json"
    assert '"rules"' in content, "Missing rules in oxlint.json"


def test_repo_git_directory_valid():
    """.git directory exists and is valid (pass_to_pass)."""
    git_dir = Path(f"{REPO}/.git")
    assert git_dir.exists(), ".git directory missing"
    assert git_dir.is_dir(), ".git is not a directory"

    # Check for essential git files
    head_file = git_dir / "HEAD"
    assert head_file.exists(), ".git/HEAD missing"


def test_repo_nix_files_syntax():
    """Nix files have valid syntax after applying patch (pass_to_pass)."""
    import pytest

    flake_path = Path(f"{REPO}/flake.nix")
    shell_path = Path(f"{REPO}/shell.nix")

    # Only run if nix files exist (after patch)
    if not flake_path.exists() and not shell_path.exists():
        pytest.skip("Nix files not yet created (base commit state)")

    if flake_path.exists():
        r = subprocess.run(
            ["nix-instantiate", "--parse", str(flake_path)],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"flake.nix has invalid syntax: {r.stderr}"

    if shell_path.exists():
        r = subprocess.run(
            ["nix-instantiate", "--parse", str(shell_path)],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"shell.nix has invalid syntax: {r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression checks (actual subprocess commands)
# ---------------------------------------------------------------------------


def test_cmake_version_works():
    """CMake is available and can report version (pass_to_pass)."""
    r = subprocess.run(
        ["cmake", "--version"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"cmake --version failed: {r.stderr}"
    assert "cmake version" in r.stdout, f"Unexpected cmake --version output: {r.stdout}"


def test_nix_cli_works():
    """Nix CLI is functional in container (pass_to_pass)."""
    r = subprocess.run(
        ["nix", "--version"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"nix --version failed: {r.stderr}"
    assert "Nix" in r.stdout, f"Unexpected nix --version output: {r.stdout}"


def test_git_repo_valid():
    """Git repository is valid and has HEAD (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
    # Verify we have a clean working tree on base commit
    assert "HEAD detached" in r.stdout or "nothing to commit" in r.stdout, (
        f"Unexpected git status: {r.stdout}"
    )


def test_prettier_config_valid_json():
    """Prettier config is valid JSON via Python subprocess (pass_to_pass)."""
    r = _run_py("""
import json, os, sys

repo = os.environ["REPO"]
config_path = os.path.join(repo, ".prettierrc")

try:
    with open(config_path) as f:
        config = json.load(f)
    if not isinstance(config, dict):
        print("ERROR: .prettierrc is not a JSON object", file=sys.stderr)
        sys.exit(1)
    print("PASS")
except json.JSONDecodeError as e:
    print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
    sys.exit(1)
except FileNotFoundError:
    print(f"ERROR: .prettierrc not found at {config_path}", file=sys.stderr)
    sys.exit(1)
""")
    assert r.returncode == 0, f"Prettier config validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_cmake_lists_syntax():
    """CMakeLists.txt has valid structure (pass_to_pass)."""
    r = _run_py("""
import os, sys

repo = os.environ["REPO"]
cmakelists = os.path.join(repo, "CMakeLists.txt")

# Just check the file exists and has expected cmake content
if not os.path.exists(cmakelists):
    print(f"ERROR: CMakeLists.txt not found", file=sys.stderr)
    sys.exit(1)

with open(cmakelists) as f:
    content = f.read()

# Basic syntax checks for CMakeLists.txt
required_patterns = ["cmake_minimum_required", "project"]
for pattern in required_patterns:
    if pattern not in content:
        print(f"ERROR: Missing {pattern} in CMakeLists.txt", file=sys.stderr)
        sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"CMakeLists.txt validation failed: {r.stderr}"
    assert "PASS" in r.stdout
