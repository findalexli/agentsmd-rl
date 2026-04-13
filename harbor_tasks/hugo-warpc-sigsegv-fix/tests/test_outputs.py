"""
Test suite for Hugo warpc lazyDispatcher SIGSEGV fix.

Tests verify that Close() doesn't panic when a lazyDispatcher fails to start.
The bug was that `started=true` was set unconditionally, so Close() would
try to call Close() on a nil dispatcher.
"""

import subprocess
import sys
import os

REPO = "/workspace/hugo"


def test_code_compiles():
    """Verify the code compiles without errors."""
    result = subprocess.run(
        ["go", "build", "./internal/warpc/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Compilation failed:\n{result.stderr}"


def test_lazy_dispatcher_started_flag_only_set_on_success():
    """
    Verify that lazyDispatcher.start() only sets started=true when Start() succeeds.
    This is the core fix for the SIGSEGV bug.

    Test by checking that the code has the correct logic:
    - started = true should be inside an 'if d.startErr == nil' block
    """
    warpc_path = os.path.join(REPO, "internal/warpc/warpc.go")
    with open(warpc_path, "r") as f:
        content = f.read()

    # The fix wraps 'd.started = true' inside a 'if d.startErr == nil' check
    # Check that this pattern exists in the code
    assert "if d.startErr == nil" in content, (
        "Missing guard check for startErr in lazyDispatcher.start(). "
        "The fix should only set started=true when Start() succeeds."
    )

    # Verify the pattern where started=true is guarded
    # Look for the specific fix pattern in the start method
    import re

    # Find the startOnce.Do block and verify the structure
    # The correct fix has: if d.startErr == nil { d.started = true ... }
    pattern = r'd\.startOnce\.Do\(func\(\)\s*\{[^}]*d\.dispatcher, d\.startErr = Start\[[^]]+\]\(d\.opts\)'
    match = re.search(pattern, content, re.DOTALL)
    assert match, "Could not find startOnce.Do block with Start call"

    # After the Start call, we should see the guard check
    start_once_block_start = match.end()
    rest_of_block = content[start_once_block_start:]

    # Find the closing of the startOnce.Do block (the next unmatched })
    # Simple approach: find the first 'if d.startErr == nil' after the Start call
    # and ensure it comes before 'd.started = true'
    start_to_end = content[match.start():]

    # The fix: started=true should be inside an if d.startErr == nil block
    # Search for the pattern: 'if d.startErr == nil' followed by 'd.started = true'
    guard_pattern = r'if\s+d\.startErr\s*==\s*nil\s*\{[^}]*d\.started\s*=\s*true'
    guard_match = re.search(guard_pattern, start_to_end, re.DOTALL)

    assert guard_match, (
        "The 'd.started = true' assignment must be guarded by 'if d.startErr == nil'. "
        "This is the core fix - without it, Close() will SIGSEGV on nil dispatcher."
    )


def test_close_handles_failed_start():
    """
    Verify that Dispatchers.Close() properly checks started flag.
    When start fails, started should be false, so Close() won't try to close nil.

    This test verifies the structural correctness of the fix by checking that
    the close method uses the 'started' guard before accessing dispatcher.
    """
    warpc_path = os.path.join(REPO, "internal/warpc/warpc.go")
    with open(warpc_path, "r") as f:
        content = f.read()

    # The Close() method should check d.katex.started before calling d.katex.dispatcher.Close()
    # This pattern should exist in the code
    assert "if d.katex.started" in content, (
        "Close() must check d.katex.started before accessing dispatcher"
    )
    assert "if d.webp.started" in content, (
        "Close() must check d.webp.started before accessing dispatcher"
    )

    # Verify the pattern: check started, then access dispatcher.Close()
    import re

    katex_pattern = r'if\s+d\.katex\.started\s*\{[^}]*d\.katex\.dispatcher\.Close\(\)'
    katex_match = re.search(katex_pattern, content, re.DOTALL)
    assert katex_match, (
        "Close() must check d.katex.started before calling d.katex.dispatcher.Close(). "
        "Without the fix, this would SIGSEGV when dispatcher is nil."
    )

    webp_pattern = r'if\s+d\.webp\.started\s*\{[^}]*d\.webp\.dispatcher\.Close\(\)'
    webp_match = re.search(webp_pattern, content, re.DOTALL)
    assert webp_match, (
        "Close() must check d.webp.started before calling d.webp.dispatcher.Close(). "
        "Without the fix, this would SIGSEGV when dispatcher is nil."
    )


def test_existing_unit_tests_pass():
    """
    Run the existing warpc package tests to ensure no regressions.
    These are pass-to-pass tests - they should work both before and after the fix.
    """
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestKatex|TestGreet", "./internal/warpc/", "-count=1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    # Tests might fail for other reasons (WASM availability), but they shouldn't panic/SIGSEGV
    # We're primarily checking that the tests don't crash due to our changes
    # If tests fail due to WASM issues, that's OK - we're testing the fix structure above
    assert "SIGSEGV" not in result.stderr, (
        f"Tests crashed with SIGSEGV - the fix may not be working:\n{result.stderr}"
    )
    assert "panic" not in result.stderr.lower() or "runtime error: invalid memory address" not in result.stderr, (
        f"Tests panicked - the fix may not be working:\n{result.stderr}"
    )


def test_no_unconditional_started_assignment():
    """
    Verify that 'd.started = true' is NOT assigned unconditionally in startOnce.Do.
    The bug was exactly this - it should only be set when startErr == nil.
    """
    warpc_path = os.path.join(REPO, "internal/warpc/warpc.go")
    with open(warpc_path, "r") as f:
        content = f.read()

    import re

    # Find the start() method
    start_method_pattern = r'func \(d \*lazyDispatcher\[Q, R\]\) start\(\) \(Dispatcher\[Q, R\], error\) \{'
    match = re.search(start_method_pattern, content)
    assert match, "Could not find lazyDispatcher.start() method"

    # Extract the method body (from { to the matching })
    start_idx = match.end()
    brace_count = 0
    end_idx = start_idx
    for i, char in enumerate(content[start_idx:]):
        if char == '{':
            brace_count += 1
        elif char == '}':
            if brace_count == 0:
                end_idx = start_idx + i
                break
            brace_count -= 1

    method_body = content[start_idx:end_idx]

    # Inside startOnce.Do, 'd.started = true' should NOT appear unconditionally
    # It should only appear inside an if block

    # Find startOnce.Do block
    do_pattern = r'd\.startOnce\.Do\(func\(\)\s*\{'
    do_match = re.search(do_pattern, method_body)
    assert do_match, "Could not find startOnce.Do block in start() method"

    # Extract the Do block content
    do_start = do_match.end()
    brace_count = 1  # Already inside the opening {
    do_end = do_start
    for i, char in enumerate(method_body[do_start:]):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                do_end = do_start + i
                break

    do_block = method_body[do_start:do_end]

    # Check that 'd.started = true' is NOT in the do_block outside of an if statement
    # First, remove any if blocks to see if there are unconditional assignments
    lines = do_block.split('\n')
    in_if_block = False
    if_brace_depth = 0

    for line in lines:
        stripped = line.strip()

        # Track if we're inside an if block
        if 'if ' in stripped and stripped.endswith('{'):
            in_if_block = True
            if_brace_depth = 1
            continue

        if in_if_block:
            if '{' in stripped:
                if_brace_depth += stripped.count('{')
            if '}' in stripped:
                if_brace_depth -= stripped.count('}')
            if if_brace_depth <= 0:
                in_if_block = False
            continue

        # Outside if block - d.started = true should NOT appear
        if 'd.started = true' in stripped:
            assert False, (
                "Found unconditional 'd.started = true' in startOnce.Do block. "
                "This is the bug! It should only be set inside 'if d.startErr == nil' block."
            )


# ============================================================================
# Pass-to-Pass Tests: Repo CI/CD checks that should pass on both base and fix
# ============================================================================

def test_repo_go_vet():
    """Repo's go vet passes on the warpc package (pass_to_pass)."""
    result = subprocess.run(
        ["go", "vet", "./internal/warpc/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"go vet failed:\n{result.stderr}"


def test_repo_gofmt():
    """Repo's gofmt check passes (pass_to_pass)."""
    result = subprocess.run(
        ["gofmt", "-l", "./internal/warpc/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    # gofmt returns 0 even if it finds issues, but prints the files
    assert result.stdout.strip() == "", f"gofmt found issues:\n{result.stdout}"


def test_repo_warpc_build():
    """Repo's warpc package builds successfully (pass_to_pass)."""
    result = subprocess.run(
        ["go", "build", "./internal/warpc/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"


def test_repo_unit_tests_warpc():
    """
    Repo warpc package unit tests pass (pass_to_pass).
    Runs tests that don't require external dependencies like WASM.
    """
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestKatex|TestGreet|TestDispatcher", "./internal/warpc/", "-count=1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    # Tests might skip due to WASM not being available, but they shouldn't fail
    assert result.returncode == 0, f"Unit tests failed:\n{result.stdout}\n{result.stderr}"


def test_repo_go_mod_tidy():
    """Repo's go.mod is tidy (pass_to_pass)."""
    result = subprocess.run(
        ["go", "mod", "tidy", "-diff"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    # -diff flag returns 0 if no changes needed, non-zero if changes needed
    assert result.returncode == 0, f"go mod tidy would make changes:\n{result.stdout}"


def test_repo_staticcheck():
    """Repo's staticcheck passes on warpc package (pass_to_pass)."""
    # Install staticcheck if not already installed
    subprocess.run(
        ["go", "install", "honnef.co/go/tools/cmd/staticcheck@latest"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    # staticcheck is installed to $GOPATH/bin or $HOME/go/bin
    result = subprocess.run(
        ["staticcheck", "./internal/warpc/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"staticcheck failed:\n{result.stderr}\n{result.stdout}"


def test_repo_check_sh():
    """
    Repo's check.sh script passes on warpc package (pass_to_pass).
    This runs gofmt, staticcheck, and tests as per Hugo's CI.
    """
    result = subprocess.run(
        ["./check.sh", "./internal/warpc/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"check.sh failed:\n{result.stdout}\n{result.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
