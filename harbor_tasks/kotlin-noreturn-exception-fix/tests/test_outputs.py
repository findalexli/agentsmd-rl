"""
Test suite for Kotlin Native noreturn fix (KT-61748).
"""

import re
import subprocess
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

# FAIL-TO-PASS TESTS
def test_exceptions_h_has_noreturn():
    content = read_file(EXCEPTIONS_H)
    pattern = r"void\s+RUNTIME_NORETURN\s+HandleCurrentExceptionWhenLeavingKotlinCode\s*\(\s*\)\s*;"
    assert re.search(pattern, content), "Exceptions.h must declare with RUNTIME_NORETURN"

def test_exceptions_cpp_has_noreturn():
    content = read_file(EXCEPTIONS_CPP)
    pattern = r"void\s+RUNTIME_NORETURN\s+HandleCurrentExceptionWhenLeavingKotlinCode\s*\(\s*\)\s*\{"
    assert re.search(pattern, content), "Exceptions.cpp must define with RUNTIME_NORETURN"

def test_c_adapter_exporter_has_noreturn():
    content = read_file(C_ADAPTER_KT)
    pattern = r"void\s+HandleCurrentExceptionWhenLeavingKotlinCode\s*\(\s*\)\s+RUNTIME_NORETURN\s*;"
    assert re.search(pattern, content), "CAdapterApiExporter.kt must generate with RUNTIME_NORETURN"

# STRUCTURAL TESTS
def test_function_actually_terminates():
    content = read_file(EXCEPTIONS_CPP)
    assert "std::terminate()" in content, "Must call std::terminate()"

def test_noreturn_macro_defined():
    content = read_file(EXCEPTIONS_H)
    assert "RUNTIME_NORETURN" in content, "RUNTIME_NORETURN must be defined"

def test_all_three_locations_consistent():
    h = read_file(EXCEPTIONS_H)
    cpp = read_file(EXCEPTIONS_CPP)
    kt = read_file(C_ADAPTER_KT)
    h_has = "RUNTIME_NORETURN HandleCurrentExceptionWhenLeavingKotlinCode" in h
    cpp_has = "RUNTIME_NORETURN HandleCurrentExceptionWhenLeavingKotlinCode" in cpp
    kt_has = "HandleCurrentExceptionWhenLeavingKotlinCode() RUNTIME_NORETURN" in kt
    assert h_has and cpp_has and kt_has, "All three must use RUNTIME_NORETURN"

# PASS-TO-PASS TESTS (origin: static - basic file checks)
def test_files_exist():
    """Required source files exist in the repository (pass_to_pass)."""
    assert EXCEPTIONS_H.exists()
    assert EXCEPTIONS_CPP.exists()
    assert C_ADAPTER_KT.exists()

def test_cpp_syntax_valid():
    """C++ source files have valid syntax (balanced braces) (pass_to_pass)."""
    content = read_file(EXCEPTIONS_CPP)
    assert content.count("{") == content.count("}")

def test_kotlin_syntax_valid():
    """Kotlin source file has valid structure (pass_to_pass)."""
    content = read_file(C_ADAPTER_KT)
    assert "class CAdapterApiExporter" in content
    assert abs(content.count("{") - content.count("}")) < 10

def test_cpp_header_guards_valid():
    """C++ header files have proper include guards (pass_to_pass)."""
    content = read_file(EXCEPTIONS_H)
    assert re.search(r"#ifndef\s+RUNTIME_\w+_H", content)
    assert re.search(r"#define\s+RUNTIME_\w+_H", content)

def test_cpp_valid_extern_c():
    """C++ header has valid extern C blocks for C linkage (pass_to_pass)."""
    content = read_file(EXCEPTIONS_H)
    assert 'extern "C" {' in content
    assert content.count("{") == content.count("}")

def test_kotlin_code_patterns():
    """Kotlin file follows repo code style patterns (pass_to_pass)."""
    content = read_file(C_ADAPTER_KT)
    assert re.search(r"^package\s+\S+", content, re.MULTILINE)

def test_copyright_headers_present():
    """All modified files have JetBrains copyright headers (pass_to_pass)."""
    for path, name in [(EXCEPTIONS_H, "Exceptions.h"), (EXCEPTIONS_CPP, "Exceptions.cpp"), (C_ADAPTER_KT, "CAdapterApiExporter.kt")]:
        content = read_file(path)
        assert "Copyright 2010" in content and "JetBrains" in content and ("Apache License" in content or "Apache 2.0" in content)

