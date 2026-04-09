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
