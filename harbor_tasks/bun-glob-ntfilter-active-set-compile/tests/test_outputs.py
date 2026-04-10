"""
Task: bun-glob-ntfilter-active-set-compile
Repo: oven-sh/bun @ 39094877abb3e74557d3975dd015ee677220eb35
PR:   28543

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Tests use subprocess.run() to execute Python analysis scripts against the
Zig source. Zig cannot be compiled in the test container (no zig compiler,
no full bun build toolchain), so behavioral tests verify the fix by running
code that extracts and validates the relevant source region.
"""

import subprocess
import json
import re
from pathlib import Path

REPO = "/workspace/bun"
TARGET = Path(REPO) / "src/glob/GlobWalker.zig"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python analysis script in an isolated subprocess."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _extract_callsite(before: int = 20, after: int = 15) -> list[str]:
    """Extract setNameFilter call-site lines via subprocess.

    Finds the iterator.setNameFilter(...) call (not the method definition
    on DirIter) and returns stripped lines in a window around it.
    """
    script = (
        "import json, sys\n"
        "from pathlib import Path\n"
        f"code = Path(r'{TARGET}').read_text()\n"
        "lines = code.splitlines()\n"
        "best = None\n"
        "for i, line in enumerate(lines):\n"
        "    if 'iterator.setNameFilter' in line.strip():\n"
        "        best = i\n"
        "        break\n"
        "if best is None:\n"
        "    for i, line in enumerate(lines):\n"
        "        if 'computeNtFilter' in line and 'fn ' not in line:\n"
        "            for j in range(max(0,i-15), min(len(lines),i+15)):\n"
        "                if 'setNameFilter' in lines[j] and 'fn ' not in lines[j] and '@hasDecl' not in lines[j]:\n"
        "                    best = j\n"
        "                    break\n"
        "            if best is not None:\n"
        "                break\n"
        "if best is None:\n"
        "    sys.exit(1)\n"
        f"start = max(0, best - {before})\n"
        f"end = min(len(lines), best + {after})\n"
        "block = [lines[i].strip() for i in range(start, end)]\n"
        "print(json.dumps(block))\n"
    )
    r = _run_py(script)
    assert r.returncode == 0, f"Callsite extraction failed: {r.stderr}"
    return json.loads(r.stdout.strip())


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


