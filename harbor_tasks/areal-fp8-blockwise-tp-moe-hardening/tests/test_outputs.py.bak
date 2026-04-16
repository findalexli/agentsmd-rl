"""
Task: areal-fp8-blockwise-tp-moe-hardening
Repo: inclusionAI/AReaL @ d36657168b4929f3b20b2b6c891bdfefa0243bb2
PR:   #1118

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace

REPO = "/workspace/AReaL"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_archon_fp8_config():
    """Extract ArchonFP8Config class from source and return it.

    Uses regex to isolate the class, then exec() with minimal builtins.
    This avoids importing the full areal package (which needs torch/GPU).
    """
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    match = re.search(
        r"(@dataclass[^\n]*\nclass ArchonFP8Config:.*?)(?=\n@dataclass|\nclass \w)",
        src, re.DOTALL,
    )
    assert match, "Could not find ArchonFP8Config class in cli_args.py"
    ns = {"__builtins__": __builtins__}
    exec("from dataclasses import dataclass, field\n" + match.group(1), ns)
    return ns["ArchonFP8Config"]


def _find_function_node(filepath, funcname):
    """Find an ast.FunctionDef node by name in the given file."""
    src = Path(f"{REPO}/{filepath}").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == funcname:
            return node, src
    return None, src


def _find_function_in_class(filepath, classname, funcname):
    """Find an ast.FunctionDef inside a specific class."""
    src = Path(f"{REPO}/{filepath}").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == classname:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == funcname:
                    return item, src
    return None, src


def _get_source_segment(src, node):
    """Get source code for an AST node."""
    lines = src.splitlines(keepends=True)
    return "".join(lines[node.lineno - 1 : node.end_lineno])


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    modified_files = [
        "areal/api/cli_args.py",
        "areal/experimental/engine/archon_checkpoint.py",
        "areal/experimental/engine/archon_engine.py",
        "areal/experimental/engine/archon_utils.py",
        "areal/experimental/models/archon/fp8.py",
        "areal/experimental/models/archon/fp8_checkpoint.py",
    ]
    for fname in modified_files:
        src = Path(f"{REPO}/{fname}").read_text()
        compile(src, fname, "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — ArchonFP8Config.enabled property
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_fp8_config_enabled_property():
    """ArchonFP8Config has an 'enabled' property: True for 'blockwise', False for 'disabled'."""
    Cfg = _load_archon_fp8_config()

    # Test blockwise mode → enabled should be True
    cfg_blockwise = Cfg(mode="blockwise")
    assert hasattr(cfg_blockwise, "enabled"), (
        "ArchonFP8Config missing 'enabled' attribute"
    )
    assert cfg_blockwise.enabled is True, (
        f"Expected enabled=True for mode='blockwise', got {cfg_blockwise.enabled!r}"
    )

    # Test disabled mode → enabled should be False
    cfg_disabled = Cfg(mode="disabled")
    assert cfg_disabled.enabled is False, (
        f"Expected enabled=False for mode='disabled', got {cfg_disabled.enabled!r}"
    )


# [pr_diff] fail_to_pass
def test_fp8_config_post_init_uses_enabled():
    """ArchonFP8Config.__post_init__ uses self.enabled (not raw mode check)."""
    Cfg = _load_archon_fp8_config()

    # The fix changed __post_init__ to use self.enabled instead of
    # self.mode != "disabled". Verify by checking that the validation
    # still works (behavioral) AND that the source references self.enabled.

    # Behavioral: blockwise + use_triton=False should still raise ValueError
    try:
        Cfg(mode="blockwise", use_triton=False)
        raise AssertionError("Should reject blockwise + use_triton=False")
    except ValueError:
        pass

    # Structural: __post_init__ references self.enabled (not self.mode != "disabled")
    node, src = _find_function_in_class(
        "areal/api/cli_args.py", "ArchonFP8Config", "__post_init__"
    )
    assert node is not None, "ArchonFP8Config.__post_init__ not found"
    func_src = _get_source_segment(src, node)
    assert "self.enabled" in func_src, (
        "__post_init__ should reference self.enabled, not raw mode check"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — validate_fp8_shard_alignment for GroupedExperts
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_validate_alignment_handles_grouped_experts():
    """validate_fp8_shard_alignment checks GroupedExperts modules (w1/w2/w3), not just nn.Linear.

    AST verification justified: this is GPU kernel validation code that requires
    torch.distributed and CUDA to run. We verify the function inspects GroupedExperts
    and checks per-expert shard dimensions.
    """
    node, src = _find_function_node(
        "areal/experimental/models/archon/fp8.py",
        "validate_fp8_shard_alignment",
    )
    assert node is not None, "validate_fp8_shard_alignment not found"
    func_src = _get_source_segment(src, node)

    # Must reference GroupedExperts (either import or isinstance check)
    assert "GroupedExperts" in func_src, (
        "validate_fp8_shard_alignment must handle GroupedExperts modules"
    )

    # Must check w1, w2, w3 weights (the 3D expert weight tensors)
    for wname in ("w1", "w2", "w3"):
        assert f'"{wname}"' in func_src or f"'{wname}'" in func_src, (
            f"validate_fp8_shard_alignment must check expert weight {wname}"
        )

    # Must raise ValueError for misaligned expert weights
    has_expert_error = False
    for child in ast.walk(node):
        if isinstance(child, ast.Raise) and child.exc is not None:
            raise_src = ast.get_source_segment(src, child)
            if raise_src and "expert" in raise_src.lower():
                has_expert_error = True
                break
    assert has_expert_error, (
        "validate_fp8_shard_alignment must raise ValueError for misaligned expert weights"
    )


# [pr_diff] fail_to_pass
def test_validate_alignment_not_linear_only():
    """validate_fp8_shard_alignment does not skip non-Linear modules unconditionally.

    The base code had `if not isinstance(mod, nn.Linear): continue` which silently
    skipped GroupedExperts. The fix removes this blanket skip.
    """
    node, src = _find_function_node(
        "areal/experimental/models/archon/fp8.py",
        "validate_fp8_shard_alignment",
    )
    assert node is not None, "validate_fp8_shard_alignment not found"
    func_src = _get_source_segment(src, node)

    # The old pattern: "if not isinstance(mod, nn.Linear):\n    continue"
    # must NOT be present — it would skip all non-Linear modules.
    # Check across adjacent lines since the continue is on the next line.
    lines = func_src.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if "not isinstance" in stripped and "nn.Linear" in stripped:
            # Check if next line is a bare continue
            if i + 1 < len(lines) and lines[i + 1].strip() == "continue":
                raise AssertionError(
                    "validate_fp8_shard_alignment still has blanket "
                    "'if not isinstance(mod, nn.Linear): continue' "
                    "which would skip GroupedExperts validation"
                )

    # Also check there's no early continue that skips non-Linear without checking _fp8_block
    # The correct pattern checks _fp8_block first, then dispatches by type
    assert "hasattr" in func_src and "_fp8_block" in func_src, (
        "validate_fp8_shard_alignment should check _fp8_block attribute"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — dequant_fp8_state_dict dtype restriction
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dequant_only_accepts_e4m3fn():
    """dequant_fp8_state_dict only recognizes float8_e4m3fn as FP8 dtype.

    The base code accepted 4 FP8 dtypes (e4m3fn, e5m2, e4m3fnuz, e5m2fnuz).
    The fix restricts to only e4m3fn, matching what _prepare_fp8_state_dict creates.
    """
    src = Path(f"{REPO}/areal/experimental/models/archon/fp8_checkpoint.py").read_text()

    # Find dequant_fp8_state_dict function
    tree = ast.parse(src)
    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "dequant_fp8_state_dict":
            func_node = node
            break
    assert func_node is not None, "dequant_fp8_state_dict not found"

    func_src = _get_source_segment(src, func_node)

    # Must contain float8_e4m3fn (the one valid dtype)
    assert "float8_e4m3fn" in func_src, (
        "dequant_fp8_state_dict must recognize float8_e4m3fn"
    )

    # Must NOT contain the removed FP8 dtypes in the fp8_dtypes set
    for bad_dtype in ["float8_e5m2", "float8_e4m3fnuz", "float8_e5m2fnuz"]:
        assert bad_dtype not in func_src, (
            f"dequant_fp8_state_dict should not accept {bad_dtype} — "
            f"only float8_e4m3fn is valid (matches _prepare_fp8_state_dict)"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — _check_fp8_shard_compatibility
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_check_shard_compatibility_exists():
    """_check_fp8_shard_compatibility function exists and validates DTensor placements.

    This early-exit validation prevents wasted DCP I/O when FP8 weights have
    unsupported column-shard (Shard(1)) placements.
    """
    node, src = _find_function_node(
        "areal/experimental/engine/archon_checkpoint.py",
        "_check_fp8_shard_compatibility",
    )
    assert node is not None, (
        "_check_fp8_shard_compatibility function not found in archon_checkpoint.py"
    )

    func_src = _get_source_segment(src, node)

    # Must check Shard placements
    assert "Shard" in func_src, (
        "_check_fp8_shard_compatibility must check Shard placements"
    )

    # Must raise ValueError for unsupported placements
    has_raise = False
    for child in ast.walk(node):
        if isinstance(child, ast.Raise) and child.exc is not None:
            exc = child.exc
            if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
                if exc.func.id == "ValueError":
                    has_raise = True
                    break
    assert has_raise, (
        "_check_fp8_shard_compatibility must raise ValueError for unsupported placements"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — DTensor handling in _fp8_linear_fwd
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_fp8_linear_handles_dtensor():
    """_fp8_linear_fwd calls to_local() on weight before passing to fp8_mm.

    After tensor parallelism, nn.Linear.weight becomes a DTensor. The patched
    FP8 forward must convert to local tensor before blockwise matmul.
    AST justified: requires GPU + DTensor runtime to test behaviorally.
    """
    src = Path(f"{REPO}/areal/experimental/models/archon/fp8.py").read_text()

    # Find _fp8_linear_fwd (it's a nested function inside _patch_fp8_forward)
    tree = ast.parse(src)
    fwd_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_fp8_linear_fwd":
            fwd_node = node
            break
    assert fwd_node is not None, "_fp8_linear_fwd not found"

    func_src = _get_source_segment(src, fwd_node)

    # Must call to_local() on the weight to handle DTensor
    assert "to_local" in func_src, (
        "_fp8_linear_fwd must call to_local() to handle DTensor weights from TP"
    )

    # Must not pass self.weight directly to fp8_mm when DTensor is possible
    # The fix assigns weight = self.weight, then conditionally calls to_local()
    assert "weight" in func_src, (
        "_fp8_linear_fwd must use a local variable for weight handling"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — _fp8_block stored on expert module
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_experts_forward_stores_fp8_block():
    """_patch_fp8_experts_forward stores _fp8_block on the module.

    Without _fp8_block, validate_fp8_shard_alignment won't check expert modules
    (it uses hasattr(mod, '_fp8_block') as the gate). The base code only stored
    _fp8_use_triton but not _fp8_block.
    """
    node, src = _find_function_node(
        "areal/experimental/models/archon/fp8.py",
        "_patch_fp8_experts_forward",
    )
    assert node is not None, "_patch_fp8_experts_forward not found"

    func_src = _get_source_segment(src, node)

    # Must assign _fp8_block to the module
    assert "_fp8_block" in func_src, (
        "_patch_fp8_experts_forward must store _fp8_block on the module "
        "so validate_fp8_shard_alignment can check expert alignment"
    )

    # Verify it's an actual assignment (not just a comment or string)
    has_assignment = False
    for child in ast.walk(node):
        if isinstance(child, ast.Assign):
            for target in child.targets:
                target_src = ast.get_source_segment(src, target)
                if target_src and "_fp8_block" in target_src:
                    has_assignment = True
                    break
    assert has_assignment, (
        "_patch_fp8_experts_forward must assign _fp8_block (not just reference it)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Key functions (present on both base and fix) have real logic, not stubs."""
    # Only check functions that exist on both base and fix commits
    checks = [
        ("areal/experimental/models/archon/fp8.py", None, "validate_fp8_shard_alignment"),
        ("areal/experimental/models/archon/fp8.py", None, "_patch_fp8_experts_forward"),
        ("areal/api/cli_args.py", "ArchonFP8Config", "__post_init__"),
    ]
    for filepath, classname, funcname in checks:
        if classname:
            node, src = _find_function_in_class(filepath, classname, funcname)
        else:
            node, src = _find_function_node(filepath, funcname)
        assert node is not None, f"{funcname} not found in {filepath}"
        # Count meaningful statements (not just pass/return None)
        meaningful = sum(
            1
            for stmt in ast.walk(node)
            if isinstance(stmt, (ast.If, ast.Raise, ast.Assert, ast.Assign, ast.Return, ast.For))
        )
        assert meaningful >= 2, (
            f"{funcname} in {filepath} appears to be a stub (only {meaningful} meaningful stmts)"
        )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from config files
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:93 @ d36657168b4929f3b20b2b6c891bdfefa0243bb2
def test_no_wildcard_imports():
    """No wildcard imports in modified files (CLAUDE.md: Never use wildcard imports)."""
    modified_files = [
        "areal/api/cli_args.py",
        "areal/experimental/engine/archon_checkpoint.py",
        "areal/experimental/engine/archon_engine.py",
        "areal/experimental/engine/archon_utils.py",
        "areal/experimental/models/archon/fp8.py",
        "areal/experimental/models/archon/fp8_checkpoint.py",
    ]
    for fname in modified_files:
        tree = ast.parse(Path(f"{REPO}/{fname}").read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and any(
                alias.name == "*" for alias in node.names
            ):
                raise AssertionError(
                    f"Wildcard import in {fname}: from {node.module} import *"
                )


# [agent_config] pass_to_pass — .claude/rules/api-config.md:37-42 @ d36657168b4929f3b20b2b6c891bdfefa0243bb2
def test_config_validation_uses_valueerror():
    """Config __post_init__ and validation functions raise ValueError with clear message."""
    # ArchonFP8Config.__post_init__ should raise ValueError
    node, src = _find_function_in_class(
        "areal/api/cli_args.py", "ArchonFP8Config", "__post_init__"
    )
    assert node is not None, "ArchonFP8Config.__post_init__ not found"
    found_valueerror = False
    for child in ast.walk(node):
        if isinstance(child, ast.Raise) and child.exc is not None:
            exc = child.exc
            if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
                assert exc.func.id == "ValueError", (
                    f"ArchonFP8Config.__post_init__ raises {exc.func.id}, expected ValueError"
                )
                found_valueerror = True
    assert found_valueerror, "ArchonFP8Config.__post_init__ has no raise statements"

    # _check_fp8_shard_compatibility should also use ValueError
    node2, src2 = _find_function_node(
        "areal/experimental/engine/archon_checkpoint.py",
        "_check_fp8_shard_compatibility",
    )
    if node2 is not None:
        for child in ast.walk(node2):
            if isinstance(child, ast.Raise) and child.exc is not None:
                exc = child.exc
                if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
                    assert exc.func.id == "ValueError", (
                        f"_check_fp8_shard_compatibility raises {exc.func.id}, expected ValueError"
                    )

# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the actual repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Repo's Python files pass ruff linting (pass_to_pass).

    Ruff is the linter configured in the repo's pre-commit hooks.
    This test ensures the modified files pass basic linting.
    """
    import subprocess
    import sys

    # Install ruff if not present
    subprocess.run([sys.executable, "-m", "pip", "install", "ruff", "-q"], check=True)

    # Run ruff check on modified files
    modified_files = [
        "areal/api/cli_args.py",
        "areal/experimental/engine/archon_checkpoint.py",
        "areal/experimental/engine/archon_engine.py",
        "areal/experimental/engine/archon_utils.py",
        "areal/experimental/models/archon/fp8.py",
        "areal/experimental/models/archon/fp8_checkpoint.py",
    ]
    for fname in modified_files:
        r = subprocess.run(
            ["ruff", "check", f"{REPO}/{fname}"],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        # Ruff returns 0 on success, 1 if there are fixable issues, 2+ for errors
        assert r.returncode <= 1, f"Ruff linting failed for {fname}:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_pyproject_valid():
    """Repo's pyproject.toml is valid (pass_to_pass).

    Validates pyproject.toml using validate-pyproject.
    """
    import subprocess
    import sys

    # Install validate-pyproject if not present
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "validate-pyproject", "packaging", "-q"],
        check=True
    )

    r = subprocess.run(
        ["validate-pyproject", f"{REPO}/pyproject.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"pyproject.toml validation failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_precommit_yaml():
    """Repo's YAML files pass pre-commit check-yaml (pass_to_pass)."""
    import subprocess
    import sys

    subprocess.run([sys.executable, "-m", "pip", "install", "pre-commit", "-q"], check=True)

    yaml_files = [
        "examples/math/gsm8k_sft_archon_fp8.yaml",
    ]
    for fname in yaml_files:
        r = subprocess.run(
            ["pre-commit", "run", "check-yaml", "--files", f"{REPO}/{fname}"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"YAML check failed for {fname}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_precommit_trailing_whitespace():
    """Modified Python files pass pre-commit trailing-whitespace check (pass_to_pass)."""
    import subprocess
    import sys

    subprocess.run([sys.executable, "-m", "pip", "install", "pre-commit", "-q"], check=True)

    modified_files = [
        "areal/api/cli_args.py",
        "areal/experimental/engine/archon_checkpoint.py",
        "areal/experimental/engine/archon_engine.py",
        "areal/experimental/engine/archon_utils.py",
        "areal/experimental/models/archon/fp8.py",
        "areal/experimental/models/archon/fp8_checkpoint.py",
    ]
    for fname in modified_files:
        r = subprocess.run(
            ["pre-commit", "run", "trailing-whitespace", "--files", f"{REPO}/{fname}"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"Trailing whitespace check failed for {fname}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_precommit_eof_fixer():
    """Modified Python files pass pre-commit end-of-file-fixer check (pass_to_pass)."""
    import subprocess
    import sys

    subprocess.run([sys.executable, "-m", "pip", "install", "pre-commit", "-q"], check=True)

    modified_files = [
        "areal/api/cli_args.py",
        "areal/experimental/engine/archon_checkpoint.py",
        "areal/experimental/engine/archon_engine.py",
        "areal/experimental/engine/archon_utils.py",
        "areal/experimental/models/archon/fp8.py",
        "areal/experimental/models/archon/fp8_checkpoint.py",
    ]
    for fname in modified_files:
        r = subprocess.run(
            ["pre-commit", "run", "end-of-file-fixer", "--files", f"{REPO}/{fname}"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"EOF fixer check failed for {fname}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_precommit_private_key():
    """Repo passes pre-commit detect-private-key check (pass_to_pass)."""
    import subprocess
    import sys

    subprocess.run([sys.executable, "-m", "pip", "install", "pre-commit", "-q"], check=True)

    r = subprocess.run(
        ["pre-commit", "run", "detect-private-key", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Private key detection check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_precommit_large_files():
    """Repo passes pre-commit check-added-large-files (pass_to_pass).

    Ensures no files larger than 1000KB are committed (excluding uv.lock).
    """
    import subprocess
    import sys

    subprocess.run([sys.executable, "-m", "pip", "install", "pre-commit", "-q"], check=True)

    r = subprocess.run(
        ["pre-commit", "run", "check-added-large-files", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Large files check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_precommit_json():
    """Repo's JSON files pass pre-commit check-json (pass_to_pass)."""
    import subprocess
    import sys

    subprocess.run([sys.executable, "-m", "pip", "install", "pre-commit", "-q"], check=True)

    r = subprocess.run(
        ["pre-commit", "run", "check-json", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"JSON check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_precommit_nbstripout():
    """Repo's Jupyter notebooks pass nbstripout (no outputs committed) (pass_to_pass).

    nbstripout ensures notebook outputs and execution counts are not committed,
    keeping the repo size small and diffs clean.
    """
    import subprocess
    import sys

    subprocess.run([sys.executable, "-m", "pip", "install", "pre-commit", "-q"], check=True)

    notebook_files = [
        "notebook/math_reflection_en.ipynb",
        "notebook/math_reflection_zh.ipynb",
        "notebook/search_agent_zh.ipynb",
    ]
    for fname in notebook_files:
        r = subprocess.run(
            ["pre-commit", "run", "nbstripout", "--files", f"{REPO}/{fname}"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"nbstripout check failed for {fname}:\\n{r.stderr}"
