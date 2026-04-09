"""Tests for Kotlin Compose compiler inline lambda groups fix.

This tests that the Compose compiler plugin correctly adds groups to inline
functions with two or more inline parameters. This preserves structure in
the argument body when inline functions hide control flow.
"""

import subprocess
import sys
import os

REPO = "/workspace/kotlin"
TRANSFORMER_FILE = "plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableFunctionBodyTransformer.kt"


def get_transformer_content():
    """Get the content of the transformer file."""
    with open(os.path.join(REPO, TRANSFORMER_FILE), 'r') as f:
        return f.read()


def test_visit_inlined_lambda_function_exists():
    """New visitInlinedLambdaInComposableScope function exists (fail_to_pass)."""
    content = get_transformer_content()

    # Check for the new function that wraps inline lambda bodies with groups
    assert "private fun visitInlinedLambdaInComposableScope(declaration: IrFunction): IrStatement" in content, \
        "visitInlinedLambdaInComposableScope function declaration not found"

    # Also check it has the forceInlinedLambdaGroup logic
    assert "parentScope.forceInlinedLambdaGroup" in content, \
        "forceInlinedLambdaGroup check not found in visitInlinedLambdaInComposableScope"


def test_force_inlined_lambda_group_field():
    """forceInlinedLambdaGroup field exists in CaptureScope (fail_to_pass)."""
    content = get_transformer_content()

    # Check for the field declaration in CaptureScope
    assert "var forceInlinedLambdaGroup = false" in content, \
        "forceInlinedLambdaGroup field declaration not found in CaptureScope"


def test_inline_lambda_count_logic():
    """Logic to count inline lambdas and force groups exists (fail_to_pass)."""
    content = get_transformer_content()

    # Check for the comment explaining the fix
    assert "non-composable call with multiple inline lambdas" in content, \
        "Comment explaining the fix not found"

    # Check for the inline lambda counting - exact variable
    assert "val inlineLambdaCount = owner.parameters.count { it.isInlineParameter() }" in content, \
        "inlineLambdaCount variable not found"

    # Check for the assignment
    assert "captureScope.forceInlinedLambdaGroup = inlineLambdaCount > 1" in content, \
        "forceInlinedLambdaGroup assignment not found"


def test_leaving_inlined_lambda_renamed():
    """leavingInlinedLambda renamed to leavingInlinedComposableLambda (fail_to_pass)."""
    content = get_transformer_content()

    # New variable name should exist
    assert "var leavingInlinedComposableLambda = false" in content, \
        "leavingInlinedComposableLambda variable declaration not found"


def test_rollback_group_condition_fixed():
    """Rollback group condition order is fixed (fail_to_pass)."""
    content = get_transformer_content()

    # The fixed condition checks rollbackGroupMarkerEnabled first
    # This is the critical fix for early return handling
    assert "if (!rollbackGroupMarkerEnabled || !leavingInlinedComposableLambda)" in content, \
        "Fixed rollback group condition not found"


def test_block_scope_marks_adds_inlined_lambda():
    """Block scope marks now add inlined lambda scopes (fail_to_pass)."""
    content = get_transformer_content()

    # Look for the specific pattern in markReturnWithLabel function
    # The fix adds blockScopeMarks.add(scope) for isInlinedLambda
    # followed by checking inComposableCall
    lines = content.split('\n')
    found_pattern = False

    for i, line in enumerate(lines):
        if "if (scope.isInlinedLambda)" in line:
            # Check following lines for the pattern
            for j in range(i + 1, min(i + 5, len(lines))):
                if "blockScopeMarks.add(scope)" in lines[j]:
                    # Continue checking for nested inComposableCall check
                    for k in range(j + 1, min(j + 5, len(lines))):
                        if "if (scope.inComposableCall)" in lines[k]:
                            found_pattern = True
                            break
                if found_pattern:
                    break
        if found_pattern:
            break

    assert found_pattern, "blockScopeMarks.add(scope) pattern for inlined lambda not found"


