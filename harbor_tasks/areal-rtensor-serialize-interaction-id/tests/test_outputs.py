"""
Task: areal-rtensor-serialize-interaction-id
Repo: inclusionAI/AReaL @ 3bf10c9c56eeae846b3de52dde8db42918f80690
PR:   #1067

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

REPO = "/repos/AReaL"
sys.path.insert(0, REPO)

# ---------------------------------------------------------------------------
# Pre-mock heavy transitive deps before importing any areal modules.
# types.py does `from areal.api import ModelResponse` which triggers
# areal.api.__getattr__ → areal.api.io_struct → transformers (not installed).
# ModelResponse is only used as a type annotation (with `from __future__ import
# annotations`), so a MagicMock is safe.
# ---------------------------------------------------------------------------
for _mod in [
    "areal.api",
    "areal.api.io_struct",
    "areal.api.cli_args",
    "areal.api.alloc_mode",
    "areal.infra.platforms",
]:
    sys.modules.setdefault(_mod, MagicMock())

MODIFIED_FILES = [
    "areal/experimental/openai/types.py",
    "areal/experimental/openai/proxy/server.py",
    "areal/experimental/inference_service/data_proxy/app.py",
]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import ast

    for f in MODIFIED_FILES:
        src = Path(f"{REPO}/{f}").read_text()
        ast.parse(src)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_interaction_id_setter_getter():
    """Bare InteractionWithTokenLogpReward supports setting and reading interaction_id."""
    from areal.experimental.openai.types import InteractionWithTokenLogpReward

    i = InteractionWithTokenLogpReward()
    # Initially None (no completion, no response, no stored ID)
    assert i.interaction_id is None

    # Set and read back -- multiple distinct values
    for test_id in ["test-id-123", "updated-id-456", "uuid-7890-abcd"]:
        i.interaction_id = test_id
        assert i.interaction_id == test_id

    # Empty string is a valid ID (distinct from None)
    i.interaction_id = ""
    assert i.interaction_id == ""

    # Fresh instance: verify independent state
    j = InteractionWithTokenLogpReward()
    j.interaction_id = "other-instance"
    assert j.interaction_id == "other-instance"
    assert i.interaction_id == ""  # unchanged


# [pr_diff] fail_to_pass
def test_setter_rejects_completion_and_response():
    """Cannot overwrite interaction_id on completion or response objects."""
    from unittest.mock import MagicMock as Mock

    import pytest
    from areal.experimental.openai.types import InteractionWithTokenLogpReward

    # Completion instance
    ic = InteractionWithTokenLogpReward()
    ic.completion = Mock()
    ic.completion.id = "comp-123"
    assert ic.interaction_id == "comp-123"  # reads from completion
    with pytest.raises(ValueError, match="[Cc]omplet|[Cc]annot set|[Rr]espon"):
        ic.interaction_id = "should-fail"

    # Response instance
    ir = InteractionWithTokenLogpReward()
    ir.response = Mock()
    ir.response.id = "resp-456"
    assert ir.interaction_id == "resp-456"  # reads from response
    with pytest.raises(ValueError, match="[Cc]omplet|[Cc]annot set|[Rr]espon"):
        ir.interaction_id = "should-fail"


# [pr_diff] fail_to_pass
def test_roundtrip_preserves_interaction_id():
    """interaction_id survives serialize -> deserialize cycle."""
    import torch
    from areal.experimental.openai.proxy.server import (
        deserialize_interactions,
        serialize_interactions,
    )
    from areal.experimental.openai.types import InteractionWithTokenLogpReward

    # Test multiple distinct IDs and tensor shapes
    test_cases = [
        ("preserve-me-456", [[1, 2, 3]], 1.0),
        ("short", [[99]], -0.5),
        ("long-id-" + "x" * 100, [[0, 0, 0, 0, 0]], 0.0),
    ]
    for iid, ids, reward in test_cases:
        i = InteractionWithTokenLogpReward()
        i._cache = {
            "input_ids": torch.tensor(ids),
            "logprobs": torch.tensor([[0.1] * len(ids[0])]),
        }
        i.reward = reward
        i.interaction_id = iid

        serialized = serialize_interactions({"k1": i})
        deserialized = deserialize_interactions(serialized)

        assert deserialized["k1"].interaction_id == iid, f"ID lost for {iid!r}"
        assert deserialized["k1"].reward == reward


# [pr_diff] fail_to_pass
def test_multi_interaction_roundtrip():
    """Multiple interactions each retain their own interaction_id after roundtrip."""
    import torch
    from areal.experimental.openai.proxy.server import (
        deserialize_interactions,
        serialize_interactions,
    )
    from areal.experimental.openai.types import InteractionWithTokenLogpReward

    interactions = {}
    for idx in range(5):
        item = InteractionWithTokenLogpReward()
        item._cache = {
            "input_ids": torch.tensor([[idx, idx + 1, idx + 2]]),
            "logprobs": torch.tensor([[0.1 * idx, 0.2 * idx, 0.3 * idx]]),
        }
        item.reward = float(idx) * 0.5
        item.interaction_id = f"batch-id-{idx}"
        interactions[f"key_{idx}"] = item

    serialized = serialize_interactions(interactions)
    deserialized = deserialize_interactions(serialized)

    assert len(deserialized) == 5
    for idx in range(5):
        key = f"key_{idx}"
        assert deserialized[key].interaction_id == f"batch-id-{idx}"
        assert deserialized[key].reward == float(idx) * 0.5


# [pr_diff] fail_to_pass
def test_roundtrip_preserves_tensor_data():
    """Tensor data survives serialize -> deserialize cycle (not just metadata)."""
    import torch
    from areal.experimental.openai.proxy.server import (
        deserialize_interactions,
        serialize_interactions,
    )
    from areal.experimental.openai.types import InteractionWithTokenLogpReward

    i = InteractionWithTokenLogpReward()
    input_ids = torch.tensor([[10, 20, 30, 40]])
    logprobs = torch.tensor([[0.5, -0.3, 0.7, -1.2]])
    i._cache = {"input_ids": input_ids, "logprobs": logprobs}
    i.reward = 2.5
    i.interaction_id = "tensor-test"

    serialized = serialize_interactions({"t1": i})
    deserialized = deserialize_interactions(serialized)

    restored = deserialized["t1"]
    assert torch.allclose(restored._cache["input_ids"].float(), input_ids.float())
    assert torch.allclose(restored._cache["logprobs"].float(), logprobs.float())


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) -- regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_serialize_value_roundtrip():
    """Core serialize_value/deserialize_value utilities still work correctly."""
    import torch
    from areal.infra.rpc.serialization import deserialize_value, serialize_value

    # Single tensor
    t = torch.tensor([1.0, 2.0, 3.0])
    assert torch.allclose(t, deserialize_value(serialize_value(t)))

    # Mixed dict with tensors, strings, nested lists
    data = {"a": torch.tensor([1, 2]), "b": "hello", "c": [torch.tensor([3.0])]}
    d = deserialize_value(serialize_value(data))
    assert torch.allclose(data["a"], d["a"])
    assert d["b"] == "hello"
    assert torch.allclose(data["c"][0], d["c"][0])


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) -- CI/CD regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass -- CI: ruff lint check on modified files
def test_ruff_lint_modified():
    """Modified files pass ruff linter checks (pass_to_pass)."""
    import subprocess

    # Install ruff if not available
    install_result = subprocess.run(
        ["pip", "install", "--quiet", "ruff"],
        capture_output=True,
        timeout=60,
    )
    if install_result.returncode != 0:
        # If we can't install ruff, skip this test
        return

    # Run ruff check on modified files - we only verify ruff can process the files
    # (returncode 0 = no errors, 1 = lint errors found but syntax valid)
    for f in MODIFIED_FILES:
        result = subprocess.run(
            ["ruff", "check", f"{REPO}/{f}"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Ruff exit codes: 0 = success/no issues, 1 = lint violations found
        # Anything else indicates a failure (crash, file not found, etc)
        if result.returncode not in [0, 1]:
            raise AssertionError(
                f"Ruff failed to process {f} (exit {result.returncode}):\n{result.stderr}"
            )


# [repo_tests] pass_to_pass -- CI: file existence check
def test_modified_files_exist():
    """Modified files exist in the repository (pass_to_pass)."""
    for f in MODIFIED_FILES:
        path = Path(f"{REPO}/{f}")
        if not path.exists():
            raise AssertionError(f"Modified file does not exist: {f}")
        if not path.is_file():
            raise AssertionError(f"Modified path is not a file: {f}")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- rules from AGENTS.md / CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass -- AGENTS.md:30 @ 3bf10c9
def test_no_wildcard_imports():
    """No wildcard imports (from x import *) in modified files."""
    for f in MODIFIED_FILES:
        src = Path(f"{REPO}/{f}").read_text()
        for i, line in enumerate(src.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("from ") and "import *" in stripped:
                raise AssertionError(
                    f"Wildcard import at {f}:{i}: {stripped}"
                )


# [agent_config] pass_to_pass -- AGENTS.md:99 @ 3bf10c9
def test_type_hints_on_new_fields():
    """New dataclass fields and function signatures use explicit type hints."""
    # AST-only because: checking type annotations requires parsing, not execution
    import ast

    src = Path(f"{REPO}/areal/experimental/openai/types.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "InteractionWithTokenLogpReward":
            # Check that _interaction_id field has a type annotation
            annotated_names = [
                stmt.target.id
                for stmt in node.body
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name)
            ]
            assert "_interaction_id" in annotated_names, (
                "_interaction_id field must have an explicit type annotation"
            )
            break
    else:
        raise AssertionError("InteractionWithTokenLogpReward class not found")


# [agent_config] pass_to_pass -- AGENTS.md:162-163 @ 3bf10c9
def test_new_fields_have_defaults():
    """New dataclass fields must have default values for backward compatibility."""
    # AST-only because: checking defaults requires parsing the dataclass definition
    import ast

    src = Path(f"{REPO}/areal/experimental/openai/types.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "InteractionWithTokenLogpReward":
            for stmt in node.body:
                if (
                    isinstance(stmt, ast.AnnAssign)
                    and isinstance(stmt.target, ast.Name)
                    and stmt.target.id == "_interaction_id"
                ):
                    assert stmt.value is not None, (
                        "_interaction_id must have a default value "
                        "(backward compat: AGENTS.md:162-163)"
                    )
                    return
            # Field doesn't exist yet (base commit) -- vacuously passes
            return
    raise AssertionError("InteractionWithTokenLogpReward class not found")


# [agent_config] fail_to_pass -- AGENTS.md:95 @ 3bf10c9
def test_no_tolist_in_serialize():
    """serialize_interactions must not call .tolist() directly -- use serialize_value instead."""
    import ast

    src = Path(f"{REPO}/areal/experimental/openai/proxy/server.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "serialize_interactions":
            for inner in ast.walk(node):
                if (
                    isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr == "tolist"
                ):
                    raise AssertionError(
                        f"serialize_interactions calls .tolist() at line {inner.lineno} -- "
                        "use serialize_value instead (AGENTS.md:95)"
                    )
            return  # function found and checked
    raise AssertionError("serialize_interactions function not found in server.py")


# [agent_config] pass_to_pass -- AGENTS.md:89-91 @ 3bf10c9
def test_no_bare_print():
    """Modified files must not use bare print() -- use areal.utils.logging instead."""
    import ast

    for f in MODIFIED_FILES:
        src = Path(f"{REPO}/{f}").read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "print":
                    raise AssertionError(
                        f"Bare print() call in {f}:{node.lineno} -- "
                        "use areal.utils.logging instead (AGENTS.md:89-91)"
                    )
