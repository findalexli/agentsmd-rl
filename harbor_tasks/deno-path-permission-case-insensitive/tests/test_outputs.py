"""
Task: deno-path-permission-case-insensitive
Repo: deno @ 7c57830506e4ded88a7bfee2a03a5e0530787fbe
PR:   33073

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: The behavioral change (case-insensitive permission matching) only
manifests on Windows (cfg!(windows)). Since tests run on Linux, we verify
the structural correctness of the fix: the comparison_path function, the
cmp_path field, and that all comparison/hashing/ordering operations use
the new cmp_path field instead of the raw path.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/deno"
LIB_RS = f"{REPO}/runtime/permissions/lib.rs"


def _read_lib_rs():
    return Path(LIB_RS).read_text()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core structural tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_comparison_path_function():
    """comparison_path() function exists and handles both Windows and non-Windows."""
    src = _read_lib_rs()

    # Function must exist with the correct signature
    assert re.search(
        r"fn\s+comparison_path\s*\(\s*path\s*:\s*&Path\s*\)\s*->\s*PathBuf",
        src,
    ), "comparison_path function with correct signature not found"

    # Must handle Windows case (cfg!(windows) with lowercase)
    assert re.search(
        r"cfg!\s*\(\s*windows\s*\)", src
    ), "comparison_path must check cfg!(windows)"

    # Must have the ascii_lowercase branch for Windows
    assert re.search(
        r"to_ascii_lowercase\s*\(\s*\)", src
    ), "comparison_path must call to_ascii_lowercase() for Windows paths"

    # Must have the non-Windows fallback (to_path_buf)
    fn_match = re.search(
        r"fn\s+comparison_path.*?\n((?:.*\n)*?)\s*\}", src
    )
    assert fn_match, "Could not extract comparison_path body"
    body = fn_match.group(1)
    assert "to_path_buf" in body, (
        "comparison_path must fall back to to_path_buf() on non-Windows"
    )


# [pr_diff] fail_to_pass
def test_cmp_path_field_in_path_query_descriptor():
    """PathQueryDescriptor struct has a cmp_path: PathBuf field."""
    src = _read_lib_rs()

    # Find the PathQueryDescriptor struct definition and check for cmp_path field
    struct_match = re.search(
        r"pub\s+struct\s+PathQueryDescriptor\s*<[^>]*>\s*\{(.*?)\}",
        src,
        re.DOTALL,
    )
    assert struct_match, "PathQueryDescriptor struct not found"
    body = struct_match.group(1)
    assert re.search(r"cmp_path\s*:\s*PathBuf", body), (
        "PathQueryDescriptor must have cmp_path: PathBuf field"
    )


# [pr_diff] fail_to_pass
def test_cmp_path_field_in_path_descriptor():
    """PathDescriptor struct has a cmp_path: PathBuf field."""
    src = _read_lib_rs()

    # Find the PathDescriptor struct (not PathQueryDescriptor)
    struct_match = re.search(
        r"pub\s+struct\s+PathDescriptor\s*\{(.*?)\}",
        src,
        re.DOTALL,
    )
    assert struct_match, "PathDescriptor struct not found"
    body = struct_match.group(1)
    assert re.search(r"cmp_path\s*:\s*PathBuf", body), (
        "PathDescriptor must have cmp_path: PathBuf field"
    )


# [pr_diff] fail_to_pass
def test_equality_uses_cmp_path():
    """All PartialEq impls compare cmp_path, not path directly."""
    src = _read_lib_rs()

    # Find all PartialEq impl blocks for PathQueryDescriptor and PathDescriptor
    # There are 3 PartialEq impls:
    # 1. PartialEq for PathQueryDescriptor (self eq)
    # 2. PartialEq<PathDescriptor> for PathQueryDescriptor (cross eq)
    # 3. PartialEq for PathDescriptor (self eq)
    eq_impls = re.findall(
        r"impl\s+PartialEq(?:<\w+>)?\s+for\s+Path(?:Query)?Descriptor.*?\{.*?fn\s+eq\s*\(.*?\)\s*->\s*bool\s*\{(.*?)\}",
        src,
        re.DOTALL,
    )
    assert len(eq_impls) >= 3, (
        f"Expected at least 3 PartialEq impls for path descriptors, found {len(eq_impls)}"
    )

    for i, body in enumerate(eq_impls):
        assert "cmp_path" in body, (
            f"PartialEq impl #{i+1} must use cmp_path for comparison"
        )
        # Must NOT use self.path == other.path (the old buggy pattern)
        stripped = body.strip()
        assert not re.match(
            r"^\s*self\.path\s*==\s*other\.path\s*$", stripped
        ), f"PartialEq impl #{i+1} still uses self.path == other.path (unfixed)"


# [pr_diff] fail_to_pass
def test_hash_uses_cmp_path():
    """Hash impl for PathDescriptor hashes cmp_path, not path."""
    src = _read_lib_rs()

    hash_match = re.search(
        r"impl\s+Hash\s+for\s+PathDescriptor\s*\{.*?fn\s+hash\s*<[^>]*>\s*\([^)]*\)\s*\{(.*?)\}",
        src,
        re.DOTALL,
    )
    assert hash_match, "Hash impl for PathDescriptor not found"
    body = hash_match.group(1)
    assert "cmp_path" in body, (
        "Hash impl must hash cmp_path, not path"
    )
    assert "self.path.hash" not in body.replace("cmp_path", ""), (
        "Hash impl still hashes self.path directly"
    )


# [pr_diff] fail_to_pass
def test_starts_with_uses_cmp_path():
    """Both starts_with methods use cmp_path for prefix checking."""
    src = _read_lib_rs()

    # Find starts_with method bodies in both descriptor types
    starts_with_methods = re.findall(
        r"pub\s+fn\s+starts_with\s*\([^)]*\)\s*->\s*bool\s*\{(.*?)\}",
        src,
        re.DOTALL,
    )
    assert len(starts_with_methods) >= 2, (
        f"Expected at least 2 starts_with methods, found {len(starts_with_methods)}"
    )

    for i, body in enumerate(starts_with_methods):
        assert "cmp_path" in body, (
            f"starts_with method #{i+1} must use cmp_path"
        )


# [pr_diff] fail_to_pass
def test_ordering_uses_cmp_path():
    """cmp_allow_allow and cmp_allow_deny use cmp_path for ordering."""
    src = _read_lib_rs()

    for fn_name in ("cmp_allow_allow", "cmp_allow_deny"):
        fn_match = re.search(
            rf"fn\s+{fn_name}\s*\([^)]*\)\s*->\s*Ordering\s*\{{(.*?)\n\s*\}}",
            src,
            re.DOTALL,
        )
        assert fn_match, f"{fn_name} method not found"
        body = fn_match.group(1)

        # Must reference cmp_path for comparisons
        assert "cmp_path" in body, (
            f"{fn_name} must use cmp_path for ordering comparisons"
        )

        # Must NOT use self.path or other.path for direct comparison
        path_refs = re.findall(r"(?:self|other)\.path\b(?!_buf)", body)
        cmp_refs = re.findall(r"(?:self|other)\.cmp_path", body)
        assert len(cmp_refs) > 0, f"{fn_name} has no cmp_path references"
        assert len(path_refs) == 0, (
            f"{fn_name} still uses raw .path for comparison: {path_refs}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub_comparison_path():
    """comparison_path function has real logic, not just a pass-through."""
    src = _read_lib_rs()

    fn_match = re.search(
        r"fn\s+comparison_path\s*\(.*?\)\s*->\s*PathBuf\s*\{(.*?)\n\}",
        src,
        re.DOTALL,
    )
    assert fn_match, "comparison_path function not found"
    body = fn_match.group(1).strip()

    # Must have at least a conditional and two branches
    lines = [l.strip() for l in body.splitlines() if l.strip()]
    assert len(lines) >= 3, (
        f"comparison_path body too short ({len(lines)} lines) — likely a stub"
    )
    assert any("cfg!" in l or "if " in l for l in lines), (
        "comparison_path must contain a platform conditional"
    )