def test_has_captured_call_check_updated():
    """Captured composable call check updated to consider forceInlinedLambdaGroup (fail_to_pass)."""
    content = get_transformer_content()

    # The condition should now check both hasCapturedComposableCall and forceInlinedLambdaGroup
    assert "if (captureScope.hasCapturedComposableCall && !captureScope.forceInlinedLambdaGroup)" in content, \
        "Updated capture scope condition not found"

    # Check for the related comment about the outer group
    assert "the outer group around the call is only required when the inline function body is not" in content, \
        "Comment about outer group not found"


def test_visit_function_in_scope_updated():
    """visitFunctionInScope updated to handle non-composable inlined lambdas (fail_to_pass)."""
    content = get_transformer_content()

    # Check that visitFunctionInScope now calls visitInlinedLambdaInComposableScope
    assert "return visitInlinedLambdaInComposableScope(declaration)" in content, \
        "visitInlinedLambdaInComposableScope call not found in visitFunctionInScope"


def test_compose_compiler_tests_exist():
    """Repo tests exist and are discoverable (pass_to_pass)."""
    # Verify the test directories exist
    test_dirs = [
        "plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin",
        "plugins/compose/compiler-hosted/runtime-tests/src/commonTest/kotlin/androidx/compose/compiler/test"
    ]

    for test_dir in test_dirs:
        full_path = os.path.join(REPO, test_dir)
        assert os.path.exists(full_path), f"Test directory not found: {test_dir}"


def test_transformer_file_structure():
    """Transformer file has expected structure with visitFunctionInScope (pass_to_pass)."""
    content = get_transformer_content()

    # Basic structure checks
    assert "private fun visitFunctionInScope(declaration: IrFunction)" in content, \
        "visitFunctionInScope function not found"

    assert "class ComposableFunctionBodyTransformer" in content, \
        "ComposableFunctionBodyTransformer class not found"


def test_repo_git_integrity():
    """Git repository is intact and at expected base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git status failed:\n{r.stderr}"

    # Check HEAD is at a valid commit
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git rev-parse failed:\n{r.stderr}"
    head_commit = r.stdout.strip()
    assert len(head_commit) == 40, f"Invalid commit hash: {head_commit}"


def test_compose_compiler_testdata_exists():
    """Compose compiler test data files exist (pass_to_pass)."""
    testdata_dirs = [
        "plugins/compose/compiler-hosted/testData/codegen",
        "plugins/compose/compiler-hosted/testData/diagnostics",
    ]

    for testdata_dir in testdata_dirs:
        full_path = os.path.join(REPO, testdata_dir)
        assert os.path.exists(full_path), f"Test data directory not found: {testdata_dir}"
        # Check there are files in the directory
        files = os.listdir(full_path)
        assert len(files) > 0, f"Test data directory is empty: {testdata_dir}"


def test_key_compose_source_files_exist():
    """Key Compose compiler source files exist and are non-empty (pass_to_pass)."""
    key_files = [
        "plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableFunctionBodyTransformer.kt",
        "plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/AbstractComposeLowering.kt",
        "plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposerParamTransformer.kt",
    ]

    for filepath in key_files:
        full_path = os.path.join(REPO, filepath)
        assert os.path.exists(full_path), f"Key source file not found: {filepath}"
        assert os.path.getsize(full_path) > 0, f"Key source file is empty: {filepath}"


def test_compose_compiler_build_files_exist():
    """Compose compiler build configuration files exist (pass_to_pass)."""
    build_files = [
        "plugins/compose/compiler-hosted/build.gradle.kts",
        "plugins/compose/compiler-hosted/integration-tests/build.gradle.kts",
        "plugins/compose/build.gradle.kts",
    ]

    for filepath in build_files:
        full_path = os.path.join(REPO, filepath)
        assert os.path.exists(full_path), f"Build file not found: {filepath}"


def test_kotlin_test_files_exist():
    """Kotlin test source files exist and are non-empty (pass_to_pass)."""
    test_files = [
        "plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/AbstractIrTransformTest.kt",
        "plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/ComposeBytecodeCodegenTest.kt",
        "plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/ClassStabilityTransformTests.kt",
    ]

    for filepath in test_files:
        full_path = os.path.join(REPO, filepath)
        assert os.path.exists(full_path), f"Test file not found: {filepath}"
        assert os.path.getsize(full_path) > 0, f"Test file is empty: {filepath}"
