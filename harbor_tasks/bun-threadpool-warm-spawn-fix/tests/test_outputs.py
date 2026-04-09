import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/bun")
THREADPOOL_PATH = REPO / "src/threading/ThreadPool.zig"


def test_syntax_valid():
    """Zig code has valid syntax (parses with zig fmt)."""
    result = subprocess.run(
        ["zig", "fmt", "--check", str(THREADPOOL_PATH)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    # zig fmt returns 0 if file is valid (even if not formatted)
    assert result.returncode == 0, f"Zig syntax check failed:\n{result.stderr}"


def test_repo_zig_fmt_threadpool():
    """Repo's Zig ThreadPool.zig passes formatting check (pass_to_pass)."""
    result = subprocess.run(
        ["zig", "fmt", "--check", str(THREADPOOL_PATH)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"zig fmt --check failed on ThreadPool.zig:\n{result.stderr}"


def test_repo_zig_fmt_mutex():
    """Repo's Zig Mutex.zig passes formatting check (pass_to_pass)."""
    mutex_path = REPO / "src/threading/Mutex.zig"
    result = subprocess.run(
        ["zig", "fmt", "--check", str(mutex_path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"zig fmt --check failed on Mutex.zig:\n{result.stderr}"


def test_repo_zig_fmt_condition():
    """Repo's Zig Condition.zig passes formatting check (pass_to_pass)."""
    condition_path = REPO / "src/threading/Condition.zig"
    result = subprocess.run(
        ["zig", "fmt", "--check", str(condition_path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"zig fmt --check failed on Condition.zig:\n{result.stderr}"


def test_repo_zig_fmt_futex():
    """Repo's Zig Futex.zig passes formatting check (pass_to_pass)."""
    futex_path = REPO / "src/threading/Futex.zig"
    result = subprocess.run(
        ["zig", "fmt", "--check", str(futex_path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"zig fmt --check failed on Futex.zig:\n{result.stderr}"


def test_repo_zig_fmt_channel():
    """Repo's Zig channel.zig passes formatting check (pass_to_pass)."""
    channel_path = REPO / "src/threading/channel.zig"
    result = subprocess.run(
        ["zig", "fmt", "--check", str(channel_path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"zig fmt --check failed on channel.zig:\n{result.stderr}"


def test_repo_zig_fmt_waitgroup():
    """Repo's Zig WaitGroup.zig passes formatting check (pass_to_pass)."""
    waitgroup_path = REPO / "src/threading/WaitGroup.zig"
    result = subprocess.run(
        ["zig", "fmt", "--check", str(waitgroup_path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"zig fmt --check failed on WaitGroup.zig:\n{result.stderr}"


def test_repo_zig_fmt_unbounded_queue():
    """Repo's Zig unbounded_queue.zig passes formatting check (pass_to_pass)."""
    queue_path = REPO / "src/threading/unbounded_queue.zig"
    result = subprocess.run(
        ["zig", "fmt", "--check", str(queue_path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"zig fmt --check failed on unbounded_queue.zig:\n{result.stderr}"


def test_repo_zig_ast_check_threadpool():
    """Repo's Zig ThreadPool.zig passes AST check (pass_to_pass)."""
    result = subprocess.run(
        ["zig", "ast-check", str(THREADPOOL_PATH)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"zig ast-check failed on ThreadPool.zig:\n{result.stderr}"


def test_repo_zig_ast_check_mutex():
    """Repo's Zig Mutex.zig passes AST check (pass_to_pass)."""
    mutex_path = REPO / "src/threading/Mutex.zig"
    result = subprocess.run(
        ["zig", "ast-check", str(mutex_path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"zig ast-check failed on Mutex.zig:\n{result.stderr}"


def test_repo_zig_ast_check_condition():
    """Repo's Zig Condition.zig passes AST check (pass_to_pass)."""
    condition_path = REPO / "src/threading/Condition.zig"
    result = subprocess.run(
        ["zig", "ast-check", str(condition_path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"zig ast-check failed on Condition.zig:\n{result.stderr}"


def test_repo_zig_ast_check_futex():
    """Repo's Zig Futex.zig passes AST check (pass_to_pass)."""
    futex_path = REPO / "src/threading/Futex.zig"
    result = subprocess.run(
        ["zig", "ast-check", str(futex_path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"zig ast-check failed on Futex.zig:\n{result.stderr}"


def test_repo_zig_ast_check_channel():
    """Repo's Zig channel.zig passes AST check (pass_to_pass)."""
    channel_path = REPO / "src/threading/channel.zig"
    result = subprocess.run(
        ["zig", "ast-check", str(channel_path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"zig ast-check failed on channel.zig:\n{result.stderr}"


def test_repo_zig_ast_check_waitgroup():
    """Repo's Zig WaitGroup.zig passes AST check (pass_to_pass)."""
    waitgroup_path = REPO / "src/threading/WaitGroup.zig"
    result = subprocess.run(
        ["zig", "ast-check", str(waitgroup_path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"zig ast-check failed on WaitGroup.zig:\n{result.stderr}"


def test_repo_zig_ast_check_unbounded_queue():
    """Repo's Zig unbounded_queue.zig passes AST check (pass_to_pass)."""
    queue_path = REPO / "src/threading/unbounded_queue.zig"
    result = subprocess.run(
        ["zig", "ast-check", str(queue_path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"zig ast-check failed on unbounded_queue.zig:\n{result.stderr}"


def test_warm_uses_target_not_delta():
    """warm() compares against target (min(count, max_threads)) not delta."""
    content = THREADPOOL_PATH.read_text()

    # The fix introduces `const target = @min(count, ...)` and uses it in the while loop
    assert "const target = @min(count, @as(u14, @truncate(self.max_threads)))" in content, \
        "warm() should declare target = min(count, max_threads)"

    # Should NOT have the old buggy pattern of `count - sync.spawned`
    assert "count - sync.spawned" not in content, \
        "warm() should not compare against delta (count - spawned)"

    # Should use `while (sync.spawned < target)` not the old `to_spawn`
    # Find the warm function and check its structure
    warm_start = content.find("pub fn warm(self: *ThreadPool, count: u14) void {")
    warm_end = content.find("\npub fn ", warm_start + 1)
    if warm_end == -1:
        warm_end = len(content)

    warm_body = content[warm_start:warm_end]

    # Check the loop uses target
    assert "while (sync.spawned < target)" in warm_body, \
        "warm() loop should compare against target not to_spawn"

    # Should NOT have the old early return
    assert "if (sync.spawned >= count)" not in warm_body, \
        "warm() should not have early return on spawned >= count"


def test_cmpxchg_correct_logic():
    """cmpxchgWeak spawns on success, retries on failure."""
    content = THREADPOOL_PATH.read_text()

    warm_start = content.find("pub fn warm(self: *ThreadPool, count: u14) void {")
    warm_end = content.find("\npub fn ", warm_start + 1)
    if warm_end == -1:
        warm_end = len(content)

    warm_body = content[warm_start:warm_end]

    # The fix: cmpxchgWeak result is checked - null = success, non-null = retry
    # Old code: `cmpxchgWeak(...) orelse break` - broke on success!
    # New code: checks for |current| pattern (failure case) and continues

    # Should NOT have the buggy `orelse break` pattern
    assert "cmpxchgWeak" in warm_body
    # Check the old buggy pattern is gone
    old_bug_pattern = "cmpxchgWeak(\n            @as(u32, @bitCast(sync)),\n            @as(u32, @bitCast(new_sync)),\n            .release,\n            .monotonic,\n        ) orelse break"
    assert old_bug_pattern not in warm_body, \
        "warm() should not use orelse break (bug: exited loop on CAS success)"

    # Should have the correct pattern: check for |current| and continue
    assert "|current|" in warm_body, \
        "warm() should handle cmpxchgWeak failure with |current| capture and continue"

    assert "sync = @as(Sync, @bitCast(current));" in warm_body, \
        "warm() should update sync from current on CAS failure"

    assert "continue;" in warm_body, \
        "warm() should continue loop on CAS failure"


def test_stack_size_used_consistently():
    """Both warm() and notifySlow() use self.stack_size not default_thread_stack_size."""
    content = THREADPOOL_PATH.read_text()

    warm_start = content.find("pub fn warm(self: *ThreadPool, count: u14) void {")
    warm_end = content.find("\npub fn ", warm_start + 1)
    if warm_end == -1:
        warm_end = len(content)

    warm_body = content[warm_start:warm_end]

    notify_start = content.find("noinline fn notifySlow(self: *ThreadPool")
    notify_end = content.find("\npub fn ", notify_start + 1)
    if notify_end == -1:
        notify_end = len(content)

    notify_body = content[notify_start:notify_end]

    # Both should use self.stack_size not default_thread_stack_size
    assert "self.stack_size" in warm_body, \
        "warm() should use self.stack_size not default_thread_stack_size"

    assert "self.stack_size" in notify_body, \
        "notifySlow() should use self.stack_size not default_thread_stack_size"

    # Should NOT use default_thread_stack_size in these functions
    # (except possibly the constant declaration itself)
    warm_lines = warm_body.split('\n')
    for line in warm_lines:
        if "default_thread_stack_size" in line:
            # Only allow if it's a comment or not a usage
            assert line.strip().startswith('//') or '.stack_size = self.stack_size' in warm_body, \
                f"warm() should not use default_thread_stack_size: {line}"


def test_thread_spawn_follows_cmpxchg_success():
    """Thread.spawn happens after successful cmpxchg, not before or on failure."""
    content = THREADPOOL_PATH.read_text()

    warm_start = content.find("pub fn warm(self: *ThreadPool, count: u14) void {")
    warm_end = content.find("\npub fn ", warm_start + 1)
    if warm_end == -1:
        warm_end = len(content)

    warm_body = content[warm_start:warm_end]

    # Find the cmpxchgWeak block structure
    # After the fix, the pattern should be:
    # if (self.sync.cmpxchgWeak(...)) |current| { ... continue; }
    # // cmpxchg succeeded - spawn thread here
    # const spawn_config = ...
    # const thread = std.Thread.spawn(...)

    # Check the spawn happens AFTER the if block that handles failure
    cmpxchg_pos = warm_body.find("cmpxchgWeak")
    if_block_end = warm_body.find("}", cmpxchg_pos)
    spawn_config_pos = warm_body.find("const spawn_config = std.Thread.SpawnConfig", if_block_end)

    assert spawn_config_pos > if_block_end, \
        "Thread spawn should happen after the if block that handles CAS failure"

    # Verify spawn_config uses the correct stack_size
    spawn_line = warm_body[spawn_config_pos:spawn_config_pos+200]
    assert "self.stack_size" in spawn_line, \
        "spawn_config should use self.stack_size"


def test_sync_updated_after_successful_spawn():
    """After successful spawn, sync is updated to new_sync."""
    content = THREADPOOL_PATH.read_text()

    warm_start = content.find("pub fn warm(self: *ThreadPool, count: u14) void {")
    warm_end = content.find("\npub fn ", warm_start + 1)
    if warm_end == -1:
        warm_end = len(content)

    warm_body = content[warm_start:warm_end]

    # After detach(), sync should be updated to new_sync for next iteration
    detach_pos = warm_body.find("thread.detach()")
    sync_update_pos = warm_body.find("sync = new_sync;", detach_pos)

    assert sync_update_pos > detach_pos, \
        "sync = new_sync should follow thread.detach() for correct state tracking"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
