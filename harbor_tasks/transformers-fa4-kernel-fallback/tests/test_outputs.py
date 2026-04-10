"""
Task: transformers-fa4-kernel-fallback
Repo: huggingface/transformers @ a269c990e8571d9b9f8adfc1add9472eec3f252d
PR:   44797

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
import textwrap
from pathlib import Path

REPO = "/workspace/transformers"
MODIFIED_FILES = [
    "src/transformers/modeling_flash_attention_utils.py",
    "src/transformers/modeling_utils.py",
]
FLASH_UTILS = Path(f"{REPO}/src/transformers/modeling_flash_attention_utils.py")
MODELING_UTILS = Path(f"{REPO}/src/transformers/modeling_utils.py")


def _extract_dict_assignment(filepath: Path, var_name: str) -> dict:
    """Extract a dict literal assigned to var_name using AST.

    # AST-only because: transformers modules import torch at module level,
    # which is not installed in this CPU-only test container.
    """
    source = filepath.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == var_name:
                    return ast.literal_eval(node.value)
    raise ValueError(f"{var_name} not found in {filepath}")


def _extract_dict_keys(filepath: Path, var_name: str):
    """Extract keys from a dict assignment (handles non-literal values)."""
    source = filepath.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == var_name:
                    if isinstance(node.value, ast.Dict):
                        keys = []
                        for k in node.value.keys:
                            if isinstance(k, ast.Constant):
                                keys.append(k.value)
                            elif isinstance(k, ast.Num):  # Python 3.7 compat
                                keys.append(k.n)
                        return keys
    raise ValueError(f"{var_name} not found in {filepath}")


def _get_diff():
    """Get the git diff of agent changes."""
    for cmd in [
        ["git", "diff", "HEAD"],
        ["git", "diff", "--cached", "HEAD"],
        ["git", "diff", "HEAD~1"],
    ]:
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=10)
        if r.stdout.strip():
            return r.stdout
    return ""


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both modified files must parse without errors."""
    for relpath in MODIFIED_FILES:
        src = Path(f"{REPO}/{relpath}").read_text()
        ast.parse(src)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_fa4_in_fallback_dict():
    """FLASH_ATTN_KERNEL_FALLBACK must contain a flash_attention_4 entry.

    # AST-only because: importing transformers modules requires torch (not installed).
    """
    d = _extract_dict_assignment(FLASH_UTILS, "FLASH_ATTN_KERNEL_FALLBACK")
    assert "flash_attention_4" in d, (
        f"flash_attention_4 not found in FLASH_ATTN_KERNEL_FALLBACK. Keys: {list(d.keys())}"
    )


# [pr_diff] fail_to_pass
def test_fa4_fallback_value_format():
    """FA4 fallback value must be a kernels-community package with a flash/attn-related name.

    # AST-only because: importing transformers modules requires torch (not installed).
    """
    d = _extract_dict_assignment(FLASH_UTILS, "FLASH_ATTN_KERNEL_FALLBACK")
    val = d.get("flash_attention_4", "")
    assert isinstance(val, str), f"Expected string value, got {type(val)}"
    assert val.startswith("kernels-community/"), (
        f"Expected kernels-community/ prefix, got: {val}"
    )
    pkg = val.split("/", 1)[1].lower()
    assert len(pkg) > 0, "Package name is empty after prefix"
    assert any(tok in pkg for tok in ("flash", "attn", "fa")), (
        f"Package name does not look FA-related: {pkg}"
    )


# [pr_diff] fail_to_pass
def test_fa4_not_skipped_in_loop():
    """The fallback loop in _check_and_adjust_attn_implementation must not skip version 4.

    # AST-only because: calling _check_and_adjust_attn_implementation requires torch,
    # model classes, and GPU-related imports not available in this CPU-only container.
    """
    source = MODELING_UTILS.read_text()
    tree = ast.parse(source)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_check_and_adjust_attn_implementation":
            found = True
            lines = source.splitlines(keepends=True)
            func_src = "".join(lines[node.lineno - 1 : node.end_lineno])
            func_tree = ast.parse(textwrap.dedent(func_src))

            for n in ast.walk(func_tree):
                if isinstance(n, ast.If) and isinstance(n.test, ast.Compare):
                    for comp, val in zip(n.test.ops, n.test.comparators):
                        if (
                            isinstance(comp, ast.Eq)
                            and isinstance(val, ast.Constant)
                            and val.value == 4
                            and len(n.body) == 1
                            and isinstance(n.body[0], ast.Continue)
                        ):
                            raise AssertionError(
                                "Version 4 is still explicitly skipped in the fallback loop"
                            )
            break

    assert found, "_check_and_adjust_attn_implementation not found in modeling_utils.py"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_fa2_fa3_entries_preserved():
    """FA2 and FA3 kernel fallback entries must remain unchanged.

    # AST-only because: importing transformers modules requires torch (not installed).
    """
    d = _extract_dict_assignment(FLASH_UTILS, "FLASH_ATTN_KERNEL_FALLBACK")
    assert d.get("flash_attention_2") == "kernels-community/flash-attn2", (
        f"FA2 entry changed: {d.get('flash_attention_2')}"
    )
    assert d.get("flash_attention_3") == "kernels-community/vllm-flash-attn3", (
        f"FA3 entry changed: {d.get('flash_attention_3')}"
    )


