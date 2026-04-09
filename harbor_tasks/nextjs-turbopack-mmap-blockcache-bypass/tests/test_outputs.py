"""
Task: nextjs-turbopack-mmap-blockcache-bypass
Repo: vercel/next.js @ 16dd58fa25abf87ae891628ce018114a4c333db6
PR:   92390

Skip the BlockCache for uncompressed (mmap-backed) SST blocks and add a
per-file CRC verification bitmap so checksums are verified at most once
per file open for any block. Uncompressed blocks bypass the cache entirely
(an mmap-backed ArcBytes is cheaper than a cache lookup), while compressed
blocks use the cache with bitmap-gated CRC checks.

No Rust toolchain is available in the Docker image — cargo check would
exceed timeout on this monorepo. Tests use subprocess to execute Python
analysis scripts that parse the Rust source.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
SRC_FILE = f"{REPO}/turbopack/crates/turbo-persistence/src/static_sorted_file.rs"


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
    """Source file exists with StaticSortedFile struct and core structure."""
    r = _run_py(f"""
import sys
from pathlib import Path
p = Path("{SRC_FILE}")
if not p.is_file():
    print("FAIL: static_sorted_file.rs missing")
    sys.exit(1)
src = p.read_text()
if "pub struct StaticSortedFile" not in src:
    print("FAIL: StaticSortedFile struct missing")
    sys.exit(1)
if "fn lookup" not in src:
    print("FAIL: lookup method missing")
    sys.exit(1)
