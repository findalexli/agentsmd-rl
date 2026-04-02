#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Check if already applied (the helper function is the distinctive marker)
if grep -q '_scheduler_died_error' python/sglang/srt/entrypoints/engine.py; then
    echo "Patch already applied."
    exit 0
fi

python3 << 'PYEOF'
filepath = "python/sglang/srt/entrypoints/engine.py"
with open(filepath) as f:
    content = f.read()

# 1. Insert the helper function before _wait_for_scheduler_ready
helper = '''\ndef _scheduler_died_error(rank: int, proc) -> RuntimeError:
    """Build a descriptive error for a scheduler process that died during init."""
    proc.join(timeout=10)
    return RuntimeError(
        f"Rank {rank} scheduler died during initialization "
        f"(exit code: {proc.exitcode}). "
        f"If exit code is -9 (SIGKILL), a common cause is the OS OOM killer. "
        f"Run `dmesg -T | grep -i oom` to check."
    )


'''

content = content.replace(
    'def _wait_for_scheduler_ready(',
    helper + 'def _wait_for_scheduler_ready('
)

# 2. Replace the old docstring
old_doc = (
    '    """Wait for the model to finish loading and return scheduler infos.\n'
    '\n'
    '    Uses polling to detect child process death quickly, rather than blocking\n'
    '    indefinitely on pipe recv(). This prevents the launch from hanging when\n'
    '    a child process is killed (e.g. by OOM killer via SIGKILL) before it can\n'
    '    send any data through the pipe.\n'
    '\n'
    '    On each poll timeout, checks ALL processes (not just the current one) so that\n'
    '    a death in any rank is detected promptly regardless of iteration order.\n'
    '    """'
)
new_doc = (
    '    """Wait for the model to finish loading and return scheduler infos.\n'
    '\n'
    '    Uses poll() with timeout instead of blocking recv(), so that child process\n'
    '    death (e.g. OOM SIGKILL) is detected promptly instead of hanging forever.\n'
    '    """'
)
content = content.replace(old_doc, new_doc)

# 3. Replace the EOFError handler block
old_eof = (
    '                except EOFError:\n'
    '                    scheduler_procs[i].join(timeout=10)\n'
    '                    raise RuntimeError(\n'
    '                        f"Rank {i} scheduler died during initialization "\n'
    '                        f"(exit code: {scheduler_procs[i].exitcode}). "\n'
    '                        f"If exit code is -9 (SIGKILL), a common cause is the OS OOM killer. "\n'
    '                        f"Run `dmesg -T | grep -i oom` to check."\n'
    '                    )\n'
    '                scheduler_infos.append(data)\n'
    '                break'
)
new_eof = (
    '                except EOFError:\n'
    '                    raise _scheduler_died_error(i, scheduler_procs[i])\n'
    '                if data["status"] != "ready":\n'
    '                    raise RuntimeError(\n'
    '                        "Initialization failed. Please see the error messages above."\n'
    '                    )\n'
    '                scheduler_infos.append(data)\n'
    '                break'
)
content = content.replace(old_eof, new_eof)

# 4. Replace the else block + post-loop status check with un-nested poll-timeout
old_else = (
    '            else:\n'
    '                # Check ALL processes, not just the current one\n'
    '                for j in range(len(scheduler_procs)):\n'
    '                    if not scheduler_procs[j].is_alive():\n'
    '                        scheduler_procs[j].join(timeout=10)\n'
    '                        raise RuntimeError(\n'
    '                            f"Rank {j} scheduler died during initialization "\n'
    '                            f"(exit code: {scheduler_procs[j].exitcode}). "\n'
    '                            f"If exit code is -9 (SIGKILL), a common cause is the OS OOM killer. "\n'
    '                            f"Run `dmesg -T | grep -i oom` to check."\n'
    '                        )\n'
    '\n'
    '    for data in scheduler_infos:\n'
    '        if data["status"] != "ready":\n'
    '            raise RuntimeError(\n'
    '                "Initialization failed. Please see the error messages above."\n'
    '            )\n'
    '    return scheduler_infos'
)
new_else = (
    '\n'
    '            # Poll timed out -- check all processes for early death\n'
    '            for j in range(len(scheduler_procs)):\n'
    '                if not scheduler_procs[j].is_alive():\n'
    '                    raise _scheduler_died_error(j, scheduler_procs[j])\n'
    '\n'
    '    return scheduler_infos'
)
content = content.replace(old_else, new_else)

with open(filepath, "w") as f:
    f.write(content)

print("Patch applied successfully.")
PYEOF
