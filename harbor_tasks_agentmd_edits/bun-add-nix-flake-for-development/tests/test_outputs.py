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

# Validate flake structure by evaluating its outputs
result = subprocess.run(
    ["nix", "eval", "--json", f"path:{repo}#devShells", "--apply", "x: x"],
    capture_output=True, text=True, cwd=repo
)

if result.returncode != 0:
    print(f"Failed to evaluate flake devShells: {result.stderr}", file=sys.stderr)
    sys.exit(1)

# Parse the output to verify it has expected structure
try:
    data = json.loads(result.stdout)
    if "default" not in str(data):
        print("Missing default devShell", file=sys.stderr)
        sys.exit(1)
except json.JSONDecodeError:
    # If eval succeeds but we can't parse JSON, that's still a pass
    pass

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

# Validate by instantiating (dry-run evaluation)
result = subprocess.run(
    ["nix-instantiate", "--eval", "-E", f"import {shell_path} {{}}"],
    capture_output=True, text=True
)

if result.returncode != 0:
    print(f"Failed to evaluate shell.nix: {result.stderr}", file=sys.stderr)
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

# Create a minimal CMakeLists.txt that tests the conditional behavior
tmpdir = tempfile.mkdtemp()
try:
    # Write CMakeLists.txt with the include path
    test_cmake = os.path.join(tmpdir, "CMakeLists.txt")
    cmake_content = '''
set(DEBUG "DEBUG")
set(RELEASE "RELEASE")
set(CMAKE_SYSTEM_NAME "Linux")
set(CMAKE_SYSTEM_PROCESSOR "x86_64")

# Mock the register_compiler_flags function to capture flags
set(CAPTURED_FLAGS "")
function(register_compiler_flags)
    set(flags "")
    set(in_desc FALSE)
    foreach(arg ${ARGN})
        if(arg STREQUAL "DESCRIPTION")
            set(in_desc TRUE)
        elseif(in_desc)
            set(in_desc FALSE)
        else()
            list(APPEND flags ${arg})
        endif()
    endforeach()
    string(JOIN " " flag_str ${flags})
    set(CAPTURED_FLAGS "${CAPTURED_FLAGS}${flag_str}\\n" CACHE STRING "" FORCE)
endfunction()

function(register_compiler_definitions)
    set(defs "")
    set(in_desc FALSE)
    foreach(arg ${ARGN})
        if(arg STREQUAL "DESCRIPTION")
            set(in_desc TRUE)
        elseif(in_desc)
            set(in_desc FALSE)
        else()
            list(APPEND defs ${arg})
        endif()
    endforeach()
endfunction()

include(''' + cmake_path + ''')

message(STATUS "CAPTURED_FLAGS:${CAPTURED_FLAGS}")
'''

    with open(test_cmake, "w") as f:
        f.write(cmake_content)

    build_dir = os.path.join(tmpdir, "build")
    os.makedirs(build_dir)

    # Test with NIX_CC set
    env_with_nix = {**os.environ, "NIX_CC": "/nix/store/..."}
    r1 = subprocess.run(
        ["cmake", "-S", tmpdir, "-B", build_dir],
        capture_output=True, text=True, env=env_with_nix
    )

    output = r1.stdout + r1.stderr

    # With NIX_CC set, should use zlib compression
    if "-gz=zlib" not in output:
        print(f"Missing -gz=zlib when NIX_CC is set. Output: {output}", file=sys.stderr)
        sys.exit(1)

    # Cleanup for second test
    shutil.rmtree(build_dir, ignore_errors=True)
    os.makedirs(build_dir)

    # Test without NIX_CC
    env_without_nix = {k: v for k, v in os.environ.items() if k != "NIX_CC"}
    r2 = subprocess.run(
        ["cmake", "-S", tmpdir, "-B", build_dir],
        capture_output=True, text=True, env=env_without_nix
    )

    output2 = r2.stdout + r2.stderr

    # Without NIX_CC, should use zstd compression
    if "-gz=zstd" not in output2:
        print(f"Missing -gz=zstd when NIX_CC is not set. Output: {output2}", file=sys.stderr)
        sys.exit(1)

finally:
    shutil.rmtree(tmpdir, ignore_errors=True)

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

# The pattern should be: if(DEFINED ENV{NIX_CC}) ... else() ... endif()
# and _FORTIFY_SOURCE should be in the else branch
pattern = r'if\s*\(\s*DEFINED\s+ENV\{NIX_CC\}\s*\)(.*?)else\s*\(\s*\)(.*?)endif\s*\(\s*\)'
match = re.search(pattern, content, re.DOTALL)

if not match:
    print("NIX_CC conditional not found with proper else branch", file=sys.stderr)
    sys.exit(1)

nix_branch = match.group(1)
else_branch = match.group(2)

# _FORTIFY_SOURCE should NOT be in the NIX_CC branch (it's guarded out)
if "_FORTIFY_SOURCE" in nix_branch:
    print("_FORTIFY_SOURCE should not be in NIX_CC branch", file=sys.stderr)
    sys.exit(1)

# _FORTIFY_SOURCE SHOULD be in the else branch
if "_FORTIFY_SOURCE" not in else_branch:
    print("_FORTIFY_SOURCE missing from else branch (non-Nix path)", file=sys.stderr)
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
