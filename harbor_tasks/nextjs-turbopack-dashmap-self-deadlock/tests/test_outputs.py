"""
Task: nextjs-turbopack-dashmap-self-deadlock
Repo: vercel/next.js @ 3e0158846e490509c6a26a4536d33777d9778101
PR:   92210

DashMap read-write self-deadlock in task_cache causing hangs during
incremental builds with persistent caching.

In get_or_create_persistent_task and get_or_create_transient_task,
self.task_cache.get(&task_type) returns a dashmap::Ref holding a read lock.
The Ref was not dropped before ConnectChildOperation::run, which can
re-enter task_cache requiring a write lock — causing self-deadlock.

No Rust toolchain is available in the Docker image. Tests use subprocess
to execute Python analysis scripts that parse the Rust source.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
MOD_FILE = f"{REPO}/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python snippet via subprocess."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_source_file_exists():
    """mod.rs exists and is not stubbed."""
    r = _run_py(f"""
import sys
from pathlib import Path
mod = Path("{MOD_FILE}")
if not mod.is_file():
    print("FAIL: mod.rs missing")
    sys.exit(1)
lines = mod.read_text().split("\\n")
if len(lines) < 1000:
    print(f"FAIL: mod.rs only {{len(lines)}} lines — likely stubbed")
    sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"Source check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_persistent_task_ref_released():
    """DashMap Ref is released before ConnectChildOperation in get_or_create_persistent_task.

    The base commit has:
        if let Some(task_id) = self.task_cache.get(&task_type) {
            let task_id = *task_id;
            ConnectChildOperation::run(...)  // read lock still held!

    The fix must consume the Ref inline (e.g. .map(|r| *r), .copied())
    so the read lock is released before ConnectChildOperation::run.
    """
    r = _run_py(f"""
import re, sys

src = open("{MOD_FILE}").read()
lines = src.split("\\n")

# Find get_or_create_persistent_task function (the inner impl, not the trait delegation)
fn_start = None
for i, line in enumerate(lines):
    if "fn get_or_create_persistent_task(" in line:
        # The inner impl has the actual cache lookup logic (longer body)
        # Trait delegation version just calls self.inner.get_or_create_persistent_task
        # Check next ~5 lines for task_cache usage
        for j in range(i, min(i + 30, len(lines))):
            if "task_cache" in lines[j]:
                fn_start = i
                break
        if fn_start is not None:
            break

if fn_start is None:
    print("FAIL: get_or_create_persistent_task with task_cache not found")
    sys.exit(1)

# Extract function body (find the matching closing brace)
depth = 0
fn_body_lines = []
started = False
for i in range(fn_start, len(lines)):
    line = lines[i]
    if "{{" in line:
        started = True
    if started:
        depth += line.count("{{") - line.count("}}")
        fn_body_lines.append(line)
        if depth <= 0:
            break

fn_body = "\\n".join(fn_body_lines)

# Check: task_cache.get(&task_type) must have inline value extraction
# The Ref must be consumed before ConnectChildOperation::run
cache_get_lines = [l for l in fn_body_lines if "task_cache.get(&task_type)" in l]
if not cache_get_lines:
    print("FAIL: task_cache.get(&task_type) not found in get_or_create_persistent_task")
    sys.exit(1)

for cache_line in cache_get_lines:
    after_get = cache_line.split("task_cache.get(&task_type)", 1)[1]
    # Must chain a method that consumes the Ref: .map(, .copied(, .and_then(, etc.
    if not re.search(r"\\.(map|copied|cloned|and_then)\\s*\\(", after_get):
        print(f"FAIL: task_cache.get(&task_type) without inline Ref extraction")
        print(f"  Line: {{cache_line.strip()[:120]}}")
        sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Persistent task check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_transient_task_ref_released():
    """DashMap Ref is released before ConnectChildOperation in get_or_create_transient_task.

    Same deadlock pattern as persistent_task but in the transient variant.
    The Ref from task_cache.get() must be consumed inline.
    """
    r = _run_py(f"""
import re, sys

src = open("{MOD_FILE}").read()
lines = src.split("\\n")

# Find get_or_create_transient_task function (the inner impl)
fn_start = None
for i, line in enumerate(lines):
    if "fn get_or_create_transient_task(" in line:
        for j in range(i, min(i + 30, len(lines))):
            if "task_cache" in lines[j]:
                fn_start = i
                break
        if fn_start is not None:
            break

if fn_start is None:
    print("FAIL: get_or_create_transient_task with task_cache not found")
    sys.exit(1)

# Extract function body
depth = 0
fn_body_lines = []
started = False
for i in range(fn_start, len(lines)):
    line = lines[i]
    if "{{" in line:
        started = True
    if started:
        depth += line.count("{{") - line.count("}}")
        fn_body_lines.append(line)
        if depth <= 0:
            break

fn_body = "\\n".join(fn_body_lines)

# Check: task_cache.get(&task_type) must have inline value extraction
cache_get_lines = [l for l in fn_body_lines if "task_cache.get(&task_type)" in l]
if not cache_get_lines:
    print("FAIL: task_cache.get(&task_type) not found in get_or_create_transient_task")
    sys.exit(1)

for cache_line in cache_get_lines:
    after_get = cache_line.split("task_cache.get(&task_type)", 1)[1]
    if not re.search(r"\\.(map|copied|cloned|and_then)\\s*\\(", after_get):
        print(f"FAIL: task_cache.get(&task_type) without inline Ref extraction")
        print(f"  Line: {{cache_line.strip()[:120]}}")
        sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Transient task check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_no_dangling_deref_after_cache_get():
    """No separate 'let task_id = *task_id;' after task_cache.get() in either function.

    The base commit has this dangling dereference pattern in both functions:
        if let Some(task_id) = self.task_cache.get(&task_type) {
            let task_id = *task_id;   // Ref still alive!

    This means the DashMap Ref lives through the entire if-let scope.
    The fix removes these lines by extracting the value inline.
    """
    r = _run_py(f"""
import re, sys

src = open("{MOD_FILE}").read()
lines = src.split("\\n")

# Find all get_or_create_persistent_task and get_or_create_transient_task
# function bodies that contain task_cache
fn_names = ["get_or_create_persistent_task", "get_or_create_transient_task"]
violations = []
found_fns = []

for fn_name in fn_names:
    fn_start = None
    for i, line in enumerate(lines):
        if f"fn {{fn_name}}(" in line:
            for j in range(i, min(i + 30, len(lines))):
                if "task_cache" in lines[j]:
                    fn_start = i
                    break
            if fn_start is not None:
                break

    if fn_start is None:
        print(f"FAIL: {{fn_name}} with task_cache not found")
        sys.exit(1)
    found_fns.append(fn_name)

    # Extract function body
    depth = 0
    fn_body_lines = []
    started = False
    for i in range(fn_start, len(lines)):
        line = lines[i]
        if "{{" in line:
            started = True
        if started:
            depth += line.count("{{") - line.count("}}")
            fn_body_lines.append((i + 1, line))
            if depth <= 0:
                break

    # Look for pattern: task_cache.get followed by let task_id = *task_id
    for idx, (lineno, line) in enumerate(fn_body_lines):
        if "task_cache.get(&task_type)" in line:
            # Check next 3 non-empty lines for dangling deref
            checked = 0
            for k in range(idx + 1, min(idx + 5, len(fn_body_lines))):
                next_line = fn_body_lines[k][1].strip()
                if not next_line or next_line.startswith("//"):
                    continue
                checked += 1
                if re.match(r"let\\s+task_id\\s*=\\s*\\*task_id\\s*;", next_line):
                    violations.append(
                        f"{{fn_name}} line {{fn_body_lines[k][0]}}: {{next_line}}"
                    )
                if checked >= 2:
                    break

if violations:
    print("FAIL: Dangling dereference after task_cache.get() — Ref stays alive:")
    for v in violations:
        print(f"  {{v}}")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Dangling deref check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_cache_lookup_preserved():
    """Both functions still perform cache lookup via task_cache.get.

    Anti-deletion check: the fix must preserve the cache lookup logic,
    not just remove it to avoid the deadlock.
    """
    r = _run_py(f"""
import sys

src = open("{MOD_FILE}").read()
lines = src.split("\\n")

fn_names = ["get_or_create_persistent_task", "get_or_create_transient_task"]
for fn_name in fn_names:
    found_fn = False
    found_cache = False
    found_connect = False
    fn_start = None
    for i, line in enumerate(lines):
        if f"fn {{fn_name}}(" in line:
            for j in range(i, min(i + 30, len(lines))):
                if "task_cache" in lines[j]:
                    fn_start = i
                    break
            if fn_start is not None:
                found_fn = True
                break

    if not found_fn:
        print(f"FAIL: {{fn_name}} not found")
        sys.exit(1)

    # Check the function body has both cache lookup and ConnectChild
    depth = 0
    started = False
    for i in range(fn_start, len(lines)):
        line = lines[i]
        if "{{" in line:
            started = True
        if started:
            depth += line.count("{{") - line.count("}}")
            if "task_cache.get" in line:
                found_cache = True
            if "ConnectChildOperation::run" in line:
                found_connect = True
            if depth <= 0:
                break

    if not found_cache:
        print(f"FAIL: {{fn_name}} missing task_cache.get — cache lookup deleted")
        sys.exit(1)
    if not found_connect:
        print(f"FAIL: {{fn_name}} missing ConnectChildOperation::run — essential logic deleted")
        sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Cache lookup check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout
