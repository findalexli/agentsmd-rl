#!/usr/bin/env python3
"""Tests for moby/moby PR #52262: daemon/libnetwork/ns refactoring.

This PR refactors the namespace initialization to use sync.OnceValues instead
of global state with sync.Once.
"""

import os
import subprocess
import sys

REPO = "/workspace/moby"
NS_PACKAGE = "daemon/libnetwork/ns"


def test_nshandle_function_exists():
    """NsHandle() function should exist and return netns.NsHandle type."""
    init_linux = os.path.join(REPO, NS_PACKAGE, "init_linux.go")
    with open(init_linux, 'r') as f:
        content = f.read()

    # Check that NsHandle function exists and has correct signature
    import re
    # Look for: func NsHandle() netns.NsHandle
    nshandle_pattern = r'func\s+NsHandle\s*\(\s*\)\s+netns\.NsHandle'
    assert re.search(nshandle_pattern, content), \
        "NsHandle() function should exist with signature: func NsHandle() netns.NsHandle"

    # Check that it calls initNamespace() and returns the namespace handle
    # The implementation should extract just the namespace from initNamespace()
    assert "initNamespace()" in content, "NsHandle should call initNamespace()"
    # Should return ns handle (first return value from initNamespace)
    assert "ns, _ := initNamespace()" in content or "ns, _ = initNamespace()" in content, \
        "NsHandle should extract namespace handle from initNamespace()"
    # Should return ns
    func_match = re.search(r'func NsHandle\(\) netns\.NsHandle \{([^}]+)\}', content, re.DOTALL)
    if func_match:
        func_body = func_match.group(1)
        assert "return ns" in func_body, "NsHandle should return the namespace handle"


def test_parsehandlerint_removed():
    """ParseHandlerInt() function should be removed."""
    init_linux = os.path.join(REPO, NS_PACKAGE, "init_linux.go")
    with open(init_linux, 'r') as f:
        content = f.read()

    # Should not contain ParseHandlerInt
    assert "ParseHandlerInt" not in content, "ParseHandlerInt should be removed"


def test_sync_oncevalues_used():
    """sync.OnceValues should be used for initialization."""
    init_linux = os.path.join(REPO, NS_PACKAGE, "init_linux.go")
    with open(init_linux, 'r') as f:
        content = f.read()

    # Should use sync.OnceValues
    assert "sync.OnceValues" in content, "Should use sync.OnceValues"
    assert "initNamespace" in content, "Should have initNamespace variable"


def test_netlink_socket_timeout_is_const():
    """NetlinkSocketsTimeout should be a const, not a var."""
    init_linux = os.path.join(REPO, NS_PACKAGE, "init_linux.go")
    with open(init_linux, 'r') as f:
        content = f.read()

    # Find the declaration of NetlinkSocketsTimeout
    lines = content.split('\n')
    found = False
    for i, line in enumerate(lines):
        if 'NetlinkSocketsTimeout' in line and 'time.Second' in line:
            # Check if it's a const declaration
            # Look for "const" on the same line or in the previous line (for const block)
            if line.strip().startswith('const '):
                found = True
                break
            # Check previous line for const block
            for j in range(max(0, i-5), i):
                if lines[j].strip() == 'const' or lines[j].strip().startswith('const ('):
                    found = True
                    break
            break

    assert found, "NetlinkSocketsTimeout should be declared as a const"

    # Should NOT have "var" block containing NetlinkSocketsTimeout at the top level
    import re
    var_block_pattern = r'var\s*\([^)]*NetlinkSocketsTimeout[^)]*\)'
    assert not re.search(var_block_pattern, content, re.DOTALL), \
        "NetlinkSocketsTimeout should not be in a var block"


def test_error_handling_with_error():
    """Error handling should use WithError() instead of Errorf with %v."""
    init_linux = os.path.join(REPO, NS_PACKAGE, "init_linux.go")
    with open(init_linux, 'r') as f:
        content = f.read()

    # Should use WithError for structured logging
    assert "WithError(err)" in content, "Should use WithError(err) for error logging"


def test_windows_stub_removed():
    """Windows stub file should be removed."""
    windows_file = os.path.join(REPO, NS_PACKAGE, "init_windows.go")
    assert not os.path.exists(windows_file), "init_windows.go should be removed"


def test_interface_uses_nshandle():
    """interface_linux.go should use ns.NsHandle() instead of ns.ParseHandlerInt()."""
    interface_linux = os.path.join(REPO, "daemon/libnetwork/osl/interface_linux.go")
    with open(interface_linux, 'r') as f:
        content = f.read()

    # Should use NsHandle
    assert "ns.NsHandle()" in content, "Should use ns.NsHandle()"

    # Should NOT use ParseHandlerInt
    assert "ns.ParseHandlerInt()" not in content, "Should not use ParseHandlerInt()"


def test_code_compiles():
    """The code should compile without errors."""
    r = subprocess.run(
        ["go", "build", "./daemon/libnetwork/ns/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Code does not compile:\n{r.stderr}"


def test_go_vet_passes():
    """go vet should pass on the modified package."""
    r = subprocess.run(
        ["go", "vet", "./daemon/libnetwork/ns/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert r.returncode == 0, f"go vet failed:\n{r.stderr}"


def test_package_tests_pass():
    """Tests in the ns package should pass."""
    r = subprocess.run(
        ["go", "test", "-v", "-count=1", "./daemon/libnetwork/ns/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Package tests failed:\n{r.stderr[-1000:]}"


def test_osl_package_compiles():
    """The osl package that uses ns should compile."""
    r = subprocess.run(
        ["go", "build", "./daemon/libnetwork/osl/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"osl package does not compile:\n{r.stderr}"


def test_go_mod_verify():
    """Go modules should be verified (pass_to_pass)."""
    r = subprocess.run(
        ["go", "mod", "verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert r.returncode == 0, f"go mod verify failed:\n{r.stderr}"


def test_gofmt_libnetwork():
    """Modified libnetwork files should be properly formatted (pass_to_pass)."""
    # Check formatting on the modified files
    modified_files = [
        "daemon/libnetwork/ns/init_linux.go",
        "daemon/libnetwork/osl/interface_linux.go",
    ]
    for f in modified_files:
        filepath = os.path.join(REPO, f)
        if os.path.exists(filepath):
            r = subprocess.run(
                ["gofmt", "-l", filepath],
                capture_output=True,
                text=True,
                timeout=30
            )
            assert r.returncode == 0, f"gofmt failed on {f}: {r.stderr}"
            assert r.stdout.strip() == "", f"File {f} is not properly formatted"


def test_vet_libnetwork_packages():
    """go vet should pass on ns and osl packages (pass_to_pass)."""
    r = subprocess.run(
        ["go", "vet", "./daemon/libnetwork/ns/...", "./daemon/libnetwork/osl/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"go vet failed:\n{r.stderr}"
