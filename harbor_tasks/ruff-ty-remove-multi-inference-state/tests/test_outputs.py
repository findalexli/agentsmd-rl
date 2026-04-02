"""
Task: ruff-ty-remove-multi-inference-state
Repo: astral-sh/ruff @ 1535879415566fab7be4e8aef233579aa89801ed
PR:   24184

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
from pathlib import Path

REPO = "/repo"
BUILDER_RS = "crates/ty_python_semantic/src/types/infer/builder.rs"
CONTEXT_RS = "crates/ty_python_semantic/src/types/context.rs"
CRATE_SRC = "crates/ty_python_semantic/src"

CARGO_ENV = {
    **os.environ,
    "CARGO_PROFILE_DEV_OPT_LEVEL": "1",
    "INSTA_FORCE_PASS": "1",
    "INSTA_UPDATE": "always",
}


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compiles():
    """ty_python_semantic crate compiles without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        cwd=REPO, capture_output=True, timeout=600, env=CARGO_ENV,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core type/field removals
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_multi_inference_state_removed():
    """MultiInferenceState enum and all references removed from crate."""
    r = subprocess.run(
        ["grep", "-r", "MultiInferenceState", CRATE_SRC],
        cwd=REPO, capture_output=True,
    )
    assert r.returncode != 0, (
        f"MultiInferenceState still referenced in crate:\n{r.stdout.decode()[:1000]}"
    )


# [pr_diff] fail_to_pass
def test_inner_expression_inference_state_removed():
    """InnerExpressionInferenceState enum and all references removed from crate."""
    r = subprocess.run(
        ["grep", "-r", "InnerExpressionInferenceState", CRATE_SRC],
        cwd=REPO, capture_output=True,
    )
    assert r.returncode != 0, (
        f"InnerExpressionInferenceState still referenced in crate:\n"
        f"{r.stdout.decode()[:1000]}"
    )


# [pr_diff] fail_to_pass
def test_multi_inference_context_flag_removed():
    """multi_inference field and methods removed from InferContext."""
    ctx = Path(f"{REPO}/{CONTEXT_RS}").read_text()
    assert "multi_inference:" not in ctx, "multi_inference field still in InferContext"
    assert "fn is_in_multi_inference" not in ctx, "is_in_multi_inference still present"
    assert "fn set_multi_inference" not in ctx, "set_multi_inference still present"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — upstream test suites
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_overload_mdtests_pass():
    """Overload/multi-inference related mdtests pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--", "mdtest::overloads"],
        cwd=REPO, capture_output=True, timeout=600, env=CARGO_ENV,
    )
    assert r.returncode == 0, (
        f"Overload mdtests failed:\n{r.stderr.decode()[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_narrowing_mdtests_pass():
    """TypedDict/narrowing mdtests pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--", "mdtest::narrow"],
        cwd=REPO, capture_output=True, timeout=600, env=CARGO_ENV,
    )
    assert r.returncode == 0, (
        f"Narrowing mdtests failed:\n{r.stderr.decode()[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_annotation_mdtests_pass():
    """Annotation inference mdtests pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--", "mdtest::annotations"],
        cwd=REPO, capture_output=True, timeout=600, env=CARGO_ENV,
    )
    assert r.returncode == 0, (
        f"Annotation mdtests failed:\n{r.stderr.decode()[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_subscript_mdtests_pass():
    """Subscript/type expression mdtests pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--", "mdtest::subscript"],
        cwd=REPO, capture_output=True, timeout=600, env=CARGO_ENV,
    )
    assert r.returncode == 0, (
        f"Subscript mdtests failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — discard/defuse refactoring
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_discard_method_removed():
    """discard() method removed from TypeInferenceBuilder — speculative builders are safe to drop."""
    content = Path(f"{REPO}/{BUILDER_RS}").read_text()
    assert "fn discard(self)" not in content, (
        "discard(self) method still present in TypeInferenceBuilder"
    )


# [pr_diff] fail_to_pass
def test_defuse_method_exists():
    """defuse() method added to InferContext for speculative builder cleanup."""
    content = Path(f"{REPO}/{CONTEXT_RS}").read_text()
    assert "fn defuse(" in content, (
        "defuse() method not found in InferContext — speculative builders need it"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:76 @ 1535879415566fab7be4e8aef233579aa89801ed
def test_no_local_imports_in_builder():
    """Rust imports at top of file, not locally in functions (AGENTS.md:76)."""
    content = Path(f"{REPO}/{BUILDER_RS}").read_text()
    in_fn = False
    depth = 0
    bad_lines = []
    for i, line in enumerate(content.split("\n"), 1):
        stripped = line.strip()
        if re.match(r"(pub(\(.*?\))?\s+)?fn\s+", stripped):
            in_fn = True
        depth += line.count("{") - line.count("}")
        if depth == 0:
            in_fn = False
        if (
            in_fn
            and depth > 1
            and stripped.startswith("use ")
            and not stripped.startswith("use super")
        ):
            bad_lines.append(f"  line {i}: {stripped}")
    assert not bad_lines, (
        f"Local imports in function bodies (AGENTS.md:76):\n" + "\n".join(bad_lines)
    )
