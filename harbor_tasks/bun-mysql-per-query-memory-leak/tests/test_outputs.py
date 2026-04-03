"""
Task: bun-mysql-per-query-memory-leak
Repo: oven-sh/bun @ 9a27ef75697d713dba18b7a9762308197014ecca
PR:   28633

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: Zig code requires a full Bun build (WebKit/JSC deps) and cannot
be compiled or executed in the test container. All checks inspect source
files for correct memory-management patterns.
# AST-only because: Zig code cannot be compiled without full Bun build toolchain
"""

import re
from pathlib import Path

REPO = "/repo"
COLDEF = f"{REPO}/src/sql/mysql/protocol/ColumnDefinition41.zig"
PREPSTMT = f"{REPO}/src/sql/mysql/protocol/PreparedStatement.zig"
MYSTMT = f"{REPO}/src/sql/mysql/MySQLStatement.zig"
MYCONN = f"{REPO}/src/sql/mysql/MySQLConnection.zig"


def _strip_comments(src: str) -> str:
    """Strip single-line Zig comments."""
    return re.sub(r"//[^\n]*", "", src)


def _read_clean(path: str) -> str:
    return _strip_comments(Path(path).read_text())


def _extract_fn_body(src: str, fn_name: str) -> str:
    """Extract function body by brace-counting (handles nested blocks)."""
    pattern = rf"(?:pub\s+)?fn {fn_name}\b[^{{]*\{{"
    m = re.search(pattern, src)
    assert m, f"Function {fn_name} not found"
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
        i += 1
    return src[start : i - 1]


def _extract_struct_body(src: str, struct_name: str) -> str:
    """Extract struct body by brace-counting."""
    pattern = rf"{struct_name}\s*=\s*struct\s*\{{"
    m = re.search(pattern, src)
    assert m, f"Struct {struct_name} not found"
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
        i += 1
    return src[start : i - 1]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_modified_files_exist():
    """All four modified Zig files must exist."""
    for path in [COLDEF, PREPSTMT, MYSTMT, MYCONN]:
        assert Path(path).exists(), f"Missing: {path}"


# [static] pass_to_pass
def test_balanced_braces():
    """Modified files must have balanced braces (basic syntax gate)."""
    for path in [COLDEF, PREPSTMT, MYSTMT, MYCONN]:
        src = Path(path).read_text()
        opens = src.count("{")
        closes = src.count("}")
        assert opens == closes, (
            f"Unmatched braces in {Path(path).name}: {opens} open vs {closes} close"
        )


# [static] pass_to_pass
def test_not_stub():
    """ColumnDefinition41.deinit has >=6 cleanup calls (not a stub)."""
    src = _read_clean(COLDEF)
    body = _extract_fn_body(src, "deinit")
    calls = re.findall(r"\.\s*(?:deinit|free)\s*\(", body)
    assert len(calls) >= 6, f"deinit has only {len(calls)} cleanup calls, need >=6"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_coldef_deinit_all_fields():
    """ColumnDefinition41.deinit() frees ALL heap-owning fields including name_or_index."""
    src = _read_clean(COLDEF)
    body = _extract_fn_body(src, "deinit")

    required = [
        "catalog", "schema", "table", "org_table",
        "name", "org_name", "name_or_index",
    ]
    freed = set()
    for field in required:
        if re.search(rf"\w+\.{field}\.\s*deinit\s*\(", body):
            freed.add(field)
        elif re.search(rf"defer\s+.*{field}.*\.\s*deinit", body):
            freed.add(field)
        elif re.search(rf"\w+\.{field}\.\s*free\s*\(", body):
            freed.add(field)

    # Accept comptime field iteration that frees everything
    if re.search(r"inline\s+for\b.*\bfields\b.*\bdeinit\b", body):
        freed = set(required)
    elif re.search(r"comptime.*(?:fields|@typeInfo).*deinit", body):
        freed = set(required)

    missing = set(required) - freed
    assert not missing, f"deinit missing cleanup for: {missing}"


