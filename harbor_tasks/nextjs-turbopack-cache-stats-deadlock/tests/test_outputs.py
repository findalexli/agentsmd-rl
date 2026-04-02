"""
Task: nextjs-turbopack-cache-stats-deadlock
Repo: vercel/next.js @ b5cb015c5f94088cf0211613051fb696b67cddda
PR:   91742

Deadlock in turbo-tasks-backend print_cache_item_size instrumentation.
When enabled, persist_snapshot hangs because get_task_name acquires a write
lock on a DashMap shard already read-locked by the stats iteration.

All checks are structural (file inspection) because this is Rust code in the
turbopack workspace (~200+ crates); cargo check would exceed test timeout and
the deadlock is a runtime concurrency issue needing the full turbo-tasks runtime.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/next.js"
MOD_FILE = f"{REPO}/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs"
CARGO_FILE = f"{REPO}/turbopack/crates/turbo-tasks-backend/Cargo.toml"


def _read_mod() -> str:
    return Path(MOD_FILE).read_text()


def _read_cargo() -> str:
    return Path(CARGO_FILE).read_text()


def _cfg_blocks(src: str):
    """Yield (start_line, block_text) for each cfg(print_cache_item_size*) block."""
    lines = src.split("\n")
    in_cfg = False
    depth = 0
    block_lines = []
    start = 0
    for i, line in enumerate(lines):
        if 'cfg(feature = "print_cache_item_size' in line:
            in_cfg = True
            depth = 0
            block_lines = []
            start = i
            continue
        if in_cfg:
            depth += line.count("{") - line.count("}")
            block_lines.append(line)
            if depth <= 0 and "{" not in line and "}" not in line:
                yield start, "\n".join(block_lines)
                in_cfg = False
                depth = 0
                block_lines = []
    if block_lines:
        yield start, "\n".join(block_lines)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_source_files_exist():
    """Required source files exist and mod.rs is not stubbed."""
    assert Path(MOD_FILE).is_file(), f"{MOD_FILE} missing"
    assert Path(CARGO_FILE).is_file(), f"{CARGO_FILE} missing"
    lines = Path(MOD_FILE).read_text().split("\n")
    assert len(lines) >= 500, (
        f"mod.rs only {len(lines)} lines — likely stubbed or truncated"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_deadlock_pattern_removed():
    """self.get_task_name must not appear in stats.entry() calls or inside
    any cfg(print_cache_item_size) block, AND stats collection code must
    still exist (anti-deletion)."""
    src = _read_mod()

    # Part A: stats.entry() must not call self.get_task_name
    entry_calls = re.findall(r"\.entry\(([^)]*self\.get_task_name[^)]*)\)", src)
    assert not entry_calls, (
        f"stats.entry() still calls self.get_task_name (deadlock source): "
        f"{entry_calls[0][:80]}"
    )

    # Part B: self.get_task_name must not appear in any cfg block
    for start, block in _cfg_blocks(src):
        for j, line in enumerate(block.split("\n")):
            assert "self.get_task_name" not in line, (
                f"self.get_task_name at ~line {start + j + 2} inside "
                f"cfg(print_cache_item_size) block"
            )

    # Part C: .entry() call must still exist in a cfg block (can't just delete stats)
    found_entry = any(".entry(" in block for _, block in _cfg_blocks(src))
    assert found_entry, (
        "No .entry() call found in cfg(print_cache_item_size) blocks — "
        "stats code deleted?"
    )


# [pr_diff] fail_to_pass
def test_task_name_from_storage():
    """Task name must be derived from the storage reference (inner/storage),
    not from self (which re-locks) and not from a hardcoded string literal."""
    src = _read_mod()
    lines = src.split("\n")

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
            depth += line.count("{") - line.count("}")
            if ".entry(" in line:
                context = "\n".join(lines[max(0, i - 8) : i + 5])
                entry_contexts.append((i + 1, line.strip(), context))
            if depth <= 0 and "{" not in line and "}" not in line:
                in_cfg = False
                depth = 0

    assert entry_contexts, "No .entry() call found in cfg blocks"

    for lineno, entry_line, context in entry_contexts:
        # Reject: string literal argument
        assert not re.search(r'\.entry\(\s*"', entry_line), (
            f"line {lineno}: .entry() uses a string literal — stats not grouped by task"
        )
        # Reject: String::new() / String::from()
        assert not re.search(r"\.entry\(\s*String::(new|from)", entry_line), (
            f"line {lineno}: .entry() uses String constructor"
        )
        # Reject: self. in entry argument
        assert not re.search(r"\.entry\([^)]*\bself\.", entry_line), (
            f"line {lineno}: .entry() references self — potential deadlock"
        )
        # Accept: context must reference inner/storage for task name derivation
        storage_patterns = [
            r"\binner\b",
            r"\bstorage\b",
            r"\btask_storage\b",
            r"get_persistent_task_type",
            r"task_name\s*\(",
            r"task_type\s*\(",
        ]
        found = any(re.search(pat, context) for pat in storage_patterns)
        assert found, (
            f"line {lineno}: .entry() argument doesn't reference storage/inner"
        )


# [pr_diff] fail_to_pass
def test_cargo_feature_split():
    """print_cache_item_size must not depend on lzzzz; a separate feature
    must extend it with lzzzz for compressed reporting."""
    content = _read_cargo()

    # Parse [features] section
    in_features = False
    features = {}
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped == "[features]":
            in_features = True
            continue
        if in_features and stripped.startswith("[") and stripped != "[features]":
            break
        if in_features and "=" in stripped:
            name, val = stripped.split("=", 1)
            features[name.strip()] = val.strip()

    assert "print_cache_item_size" in features, (
        "print_cache_item_size feature missing from Cargo.toml"
    )
    assert "lzzzz" not in features["print_cache_item_size"], (
        "print_cache_item_size still depends on lzzzz"
    )

    # A separate feature must combine print_cache_item_size + lzzzz
    found_compressed = any(
        name != "print_cache_item_size"
        and "print_cache_item_size" in val
        and "lzzzz" in val
        for name, val in features.items()
    )
    assert found_compressed, (
        "No feature found that extends print_cache_item_size with lzzzz"
    )


# [pr_diff] fail_to_pass
def test_add_counts_covers_data():
    """add_counts must be triggered when data OR meta is modified,
    not just meta-only (the old bug).  The guard `if` that contains
    the .add_counts() call must reference encode_data (or have no
    meta-only gate at all)."""
    src = _read_mod()
    lines = src.split("\n")

    # Find every .add_counts( call site (skip the fn definition)
    call_sites = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if ".add_counts(" in stripped and not stripped.startswith("fn "):
            call_sites.append(i)

    assert call_sites, "No .add_counts() call sites found"

    # For each call site, walk upward to find the nearest `if` guard
    ok = False
    for idx in call_sites:
        for j in range(idx - 1, max(idx - 8, -1), -1):
            guard = lines[j].strip()
            if guard.startswith("if "):
                # The guard condition must include encode_data (or be unconditional)
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

    assert ok, (
        "add_counts still guarded by encode_meta only — "
        "data-only tasks excluded from stats"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_persist_snapshot_and_stats_struct_intact():
    """persist_snapshot method and TaskCacheStats struct with core fields
    must still exist."""
    src = _read_mod()

    assert "fn snapshot_and_persist" in src, "snapshot_and_persist method missing"
    assert "struct TaskCacheStats" in src, "TaskCacheStats struct missing"

    # Extract struct body
    struct_match = re.search(r"struct TaskCacheStats\s*\{", src)
    assert struct_match, "TaskCacheStats struct declaration not found"
    start = struct_match.end()
    depth = 1
    pos = start
    while pos < len(src) and depth > 0:
        if src[pos] == "{":
            depth += 1
        elif src[pos] == "}":
            depth -= 1
        pos += 1
    struct_body = src[start:pos]

    for field in ["data:", "data_count:", "meta:", "meta_count:", "upper_count:"]:
        assert field in struct_body, (
            f"TaskCacheStats missing required field '{field}'"
        )


# [static] pass_to_pass
def test_cfg_blocks_not_stubbed():
    """cfg(print_cache_item_size) blocks must have meaningful code (>15 lines),
    stats Mutex/HashMap must exist, and TaskCacheStats impl must have >=2 methods."""
    src = _read_mod()

    # Count non-comment lines in cfg blocks
    cfg_lines = 0
    for _, block in _cfg_blocks(src):
        for line in block.split("\n"):
            stripped = line.strip()
            if stripped and not stripped.startswith("//"):
                cfg_lines += 1

    assert cfg_lines >= 15, (
        f"Only {cfg_lines} non-comment lines in cfg(print_cache_item_size) blocks "
        f"— instrumentation code deleted?"
    )

    # Stats collection infrastructure
    assert "Mutex<" in src and "TaskCacheStats" in src, (
        "Stats collection infrastructure (Mutex + TaskCacheStats) missing"
    )

    # TaskCacheStats impl with methods
    impl_match = re.search(r"impl\s+TaskCacheStats\s*\{", src)
    assert impl_match, "No impl block for TaskCacheStats"

    start = impl_match.end()
    depth = 1
    pos = start
    while pos < len(src) and depth > 0:
        if src[pos] == "{":
            depth += 1
        elif src[pos] == "}":
            depth -= 1
        pos += 1
    impl_body = src[start:pos]
    fn_count = len(re.findall(r"\bfn\s+\w+", impl_body))
    assert fn_count >= 2, (
        f"TaskCacheStats impl has only {fn_count} methods — likely stubbed"
    )
