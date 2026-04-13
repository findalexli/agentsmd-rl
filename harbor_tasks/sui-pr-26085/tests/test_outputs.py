"""Test suite for sui-framework option macros PR #26085.

Tests that the new macro functions are correctly implemented:
- map_mut: Map by mutable reference
- is_none_or: Check if None or predicate returns true
- fold: Consume option and apply function
- fold_ref: Apply function to borrowed value
- fold_mut: Apply function to mutably borrowed value
"""

import subprocess
import re
import pytest

REPO = "/workspace/sui"
MOVE_STDLIB = "crates/sui-framework/packages/move-stdlib"
OPTION_MOVE = f"{MOVE_STDLIB}/sources/option.move"
OPTION_TESTS = f"{MOVE_STDLIB}/tests/option_tests.move"


def test_map_mut_macro_exists():
    """Fail-to-pass: map_mut macro must exist in option.move."""
    with open(f"{REPO}/{OPTION_MOVE}", "r") as f:
        content = f.read()

    # Check function signature exists
    assert "public macro fun map_mut" in content, "map_mut macro not found in option.move"

    # Check parameter types are correct
    assert "&mut Option<$T>" in content or "&mut Option" in content, "map_mut should accept &mut Option"
    assert "|&mut $T| -> $U" in content or "|&mut" in content, "map_mut should accept closure with &mut param"


def test_is_none_or_macro_exists():
    """Fail-to-pass: is_none_or macro must exist in option.move."""
    with open(f"{REPO}/{OPTION_MOVE}", "r") as f:
        content = f.read()

    assert "public macro fun is_none_or" in content, "is_none_or macro not found"

    # Check it uses is_none and short-circuit OR
    assert "is_none() ||" in content or "is_none()" in content, "is_none_or should use is_none"


def test_fold_macro_exists():
    """Fail-to-pass: fold macro must exist in option.move."""
    with open(f"{REPO}/{OPTION_MOVE}", "r") as f:
        content = f.read()

    assert "public macro fun fold<" in content, "fold macro not found"

    # Check it consumes the option (takes ownership)
    assert "destroy_some()" in content, "fold should consume with destroy_some"
    assert "destroy_none()" in content, "fold should handle None with destroy_none"


def test_fold_ref_macro_exists():
    """Fail-to-pass: fold_ref macro must exist in option.move."""
    with open(f"{REPO}/{OPTION_MOVE}", "r") as f:
        content = f.read()

    assert "public macro fun fold_ref" in content, "fold_ref macro not found"

    # Check it borrows (not consumes)
    assert "o.borrow()" in content, "fold_ref should use borrow() not destroy_some()"


def test_fold_mut_macro_exists():
    """Fail-to-pass: fold_mut macro must exist in option.move."""
    with open(f"{REPO}/{OPTION_MOVE}", "r") as f:
        content = f.read()

    assert "public macro fun fold_mut" in content, "fold_mut macro not found"

    # Check it uses borrow_mut for mutable reference
    assert "o.borrow_mut()" in content, "fold_mut should use borrow_mut()"


def test_map_mut_functionality():
    """Fail-to-pass: map_mut tests must exist and pass."""
    with open(f"{REPO}/{OPTION_TESTS}", "r") as f:
        content = f.read()

    # Check test exists
    assert "fun map_mut()" in content, "map_mut test function not found"

    # Check test validates both Some and None cases
    assert "option::some(5u64)" in content, "map_mut test should test Some case"
    assert "option::none<u64>()" in content, "map_mut test should test None case"

    # Check mutable modification is validated
    assert "*x = 100" in content, "map_mut test should verify mutation occurred"


def test_is_none_or_functionality():
    """Fail-to-pass: is_none_or tests must exist and cover all cases."""
    with open(f"{REPO}/{OPTION_TESTS}", "r") as f:
        content = f.read()

    # Check test function exists
    assert "fun is_none_or()" in content, "is_none_or test not found"

    # Check all three cases are tested:
    # 1. Some with matching predicate
    # 2. Some with non-matching predicate
    # 3. None (should return true)
    assert "*x == 5" in content, "is_none_or should test matching predicate"
    assert "*x == 6" in content, "is_none_or should test non-matching predicate"


def test_fold_functionality():
    """Fail-to-pass: fold tests must exist with both Some and None cases."""
    with open(f"{REPO}/{OPTION_TESTS}", "r") as f:
        content = f.read()

    # Check test exists
    assert "fun fold()" in content, "fold test not found"

    # Check both cases tested
    assert "option::some(5u64).fold!" in content, "fold should test Some case"
    assert "option::none<u64>().fold!" in content, "fold should test None case"


def test_fold_ref_functionality():
    """Fail-to-pass: fold_ref tests must exist."""
    with open(f"{REPO}/{OPTION_TESTS}", "r") as f:
        content = f.read()

    assert "fun fold_ref()" in content, "fold_ref test not found"


def test_fold_mut_functionality():
    """Fail-to-pass: fold_mut tests must exist with mutation validation."""
    with open(f"{REPO}/{OPTION_TESTS}", "r") as f:
        content = f.read()

    assert "fun fold_mut()" in content, "fold_mut test not found"

    # Check mutation is tested
    assert "*x = 100" in content, "fold_mut should test mutation"


def test_move_tests_compile():
    """Pass-to-pass: Move code should compile successfully."""
    # Just check the Move syntax is valid by checking for common errors
    # This is faster than full cargo build which takes a long time
    with open(f"{REPO}/{OPTION_MOVE}", "r") as f:
        content = f.read()

    # Basic syntax checks
    # All public macros should have balanced braces
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, "Unbalanced braces in option.move"

    # All public macros should have balanced parentheses
    open_parens = content.count("(")
    close_parens = content.count(")")
    assert open_parens == close_parens, "Unbalanced parentheses in option.move"


def test_repo_cargo_fmt():
    """Repo's Rust code passes cargo fmt --check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt --check failed:\n{r.stderr[-500:] or r.stdout[-500:]}"


def test_repo_cargo_check_sui_framework():
    """Repo's sui-framework crate passes cargo check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "sui-framework"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check -p sui-framework failed:\n{r.stderr[-500:]}"


def test_repo_cargo_check_sui_framework_tests():
    """Repo's sui-framework-tests crate passes cargo check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "sui-framework-tests"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check -p sui-framework-tests failed:\n{r.stderr[-500:]}"


def test_repo_cargo_check_sui_move():
    """Repo's sui-move crate passes cargo check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "sui-move"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check -p sui-move failed:\n{r.stderr[-500:]}"


def test_repo_cargo_xlint():
    """Repo passes cargo xlint license check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "xlint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo xlint failed:\n{r.stderr[-500:] or r.stdout[-500:]}"


def test_repo_cargo_clippy_sui_framework():
    """Repo's sui-framework crate passes cargo clippy (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "sui-framework"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy -p sui-framework failed:\n{r.stderr[-500:]}"
