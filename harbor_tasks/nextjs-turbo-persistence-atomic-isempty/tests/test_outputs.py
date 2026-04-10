"""
Task: nextjs-turbo-persistence-atomic-isempty
Repo: next.js @ e513488d0d3bc19ae9b16b08ef43add7e4faab7c
PR:   92481

Replace RwLock-based is_empty() in TurboPersistence with lock-free AtomicBool.
The is_empty() method is called on the hot read path (lookup_task_candidates) and
previously acquired a read lock purely to check a boolean state that changes
infrequently. The fix adds an AtomicBool mirror that is updated at the two
mutation points (load_directory and commit).

No Rust toolchain is available in the Docker image — cargo check would exceed
timeout on this monorepo. Tests use subprocess to execute Python analysis scripts
that parse the Rust source.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
DB_FILE = f"{REPO}/turbopack/crates/turbo-persistence/src/db.rs"
PERSISTENCE_SRC = f"{REPO}/turbopack/crates/turbo-persistence/src"


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
def test_source_file_valid():
    """Source file exists with TurboPersistence struct and core structure."""
    r = _run_py(f"""
import sys
from pathlib import Path
p = Path("{DB_FILE}")
if not p.is_file():
    print("FAIL: db.rs missing")
    sys.exit(1)
src = p.read_text()
if "struct TurboPersistence" not in src:
    print("FAIL: TurboPersistence struct missing")
    sys.exit(1)
if "fn is_empty" not in src:
    print("FAIL: is_empty method missing")
    sys.exit(1)
if "struct Inner" not in src:
    print("FAIL: Inner struct missing")
    sys.exit(1)
