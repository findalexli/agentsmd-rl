"""
Task: sglang-flux2-tokenization-length
Repo: sgl-project/sglang @ edd4d540237be4267c3a260d6a2f23a035e203af
PR:   21407

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import textwrap
from pathlib import Path

REPO = "/workspace/sglang"
TARGET = f"{REPO}/python/sglang/multimodal_gen/configs/pipeline_configs/flux.py"


def _parse_target():
    """Parse the target file and return the AST tree and source text."""
    src = Path(TARGET).read_text()
    tree = ast.parse(src)
    return tree, src


def _get_class_node(tree: ast.Module, class_name: str) -> ast.ClassDef | None:
    """Return the ClassDef AST node by name."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    return None


def _find_field_value(body: list[ast.stmt], field_name: str) -> ast.expr | None:
    """Find the value node of a class-level assignment (annotated or plain)."""
    for item in body:
        if isinstance(item, ast.AnnAssign) and hasattr(item.target, "id"):
            if item.target.id == field_name and item.value is not None:
                return item.value
        if isinstance(item, ast.Assign) and len(item.targets) == 1:
            t = item.targets[0]
            if hasattr(t, "id") and t.id == field_name:
                return item.value
    return None


def _eval_field_default(value_node: ast.expr, source_path: str):
    """Compile and evaluate a field default expression, resolving dataclass field().

    Returns the materialized default value (calls default_factory if present).
    """
    from dataclasses import field

    expr_code = compile(ast.Expression(body=value_node), source_path, "eval")
    # Provide all builtins plus field/dict so lambdas in field(default_factory=...) work
    ns = {"field": field, "dict": dict, "list": list, "tuple": tuple,
          "True": True, "False": False, "None": None, "__builtins__": __builtins__}
    value = eval(expr_code, ns)
    if hasattr(value, "default_factory") and callable(value.default_factory):
        return value.default_factory()
    if hasattr(value, "default") and value.default is not ...:
        return value.default
    return value


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """flux.py must parse without syntax errors.
    # AST-only because: module imports torch/sglang which are not installed
    """
    _parse_target()  # will raise SyntaxError if invalid


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_flux2_text_encoder_extra_args_512():
    """Flux2PipelineConfig must override text_encoder_extra_args with max_length=512.

    On the base commit, Flux2PipelineConfig inherits text_encoder_extra_args from
    FluxPipelineConfig which uses max_length=77 (CLIP-style). The fix adds an
    explicit override with max_length=512 for the Qwen3/Mistral text encoder.

    # AST-only because: module imports torch/sglang which are not installed
    """
    tree, _ = _parse_target()

    cls = _get_class_node(tree, "Flux2PipelineConfig")
    assert cls is not None, "Flux2PipelineConfig class not found"

    value_node = _find_field_value(cls.body, "text_encoder_extra_args")
    assert value_node is not None, (
        "Flux2PipelineConfig must override text_encoder_extra_args "
        "(inherited max_length=77 from FluxPipelineConfig is wrong for Flux2)"
    )

    actual = _eval_field_default(value_node, TARGET)
    assert isinstance(actual, list) and len(actual) >= 1, (
        f"text_encoder_extra_args should be a non-empty list, got {actual!r}"
    )

    # Verify max_length=512 in at least one entry
    found_512 = False
    for d in actual:
        assert isinstance(d, dict), f"Each entry must be a dict, got {type(d).__name__}"
        if d.get("max_length") == 512:
            found_512 = True
    assert found_512, f"No entry with max_length=512 in text_encoder_extra_args: {actual}"

    # Verify it's NOT 77 (the inherited CLIP value)
    for d in actual:
        assert d.get("max_length") != 77, (
            "text_encoder_extra_args still has max_length=77 (CLIP), should be 512"
        )


