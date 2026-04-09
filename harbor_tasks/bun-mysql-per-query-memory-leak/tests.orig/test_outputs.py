"""
Task: bun-mysql-per-query-memory-leak
Repo: oven-sh/bun @ 9a27ef75697d713dba18b7a9762308197014ecca
PR:   28633

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

These tests use Python-based AST extraction to validate the exact code
patterns from the PR diff. They verify that:
1. Memory is freed before reassignment (preventing the leak)
2. All heap-owning fields are properly cleaned up in deinit
3. Allocated memory is zero-initialized
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
    pattern = rf"(?:pub\s+)?fn\s+{fn_name}\b[^{{]*\{{"
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


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# -----------------------------------------------------------------------------

def test_modified_files_exist():
    """All four modified Zig files must exist."""
    for path in [COLDEF, PREPSTMT, MYSTMT, MYCONN]:
        assert Path(path).exists(), f"Missing: {path}"


def test_balanced_braces():
    """Modified files must have balanced braces (basic syntax gate)."""
    for path in [COLDEF, PREPSTMT, MYSTMT, MYCONN]:
        src = Path(path).read_text()
        opens = src.count("{")
        closes = src.count("}")
        assert opens == closes, (
            f"Unmatched braces in {Path(path).name}: {opens} open vs {closes} close"
        )


def test_not_stub():
    """ColumnDefinition41.deinit has >=6 cleanup calls (not a stub)."""
    src = _read_clean(COLDEF)
    body = _extract_fn_body(src, "deinit")
    calls = re.findall(r"\.\s*(?:deinit|free)\s*\(", body)
    assert len(calls) >= 6, f"deinit has only {len(calls)} cleanup calls, need >=6"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# These verify the exact fix patterns from the PR diff
# -----------------------------------------------------------------------------

def test_coldef_deinit_frees_name_or_index():
    """ColumnDefinition41.deinit() frees name_or_index field."""
    src = _read_clean(COLDEF)
    body = _extract_fn_body(src, "deinit")

    # Must have: this.name_or_index.deinit()
    assert re.search(r"this\.name_or_index\.\s*deinit\s*\(", body), (
        "name_or_index.deinit() not found in ColumnDefinition41.deinit() - "
        "this is the primary leak fix for the column definition struct"
    )


def test_coldef_deinit_frees_all_data_fields():
    """ColumnDefinition41.deinit() frees all Data fields (catalog, schema, table, etc.)."""
    src = _read_clean(COLDEF)
    body = _extract_fn_body(src, "deinit")

    required = ["catalog", "schema", "table", "org_table", "name", "org_name"]
    for field in required:
        assert re.search(rf"this\.{field}\.\s*deinit\s*\(", body), (
            f"{field}.deinit() not found in deinit - all Data fields must be freed"
        )


def test_decodeinternal_frees_before_reassign():
    """decodeInternal() frees name_or_index before reassignment (prevents per-query leak)."""
    src = _read_clean(COLDEF)
    body = _extract_fn_body(src, "decodeInternal")

    # Find the line: this.name_or_index = try ColumnIdentifier.init(this.name)
    assign_match = re.search(
        r"this\.name_or_index\s*=\s*(?:try\s+)?ColumnIdentifier\.init",
        body
    )
    assert assign_match, (
        "name_or_index assignment not found in decodeInternal - "
        "expected: this.name_or_index = try ColumnIdentifier.init(this.name)"
    )

    # Check that deinit appears BEFORE the assignment
    before = body[:assign_match.start()]
    assert re.search(r"this\.name_or_index\.\s*deinit\s*\(", before), (
        "name_or_index.deinit() must be called BEFORE reassignment in decodeInternal. "
        "Without this, the old allocation is leaked on every query execution."
    )


def test_execute_deinit_frees_params_slice():
    """Execute.deinit() frees the params slice after freeing individual params."""
    src = _read_clean(PREPSTMT)

    # Extract the Execute struct
    execute_body = _extract_struct_body(src, "Execute")
    deinit_body = _extract_fn_body(execute_body, "deinit")

    # Must free individual params first (loop), then the slice itself
    # The fix adds: if (this.params.len > 0) { bun.default_allocator.free(this.params); }
    assert re.search(r"bun\.default_allocator\.\s*free\s*\(\s*this\.params\s*\)", deinit_body), (
        "bun.default_allocator.free(this.params) not found in Execute.deinit() - "
        "the params slice allocation is leaked without this fix"
    )


def test_checkduplicate_frees_before_overwrite():
    """checkForDuplicateFields frees name_or_index before .duplicate overwrite."""
    src = _read_clean(MYSTMT)
    body = _extract_fn_body(src, "checkForDuplicateFields")

    # Find the found_existing block and check for deinit before .duplicate assignment
    # Pattern: field.name_or_index.deinit(); field.name_or_index = .duplicate;
    dup_pattern = re.search(
        r"field\.name_or_index\.\s*deinit\s*\([^)]*\);?\s*field\.name_or_index\s*=\s*\.duplicate",
        body,
        re.DOTALL
    )

    # Alternative: might be on separate lines
    if not dup_pattern:
        deinit_match = re.search(r"field\.name_or_index\.\s*deinit\s*\(", body)
        duplicate_match = re.search(r"field\.name_or_index\s*=\s*\.duplicate", body)

        assert deinit_match and duplicate_match, (
            "Missing field.name_or_index.deinit() or .duplicate assignment in checkForDuplicateFields"
        )
        assert deinit_match.start() < duplicate_match.start(), (
            "field.name_or_index.deinit() must come BEFORE .duplicate assignment - "
            "otherwise the original allocation is leaked when overwriting with .duplicate"
        )
    else:
        assert dup_pattern, (
            "Pattern 'field.name_or_index.deinit(); field.name_or_index = .duplicate' not found - "
            "the duplicate column case leaks memory without this fix"
        )


def test_columns_zero_initialized_after_alloc():
    """ColumnDefinition41 arrays are zero-initialized after allocation (prevents use-of-uninitialized)."""
    src = _read_clean(MYCONN)

    # Find the pattern: statement.columns = try bun.default_allocator.alloc(...)
    # followed by: for (statement.columns) |*col| col.* = .{};

    alloc_pattern = r"statement\.columns\s*=\s*try\s+bun\.default_allocator\.alloc\s*\(\s*ColumnDefinition41\s*,"

    for match in re.finditer(alloc_pattern, src):
        after = src[match.end():match.end() + 600]
        # Check for zero-initialization loop
        zero_init = re.search(
            r"for\s*\(\s*statement\.columns\s*\)\s*\|\*col\|\s*col\.\*\s*=\s*\.\{\s*\}",
            after
        )
        assert zero_init, (
            "Zero-initialization loop 'for (statement.columns) |*col| col.* = .{}' "
            f"not found after alloc at offset {match.start()}. "
            "Without this, ColumnDefinition41 fields contain garbage values."
        )


# -----------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# These ensure existing functionality is preserved
# -----------------------------------------------------------------------------

def test_individual_params_still_freed():
    """Execute.deinit() still frees individual param values in the loop."""
    src = _read_clean(PREPSTMT)
    execute_body = _extract_struct_body(src, "Execute")
    deinit_body = _extract_fn_body(execute_body, "deinit")

    # Check for the for loop with params and a deinit call on param inside
    has_loop = re.search(r"for\s*\(\s*this\.params\s*\)\s*\|\*param\|", deinit_body)
    has_deinit = re.search(r"param\.deinit\s*\(", deinit_body)
    assert has_loop and has_deinit, (
        "Individual param.deinit() loop not found - regression in param cleanup"
    )


def test_columns_array_still_freed():
    """MySQLStatement.deinit() still frees columns array."""
    src = _read_clean(MYSTMT)

    assert re.search(r"column\.deinit\s*\(", src), (
        "column.deinit() not found in MySQLStatement - regression in column cleanup"
    )
    assert re.search(r"\.\s*free\s*\(", src), (
        "Allocator free not found in MySQLStatement - regression in memory cleanup"
    )


# -----------------------------------------------------------------------------
# Static pattern checks (pass_to_pass)
# -----------------------------------------------------------------------------

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


def test_no_inline_imports():
    """No @import() calls inline inside function bodies in modified files."""
    for path in [COLDEF, PREPSTMT, MYSTMT, MYCONN]:
        src = Path(path).read_text()
        # Find all function bodies and check for @import inside them
        for fn_match in re.finditer(r"(?:pub\s+)?fn\s+\w+\b[^{]*\{", src):
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


# -----------------------------------------------------------------------------
# Repo CI-derived checks — file/syntax validation gates
# -----------------------------------------------------------------------------

def test_repo_zig_syntax_valid():
    """Modified Zig files have balanced braces and valid syntax (repo CI gate)."""
    for path in [COLDEF, PREPSTMT, MYSTMT, MYCONN]:
        src = Path(path).read_text()
        opens = src.count("{")
        closes = src.count("}")
        assert opens == closes, (
            f"Syntax error in {Path(path).name}: {opens} open vs {closes} close braces"
        )


def test_repo_modified_files_readable():
    """All modified SQL/MySQL files are readable and non-empty (repo CI gate)."""
    for path in [COLDEF, PREPSTMT, MYSTMT, MYCONN]:
        p = Path(path)
        assert p.exists(), f"File not found: {path}"
        content = p.read_text()
        assert len(content) > 100, f"File {p.name} is too small or empty"
        assert "const " in content, f"File {p.name} missing expected Zig keywords"


def test_repo_required_fields_exist():
    """Required struct fields exist in modified files (repo CI gate)."""
    # ColumnDefinition41 must have name_or_index field
    src = _read_clean(COLDEF)
    assert "name_or_index:" in src, "name_or_index field missing from ColumnDefinition41"

    # PreparedStatement Execute must have params field
    src = _read_clean(PREPSTMT)
    assert "params" in src, "params field missing from PreparedStatement"


def test_repo_bun_allocator_used():
    """Modified files use bun.default_allocator for memory (repo CI gate)."""
    for path in [PREPSTMT, MYCONN]:
        src = Path(path).read_text()
        has_bun = "bun.default_allocator" in src or "bun.default.allocator" in src
        assert has_bun, f"{Path(path).name} should use bun.default_allocator"


def test_repo_no_std_allocator_usage():
    """Modified files do not use std.heap or std.mem.Allocator directly (repo CI gate)."""
    for path in [COLDEF, PREPSTMT, MYSTMT, MYCONN]:
        src = Path(path).read_text()
        assert "std.heap" not in src, f"{Path(path).name} uses forbidden std.heap"
        assert "std.mem.Allocator" not in src, f"{Path(path).name} uses forbidden std.mem.Allocator"
