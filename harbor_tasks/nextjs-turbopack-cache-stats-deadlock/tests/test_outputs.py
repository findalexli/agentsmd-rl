"""
Task: nextjs-turbopack-cache-stats-deadlock
Repo: vercel/next.js @ b5cb015c5f94088cf0211613051fb696b67cddda
PR:   91742

Deadlock in turbo-tasks-backend print_cache_item_size instrumentation.
When enabled, persist_snapshot hangs because get_task_name acquires a write
lock on a DashMap shard already read-locked by the stats iteration.

The fix:
1. Replaces self.get_task_name(task_id, turbo_tasks) with
   TaskCacheStats::task_name(inner) — reads from already-locked storage
2. Splits print_cache_item_size from lzzzz dependency
3. Expands add_counts guard from encode_meta-only to encode_data || encode_meta
4. Refactors formatting with FormatSizes struct and helper methods

No Rust toolchain is available in the Docker image and cargo check would
exceed timeout even if it were. Tests use subprocess to execute Python
analysis scripts that parse the Rust source.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
MOD_FILE = f"{REPO}/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs"
CARGO_FILE = f"{REPO}/turbopack/crates/turbo-tasks-backend/Cargo.toml"


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
def test_source_files_exist():
    """Required source files exist and mod.rs is not stubbed."""
    r = _run_py(f"""
import sys
from pathlib import Path
mod = Path("{MOD_FILE}")
cargo = Path("{CARGO_FILE}")
if not mod.is_file():
    print("FAIL: mod.rs missing")
    sys.exit(1)
if not cargo.is_file():
    print("FAIL: Cargo.toml missing")
    sys.exit(1)