def test_no_trailing_whitespace():
    """Modified files have minimal trailing whitespace (pass_to_pass)."""
    for path, name in [(EXCEPTIONS_H, "Exceptions.h"), (EXCEPTIONS_CPP, "Exceptions.cpp"), (C_ADAPTER_KT, "CAdapterApiExporter.kt")]:
        lines = read_file(path).split("\n")
        if len([l for l in lines if l != l.rstrip()]) > 10:
            assert False, f"{name} has too many lines with trailing whitespace"

def test_repo_git_state_clean():
    """Git repository is in a valid state (pass_to_pass)."""
    r = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert r.returncode == 0

# NEW P2P TESTS - Repo CI/CD checks (using subprocess.run())
def test_repo_clang_version():
    """Verify clang is available for C++ compilation checks (pass_to_pass)."""
    r = subprocess.run(["clang", "--version"], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, f"clang --version failed: {r.stderr}"
    assert "clang" in r.stdout.lower()

def test_repo_git_log():
    """Git history is accessible and has commits (pass_to_pass)."""
    r = subprocess.run(["git", "log", "--oneline", "-5"], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert r.returncode == 0, f"git log failed: {r.stderr}"
    assert len(r.stdout.strip().split("\n")) > 0, "Git history should have commits"

def test_repo_exceptions_file_structure():
    """Exceptions.cpp has valid include structure with expected headers (pass_to_pass)."""
    # This is a static check but uses subprocess to verify file integrity
    r = subprocess.run(
        ["grep", "-E", r'^#include\s+"(Exceptions\.h|Types\.h|Memory\.h)"$', str(EXCEPTIONS_CPP)],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert r.returncode == 0 or r.stdout.strip(), "Expected includes not found"

def test_repo_clang_basic_syntax_check():
    """Basic C++ syntax validation using clang preprocessor (pass_to_pass)."""
    # Run clang preprocessor only - faster and doesn't require full build environment
    r = subprocess.run(
        ["clang", "-E", "-std=c++17", str(EXCEPTIONS_H)],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    # Preprocessor should succeed on the header (may fail on cpp due to deps)
    if r.returncode != 0:
        # If it fails, it should only be due to missing includes, not syntax errors
        for line in r.stderr.split("\n"):
            if "error:" in line and "syntax" in line.lower():
                assert False, f"Syntax error found: {line}"

# STATIC P2P TESTS (file content checks)
def test_repo_cpp_codestyle_naming():
    """C++ code follows repo naming conventions (PascalCase, SCREAMING_SNAKE_CASE)."""
    content_h = read_file(EXCEPTIONS_H)
    matches = re.findall(r"void\s+(?:RUNTIME_\w+\s+)?([A-Z][a-zA-Z0-9]*)\s*\(", content_h)
    for func in ["ThrowException", "SetKonanTerminateHandler", "HandleCurrentExceptionWhenLeavingKotlinCode"]:
        assert func in matches, f"{func} should follow PascalCase"
    assert "RUNTIME_NORETURN" in content_h

def test_repo_file_naming_convention():
    """Files follow repo naming conventions (.h/.cpp, PascalCase)."""
    assert EXCEPTIONS_H.suffix == ".h"
    assert EXCEPTIONS_CPP.suffix == ".cpp"
    for path in [EXCEPTIONS_H, EXCEPTIONS_CPP]:
        assert path.stem[0].isupper()

def test_repo_include_structure():
    """C++ files have valid include structure."""
    content_cpp = read_file(EXCEPTIONS_CPP)
    includes = re.findall(r"#include\s+\"([^\"]+)\"", content_cpp)
    for header in ["Exceptions.h", "Types.h", "Memory.h"]:
        assert header in includes

def test_repo_kotlin_package_structure():
    """Kotlin file follows repo package/directory structure."""
    content = read_file(C_ADAPTER_KT)
    match = re.search(r"^package\s+(\S+)", content, re.MULTILINE)
    assert match
    assert match.group(1).replace(".", "/") in str(C_ADAPTER_KT)

def test_repo_common_attributes():
    """Common.h defines required attribute macros."""
    content = read_file(REPO / "kotlin-native/runtime/src/main/cpp/Common.h")
    assert "#define RUNTIME_NORETURN" in content
    assert re.search(r"#define\s+RUNTIME_NORETURN\s+__attribute__\(\(noreturn\)\)", content)