# [pr_diff] fail_to_pass
def test_decode_frees_before_reassign():
    """decodeInternal() frees name_or_index before reassignment (prevents per-query leak)."""
    src = _read_clean(COLDEF)
    body = _extract_fn_body(src, "decodeInternal")

    assign = re.search(r"name_or_index\s*=\s*(?:try\s+)?(?:ColumnIdentifier|\.)", body)
    assert assign, "name_or_index assignment not found in decodeInternal"

    before = body[: assign.start()]
    ok = False

    # Pattern 1: deinit/free before assignment
    if re.search(r"name_or_index\.\s*deinit\s*\(", before):
        ok = True
    elif re.search(r"name_or_index\.\s*free\s*\(", before):
        ok = True
    elif re.search(r"defer\s+.*name_or_index.*\.\s*deinit", before):
        ok = True

    # Pattern 2: save-old-free-after
    if not ok:
        after = body[assign.end() :]
        temp = re.search(r"(?:const|var)\s+(\w+)\s*=\s*\w+\.name_or_index", before)
        if temp:
            t = temp.group(1)
            if re.search(rf"{t}\.\s*deinit\s*\(", after) or re.search(
                rf"{t}\.\s*free\s*\(", after
            ):
                ok = True

    # Pattern 3: defer on any local before assignment
    if not ok and re.search(r"defer\s+\w+\.\s*deinit\s*\(", before):
        ok = True

    assert ok, "name_or_index not freed before/around reassignment in decodeInternal"


# [pr_diff] fail_to_pass
def test_execute_deinit_frees_params_slice():
    """Execute.deinit() frees the params slice allocation (not just individual values)."""
    src = _read_clean(PREPSTMT)

    # Extract the Execute struct, then find deinit within it
    execute_body = _extract_struct_body(src, "Execute")
    deinit_body = _extract_fn_body(execute_body, "deinit")

    # Must free the params slice (allocator.free(this.params) or equivalent)
    freed = re.search(r"\.\s*free\s*\(\s*(?:this|self)\.params\s*\)", deinit_body)
    if not freed:
        freed = re.search(
            r"(?:dealloc|destroy)\s*\(\s*(?:this|self)\.params", deinit_body
        )
    if not freed:
        # Local alias pattern
        alias = re.search(
            r"(?:const|var)\s+\w*params\w*\s*=\s*(?:this|self)\.params", deinit_body
        )
        if alias:
            freed = re.search(r"\.\s*free\s*\(\s*\w*params\w*\s*\)", deinit_body)

    assert freed, "Execute.deinit does not free the params slice"


# [pr_diff] fail_to_pass
def test_duplicate_fields_frees_before_overwrite():
    """checkForDuplicateFields frees name_or_index before .duplicate overwrite."""
    src = _read_clean(MYSTMT)
    body = _extract_fn_body(src, "checkForDuplicateFields")

    dup_assign = re.search(r"name_or_index\s*=\s*\.duplicate", body)
    assert dup_assign, ".duplicate assignment not found in checkForDuplicateFields"

    before = body[: dup_assign.start()]
    # Narrow to the block around found_existing
    block_start = before.rfind("found_existing")
    if block_start < 0:
        block_start = max(0, dup_assign.start() - 400)
    between = before[block_start:]

    ok = False
    if re.search(r"name_or_index\.\s*deinit\s*\(", between):
        ok = True
    elif re.search(r"name_or_index\.\s*free\s*\(", between):
        ok = True
    elif re.search(r"defer\s+.*name_or_index.*\.\s*deinit", between):
        ok = True

    # Save-old pattern
    if not ok:
        after = body[dup_assign.end() : dup_assign.end() + 300]
        temp = re.search(
            r"(?:const|var)\s+(\w+)\s*=\s*\w+\.name_or_index", between
        )
        if temp:
            t = temp.group(1)
            if re.search(rf"{t}\.\s*deinit\s*\(", after) or re.search(
                rf"{t}\.\s*free\s*\(", after
            ):
                ok = True

    assert ok, "name_or_index not freed before .duplicate overwrite"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_coldef_existing_deinit_intact():
    """ColumnDefinition41.deinit() still frees all original Data fields."""
    src = _read_clean(COLDEF)
    for field in ["catalog", "schema", "table", "org_table", "name", "org_name"]:
        assert re.search(rf"\.{field}\.deinit\(\)", src), (
            f"Missing {field}.deinit() in ColumnDefinition41"
        )


