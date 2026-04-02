"""
Task: react-compiler-typo-fixes
Repo: facebook/react @ ba833da405d44260e94bd47c13eec90816bf44f1

Three typos in the React compiler: 'explicitlyu' in compiler/CLAUDE.md,
'intialized' in InferMutationAliasingEffects.ts and InferReactiveScopeVariables.ts.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/react"
INFER_MUTATION = (
    f"{REPO}/compiler/packages/babel-plugin-react-compiler"
    "/src/Inference/InferMutationAliasingEffects.ts"
)
INFER_REACTIVE = (
    f"{REPO}/compiler/packages/babel-plugin-react-compiler"
    "/src/ReactiveScopes/InferReactiveScopeVariables.ts"
)
CLAUDE_MD = f"{REPO}/compiler/CLAUDE.md"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — each typo must be corrected
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_infer_mutation_typo_fixed():
    """InferMutationAliasingEffects.ts error message says 'initialized' not 'intialized'."""
    content = Path(INFER_MUTATION).read_text()
    assert "intialized" not in content, (
        "Old typo 'intialized' still present in InferMutationAliasingEffects.ts"
    )
    assert "initialized with a DeclareLocal Catch instruction" in content, (
        "Corrected error message text not found in InferMutationAliasingEffects.ts"
    )


# [pr_diff] fail_to_pass
def test_claude_md_typo_fixed():
    """compiler/CLAUDE.md says 'explicitly added/removed' not 'explicitlyu added/removed'."""
    content = Path(CLAUDE_MD).read_text()
    assert "explicitlyu" not in content, (
        "Old typo 'explicitlyu' still present in compiler/CLAUDE.md"
    )
    assert "explicitly added/removed" in content, (
        "Corrected text 'explicitly added/removed' not found in compiler/CLAUDE.md"
    )


# [pr_diff] fail_to_pass
def test_reactive_scope_typo_fixed():
    """InferReactiveScopeVariables.ts comment says 'initialized' not 'intialized'."""
    content = Path(INFER_REACTIVE).read_text()
    assert "intialized" not in content, (
        "Old typo 'intialized' still present in InferReactiveScopeVariables.ts"
    )
    assert "properly initialized, valid mutable ranges" in content, (
        "Corrected comment text not found in InferReactiveScopeVariables.ts"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — files intact, not accidentally deleted or hollowed
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_files_intact():
    """Modified files still exist and retain their structural content."""
    ts_mutation = Path(INFER_MUTATION).read_text()
    assert "CompilerError.invariant" in ts_mutation, (
        "InferMutationAliasingEffects.ts is missing CompilerError.invariant usage"
    )

    ts_reactive = Path(INFER_REACTIVE).read_text()
    assert "inferReactiveScopeVariables" in ts_reactive, (
        "InferReactiveScopeVariables.ts is missing inferReactiveScopeVariables function"
    )

    md = Path(CLAUDE_MD).read_text()
    assert "Sapling" in md, (
        "compiler/CLAUDE.md is missing the Sapling version-control section"
    )
