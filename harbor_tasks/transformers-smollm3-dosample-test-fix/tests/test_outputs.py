"""
Task: transformers-smollm3-dosample-test-fix
Repo: huggingface/transformers @ 9cd278715c5154597a44110d6e0c114a7e90d6f5
PR:   45048

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: Integration tests require a 3B model + GPU to actually run generate().
AST-based checks are justified here because we cannot call the code under test.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/transformers"
TARGET = Path(REPO) / "tests/models/smollm3/test_modeling_smollm3.py"

# The two methods modified by the fix (PR #45048)
AFFECTED_METHODS = {"test_model_3b_generation", "test_model_3b_long_prompt"}


def _parse_target():
    return ast.parse(TARGET.read_text())


def _find_integration_class(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "SmolLM3IntegrationTest":
            return node
    return None


def _find_affected_methods(cls_node):
    """Return FunctionDef nodes for the methods modified by the PR."""
    return [
        item for item in cls_node.body
        if isinstance(item, ast.FunctionDef) and item.name in AFFECTED_METHODS
    ]


def _find_generate_calls(node):
    """Find all .generate() calls within an AST node."""
    calls = []
    for child in ast.walk(node):
        if (
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and child.func.attr == "generate"
        ):
            calls.append(child)
    return calls


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax():
    """Target test file must parse without errors."""
    tree = _parse_target()
    assert tree is not None


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dosample_false_in_generate():
    """All generate() calls in the affected test methods must use do_sample=False.

    The model's generation_config.json has do_sample=True by default.
    Without explicit do_sample=False, greedy decoding is not guaranteed.
    # AST-only because: model.generate() requires GPU + 3B model weights
    """
    tree = _parse_target()
    cls = _find_integration_class(tree)
    assert cls is not None, "SmolLM3IntegrationTest class not found"

    methods = _find_affected_methods(cls)
    assert len(methods) == 2, f"Expected 2 affected methods, found {len(methods)}"

    all_calls = []
    for method in methods:
        calls = _find_generate_calls(method)
        assert len(calls) >= 1, f"{method.name} has no generate() calls"
        all_calls.extend(calls)

    assert len(all_calls) >= 3, f"Expected >=3 generate() calls, found {len(all_calls)}"

    for call in all_calls:
        kw_map = {kw.arg: kw for kw in call.keywords if kw.arg is not None}
        assert "do_sample" in kw_map, (
            f"generate() at line {call.lineno} missing do_sample keyword"
        )
        val = kw_map["do_sample"].value
        assert isinstance(val, ast.Constant) and val.value is False, (
            f"generate() at line {call.lineno}: do_sample must be literal False"
        )


# [pr_diff] fail_to_pass
def test_no_temperature_in_generate():
    """generate() calls in affected methods must not use temperature kwarg.

    temperature=0 does NOT override do_sample=True from generation_config,
    so the fix must remove temperature and use do_sample=False instead.
    # AST-only because: model.generate() requires GPU + 3B model weights
    """
    tree = _parse_target()
    cls = _find_integration_class(tree)
    assert cls is not None, "SmolLM3IntegrationTest class not found"

    for method in _find_affected_methods(cls):
        for call in _find_generate_calls(method):
            kw_names = {kw.arg for kw in call.keywords if kw.arg is not None}
            assert "temperature" not in kw_names, (
                f"generate() at line {call.lineno} in {method.name} still uses temperature kwarg"
            )


# [pr_diff] fail_to_pass
def test_expected_text_updated():
    """Old buggy expected text in test_model_3b_generation must be replaced.

    The old EXPECTED_TEXT_COMPLETION was generated with temperature=0 + do_sample=True
    (non-deterministic). True greedy decoding produces different text.
    # AST-only because: verifying string constant in test code, cannot run generation
    """
    tree = _parse_target()
    cls = _find_integration_class(tree)
    assert cls is not None

    # Find the test_model_3b_generation method and extract its source span
    gen_method = None
    for item in cls.body:
        if isinstance(item, ast.FunctionDef) and item.name == "test_model_3b_generation":
            gen_method = item
            break
    assert gen_method is not None, "test_model_3b_generation method not found"

    # Get the source lines for just this method
    src_lines = TARGET.read_text().splitlines()
    method_src = "\n".join(src_lines[gen_method.lineno - 1:gen_method.end_lineno])

    old_fragment = "pulls objects toward the center of the Earth"
    assert old_fragment not in method_src, (
        f"Old expected text still present in test_model_3b_generation: '{old_fragment}'"
    )

    # Must still have an expected text assertion
    has_assertion = False
    for item in ast.walk(gen_method):
        if isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute):
            if item.func.attr in ("assertEqual", "assertIn", "assertTrue"):
                has_assertion = True
                break
    assert has_assertion, "No assertions found in test_model_3b_generation"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_class_structure_preserved():
    """All original test classes and integration test methods must still exist.
    # AST-only because: verifying class/method presence, not behavior
    """
    tree = _parse_target()

    required_classes = {"SmolLM3IntegrationTest", "SmolLM3ModelTest", "SmolLM3ModelTester"}
    required_methods = {"test_model_3b_generation", "test_model_3b_long_prompt", "test_model_3b_logits"}

    found_classes = set()
    found_methods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            found_classes.add(node.name)
            if node.name == "SmolLM3IntegrationTest":
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        found_methods.add(item.name)

    missing_classes = required_classes - found_classes
    assert not missing_classes, f"Missing classes: {missing_classes}"

    missing_methods = required_methods - found_methods
    assert not missing_methods, f"Missing methods: {missing_methods}"


# [static] pass_to_pass
def test_not_stub():
    """Integration test methods must have real bodies (not stubbed out).
    # AST-only because: checking code structure, not running it
    """
    src = TARGET.read_text()
    assert len(src.splitlines()) >= 100, "File too short, likely stubbed"

    tree = ast.parse(src)
    cls = _find_integration_class(tree)
    assert cls is not None

    for item in cls.body:
        if isinstance(item, ast.FunctionDef) and item.name.startswith("test_model_3b"):
            meaningful = 0
            for stmt in ast.walk(item):
                if isinstance(stmt, (ast.Assign, ast.AugAssign, ast.Return, ast.Assert)):
                    meaningful += 1
                elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                    meaningful += 1  # method calls like self.assertEqual()
            assert meaningful >= 3, (
                f"{item.name} has only {meaningful} meaningful statements, likely stubbed"
            )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:16 @ 9cd278715c
def test_no_new_test_files():
    """Tests must be added to existing files, not new ones.

    From .github/copilot-instructions.md line 16:
    'When writing tests, they should be added to an existing file.'
    """
    r = subprocess.run(
        ["git", "diff", "--name-status", "HEAD"],
        cwd=REPO, capture_output=True, text=True,
    )
    diff_output = r.stdout.strip()
    if not diff_output:
        # No unstaged changes; check last commit
        r = subprocess.run(
            ["git", "diff", "--name-status", "HEAD~1", "HEAD"],
            cwd=REPO, capture_output=True, text=True,
        )
        diff_output = r.stdout.strip()

    for line in diff_output.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0] == "A" and "test" in parts[1].lower():
            raise AssertionError(f"New test file created: {parts[1]}")


# [agent_config] pass_to_pass — .github/copilot-instructions.md:17 @ 9cd278715c
def test_code_style():
    """Modified test file must pass ruff linting.

    From .github/copilot-instructions.md line 17:
    'Code style is enforced in CI. [...] Run make fixup to apply style/consistency fixes.'
    """
    r = subprocess.run(
        ["ruff", "check", str(TARGET), "--no-fix"],
        cwd=REPO, capture_output=True, text=True,
    )
    assert r.returncode == 0, f"ruff lint failures:\n{r.stdout}\n{r.stderr}"
