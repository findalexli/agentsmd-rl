"""
Task: ruff-formatter-snapshot-diagnostic-sort
Repo: astral-sh/ruff @ 23364ae6a52b47c855db63c203893325a9aab1fa
PR:   24375

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/ruff"

FIXTURES_RS = Path(REPO) / "crates/ruff_python_formatter/tests/fixtures.rs"
SNAPSHOT = (
    Path(REPO)
    / "crates/ruff_python_formatter/tests/snapshots"
    / "format@expression__nested_string_quote_style.py.snap"
)


def _extract_ensure_unchanged_ast() -> str:
    """Extract the body of ensure_unchanged_ast from fixtures.rs."""
    source = FIXTURES_RS.read_text()
    fn_start = source.find("fn ensure_unchanged_ast(")
    assert fn_start != -1, "ensure_unchanged_ast function not found in fixtures.rs"
    fn_end = source.find("\nfn ", fn_start + 1)
    if fn_end == -1:
        fn_end = len(source)
    return source[fn_start:fn_end]


def _extract_error_sections(text: str) -> list[list[tuple[int, int]]]:
    """Extract error locations from each 'Unsupported Syntax Errors' section.

    Returns a list of sections, each containing (line, col) tuples
    extracted from '  --> filename.py:LINE:COL' markers.
    """
    sections: list[list[tuple[int, int]]] = []
    current_section: list[tuple[int, int]] | None = None

    for line in text.splitlines():
        if "### Unsupported Syntax Errors" in line:
            if current_section is not None:
                sections.append(current_section)
            current_section = []
        elif current_section is not None:
            m = re.match(r"\s*-->\s*\S+:(\d+):(\d+)", line)
            if m:
                current_section.append((int(m.group(1)), int(m.group(2))))

    if current_section is not None:
        sections.append(current_section)

    return sections


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_snapshot_errors_sorted_by_location():
    """Errors in each snapshot section are sorted by source line number.

    On the base commit, errors appear in HashMap iteration order (line 30
    before line 28). After the fix, they must be sorted ascending by line.
    """
    snap_text = SNAPSHOT.read_text()
    sections = _extract_error_sections(snap_text)
    assert len(sections) >= 2, (
        f"Expected at least 2 'Unsupported Syntax Errors' sections, found {len(sections)}"
    )

    for i, section in enumerate(sections):
        assert len(section) >= 2, (
            f"Section {i}: expected at least 2 error locations, found {len(section)}"
        )
        lines = [loc[0] for loc in section]
        assert lines == sorted(lines), (
            f"Section {i}: error locations not sorted by line number: {section}"
        )


# [pr_diff] fail_to_pass
def test_sort_applied_to_errors():
    """fixtures.rs applies sorting to unsupported syntax errors before diagnosis.

    The function ensure_unchanged_ast must sort formatted_unsupported_syntax_errors
    (or the diagnostics derived from them) by location to ensure deterministic
    snapshot output. Any sort method (.sort, .sort_by, .sort_by_key, etc.) is
    acceptable.
    """
    func_body = _extract_ensure_unchanged_ast()
    has_sort = bool(re.search(r"\.sort", func_body))
    assert has_sort, (
        "ensure_unchanged_ast must sort errors/diagnostics for stable snapshot output. "
        "No .sort* call found in the function body."
    )


# [pr_diff] fail_to_pass
def test_hashmap_iteration_order_addressed():
    """HashMap non-deterministic iteration order must be addressed.

    On the base commit, formatted_unsupported_syntax_errors (a HashMap) is
    iterated via .values().map() without sorting. The fix must either:
    (a) collect HashMap values into a Vec and sort before creating diagnostics, or
    (b) sort the diagnostics Vec after creation.
    """
    func_body = _extract_ensure_unchanged_ast()
    has_values_map = bool(
        re.search(
            r"formatted_unsupported_syntax_errors\s*\.\s*values\s*\(\s*\)\s*\.\s*map",
            func_body,
        )
    )
    if has_values_map:
        # .values().map() is still used — diagnostics must be sorted afterward
        has_post_sort = bool(re.search(r"diagnostics\s*\.\s*sort", func_body))
        assert has_post_sort, (
            "formatted_unsupported_syntax_errors still uses .values().map() directly "
            "without sorting the resulting diagnostics Vec afterward. Either collect "
            "HashMap values into a sorted Vec before creating diagnostics, or sort "
            "the diagnostics Vec after creation."
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — cargo test on formatter
def test_repo_formatter_tests():
    """Repo's formatter tests pass (pass_to_pass)."""
    import subprocess

    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_python_formatter", "--test", "fixtures"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Formatter tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — cargo check on formatter
def test_repo_cargo_check():
    """Repo's cargo check passes on formatter crate (pass_to_pass)."""
    import subprocess

    r = subprocess.run(
        ["cargo", "check", "-p", "ruff_python_formatter"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — cargo clippy on formatter
def test_repo_cargo_clippy():
    """Repo's cargo clippy passes on formatter crate (pass_to_pass)."""
    import subprocess

    r = subprocess.run(
        ["cargo", "clippy", "-p", "ruff_python_formatter", "--", "-D", "warnings"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo clippy failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — cargo fmt check on formatter
def test_repo_cargo_fmt():
    """Repo's cargo fmt check passes on formatter crate (pass_to_pass)."""
    import subprocess

    r = subprocess.run(
        ["cargo", "fmt", "--check", "-p", "ruff_python_formatter"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo fmt check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 23364ae6a52b47c855db63c203893325a9aab1fa
def test_no_panic_unwrap_in_sorting_section():
    """No panic!/unwrap in the sorting logic added to ensure_unchanged_ast (AGENTS.md:79)."""
    func_body = _extract_ensure_unchanged_ast()

    # Focus on the section between .retain() and the diagnostics map chain
    retain_idx = func_body.find(".retain(")
    file_builder_idx = func_body.find("SourceFileBuilder::new")
    if retain_idx == -1 or file_builder_idx == -1:
        return  # Can't isolate the section; skip gracefully

    section = func_body[retain_idx:file_builder_idx]
    for i, line in enumerate(section.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert "panic!(" not in stripped, (
            f"panic! found in sorting section (line {i}): {stripped}"
        )
        assert ".unwrap()" not in stripped, (
            f".unwrap() found in sorting section (line {i}): {stripped}"
        )


# [agent_config] pass_to_pass — AGENTS.md:76 @ 23364ae6a52b47c855db63c203893325a9aab1fa
def test_no_local_imports_in_modified_function():
    """No local use statements inside ensure_unchanged_ast (AGENTS.md:76)."""
    func_body = _extract_ensure_unchanged_ast()
    for i, line in enumerate(func_body.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert not stripped.startswith("use "), (
            f"Local import in ensure_unchanged_ast line {i}: {stripped}"
        )
