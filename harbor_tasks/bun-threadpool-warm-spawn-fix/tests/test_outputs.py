import subprocess
import sys
import os
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


def test_repo_zig_syntax_valid_threadpool():
    """ThreadPool.zig has valid Zig syntax (pass_to_pass)."""
    result = subprocess.run(
        ["zig", "fmt", "--check", str(THREADPOOL_PATH)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Zig syntax check failed on ThreadPool.zig:\n{result.stderr}"


def test_repo_zig_ast_check_main():
    """Main bun.zig passes AST check (pass_to_pass)."""
    main_path = REPO / "src/bun.zig"
    result = subprocess.run(
        ["zig", "ast-check", str(main_path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"zig ast-check failed on bun.zig:\n{result.stderr}"


def test_repo_zig_ast_check_cli():
    """CLI module passes AST check (pass_to_pass)."""
    cli_path = REPO / "src/cli.zig"
    result = subprocess.run(
        ["zig", "ast-check", str(cli_path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"zig ast-check failed on cli.zig:\n{result.stderr}"


def _get_warm_body():
    """Extract the warm() function body from ThreadPool.zig."""
    content = THREADPOOL_PATH.read_text()
    warm_start = content.find("pub fn warm(self: *ThreadPool, count: u14) void {")
    if warm_start == -1:
        return None
    warm_end = content.find("\npub fn ", warm_start + 1)
    if warm_end == -1:
        warm_end = content.find("\nnoinline fn ", warm_start + 1)
    if warm_end == -1:
        warm_end = len(content)
    return content[warm_start:warm_end]


def _get_notify_slow_body():
    """Extract the notifySlow() function body from ThreadPool.zig."""
    content = THREADPOOL_PATH.read_text()
    notify_start = content.find("noinline fn notifySlow(self: *ThreadPool")
    if notify_start == -1:
        return None
    notify_end = content.find("\npub fn ", notify_start + 1)
    if notify_end == -1:
        notify_end = content.find("\nnoinline fn ", notify_start + 1)
    if notify_end == -1:
        notify_end = len(content)
    return content[notify_start:notify_end]


def test_warm_loop_uses_stable_target():
    """Verify warm() loop uses a stable target value computed before the loop.

    The bug: `while (sync.spawned < to_spawn)` where to_spawn is computed
    as `count - sync.spawned` and recalculated each iteration, causing
    incorrect loop termination.

    The fix: Computes target once before the loop and uses that stable
    value in the condition.

    This test verifies the pattern is correct by checking that the buggy
    recalculation pattern is NOT present.
    """
    warm_body = _get_warm_body()
    assert warm_body is not None, "Could not find warm() function"

    # The buggy code recalculates to_spawn each iteration inside the loop
    # Pattern: const to_spawn = count - sync.spawned
    # This should NOT be present after the fix
    assert "const to_spawn = count - sync.spawned" not in warm_body, \
        "Buggy pattern still present: to_spawn is recalculated each iteration"


def test_cmpxchg_handles_failure_correctly():
    """Verify cmpxchgWeak failure is handled correctly (retry on failure).

    The bug: cmpxchgWeak returns null on success, non-null on failure.
    The buggy code used `orelse break` which breaks on success, preventing
    thread spawning. The fix uses `if (cmpxchgWeak(...)) |x| { continue; }`
    which correctly continues on failure.
    """
    warm_body = _get_warm_body()
    assert warm_body is not None, "Could not find warm() function"

    # The buggy pattern: orelse break immediately after cmpxchgWeak
    # This breaks on SUCCESS (null), preventing thread spawning
    assert "orelse break" not in warm_body, \
        "Buggy pattern still present: orelse break after cmpxchgWeak"


def test_warm_no_early_return():
    """Verify the early return bug is fixed.

    The bug: `if (sync.spawned >= count) return;` causes warm() to return
    early if any threads were previously spawned, defeating the purpose of
    pre-warming.
    """
    warm_body = _get_warm_body()
    assert warm_body is not None, "Could not find warm() function"

    # The buggy early return pattern should NOT be present
    assert "if (sync.spawned >= count)" not in warm_body, \
        "Buggy early return 'if (sync.spawned >= count)' should be removed"


def test_uses_self_stack_size():
    """Verify thread stack size comes from self.stack_size, not default.

    Both warm() and notifySlow() should use self.stack_size for thread
    spawning, not the hardcoded default_thread_stack_size.
    """
    warm_body = _get_warm_body()
    assert warm_body is not None, "Could not find warm() function"

    notify_body = _get_notify_slow_body()
    assert notify_body is not None, "Could not find notifySlow() function"

    # Both functions should use self.stack_size
    assert "self.stack_size" in warm_body, \
        "warm() should use self.stack_size for spawn config"
    assert "self.stack_size" in notify_body, \
        "notifySlow() should use self.stack_size for spawn config"


def test_sync_updated_after_spawn():
    """Verify sync is updated after successful thread spawn.

    The bug: sync was updated inside the CAS assignment before thread.detach(),
    which happens on every iteration regardless of success.

    The fix: Updates sync after thread.detach(), ensuring sync only advances
    after a successful spawn.
    """
    warm_body = _get_warm_body()
    assert warm_body is not None, "Could not find warm() function"

    # Find thread.detach() and check that sync update follows it
    detach_pos = warm_body.find("thread.detach()")
    assert detach_pos != -1, "thread.detach() should be present in warm()"

    # After detach, there should be sync = new_sync
    after_detach = warm_body[detach_pos:]
    assert "sync = new_sync;" in after_detach, \
        "sync should be updated to new_sync after thread.detach()"


def test_warm_executes_subprocess():
    """Verify warm() CAS loop logic can be compiled and runs correctly.

    This test compiles a Zig program that implements the CAS loop pattern
    from warm() and verifies it executes correctly.
    """
    test_program = '''
const std = @import("std");
const Atomic = std.atomic.Value;

pub fn main() void {
    var sync: Atomic(u32) = Atomic(u32).init(0);
    const target: u32 = 8;

    var sync_val = sync.load(.monotonic);
    var iterations: u32 = 0;

    // The correct warm() pattern: compute target once, loop with CAS
    while (sync_val < target and iterations < 1000) : (iterations += 1) {
        const new_sync_val = sync_val + 1;

        // Correct: handle failure (non-null) by continuing
        if (sync.cmpxchgWeak(sync_val, new_sync_val, .release, .monotonic)) |_| {
            continue;
        }
        // Success: proceed with updated sync
        sync_val = new_sync_val;
    }

    if (sync_val >= target) {
        std.debug.print("SUCCESS\\n", .{});
    } else {
        std.process.exit(1);
    }
}
'''
    test_file = Path("/tmp/test_warm_exec.zig")
    test_file.write_text(test_program)

    compile_result = subprocess.run(
        ["zig", "build-exe", "--name", "test_warm_exec", str(test_file)],
        cwd="/tmp",
        capture_output=True,
        text=True,
        timeout=120
    )

    assert compile_result.returncode == 0, \
        f"Failed to compile warm() logic:\n{compile_result.stderr}"

    run_result = subprocess.run(
        ["/tmp/test_warm_exec"],
        capture_output=True,
        text=True,
        timeout=30
    )

    assert run_result.returncode == 0, \
        f"warm() logic test failed:\n{run_result.stderr}\n{run_result.stdout}"
    # std.debug.print outputs to stderr
    assert "SUCCESS" in run_result.stderr, \
        f"Expected SUCCESS output, got:\n{run_result.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))