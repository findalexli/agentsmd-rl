"""
Test suite for sui-option-macros task.

This tests that 5 new macro functions are added to std::option:
- map_mut
- is_none_or
- fold
- fold_ref
- fold_mut

Since we don't have the Move compiler in the test environment, we verify by:
1. Checking the functions exist in the source file (structural)
2. Checking syntax patterns are correct
3. Checking documentation comments exist
"""

import subprocess
import sys
import os
import re

REPO = "/workspace/sui"
OPTION_MOVE = "crates/sui-framework/packages/move-stdlib/sources/option.move"
FULL_OPTION_PATH = os.path.join(REPO, OPTION_MOVE)
MOVE_STDLIB_PATH = "crates/sui-framework/packages/move-stdlib"
FULL_MOVE_STDLIB_PATH = os.path.join(REPO, MOVE_STDLIB_PATH)


def test_option_file_exists():
    """Verify the option.move file exists."""
    assert os.path.exists(FULL_OPTION_PATH), f"File not found: {FULL_OPTION_PATH}"


def read_option_file():
    """Read and return the option.move file content."""
    with open(FULL_OPTION_PATH, 'r') as f:
        return f.read()


def test_map_mut_exists():
    """Verify map_mut macro function exists in option.move."""
    content = read_option_file()
    # Check for the function signature
    assert "public macro fun map_mut<" in content, "map_mut macro function not found"
    # Check for implementation details
    assert "&mut Option<$T>" in content, "map_mut parameter type not found"


def test_is_none_or_exists():
    """Verify is_none_or macro function exists in option.move."""
    content = read_option_file()
    assert "public macro fun is_none_or<" in content, "is_none_or macro function not found"
    assert "o.is_none()" in content, "is_none_or implementation not found"


def test_fold_exists():
    """Verify fold macro function exists in option.move."""
    content = read_option_file()
    assert "public macro fun fold<" in content, "fold macro function not found"
    assert "o.destroy_some()" in content, "fold implementation not found"


def test_fold_ref_exists():
    """Verify fold_ref macro function exists in option.move."""
    content = read_option_file()
    assert "public macro fun fold_ref<" in content, "fold_ref macro function not found"


def test_fold_mut_exists():
    """Verify fold_mut macro function exists in option.move."""
    content = read_option_file()
    assert "public macro fun fold_mut<" in content, "fold_mut macro function not found"
    assert "&mut Option<$T>" in content, "fold_mut parameter type not found"


def test_map_mut_has_docs():
    """Verify map_mut has documentation comment."""
    content = read_option_file()
    # Look for documentation comment before map_mut
    pattern = r"///.*[Mm]ap.*[Oo]ption.*[Mm]ut"
    assert re.search(pattern, content), "map_mut documentation not found"


def test_is_none_or_has_docs():
    """Verify is_none_or has documentation comment."""
    content = read_option_file()
    pattern = r"///.*is_none_or|///.*[Nn]one.*[Oo]r"
    assert re.search(pattern, content), "is_none_or documentation not found"


def test_fold_has_docs():
    """Verify fold has documentation comment."""
    content = read_option_file()
    pattern = r"///.*fold|///.*[Cc]onsume.*[Oo]ption"
    assert re.search(pattern, content, re.IGNORECASE), "fold documentation not found"


def test_all_five_macros_present():
    """Verify all 5 macros are present in the source file."""
    content = read_option_file()
    macros = ["map_mut", "is_none_or", "fold", "fold_ref", "fold_mut"]
    for macro in macros:
        pattern = rf"public macro fun {macro}<"
        assert re.search(pattern, content), f"Macro {macro} not found in option.move"


def test_macro_syntax_valid():
    """Verify the macro syntax follows Move patterns."""
    content = read_option_file()
    # Check that type parameters use $T, $U, $R convention
    type_param_pattern = r"public macro fun \w+<\$[TUR]"
    matches = re.findall(type_param_pattern, content)
    assert len(matches) >= 5, "Expected at least 5 new macros with proper type params"


def test_map_mut_correct_signature():
    """Verify map_mut has the correct function signature."""
    content = read_option_file()
    # Should take &mut Option<$T> and closure |&mut $T| -> $U
    pattern = r"public macro fun map_mut<\$T, \$U>\(\$o: &mut Option<\$T>, \$f: \|&mut \$T\| -> \$U\): Option<\$U>"
    assert re.search(pattern, content), "map_mut signature doesn't match expected pattern"


def test_is_none_or_correct_signature():
    """Verify is_none_or has the correct function signature."""
    content = read_option_file()
    pattern = r"public macro fun is_none_or<\$T>\(\$o: &Option<\$T>, \$f: \|&\$T\| -> bool\): bool"
    assert re.search(pattern, content), "is_none_or signature doesn't match expected pattern"


def test_fold_correct_signature():
    """Verify fold has the correct function signature."""
    content = read_option_file()
    pattern = r"public macro fun fold<\$T, \$R>\(\$o: Option<\$T>, \$none: \$R, \$some: \|\$T\| -> \$R\): \$R"
    assert re.search(pattern, content), "fold signature doesn't match expected pattern"


def test_fold_ref_correct_signature():
    """Verify fold_ref has the correct function signature."""
    content = read_option_file()
    pattern = r"public macro fun fold_ref<\$T, \$R>\(\$o: &Option<\$T>, \$none: \$R, \$some: \|&\$T\| -> \$R\): \$R"
    assert re.search(pattern, content), "fold_ref signature doesn't match expected pattern"


def test_fold_mut_correct_signature():
    """Verify fold_mut has the correct function signature."""
    content = read_option_file()
    pattern = r"public macro fun fold_mut<\$T, \$R>\(\$o: &mut Option<\$T>, \$none: \$R, \$some: \|&mut \$T\| -> \$R\): \$R"
    assert re.search(pattern, content), "fold_mut signature doesn't match expected pattern"


