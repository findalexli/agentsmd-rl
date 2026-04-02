"""
Task: transformers-flash-attn-version-compat
Repo: huggingface/transformers @ b0bba2d832f3cfd94b339a407f2b3e5b90ce3499

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import importlib
import sys
import warnings
from types import ModuleType

REPO = "/repo"


def _clear_flash_attn_state():
    """Remove all flash_attn modules and clear lru_cache entries."""
    for mod in list(sys.modules):
        if "flash_attn" in mod:
            del sys.modules[mod]
    import transformers.utils.import_utils as iu

    importlib.reload(iu)
    for name in dir(iu):
        obj = getattr(iu, name, None)
        if callable(obj) and hasattr(obj, "cache_clear"):
            try:
                obj.cache_clear()
            except Exception:
                pass
    return iu


def _inject_flash_attn(version_str):
    """Inject a fake flash_attn module with the given version and reload."""
    from importlib.machinery import ModuleSpec

    for mod in list(sys.modules):
        if "flash_attn" in mod:
            del sys.modules[mod]
    fake_fa = ModuleType("flash_attn")
    fake_fa.__version__ = version_str
    fake_fa.__spec__ = ModuleSpec("flash_attn", None)
    sys.modules["flash_attn"] = fake_fa
    fake_cuda = ModuleType("flash_attn_2_cuda")
    fake_cuda.__spec__ = ModuleSpec("flash_attn_2_cuda", None)
    sys.modules["flash_attn_2_cuda"] = fake_cuda
    import transformers.utils.import_utils as iu

    importlib.reload(iu)
    # Ensure the fake package appears in the distribution mapping so
    # is_flash_attn_greater_or_equal can look it up.
    iu.PACKAGE_DISTRIBUTION_MAPPING.setdefault("flash_attn", ["flash-attn"])
    for name in dir(iu):
        obj = getattr(iu, name, None)
        if callable(obj) and hasattr(obj, "cache_clear"):
            try:
                obj.cache_clear()
            except Exception:
                pass
    return iu


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_valid():
    """Modified files parse without syntax errors."""
    import py_compile

    for f in [
        f"{REPO}/src/transformers/utils/import_utils.py",
        f"{REPO}/src/transformers/utils/__init__.py",
    ]:
        py_compile.compile(f, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_function_importable():
    """is_flash_attn_greater_or_equal_2_10 is importable from transformers.utils."""
    from transformers.utils import is_flash_attn_greater_or_equal_2_10

    assert callable(is_flash_attn_greater_or_equal_2_10)


# [pr_diff] fail_to_pass
def test_delegation_with_versions():
    """Function delegates to real version check across multiple versions."""
    cases = [
        ("2.11.0", True),
        ("2.1.0", True),  # 2.1.0 == 2.10 in semver
        ("2.5.0", True),
        ("2.0.0", False),
        ("1.9.5", False),
        ("2.0.9", False),
    ]
    for version, expected in cases:
        iu = _inject_flash_attn(version)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = iu.is_flash_attn_greater_or_equal_2_10()
        assert isinstance(result, bool), f"v{version}: expected bool, got {type(result)}"
        assert result == expected, f"v{version}: expected {expected}, got {result}"


# [pr_diff] fail_to_pass
def test_returns_false_without_flash_attn():
    """Returns False (bool) when flash_attn is not installed at all."""
    iu = _clear_flash_attn_state()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = iu.is_flash_attn_greater_or_equal_2_10()
    assert isinstance(result, bool), f"Expected bool, got {type(result)}"
    assert result is False, f"Expected False without flash_attn, got {result}"


# [pr_diff] fail_to_pass
def test_deprecation_warning_emitted():
    """Function emits a FutureWarning or DeprecationWarning on call."""
    iu = _clear_flash_attn_state()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        iu.is_flash_attn_greater_or_equal_2_10()
        dep = [
            x
            for x in w
            if issubclass(x.category, (FutureWarning, DeprecationWarning))
        ]
        assert len(dep) >= 1, (
            f"Expected deprecation warning, got: {[x.category.__name__ for x in w]}"
        )
        msg = str(dep[0].message).lower()
        assert any(kw in msg for kw in ("deprecat", "removed", "use ")), (
            f"Warning doesn't mention deprecation/replacement: {msg}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_existing_version_check_works():
    """is_flash_attn_greater_or_equal still works and returns bool."""
    from transformers.utils import is_flash_attn_greater_or_equal

    result = is_flash_attn_greater_or_equal("2.1.0")
    assert isinstance(result, bool), f"Expected bool, got {type(result)}"


# [pr_diff] pass_to_pass
def test_utils_core_exports():
    """Core utility functions still importable from transformers.utils."""
    from transformers.utils import is_flash_attn_2_available, is_torch_available

    assert callable(is_torch_available)
    assert callable(is_flash_attn_2_available)


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from agent config files
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — .ai/skills/add-or-fix-type-checking/SKILL.md:185-186
def test_no_bare_type_ignore():
    """Any # type: ignore added in the diff must include a specific error code."""
    import re
    import subprocess

    BASE = "b0bba2d832f3cfd94b339a407f2b3e5b90ce3499"
    r = subprocess.run(
        [
            "git", "diff", BASE, "--",
            "src/transformers/utils/import_utils.py",
            "src/transformers/utils/__init__.py",
        ],
        cwd=REPO, capture_output=True, text=True,
    )
    added_lines = [
        l for l in r.stdout.splitlines()
        if l.startswith("+") and not l.startswith("+++")
    ]
    for line in added_lines:
        if "# type: ignore" in line and not re.search(r"# type: ignore\[", line):
            assert False, f"Bare '# type: ignore' without error code: {line.strip()}"
