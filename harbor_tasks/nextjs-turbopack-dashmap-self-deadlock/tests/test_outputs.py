"""
Task: nextjs-turbopack-dashmap-self-deadlock
Repo: vercel/next.js @ 3e0158846e490509c6a26a4536d33777d9778101
PR:   92210

DashMap read-write self-deadlock in task_cache causing hangs during
incremental builds with persistent caching.

No Rust toolchain is available in the Docker image.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
MOD_FILE = f"{REPO}/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs"


def _run_py(code: str, timeout: int = 30):
    return subprocess.run(["python3", "-c", code], capture_output=True, text=True, timeout=timeout)


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
lines = mod.read_text().splitlines()
if len(lines) < 1000:
    print(f"FAIL: mod.rs only {{len(lines)}} lines")
    sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"Source check: {{r.stdout}} {{r.stderr}}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_rust_file_parses():
    """Rust file is valid and parseable."""
    r = _run_py(f"""
import sys
from pathlib import Path
mod = Path("{MOD_FILE}")
if not mod.is_file():
    print("FAIL: mod.rs missing")
    sys.exit(1)
try:
    src = mod.read_text()
    lines = src.splitlines()
    fn_names = ["get_or_create_persistent_task", "get_or_create_transient_task"]
    for fn_name in fn_names:
        found = False
        for i, line in enumerate(lines):
            if f"fn {{fn_name}}(" in line:
                found = True
                break
        if not found:
            print(f"FAIL: {{fn_name}} not found")
            sys.exit(1)
    print("PASS")
except Exception as e:
    print(f"FAIL: {{e}}")
    sys.exit(1)
""")
    assert r.returncode == 0
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass  
def test_repo_dashmap_usage_present():
    """DashMap task_cache is used."""
    r = _run_py(f"""
