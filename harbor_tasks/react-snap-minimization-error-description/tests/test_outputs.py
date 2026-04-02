"""
Task: react-snap-minimization-error-description
Repo: facebook/react @ f84ce5a45c47b1081a09c17eea58c16ef145c113

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/react"
MINIMIZE_TS = f"{REPO}/compiler/packages/snap/src/minimize.ts"


def _read_minimize() -> str:
    src = Path(MINIMIZE_TS)
    assert src.exists(), f"minimize.ts not found at {MINIMIZE_TS}"
    return src.read_text()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file presence check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_minimize_ts_exists():
    """minimize.ts must exist and be non-empty."""
    content = _read_minimize()
    assert len(content) > 1000, "minimize.ts appears empty or truncated"
    assert "errorsMatch" in content, "minimize.ts missing expected function errorsMatch"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — error description in type definitions
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: TypeScript type declarations; behavior requires full React compiler pipeline
def test_compile_errors_type_has_description():
    """CompileErrors.errors array must include description: string | null."""
    content = _read_minimize()
    # Base has: errors: Array<{category: string; reason: string}>
    # Fixed:    errors: Array<{category: string; reason: string; description: string | null}>
    assert re.search(
        r"errors:\s*Array<\{[^}]*description:\s*string\s*\|\s*null[^}]*\}>",
        content,
    ), "CompileErrors.errors must include `description: string | null`"


# [pr_diff] fail_to_pass
# AST-only because: TypeScript type declarations; behavior requires full React compiler pipeline
def test_error_details_type_has_description():
    """error.details array type must include description: string | null."""
    content = _read_minimize()
    # Base has: details?: Array<{category: string; reason: string}>;
    # Fixed:    details?: Array<{...description: string | null;...}>;
    # Use DOTALL so we match the multi-line form introduced by the fix
    assert re.search(
        r"details\?:.*?description:\s*string\s*\|\s*null",
        content,
        re.DOTALL,
    ), "error.details type must include `description: string | null`"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — error extraction and comparison
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: TypeScript, function is internal to module with complex React compiler deps
def test_error_mapping_preserves_description():
    """error.details.map must copy description field onto each mapped error object."""
    content = _read_minimize()
    assert "description: detail.description" in content, (
        "Error mapping must include `description: detail.description` "
        "so the description is preserved from CompilerError details"
    )


# [pr_diff] fail_to_pass
# AST-only because: TypeScript, function is internal to module with complex React compiler deps
def test_errors_match_compares_description():
    """errorsMatch must return false when descriptions differ."""
    content = _read_minimize()
    # Base has only category and reason in the comparison
    # Fixed adds: a.errors[i].description !== b.errors[i].description
    assert re.search(
        r"a\.errors\[i\]\.description\s*!==\s*b\.errors\[i\]\.description",
        content,
    ), "errorsMatch must compare `a.errors[i].description !== b.errors[i].description`"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — new minimization strategy generators
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: TypeScript generator functions, cannot call without full package compilation
def test_remove_function_parameters_generator_exists():
    """Generator function removeFunctionParameters must be defined."""
    content = _read_minimize()
    assert re.search(r"function\*\s+removeFunctionParameters\s*\(", content), (
        "Generator `function* removeFunctionParameters(...)` must be defined"
    )


# [pr_diff] fail_to_pass
# AST-only because: TypeScript generator functions, cannot call without full package compilation
def test_remove_array_pattern_elements_generator_exists():
    """Generator function removeArrayPatternElements must be defined."""
    content = _read_minimize()
    assert re.search(r"function\*\s+removeArrayPatternElements\s*\(", content), (
        "Generator `function* removeArrayPatternElements(...)` must be defined"
    )


# [pr_diff] fail_to_pass
# AST-only because: TypeScript generator functions, cannot call without full package compilation
def test_remove_object_pattern_properties_generator_exists():
    """Generator function removeObjectPatternProperties must be defined."""
    content = _read_minimize()
    assert re.search(r"function\*\s+removeObjectPatternProperties\s*\(", content), (
        "Generator `function* removeObjectPatternProperties(...)` must be defined"
    )


# [pr_diff] fail_to_pass
# AST-only because: TypeScript, strategy array is module-level; cannot introspect at runtime
def test_new_strategies_registered_in_array():
    """All three new strategies must be registered in simplificationStrategies."""
    content = _read_minimize()
    # Find the simplificationStrategies array
    match = re.search(
        r"simplificationStrategies\s*=\s*\[(.+?)(?=\n\]|\];)",
        content,
        re.DOTALL,
    )
    assert match, "Could not locate `simplificationStrategies` array"
    block = match.group(1)
    for name in ("removeFunctionParameters", "removeArrayPatternElements", "removeObjectPatternProperties"):
        assert name in block, (
            f"`{name}` must be registered inside the simplificationStrategies array"
        )