def test_count_new_macros():
    """Count that we have at least the 5 new macro functions."""
    content = read_option_file()
    # Count public macro fun declarations
    matches = re.findall(r"public macro fun (\w+)<", content)
    expected_new = ["map_mut", "is_none_or", "fold", "fold_ref", "fold_mut"]
    for macro in expected_new:
        assert macro in matches, f"Expected macro {macro} not found in declared macros"


def test_no_lint_suppressions():
    """Verify no #[allow(...)] suppressions are added."""
    content = read_option_file()
    # Check for lint suppressions
    assert "#[allow(" not in content, "Lint suppressions found in option.move"
    assert "#[allow(dead_code)]" not in content, "dead_code suppression found"
    assert "#[allow(unused)]" not in content, "unused suppression found"


def test_file_structure_preserved():
    """Verify the file structure is intact with expected sections."""
    content = read_option_file()
    # Check for standard Option functions that should exist
    assert "public fun is_some<" in content, "Core is_some function missing"
    assert "public fun is_none<" in content, "Core is_none function missing"
    assert "public macro fun map<" in content, "Existing map macro missing"
    assert "public macro fun map_ref<" in content, "Existing map_ref macro missing"


# === Pass-to-Pass Repo Tests ===
# These tests use subprocess.run() to execute actual repo CI checks

def test_option_move_syntax_valid():
    """Verify option.move has valid Move syntax - braces are balanced (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c",
         f"cd {REPO} && cat {OPTION_MOVE} | tr -d '[:space:]' | " +
         "awk '{open=0; for(i=1;i<=length($0);i++){c=substr($0,i,1); if(c==\"{\")open++; if(c==\"}\")open--; if(open<0)exit 1}} END{if(open!=0)exit 1}'"
        ],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, "option.move has unbalanced braces/syntax error"


def test_move_stdlib_package_structure():
    """Verify move-stdlib package has required files (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c",
         f"test -f {FULL_MOVE_STDLIB_PATH}/Move.toml && " +
         f"test -d {FULL_MOVE_STDLIB_PATH}/sources && " +
         f"test -d {FULL_MOVE_STDLIB_PATH}/tests"
        ],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, "move-stdlib package structure is incomplete"


def test_option_tests_file_exists():
    """Verify option_tests.move exists with test content (pass_to_pass)."""
    option_tests_path = f"{FULL_MOVE_STDLIB_PATH}/tests/option_tests.move"
    r = subprocess.run(
        ["bash", "-c",
         rf"test -f {option_tests_path} && " +
         rf"grep -q '#\[test\]' {option_tests_path} && " +
         rf"grep -q 'module std::option_tests' {option_tests_path}"
        ],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, "option_tests.move missing or invalid structure"


def test_move_toml_valid():
    """Verify Move.toml is valid TOML format (pass_to_pass)."""
    move_toml_path = f"{FULL_MOVE_STDLIB_PATH}/Move.toml"
    r = subprocess.run(
        ["bash", "-c",
         rf"cat {move_toml_path} | grep -q '\[package\]' && " +
         rf"cat {move_toml_path} | grep -q 'name.*=' && " +
         rf"cat {move_toml_path} | grep -q '\[addresses\]'"
        ],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, "Move.toml missing required sections"


def test_option_move_module_decl():
    """Verify option.move has valid module declaration (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c",
         f"grep -q '^module std::option' {FULL_OPTION_PATH} && " +
         f"grep -q 'public struct Option<' {FULL_OPTION_PATH}"
        ],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, "option.move missing valid module declaration"


def test_move_source_files_present():
    """Verify expected Move source files are present in stdlib (pass_to_pass)."""
    sources_dir = f"{FULL_MOVE_STDLIB_PATH}/sources"
    required_files = ["option.move", "vector.move", "string.move", "ascii.move"]
    cmd = " && ".join([f"test -f {sources_dir}/{f}" for f in required_files])
    r = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, "Required Move source files missing"


def test_option_move_no_syntax_errors():
    """Verify option.move has no obvious syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c",
         rf"cd {REPO} && " +
         rf"! grep -n 'public macro fun' {OPTION_MOVE} | grep -v '<\$' | grep -v '>' | head -1"
        ],
        capture_output=True, text=True, timeout=30,
    )
    # This check is basic - it looks for macro declarations without type parameters
    # The returncode will be 0 if grep found nothing (good) or 1 if found issues
    # We need to invert: if r.returncode == 0 and r.stdout == "", then pass
    assert r.returncode != 0 or r.stdout.strip() == "", "option.move may have syntax issues"


def test_option_macros_consistent():
    """Verify macro patterns are consistent across the file (pass_to_pass)."""
    # Check that macros exist and use type parameters
    content = read_option_file()
    macro_count = len(re.findall(r"public macro fun \w+", content))
    type_param_count = len(re.findall(r"\$[TUR]", content))
    # Base commit has 13 macros (5 new ones will be added)
    assert macro_count >= 10, f"Too few macros found: {macro_count}"
    assert type_param_count >= 10, f"Too few type parameters: {type_param_count}"


def test_all_test_files_executable():
    """Verify all Move test files are readable (pass_to_pass)."""
    tests_dir = f"{FULL_MOVE_STDLIB_PATH}/tests"
    # Check that test files exist and are readable
    r = subprocess.run(
        ["bash", "-c",
         f"test -r {tests_dir}/option_tests.move && " +
         f"test -r {tests_dir}/vector_tests.move && " +
         f"test -r {tests_dir}/string_tests.move"
        ],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, "Required Move test files are not readable"