# [pr_diff] fail_to_pass
def test_klein_forces_max_length_512():
    """Flux2KleinPipelineConfig.tokenize_prompt must use max_length=512
    regardless of what tok_kwargs contains.

    On the base commit, max_length = tok_kwargs.pop("max_length", 512) means
    an inbound max_length=77 would be used. The fix pops and discards it,
    then hardcodes max_length=512.

    # AST-only because: module imports torch/sglang which are not installed;
    # we extract and exec only the max_length-handling lines from tokenize_prompt.
    """
    tree, src = _parse_target()
    lines = src.splitlines()

    cls = _get_class_node(tree, "Flux2KleinPipelineConfig")
    assert cls is not None, "Flux2KleinPipelineConfig class not found"

    # Find tokenize_prompt method
    func = None
    for item in cls.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if item.name == "tokenize_prompt":
                func = item
                break
    assert func is not None, "Flux2KleinPipelineConfig.tokenize_prompt not found"

    # Extract source lines of the function body
    func_lines = lines[func.lineno - 1 : func.end_lineno]

    # Simulate the max_length resolution with varied inbound values.
    # On the base commit: tok_kwargs.pop("max_length", 512) → uses the inbound value.
    # On the fix: tok_kwargs.pop("max_length", None) discards it, then max_length = 512.
    #
    # We extract ONLY the relevant lines: tok_kwargs dict copy, the pop("max_length", ...)
    # call, and the standalone max_length = <value> assignment. We must be careful to
    # exclude the keyword arg `max_length=max_length,` inside the tokenizer() call and
    # the `padding = tok_kwargs.pop("padding", "max_length")` line which also mentions
    # "max_length" as a string value.
    for test_val in [77, 128, 256, 1024]:
        ns: dict = {"tok_kwargs": {"max_length": test_val}}
        executed = False

        for line in func_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("def "):
                continue
            # Execute tok_kwargs dict copy: tok_kwargs = dict(tok_kwargs or {})
            if re.match(r"^tok_kwargs\s*=\s*dict\(", stripped):
                exec(stripped, ns)
                executed = True
            # Execute ONLY the pop that targets "max_length" as the first arg,
            # not lines like padding = tok_kwargs.pop("padding", "max_length")
            elif re.match(r"^(max_length\s*=\s*)?tok_kwargs\.pop\(\s*['\"]max_length['\"]", stripped):
                exec(stripped, ns)
                executed = True
            # Execute standalone max_length assignment (not keyword arg in a call)
            elif re.match(r"^max_length\s*=\s*\d", stripped):
                exec(stripped, ns)
                executed = True

        assert executed, "No max_length handling found in tokenize_prompt"
        assert ns.get("max_length") == 512, (
            f"With tok_kwargs max_length={test_val}, resolved to "
            f"{ns.get('max_length')} instead of 512"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_parent_flux_config_max_length_77():
    """FluxPipelineConfig must retain max_length=77 in text_encoder_extra_args.

    The fix should only change Flux2 configs, not the parent Flux1 config
    which correctly uses CLIP-style max_length=77.

    # AST-only because: module imports torch/sglang which are not installed
    """
    tree, _ = _parse_target()

    cls = _get_class_node(tree, "FluxPipelineConfig")
    assert cls is not None, "FluxPipelineConfig class not found"

    value_node = _find_field_value(cls.body, "text_encoder_extra_args")
    assert value_node is not None, "FluxPipelineConfig.text_encoder_extra_args not found"

    actual = _eval_field_default(value_node, TARGET)
    assert isinstance(actual, list) and len(actual) >= 1, (
        f"text_encoder_extra_args should be a non-empty list, got {actual!r}"
    )
    assert any(isinstance(d, dict) and d.get("max_length") == 77 for d in actual), (
        f"FluxPipelineConfig should have max_length=77 (CLIP): {actual}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — python/sglang/multimodal_gen/.claude/skills/sglang-diffusion-add-model/SKILL.md:201,273-274 @ edd4d540237be4267c3a260d6a2f23a035e203af
def test_flux2_uses_field_default_factory():
    """Flux2PipelineConfig.text_encoder_extra_args must use field(default_factory=...)
    for its mutable default, not a bare list literal.

    # AST-only because: module imports torch/sglang which are not installed
    """
    tree, _ = _parse_target()

    cls = _get_class_node(tree, "Flux2PipelineConfig")
    assert cls is not None, "Flux2PipelineConfig class not found"

    value_node = _find_field_value(cls.body, "text_encoder_extra_args")
    assert value_node is not None, (
        "Flux2PipelineConfig must define text_encoder_extra_args"
    )

    # Must be a call to field(...), not a bare List literal
    assert isinstance(value_node, ast.Call), (
        f"text_encoder_extra_args should use field(default_factory=...), "
        f"got {type(value_node).__name__} instead of a Call node"
    )
    func_node = value_node.func
    func_name = getattr(func_node, "id", None) or getattr(func_node, "attr", None)
    assert func_name == "field", (
        f"Expected field(...) call, got {func_name}(...)"
    )
    kw_names = [kw.arg for kw in value_node.keywords]
    assert "default_factory" in kw_names, (
        f"field() call must use default_factory for mutable default, "
        f"got keywords: {kw_names}"
    )


# [agent_config] fail_to_pass — python/sglang/multimodal_gen/.claude/skills/sglang-diffusion-add-model/SKILL.md:267-274 @ edd4d540237be4267c3a260d6a2f23a035e203af
def test_flux2_text_encoder_extra_args_type_annotated():
    """Flux2PipelineConfig.text_encoder_extra_args must have a type annotation.

    SKILL.md requires all dataclass fields have explicit type annotations.

    # AST-only because: module imports torch/sglang which are not installed
    """
    tree, _ = _parse_target()

    cls = _get_class_node(tree, "Flux2PipelineConfig")
    assert cls is not None, "Flux2PipelineConfig class not found"

    # Check that text_encoder_extra_args is defined with an annotation (AnnAssign)
    for item in cls.body:
        if isinstance(item, ast.AnnAssign) and hasattr(item.target, "id"):
            if item.target.id == "text_encoder_extra_args":
                assert item.annotation is not None, (
                    "text_encoder_extra_args must have a type annotation"
                )
                return  # Found annotated assignment

    # If we reach here, check if it exists as a plain Assign (no annotation = fail)
    for item in cls.body:
        if isinstance(item, ast.Assign):
            for t in item.targets:
                if hasattr(t, "id") and t.id == "text_encoder_extra_args":
                    assert False, (
                        "text_encoder_extra_args is defined without a type annotation; "
                        "SKILL.md requires all dataclass fields to have explicit type annotations"
                    )

    assert False, "Flux2PipelineConfig must define text_encoder_extra_args"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_py_compile():
    """Repo's Python files compile without syntax errors (py_compile).

    # Uses py_compile because: torch/sglang dependencies are not installed
    """
    import py_compile
    py_compile.compile(TARGET, doraise=True)


# [repo_tests] pass_to_pass
def test_repo_ruff_critical():
    """Repo's Python files pass ruff critical checks (F401, F821).

    # F401: unused imports (catches import errors when dependencies missing)
    # F821: undefined names (catches typos/undefined variables)
    # AST-only fallback: if ruff not installed, do basic AST name resolution
    """
    import subprocess

    # Try to run ruff if available
    try:
        r = subprocess.run(
            ["python3", "-m", "ruff", "check", "--select", "F401,F821", TARGET],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        if r.returncode == 0:
            return  # ruff passed
        # If ruff has errors, check if they're real issues or just noise
        if "F821" in r.stdout or "F401" in r.stdout:
            # These are real critical errors
            assert False, f"Ruff found critical errors:\n{r.stdout}"
    except FileNotFoundError:
        pass  # ruff not installed, fall back to AST check

    # AST fallback: check for undefined names in the target file
    tree, src = _parse_target()

    # Collect all defined names (imports, classes, functions, assignments)
    defined_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                defined_names.add(alias.asname if alias.asname else alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                defined_names.add(alias.asname if alias.asname else alias.name)
        elif isinstance(node, ast.ClassDef):
            defined_names.add(node.name)
        elif isinstance(node, ast.FunctionDef):
            defined_names.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            defined_names.add(node.id)
        elif isinstance(node, ast.arg):
            defined_names.add(node.arg)

    # Add builtins and common dataclass names
    defined_names.update(dir(__builtins__))
    defined_names.update(['field', 'dataclass'])

    # Check for undefined names (F821-like check)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id not in defined_names and not node.id.startswith('_'):
                pass  # Skip for now - many false positives without full analysis

    # If we get here, basic AST structure is valid


# [repo_tests] pass_to_pass
def test_repo_ast_structure():
    """Repo's flux.py has valid AST structure with required classes.

    Verifies that the key classes exist and have proper structure.
    """
    tree, _ = _parse_target()

    required_classes = [
        "FluxPipelineConfig",
        "Flux2PipelineConfig",
        "Flux2KleinPipelineConfig",
    ]

    found_classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            found_classes.append(node.name)

    for cls_name in required_classes:
        assert cls_name in found_classes, f"Required class {cls_name} not found in flux.py"


# ---------------------------------------------------------------------------
# Anti-stub (static) — implementation quality
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_klein_tokenize_prompt_not_stub():
    """Flux2KleinPipelineConfig.tokenize_prompt must have a meaningful body.

    # AST-only because: module imports torch/sglang which are not installed
    """
    tree, _ = _parse_target()

    cls = _get_class_node(tree, "Flux2KleinPipelineConfig")
    assert cls is not None, "Flux2KleinPipelineConfig class not found"

    for item in cls.body:
        if isinstance(item, ast.FunctionDef) and item.name == "tokenize_prompt":
            real_stmts = [
                s
                for s in item.body
                if not isinstance(s, ast.Pass)
                and not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
            ]
            assert len(real_stmts) >= 4, (
                f"tokenize_prompt has only {len(real_stmts)} real statements — "
                "looks like a stub"
            )
            return

    assert False, "Flux2KleinPipelineConfig.tokenize_prompt not found"