# [pr_diff] pass_to_pass
def test_execute_individual_param_deinit():
    """Execute.deinit() still frees individual param values."""
    src = _read_clean(PREPSTMT)
    assert re.search(r"param\.deinit\(", src), (
        "Individual param.deinit not found in PreparedStatement"
    )


# [pr_diff] pass_to_pass
def test_mystmt_deinit_intact():
    """MySQLStatement.deinit() still frees columns array."""
    src = _read_clean(MYSTMT)
    assert re.search(r"column\.deinit\(\)", src), (
        "column.deinit() not found in MySQLStatement"
    )
    assert re.search(r"\.free\(", src), ".free() not found in MySQLStatement"


# [static] pass_to_pass
def test_coldef_has_name_or_index_field():
    """ColumnDefinition41 struct still defines name_or_index field."""
    src = _read_clean(COLDEF)
    assert re.search(r"name_or_index:", src), (
        "name_or_index field missing from ColumnDefinition41"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — src/CLAUDE.md:230-232 @ 9a27ef75
def test_uses_bun_allocator():
    """Params slice freed with bun.default_allocator, not std.* (src/CLAUDE.md:230-232)."""
    src = _read_clean(PREPSTMT)

    # Extract Execute struct, then deinit body
    execute_body = _extract_struct_body(src, "Execute")
    deinit_body = _extract_fn_body(execute_body, "deinit")

    if re.search(r"\.\s*free\s*\(", deinit_body):
        assert "bun" in deinit_body or "bun" in execute_body[:200], (
            "Must use bun.default_allocator, not std.heap"
        )
        assert "std.heap" not in deinit_body, "std.heap usage found"
    else:
        assert "std.heap" not in deinit_body, "std.heap usage found"


# [agent_config] fail_to_pass — src/CLAUDE.md:230-232 @ 9a27ef75
def test_columns_zero_initialized():
    """Newly allocated ColumnDefinition41 arrays are zero-initialized after alloc."""
    src = _read_clean(MYCONN)

    allocs = list(re.finditer(r"alloc\(\s*ColumnDefinition41\s*,", src))
    assert allocs, "No ColumnDefinition41 allocations found in MySQLConnection"

    for alloc in allocs:
        after = src[alloc.end() : alloc.end() + 400]
        init_pattern = re.search(
            r"(col\.\*\s*=\s*\.\{\}|@memset|\.init\(\)|std\.mem\.zeroes|=\s*\.\{\}|\*\s*=\s*\.\{\})",
            after,
        )
        assert init_pattern, (
            f"ColumnDefinition41 alloc at offset {alloc.start()} not followed by zero-init"
        )


# [agent_config] pass_to_pass — src/CLAUDE.md:14-16 @ 9a27ef75
def test_no_std_allocator():
    """No std.heap or std.mem.Allocator in modified files (use bun.default_allocator)."""
    for path in [COLDEF, PREPSTMT, MYSTMT, MYCONN]:
        src = Path(path).read_text()
        assert "std.heap" not in src, (
            f"std.heap found in {Path(path).name} — use bun.default_allocator instead"
        )
        assert not re.search(r"std\.mem\.Allocator\b", src), (
            f"std.mem.Allocator found in {Path(path).name} — use bun.default_allocator instead"
        )


# [agent_config] pass_to_pass — src/CLAUDE.md:11-12 @ 9a27ef75
def test_no_inline_imports():
    """No @import() calls inline inside function bodies in modified files."""
    for path in [COLDEF, PREPSTMT, MYSTMT, MYCONN]:
        src = Path(path).read_text()
        # Find all function bodies and check for @import inside them
        for fn_match in re.finditer(r"(?:pub\s+)?fn \w+\b[^{]*\{", src):
            fn_start = fn_match.end()
            depth = 1
            i = fn_start
            while i < len(src) and depth > 0:
                if src[i] == "{":
                    depth += 1
                elif src[i] == "}":
                    depth -= 1
                i += 1
            fn_body = src[fn_start : i - 1]
            assert "@import(" not in fn_body, (
                f"Inline @import() found inside function body in {Path(path).name}"
            )
