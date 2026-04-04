"""
Task: uv-remove-dep-comment-preservation
Repo: astral-sh/uv @ 46c9bac182d64359cef45d51fd796b81b3736f8b
PR:   18557

Tests that `remove_dependency` preserves end-of-line TOML comments.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/repo"
MUT_RS = Path(f"{REPO}/crates/uv-workspace/src/pyproject_mut.rs")

# ---------------------------------------------------------------------------
# Rust test harness — injected into pyproject_mut's #[cfg(test)] mod test
# ---------------------------------------------------------------------------

_HARNESS_RUST = r'''
    #[test]
    fn harness_remove_last_preserves_comment() {
        // Case 1: two deps, remove last — comment on first must survive
        let toml = "[project]\ndependencies = [\n    \"iniconfig>=2.0.0\", # keep this note\n    \"typing-extensions>=4.0.0\",\n]\n";
        let mut doc: DocumentMut = toml.parse().unwrap();
        let deps = doc["project"]["dependencies"].as_array_mut().unwrap();
        remove_dependency(&uv_normalize::PackageName::from_str("typing-extensions").unwrap(), deps);
        let out = doc.to_string();
        assert!(out.contains("# keep this note"), "Case1: comment lost:\n{out}");
        assert!(!out.to_lowercase().contains("typing-extensions"), "Case1: dep not removed");

        // Case 2: three deps, remove last, comment on second-to-last
        let toml2 = "[project]\ndependencies = [\n    \"a>=1.0\",\n    \"b>=2.0\", # b comment\n    \"c>=3.0\",\n]\n";
        let mut doc2: DocumentMut = toml2.parse().unwrap();
        let deps2 = doc2["project"]["dependencies"].as_array_mut().unwrap();
        remove_dependency(&uv_normalize::PackageName::from_str("c").unwrap(), deps2);
        let out2 = doc2.to_string();
        assert!(out2.contains("# b comment"), "Case2: comment lost:\n{out2}");

        // Case 3: different comment text
        let toml3 = "[project]\ndependencies = [\n    \"anyio>=4.0.0\", # pinned for compat\n    \"flask>=3.0.0\",\n]\n";
        let mut doc3: DocumentMut = toml3.parse().unwrap();
        let deps3 = doc3["project"]["dependencies"].as_array_mut().unwrap();
        remove_dependency(&uv_normalize::PackageName::from_str("flask").unwrap(), deps3);
        let out3 = doc3.to_string();
        assert!(out3.contains("# pinned for compat"), "Case3: comment lost:\n{out3}");
    }

    #[test]
    fn harness_remove_middle_preserves_comment() {
        // Case 1: remove middle of 3, comment on first
        let toml = "[project]\ndependencies = [\n    \"a>=1.0\", # a note\n    \"b>=2.0\",\n    \"c>=3.0\",\n]\n";
        let mut doc: DocumentMut = toml.parse().unwrap();
        let deps = doc["project"]["dependencies"].as_array_mut().unwrap();
        remove_dependency(&uv_normalize::PackageName::from_str("b").unwrap(), deps);
        let out = doc.to_string();
        assert!(out.contains("# a note"), "Comment lost:\n{out}");
        assert!(out.contains("c>=3.0"), "c should remain");

        // Case 2: comments on surrounding entries survive
        let toml2 = "[project]\ndependencies = [\n    \"x>=1.0\", # x note\n    \"y>=2.0\",\n    \"z>=3.0\", # z note\n    \"w>=4.0\",\n]\n";
        let mut doc2: DocumentMut = toml2.parse().unwrap();
        let deps2 = doc2["project"]["dependencies"].as_array_mut().unwrap();
        remove_dependency(&uv_normalize::PackageName::from_str("y").unwrap(), deps2);
        let out2 = doc2.to_string();
        assert!(out2.contains("# x note"), "x comment lost:\n{out2}");
        assert!(out2.contains("# z note"), "z comment lost:\n{out2}");
    }

    #[test]
    fn harness_remove_adjacent_duplicates_preserves_comment() {
        // Case 1: two typing-extensions with markers, comment on preceding dep
        let toml = "[project]\ndependencies = [\n    \"numpy>=2.4.3\", # numpy comment\n    \"typing-extensions>=4.0.0 ; python_version < '3.11'\",\n    \"typing-extensions>=4.0.0 ; python_version >= '3.11'\",\n    \"sniffio>=1.3.0\",\n]\n";
        let mut doc: DocumentMut = toml.parse().unwrap();
        let deps = doc["project"]["dependencies"].as_array_mut().unwrap();
        remove_dependency(&uv_normalize::PackageName::from_str("typing-extensions").unwrap(), deps);
        let out = doc.to_string();
        assert!(!out.to_lowercase().contains("typing-extensions"), "Not removed");
        assert!(out.contains("# numpy comment"), "Comment lost:\n{out}");
        assert!(out.contains("sniffio"), "sniffio should remain");

        // Case 2: no trailing dep after duplicates
        let toml2 = "[project]\ndependencies = [\n    \"anyio>=4.0.0\", # anyio note\n    \"typing-extensions>=4.0.0 ; python_version < '3.11'\",\n    \"typing-extensions>=4.0.0 ; python_version >= '3.11'\",\n]\n";
        let mut doc2: DocumentMut = toml2.parse().unwrap();
        let deps2 = doc2["project"]["dependencies"].as_array_mut().unwrap();
        remove_dependency(&uv_normalize::PackageName::from_str("typing-extensions").unwrap(), deps2);
        let out2 = doc2.to_string();
        assert!(out2.contains("# anyio note"), "anyio comment lost:\n{out2}");
    }

    #[test]
    fn harness_sequential_removals() {
        let toml = "[project]\ndependencies = [\n    \"a>=1.0\", # must survive\n    \"b>=2.0\",\n    \"c>=3.0\",\n]\n";
        let mut doc: DocumentMut = toml.parse().unwrap();

        // First removal: b
        let deps = doc["project"]["dependencies"].as_array_mut().unwrap();
        remove_dependency(&uv_normalize::PackageName::from_str("b").unwrap(), deps);
        let after1 = doc.to_string();
        assert!(after1.contains("# must survive"), "Comment lost after first removal:\n{after1}");

        // Second removal: c
        let deps = doc["project"]["dependencies"].as_array_mut().unwrap();
        remove_dependency(&uv_normalize::PackageName::from_str("c").unwrap(), deps);
        let after2 = doc.to_string();
        assert!(after2.contains("# must survive"), "Comment lost after second removal:\n{after2}");
    }

    #[test]
    fn harness_remove_only_dep() {
        let toml = "[project]\ndependencies = [\n    \"typing-extensions>=4.0.0\",\n]\n";
        let mut doc: DocumentMut = toml.parse().unwrap();
        let deps = doc["project"]["dependencies"].as_array_mut().unwrap();
        remove_dependency(&uv_normalize::PackageName::from_str("typing-extensions").unwrap(), deps);
        let out = doc.to_string();
        assert!(!out.to_lowercase().contains("typing-extensions"), "Not removed:\n{out}");
        assert!(out.contains("dependencies"), "dependencies key should remain");
    }
'''

# ---------------------------------------------------------------------------
# Harness runner — inject tests, run cargo test, cache results
# ---------------------------------------------------------------------------

_cached_results = None


def _run_harness():
    """Inject Rust tests into pyproject_mut.rs test module, run cargo test, cache results."""
    global _cached_results
    if _cached_results is not None:
        return _cached_results

    original = MUT_RS.read_text()

    # Add import for remove_dependency if not already present
    import_line = ""
    if "use super::remove_dependency" not in original:
        import_line = "    use super::remove_dependency;\n"

    # Find the #[cfg(test)] mod test { ... } block
    mod_test_match = re.search(r"#\[cfg\(test\)\]\s*mod test \{", original)
    assert mod_test_match, "Could not find #[cfg(test)] mod test block in pyproject_mut.rs"
    insert_after = mod_test_match.end()

    # Find the final closing brace of the file (end of mod test)
    last_brace = original.rfind("}")
    assert last_brace > insert_after, "Could not find closing brace of mod test"

    modified = (
        original[:insert_after]
        + "\n" + import_line
        + original[insert_after:last_brace]
        + _HARNESS_RUST
        + "\n}\n"
    )

    MUT_RS.write_text(modified)
    try:
        r = subprocess.run(
            ["cargo", "test", "-p", "uv-workspace", "--lib", "--no-fail-fast"],
            cwd=REPO, capture_output=True, timeout=600,
        )
    finally:
        MUT_RS.write_text(original)

    # Parse test results from stdout + stderr
    output = r.stdout.decode(errors="replace") + "\n" + r.stderr.decode(errors="replace")
    tests = {}
    for line in output.splitlines():
        m = re.search(r"test\s+\S+::(\w+)\s+\.\.\.\s+(ok|FAILED|ignored)", line)
        if m:
            tests[m.group(1)] = m.group(2)

    _cached_results = {"tests": tests, "output": output, "returncode": r.returncode}
    return _cached_results


def _assert_harness_test(test_name: str, msg: str):
    """Assert that a specific injected Rust test passed."""
    results = _run_harness()
    assert results["tests"], (
        f"No test results — compilation likely failed:\n"
        f"{results['output'][-3000:]}"
    )
    assert test_name in results["tests"], (
        f"Test '{test_name}' not found. Found: {list(results['tests'].keys())}"
    )
    assert results["tests"][test_name] == "ok", msg


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """Modified crate must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-workspace"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_remove_last_dep_preserves_prev_comment():
    """End-of-line comment on previous entry survives removal of last entry (3 inputs)."""
    _assert_harness_test(
        "harness_remove_last_preserves_comment",
        "End-of-line comment lost when removing last dep",
    )


