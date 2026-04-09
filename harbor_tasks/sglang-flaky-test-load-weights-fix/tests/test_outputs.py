"""
Task: sglang-flaky-test-load-weights-fix
Repo: sglang @ df9c831ab80c78495142b4dbcb1dfa537c9e1c73
PR:   22150

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This is a GPU-dependent test, so we verify the fix via AST parsing:
1. The remote_instance_weight_loader_start_seed_via_transfer_engine parameter
   is now hardcoded to False (not conditional on backend)
2. The FIXME comment about random behavior refactoring is added
"""

import ast
from pathlib import Path

REPO = "/workspace/sglang"
TEST_FILE = "test/registered/distributed/test_load_weights_from_remote_instance.py"


def get_test_file_content():
    """Read the test file content."""
    path = Path(f"{REPO}/{TEST_FILE}")
    if not path.exists():
        raise FileNotFoundError(f"Test file not found: {path}")
    return path.read_text()


def parse_test_file():
    """Parse the test file and return AST."""
    content = get_test_file_content()
    return ast.parse(content)


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Test file must parse without errors."""
    content = get_test_file_content()
    tree = ast.parse(content)
    assert tree is not None, "Failed to parse test file"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_transfer_engine_flag_hardcoded_false():
    """remote_instance_weight_loader_start_seed_via_transfer_engine must be hardcoded to False.

    Before: remote_instance_weight_loader_start_seed_via_transfer_engine=(
                remote_instance_loader_backend == "transfer_engine"
            )
    After:  remote_instance_weight_loader_start_seed_via_transfer_engine=False
    """
    tree = parse_test_file()

    found_engine_init = False
    found_hardcoded_false = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check if this is an sgl.Engine call
            func_name = None
            if isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            elif isinstance(node.func, ast.Name):
                func_name = node.func.id

            if func_name == "Engine" or func_name == "sgl" or (
                isinstance(node.func, ast.Attribute) and
                isinstance(node.func.value, ast.Name) and
                node.func.value.id == "sgl" and
                node.func.attr == "Engine"
            ):
                found_engine_init = True

                # Check for the remote_instance_weight_loader_start_seed_via_transfer_engine keyword
                for kw in node.keywords:
                    if kw.arg == "remote_instance_weight_loader_start_seed_via_transfer_engine":
                        # Check if it's a constant False
                        if isinstance(kw.value, ast.Constant) and kw.value.value is False:
                            found_hardcoded_false = True
                        else:
                            raise AssertionError(
                                "remote_instance_weight_loader_start_seed_via_transfer_engine is not hardcoded False"
                            )

    assert found_engine_init, "Could not find sgl.Engine() call in the test file"
    assert found_hardcoded_false, (
        "remote_instance_weight_loader_start_seed_via_transfer_engine is not hardcoded to False. "
        "The fix should set it to False unconditionally, not conditional on backend type."
    )


# [pr_diff] fail_to_pass
def test_fixme_comment_added():
    """FIXME comment about random behavior must be added before the random.choice calls.

    Before: no FIXME comment
    After:  # FIXME: refactor this test to have less random behavior
    """
    content = get_test_file_content()

    # Check for the FIXME comment
    assert "# FIXME: refactor this test to have less random behavior" in content, (
        "FIXME comment about random behavior is missing. "
        "The fix should add a comment indicating the test needs refactoring."
    )


# [pr_diff] fail_to_pass
def test_no_conditional_transfer_engine_expression():
    """The conditional expression checking backend == 'transfer_engine' must be removed.

    Before: remote_instance_weight_loader_backend == "transfer_engine"
            was used as the value for remote_instance_weight_loader_start_seed_via_transfer_engine
    After:  hardcoded False
    """
    content = get_test_file_content()
    tree = ast.parse(content)

    # Find the init_process_dst function
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "init_process_dst":
            # Check that there's no Compare node checking for "transfer_engine"
            for child in ast.walk(node):
                if isinstance(child, ast.Compare):
                    # Check if comparing against the string "transfer_engine"
                    if any(isinstance(comp, ast.Constant) and
                           comp.value == "transfer_engine"
                           for comp in child.comparators):
                        # This is OK if it's in the comment or elsewhere,
                        # but we should verify it's not in the Engine() call
                        pass

    # More specific check: look at the sgl.Engine call specifically
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = None
            if isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            elif isinstance(node.func, ast.Name):
                func_name = node.func.id

            if func_name == "Engine":
                for kw in node.keywords:
                    if kw.arg == "remote_instance_weight_loader_start_seed_via_transfer_engine":
                        # Must be a constant, not a Compare expression
                        if isinstance(kw.value, ast.Compare):
                            raise AssertionError(
                                "Found conditional expression for "
                                "remote_instance_weight_loader_start_seed_via_transfer_engine. "
                                "It should be hardcoded to False."
                            )


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_structure_intact():
    """The test file should still have the expected structure."""
    tree = parse_test_file()

    # Check for key imports
    import_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            import_names.add(node.module)

    # Key imports should exist
    assert "sglang" in import_names or "sgl" in str(tree), "sglang import missing"
    assert "torch" in import_names or "torch" in str(tree), "torch import missing"

    # Check for key functions
    func_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    assert "init_process_dst" in func_names, "init_process_dst function missing"
    assert "test_load_weights_from_remote_instance" in func_names, "Test function missing"


# [static] pass_to_pass
def test_not_stub():
    """The fix is not a stub - it has real logic changes."""
    content = get_test_file_content()

    # The fix should contain hardcoded False for the parameter
    assert "remote_instance_weight_loader_start_seed_via_transfer_engine=False" in content, (
        "The fix must hardcode False for remote_instance_weight_loader_start_seed_via_transfer_engine"
    )

    # Should NOT contain the old conditional pattern
    old_pattern = 'remote_instance_loader_backend == "transfer_engine"'
    assert old_pattern not in content, (
        f"The old conditional pattern '{old_pattern}' should be removed"
    )
