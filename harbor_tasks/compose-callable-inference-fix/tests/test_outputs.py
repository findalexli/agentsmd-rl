#!/usr/bin/env python3
"""
Test outputs for compose-callable-inference-fix task.

This task fixes callableInferenceNodeOf in ComposableTargetChecker.kt to properly
handle scheme storage for callable inference nodes. The fix ensures:
1. FirCallableElementInferenceNode.kind returns NodeKind.Function (not Expression)
2. callableInferenceNodeOf properly handles FirFunctionCall expressions
3. Nodes have correct element properties for scheme caching
"""

import subprocess
import sys
import re
from pathlib import Path

REPO = Path("/workspace/kotlin")
TARGET_FILE = REPO / "plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/k2/ComposableTargetChecker.kt"


def test_file_exists():
    """Verify the target file exists."""
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"


def test_syntax_valid():
    """Verify the Kotlin file compiles without syntax errors."""
    result = subprocess.run(
        ["./gradlew", ":plugins:compose:compiler-hosted:compileKotlin", "-q"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Syntax error:\n{result.stderr.decode()}"


def test_callable_node_kind_returns_function():
    """
    Verify FirCallableElementInferenceNode.kind returns NodeKind.Function.

    This is a key behavioral fix - the node kind should be Function, not Expression.
    """
    content = TARGET_FILE.read_text()

    # Find the FirCallableElementInferenceNode class
    class_pattern = r'private class FirCallableElementInferenceNode\([^}]+\) : FirElementInferenceNode\([^)]+\) \{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    match = re.search(class_pattern, content, re.DOTALL)
    assert match, "FirCallableElementInferenceNode class not found"

    class_body = match.group(1)

    # Check that kind property returns NodeKind.Function
    kind_pattern = r'override val kind\s+get\(\)\s*=\s*NodeKind\.Function'
    assert re.search(kind_pattern, class_body), (
        "FirCallableElementInferenceNode.kind must return NodeKind.Function. "
        "This is the key fix for proper node classification."
    )


def test_callable_inference_node_of_structure():
    """
    Verify callableInferenceNodeOf has proper control flow with explicit returns.

    The fix restructures the function to use explicit returns instead of the Elvis operator chain.
    """
    content = TARGET_FILE.read_text()

    # Find the callableInferenceNodeOf function
    func_pattern = r'@OptIn\(SymbolInternals::class\)\s*private fun callableInferenceNodeOf\([^)]+\): FirInferenceNode \{'
    assert re.search(func_pattern, content), (
        "callableInferenceNodeOf must have explicit return type FirInferenceNode "
        "and use explicit return statements"
    )

    # Check for the explicit return pattern (not Elvis operator chain)
    # The fix should have "return it" for parameterInferenceNodeOrNull
    assert 'parameterInferenceNodeOrNull(expression, context)?.let {' in content, (
        "Must check parameterInferenceNodeOrNull first with explicit return"
    )
    assert 'return it' in content, "Must use explicit return statements"


def test_function_call_handling():
    """
    Verify FirFunctionCall is properly handled with callable.fir as element.

    This is a key behavioral fix - for FirFunctionCall, we should use callable.fir
    as the element to ensure proper scheme caching.
    """
    content = TARGET_FILE.read_text()

    # Check for FirFunctionCall handling
    func_call_pattern = r'\(expression as\? FirFunctionCall\)\?\.let \{\s*return FirCallableElementInferenceNode\(callable, callable\.fir\)'
    assert re.search(func_call_pattern, content), (
        "Must handle FirFunctionCall by returning FirCallableElementInferenceNode "
        "with callable.fir as the element. This ensures proper scheme caching."
    )


def test_fallback_returns_expression():
    """
    Verify the fallback case returns expression (not callable.fir).

    The fallback should use expression as element when it's not safe to share schemes.
    """
    content = TARGET_FILE.read_text()

    # Find the last return in callableInferenceNodeOf
    # It should return FirCallableElementInferenceNode(callable, expression)
    # This is the safe fallback when we can't determine sharing is safe
    func_match = re.search(
        r'@OptIn\(SymbolInternals::class\)\s*private fun callableInferenceNodeOf\([^)]+\): FirInferenceNode \{([^}]+(?:\{[^}]*\}[^}]*)*return FirCallableElementInferenceNode\(callable, expression\)',
        content,
        re.DOTALL
    )

    # Check that there's a comment explaining the fallback and it returns expression
    assert func_match, (
        "Fallback must return FirCallableElementInferenceNode(callable, expression) "
        "with comment explaining that it is not safe to share schemes"
    )

    func_body = func_match.group(1)
    assert "not safe" in func_body or "not safe" in content[func_match.start():func_match.end()], (
        "Fallback case must have explanatory comment about scheme safety"
    )


def test_no_elvis_operator_chain():
    """
    Verify the old Elvis operator chain pattern is removed.

    The fix replaces the old pattern with explicit control flow.
    """
    content = TARGET_FILE.read_text()

    # Old pattern: parameterInferenceNodeOrNull(expression, context) ?: ... ?:
    old_pattern = r'parameterInferenceNodeOrNull\(expression, context\) \?:'
    assert not re.search(old_pattern, content), (
        "Must not use the old Elvis operator chain pattern. "
        "Use explicit control flow with if/return instead."
    )


def test_fir_callable_element_has_kind_override():
    """
    Verify FirCallableElementInferenceNode has explicit kind override.
    """
    content = TARGET_FILE.read_text()

    # Find the class and verify it has kind override
    class_start = content.find('private class FirCallableElementInferenceNode')
    assert class_start != -1, "FirCallableElementInferenceNode class not found"

    # Find the end of the class (next private/open/public class or end of file)
    next_class = re.search(r'\n(?:private|open|public|abstract) class|@OptIn', content[class_start + 1:])
    if next_class:
        class_end = class_start + 1 + next_class.start()
        class_content = content[class_start:class_end]
    else:
        class_content = content[class_start:]

    assert 'override val kind' in class_content, (
        "FirCallableElementInferenceNode must override the kind property"
    )
