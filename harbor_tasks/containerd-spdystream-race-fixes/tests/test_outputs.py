"""Tests for containerd spdystream race condition fix.

This task involves updating moby/spdystream from v0.2.0 to v0.5.0
to fix race conditions and goroutine leaks in the spdystream library.
"""

import subprocess
import os
import re

REPO = "/workspace/containerd"
CONNECTION_GO = f"{REPO}/vendor/github.com/moby/spdystream/connection.go"
STREAM_GO = f"{REPO}/vendor/github.com/moby/spdystream/stream.go"
GO_MOD = f"{REPO}/go.mod"


def test_spdystream_version_updated():
    """Fail-to-pass: go.mod must reference moby/spdystream v0.5.0."""
    with open(GO_MOD, 'r') as f:
        content = f.read()

    # Check for the new version
    assert 'github.com/moby/spdystream v0.5.0' in content, \
        "go.mod must update moby/spdystream to v0.5.0"

    # Ensure old version is not present
    assert 'github.com/moby/spdystream v0.2.0' not in content, \
        "go.mod should not contain old version v0.2.0"


def test_pingLock_protects_pingChans():
    """Fail-to-pass: pingLock must protect both pingId and pingChans.

    The fix renames pingIdLock to pingLock and uses it to protect
    both pingId and pingChans in a critical section.
    """
    with open(CONNECTION_GO, 'r') as f:
        content = f.read()

    # Check that pingLock is used (not just pingIdLock)
    assert 'pingLock' in content, \
        "connection.go must use pingLock for synchronization"

    # Check that comment explains the lock protection
    assert 'pingLock protects pingChans and pingId' in content, \
        "pingLock comment must explain what it protects"

    # Verify pingChans is accessed under lock in Ping()
    # Look for pattern where pingChans is written inside lock scope
    ping_pattern = r's\.pingLock\.Lock\(\).*s\.pingChans\[pid\].*pingChan.*s\.pingLock\.Unlock\(\)'
    assert re.search(ping_pattern, content, re.DOTALL), \
        "pingChans[pid] must be written under pingLock protection"


def test_pingChans_deletion_under_lock():
    """Fail-to-pass: Deleting from pingChans must be under lock protection.

    The fix wraps the delete in a deferred function that properly locks.
    """
    with open(CONNECTION_GO, 'r') as f:
        content = f.read()

    # Check for deferred delete with proper locking
    deferred_delete_pattern = r'defer func\(\)\s*{\s*s\.pingLock\.Lock\(\)\s*delete\(s\.pingChans, pid\)\s*s\.pingLock\.Unlock\(\)\s*}\(\)'
    assert re.search(deferred_delete_pattern, content, re.DOTALL), \
        "delete from pingChans must be done under pingLock in deferred function"


def test_handlePingFrame_uses_local_pingId():
    """Fail-to-pass: handlePingFrame must read pingId and pingChans under lock.

    The fix reads both values under lock before using them, avoiding race.
    """
    with open(CONNECTION_GO, 'r') as f:
        content = f.read()

    # Look for the fixed pattern: reading pingId and pingChans under lock
    handle_ping_pattern = r's\.pingLock\.Lock\(\)\s*pingId := s\.pingId\s*pingChan, pingOk := s\.pingChans\[frame\.Id\]\s*s\.pingLock\.Unlock\(\)'
    assert re.search(handle_ping_pattern, content, re.DOTALL), \
        "handlePingFrame must read pingId and pingChans under lock"


def test_shutdown_uses_timer_not_afterfunc():
    """Fail-to-pass: shutdown must use time.NewTimer with defer Stop, not AfterFunc.

    The old code used time.AfterFunc which creates a goroutine that might leak.
    The fix uses time.NewTimer with proper cleanup via defer timer.Stop().
    """
    with open(CONNECTION_GO, 'r') as f:
        content = f.read()

    # Check that time.AfterFunc is NOT used (it's the old buggy pattern)
    assert 'time.AfterFunc' not in content, \
        "connection.go must not use time.AfterFunc (causes goroutine leaks)"

    # Check that NewTimer with defer Stop is used in shutdown
    shutdown_timer_pattern = r'timer := time\.NewTimer\(duration\)\s*defer timer\.Stop\(\)'
    assert re.search(shutdown_timer_pattern, content, re.DOTALL), \
        "shutdown must use NewTimer with defer Stop for proper cleanup"

    # Check for select pattern with timer.C
    assert re.search(r'select\s*{\s*case s\.shutdownChan <- err:', content, re.DOTALL), \
        "shutdown must use select with timer to prevent blocking"


