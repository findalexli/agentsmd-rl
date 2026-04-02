"""
Task: ruff-ty-intern-inferable-typevars
Repo: astral-sh/ruff @ 3a44cce48e2f9687c767a36b9af2da280ef68c64
PR:   #24161

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

REPO = "/repo"

GENERICS_RS = f"{REPO}/crates/ty_python_semantic/src/types/generics.rs"
BIND_RS = f"{REPO}/crates/ty_python_semantic/src/types/call/bind.rs"
CONSTRAINTS_RS = f"{REPO}/crates/ty_python_semantic/src/types/constraints.rs"
RELATION_RS = f"{REPO}/crates/ty_python_semantic/src/types/relation.rs"
SIGNATURES_RS = f"{REPO}/crates/ty_python_semantic/src/types/signatures.rs"
TYPES_RS = f"{REPO}/crates/ty_python_semantic/src/types.rs"

AFFECTED_FILES = [GENERICS_RS, BIND_RS, CONSTRAINTS_RS, RELATION_RS, SIGNATURES_RS, TYPES_RS]

CARGO_ENV = {
    **os.environ,
    "CARGO_PROFILE_DEV_OPT_LEVEL": "1",
    "INSTA_FORCE_PASS": "1",
    "INSTA_UPDATE": "always",
}


def _cargo(args: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["cargo"] + args,
        cwd=REPO,
        capture_output=True,
        timeout=timeout,
        env=CARGO_ENV,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — grep-based, fast
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_two_variant_removed():
    """The lazy-reference Two variant must be removed from InferableTypeVars."""
    content = Path(GENERICS_RS).read_text()
    assert "Two(" not in content, "Two variant still present in InferableTypeVars"


# [pr_diff] fail_to_pass
def test_salsa_interned_used():
    """Inner set storage must use salsa interning."""
    content = Path(GENERICS_RS).read_text()
    assert "#[salsa::interned" in content, (
        "No #[salsa::interned] struct found in generics.rs"
    )


# [pr_diff] fail_to_pass
def test_all_signatures_single_lifetime():
    """All InferableTypeVars references must use single lifetime <'db>, not <'a, 'db>."""
    dual = re.compile(r"InferableTypeVars<'[a-z]+,\s*'db>")
    for path in AFFECTED_FILES:
        p = Path(path)
        if p.exists():
            content = p.read_text()
            match = dual.search(content)
            assert match is None, (
                f"Dual-lifetime InferableTypeVars found in {p.name}: {match.group()}"
            )


# [pr_diff] fail_to_pass
def test_single_lifetime_hash_eq():
    """InferableTypeVars<'db> must compile with Hash + Eq bounds (salsa compat)."""
    gate_code = """
#[allow(dead_code, unused_imports)]
mod _harbor_refactor_gate {
    use super::InferableTypeVars;
    fn _single_lifetime<'db>(itv: InferableTypeVars<'db>) -> InferableTypeVars<'db> { itv }
    fn _assert_hash<'db>() where InferableTypeVars<'db>: std::hash::Hash {}
    fn _assert_eq<'db>() where InferableTypeVars<'db>: Eq {}
}
"""
    src = Path(GENERICS_RS)
    backup = Path("/tmp/generics_backup.rs")
    shutil.copy2(src, backup)
    try:
        with open(src, "a") as f:
            f.write(gate_code)
        r = _cargo(["check", "-p", "ty_python_semantic"])
        assert r.returncode == 0, (
            f"InferableTypeVars<'db> must satisfy Hash + Eq:\n"
            f"{r.stderr.decode()[-1000:]}"
        )
    finally:
        shutil.copy2(backup, src)


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) — cargo builds & test suites
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_compilation():
    """Full crate must compile after refactoring."""
    r = _cargo(["check", "-p", "ty_python_semantic"])
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr.decode()[-1000:]}"
    )


# [repo_tests] pass_to_pass
def test_generics_mdtests():
    """Generic specialization mdtests must pass."""
    r = _cargo(["test", "-p", "ty_python_semantic", "--", "mdtest::generics"], timeout=300)
    assert r.returncode == 0, (
        f"Generics mdtests failed:\n{r.stdout.decode()[-500:]}\n{r.stderr.decode()[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_overloads_mdtests():
    """Overload resolution mdtests must pass (exercises merge paths)."""
    r = _cargo(["test", "-p", "ty_python_semantic", "--", "mdtest::overloads"], timeout=300)
    assert r.returncode == 0, (
        f"Overloads mdtests failed:\n{r.stdout.decode()[-500:]}\n{r.stderr.decode()[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_narrowing_mdtests():
    """Type narrowing mdtests must pass (exercises constraint solving)."""
    r = _cargo(["test", "-p", "ty_python_semantic", "--", "mdtest::narrow"], timeout=300)
    assert r.returncode == 0, (
        f"Narrowing mdtests failed:\n{r.stdout.decode()[-500:]}\n{r.stderr.decode()[-500:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:76 @ 3a44cce
def test_no_local_imports():
    """Rust imports should go at top of file, not locally in functions (AGENTS.md:76)."""
    content = Path(GENERICS_RS).read_text()
    depth = 0
    in_fn = False
    for line in content.splitlines():
        stripped = line.strip()
        if re.match(r"(pub(\(.*?\))?\s+)?fn\s+", stripped):
            in_fn = True
        depth += line.count("{") - line.count("}")
        if depth == 0:
            in_fn = False
        if in_fn and depth > 1 and stripped.startswith("use ") and not stripped.startswith("use super"):
            assert False, f"Local import in function body: {stripped}"


# [agent_config] pass_to_pass — AGENTS.md:79 @ 3a44cce
def test_no_unwrap_panic_unreachable():
    """New code must avoid .unwrap(), panic!(), unreachable!() (AGENTS.md:79)."""
    # The InferableTypeVars enum and its impl blocks are the changed code.
    # Check that the agent hasn't introduced these anti-patterns in generics.rs.
    content = Path(GENERICS_RS).read_text()

    # Extract lines in/around InferableTypeVars definitions
    bad_patterns = [".unwrap()", "panic!(", "unreachable!("]
    inferable_section = False
    violations = []
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if "InferableTypeVars" in line and ("enum" in line or "impl" in line or "struct" in line):
            inferable_section = True
        if inferable_section:
            for pat in bad_patterns:
                if pat in stripped and not stripped.startswith("//"):
                    violations.append(f"  line {i}: {stripped}")
            # End section at closing brace at column 0
            if stripped == "}" and not line.startswith(" ") and not line.startswith("\t"):
                inferable_section = False

    assert not violations, (
        f"Found unwrap/panic/unreachable in InferableTypeVars code:\n"
        + "\n".join(violations)
    )


# [agent_config] pass_to_pass — AGENTS.md:81 @ 3a44cce
def test_prefer_expect_over_allow():
    """New lint suppressions should use #[expect()] not #[allow()] (AGENTS.md:81)."""
    content = Path(GENERICS_RS).read_text()
    # Find #[allow(...)] that aren't dead_code (which is standard for kept-around debug code)
    allow_pattern = re.compile(r"#\[allow\((?!dead_code)")
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if allow_pattern.search(stripped):
            # Check if this is near InferableTypeVars code (within 5 lines of mention)
            context_start = max(0, i - 6)
            context_end = min(len(content.splitlines()), i + 5)
            context_lines = content.splitlines()[context_start:context_end]
            if any("InferableTypeVars" in cl or "InferableTypeVarsInner" in cl for cl in context_lines):
                assert False, (
                    f"Line {i}: Use #[expect()] instead of #[allow()] per AGENTS.md:81: {stripped}"
                )
