"""
Task: slime-mla-indexcache-skip-topk
Repo: THUDM/slime @ 6e3699c83ac65c119e755ccec1a14ac87644489f
PR:   1736

skip_topk / next_skip_topk must be initialized unconditionally in __init__,
not only inside `if is_nextn:` (which is inside `if self.use_nsa:`).
The agent edits docker/patch/latest/sglang.patch to fix this.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

The patched code targets sglang's DeepseekV2AttentionMLA which requires torch,
triton, CUDA — none available in this CPU container. Fail-to-pass tests use
subprocess to run scope-aware analysis of the patch control flow rather than
simple string matching.
"""

import subprocess
import pytest
from pathlib import Path

REPO = "/workspace/slime"
PATCH_FILE = Path(REPO) / "docker/patch/latest/sglang.patch"


# ---------------------------------------------------------------------------
# Subprocess script: scope-aware analysis of attribute initialization
# ---------------------------------------------------------------------------

UNCONDITIONAL_INIT_CHECK = r'''
"""Verify self.<attr> is initialized unconditionally in sglang.patch.

Parses the deepseek_v2.py hunks from the patch and traces control flow
scope to ensure the assignment is NOT nested inside `if self.use_nsa:`
or `if is_nextn:` conditional blocks.

The fix requires the initialization to be at method-body level (indent <= 8),
which means it's outside the `if self.use_nsa:` block entirely.
"""
import sys
from pathlib import Path

ATTR = sys.argv[1]
patch = Path("/workspace/slime/docker/patch/latest/sglang.patch").read_text()

# Extract deepseek_v2.py section
dsv2 = ""
for sec in patch.split("diff --git "):
    if "deepseek_v2.py" in sec.split("\n")[0]:
        dsv2 = sec
        break
if not dsv2:
    print("FAIL: deepseek_v2.py not found in patch")
    sys.exit(1)

# Parse into individual hunks — each hunk is a contiguous code region
hunks = []
current = []
for line in dsv2.split("\n"):
    if line.startswith("@@"):
        if current:
            hunks.append(current)
        current = []
        continue
    if line.startswith(("diff ", "index ", "--- ", "+++ ")):
        continue
    if line.startswith("-") and not line.startswith("---"):
        continue  # removed lines not in final code
    if line.startswith("+") and not line.startswith("+++"):
        current.append(("added", line[1:]))
    elif line.startswith(" "):
        current.append(("context", line[1:]))
if current:
    hunks.append(current)

# Search each hunk for self.ATTR = ... in added lines at method-body level
for hunk in hunks:
    for idx, (tag, line) in enumerate(hunk):
        stripped = line.strip()
        if (tag == "added"
            and f"self.{ATTR}" in stripped
            and "=" in stripped
            and "==" not in stripped
            and "offset" not in stripped):

            indent = len(line) - len(line.lstrip())

            # At method-body level (indent <= 8), guaranteed unconditional
            # This means outside the `if self.use_nsa:` block entirely
            if indent <= 8:
                print(f"PASS: self.{ATTR} at indent {indent} — method-body level (unconditional)")
                sys.exit(0)

# If we didn't find any method-body level initialization, FAIL
print(f"FAIL: self.{ATTR} not initialized at method-body level (indent <= 8)")
print(f"       It may be inside `if self.use_nsa:` or `if is_nextn:` conditionals.")
sys.exit(1)
'''


# ---------------------------------------------------------------------------
# Helpers (for pass_to_pass tests)
# ---------------------------------------------------------------------------

def _dsv2_section():
    """Return the raw text of the deepseek_v2.py diff section from sglang.patch."""
    content = PATCH_FILE.read_text()
    marker = "python/sglang/srt/models/deepseek_v2.py"
    for section in content.split("diff --git "):
        if marker in section.split("\n")[0]:
            return section
    return ""


def _dsv2_all_hunk_lines():
    """Return both context and added lines from hunks (strips the diff prefix).

    Removed lines (-) are excluded. Used for pass_to_pass checks that look
    for code present in both base and fixed versions.
    """
    section = _dsv2_section()
    lines = []
    in_hunk = False
    for line in section.split("\n"):
        if line.startswith("@@"):
            in_hunk = True
            continue
        if not in_hunk:
            continue
        if line.startswith("-") and not line.startswith("---"):
            continue
        if line.startswith("+") and not line.startswith("+++"):
            lines.append(line[1:])
        elif line.startswith(" "):
            lines.append(line[1:])
    return lines


def _hunk_text():
    """All non-blank, non-comment hunk lines joined for substring search."""
    return "\n".join(
        l for l in _dsv2_all_hunk_lines()
        if l.strip() and not l.strip().startswith("#")
    )


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_patch_targets_deepseek_v2():
    """Patch file exists and modifies deepseek_v2.py."""
    assert PATCH_FILE.exists(), f"{PATCH_FILE} does not exist"
    content = PATCH_FILE.read_text()
    assert "deepseek_v2.py" in content, "sglang.patch does not modify deepseek_v2.py"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core bug: attrs must not require use_nsa=True
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skip_topk_init_unconditional():
    """self.skip_topk must be initialized unconditionally, not only inside use_nsa/is_nextn.

    Runs a subprocess that parses the patch hunks and traces the control flow
    scope of the assignment. On the base commit, skip_topk is inside
    `if is_nextn:` (inside `if self.use_nsa:`) at indent 16 — this test fails.
    After the fix, it's at method-body level (indent 8) — this test passes.
    """
    r = subprocess.run(
        ["python3", "-c", UNCONDITIONAL_INIT_CHECK, "skip_topk"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert "PASS" in r.stdout, (
        f"self.skip_topk not initialized unconditionally — non-NSA MLA models "
        f"will raise AttributeError.\nstdout: {r.stdout.strip()}\nstderr: {r.stderr.strip()}"
    )


# [pr_diff] fail_to_pass
def test_next_skip_topk_init_unconditional():
    """self.next_skip_topk must be initialized unconditionally.

    Same bug as skip_topk: only set inside `if is_nextn:` (inside `if self.use_nsa:`),
    so non-NSA MLA models raise AttributeError in forward_absorb_prepare.
    """
    r = subprocess.run(
        ["python3", "-c", UNCONDITIONAL_INIT_CHECK, "next_skip_topk"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert "PASS" in r.stdout, (
        f"self.next_skip_topk not initialized unconditionally — non-NSA MLA models "
        f"will raise AttributeError.\nstdout: {r.stdout.strip()}\nstderr: {r.stderr.strip()}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression: topk caching infrastructure must survive
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_config_attrs_preserved():
    """index_topk_freq, index_topk_pattern, index_skip_topk_offset still configured in NSA branch."""
    text = _hunk_text()
    required = ["index_topk_freq", "index_topk_pattern", "index_skip_topk_offset"]
    missing = [r for r in required if r not in text]
    assert not missing, (
        f"Config attributes missing from sglang.patch: {', '.join(missing)}. "
        "The NSA branch must still configure topk caching parameters."
    )


# [pr_diff] pass_to_pass
def test_forward_skip_logic_preserved():
    """forward_absorb_prepare conditionally skips indexer via skip_topk with prev_topk_indices fallback."""
    text = _hunk_text()
    assert "prev_topk_indices" in text, (
        "prev_topk_indices not found in patch — cross-layer topk caching broken"
    )
    has_conditional = (
        "if not self.skip_topk" in text
        or "if self.skip_topk" in text
    )
    assert has_conditional, (
        "No conditional skip logic using skip_topk in sglang.patch forward path"
    )


# [pr_diff] pass_to_pass
def test_return_includes_topk_indices():
    """forward_absorb_prepare returns topk_indices for cross-layer caching."""
    lines = _dsv2_all_hunk_lines()
    has_tuple_return = any(
        (l.strip().startswith("return output,") and "topk" in l)
        or l.strip().startswith("return output, None")
        for l in lines
    )
    assert has_tuple_return, (
        "forward_absorb_prepare must return a (output, topk_indices) tuple "
        "for cross-layer topk index caching"
    )
    text = _hunk_text()
    assert "next_skip_topk" in text, (
        "next_skip_topk logic missing from patch return path"
    )


# [pr_diff] pass_to_pass
def test_decoder_layer_threads_topk():
    """DecoderLayer returns 3-tuple and DeepseekV2Model unpacks topk_indices across layers."""
    lines = _dsv2_all_hunk_lines()
    has_layer_return = any(
        l.strip().startswith("return ")
        and "hidden_states" in l
        and "residual" in l
        and "topk" in l
        for l in lines
    )
    assert has_layer_return, (
        "DeepseekV2DecoderLayer does not return 3-tuple (hidden_states, residual, topk_indices)"
    )
    has_unpack = any(
        "topk" in l and "residual" in l and "hidden_states" in l and "=" in l
        and l.strip().startswith(("hidden_states", "topk"))
        for l in lines
    )
    assert has_unpack, (
        "DeepseekV2Model does not unpack topk_indices from layer call"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — verify repo CI/CD checks pass on base AND fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_python_syntax_valid():
    """All Python files have valid syntax (pass_to_pass)."""
    import py_compile
    import os

    errors = []
    for root, dirs, files in os.walk(REPO):
        # Skip hidden directories and common non-source directories
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "build", "dist")]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    py_compile.compile(filepath, doraise=True)
                except py_compile.PyCompileError as e:
                    errors.append(f"{filepath}: {e}")

    assert not errors, f"Python syntax errors found:\n" + "\n".join(errors[:10])


# [repo_tests] pass_to_pass
def test_repo_package_importable():
    """The slime package is importable after installation (pass_to_pass)."""
    # This verifies basic package structure is intact
    r = subprocess.run(
        ["python3", "-c", "import slime; print('slime imported successfully')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to import slime package:\n{r.stderr}"
    assert "slime imported successfully" in r.stdout, "slime package import did not succeed"


# [repo_tests] pass_to_pass
def test_repo_patch_file_valid():
    """The sglang.patch file exists and is valid (pass_to_pass)."""
    assert PATCH_FILE.exists(), f"Patch file {PATCH_FILE} does not exist"

    # Check that the patch file can be parsed as a unified diff
    content = PATCH_FILE.read_text()

    # Verify basic patch structure
    assert "diff --git" in content, "Patch file missing diff headers"
    assert "---" in content, "Patch file missing --- markers"
    assert "+++" in content, "Patch file missing +++ markers"

    # Check that deepseek_v2.py is mentioned (the target of this fix)
    assert "deepseek_v2.py" in content, "Patch file does not mention deepseek_v2.py"


# [repo_tests] pass_to_pass
def test_repo_pyproject_toml_valid():
    """pyproject.toml is valid TOML (pass_to_pass)."""
    import tomllib

    pyproject_path = Path(REPO) / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml does not exist"

    content = pyproject_path.read_text()
    try:
        config = tomllib.loads(content)
    except Exception as e:
        assert False, f"Invalid TOML in pyproject.toml: {e}"

    # Basic structure checks
    assert "build-system" in config, "Missing build-system section"
    assert "tool" in config, "Missing tool section"
    assert "pytest" in config.get("tool", {}), "Missing pytest configuration"


# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff linter passes on slime/ (pass_to_pass).

    This runs the repo's configured ruff check as specified in pyproject.toml.
    The ruff tool is installed and run via subprocess to match CI behavior.
    """
    r = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Even if pip outputs warnings, we proceed

    r = subprocess.run(
        ["ruff", "check", "slime/", "--config", "pyproject.toml"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_isort_check():
    """Repo's import sorting (isort) passes on slime/ (pass_to_pass).

    This runs isort --check-only to verify imports are sorted according to
    the project's pyproject.toml configuration.
    """
    r = subprocess.run(
        ["pip", "install", "isort", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )

    r = subprocess.run(
        ["isort", "--check-only", "slime/", "--settings-file", "pyproject.toml"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_no_syntax_errors():
    """All Python files in slime/ have valid syntax (pass_to_pass).

    Uses py_compile to verify all .py files can be parsed without errors.
    This is a lightweight check that catches basic syntax issues.
    """
    import py_compile
    import os

    errors = []
    slime_path = Path(REPO) / "slime"
    for root, dirs, files in os.walk(slime_path):
        # Skip hidden directories and common non-source directories
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "build", "dist")]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    py_compile.compile(filepath, doraise=True)
                except py_compile.PyCompileError as e:
                    errors.append(f"{filepath}: {e}")

    assert not errors, f"Python syntax errors found in slime/:\n" + "\n".join(errors[:10])