# [pr_diff] pass_to_pass
def test_compat_matrix_has_all_versions():
    """FLASH_ATTENTION_COMPATIBILITY_MATRIX must include versions 2, 3, and 4.

    # AST-only because: importing transformers modules requires torch (not installed).
    """
    keys = _extract_dict_keys(FLASH_UTILS, "FLASH_ATTENTION_COMPATIBILITY_MATRIX")
    for v in (2, 3, 4):
        assert v in keys, (
            f"Version {v} missing from FLASH_ATTENTION_COMPATIBILITY_MATRIX. Keys: {keys}"
        )


# ---------------------------------------------------------------------------
# Repo CI tests (repo_tests) — actual CI commands that should pass
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check"] + MODIFIED_FILES,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_check_copies():
    """Repo's check_copies.py passes (pass_to_pass).

    This validates that # Copied from blocks are consistent across the codebase.
    """
    r = subprocess.run(
        [sys.executable, "utils/check_copies.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_copies.py failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_check_dummies():
    """Repo's check_dummies.py passes (pass_to_pass).

    This validates that dummy objects are correctly defined for optional dependencies.
    """
    r = subprocess.run(
        [sys.executable, "utils/check_dummies.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_dummies.py failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_check_doc_toc():
    """Repo's check_doc_toc.py passes (pass_to_pass).

    This validates that documentation table of contents is correctly structured.
    """
    r = subprocess.run(
        [sys.executable, "utils/check_doc_toc.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_doc_toc.py failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_check_inits():
    """Repo's check_inits.py passes (pass_to_pass).

    This validates that __init__.py files correctly expose public APIs.
    """
    r = subprocess.run(
        [sys.executable, "utils/check_inits.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_inits.py failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:2 @ a269c990e8571d9b9f8adfc1add9472eec3f252d
def test_ruff_check():
    """ruff check passes on the two modified files (CLAUDE.md: run 'make style')."""
    r = subprocess.run(
        [
            sys.executable, "-m", "ruff", "check",
            "src/transformers/modeling_flash_attention_utils.py",
            "src/transformers/modeling_utils.py",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout}\n{r.stderr}"


# [agent_config] pass_to_pass — .github/copilot-instructions.md:15 @ a269c990e8571d9b9f8adfc1add9472eec3f252d
def test_minimal_diff():
    """Diff should touch at most 3 files (copilot-instructions.md: minimize diff size)."""
    diff_output = ""
    for cmd in [
        ["git", "diff", "--stat", "HEAD"],
        ["git", "diff", "--stat", "--cached", "HEAD"],
        ["git", "diff", "--stat", "HEAD~1"],
    ]:
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=10)
        if r.stdout.strip():
            diff_output = r.stdout.strip()
            break

    file_lines = [l for l in diff_output.splitlines() if "|" in l]
    n_files = len(file_lines)
    assert n_files <= 3, f"{n_files} files changed (expected <= 3)"


# [agent_config] pass_to_pass — CLAUDE.md:66 @ a269c990e8571d9b9f8adfc1add9472eec3f252d
def test_no_copied_from_edits():
    """Changes must not modify lines inside a '# Copied from' block.

    CLAUDE.md: 'Do not edit a # Copied from block, as it will be reverted by make fix-repo.'
    """
    diff_text = _get_diff()

    current_file = None
    in_copied_block = False
    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            current_file = line.split(" b/")[-1] if " b/" in line else None
            in_copied_block = False
        elif line.startswith("@@"):
            in_copied_block = False
        elif line.startswith((" ", "+", "-")):
            content = line[1:]
            if "# Copied from" in content:
                in_copied_block = True
            if in_copied_block and line.startswith(("+", "-")) and "# Copied from" not in content:
                assert False, (
                    f"Diff modifies code inside a '# Copied from' block in {current_file}: {line.strip()}"
                )


# [agent_config] pass_to_pass — CLAUDE.md:67 @ a269c990e8571d9b9f8adfc1add9472eec3f252d
def test_no_modular_file_edits():
    """Changed files must not be auto-generated from a modular file.

    CLAUDE.md: 'When a modular file is present, generated files should not be edited
    directly, as changes will be overwritten by make fix-repo.'
    """
    changed = ""
    for cmd in [
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "diff", "--name-only", "--cached", "HEAD"],
        ["git", "diff", "--name-only", "HEAD~1"],
    ]:
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=10)
        if r.stdout.strip():
            changed = r.stdout.strip()
            break

    for filepath in changed.splitlines():
        filepath = filepath.strip()
        if not filepath:
            continue
        p = Path(filepath)
        modular_name = f"modular_{p.name}"
        modular_path = Path(REPO) / p.parent / modular_name
        if modular_path.exists():
            assert False, (
                f"{filepath} appears to be auto-generated (found {p.parent / modular_name}). "
                "Edit the modular file instead."
            )