# [pr_diff] fail_to_pass
def test_remove_middle_dep_preserves_prev_comment():
    """End-of-line comment on previous entry survives removal of middle entry (2 inputs)."""
    _assert_harness_test(
        "harness_remove_middle_preserves_comment",
        "End-of-line comment lost when removing middle dep",
    )


# [pr_diff] fail_to_pass
def test_remove_adjacent_duplicates_preserves_comment():
    """Removing multiple adjacent matching deps preserves comment on preceding entry (2 inputs)."""
    _assert_harness_test(
        "harness_remove_adjacent_duplicates_preserves_comment",
        "Comment lost when removing adjacent duplicate deps",
    )


# [pr_diff] fail_to_pass
def test_comment_preserved_across_sequential_removals():
    """Comments survive when multiple deps are removed in sequence."""
    _assert_harness_test(
        "harness_sequential_removals",
        "Comment lost after sequential dep removals",
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_unit_tests_pass():
    """Existing uv-workspace unit tests still pass."""
    results = _run_harness()
    existing = [
        name for name in results["tests"]
        if not name.startswith("harness_")
    ]
    assert existing, (
        f"No existing tests found — compilation may have failed:\n"
        f"{results['output'][-3000:]}"
    )
    failed = [name for name in existing if results["tests"][name] == "FAILED"]
    assert not failed, f"Existing tests failed: {failed}"


# [static] pass_to_pass
def test_remove_only_dep_basic():
    """Removing the sole dependency works and leaves dependencies key."""
    _assert_harness_test(
        "harness_remove_only_dep",
        "Failed to remove the only dependency",
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ 46c9bac182d64359cef45d51fd796b81b3736f8b
def test_no_panic_unwrap_unreachable():
    """remove_dependency avoids panic!/unreachable!/.unwrap() per CLAUDE.md line 7."""
    # AST-only because: Rust code cannot be imported into Python
    src = MUT_RS.read_text()
    match = re.search(
        r"fn remove_dependency\b.*?\n(.*?)(?=\nfn |\Z)",
        src, re.DOTALL,
    )
    assert match, "remove_dependency function not found"
    fn_body = match.group(0)

    unwrap_count = len(re.findall(r"\.unwrap\(\)", fn_body))
    assert unwrap_count <= 1, (
        f"Too many .unwrap() calls ({unwrap_count}) in remove_dependency — "
        f"CLAUDE.md line 7: AVOID .unwrap()"
    )

    panic_count = len(re.findall(r"\bpanic!\s*\(", fn_body))
    assert panic_count == 0, (
        f"Found panic! in remove_dependency — CLAUDE.md line 7: AVOID panic!"
    )

    unreachable_count = len(re.findall(r"\bunreachable!\s*\(", fn_body))
    assert unreachable_count == 0, (
        f"Found unreachable! in remove_dependency — CLAUDE.md line 7: AVOID unreachable!"
    )
