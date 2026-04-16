"""
Task: transformers-fa4-kernel-fallback
Repo: huggingface/transformers @ a269c990e8571d9b9f8adfc1add9472eec3f252d
PR:   44797

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import subprocess
import sys
import textwrap
from pathlib import Path

REPO = "/workspace/transformers"
MODIFIED_FILES = [
    "src/transformers/modeling_flash_attention_utils.py",
    "src/transformers/modeling_utils.py",
]


# ---------------------------------------------------------------------------
# Subprocess helper: import flash_attention_utils with mocked torch
# ---------------------------------------------------------------------------

_FLASH_UTILS_IMPORT_SCRIPT = textwrap.dedent("""\
    import sys, types, importlib.util

    class DynaMod(types.ModuleType):
        def __init__(self, name, **kw):
            super().__init__(name)
            for k, v in kw.items():
                setattr(self, k, v)
        def __getattr__(self, name):
            if name.startswith('__') and name.endswith('__'):
                raise AttributeError(name)
            val = DynaMod(f'{self.__name__}.{name}')
            setattr(self, name, val)
            return val
        def __or__(self, other):
            import typing
            return typing.Union[self, other]
        def __ror__(self, other):
            import typing
            return typing.Union[other, self]

    # 1. Fake torch
    torch_mod = DynaMod('torch',
        __path__=['torch'],
        __spec__=importlib.util.spec_from_loader('torch', loader=None),
        __version__='99.0.0',
        __file__='/fake/torch/__init__.py',
    )
    sys.modules['torch'] = torch_mod
    for s in ['nn', 'nn.functional', 'cuda', 'distributed', 'types', '_C', 'autograd',
              'utils', 'utils.data']:
        m = DynaMod(f'torch.{s}', __path__=[f'torch.{s}'], __spec__=None)
        setattr(torch_mod, s.split('.')[-1], m)
        sys.modules[f'torch.{s}'] = m

    # 2. Fake transformers package
    fake_tf = DynaMod('transformers',
                      __path__=['/workspace/transformers/src/transformers'])
    sys.modules['transformers'] = fake_tf

    # 3. Fake transformers.utils
    fake_utils = DynaMod('transformers.utils', __path__=['/fake'])
    for fn in ['is_flash_attn_2_available', 'is_flash_attn_3_available',
               'is_flash_attn_4_available', 'is_torch_cuda_available',
               'is_torch_mlu_available', 'is_torch_npu_available',
               'is_torch_xpu_available']:
        setattr(fake_utils, fn, lambda *a, **kw: False)
    fake_utils.logging = DynaMod('transformers.utils.logging')
    fake_utils.logging.get_logger = lambda *a, **kw: __import__('logging').getLogger('test')
    sys.modules['transformers.utils'] = fake_utils

    # 4. Fake transformers.utils.import_utils
    fake_iu = DynaMod('transformers.utils.import_utils',
                      PACKAGE_DISTRIBUTION_MAPPING={}, is_tracing=lambda: False)
    sys.modules['transformers.utils.import_utils'] = fake_iu
    sys.modules['transformers.integrations'] = DynaMod('transformers.integrations')
    sys.modules['transformers.integrations.npu_flash_attention'] = DynaMod('t.i.npu')
    sys.modules['transformers.integrations.npu_flash_attention'].is_npu_fa2_top_left_aligned_causal_mask = lambda: False

    # 5. Load the actual module file
    spec = importlib.util.spec_from_file_location(
        'transformers.modeling_flash_attention_utils',
        '/workspace/transformers/src/transformers/modeling_flash_attention_utils.py'
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # 6. Output data
    import json
    print(json.dumps({
        'fallback': {str(k): str(v) for k, v in mod.FLASH_ATTN_KERNEL_FALLBACK.items()},
        'compat_keys': sorted(mod.FLASH_ATTENTION_COMPATIBILITY_MATRIX.keys()),
    }))
""")


def _get_flash_attn_data():
    """Import modeling_flash_attention_utils via subprocess and return runtime data."""
    r = subprocess.run(
        [sys.executable, "-c", _FLASH_UTILS_IMPORT_SCRIPT],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Module import failed: {r.stderr}\n{r.stdout}"
    return json.loads(r.stdout.strip())


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

    Tests by importing the module with mocked torch and reading the runtime
    dict value.
    """
    data = _get_flash_attn_data()
    fallback = data["fallback"]
    assert "flash_attention_4" in fallback, (
        f"flash_attention_4 not found in FLASH_ATTN_KERNEL_FALLBACK. Keys: {list(fallback.keys())}"
    )


# [pr_diff] fail_to_pass
def test_fa4_fallback_value_format():
    """FA4 fallback value must be a kernels-community package with a flash/attn-related name.

    Tests by importing the module and checking the runtime value.
    """
    data = _get_flash_attn_data()
    val = data["fallback"].get("flash_attention_4", "")
    assert isinstance(val, str) and len(val) > 0, f"Expected non-empty string, got: {val!r}"
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
    """Every version in FLASH_ATTENTION_COMPATIBILITY_MATRIX must have a kernel fallback entry.

    The fallback loop in _check_and_adjust_attn_implementation iterates over
    FLASH_ATTENTION_COMPATIBILITY_MATRIX. For the loop to actually use kernel
    fallbacks for every supported version, each version must have a corresponding
    entry in FLASH_ATTN_KERNEL_FALLBACK. The bug was that version 4 had no fallback
    entry AND was explicitly skipped in the loop.
    """
    data = _get_flash_attn_data()
    compat_keys = data["compat_keys"]
    fallback = data["fallback"]

    missing = []
    for v in compat_keys:
        key = f"flash_attention_{v}"
        if key not in fallback:
            missing.append(key)

    assert not missing, (
        f"COMPAT_MATRIX versions without fallback entries: {missing}. "
        "Either FLASH_ATTN_KERNEL_FALLBACK lacks entries or the loop still skips these versions."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_fa2_fa3_entries_preserved():
    """FA2 and FA3 kernel fallback entries must remain present and valid.

    Tests by importing the module and checking runtime values match expected format.
    """
    data = _get_flash_attn_data()
    fallback = data["fallback"]
    for key in ["flash_attention_2", "flash_attention_3"]:
        assert key in fallback, f"{key} missing from FLASH_ATTN_KERNEL_FALLBACK"
        val = fallback[key]
        assert isinstance(val, str) and len(val) > 0, f"Invalid value for {key}: {val!r}"
        assert val.startswith("kernels-community/"), f"Invalid format for {key}: {val}"


# [pr_diff] pass_to_pass
def test_compat_matrix_has_all_versions():
    """FLASH_ATTENTION_COMPATIBILITY_MATRIX must include versions 2, 3, and 4.

    Tests by importing the module and reading runtime keys.
    """
    data = _get_flash_attn_data()
    keys = data["compat_keys"]
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


# [repo_tests] pass_to_pass
def test_repo_check_doctest_list():
    """Repo's check_doctest_list.py passes (pass_to_pass).

    This validates that doctest lists are correctly maintained.
    """
    r = subprocess.run(
        [sys.executable, "utils/check_doctest_list.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_doctest_list.py failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_sort_auto_mappings():
    """Repo's sort_auto_mappings.py --check_only passes (pass_to_pass).

    This validates that auto mappings are correctly sorted.
    """
    r = subprocess.run(
        [sys.executable, "utils/sort_auto_mappings.py", "--check_only"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"sort_auto_mappings.py --check_only failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


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