lines = src.split("\\n")
if len(lines) < 400:
    print(f"FAIL: file only {{len(lines)}} lines — likely stubbed")
    sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"Source check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_verified_blocks_field():
    """StaticSortedFile struct contains a verified_blocks field typed as
    Box<[AtomicU64]>.

    The fix adds a per-file CRC verification bitmap so that uncompressed
    blocks (which bypass the cache) don't re-verify their checksum on every
    access.
    """
    r = _run_py(f"""
import re, sys
src = open("{SRC_FILE}").read()

# Find StaticSortedFile struct body
match = re.search(r'pub struct StaticSortedFile\\s*\\{{', src)
if not match:
    print("FAIL: StaticSortedFile struct not found")
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
struct_body = src[start:pos]

# Check for verified_blocks field with AtomicU64
if 'verified_blocks' not in struct_body:
    print("FAIL: verified_blocks field missing from StaticSortedFile")
    sys.exit(1)

if 'AtomicU64' not in struct_body:
    print("FAIL: AtomicU64 type not found in StaticSortedFile fields")
    sys.exit(1)

# Must be Box<[AtomicU64]> specifically
if 'Box<[AtomicU64]>' not in struct_body:
    print("FAIL: verified_blocks is not Box<[AtomicU64]>")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"verified_blocks check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_arc_block_cache_reader_struct():
    """ArcBlockCacheReader struct bundles cache + verified_blocks bitmap.

    This struct is the core of the fix: it threads the CRC bitmap through
    the existing generic lookup machinery without changing the trait
    signature. Must have cache and verified_blocks fields and derive
    Clone, Copy.
    """
    r = _run_py(f"""
import re, sys
src = open("{SRC_FILE}").read()

# Check struct exists
if 'struct ArcBlockCacheReader' not in src:
    print("FAIL: ArcBlockCacheReader struct not found")
    sys.exit(1)

# Find the struct definition
match = re.search(r'#\\[derive\\([^)]*Clone[^)]*Copy[^)]*\\)\\s*struct ArcBlockCacheReader', src, re.DOTALL)
if not match:
    # Try alternate order (Copy, Clone)
    match = re.search(r'#\\[derive\\([^)]*Copy[^)]*Clone[^)]*\\)\\s*struct ArcBlockCacheReader', src, re.DOTALL)
if not match:
    print("FAIL: ArcBlockCacheReader must derive Clone, Copy")
    sys.exit(1)

# Extract struct body
struct_match = re.search(r'struct ArcBlockCacheReader[^\\{{]*\\{{', src)
if not struct_match:
    print("FAIL: ArcBlockCacheReader struct body not found")
    sys.exit(1)

start = struct_match.end()
depth = 1
pos = start
while pos < len(src) and depth > 0:
    if src[pos] == '{{':
        depth += 1
    elif src[pos] == '}}':
        depth -= 1
    pos += 1
struct_body = src[start:pos]

# Must have cache and verified_blocks fields
if 'cache' not in struct_body:
    print("FAIL: ArcBlockCacheReader missing 'cache' field")
    sys.exit(1)
if 'verified_blocks' not in struct_body:
    print("FAIL: ArcBlockCacheReader missing 'verified_blocks' field")
    sys.exit(1)

# Anti-stub: must reference BlockCache type
if 'BlockCache' not in struct_body:
    print("FAIL: ArcBlockCacheReader cache field must reference BlockCache type")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"ArcBlockCacheReader check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_get_or_cache_block_function():
    """get_or_cache_block free function replaces per-method cache logic.

    This is the unified block reading function that:
    1. Reads raw block data exactly once
    2. For uncompressed blocks: verifies CRC via bitmap, returns mmap-backed ArcBytes
    3. For compressed blocks: checks cache, decompresses on miss, inserts
    Must accept verified_blocks parameter and use get_raw_block_slice.
    """
    r = _run_py(f"""
import re, sys
src = open("{SRC_FILE}").read()

# Must be a free function (not method)
match = re.search(r'^fn get_or_cache_block\\b', src, re.MULTILINE)
if not match:
    print("FAIL: get_or_cache_block free function not found")
    sys.exit(1)

# Extract function body
fn_start = match.start()
# Find opening brace
brace_pos = src.index('{{', match.end())
depth = 1
pos = brace_pos + 1
while pos < len(src) and depth > 0:
    if src[pos] == '{{':
        depth += 1
    elif src[pos] == '}}':
        depth -= 1
    pos += 1
fn_body = src[brace_pos:pos]

# Must accept verified_blocks parameter
if 'verified_blocks' not in fn_body:
    print("FAIL: get_or_cache_block doesn't use verified_blocks parameter")
    sys.exit(1)

# Must use get_raw_block_slice (single read)
if 'get_raw_block_slice' not in fn_body:
    print("FAIL: get_or_cache_block doesn't call get_raw_block_slice")
    sys.exit(1)

# Must have uncompressed branch (uncompressed_length == 0)
if 'uncompressed_length' not in fn_body:
    print("FAIL: get_or_cache_block doesn't check uncompressed_length")
    sys.exit(1)

# Must verify checksum for uncompressed blocks
if 'verify_checksum' not in fn_body:
    print("FAIL: get_or_cache_block doesn't verify checksums")
    sys.exit(1)

# Anti-stub: must have meaningful branching logic
if fn_body.count('if') < 1:
    print("FAIL: get_or_cache_block lacks conditional logic — likely stubbed")
    sys.exit(1)

# Must return mmap-backed ArcBytes for uncompressed (from_mmap)
if 'from_mmap' not in fn_body:
    print("FAIL: get_or_cache_block doesn't create mmap-backed ArcBytes")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"get_or_cache_block check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_verify_checksum_once_function():
    """verify_checksum_once uses bitmap to avoid redundant CRC checks.

    Uses AtomicU64 bitmap with Relaxed ordering:
    1. Checks if bit already set → skip verification
    2. Calls verify_checksum on miss
    3. Sets bit via fetch_or after successful verification
    Failures are NOT recorded in bitmap (corrupted blocks re-check every time).
    """
    r = _run_py(f"""
import re, sys
src = open("{SRC_FILE}").read()

# Must be a free function
match = re.search(r'^fn verify_checksum_once\\b', src, re.MULTILINE)
if not match:
    print("FAIL: verify_checksum_once free function not found")
    sys.exit(1)

# Extract function body
brace_pos = src.index('{{', match.end())
depth = 1
pos = brace_pos + 1
while pos < len(src) and depth > 0:
    if src[pos] == '{{':
        depth += 1
    elif src[pos] == '}}':
        depth -= 1
    pos += 1
fn_body = src[brace_pos:pos]

# Must use atomic operations
if 'AtomicOrdering' not in fn_body and 'Ordering' not in fn_body:
    print("FAIL: verify_checksum_once doesn't use atomic ordering")
    sys.exit(1)

# Must use .load() to check if already verified
if '.load(' not in fn_body:
    print("FAIL: verify_checksum_once doesn't load bitmap state")
    sys.exit(1)

# Must use fetch_or or equivalent to set the bit
if 'fetch_or' not in fn_body:
    print("FAIL: verify_checksum_once doesn't set bitmap bit (no fetch_or)")
    sys.exit(1)

# Must call verify_checksum for actual verification
if 'verify_checksum(' not in fn_body:
    print("FAIL: verify_checksum_once doesn't call verify_checksum")
    sys.exit(1)

# Anti-stub: function body must have multiple branches
if fn_body.count('if') < 1:
    print("FAIL: verify_checksum_once lacks conditional logic — likely stubbed")
    sys.exit(1)

# Must compute word index and bit from block_index
if 'word_idx' not in fn_body and 'block_index' not in fn_body:
    print("FAIL: verify_checksum_once doesn't compute bitmap position from block_index")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"verify_checksum_once check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_block_weighter_debug_assert():
    """BlockWeighter::weight adds debug_assert against mmap-backed insertion.

    Since uncompressed blocks now bypass the cache, inserting an mmap-backed
    block into BlockCache indicates a logic error. The debug_assert catches
    this in debug builds with a descriptive message.
    """
    r = _run_py(f"""
import re, sys
src = open("{SRC_FILE}").read()

# Find BlockWeighter impl
match = re.search(r'impl.*Weighter.*for BlockWeighter', src)
if not match:
    print("FAIL: BlockWeighter impl not found")
    sys.exit(1)

# Find the weight method within this impl
impl_start = match.start()
brace_pos = src.index('{{', match.end())
depth = 1
pos = brace_pos + 1
while pos < len(src) and depth > 0:
    if src[pos] == '{{':
        depth += 1
    elif src[pos] == '}}':
        depth -= 1
    pos += 1
impl_body = src[brace_pos:pos]

# Find weight method body
weight_match = re.search(r'fn weight\\b.*?\\{\\{', impl_body, re.DOTALL)
if not weight_match:
    print("FAIL: weight method not found in BlockWeighter impl")
    sys.exit(1)

w_brace = impl_body.index('{{', weight_match.start())
w_depth = 1
w_pos = w_brace + 1
while w_pos < len(impl_body) and w_depth > 0:
    if impl_body[w_pos] == '{{':
        w_depth += 1
    elif impl_body[w_pos] == '}}':
        w_depth -= 1
    w_pos += 1
weight_body = impl_body[w_brace:w_pos]

# Must have debug_assert
if 'debug_assert' not in weight_body:
    print("FAIL: weight method doesn't contain debug_assert")
    sys.exit(1)

# debug_assert must reference is_mmap_backed
if 'is_mmap_backed' not in weight_body:
    print("FAIL: debug_assert doesn't reference is_mmap_backed")
    sys.exit(1)

# Must be a negation (should NOT be mmap-backed)
if '!' not in weight_body.split('debug_assert')[1].split('(')[1].split(',')[0]:
    print("FAIL: debug_assert doesn't negate is_mmap_backed (should assert NOT mmap-backed)")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"BlockWeighter debug_assert check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_core_api_intact():
    """Core types and methods still exist after the refactor.

    Regression test: verifies the fix didn't delete essential infrastructure
    that other code depends on.
    """
    r = _run_py(f"""
import re, sys
src = open("{SRC_FILE}").read()

# Core types that must exist on both base and fix
required = [
    "pub struct StaticSortedFile",
    "pub struct StaticSortedFileMetaData",
    "pub struct BlockWeighter",
    "type BlockCache",
    "fn verify_checksum",
    "fn get_raw_block_slice",
    "BLOCK_TYPE_KEY_WITH_HASH",
    "BLOCK_TYPE_KEY_NO_HASH",
    "SstLookupResult",
]
for item in required:
    if item not in src:
        print(f"FAIL: required API element '{{item}}' missing")
        sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Core API check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_imports_include_atomic():
    """Source file imports AtomicU64 from std::sync::atomic.

    The fix uses atomic operations for the verified_blocks bitmap.
    This import must be present for the code to compile.
    """
    r = _run_py(f"""
import sys
src = open("{SRC_FILE}").read()

if "AtomicU64" not in src:
    print("FAIL: AtomicU64 not referenced in source")
    sys.exit(1)

# Must be in a use statement (import)
import_found = False
for line in src.split("\\n"):
    if 'use ' in line and 'AtomicU64' in line:
        import_found = True
        break
    if 'atomic' in line and ('AtomicU64' in line or '::atomic' in line):
        import_found = True
        break

if not import_found:
    print("FAIL: AtomicU64 not in a use/import statement")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Import check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout
