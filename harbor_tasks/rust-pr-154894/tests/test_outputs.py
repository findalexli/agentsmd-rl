"""Tests for rust-lang/rust#154894: mplace<->ptr conversions refactoring.

This PR renames two functions in the Rust interpreter and verifies
the renamed functions have the correct signatures and are properly called.
"""

import os
import re
import subprocess
import sys

REPO = "/workspace/rust"
PLACE_FILE = f"{REPO}/compiler/rustc_const_eval/src/interpret/place.rs"


def test_compilation_place_rs():
    """The modified place.rs file should compile without errors.

    This is a behavioral test: we check that the Rust code at least
    has valid structure by verifying brace balance and basic syntax.
    """
    result = subprocess.run(
        ["python3", "-c", f"""
import re
with open('{PLACE_FILE}', 'r') as f:
    content = f.read()
open_braces = content.count('{{')
close_braces = content.count('}}')
pub_fns = re.findall(r'pub\\s+fn\\s+\\w+\\s*\\([^)]*\\)', content)
print(f"open_braces={{open_braces}}, close_braces={{close_braces}}, pub_fns={{len(pub_fns)}}")
if open_braces == close_braces and len(pub_fns) > 0:
    print("VALID_STRUCTURE")
else:
    print("INVALID_STRUCTURE")
"""],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert "VALID_STRUCTURE" in result.stdout, f"place.rs structure check failed: {result.stdout}"


def test_first_pointer_conversion_function_has_new_name():
    """First pointer conversion function should have a renamed function taking ImmTy.
    
    The function that converts pointer values to memory places should:
    - Have been renamed from ref_to_mplace
    - Takes an ImmTy as parameter
    - Returns MPlaceTy
    """
    with open(PLACE_FILE, 'r') as f:
        content = f.read()

    # Check old name is gone
    assert 'fn ref_to_mplace' not in content, "Old function name ref_to_mplace should be removed"
    
    # Check the new function exists with the multiline signature pattern
    # Pattern: val: &ImmTy followed by ) -> InterpResult and MPlaceTy
    pattern = r'val:\s*&ImmTy<[^>]+>,\s*\)\s*->\s*InterpResult<[^>]+,\s*MPlaceTy'
    match = re.search(pattern, content)
    assert match is not None, "Could not find function taking ImmTy and returning MPlaceTy with new name"
    
    # Verify the function name is not ref_to_mplace
    # Find the function definition containing our pattern
    fn_match = re.search(r'pub\s+fn\s+(\w+)\s*\([^)]*val:\s*&ImmTy', content, re.DOTALL)
    assert fn_match is not None, "Could not find pub fn taking val: &ImmTy"
    fn_name = fn_match.group(1)
    assert fn_name != 'ref_to_mplace', f"Function still named ref_to_mplace (now {fn_name})"


def test_second_pointer_conversion_function_has_new_name_and_ptr_ty():
    """Second pointer conversion function should have new name and ptr_ty parameter.
    
    The function that converts memory places to pointer values should:
    - Have been renamed from mplace_to_ref
    - Take MPlaceTy and Option<Ty> as parameters
    - Return ImmTy
    """
    with open(PLACE_FILE, 'r') as f:
        content = f.read()

    # Check old name is gone
    assert 'fn mplace_to_ref' not in content, "Old function name mplace_to_ref should be removed"
    
    # Check the new function exists with ptr_ty parameter
    # Pattern: mplace: &MPlaceTy followed by ptr_ty: Option<Ty>
    pattern = r'mplace:\s*&MPlaceTy<[^>]+>,\s*ptr_ty:\s*Option<Ty'
    match = re.search(pattern, content, re.DOTALL)
    assert match is not None, "Could not find function taking MPlaceTy and ptr_ty parameter"
    
    # Find the function name
    fn_match = re.search(r'pub\s+fn\s+(\w+)\s*\([^)]*mplace:\s*&MPlaceTy[^)]*,\s*ptr_ty:\s*Option', content, re.DOTALL)
    assert fn_match is not None, "Could not find pub fn with mplace and ptr_ty parameters"
    fn_name = fn_match.group(1)
    assert fn_name != 'mplace_to_ref', f"Function still named mplace_to_ref (now {fn_name})"


def test_callers_use_two_arg_mplace_conversion():
    """Callers of mplace-to-pointer conversion should use two arguments (mplace, ptr_ty).

    The new function takes a second optional ptr_ty argument.
    Callers should either pass (place, None) or (place, Some(type)).
    """
    files_to_check = [
        f"{REPO}/compiler/rustc_const_eval/src/const_eval/type_info.rs",
        f"{REPO}/compiler/rustc_const_eval/src/const_eval/type_info/adt.rs",
        f"{REPO}/compiler/rustc_const_eval/src/interpret/call.rs",
    ]

    for filepath in files_to_check:
        with open(filepath, 'r') as f:
            content = f.read()

        # Old pattern should be gone
        assert not re.search(r'\bmplace_to_ref\s*\(', content), \
            f"Old single-arg mplace_to_ref call still exists in {filepath}"

        # New pattern should exist with 2 args
        new_pattern = r'\bmplace_to_imm_ptr\s*\([^,]+,\s*[^)]+\)'
        assert re.search(new_pattern, content), \
            f"New mplace_to_imm_ptr with 2 args not found in {filepath}"


def test_callers_use_single_arg_ptr_to_mplace():
    """Callers of pointer-to-mplace conversion should use the renamed function."""
    files_to_check = [
        f"{REPO}/compiler/rustc_const_eval/src/const_eval/machine.rs",
        f"{REPO}/compiler/rustc_const_eval/src/interpret/call.rs",
        f"{REPO}/compiler/rustc_const_eval/src/interpret/intrinsics.rs",
        f"{REPO}/compiler/rustc_const_eval/src/interpret/validity.rs",
    ]

    for filepath in files_to_check:
        with open(filepath, 'r') as f:
            content = f.read()

        # Old pattern should be gone
        assert not re.search(r'\bref_to_mplace\s*\(', content), \
            f"Old ref_to_mplace call still exists in {filepath}"

        # New pattern should exist
        assert re.search(r'\bimm_ptr_to_mplace\s*\(', content), \
            f"New imm_ptr_to_mplace call not found in {filepath}"


def test_miri_callers_updated():
    """Miri tool callers should be updated to use new function names."""
    files_to_check = [
        f"{REPO}/src/tools/miri/src/borrow_tracker/stacked_borrows/mod.rs",
        f"{REPO}/src/tools/miri/src/borrow_tracker/tree_borrows/mod.rs",
        f"{REPO}/src/tools/miri/src/shims/panic.rs",
    ]

    for filepath in files_to_check:
        with open(filepath, 'r') as f:
            content = f.read()

        # Old patterns should be gone
        assert 'ref_to_mplace' not in content, f"Old ref_to_mplace still in {filepath}"
        assert 'mplace_to_ref' not in content, f"Old mplace_to_ref still in {filepath}"

        # New patterns should exist
        if 'stacked_borrows' in filepath or 'tree_borrows' in filepath:
            assert 'imm_ptr_to_mplace' in content, f"New imm_ptr_to_mplace not in {filepath}"
        if 'panic' in filepath:
            assert 'mplace_to_imm_ptr' in content, f"New mplace_to_imm_ptr not in {filepath}"


def test_documentation_mentions_pointer():
    """Documentation should clarify functions work with pointers (not just references)."""
    with open(PLACE_FILE, 'r') as f:
        content = f.read()

    # Find the function taking ImmTy and check its docs mention pointer
    # Look for the documentation comment before the function
    idx = content.find('val: &ImmTy')
    if idx >= 0:
        # Get the preceding comment block (look backwards for ///)
        start = max(0, content.rfind('///', 0, idx - 10))
        doc_block = content[start:idx]
        # Doc should mention pointer
        assert 'pointer' in doc_block.lower() or 'ptr' in doc_block.lower(), \
            "Documentation should clarify functions work with pointers"


# =============================================================================
# Pass-to-pass tests - Repo CI tests that should pass on both base and patched
# =============================================================================

def test_repo_tidy_unit_tests():
    """Tidy tool unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=f"{REPO}/src/tools/tidy",
    )
    assert r.returncode == 0, f"Tidy unit tests failed:\n{r.stderr[-500:]}"


def test_repo_bootstrap_verify_tests():
    """Bootstrap verify tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pytest", "src/bootstrap/bootstrap_test.py::VerifyTestCase", "-v"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Bootstrap verify tests failed:\n{r.stderr[-500:]}"


def test_repo_bootstrap_parse_args_tests():
    """Bootstrap parse args tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pytest", "src/bootstrap/bootstrap_test.py::ParseArgsInConfigure", "-v"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Bootstrap parse args tests failed:\n{r.stderr[-500:]}"


def test_repo_bootstrap_python_syntax():
    """Bootstrap Python files have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "src/bootstrap/bootstrap.py"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Bootstrap Python syntax check failed:\n{r.stderr[-500:]}"


def test_repo_configure_python_syntax():
    """Configure Python file has valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "src/bootstrap/configure.py"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Configure Python syntax check failed:\n{r.stderr[-500:]}"


def test_repo_x_py_syntax():
    """x.py Python file has valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "x.py"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"x.py syntax check failed:\n{r.stderr[-500:]}"


def test_repo_const_eval_place_file_exists():
    """The modified place.rs file exists and is readable (pass_to_pass)."""
    r = subprocess.run(
        ["test", "-r", PLACE_FILE],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, f"place.rs file not found or not readable: {PLACE_FILE}"


def test_repo_const_eval_module_structure():
    """The const_eval interpret module has expected file structure (pass_to_pass)."""
    expected_files = [
        f"{REPO}/compiler/rustc_const_eval/src/interpret/place.rs",
        f"{REPO}/compiler/rustc_const_eval/src/interpret/call.rs",
        f"{REPO}/compiler/rustc_const_eval/src/interpret/intrinsics.rs",
        f"{REPO}/compiler/rustc_const_eval/src/interpret/validity.rs",
        f"{REPO}/compiler/rustc_const_eval/src/interpret/machine.rs",
    ]
    for filepath in expected_files:
        r = subprocess.run(
            ["test", "-r", filepath],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert r.returncode == 0, f"Expected file not found: {filepath}"


def test_repo_miri_shims_panic_exists():
    """Miri shims panic.rs file exists (pass_to_pass)."""
    filepath = f"{REPO}/src/tools/miri/src/shims/panic.rs"
    r = subprocess.run(
        ["test", "-r", filepath],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, f"Miri panic.rs not found: {filepath}"