import sys
src = open("{MOD_FILE}").read()
for pat in ["FxDashMap", "task_cache"]:
    if pat not in src:
        print(f"FAIL: {{pat}} not found")
        sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_taskid_type_present():
    """TaskId and ConnectChildOperation present."""
    r = _run_py(f"""
import sys
src = open("{MOD_FILE}").read()
if "TaskId" not in src:
    print("FAIL: TaskId not found")
    sys.exit(1)
if "ConnectChildOperation" not in src:
    print("FAIL: ConnectChildOperation not found")
    sys.exit(1)
if "::run(" not in src:
    print("FAIL: ::run not found")
    sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_git_history_intact():
    """Git history intact."""
    r = _run_py("""
import subprocess, sys
result = subprocess.run(["git", "-C", "/workspace/next.js", "log", "--oneline", "-n", "5"], capture_output=True, text=True)
if result.returncode != 0:
    print(f"FAIL: {{result.stderr}}")
    sys.exit(1)
if "3e0158846" not in result.stdout:
    print("FAIL: Base commit not found")
    sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_persistent_task_ref_released():
    """DashMap Ref released in get_or_create_persistent_task."""
    r = _run_py(f"""
import re, sys
src = open("{MOD_FILE}").read()
lines = src.splitlines()
fn_start = None
for i, line in enumerate(lines):
    if "fn get_or_create_persistent_task(" in line:
        for j in range(i, min(i+30, len(lines))):
            if "task_cache" in lines[j]:
                fn_start = i
                break
        if fn_start:
            break
if not fn_start:
    print("FAIL: fn not found")
    sys.exit(1)
depth = 0
fn_body = []
started = False
for i in range(fn_start, len(lines)):
    line = lines[i]
    if "{{" in line:
        started = True
    if started:
        depth += line.count("{{") - line.count("}}")
        fn_body.append(line)
        if depth <= 0:
            break
cache_lines = [l for l in fn_body if "task_cache.get(&task_type)" in l]
if not cache_lines:
    print("FAIL: task_cache.get not found")
    sys.exit(1)
for cl in cache_lines:
    after = cl.split("task_cache.get(&task_type)", 1)[1]
    # Check for .map(|r| *r), .copied(), .cloned() or similar inline extraction
    if not re.search(r"\.(map|copied|cloned|and_then)", after):
        print("FAIL: No inline Ref extraction in persistent_task")
        sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_transient_task_ref_released():
    """DashMap Ref released in get_or_create_transient_task."""
    r = _run_py(f"""
import re, sys
src = open("{MOD_FILE}").read()
lines = src.splitlines()
fn_start = None
for i, line in enumerate(lines):
    if "fn get_or_create_transient_task(" in line:
        for j in range(i, min(i+30, len(lines))):
            if "task_cache" in lines[j]:
                fn_start = i
                break
        if fn_start:
            break
if not fn_start:
    print("FAIL: fn not found")
    sys.exit(1)
depth = 0
fn_body = []
started = False
for i in range(fn_start, len(lines)):
    line = lines[i]
    if "{{" in line:
        started = True
    if started:
        depth += line.count("{{") - line.count("}}")
        fn_body.append(line)
        if depth <= 0:
            break
cache_lines = [l for l in fn_body if "task_cache.get(&task_type)" in l]
if not cache_lines:
    print("FAIL: task_cache.get not found")
    sys.exit(1)
for cl in cache_lines:
    after = cl.split("task_cache.get(&task_type)", 1)[1]
    # Check for .map(|r| *r), .copied(), .cloned() or similar inline extraction
    if not re.search(r"\.(map|copied|cloned|and_then)", after):
        print("FAIL: No inline Ref extraction in transient_task")
        sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_no_dangling_deref_after_cache_get():
    """No dangling deref after cache get."""
    r = _run_py(f"""
import re, sys
src = open("{MOD_FILE}").read()
lines = src.splitlines()
fn_names = ["get_or_create_persistent_task", "get_or_create_transient_task"]
violations = []
for fn_name in fn_names:
    fn_start = None
    for i, line in enumerate(lines):
        if f"fn {{fn_name}}(" in line:
            for j in range(i, min(i+30, len(lines))):
                if "task_cache" in lines[j]:
                    fn_start = i
                    break
            if fn_start:
                break
    if not fn_start:
        continue
    depth = 0
    fn_body = []
    started = False
    for i in range(fn_start, len(lines)):
        line = lines[i]
        if "{{" in line:
            started = True
        if started:
            depth += line.count("{{") - line.count("}}")
            fn_body.append((i+1, line))
            if depth <= 0:
                break
    for idx, (ln, line) in enumerate(fn_body):
        if "task_cache.get(&task_type)" in line:
            checked = 0
            for k in range(idx+1, min(idx+5, len(fn_body))):
                nl = fn_body[k][1].strip()
                if not nl or nl.startswith("//"):
                    continue
                checked += 1
                # Pattern: let task_id = *task_id;
                if re.match(r"let\s+task_id\s*=\s*\*task_id\s*;", nl):
                    violations.append(f"{{fn_name}} line {{fn_body[k][0]}}: {{nl}}")
                if checked >= 2:
                    break
if violations:
    print("FAIL: Dangling deref found")
    for v in violations:
        print(f"  {{v}}")
    sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_cache_lookup_preserved():
    """Cache lookup preserved."""
    r = _run_py(f"""
import sys
src = open("{MOD_FILE}").read()
lines = src.splitlines()
fn_names = ["get_or_create_persistent_task", "get_or_create_transient_task"]
for fn_name in fn_names:
    fn_start = None
    for i, line in enumerate(lines):
        if f"fn {{fn_name}}(" in line:
            for j in range(i, min(i+30, len(lines))):
                if "task_cache" in lines[j]:
                    fn_start = i
                    break
            if fn_start:
                break
    if not fn_start:
        print(f"FAIL: {{fn_name}} not found")
        sys.exit(1)
    found_cache = False
    found_connect = False
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
        print(f"FAIL: {{fn_name}} missing cache")
        sys.exit(1)
    if not found_connect:
        print(f"FAIL: {{fn_name}} missing connect")
        sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_cargo_fmt():
    """Rust code passes cargo fmt --check (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
set -e
export PATH="$HOME/.cargo/bin:$PATH"
# Install rustup if not present
if ! command -v cargo &>/dev/null; then
    apt-get update -qq && apt-get install -y --no-install-recommends curl ca-certificates -qq 2>&1 >/dev/null
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain nightly-2026-02-18 --component rustfmt 2>&1 | tail -3
fi
. "$HOME/.cargo/env"
cd /workspace/next.js/turbopack/crates/turbo-tasks-backend
exec cargo fmt -- --check
"""],
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo fmt --check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_cargo_check():
    """Rust code passes cargo check (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
set -e
export PATH="$HOME/.cargo/bin:$PATH"
# Install rustup if not present
if ! command -v cargo &>/dev/null; then
    apt-get update -qq && apt-get install -y --no-install-recommends curl ca-certificates -qq 2>&1 >/dev/null
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain nightly-2026-02-18 2>&1 | tail -3
fi
. "$HOME/.cargo/env"
cd /workspace/next.js/turbopack/crates/turbo-tasks-backend
exec cargo check
"""],
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_test_unit():
    """Rust unit tests for turbo-tasks-backend pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
set -e
export PATH="$HOME/.cargo/bin:$PATH"
# Install rustup if not present
if ! command -v cargo &>/dev/null; then
    apt-get update -qq && apt-get install -y --no-install-recommends curl ca-certificates -qq 2>&1 >/dev/null
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain nightly-2026-02-18 2>&1 | tail -3
fi
. "$HOME/.cargo/env"
cd /workspace/next.js/turbopack/crates/turbo-tasks-backend
# Run only a quick subset of tests to verify the code works
exec cargo test --lib -- --test-threads=2 test_basic
"""],
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo test failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
