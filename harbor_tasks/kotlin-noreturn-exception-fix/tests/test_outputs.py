"""
Test suite for Kotlin Native noreturn fix (KT-61748).

Behavioral tests that verify RUNTIME_NORETURN is properly applied by:
1. Using Clang to verify noreturn attribute in C/C++ AST (for headers)
2. Compiling C++ code that includes the fixed headers and verifying behavior
3. For files that can't be compiled standalone, verifying source patterns
       that would produce correct behavior when compiled
"""

import subprocess
import tempfile
import re
from pathlib import Path

REPO = Path("/workspace/kotlin")
EXCEPTIONS_H = REPO / "kotlin-native/runtime/src/main/cpp/Exceptions.h"
EXCEPTIONS_CPP = REPO / "kotlin-native/runtime/src/main/cpp/Exceptions.cpp"
C_ADAPTER_KT = REPO / "kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/cexport/CAdapterApiExporter.kt"


def read_file(path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def clang_function_has_noreturn(header_path, function_name):
    """
    Use Clang AST to verify a function declaration has the noreturn attribute.
    
    This works for header files (.h) where the function is declared.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.cpp"
        include_directive = f'#include "{header_path}"\n'
        test_file.write_text(include_directive + f'void {function_name}();\n')

        result = subprocess.run(
            ["clang", "-Xclang", "-ast-dump", "-fsyntax-only",
             "-I", str(header_path.parent), str(test_file)],
            capture_output=True, text=True, timeout=60
        )

        if result.returncode != 0:
            return False

        ast_output = result.stdout
        lines = ast_output.split('\n')

        # Find FunctionDecl lines for the function and check for noreturn on THAT line
        for line in lines:
            if function_name in line and 'FunctionDecl' in line:
                if 'noreturn' in line.lower():
                    return True
        return False


def clang_compile_with_noreturn_check(cpp_code, description=""):
    """
    Compile C++ code and check for -Wreturn-type warnings.
    
    Returns (success, warning_output).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.cpp"
        test_file.write_text(cpp_code)

        result = subprocess.run(
            ["clang", "-c", "-Wreturn-type", "-Wall", "-Wextra", "-std=c++17",
             "-I", str(EXCEPTIONS_H.parent), str(test_file)],
            capture_output=True, text=True, timeout=60
        )

        # Check for -Wreturn-type warnings specifically
        return_type_warnings = [
            line for line in result.stderr.split('\n')
            if 'warning:' in line and 'return' in line.lower()
        ]

        return len(return_type_warnings) == 0, return_type_warnings


# ============================================================================
# FAIL-TO-PASS TESTS - Behavioral
# ============================================================================

def test_exceptions_h_has_noreturn():
    """
    Verify Exceptions.h declares HandleCurrentExceptionWhenLeavingKotlinCode
    with RUNTIME_NORETURN using Clang AST inspection.
    """
    has_attr = clang_function_has_noreturn(EXCEPTIONS_H, "HandleCurrentExceptionWhenLeavingKotlinCode")
    assert has_attr, (
        "HandleCurrentExceptionWhenLeavingKotlinCode in Exceptions.h lacks noreturn attribute. "
        "The AST shows the function declaration must have RUNTIME_NORETURN."
    )


def test_exceptions_cpp_has_noreturn():
    """
    Verify Exceptions.cpp defines HandleCurrentExceptionWhenLeavingKotlinCode
    with RUNTIME_NORETURN.
    
    Since Exceptions.cpp cannot be compiled standalone (missing project includes),
    we verify the source pattern that would produce correct behavior.
    The pattern should match: void RUNTIME_NORETURN HandleCurrentExceptionWhenLeavingKotlinCode()
    """
    content = read_file(EXCEPTIONS_CPP)
    
    # Check for the definition pattern with RUNTIME_NORETURN before the function name
    pattern = r'void\s+RUNTIME_NORETURN\s+HandleCurrentExceptionWhenLeavingKotlinCode\s*\(\s*\)\s*\{'
    has_fix = bool(re.search(pattern, content))
    
    assert has_fix, (
        "Exceptions.cpp must define HandleCurrentExceptionWhenLeavingKotlinCode with RUNTIME_NORETURN. "
        "Expected pattern: void RUNTIME_NORETURN HandleCurrentExceptionWhenLeavingKotlinCode() {"
    )
    
    # Additionally verify using Clang that the header declaration has noreturn
    # (this confirms the macro expansion works)
    has_attr = clang_function_has_noreturn(EXCEPTIONS_H, "HandleCurrentExceptionWhenLeavingKotlinCode")
    assert has_attr, "Header declaration must have noreturn attribute"


def test_c_adapter_exporter_generates_correct_output():
    """
    Verify CAdapterApiExporter.kt generates C code with RUNTIME_NORETURN
    by checking both the Kotlin source pattern AND verifying Clang accepts
    the generated code pattern without -Wreturn-type warnings.
    """
    kt_content = read_file(C_ADAPTER_KT)

    # Check that the Kotlin source generates RUNTIME_NORETURN after the function
    # The pattern in generated C code: void HandleCurrentExceptionWhenLeavingKotlinCode() RUNTIME_NORETURN;
    pattern = r'\|void\s+HandleCurrentExceptionWhenLeavingKotlinCode\s*\(\s*\)\s+RUNTIME_NORETURN\s*;'
    has_fix = bool(re.search(pattern, kt_content))

    assert has_fix, (
        "CAdapterApiExporter.kt must generate: void HandleCurrentExceptionWhenLeavingKotlinCode() RUNTIME_NORETURN; "
        "The RUNTIME_NORETURN must appear after the function declaration (as is conventional for C attributes)."
    )

    # Verify the generated code pattern compiles without -Wreturn-type warnings
    # This is the actual bug fix: Clang warns about non-void functions not returning
    # when calling a noreturn function in catch blocks. With RUNTIME_NORETURN, no warning.
    mock_code = '''
extern "C" {
#define RUNTIME_NORETURN __attribute__((noreturn))
void HandleCurrentExceptionWhenLeavingKotlinCode() RUNTIME_NORETURN;
}

// Simulates Kotlin-generated code: function returning int with try-catch
int Kotlin_function_with_exception_handling() {
    try {
        return 1;
    } catch (...) {
        HandleCurrentExceptionWhenLeavingKotlinCode();
    }
}
'''

    success, warnings = clang_compile_with_noreturn_check(mock_code)
    assert success, (
        f"Generated code pattern causes -Wreturn-type warnings. "
        f"RUNTIME_NORETURN should suppress these warnings.\n"
        + '\n'.join(warnings)
    )


def test_function_actually_terminates():
    """
    Verify HandleCurrentExceptionWhenLeavingKotlinCode calls std::terminate
    or rethrows - the semantic justification for RUNTIME_NORETURN.
    """
    content = read_file(EXCEPTIONS_CPP)

    lines = content.split('\n')
    in_function = False
    function_body_has_terminate_or_rethrow = False

    for line in lines:
        if "HandleCurrentExceptionWhenLeavingKotlinCode()" in line and "{" in line:
            in_function = True
        if in_function:
            if "std::terminate()" in line:
                function_body_has_terminate_or_rethrow = True
                break
            if "throw;" in line:
                function_body_has_terminate_or_rethrow = True
                break
            if line.strip() == "}" and in_function:
                break

    assert function_body_has_terminate_or_rethrow, (
        "HandleCurrentExceptionWhenLeavingKotlinCode must call std::terminate() or throw; "
        "This semantic behavior justifies the RUNTIME_NORETURN attribute."
    )


def test_noreturn_macro_defined():
    """
    Verify RUNTIME_NORETURN macro is defined and usable.
    """
    common_h = REPO / "kotlin-native/runtime/src/main/cpp/Common.h"
    h_content = read_file(EXCEPTIONS_H)
    
    found_definition = False
    if "#define RUNTIME_NORETURN" in h_content:
        found_definition = True
    
    if common_h.exists():
        common_content = read_file(common_h)
        if "#define RUNTIME_NORETURN" in common_content:
            found_definition = True
    
    assert found_definition, "RUNTIME_NORETURN must be #defined in Common.h or Exceptions.h"

    # Verify the macro is usable
    test_code = '''
#define RUNTIME_NORETURN __attribute__((noreturn))
RUNTIME_NORETURN void test_func();
'''
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.cpp"
        test_file.write_text(test_code)

        result = subprocess.run(
            ["clang", "-fsyntax-only", "-std=c++17", str(test_file)],
            capture_output=True, text=True, timeout=30
        )

        assert result.returncode == 0, f"RUNTIME_NORETURN macro is not usable: {result.stderr}"


def test_all_three_locations_consistent():
    """
    Verify all three locations consistently use RUNTIME_NORETURN.
    """
    h_content = read_file(EXCEPTIONS_H)
    cpp_content = read_file(EXCEPTIONS_CPP)
    kt_content = read_file(C_ADAPTER_KT)

    # Header: RUNTIME_NORETURN before function name
    h_has = bool(re.search(r'void\s+RUNTIME_NORETURN\s+HandleCurrentExceptionWhenLeavingKotlinCode\s*\(', h_content))
    
    # Cpp: RUNTIME_NORETURN before function name in definition
    cpp_has = bool(re.search(r'void\s+RUNTIME_NORETURN\s+HandleCurrentExceptionWhenLeavingKotlinCode\s*\(\s*\)\s*\{', cpp_content))
    
    # Kotlin: RUNTIME_NORETURN after function in generated C code pattern
    kt_has = bool(re.search(r'\|void\s+HandleCurrentExceptionWhenLeavingKotlinCode\s*\(\s*\)\s+RUNTIME_NORETURN', kt_content))

    assert h_has, "Exceptions.h missing: void RUNTIME_NORETURN HandleCurrentExceptionWhenLeavingKotlinCode"
    assert cpp_has, "Exceptions.cpp missing: void RUNTIME_NORETURN HandleCurrentExceptionWhenLeavingKotlinCode() {"
    assert kt_has, "CAdapterApiExporter.kt missing generation of: void HandleCurrentExceptionWhenLeavingKotlinCode() RUNTIME_NORETURN"


# ============================================================================
# PASS-TO-PASS TESTS - Static checks
# ============================================================================

def test_files_exist():
    assert EXCEPTIONS_H.exists()
    assert EXCEPTIONS_CPP.exists()
    assert C_ADAPTER_KT.exists()


def test_cpp_syntax_valid():
    content = read_file(EXCEPTIONS_CPP)
    assert content.count("{") == content.count("}")


def test_kotlin_syntax_valid():
    content = read_file(C_ADAPTER_KT)
    assert "class CAdapterApiExporter" in content
    assert abs(content.count("{") - content.count("}")) < 10


def test_cpp_header_guards_valid():
    content = read_file(EXCEPTIONS_H)
    assert re.search(r"#ifndef\s+RUNTIME_\w+_H", content)
    assert re.search(r"#define\s+RUNTIME_\w+_H", content)


def test_cpp_valid_extern_c():
    content = read_file(EXCEPTIONS_H)
    assert 'extern "C" {' in content
    assert content.count("{") == content.count("}")


def test_kotlin_code_patterns():
    content = read_file(C_ADAPTER_KT)
    assert re.search(r"^package\s+\S+", content, re.MULTILINE)


def test_copyright_headers_present():
    for path, name in [(EXCEPTIONS_H, "Exceptions.h"), (EXCEPTIONS_CPP, "Exceptions.cpp"), (C_ADAPTER_KT, "CAdapterApiExporter.kt")]:
        content = read_file(path)
        assert "Copyright 2010" in content and "JetBrains" in content and ("Apache License" in content or "Apache 2.0" in content)


def test_no_trailing_whitespace():
    for path, name in [(EXCEPTIONS_H, "Exceptions.h"), (EXCEPTIONS_CPP, "Exceptions.cpp"), (C_ADAPTER_KT, "CAdapterApiExporter.kt")]:
        lines = read_file(path).split("\n")
        if len([l for l in lines if l != l.rstrip()]) > 10:
            assert False, f"{name} has too many lines with trailing whitespace"


def test_repo_git_state_clean():
    r = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert r.returncode == 0


def test_repo_clang_version():
    r = subprocess.run(["clang", "--version"], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, f"clang --version failed: {r.stderr}"
    assert "clang" in r.stdout.lower()


def test_repo_git_log():
    r = subprocess.run(["git", "log", "--oneline", "-5"], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert r.returncode == 0, f"git log failed: {r.stderr}"
    assert len(r.stdout.strip().split("\n")) > 0


def test_repo_exceptions_file_structure():
    r = subprocess.run(
        ["grep", "-E", r'^#include\s+"(Exceptions\.h|Types\.h|Memory\.h)"$', str(EXCEPTIONS_CPP)],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert r.returncode == 0 or r.stdout.strip(), "Expected includes not found"


def test_repo_clang_basic_syntax_check():
    r = subprocess.run(
        ["clang", "-E", "-std=c++17", str(EXCEPTIONS_H)],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    if r.returncode != 0:
        for line in r.stderr.split("\n"):
            if "error:" in line and "syntax" in line.lower():
                assert False, f"Syntax error found: {line}"


def test_repo_cpp_codestyle_naming():
    content_h = read_file(EXCEPTIONS_H)
    matches = re.findall(r"void\s+(?:RUNTIME_\w+\s+)?([A-Z][a-zA-Z0-9]*)\s*\(", content_h)
    for func in ["ThrowException", "SetKonanTerminateHandler", "HandleCurrentExceptionWhenLeavingKotlinCode"]:
        assert func in matches
    assert "RUNTIME_NORETURN" in content_h


def test_repo_file_naming_convention():
    assert EXCEPTIONS_H.suffix == ".h"
    assert EXCEPTIONS_CPP.suffix == ".cpp"
    for path in [EXCEPTIONS_H, EXCEPTIONS_CPP]:
        assert path.stem[0].isupper()


def test_repo_include_structure():
    content_cpp = read_file(EXCEPTIONS_CPP)
    includes = re.findall(r"#include\s+\"([^\"]+)\"", content_cpp)
    for header in ["Exceptions.h", "Types.h", "Memory.h"]:
        assert header in includes


def test_repo_kotlin_package_structure():
    content = read_file(C_ADAPTER_KT)
    match = re.search(r"^package\s+(\S+)", content, re.MULTILINE)
    assert match
    assert match.group(1).replace(".", "/") in str(C_ADAPTER_KT)


def test_repo_common_attributes():
    common_h = REPO / "kotlin-native/runtime/src/main/cpp/Common.h"
    if common_h.exists():
        content = read_file(common_h)
        assert "#define RUNTIME_NORETURN" in content
        assert re.search(r"#define\s+RUNTIME_NORETURN\s+__attribute__\(\(noreturn\)\)", content)