def test_shutdown_timeout_uses_proper_timer():
    """Fail-to-pass: shutdown closeTimeout handling must use proper timer."""
    with open(CONNECTION_GO, 'r') as f:
        content = f.read()

    # Check that time.After is not used (old pattern)
    # Note: there might be legitimate uses, so we check specific patterns

    # Verify the shutdown function uses NewTimer for closeTimeout
    # Look for the specific pattern in the shutdown function
    shutdown_timeout_pattern = r'if closeTimeout > time\.Duration\(0\)\s*{\s*timer := time\.NewTimer\(closeTimeout\)\s*defer timer\.Stop\(\)\s*timeout = timer\.C\s*}'
    assert re.search(shutdown_timeout_pattern, content, re.DOTALL), \
        "shutdown must use NewTimer with Stop for closeTimeout"


def test_wait_uses_proper_timer():
    """Fail-to-pass: Wait must use NewTimer with defer Stop, not After."""
    with open(CONNECTION_GO, 'r') as f:
        content = f.read()

    # Check Wait function uses proper timer
    wait_timer_pattern = r'func \(s \*Connection\) Wait\(waitTimeout time\.Duration\).*?if waitTimeout > time\.Duration\(0\)\s*{\s*timer := time\.NewTimer\(waitTimeout\)\s*defer timer\.Stop\(\)\s*timeout = timer\.C\s*}'
    assert re.search(wait_timer_pattern, content, re.DOTALL), \
        "Wait must use NewTimer with defer Stop for waitTimeout"


def test_isfinished_uses_finishLock():
    """Fail-to-pass: IsFinished must use finishLock to avoid race.

    The fix adds proper locking when reading the finished field.
    """
    with open(STREAM_GO, 'r') as f:
        content = f.read()

    # Check that IsFinished uses lock
    isfinished_pattern = r'func \(s \*Stream\) IsFinished\(\) bool\s*{\s*s\.finishLock\.Lock\(\)\s*defer s\.finishLock\.Unlock\(\)\s*return s\.finished\s*}'
    assert re.search(isfinished_pattern, content, re.DOTALL), \
        "IsFinished must use finishLock.Lock/Unlock to protect finished field"


def test_vendor_connection_go_compiles():
    """Pass-to-pass: vendored connection.go must have valid Go syntax."""
    result = subprocess.run(
        ['go', 'build', '-o', '/dev/null', './vendor/github.com/moby/spdystream/'],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"Vendor spdystream package must compile: {result.stderr}"


def test_go_mod_tidy():
    """Pass-to-pass: go.mod must be valid (go mod verify passes)."""
    result = subprocess.run(
        ['go', 'mod', 'verify'],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"go mod verify must pass: {result.stderr}"


def test_repo_builds():
    """Pass-to-pass: containerd binaries must compile."""
    result = subprocess.run(
        ['make', 'binaries'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, \
        f"make binaries must succeed: {result.stderr[-500:]}"


def test_repo_go_build():
    """Pass-to-pass: all Go packages build successfully (pass_to_pass)."""
    result = subprocess.run(
        ['go', 'build', './...'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, \
        f"go build ./... failed: {result.stderr[-500:]}"


def test_repo_vet():
    """Pass-to-pass: go vet passes on all packages (pass_to_pass)."""
    result = subprocess.run(
        ['go', 'vet', './...'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"go vet failed: {result.stderr[-500:]}"


def test_vendor_gofmt():
    """Pass-to-pass: vendored spdystream code is properly formatted (pass_to_pass)."""
    result = subprocess.run(
        ['gofmt', '-d', './vendor/github.com/moby/spdystream/'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.stdout == "", \
        f"gofmt found formatting issues: {result.stdout[:500]}"


def test_vendor_vet():
    """Pass-to-pass: go vet passes on vendored spdystream (pass_to_pass)."""
    result = subprocess.run(
        ['go', 'vet', './vendor/github.com/moby/spdystream/...'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"go vet on spdystream failed: {result.stderr[-500:]}"


def test_make_build():
    """Pass-to-pass: make build compiles packages (pass_to_pass)."""
    result = subprocess.run(
        ['make', 'build'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, \
        f"make build failed: {result.stderr[-500:]}"


def test_go_sum_updated():
    """Fail-to-pass: go.sum must reference v0.5.0 of spdystream."""
    go_sum = f"{REPO}/go.sum"
    with open(go_sum, 'r') as f:
        content = f.read()

    # Check that v0.5.0 is referenced
    assert 'github.com/moby/spdystream v0.5.0' in content, \
        "go.sum must contain checksum for moby/spdystream v0.5.0"


def test_vendor_modules_txt_updated():
    """Fail-to-pass: vendor/modules.txt must reflect v0.5.0."""
    modules_txt = f"{REPO}/vendor/modules.txt"
    with open(modules_txt, 'r') as f:
        content = f.read()

    # Check that modules.txt has the right version
    assert 'github.com/moby/spdystream v0.5.0' in content, \
        "vendor/modules.txt must show moby/spdystream v0.5.0"

    assert 'github.com/moby/spdystream v0.2.0' not in content, \
        "vendor/modules.txt should not show old version v0.2.0"
