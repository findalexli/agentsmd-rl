"""
Task: bun-build-make-ccnopch-cxx-implicitdepend
Repo: oven-sh/bun @ 485ec522a22b469b336aece8276b507a71665a87
PR:   28858

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/bun"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cc_implicit_dep_outputs():
    """cc() calls in compileC pass depOutputs as implicitInputs, not orderOnlyInputs."""
    r = subprocess.run(
        ["python3", "-c", """
import re
src = open('/workspace/bun/scripts/build/bun.ts').read()

# Find the compileC lambda and the cc() call within it.
# On base: cc(n, cfg, src, { flags: cFlagsFull, orderOnlyInputs: depOrderOnly })
# On fix:  cc(n, cfg, src, { ..., implicitInputs: depOutputs, orderOnlyInputs: codegenOrderOnly })
m = re.search(r'const compileC.*?cc\\(n,.*?\\)', src, re.DOTALL)
assert m, "compileC function with cc() call not found in bun.ts"
cc_block = m.group()

# The cc() call must include implicitInputs referencing depOutputs
assert re.search(r'implicitInputs[:\\s]+depOutputs', cc_block), (
    "cc() must pass depOutputs as implicitInputs.\\n"
    f"Found in compileC: ...{cc_block[-200:]}"
)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_nopch_cxx_implicit_dep_outputs():
    """No-PCH cxx path in bun.ts sets opts.implicitInputs = depOutputs."""
    r = subprocess.run(
        ["python3", "-c", """
src = open('/workspace/bun/scripts/build/bun.ts').read()

# The no-PCH else branch must assign opts.implicitInputs = depOutputs.
# On base: only opts.orderOnlyInputs = depOrderOnly  (no implicitInputs)
# On fix:  opts.implicitInputs = depOutputs; opts.orderOnlyInputs = codegenOrderOnly
assert 'opts.implicitInputs = depOutputs' in src, (
    "No-PCH cxx path must set opts.implicitInputs = depOutputs"
)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_codegen_separated_from_dep_outputs():
    """depOutputs and codegen.cppAll are not combined into one order-only variable."""
    r = subprocess.run(
        ["python3", "-c", """
import re
src = open('/workspace/bun/scripts/build/bun.ts').read()

# On base: const depOrderOnly = [...depOutputs, ...codegen.cppAll]
# On fix:  const codegenOrderOnly = codegen.cppAll  (depOutputs NOT mixed in)
mixed = re.search(
    r'const\\s+\\w+\\s*=\\s*\\[.*?depOutputs.*?codegen\\.cppAll.*?\\]',
    src, re.DOTALL
)
assert not mixed, (
    "depOutputs must not be combined with codegen.cppAll in one array. "
    f"Found: {mixed.group()[:120] if mixed else ''}"
)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — CLAUDE.md documentation must match code
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — scripts/build/CLAUDE.md:229 @ 485ec522
def test_claude_md_dep_strategy_updated():
    """CLAUDE.md Gotchas documents cc and no-PCH cxx using implicit deps on depOutputs."""
    r = subprocess.run(
        ["python3", "-c", """
import re
src = open('/workspace/bun/scripts/build/CLAUDE.md').read()

# Base has: "cxx needs order-only dep on `depOutputs`"
# Fix has:  "PCH, cc, and no-PCH cxx need implicit dep on `depOutputs`"
old_guidance = re.search(r'cxx needs order-only dep on.*depOutputs', src)
assert not old_guidance, (
    "CLAUDE.md must NOT say 'cxx needs order-only dep on depOutputs' -- "
    "the fix changes cc/no-PCH cxx to use implicit deps"
)

# Verify the new guidance mentions cc needing implicit dep
assert re.search(r'cc.*need implicit dep', src), (
    "CLAUDE.md Gotchas must state that cc needs implicit dep on depOutputs"
)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compile_opts_has_both_input_types():
    """compile.ts CompileOpts interface retains both implicitInputs and orderOnlyInputs."""
    src = Path(f"{REPO}/scripts/build/compile.ts").read_text()
    assert "implicitInputs" in src, "CompileOpts must have implicitInputs field"
    assert "orderOnlyInputs" in src, "CompileOpts must have orderOnlyInputs field"


# [static] pass_to_pass
def test_bun_ts_pch_implicit_deps():
    """PCH still uses implicit deps on depOutputs (unchanged across base and fix)."""
    src = Path(f"{REPO}/scripts/build/bun.ts").read_text()
    assert "PCH" in src and "implicit dep" in src, \
        "bun.ts must reference PCH's implicit dep on depOutputs in comments"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo's own CI/CD checks
# These ensure the fix doesn't break existing repo functionality
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — Build scripts exist and have content
def test_repo_build_scripts_exist():
    """Build scripts exist and are non-empty (pass_to_pass)."""
    bun_ts = Path(f"{REPO}/scripts/build/bun.ts")
    compile_ts = Path(f"{REPO}/scripts/build/compile.ts")
    claude_md = Path(f"{REPO}/scripts/build/CLAUDE.md")

    assert bun_ts.exists(), "bun.ts must exist"
    assert compile_ts.exists(), "compile.ts must exist"
    assert claude_md.exists(), "CLAUDE.md must exist"

    assert len(bun_ts.read_text()) > 1000, "bun.ts must have substantial content"
    assert len(compile_ts.read_text()) > 1000, "compile.ts must have substantial content"
    assert len(claude_md.read_text()) > 500, "CLAUDE.md must have substantial content"


# [repo_tests] pass_to_pass — CLAUDE.md documentation structure
def test_repo_claude_md_structure():
    """CLAUDE.md has expected sections (pass_to_pass)."""
    claude_md = Path(f"{REPO}/scripts/build/CLAUDE.md").read_text()

    # Check for key documentation concepts that should exist in any version
    assert "Ninja" in claude_md, "CLAUDE.md must reference Ninja"
    assert "implicit" in claude_md, "CLAUDE.md must document implicit inputs"
    assert "order-only" in claude_md, "CLAUDE.md must document order-only inputs"
    assert "PCH" in claude_md, "CLAUDE.md must document PCH"
    assert "depOutputs" in claude_md, "CLAUDE.md must reference depOutputs"


# [repo_tests] pass_to_pass — Build scripts have key functions
def test_repo_build_scripts_structure():
    """Build scripts have expected functions and interfaces (pass_to_pass)."""
    bun_ts = Path(f"{REPO}/scripts/build/bun.ts").read_text()
    compile_ts = Path(f"{REPO}/scripts/build/compile.ts").read_text()

    # bun.ts should have key functions
    assert "compileC" in bun_ts, "bun.ts must have compileC function"
    assert "function cc(" in compile_ts or "const cc" in compile_ts, "compile.ts must have cc function"
    assert "interface CompileOpts" in compile_ts, "compile.ts must have CompileOpts interface"

    # compile.ts should have key rules
    assert 'n.rule("cxx"' in compile_ts, "compile.ts must define cxx rule"
    assert 'n.rule("cc"' in compile_ts, "compile.ts must define cc rule"
    assert 'n.rule("pch"' in compile_ts, "compile.ts must define pch rule"


# [repo_tests] pass_to_pass — Banned words check (simplified)
def test_repo_banned_words():
    """Build scripts don't contain obviously banned terms (pass_to_pass)."""
    ban_limits_path = Path(f"{REPO}/test/internal/ban-limits.json")
    if not ban_limits_path.exists():
        # Skip if ban-limits.json doesn't exist in this commit
        return

    import json
    ban_limits = json.loads(ban_limits_path.read_text())

    bun_ts = Path(f"{REPO}/scripts/build/bun.ts").read_text()
    compile_ts = Path(f"{REPO}/scripts/build/compile.ts").read_text()

    banned = ban_limits.get('banned', [])
    for word in banned:
        # Skip short words that might appear in normal code
        if len(word) < 4:
            continue
        assert word.lower() not in bun_ts.lower(), f"bun.ts contains banned word: {word}"
        assert word.lower() not in compile_ts.lower(), f"compile.ts contains banned word: {word}"


# [repo_tests] pass_to_pass — TypeScript typecheck (skipped if tsc not available)
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass).

    Runs tsc --noEmit to verify no type errors in scripts/build/*.ts
    """
    import shutil
    if not shutil.which("npx"):
        # Skip if npx is not available (tools not installed in Docker)
        return

    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--project", f"{REPO}/scripts/build/tsconfig.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Lint check (skipped if oxlint not available)
def test_repo_lint():
    """Repo's JavaScript lint passes (pass_to_pass).

    Runs oxlint on src/js to verify no lint errors.
    """
    import shutil
    if not shutil.which("npx"):
        # Skip if npx is not available (tools not installed in Docker)
        return

    r = subprocess.run(
        ["npx", "oxlint", "--config=oxlint.json", "--format=github", "src/js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"
