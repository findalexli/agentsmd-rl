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
    assert r.returncode == 0, f"Source check failed: {r.stdout}\\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_deadlock_pattern_removed():
    """The deadlock-causing self.get_task_name pattern is removed from stats code.

    Verifies that the fix for the RwLock deadlock has been applied:
    - No .entry() call passes self.get_task_name (which would re-lock)
    - No cfg(print_cache_item_size) block contains self.get_task_name
    - Stats collection code still exists (not just deleted to avoid the bug)
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
cfg_start_line = 0
depth = 0
for i, line in enumerate(lines):
    if 'cfg(feature = "print_cache_item_size' in line:
        in_cfg = True
        cfg_start_line = i + 1
        depth = 0
        continue
    if in_cfg:
        depth += line.count("{{") - line.count("}}")
        if "self.get_task_name" in line:
            print(f"FAIL: self.get_task_name at line {{i+1}} inside cfg block starting at {{cfg_start_line}}")
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
    print("FAIL: No .entry() in cfg blocks — stats code deleted instead of fixed")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Deadlock check failed: {r.stdout}\\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_task_name_from_storage():
    """Task name is derived from storage reference, not via self re-lock.

    Verifies that TaskCacheStats::task_name(inner) is used instead of
    self.get_task_name(task_id, turbo_tasks), which would cause deadlock
    by trying to acquire a write lock while holding a read lock.
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
    # Reject: string literal argument (would be a stub)
    if re.search(r'\\.entry\\(\\s*"', entry_line):
        print(f"FAIL: line {{lineno}}: .entry() uses a string literal — likely stubbed")
        sys.exit(1)
    # Reject: String::new() / String::from() (would be a stub)
    if re.search(r"\\.entry\\(\\s*String::(new|from)", entry_line):
        print(f"FAIL: line {{lineno}}: .entry() uses String constructor — likely stubbed")
        sys.exit(1)
    # Reject: self. in entry argument (deadlock risk)
    if re.search(r"\\.entry\\([^)]*\\bself\\.", entry_line):
        print(f"FAIL: line {{lineno}}: .entry() references self — deadlock risk")
        sys.exit(1)
    # Accept: context must reference storage/inner for task name derivation
    # The fix uses TaskCacheStats::task_name(inner) which extracts from storage
    storage_patterns = [
        r"TaskCacheStats::task_name",
        r"task_name\\s*\\(\\s*inner",
        r"task_name\\s*\\(\\s*storage",
        r"\\binner\\b.*get_persistent_task_type",
        r"\\bstorage\\b.*get_persistent_task_type",
    ]
    found = any(re.search(pat, context) for pat in storage_patterns)
    if not found:
        print(f"FAIL: line {{lineno}}: .entry() argument doesn't reference correct task name source")
        print(f"Context: {{context[:200]}}")
        sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Task name check failed: {r.stdout}\\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_cargo_feature_split():
    """Cargo feature dependencies correctly split between basic and compressed.

    Verifies that:
    1. print_cache_item_size exists as a standalone feature (no lzzzz dep)
    2. A separate feature extends it with lzzzz for compressed reporting
    This allows using the stats without pulling in the lz4 dependency.
    """
    r = _run_py(f"""
import re, sys
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
    if in_features and "=" in stripped and not stripped.startswith("#"):
        name, val = stripped.split("=", 1)
        features[name.strip()] = val.strip()

if "print_cache_item_size" not in features:
    print("FAIL: print_cache_item_size feature missing from Cargo.toml")
    sys.exit(1)

# Basic feature must NOT depend on lzzzz
if "lzzzz" in features["print_cache_item_size"]:
    print("FAIL: print_cache_item_size still depends on lzzzz (should be standalone)")
    sys.exit(1)

# Must have a separate feature for compressed reporting
found_compressed = False
for name, val in features.items():
    if name != "print_cache_item_size":
        if "print_cache_item_size" in val and "lzzzz" in val:
            found_compressed = True
            break

if not found_compressed:
    print("FAIL: No feature combines print_cache_item_size with lzzzz for compressed reporting")
    sys.exit(1)

# Verify standalone feature is not empty (must enable something)
if features["print_cache_item_size"] == "[]":
    print("PASS_EMPTY")  # Empty is valid for this fix
else:
    print("PASS_WITH_DEPS")
print("PASS")
""")
    assert r.returncode == 0, f"Feature split check failed: {r.stdout}\\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_add_counts_covers_data():
    """add_counts called when data OR meta modified, not meta-only.

    The original bug: add_counts was only called when encode_meta was true,
    missing tasks that only had data modifications. After fix, it should be
    called when encode_data || encode_meta.
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

# For each call site, check the enclosing if-guard
all_ok = True
for idx in call_sites:
    found_guard = False
    ok_for_this_site = False
    for j in range(idx - 1, max(idx - 10, -1), -1):
        guard = lines[j].strip()
        if guard.startswith("if "):
            found_guard = True
            # Must include encode_data (not meta-only)
            if "encode_data" in guard:
                ok_for_this_site = True
            elif "encode_meta" in guard and "encode_data" not in guard:
                ok_for_this_site = False  # Still meta-only gated
            else:
                ok_for_this_site = True  # Some other guard that doesn't exclude data
            break
    if not found_guard or not ok_for_this_site:
        all_ok = False
        break

if not all_ok:
    print("FAIL: add_counts still guarded by encode_meta only — data-only tasks excluded from stats")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"add_counts check failed: {r.stdout}\\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_formatsizes_struct_exists():
    """FormatSizes helper struct exists for DRY size formatting.

    Part of the fix refactors the duplicated size formatting code into
    a FormatSizes struct with Display implementation.
    """
    r = _run_py(f"""
import re, sys
src = open("{MOD_FILE}").read()

# Check for FormatSizes struct
if "struct FormatSizes" not in src:
    print("FAIL: FormatSizes struct not found")
    sys.exit(1)

# Check for Display impl
if "impl std::fmt::Display for FormatSizes" not in src:
    print("FAIL: Display impl for FormatSizes not found")
    sys.exit(1)

# Check for conditional compressed_size field
if '#[cfg(feature = "print_cache_item_size_with_compressed")]' not in src:
    print("FAIL: cfg gating for compressed feature not found")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"FormatSizes check failed: {r.stdout}\\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_persist_snapshot_and_stats_struct_intact():
    """persist_snapshot method and TaskCacheStats struct with core fields exist.

    Regression test: verifies that the fix didn't delete essential infrastructure.
    These elements exist on both base commit and after the fix.
    """
    r = _run_py(f"""
import re, sys
src = open("{MOD_FILE}").read()

# Check essential methods and types exist (both base and fix)
if "fn snapshot_and_persist" not in src:
    print("FAIL: snapshot_and_persist method missing")
    sys.exit(1)
if "struct TaskCacheStats" not in src:
    print("FAIL: TaskCacheStats struct missing")
    sys.exit(1)

# Extract struct body for field checking - core fields exist on both base and fix
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

# Core fields that exist on both base and fix
required_fields = ["data:", "data_count:", "meta:", "meta_count:", "upper_count:"]
for field in required_fields:
    if field not in struct_body:
        print(f"FAIL: TaskCacheStats missing required field '{{field}}'")
        sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Struct check failed: {r.stdout}\\n{r.stderr}"
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_cfg_blocks_not_stubbed():
    """cfg(print_cache_item_size) blocks have meaningful code.

    Anti-stub test: verifies stats infrastructure wasn't just stubbed out.
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
    print(f"FAIL: Only {{cfg_lines}} non-comment lines in cfg blocks — likely stubbed")
    sys.exit(1)

# Stats collection infrastructure must exist
if "Mutex<" not in src:
    print("FAIL: Stats collection infrastructure (Mutex) missing")
    sys.exit(1)

# TaskCacheStats must have multiple methods (not just a stub struct)
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
if fn_count < 3:
    print(f"FAIL: TaskCacheStats impl has only {{fn_count}} methods — likely stubbed")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Cfg blocks check failed: {r.stdout}\\n{r.stderr}"
    assert "PASS" in r.stdout