lines = src.split("\\n")
if len(lines) < 400:
    print(f"FAIL: db.rs only {{len(lines)}} lines — likely stubbed")
    sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"Source check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_repo_module_files_exist():
    """All declared Rust module files exist (pass_to_pass).

    Validates that the crate structure is intact and no source files are missing.
    This catches file corruption, incomplete checkouts, or broken module paths.
    """
    r = _run_py(f"""
import sys
from pathlib import Path

src_dir = Path("{REPO}/turbopack/crates/turbo-persistence/src")
lib_file = src_dir / "lib.rs"

if not lib_file.exists():
    print("FAIL: lib.rs not found")
    sys.exit(1)

src = lib_file.read_text()

# Extract mod declarations
import re
mod_decls = re.findall(r"^\\s*(?:pub\\s+)?(?:mod|pub\\s+mod)\\s+(\\w+)", src, re.MULTILINE)

missing = []
for mod in mod_decls:
    mod_file = src_dir / f"{{mod}}.rs"
    mod_dir_file = src_dir / mod / "mod.rs"
    if not mod_file.exists() and not mod_dir_file.exists():
        missing.append(mod)

if missing:
    print(f"FAIL: Missing module files: {{missing}}")
    sys.exit(1)

print(f"PASS: All {{len(mod_decls)}} module files exist")
""")
    assert r.returncode == 0, "Module file check failed: " + r.stdout + "\n" + r.stderr
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_repo_source_integrity():
    """Source files are not truncated/corrupted (pass_to_pass).

    Validates that key source files have reasonable line counts and structure.
    Catches truncated downloads, disk issues, or git checkout problems.
    """
    r = _run_py(f"""
import sys
from pathlib import Path

src_dir = Path("{REPO}/turbopack/crates/turbo-persistence/src")
files_to_check = ["lib.rs", "db.rs"]

for fname in files_to_check:
    fpath = src_dir / fname
    if not fpath.exists():
        print(f"FAIL: {{fname}} does not exist")
        sys.exit(1)
    lines = fpath.read_text().splitlines()
    if len(lines) < 10:
        print(f"FAIL: {{fname}} only has {{len(lines)}} lines -- likely truncated")
        sys.exit(1)

print(f"PASS: All source files have valid structure")
""")
    assert r.returncode == 0, "Source integrity check failed: " + r.stdout + "\n" + r.stderr
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_repo_no_tabs():
    """Source files use spaces for indentation, not tabs (pass_to_pass).

    Rust standard style uses 4 spaces for indentation. This check ensures
    the source files follow standard formatting conventions.
    """
    r = _run_py(f"""
import sys
from pathlib import Path

src_dir = Path("{PERSISTENCE_SRC}")
rust_files = list(src_dir.glob("*.rs"))

for fpath in rust_files:
    content = fpath.read_text()
    if '\\t' in content:
        print(f"FAIL: {{fpath.name}} contains tab characters")
        sys.exit(1)

print(f"PASS: All {{len(rust_files)}} Rust files use spaces for indentation")
""")
    assert r.returncode == 0, "Tab check failed: " + r.stdout + "\n" + r.stderr
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_repo_valid_utf8():
    """Source files are valid UTF-8 (pass_to_pass).

    Validates that source files can be read as valid UTF-8 text.
    Catches encoding issues or binary corruption.
    """
    r = _run_py(f"""
import sys
from pathlib import Path

src_dir = Path("{PERSISTENCE_SRC}")
files = list(src_dir.glob("*.rs"))

for fpath in files:
    try:
        fpath.read_text(encoding='utf-8')
    except UnicodeDecodeError as e:
        print(f"FAIL: {{fpath.name}} is not valid UTF-8: {{e}}")
        sys.exit(1)

print(f"PASS: All {{len(files)}} source files are valid UTF-8")
""")
    assert r.returncode == 0, "UTF-8 check failed: " + r.stdout + "\n" + r.stderr
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_struct_has_atomic_bool():
    """TurboPersistence struct contains an AtomicBool field for is_empty state.

    The fix adds an AtomicBool field that mirrors the emptiness of
    inner.meta_files, avoiding lock contention on the hot read path.
    The struct already has active_write_operation: AtomicBool on the base
    commit, so we specifically check for a NEW AtomicBool field.
    """
    r = _run_py(f"""
import re, sys
src = open("{DB_FILE}").read()

# Find TurboPersistence struct body
match = re.search(r'pub struct TurboPersistence.*?\\{{', src, re.DOTALL)
if not match:
    print("FAIL: TurboPersistence struct not found")
    sys.exit(1)

# Extract struct body
start = match.end()
depth = 1
pos = start
while pos < len(src) and depth > 0:
    if src[pos] == '{{':
        depth += 1
    elif src[pos] == '}}':
        depth -= 1
    pos += 1
struct_body = src[start:pos]

# Find all AtomicBool fields
atomic_fields = re.findall(r'(\\w+):\\s*AtomicBool', struct_body)

# active_write_operation already uses AtomicBool on the base commit
# We need at least one MORE AtomicBool field for the is_empty mirror
non_write_atomics = [f for f in atomic_fields if f != 'active_write_operation']
if not non_write_atomics:
    print("FAIL: No new AtomicBool field in TurboPersistence (only active_write_operation)")
    sys.exit(1)

print(f"PASS: found AtomicBool field(s): {{non_write_atomics}}")
""")
    assert r.returncode == 0, f"AtomicBool check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_isempty_lock_free():
    """is_empty() uses atomic load instead of acquiring RwLock read lock.

    Before: self.inner.read().meta_files.is_empty()  (acquires read lock)
    After:  self.is_empty.load(Ordering::Relaxed)     (lock-free atomic read)
    """
    r = _run_py(f"""
import re, sys
src = open("{DB_FILE}").read()

# Find the is_empty method body
pattern = r'pub fn is_empty\\s*\\(&self\\)\\s*->\\s*bool\\s*\\{{'
match = re.search(pattern, src)
if not match:
    print("FAIL: is_empty() method signature not found")
    sys.exit(1)

start = match.end()
depth = 1
pos = start
while pos < len(src) and depth > 0:
    if src[pos] == '{{':
        depth += 1
    elif src[pos] == '}}':
        depth -= 1
    pos += 1
method_body = src[start:pos - 1]

# Negative check: must NOT use self.inner.read()
if 'self.inner.read()' in method_body:
    print("FAIL: is_empty() still acquires RwLock read lock via self.inner.read()")
    sys.exit(1)

# Positive check: must use atomic load
if '.load(' not in method_body:
    print("FAIL: is_empty() doesn't use atomic load — expected .load(Ordering::...)")
    sys.exit(1)

# Anti-stub: must not be a hardcoded constant
stripped = method_body.strip()
if stripped in ('true', 'false'):
    print("FAIL: is_empty() is stubbed as a constant")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Lock-free check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_atomic_synced_on_mutation():
    """AtomicBool is updated at both meta_files mutation points.

    The atomic must be stored/updated wherever inner.meta_files is modified:
    1. In load_directory — after reading meta files from disk
    2. In commit — after appending/removing meta files
    Without both updates, the atomic becomes stale and is_empty() returns
    incorrect results.
    """
    r = _run_py(f"""
import re, sys
src = open("{DB_FILE}").read()

# Count .store() calls that reference meta_files.is_empty()
# Pattern: something.store(something_meta_files.is_empty(), Ordering::...)
store_calls = re.findall(r'\\.store\\([^)]*meta_files\\.is_empty\\(\\)[^)]*\\)', src)
if len(store_calls) < 2:
    print(f"FAIL: Found {{len(store_calls)}} atomic store(s) with meta_files.is_empty(), need at least 2")
    sys.exit(1)

# Verify stores are in different functions (at least 30 lines apart)
lines = src.split("\\n")
store_line_nums = []
for i, line in enumerate(lines):
    if '.store(' in line and 'meta_files.is_empty()' in line:
        store_line_nums.append(i)

if len(store_line_nums) < 2:
    print(f"FAIL: Found atomic store on {{len(store_line_nums)}} line(s), need at least 2")
    sys.exit(1)

# Ensure they're spread across different methods (not duplicated in one place)
if abs(store_line_nums[-1] - store_line_nums[0]) < 30:
    print(f"FAIL: All store calls within 30 lines (lines {{store_line_nums}}) — likely same function")
    sys.exit(1)

print(f"PASS: found {{len(store_calls)}} store syncs at lines {{store_line_nums}}")
""")
    assert r.returncode == 0, f"Mutation sync check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Git repository integrity checks
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_git_valid():
    """Git repository is valid and has expected commit (pass_to_pass).

    Verifies that the git checkout is not corrupted and the expected
    base commit is present. This catches incomplete clones or corruption.
    """
    r = subprocess.run(
        ["git", "-C", REPO, "rev-parse", "--verify", "e513488d0d3bc19ae9b16b08ef43add7e4faab7c"],
        capture_output=True, text=True, timeout=30
    )
    assert r.returncode == 0, f"Git commit check failed: {r.stderr}"
    assert "e513488d0d3bc19ae9b16b08ef43add7e4faab7c" in r.stdout
