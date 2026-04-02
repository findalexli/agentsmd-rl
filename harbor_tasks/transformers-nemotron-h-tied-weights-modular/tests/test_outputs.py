"""
Task: transformers-nemotron-h-tied-weights-modular
Repo: huggingface/transformers @ 2cd52c267ce4d0212eaa40c0ec7192a11654336f
PR:   #44876

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import subprocess
from pathlib import Path

REPO = "/repo"
MODELING = f"{REPO}/src/transformers/models/nemotron_h/modeling_nemotron_h.py"
MODULAR = f"{REPO}/src/transformers/models/nemotron_h/modular_nemotron_h.py"


def _parse(path: str) -> ast.Module:
    return ast.parse(Path(path).read_text())


def _find_class(tree: ast.Module, name: str) -> ast.ClassDef | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _class_has_assign(cls: ast.ClassDef, attr_name: str) -> bool:
    """Check if a class has a direct class-level assignment to attr_name."""
    for item in cls.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name) and target.id == attr_name:
                    return True
    return False


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """Both modeling and modular files must be valid Python."""
    # AST-only because: torch/transformers deps not installed in test container
    for path in [MODELING, MODULAR]:
        src = Path(path).read_text()
        ast.parse(src)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core bug fix checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_base_class_no_tied_weights_keys():
    """NemotronHPreTrainedModel must NOT define _tied_weights_keys (it shadows parent)."""
    # AST-only because: torch/transformers deps not installed in test container
    tree = _parse(MODELING)
    cls = _find_class(tree, "NemotronHPreTrainedModel")
    assert cls is not None, "NemotronHPreTrainedModel not found in modeling file"
    assert not _class_has_assign(cls, "_tied_weights_keys"), (
        "NemotronHPreTrainedModel still defines _tied_weights_keys — "
        "it should only be on NemotronHForCausalLM"
    )


# [pr_diff] fail_to_pass
def test_modular_base_no_tied_weights_keys():
    """Modular NemotronHPreTrainedModel must NOT define _tied_weights_keys."""
    # AST-only because: torch/transformers deps not installed in test container
    tree = _parse(MODULAR)
    cls = _find_class(tree, "NemotronHPreTrainedModel")
    if cls is None:
        return  # class absent from modular is acceptable
    assert not _class_has_assign(cls, "_tied_weights_keys"), (
        "Modular NemotronHPreTrainedModel still defines _tied_weights_keys"
    )


# [pr_diff] fail_to_pass
def test_modular_causal_lm_no_init_override():
    """Modular NemotronHForCausalLM must not have an __init__ that deletes _tied_weights_keys."""
    # AST-only because: torch/transformers deps not installed in test container
    tree = _parse(MODULAR)
    cls = _find_class(tree, "NemotronHForCausalLM")
    assert cls is not None, "NemotronHForCausalLM not found in modular"
    for item in cls.body:
        if isinstance(item, ast.FunctionDef) and item.name == "__init__":
            # If __init__ exists, it must NOT contain `del self._tied_weights_keys`
            for stmt in ast.walk(item):
                if isinstance(stmt, ast.Delete):
                    for target in stmt.targets:
                        if isinstance(target, ast.Attribute) and target.attr == "_tied_weights_keys":
                            raise AssertionError(
                                "Modular __init__ still deletes _tied_weights_keys — "
                                "remove the __init__ override entirely"
                            )
            # Also check: if __init__ body is only super().__init__ + del, it's the old workaround
            non_expr_stmts = [
                s for s in item.body
                if not isinstance(s, ast.Expr)  # skip docstrings
            ]
            if len(non_expr_stmts) <= 2:
                # A 1-2 line __init__ (super().__init__ + maybe one stmt) is suspicious
                # but only fail if it has no meaningful logic beyond the super call
                has_only_super = all(
                    (isinstance(s, ast.Expr) and isinstance(s.value, ast.Call))
                    or isinstance(s, ast.Delete)
                    for s in non_expr_stmts
                )
                if has_only_super and len(non_expr_stmts) == 1:
                    # Just super().__init__() — unnecessary override, but not the bug
                    pass


# [pr_diff] fail_to_pass
def test_causal_lm_init_config_annotation():
    """NemotronHForCausalLM.__init__ config param has NemotronHConfig type annotation."""
    # AST-only because: torch/transformers deps not installed in test container
    tree = _parse(MODELING)
    cls = _find_class(tree, "NemotronHForCausalLM")
    assert cls is not None, "NemotronHForCausalLM not found"
    for item in cls.body:
        if isinstance(item, ast.FunctionDef) and item.name == "__init__":
            args = item.args
            assert len(args.args) >= 2, "__init__ must have at least self and config"
            config_arg = args.args[1]
            ann = config_arg.annotation
            assert ann is not None, "config parameter missing type annotation"
            # Check that annotation references NemotronHConfig (Name or Attribute node)
            ann_dump = ast.dump(ann)
            assert "NemotronHConfig" in ann_dump, (
                f"config annotation should reference NemotronHConfig, got: {ast.dump(ann)}"
            )
            return
    raise AssertionError("__init__ not found on NemotronHForCausalLM")


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_causal_lm_has_tied_weights_keys():
    """NemotronHForCausalLM must retain _tied_weights_keys as a class attribute."""
    # AST-only because: torch/transformers deps not installed in test container
    tree = _parse(MODELING)
    cls = _find_class(tree, "NemotronHForCausalLM")
    assert cls is not None, "NemotronHForCausalLM not found"
    assert _class_has_assign(cls, "_tied_weights_keys"), (
        "NemotronHForCausalLM must define _tied_weights_keys"
    )


# [static] pass_to_pass
def test_key_classes_exist():
    """All key model classes must be present in modeling file."""
    # AST-only because: torch/transformers deps not installed in test container
    tree = _parse(MODELING)
    classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    required = {"NemotronHModel", "NemotronHForCausalLM", "NemotronHPreTrainedModel"}
    missing = required - classes
    assert not missing, f"Missing classes: {missing}"


# [static] pass_to_pass
def test_modeling_not_stub():
    """Modeling file must not be stubbed out (original is ~1500 lines)."""
    lines = len(Path(MODELING).read_text().splitlines())
    assert lines > 500, f"Modeling file suspiciously short ({lines} lines, expected >500)"


# [static] pass_to_pass
def test_modular_not_stub():
    """Modular file must not be stubbed out (original is ~400 lines)."""
    lines = len(Path(MODULAR).read_text().splitlines())
    assert lines > 150, f"Modular file suspiciously short ({lines} lines, expected >150)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:2 @ 2cd52c267ce4d0212eaa40c0ec7192a11654336f
def test_ruff_clean():
    """Both files must pass ruff linting (CLAUDE.md: 'make style: runs formatters and linters')."""
    r = subprocess.run(
        ["ruff", "check", MODELING, MODULAR, "--select", "E,F,W", "--quiet"],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [agent_config] pass_to_pass — .ai/skills/add-or-fix-type-checking/SKILL.md:185 @ 2cd52c267ce4d0212eaa40c0ec7192a11654336f
def test_no_bare_type_ignore():
    """No bare '# type: ignore' without error code in modified files (SKILL.md: 'Always add the specific error code')."""
    for path in [MODELING, MODULAR]:
        src = Path(path).read_text()
        # Match bare `# type: ignore` NOT followed by `[` (which would indicate an error code)
        bare_ignores = re.findall(r"#\s*type:\s*ignore(?!\[)", src)
        assert not bare_ignores, (
            f"{Path(path).name} has bare '# type: ignore' without error code — "
            f"use '# type: ignore[error-code]' instead. Found {len(bare_ignores)} occurrence(s)."
        )
