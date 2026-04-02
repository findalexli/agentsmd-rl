"""
Task: prime-rl-sft-hybrid-cp-model-ordering
Repo: PrimeIntellect-ai/prime-rl @ b7afd84024531074830143d88bf0f60f506e1588
PR:   2097

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import sys
from pathlib import Path
from unittest.mock import MagicMock

FILE = Path("/workspace/src/prime_rl/trainer/sft/train.py")


def _parse_train_func():
    """Parse train.py and return (source, AST node for train())."""
    source = FILE.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "train":
            return source, node
    raise AssertionError("train() function not found in train.py")


def _find_calls(node, name):
    """Find all Call nodes in an AST subtree matching a function name."""
    results = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            func_name = getattr(child.func, "id", None) or getattr(child.func, "attr", None)
            if func_name == name:
                results.append(child)
    return results


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """train.py must be valid Python."""
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    source = FILE.read_text()
    compile(source, str(FILE), "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_nameerror_on_model():
    """Mock-execute train() — setup_hybrid_cp must not trigger NameError on 'model'.

    The base-commit bug: setup_hybrid_cp(model, ...) runs before model = setup_model(),
    causing a NameError. The fix reorders so model is assigned first.
    """

    class _FallbackFinder:
        @staticmethod
        def find_module(name, path=None):
            return _FallbackFinder

        @staticmethod
        def load_module(name):
            if name not in sys.modules:
                m = MagicMock()
                m.__name__ = name
                m.__path__ = [name]
                m.__file__ = "<mock:" + name + ">"
                m.__loader__ = _FallbackFinder
                m.__package__ = name.rsplit(".", 1)[0] if "." in name else name
                sys.modules[name] = m
            return sys.modules[name]

    original_meta = sys.meta_path[:]
    sys.meta_path.append(_FallbackFinder)
    old_path = sys.path[:]
    sys.path.insert(0, "/workspace/src")
    try:
        source = FILE.read_text()
        ns = {"__builtins__": __builtins__, "__name__": "__test__", "__file__": str(FILE)}
        try:
            exec(compile(source, str(FILE), "exec"), ns)
        except Exception:
            pass

        # Fallback: extract train() via AST if whole-module exec didn't define it
        if "train" not in ns or not callable(ns.get("train")):
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == "train":
                    lines = source.splitlines(keepends=True)
                    func_src = "".join(lines[node.lineno - 1 : node.end_lineno])
                    try:
                        exec(compile(func_src, str(FILE), "exec"), ns)
                    except Exception:
                        pass
                    break

        train_fn = ns.get("train")
        assert train_fn is not None and callable(train_fn), "Could not extract train()"

        config = MagicMock()
        try:
            train_fn(config)
        except NameError as e:
            if "model" in str(e).lower():
                raise AssertionError(
                    f"NameError on 'model' — setup_hybrid_cp called before model assignment: {e}"
                )
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception:
            pass  # Other errors expected with mocked deps
    finally:
        sys.meta_path[:] = original_meta
        sys.path[:] = old_path


# [pr_diff] fail_to_pass
def test_hybrid_cp_after_model_init():
    """setup_hybrid_cp() must be called AFTER setup_model() in train().

    AST ordering check: the line number of setup_hybrid_cp must be greater
    than the line number of setup_model. Tests multiple orderings to ensure
    the fix isn't fragile.
    """
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    _, train_node = _parse_train_func()

    setup_model_calls = _find_calls(train_node, "setup_model")
    setup_hybrid_cp_calls = _find_calls(train_node, "setup_hybrid_cp")

    assert setup_model_calls, "setup_model() call not found in train()"
    assert setup_hybrid_cp_calls, "setup_hybrid_cp() call not found in train()"

    sm_line = setup_model_calls[0].lineno
    shcp_line = setup_hybrid_cp_calls[0].lineno

    assert shcp_line > sm_line, (
        f"setup_hybrid_cp (line {shcp_line}) must come after "
        f"setup_model (line {sm_line}) in train()"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_setup_hybrid_cp_retained():
    """setup_hybrid_cp call must still exist — not deleted to dodge NameError."""
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    _, train_node = _parse_train_func()
    calls = _find_calls(train_node, "setup_hybrid_cp")
    assert calls, "setup_hybrid_cp() call was removed from train()"


# [pr_diff] pass_to_pass
def test_substitute_ring_attn_present():
    """substitute_ring_attn must still be called (regression guard)."""
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    source = FILE.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name == "substitute_ring_attn":
                return
    raise AssertionError("substitute_ring_attn() call was removed")


# [pr_diff] pass_to_pass
def test_setup_model_present():
    """setup_model must still be called."""
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    _, train_node = _parse_train_func()
    calls = _find_calls(train_node, "setup_model")
    assert calls, "setup_model() call was removed from train()"


# [static] pass_to_pass
def test_train_not_stub():
    """train() must have >= 20 top-level statements (reject total rewrites)."""
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    _, train_node = _parse_train_func()
    assert len(train_node.body) >= 20, (
        f"train() has only {len(train_node.body)} statements — likely a stub"
    )


# [pr_diff] pass_to_pass
def test_setup_ckpt_managers_retained():
    """setup_ckpt_managers must still be called (reject gutted rewrites)."""
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    source = FILE.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name == "setup_ckpt_managers":
                return
    raise AssertionError("setup_ckpt_managers() call was removed")


# [pr_diff] pass_to_pass
def test_hybrid_cp_guarded_by_cp_enabled():
    """setup_hybrid_cp must be inside a cp_enabled conditional (not called unconditionally)."""
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    _, train_node = _parse_train_func()

    # Walk the train function to find setup_hybrid_cp calls
    # and verify each is inside an If node that tests cp_enabled
    for node in ast.walk(train_node):
        if isinstance(node, ast.If):
            # Check if this If tests cp_enabled (attribute or name)
            test_src = ast.dump(node.test)
            if "cp_enabled" in test_src:
                # Check if setup_hybrid_cp is called inside this If body
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        name = getattr(child.func, "id", None) or getattr(child.func, "attr", None)
                        if name == "setup_hybrid_cp":
                            return
    raise AssertionError(
        "setup_hybrid_cp() is not guarded by a cp_enabled check — "
        "it must only run when context parallelism is enabled"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:5 @ b7afd84024531074830143d88bf0f60f506e1588
def test_no_try_except_around_hybrid_cp():
    """setup_hybrid_cp must not be wrapped in try/except (AGENTS.md: avoid unnecessary try/except)."""
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    source = FILE.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    name = getattr(child.func, "id", None) or getattr(child.func, "attr", None)
                    if name == "setup_hybrid_cp":
                        raise AssertionError(
                            "setup_hybrid_cp is inside a try/except block — "
                            "AGENTS.md says avoid unnecessary try/except"
                        )