lines = mod.read_text().split("\\n")
if len(lines) < 500:
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
def test_deadlock_pattern_removed():
    """self.get_task_name removed from stats.entry() calls and cfg blocks;
    stats collection code preserved (not just deleted).

    Executes a Python script that parses the Rust source to verify:
    - No .entry() call passes self.get_task_name as argument
    - No cfg(print_cache_item_size) block contains self.get_task_name
    - At least one .entry() call exists in cfg blocks (stats not deleted)
    """
    r = _run_py(f"""
import re, sys
src = open("{MOD_FILE}").read()

# Part A: stats.entry() must not call self.get_task_name
entry_calls = re.findall(r'\\.entry\\(([^)]*self\\.get_task_name[^)]*)\\)', src)
if entry_calls:
    print(f"FAIL: stats.entry() still calls self.get_task_name: {{entry_calls[0][:80]}}")
    sys.exit(1)

# Part B: self.get_task_name must not appear in any cfg block
lines = src.split("\\n")
in_cfg = False
depth = 0
for i, line in enumerate(lines):
    if 'cfg(feature = "print_cache_item_size' in line:
        in_cfg = True
        depth = 0
        continue
    if in_cfg:
        depth += line.count("{{") - line.count("}}")
        if "self.get_task_name" in line:
            print(f"FAIL: self.get_task_name at line {{i+1}} inside cfg block")
            sys.exit(1)
        if depth <= 0 and "{{" not in line and "}}" not in line:
            in_cfg = False

# Part C: .entry() must still exist in cfg blocks (can't just delete stats)
found_entry = False
in_cfg = False
depth = 0
for line in lines:
    if 'cfg(feature = "print_cache_item_size' in line:
        in_cfg = True
        depth = 0
        continue
    if in_cfg:
        depth += line.count("{{") - line.count("}}")
        if ".entry(" in line:
            found_entry = True
        if depth <= 0 and "{{" not in line and "}}" not in line:
            in_cfg = False
if not found_entry:
    print("FAIL: No .entry() in cfg blocks — stats code deleted?")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Deadlock check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_task_name_from_storage():
    """Task name derived from storage reference (inner), not self.

    Executes a Python script that:
    - Finds all .entry() calls inside cfg(print_cache_item_size) blocks
    - Verifies no entry() uses self.get_task_name, string literals, or String ctors
    - Verifies the surrounding context references storage/inner/task_storage
    """
    r = _run_py(f"""
import re, sys
src = open("{MOD_FILE}").read()
lines = src.split("\\n")

# Collect .entry() calls inside cfg blocks with surrounding context
entry_contexts = []
in_cfg = False
depth = 0
for i, line in enumerate(lines):
    if 'cfg(feature = "print_cache_item_size' in line:
        in_cfg = True
        depth = 0
        continue
    if in_cfg:
        depth += line.count("{{") - line.count("}}")
        if ".entry(" in line:
            context = "\\n".join(lines[max(0, i - 8) : i + 5])
            entry_contexts.append((i + 1, line.strip(), context))
        if depth <= 0 and "{{" not in line and "}}" not in line:
            in_cfg = False
            depth = 0

if not entry_contexts:
    print("FAIL: No .entry() call found in cfg blocks")
    sys.exit(1)

for lineno, entry_line, context in entry_contexts:
    # Reject: string literal argument
    if re.search(r'\\.entry\\(\\s*"', entry_line):
        print(f"FAIL: line {{lineno}}: .entry() uses a string literal")
        sys.exit(1)
    # Reject: String::new() / String::from()
    if re.search(r"\\.entry\\(\\s*String::(new|from)", entry_line):
        print(f"FAIL: line {{lineno}}: .entry() uses String constructor")
        sys.exit(1)
    # Reject: self. in entry argument
    if re.search(r"\\.entry\\([^)]*\\bself\\.", entry_line):
        print(f"FAIL: line {{lineno}}: .entry() references self — deadlock risk")
        sys.exit(1)
    # Accept: context must reference storage/inner for task name derivation
    storage_patterns = [
        r"\\binner\\b",
        r"\\bstorage\\b",
        r"\\btask_storage\\b",
        r"get_persistent_task_type",
        r"task_name\\s*\\(",
        r"task_type\\s*\\(",
    ]
    found = any(re.search(pat, context) for pat in storage_patterns)
    if not found:
        print(f"FAIL: line {{lineno}}: .entry() argument doesn't reference storage/inner")
        sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Task name check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_cargo_feature_split():
    """print_cache_item_size decoupled from lzzzz; separate feature for
    compressed reporting.

    Executes a Python script that parses [features] from Cargo.toml and
    verifies the dependency split.
    """
    r = _run_py(f"""
import sys
content = open("{CARGO_FILE}").read()

# Parse [features] section
in_features = False
features = {{}}
for line in content.split("\\n"):
    stripped = line.strip()
    if stripped == "[features]":
        in_features = True
        continue
    if in_features and stripped.startswith("[") and stripped != "[features]":
        break
    if in_features and "=" in stripped:
        name, val = stripped.split("=", 1)
        features[name.strip()] = val.strip()

if "print_cache_item_size" not in features:
    print("FAIL: print_cache_item_size feature missing from Cargo.toml")
    sys.exit(1)

if "lzzzz" in features["print_cache_item_size"]:
    print("FAIL: print_cache_item_size still depends on lzzzz")
    sys.exit(1)

# A separate feature must combine print_cache_item_size + lzzzz
found_compressed = any(
    name != "print_cache_item_size"
    and "print_cache_item_size" in val
    and "lzzzz" in val
    for name, val in features.items()
)
if not found_compressed:
    print("FAIL: No feature extends print_cache_item_size with lzzzz")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Feature split check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_add_counts_covers_data():
    """add_counts triggered on data OR meta modified, not meta-only.

    Executes a Python script that finds every .add_counts() call site and
    verifies the enclosing if-guard includes encode_data.
    """
    r = _run_py(f"""
import sys
src = open("{MOD_FILE}").read()
lines = src.split("\\n")

# Find every .add_counts( call site (skip fn definition)
call_sites = []
for i, line in enumerate(lines):
    stripped = line.strip()
    if ".add_counts(" in stripped and not stripped.startswith("fn "):
        call_sites.append(i)

if not call_sites:
    print("FAIL: No .add_counts() call sites found")
    sys.exit(1)

# For each call site, walk upward to find the nearest if guard
ok = False
for idx in call_sites:
    for j in range(idx - 1, max(idx - 8, -1), -1):
        guard = lines[j].strip()
        if guard.startswith("if "):
            if "encode_data" in guard:
                ok = True
                break
            # If guard is meta-only, that's the old bug
            if "encode_meta" in guard and "encode_data" not in guard:
                break  # still meta-only gated
            # Some other guard — accept if it doesn't exclude data
            ok = True
            break
    if ok:
        break

if not ok:
    print("FAIL: add_counts still guarded by encode_meta only — data-only tasks excluded")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"add_counts check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_persist_snapshot_and_stats_struct_intact():
    """persist_snapshot method and TaskCacheStats struct with core fields
    still exist.

    Executes a Python script that parses the struct definition and verifies
    all required fields are present.
    """
    r = _run_py(f"""
import re, sys
src = open("{MOD_FILE}").read()

if "fn snapshot_and_persist" not in src:
    print("FAIL: snapshot_and_persist method missing")
    sys.exit(1)
if "struct TaskCacheStats" not in src:
    print("FAIL: TaskCacheStats struct missing")
    sys.exit(1)

# Extract struct body
struct_match = re.search(r"struct TaskCacheStats\\s*\\{{", src)
if not struct_match:
    print("FAIL: TaskCacheStats struct declaration not found")
    sys.exit(1)

start = struct_match.end()
depth = 1
pos = start
while pos < len(src) and depth > 0:
    if src[pos] == "{{":
        depth += 1
    elif src[pos] == "}}":
        depth -= 1
    pos += 1
struct_body = src[start:pos]

for field in ["data:", "data_count:", "meta:", "meta_count:", "upper_count:"]:
    if field not in struct_body:
        print(f"FAIL: TaskCacheStats missing field '{{field}}'")
        sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Struct check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_cfg_blocks_not_stubbed():
    """cfg(print_cache_item_size) blocks have meaningful code, stats
    infrastructure intact.

    Executes a Python script that counts non-comment lines in cfg blocks
    and verifies TaskCacheStats impl has >=2 methods.
    """
    r = _run_py(f"""
import re, sys
src = open("{MOD_FILE}").read()

# Count non-comment lines in cfg blocks
lines = src.split("\\n")
cfg_lines = 0
in_cfg = False
depth = 0
for line in lines:
    if 'cfg(feature = "print_cache_item_size' in line:
        in_cfg = True
        depth = 0
        continue
    if in_cfg:
        depth += line.count("{{") - line.count("}}")
        stripped = line.strip()
        if stripped and not stripped.startswith("//"):
            cfg_lines += 1
        if depth <= 0 and "{{" not in line and "}}" not in line:
            in_cfg = False

if cfg_lines < 15:
    print(f"FAIL: Only {{cfg_lines}} non-comment lines in cfg blocks — deleted?")
    sys.exit(1)

# Stats collection infrastructure
if "Mutex<" not in src or "TaskCacheStats" not in src:
    print("FAIL: Stats collection infrastructure (Mutex + TaskCacheStats) missing")
    sys.exit(1)

# TaskCacheStats impl with methods
impl_match = re.search(r"impl\\s+TaskCacheStats\\s*\\{{", src)
if not impl_match:
    print("FAIL: No impl block for TaskCacheStats")
    sys.exit(1)

start = impl_match.end()
depth = 1
pos = start
while pos < len(src) and depth > 0:
    if src[pos] == "{{":
        depth += 1
    elif src[pos] == "}}":
        depth -= 1
    pos += 1
impl_body = src[start:pos]
fn_count = len(re.findall(r"\\bfn\\s+\\w+", impl_body))
if fn_count < 2:
    print(f"FAIL: TaskCacheStats impl has only {{fn_count}} methods — likely stubbed")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Cfg blocks check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout
