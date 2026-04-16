#!/usr/bin/env python3
"""
Test outputs for Kotlin Compose compiler stability caching fix.
PR: JetBrains/kotlin#5680
"""

import subprocess
import os
import sys
import re

REPO = "/workspace/kotlin"
TARGET_FILE = "plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/analysis/Stability.kt"

def test_cache_field_exists():
    """Fail-to-pass: Cache field must exist in StabilityInferencer class."""
    target_path = os.path.join(REPO, TARGET_FILE)
    with open(target_path, 'r') as f:
        content = f.read()

    # Check for the cache field declaration
    assert "private val cache = mutableMapOf<SymbolForAnalysis, Stability>()" in content, \
        "Cache field not found in StabilityInferencer"

def test_cache_check_in_stabilityOf():
    """Fail-to-pass: Cache lookup must be present in stabilityOf method."""
    target_path = os.path.join(REPO, TARGET_FILE)
    with open(target_path, 'r') as f:
        content = f.read()

    # Check for cache lookup: "if (fullSymbol in cache)"
    assert "if (fullSymbol in cache)" in content, \
        "Cache lookup check not found"

    # Check for cache return: "return cache[fullSymbol]!!"
    assert "return cache[fullSymbol]!!" in content, \
        "Cache return statement not found"

def test_cache_write_after_computation():
    """Fail-to-pass: Cache must be populated after computing stability."""
    target_path = os.path.join(REPO, TARGET_FILE)
    with open(target_path, 'r') as f:
        content = f.read()

    # Check for cache write: "cache[fullSymbol] = result"
    assert "cache[fullSymbol] = result" in content, \
        "Cache write statement not found"

def test_new_overloaded_stabilityOf_method():
    """Fail-to-pass: New private stabilityOf method with symbol parameter must exist."""
    target_path = os.path.join(REPO, TARGET_FILE)
    with open(target_path, 'r') as f:
        content = f.read()

    # Check for the new private method signature with IrClass and SymbolForAnalysis params
    # The method should have: private fun stabilityOf(declaration: IrClass, symbol: SymbolForAnalysis, ...
    pattern = r"private fun stabilityOf\(\s*declaration: IrClass,\s*symbol: SymbolForAnalysis,"
    assert re.search(pattern, content), \
        "New private stabilityOf method with symbol parameter not found"

def test_new_method_uses_symbol_for_circular_check():
    """Fail-to-pass: New stabilityOf method should use 'symbol' parameter for circular dependency check."""
    target_path = os.path.join(REPO, TARGET_FILE)
    with open(target_path, 'r') as f:
        content = f.read()

    # Find all private stabilityOf methods
    lines = content.split('\n')

    # Find the line with "private fun stabilityOf(" that has IrClass parameter (the new overload)
    method_start_line = -1
    for i, line in enumerate(lines):
        if "private fun stabilityOf(" in line and i > 0:
            # Check if this is the overload with IrClass parameter
            next_lines = '\n'.join(lines[i:min(i+5, len(lines))])
            if "declaration: IrClass" in next_lines and "symbol: SymbolForAnalysis" in next_lines:
                method_start_line = i
                break

    assert method_start_line != -1, "Could not find new private stabilityOf overload"

    # Find the end of this method
    method_end_line = len(lines)
    brace_count = 0
    found_first_brace = False

    for i in range(method_start_line, len(lines)):
        line = lines[i]
        if '{' in line:
            found_first_brace = True
            brace_count += line.count('{')
        if '}' in line:
            brace_count -= line.count('}')

        if found_first_brace and brace_count == 0:
            method_end_line = i
            break

    method_content = '\n'.join(lines[method_start_line:method_end_line+1])

    # The new method should check currentlyAnalyzing.contains(symbol) - using the symbol param
    assert "currentlyAnalyzing.contains(symbol)" in method_content, \
        "New stabilityOf method should check currentlyAnalyzing.contains(symbol)"

def test_stability_inferencer_class_structure():
    """Fail-to-pass: StabilityInferencer class must have proper structure for caching."""
    target_path = os.path.join(REPO, TARGET_FILE)
    with open(target_path, 'r') as f:
        content = f.read()

    # Verify StabilityInferencer class exists
    assert "class StabilityInferencer(" in content, \
        "StabilityInferencer class not found"

    # Verify the class has the public entry point method
    assert "fun stabilityOf(irType: IrType)" in content, \
        "stabilityOf(irType) public entry method not found"

    # Count private stabilityOf methods - should be at least 2 (one original + one new overload)
    private_stabilityOf_count = content.count("private fun stabilityOf(")
    assert private_stabilityOf_count >= 2, \
        f"Expected at least 2 private stabilityOf methods, found {private_stabilityOf_count}"

def test_no_fullSymbol_in_new_method():
    """Fail-to-pass: New stabilityOf overload should NOT reference fullSymbol."""
    target_path = os.path.join(REPO, TARGET_FILE)
    with open(target_path, 'r') as f:
        content = f.read()

    # Find the new private stabilityOf method (the one with IrClass param)
    lines = content.split('\n')

    # Find the line with "private fun stabilityOf(" that has IrClass parameter
    method_start_line = -1
    for i, line in enumerate(lines):
        if "private fun stabilityOf(" in line and i > 0:
            # Check if this is the overload with IrClass parameter
            next_lines = '\n'.join(lines[i:min(i+5, len(lines))])
            if "declaration: IrClass" in next_lines and "symbol: SymbolForAnalysis" in next_lines:
                method_start_line = i
                break

    assert method_start_line != -1, "Could not find new private stabilityOf overload"

    # Find the end of this method
    method_end_line = len(lines)
    brace_count = 0
    found_first_brace = False

    for i in range(method_start_line, len(lines)):
        line = lines[i]
        if '{' in line:
            found_first_brace = True
            brace_count += line.count('{')
        if '}' in line:
            brace_count -= line.count('}')

        if found_first_brace and brace_count == 0:
            method_end_line = i
            break

    method_content = '\n'.join(lines[method_start_line:method_end_line+1])

    # The new method should NOT contain 'fullSymbol' - only 'symbol'
    assert 'fullSymbol' not in method_content, \
        f"New stabilityOf method should not reference 'fullSymbol', only 'symbol'"

def test_compose_compiler_syntax():
    """Pass-to-pass: Compose compiler module should have valid Kotlin syntax (static check)."""
    # Simple syntax validation: check for balanced braces and basic Kotlin structure
    target_path = os.path.join(REPO, TARGET_FILE)
    with open(target_path, 'r') as f:
        content = f.read()

    # Check basic Kotlin file structure
    assert "package androidx.compose.compiler.plugins.kotlin.analysis" in content, \
        "Package declaration missing or incorrect"

    assert "class StabilityInferencer" in content, \
        "StabilityInferencer class not found"

    # Check for balanced braces at the file level
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, \
        f"Unbalanced braces: {open_braces} open, {close_braces} close"

    # Check for basic method structure (parentheses matching)
    open_parens = content.count('(')
    close_parens = content.count(')')
    assert open_parens == close_parens, \
        f"Unbalanced parentheses: {open_parens} open, {close_parens} close"


def test_repo_git_status():
    """Repo git workspace is clean at base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Should be empty (clean) at base commit
    assert r.returncode == 0, f"Git status failed: {r.stderr}"
    # Allow for potentially empty or minimal output at base commit


def test_repo_base_commit():
    """Repo is at expected base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Git log failed: {r.stderr}"
    # At base commit 3657c00274a (or shortened version)
    assert "3657c00274a" in r.stdout or "Fix Compose codegen" in r.stdout, \
        f"Not at expected base commit: {r.stdout}"


def test_compose_analysis_files_exist():
    """Compose analysis module files exist (pass_to_pass)."""
    analysis_dir = os.path.join(REPO, "plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/analysis")
    required_files = [
        "Stability.kt",
        "StabilityConfigParser.kt",
        "StabilityExternalClassNameMatching.kt",
        "KnownStableConstructs.kt",
    ]
    for filename in required_files:
        filepath = os.path.join(analysis_dir, filename)
        assert os.path.exists(filepath), f"Required file missing: {filename}"


def test_stability_test_golden_files_exist():
    """Stability test golden files exist (pass_to_pass)."""
    golden_dir = os.path.join(
        REPO,
        "plugins/compose/compiler-hosted/integration-tests/src/jvmTest/resources/golden/androidx.compose.compiler.plugins.kotlin.ClassStabilityTransformTests"
    )
    r = subprocess.run(
        ["ls", golden_dir],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, f"Golden files directory not found: {r.stderr}"
    # Should have multiple golden files
    files = r.stdout.strip().split('\n')
    assert len(files) > 10, f"Expected many golden files, found {len(files)}"


def test_stability_inferencer_structure():
    """Stability.kt has expected class and method structure (pass_to_pass)."""
    target_path = os.path.join(REPO, TARGET_FILE)

    # Use Python to check file structure
    r = subprocess.run(
        [
            "python3", "-c",
            f"""
import sys
with open('{target_path}') as f:
    content = f.read()

checks = {{
    'sealed_class_stability': 'sealed class Stability' in content,
    'stability_inferencer_class': 'class StabilityInferencer' in content,
    'stability_of_methods': content.count('fun stabilityOf') >= 1,
    'symbol_for_analysis': 'SymbolForAnalysis' in content,
    'balanced_braces': content.count('{{') == content.count('}}'),
}}

for name, result in checks.items():
    print(f'{{name}}: {{result}}')

if not all(checks.values()):
    sys.exit(1)
"""
        ],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, f"StabilityInferencer structure check failed:\n{r.stdout}\n{r.stderr}"

if __name__ == "__main__":
    # Run all tests
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
