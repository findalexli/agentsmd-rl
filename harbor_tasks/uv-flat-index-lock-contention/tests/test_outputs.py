"""
Task: uv-flat-index-lock-contention
Repo: astral-sh/uv @ 9d45e7f8177e6f60e084ba52b2a32a56edf237c7
PR:   18659

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/repo")
FILE = REPO / "crates" / "uv-client" / "src" / "registry_client.rs"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_flat_single_index_body() -> str:
    """Extract the flat_single_index method body from registry_client.rs."""
    source = FILE.read_text()
    # Match from fn signature to the next method at the same indent level
    match = re.search(
        r"(fn flat_single_index\b.*?)(\n    (?:pub\s+)?(?:async\s+)?fn\s)",
        source,
        re.DOTALL,
    )
    if not match:
        match = re.search(r"(fn flat_single_index\b.*?)(\n\})", source, re.DOTALL)
    assert match, "flat_single_index method not found in registry_client.rs"
    return match.group(1)


def strip_rust_comments(code: str) -> str:
    """Remove // and /* */ comments from Rust source."""
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    return code


def cargo_check(*packages: str, timeout: int = 300) -> subprocess.CompletedProcess:
    cmd = ["cargo", "check"]
    for p in packages:
        cmd += ["-p", p]
    return subprocess.run(cmd, cwd=REPO, capture_output=True, timeout=timeout)


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compilation():
    """uv-client crate must compile after changes."""
    r = cargo_check("uv-client")
    assert r.returncode == 0, (
        f"Compilation failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# AST-only because: Rust async crate, cannot import/call from Python
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_lock_not_held_across_fetch():
    """Cache-level lock must NOT be held across the fetch_index network call.

    The bug: self.flat_indexes.lock().await holds MutexGuard across the entire
    method including the network fetch. Any correct fix releases the cache-level
    lock before fetch_index is called.

    Accepts: scoped blocks, explicit drop(), DashMap, per-index locks, RwLock,
    fetch-first-then-lock, or any pattern that avoids holding the global lock
    across the .await point.
    """
    source = FILE.read_text()

    # --- Pattern A: DashMap replaces Mutex-based cache ---
    if "DashMap" in source and "FlatIndexCache" in source:
        return

    body = get_flat_single_index_body()
    code = strip_rust_comments(body)
    lines = code.split("\n")

    # Find lines with cache-level lock and fetch_index call
    lock_lines = []
    fetch_lines = []
    for i, line in enumerate(lines):
        if ".lock().await" in line and (
            "flat_index" in line.lower()
            or "cache" in line.lower()
            or "self." in line
        ):
            lock_lines.append(i)
        if "fetch_index" in line:
            fetch_lines.append(i)

    assert fetch_lines, "fetch_index call not found — method may have been hollowed out"

    if not lock_lines:
        # No cache-level lock in method — valid (lock moved elsewhere or DashMap)
        return

    first_lock = min(lock_lines)
    first_fetch = min(fetch_lines)

    if first_lock >= first_fetch:
        # Lock comes AFTER fetch — valid fix pattern
        return

    # The lock is acquired before fetch. Check if the MutexGuard is released
    # before the fetch_index call. We look for evidence the guard's scope ends.
    between = "\n".join(lines[first_lock:first_fetch])

    # Extract the guard variable name (e.g., "cache" from "let mut cache = ...lock().await")
    lock_line = lines[first_lock]
    guard_match = re.search(r"let\s+(?:mut\s+)?(\w+)\s*=.*\.lock\(\)\.await", lock_line)
    guard_name = guard_match.group(1) if guard_match else None

    # Method 1: Explicit drop() of the guard
    if guard_name and re.search(rf"drop\s*\(\s*{re.escape(guard_name)}\s*\)", between):
        return
    if re.search(r"drop\s*\(", between):
        return

    # Method 2: Lock is inside a scoped block (`let x = { ... lock ... }; fetch_index`)
    # The lock line must be inside a block expression that closes before fetch
    if guard_name:
        # Check if the guard binding is inside a `let x = { ... };` block
        lock_line_stripped = lock_line.strip()
        # Look backward from the lock line to see if we're inside a block
        pre_lock = "\n".join(lines[:first_lock + 1])
        # Pattern: `let something = {` ... `lock().await` ... `};`
        # Find the innermost block containing the lock
        block_start = None
        depth = 0
        for j in range(first_lock, -1, -1):
            for ch in reversed(lines[j]):
                if ch == "}":
                    depth += 1
                elif ch == "{":
                    if depth == 0:
                        block_start = j
                        break
                    depth -= 1
            if block_start is not None:
                break

        if block_start is not None:
            # Find matching close brace
            depth = 0
            block_end = None
            for j in range(block_start, len(lines)):
                for ch in lines[j]:
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0:
                            block_end = j
                            break
                if block_end is not None:
                    break
            if block_end is not None and block_end < first_fetch:
                return

    # Method 3: Guard variable is NOT referenced after the block where it's used
    # (i.e., it's shadowed or the name doesn't appear between the lock's block
    # and fetch_index). This handles `let slot = { let mut c = lock(); ... }; fetch()`
    if guard_name:
        # Find where the guard is last used
        post_lock_lines = lines[first_lock + 1:first_fetch]
        guard_used_after = any(guard_name in line for line in post_lock_lines
                               if "drop" not in line and ".lock()" not in line)
        if not guard_used_after:
            # Guard may be in a scoped block with no further use — check brace scoping
            # If the lock line is inside an expression block that ends before fetch
            pass

    assert False, (
        "Cache-level lock is still held across fetch_index — "
        "the global Mutex guard must be released before the network call"
    )


# [pr_diff] fail_to_pass
def test_cache_restructured_for_concurrency():
    """FlatIndexCache must support per-index concurrent access.

    The old cache stored entries directly as FxHashMap<IndexUrl, FxHashMap<...>>.
    A correct fix changes the cache to support per-index granularity.

    Accepts: per-index Mutex/RwLock/OnceCell slots, DashMap, entry API with Arc,
    or any restructuring that removes the direct mapping.
    """
    source = FILE.read_text()
    code = strip_rust_comments(source)

    # Pattern 1: DashMap (inherently concurrent per-key)
    if "DashMap" in code:
        return

    # Pattern 2: Per-index Mutex/RwLock slot
    if re.search(r"Arc<(?:Mutex|RwLock)<Option<", code):
        return

    # Pattern 3: Per-index OnceCell or Lazy
    if "OnceCell" in code or "OnceLock" in code:
        return

    # Pattern 4: Cache struct field no longer stores PackageName directly
    cache_struct = re.search(
        r"struct FlatIndexCache\s*[\({]([^)}]*)[\)}]", code, re.DOTALL
    )
    if cache_struct:
        fields = cache_struct.group(1)
        if "PackageName" not in fields:
            return

    # Pattern 5: Type alias for a per-index slot
    if re.search(r"type\s+\w*(?:Slot|Entry|Cell)\w*\s*=\s*Arc<", code):
        return

    assert False, (
        "FlatIndexCache not restructured for per-index concurrency. "
        "Expected DashMap, per-index slots, or similar."
    )


# [pr_diff] fail_to_pass
def test_global_insert_removed():
    """Old cache.insert(index.clone(), entries) pattern must be removed.

    The bug pattern writes fetched data via cache.insert() while the global
    cache lock is held. Any correct fix replaces this with per-index writes.
    """
    body = get_flat_single_index_body()
    assert not re.search(r"cache\.insert.*index", body), (
        "Global-lock cache.insert(index, ...) pattern still present in flat_single_index"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_fetch_logic_preserved():
    """flat_single_index must still call fetch_index to retrieve index data."""
    body = get_flat_single_index_body()
    assert "fetch_index" in body, (
        "flat_single_index no longer calls fetch_index — core fetch logic removed"
    )


# [pr_diff] pass_to_pass
def test_package_lookup_preserved():
    """flat_single_index must still look up entries by package_name."""
    body = get_flat_single_index_body()
    assert "package_name" in body, (
        "flat_single_index no longer references package_name — lookup logic removed"
    )


# ---------------------------------------------------------------------------
# Anti-stub (static) — pass_to_pass
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """flat_single_index has substantial implementation, not placeholders."""
    body = get_flat_single_index_body()

    assert "todo!()" not in body.lower(), "flat_single_index contains todo!()"
    assert "unimplemented!()" not in body, "flat_single_index contains unimplemented!()"

    non_empty = [
        line
        for line in body.split("\n")
        if line.strip() and not line.strip().startswith("//")
    ]
    assert len(non_empty) >= 15, (
        f"flat_single_index has only {len(non_empty)} non-empty lines — "
        "expected at least 15 for a substantive implementation"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# AST-only because: Rust crate, cannot import/call from Python
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ 9d45e7f8177e6f60e084ba52b2a32a56edf237c7
def test_no_unwrap_panic():
    """No .unwrap(), panic!(), or unreachable!() in flat_single_index (CLAUDE.md:7)."""
    body = strip_rust_comments(get_flat_single_index_body())
    for pattern, label in [
        (r"\.unwrap\(\)", ".unwrap()"),
        (r"panic!\(", "panic!()"),
        (r"unreachable!\(", "unreachable!()"),
    ]:
        assert not re.search(pattern, body), (
            f"Found {label} in flat_single_index — "
            "CLAUDE.md:7 says to avoid panic!/unreachable!/.unwrap()"
        )


# [agent_config] pass_to_pass — CLAUDE.md:7 @ 9d45e7f8177e6f60e084ba52b2a32a56edf237c7
def test_no_unsafe_code():
    """No unsafe blocks in flat_single_index (CLAUDE.md:7)."""
    body = strip_rust_comments(get_flat_single_index_body())
    assert not re.search(r"\bunsafe\s*\{", body), (
        "Found unsafe block in flat_single_index — "
        "CLAUDE.md:7 says to avoid unsafe code"
    )


# [agent_config] pass_to_pass — CLAUDE.md:7 @ 9d45e7f8177e6f60e084ba52b2a32a56edf237c7
def test_no_clippy_ignores():
    """No #[allow(clippy::...)] in flat_single_index (CLAUDE.md:7)."""
    body = strip_rust_comments(get_flat_single_index_body())
    assert not re.search(r"#\[allow\(clippy::", body), (
        "Found #[allow(clippy::...)] in flat_single_index — "
        "CLAUDE.md:7 says to avoid clippy rule ignores"
    )


# [agent_config] pass_to_pass — CLAUDE.md:16-17 @ 9d45e7f8177e6f60e084ba52b2a32a56edf237c7
def test_no_shortened_names():
    """No abbreviated variable names in flat_single_index (CLAUDE.md:16-17)."""
    body = strip_rust_comments(get_flat_single_index_body())
    short_names = re.findall(r"\blet\s+(idx|ent|pkg|res|val|ret|tmp|buf)\b", body)
    assert not short_names, (
        f"Found shortened variable name(s): {short_names} — "
        "CLAUDE.md:16-17 says to avoid shortening variable names"
    )