def test_source_file_exists_balanced_braces():
    """GlobWalker.zig exists and has roughly balanced braces."""
    r = _run_py(
        "from pathlib import Path\n"
        f"code = Path(r'{TARGET}').read_text()\n"
        "assert len(code) > 1000, 'File appears truncated or empty'\n"
        "opens = code.count('{')\n"
        "closes = code.count('}')\n"
        "assert abs(opens - closes) <= 5, f'Unbalanced braces: {opens} open, {closes} close'\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core fix verification
# ---------------------------------------------------------------------------


def test_buggy_component_idx_removed():
    """The broken computeNtFilter(component_idx) call is removed from source."""
    r = _run_py(
        "from pathlib import Path\n"
        f"code = Path(r'{TARGET}').read_text()\n"
        "stripped = []\n"
        "for line in code.splitlines():\n"
        "    idx = line.find('//')\n"
        "    stripped.append(line[:idx] if idx >= 0 else line)\n"
        "text = chr(10).join(stripped)\n"
        "assert 'computeNtFilter(component_idx)' not in text, (\n"
        "    \"Still references undeclared 'component_idx' variable\"\n"
        ")\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_fix_uses_active_bitset():
    """Fix derives component index from the active BitSet near setNameFilter."""
    lines = _extract_callsite(before=6, after=3)
    block = "\n".join(lines)
    assert block, "setNameFilter call site not found in source"
    assert re.search(r"\bactive\.\w+\(", block), (
        "No BitSet method call on 'active' near setNameFilter - "
        "fix must derive component index from active BitSet "
        "(e.g. active.findFirstSet(), active.count())"
    )


def test_multi_active_conditional():
    """Fix checks active.count() and uses null when multiple components active."""
    lines = _extract_callsite(before=10, after=5)
    block = "\n".join(lines)
    assert block, "setNameFilter call site not found in source"
    assert re.search(r"\.count\(\)", block), (
        "No .count() check on active set - fix must check if multiple "
        "components are active to decide whether to apply the NT filter"
    )
    assert "null" in block, (
        "No null fallback - when multiple components are active, "
        "setNameFilter must receive null to skip single-component filtering"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) - regression checks
# ---------------------------------------------------------------------------


def test_set_name_filter_preserved():
    """setNameFilter call still exists in the Windows block."""
    r = _run_py(
        "from pathlib import Path\n"
        f"code = Path(r'{TARGET}').read_text()\n"
        "found = any('setNameFilter' in l for l in code.splitlines() if l.strip())\n"
        "assert found, 'setNameFilter call was removed entirely'\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_compute_nt_filter_function_preserved():
    """computeNtFilter function definition still exists with u32 parameter."""
    r = _run_py(
        "from pathlib import Path\n"
        f"code = Path(r'{TARGET}').read_text()\n"
        "assert 'fn computeNtFilter' in code, 'computeNtFilter function was removed'\n"
        "idx = code.index('fn computeNtFilter')\n"
        "sig = code[idx:idx+200]\n"
        "assert 'u32' in sig, 'computeNtFilter signature changed - missing u32 param'\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_compute_nt_filter_still_called():
    """computeNtFilter is called (not just defined) near setNameFilter."""
    r = _run_py(
        "from pathlib import Path\n"
        f"code = Path(r'{TARGET}').read_text()\n"
        "lines = code.splitlines()\n"
        "set_idx = None\n"
        "call_idx = None\n"
        "for i, line in enumerate(lines):\n"
        "    s = line.strip()\n"
        "    if 'setNameFilter' in s:\n"
        "        set_idx = i\n"
        "    if 'computeNtFilter' in s and 'fn ' not in s:\n"
        "        call_idx = i\n"
        "assert set_idx is not None, 'setNameFilter not found'\n"
        "assert call_idx is not None, 'computeNtFilter never called'\n"
        "assert abs(set_idx - call_idx) <= 25, 'computeNtFilter call too far from setNameFilter'\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI/CD equivalent validation
# Container lacks bun/zig toolchains, using npx-based CI commands
# ---------------------------------------------------------------------------


def test_repo_oxlint_js():
    """JavaScript/TypeScript linting passes with oxlint (pass_to_pass).

    Mirrors 'bun lint' CI check using oxlint on src/js directory.
    """
    r = subprocess.run(
        ["npx", "oxlint", "src/js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # oxlint returns 0 when no errors found (warnings are OK)
    assert r.returncode == 0, f"oxlint found errors:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_prettier_check_scripts():
    """Scripts directory formatting check passes with prettier (pass_to_pass).

    Mirrors CI formatting check for scripts directory.
    """
    r = subprocess.run(
        ["npx", "prettier", "--check", "scripts/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"prettier check failed for scripts/:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"




def test_repo_prettier_check_docs():
    """Docs directory formatting check passes with prettier (pass_to_pass).

    Mirrors CI formatting check for docs directory.
    """
    r = subprocess.run(
        ["npx", "prettier", "--check", "docs/", "--ignore-unknown"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"prettier check failed for docs/:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_prettier_check_glob_tests():
    """Glob-related test files formatting check passes with prettier (pass_to_pass).

    Mirrors CI formatting check for glob test files that exercise GlobWalker code.
    """
    r = subprocess.run(
        ["npx", "prettier", "--check", "test/js/node/fs/glob.test.ts", "test/js/node/path/matches-glob.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"prettier check failed for glob test files:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"

def test_repo_git_status_clean():
    """Git repository is in a clean state (pass_to_pass).

    Verifies that the repo was checked out properly without uncommitted changes
    except for the expected fix file (src/glob/GlobWalker.zig).
    """
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
    # Allow for the presence of test files being mounted and the fix file
    # Filter out expected modified files (GlobWalker.zig is the fix target)
    modified_files = [line for line in r.stdout.splitlines() if line.startswith(" M")]
    unexpected = [f for f in modified_files if "GlobWalker.zig" not in f and not f.startswith(" M test/")]
    assert len(unexpected) == 0, f"Unexpected modified source files: {unexpected}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------


def test_no_std_usage_near_fix():
    """No std.* API usage near the fix (use bun.* instead per src/CLAUDE.md)."""
    lines = _extract_callsite(before=15, after=10)
    assert lines, "setNameFilter call site not found"
    for line in lines:
        if line and "std." in line and "@import" not in line:
            raise AssertionError(f"std.* usage near fix: {line}")


def test_no_inline_import_near_fix():
    """No inline @import near the fix (per src/CLAUDE.md)."""
    lines = _extract_callsite(before=15, after=10)
    assert lines, "setNameFilter call site not found"
    for line in lines:
        if line and "@import" in line:
            raise AssertionError(f"Inline @import near fix: {line}")
