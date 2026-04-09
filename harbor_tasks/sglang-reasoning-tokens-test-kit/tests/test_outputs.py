"""
Task: sglang-reasoning-tokens-test-kit
Repo: sglang @ bb9e058f5b9d4754ac2965bb36864fee1cd978e8
PR:   22102

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/sglang"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_reasoning_tokens_kit_syntax():
    """New reasoning_tokens_kit.py must be valid Python."""
    kit_path = Path(f"{REPO}/python/sglang/test/kits/reasoning_tokens_kit.py")
    if not kit_path.exists():
        # This is expected to fail on base commit (file doesn't exist)
        assert False, "reasoning_tokens_kit.py does not exist"

    src = kit_path.read_text()
    try:
        ast.parse(src)
    except SyntaxError as e:
        assert False, f"Syntax error in reasoning_tokens_kit.py: {e}"


def test_modified_files_syntax():
    """Modified test files must parse without errors."""
    files = [
        f"{REPO}/test/registered/openai_server/features/test_enable_thinking.py",
        f"{REPO}/test/registered/4-gpu-models/test_qwen35_models.py",
    ]
    for path_str in files:
        path = Path(path_str)
        if not path.exists():
            continue
        src = path.read_text()
        try:
            ast.parse(src)
        except SyntaxError as e:
            assert False, f"Syntax error in {path.name}: {e}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core structural tests
# ---------------------------------------------------------------------------

def test_reasoning_tokens_kit_exists():
    """The reasoning_tokens_kit.py file must exist with ReasoningTokenUsageMixin."""
    kit_path = Path(f"{REPO}/python/sglang/test/kits/reasoning_tokens_kit.py")
    assert kit_path.exists(), "reasoning_tokens_kit.py does not exist"

    src = kit_path.read_text()
    tree = ast.parse(src)

    # Find the ReasoningTokenUsageMixin class
    mixin_found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ReasoningTokenUsageMixin":
            mixin_found = True
            break

    assert mixin_found, "ReasoningTokenUsageMixin class not found in kit"


def test_mixin_has_required_methods():
    """ReasoningTokenUsageMixin must have the 5 test methods."""
    kit_path = Path(f"{REPO}/python/sglang/test/kits/reasoning_tokens_kit.py")
    assert kit_path.exists(), "reasoning_tokens_kit.py does not exist"

    src = kit_path.read_text()
    tree = ast.parse(src)

    required_methods = [
        "test_reasoning_tokens_thinking",
        "test_reasoning_tokens_non_thinking",
        "test_reasoning_tokens_thinking_stream",
        "test_reasoning_tokens_non_thinking_stream",
        "test_reasoning_tokens_generate_exact_count",
    ]

    found_methods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ReasoningTokenUsageMixin":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name in required_methods:
                    found_methods.add(item.name)

    missing = set(required_methods) - found_methods
    assert not missing, f"Missing methods in mixin: {missing}"


def test_mixin_has_init_reasoning_token_verifier():
    """Mixin must have init_reasoning_token_verifier classmethod."""
    kit_path = Path(f"{REPO}/python/sglang/test/kits/reasoning_tokens_kit.py")
    assert kit_path.exists(), "reasoning_tokens_kit.py does not exist"

    src = kit_path.read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ReasoningTokenUsageMixin":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "init_reasoning_token_verifier":
                    # Check it's a classmethod
                    for d in item.decorator_list:
                        if isinstance(d, ast.Name) and d.id == "classmethod":
                            return
                        elif isinstance(d, ast.Attribute) and d.attr == "classmethod":
                            return

    assert False, "init_reasoning_token_verifier classmethod not found in mixin"


def test_enable_thinking_imports_mixin():
    """TestEnableThinking must import and use ReasoningTokenUsageMixin."""
    test_path = Path(f"{REPO}/test/registered/openai_server/features/test_enable_thinking.py")
    assert test_path.exists(), "test_enable_thinking.py does not exist"

    src = test_path.read_text()

    # Check for import
    assert "from sglang.test.kits.reasoning_tokens_kit import ReasoningTokenUsageMixin" in src, \
        "ReasoningTokenUsageMixin import not found in test_enable_thinking.py"

    # Check TestEnableThinking inherits from the mixin
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestEnableThinking":
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
            assert "ReasoningTokenUsageMixin" in bases, \
                "TestEnableThinking does not inherit from ReasoningTokenUsageMixin"
            return

    assert False, "TestEnableThinking class not found"


def test_enable_thinking_sets_reasoning_parser():
    """TestEnableThinking must set reasoning_parser_name attribute."""
    test_path = Path(f"{REPO}/test/registered/openai_server/features/test_enable_thinking.py")
    assert test_path.exists(), "test_enable_thinking.py does not exist"

    src = test_path.read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestEnableThinking":
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == "reasoning_parser_name":
                            # Check it's set to "qwen3"
                            if isinstance(item.value, ast.Constant) and item.value.value == "qwen3":
                                return

    assert False, "reasoning_parser_name = 'qwen3' not found in TestEnableThinking"


def test_qwen35_mtp_imports_mixin():
    """TestQwen35FP4MTP must import and use ReasoningTokenUsageMixin."""
    test_path = Path(f"{REPO}/test/registered/4-gpu-models/test_qwen35_models.py")
    assert test_path.exists(), "test_qwen35_models.py does not exist"

    src = test_path.read_text()

    # Check for import
    assert "from sglang.test.kits.reasoning_tokens_kit import ReasoningTokenUsageMixin" in src, \
        "ReasoningTokenUsageMixin import not found in test_qwen35_models.py"

    # Check TestQwen35FP4MTP inherits from the mixin
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestQwen35FP4MTP":
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
            assert "ReasoningTokenUsageMixin" in bases, \
                "TestQwen35FP4MTP does not inherit from ReasoningTokenUsageMixin"
            return

    assert False, "TestQwen35FP4MTP class not found"


def test_qwen35_mtpv2_imports_mixin():
    """TestQwen35FP4MTPV2 must import and use ReasoningTokenUsageMixin."""
    test_path = Path(f"{REPO}/test/registered/4-gpu-models/test_qwen35_models.py")
    assert test_path.exists(), "test_qwen35_models.py does not exist"

    src = test_path.read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestQwen35FP4MTPV2":
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
            assert "ReasoningTokenUsageMixin" in bases, \
                "TestQwen35FP4MTPV2 does not inherit from ReasoningTokenUsageMixin"
            return

    assert False, "TestQwen35FP4MTPV2 class not found"


def test_qwen35_fp4_uses_custom_test_case():
    """TestQwen35FP4 must use CustomTestCase instead of unittest.TestCase."""
    test_path = Path(f"{REPO}/test/registered/4-gpu-models/test_qwen35_models.py")
    assert test_path.exists(), "test_qwen35_models.py does not exist"

    src = test_path.read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestQwen35FP4":
            bases = []
            for b in node.bases:
                if isinstance(b, ast.Name):
                    bases.append(b.id)
                elif isinstance(b, ast.Attribute):
                    bases.append(f"{b.value.id}.{b.attr}")

            assert "unittest.TestCase" not in bases, \
                "TestQwen35FP4 still inherits from unittest.TestCase"
            assert "CustomTestCase" in bases, \
                "TestQwen35FP4 does not inherit from CustomTestCase"
            return

    assert False, "TestQwen35FP4 class not found"


def test_old_reasoning_usage_tokens_deleted():
    """The old standalone test_reasoning_usage_tokens.py must be deleted."""
    old_test_path = Path(
        f"{REPO}/test/registered/openai_server/features/test_reasoning_usage_tokens.py"
    )
    assert not old_test_path.exists(), \
        "Old test_reasoning_usage_tokens.py should be deleted but still exists"


def test_enable_thinking_calls_init_verifier():
    """TestEnableThinking setUpClass must call init_reasoning_token_verifier."""
    test_path = Path(f"{REPO}/test/registered/openai_server/features/test_enable_thinking.py")
    assert test_path.exists(), "test_enable_thinking.py does not exist"

    src = test_path.read_text()

    # Check for the call to init_reasoning_token_verifier in setUpClass
    assert "cls.init_reasoning_token_verifier()" in src, \
        "init_reasoning_token_verifier() call not found in TestEnableThinking"


def test_qwen35_mtp_calls_init_verifier():
    """TestQwen35FP4MTP setUpClass must call init_reasoning_token_verifier."""
    test_path = Path(f"{REPO}/test/registered/4-gpu-models/test_qwen35_models.py")
    assert test_path.exists(), "test_qwen35_models.py does not exist"

    src = test_path.read_text()

    # Check that TestQwen35FP4MTP has the init call by looking for the pattern in source
    assert "cls.init_reasoning_token_verifier()" in src, \
        "init_reasoning_token_verifier() not called in TestQwen35FP4MTP.setUpClass"
