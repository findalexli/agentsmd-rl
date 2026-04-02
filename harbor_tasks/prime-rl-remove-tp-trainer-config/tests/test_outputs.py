"""
Task: prime-rl-remove-tp-trainer-config
Repo: PrimeIntellect-ai/prime-rl @ 80a52899ea6a74e0738c15228181ef7b9775dfe9
PR:   2109

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import textwrap
from pathlib import Path

REPO = "/workspace/prime-rl"
BASE = f"{REPO}/src/prime_rl"
TRAINER_CFG = f"{BASE}/configs/trainer.py"
RL_CFG = f"{BASE}/configs/rl.py"
PARALLEL_DIMS = f"{BASE}/trainer/parallel_dims.py"
SFT_TRAIN = f"{BASE}/trainer/sft/train.py"
CHANGELOG = f"{REPO}/CHANGELOG.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse(path: str) -> tuple[str, ast.Module]:
    src = Path(path).read_text()
    return src, ast.parse(src)


def _find_class(tree: ast.Module, name: str) -> ast.ClassDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    raise AssertionError(f"Class {name!r} not found")


def _class_fields(cls: ast.ClassDef) -> set[str]:
    return {
        item.target.id
        for item in cls.body
        if isinstance(item, ast.AnnAssign)
        and isinstance(item.target, ast.Name)
        and not item.target.id.startswith("_")
    }


def _class_methods(cls: ast.ClassDef) -> set[str]:
    return {item.name for item in cls.body if isinstance(item, ast.FunctionDef)}


def _extract_method_body(source: str, cls: ast.ClassDef, method_name: str) -> str:
    """Extract a method's source, stripping decorators, for exec()."""
    for item in cls.body:
        if isinstance(item, ast.FunctionDef) and item.name == method_name:
            lines = source.splitlines(keepends=True)
            func_src = "".join(lines[item.lineno - 1 : item.end_lineno])
            body_lines = [l for l in func_src.splitlines(keepends=True)
                          if not l.strip().startswith("@")]
            return "".join(body_lines)
    raise AssertionError(f"Method {method_name!r} not found in {cls.name}")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified files must parse without errors."""
    for path in [TRAINER_CFG, RL_CFG, PARALLEL_DIMS, SFT_TRAIN]:
        src = Path(path).read_text()
        ast.parse(src)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_non_data_parallel_size_excludes_tp():
    """non_data_parallel_size must return cp*pp, not cp*tp*pp.

    Extracts the property via AST then execs it to test behaviorally.
    # AST-only because: module imports torch.distributed (GPU-only)
    """
    src, tree = _parse(PARALLEL_DIMS)
    cls = _find_class(tree, "ParallelDims")
    func_src = _extract_method_body(src, cls, "non_data_parallel_size")

    ns = {}
    exec(textwrap.dedent(func_src), ns)
    fn = ns["non_data_parallel_size"]

    # Test with multiple input combos; tp is set high to catch leaks
    for cp, pp, tp in [(4, 2, 8), (1, 1, 16), (2, 4, 4), (3, 3, 7)]:
        mock = type("M", (), {"cp": cp, "pp": pp, "tp": tp})()
        result = fn(mock)
        expected = cp * pp
        assert result == expected, (
            f"non_data_parallel_size({cp=},{pp=}) = {result}, expected {expected}"
        )


# [pr_diff] fail_to_pass
def test_seq_len_divisor_excludes_tp():
    """seq_len_divisor must return cp*2, not tp*cp*2.

    Extracts the property via AST then execs it to test behaviorally.
    # AST-only because: module imports torch.distributed (GPU-only)
    """
    src, tree = _parse(PARALLEL_DIMS)
    cls = _find_class(tree, "ParallelDims")
    func_src = _extract_method_body(src, cls, "seq_len_divisor")

    ns = {}
    exec(textwrap.dedent(func_src), ns)
    fn = ns["seq_len_divisor"]

    for cp, tp in [(4, 8), (1, 16), (3, 5), (6, 3)]:
        mock = type("M", (), {"cp": cp, "tp": tp})()
        result = fn(mock)
        expected = cp * 2
        assert result == expected, (
            f"seq_len_divisor({cp=}) = {result}, expected {expected}"
        )


# [pr_diff] fail_to_pass
# AST-only because: ModelConfig inherits pydantic BaseModel with torch-dependent validators
def test_model_config_no_tp_field():
    """ModelConfig must not have a tp field — it should be fully removed."""
    _, tree = _parse(TRAINER_CFG)
    cls = _find_class(tree, "ModelConfig")
    fields = _class_fields(cls)
    assert "tp" not in fields, f"ModelConfig still has tp (fields: {fields})"


# [pr_diff] fail_to_pass
# AST-only because: ParallelDims is a dataclass importing torch.distributed.DeviceMesh
def test_parallel_dims_no_tp():
    """ParallelDims must have no tp field and no tp_enabled property."""
    _, tree = _parse(PARALLEL_DIMS)
    cls = _find_class(tree, "ParallelDims")
    assert "tp" not in _class_fields(cls), "ParallelDims still has tp field"
    assert "tp_enabled" not in _class_methods(cls), "ParallelDims still has tp_enabled"


# [pr_diff] fail_to_pass
# AST-only because: sft/train.py imports torch, torch.distributed, and GPU-only modules
def test_sft_train_no_tp_multiplication():
    """SFT train.py must not reference model.tp in computations."""
    src, tree = _parse(SFT_TRAIN)
    tp_refs = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Attribute) and node.attr == "tp"
                and isinstance(node.value, ast.Attribute)
                and node.value.attr == "model"):
            segment = ast.get_source_segment(src, node) or f"line {node.lineno}"
            tp_refs.append(segment)
    assert not tp_refs, f"sft/train.py still references model.tp: {tp_refs}"


# [pr_diff] fail_to_pass
# AST-only because: rl.py imports torch and GPU-only config dependencies
def test_rl_deployment_no_tp():
    """auto_setup_deployment must not reference model.tp."""
    src, tree = _parse(RL_CFG)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "auto_setup_deployment":
            for n in ast.walk(node):
                if (isinstance(n, ast.Attribute) and n.attr == "tp"
                        and isinstance(n.value, ast.Attribute)
                        and n.value.attr == "model"):
                    raise AssertionError("auto_setup_deployment still references .model.tp")
            return
    raise AssertionError("auto_setup_deployment function not found")


# [pr_diff] fail_to_pass
def test_changelog_documents_tp_removal():
    """CHANGELOG.md must document the removal of the tp config field."""
    changelog = Path(CHANGELOG).read_text()
    lower = changelog.lower()
    assert "model.tp" in lower or ("tp" in lower and "removed" in lower) or (
        "tp" in lower and "tensor parallelism" in lower
    ), "CHANGELOG.md does not document the removal of model.tp"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_parallel_dims_core_fields():
    """ParallelDims must retain dp_replicate, dp_shard, cp, pp, ep, world_size."""
    _, tree = _parse(PARALLEL_DIMS)
    cls = _find_class(tree, "ParallelDims")
    fields = _class_fields(cls)
    required = {"dp_replicate", "dp_shard", "cp", "pp", "ep", "world_size"}
    missing = required - fields
    assert not missing, f"ParallelDims missing fields: {missing}"


# [pr_diff] pass_to_pass
def test_parallel_dims_methods_intact():
    """Key properties/methods must still exist on ParallelDims."""
    _, tree = _parse(PARALLEL_DIMS)
    cls = _find_class(tree, "ParallelDims")
    methods = _class_methods(cls)
    required = {
        "dp_enabled", "cp_enabled", "pp_enabled", "ep_enabled",
        "non_data_parallel_size", "seq_len_divisor", "build_mesh",
    }
    missing = required - methods
    assert not missing, f"ParallelDims missing methods: {missing}"


# [static] pass_to_pass
def test_model_config_retains_fields():
    """ModelConfig must still have cp, dp_replicate, ep and >=5 total fields."""
    _, tree = _parse(TRAINER_CFG)
    cls = _find_class(tree, "ModelConfig")
    fields = _class_fields(cls)
    for req in ("cp", "dp_replicate", "ep"):
        assert req in fields, f"ModelConfig missing required field {req}"
    assert len(fields) >= 5, f"ModelConfig has only {len(fields)} fields (stubbed?)"


# [static] pass_to_pass
def test_parallel_dims_not_stubbed():
    """parallel_dims.py must not be hollowed out."""
    src, tree = _parse(PARALLEL_DIMS)
    cls = _find_class(tree, "ParallelDims")
    method_count = sum(1 for item in cls.body if isinstance(item, ast.FunctionDef))
    assert method_count >= 8, f"ParallelDims has only {method_count} methods (stubbed?)"
    non_blank = [l for l in src.splitlines() if l.strip() and not l.strip().startswith("#")]
    assert len(non_blank) >= 80, f"parallel_dims.py only {len(non_blank)} substantive lines"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:5 @ 80a52899ea6a74e0738c15228181ef7b9775dfe9
def test_no_excessive_try_except():
    """Changed files must not introduce unnecessary try/except blocks (AGENTS.md:5)."""
    for path in [PARALLEL_DIMS, TRAINER_CFG]:
        _, tree = _parse(path)
        try_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Try))
        assert try_count <= 2, (
            f"{Path(path).name} has {try_count} try/except blocks (excessive)"
        )
