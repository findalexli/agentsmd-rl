"""
Task: react-compiler-tryrecord-consistent-wrapping
Repo: react @ cebe42e24521ce02bf427fd482009d01e1466277
PR:   35880

The React compiler pipeline has inconsistent error handling: some validation
and inference passes are not wrapped in env.tryRecord(), some validation files
use a manual for-loop instead of the batch recordErrors() method, and BuildHIR
has a redundant instanceof ternary.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
COMPILER_SRC = f"{REPO}/compiler/packages/babel-plugin-react-compiler/src"
PIPELINE = f"{COMPILER_SRC}/Entrypoint/Pipeline.ts"
BUILD_HIR = f"{COMPILER_SRC}/HIR/BuildHIR.ts"
VALIDATE_DERIVED = f"{COMPILER_SRC}/Validation/ValidateNoDerivedComputationsInEffects.ts"
VALIDATE_MEMO = f"{COMPILER_SRC}/Validation/ValidatePreservedManualMemoization.ts"
VALIDATE_SOURCE = f"{COMPILER_SRC}/Validation/ValidateSourceLocations.ts"


def _is_wrapped_in_tryrecord(content: str, func_call: str) -> bool:
    """Check if a function call is wrapped in env.tryRecord(() => { ... })."""
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if func_call in line:
            context_before = "\n".join(lines[max(0, i - 3) : i + 1])
            if "tryRecord" in context_before:
                return True
    return False


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a temp JS file and execute it with Node."""
    tmp = Path(REPO) / "_eval_check.mjs"
    tmp.write_text(script)
    try:
        return subprocess.run(
            ["node", str(tmp)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — tryRecord wrapping in Pipeline.ts
# ---------------------------------------------------------------------------

def test_tryrecord_wraps_early_and_hook_validations():
    """Early validation passes and hook validations must be wrapped in tryRecord."""
    r = _run_node(f"""
import fs from 'node:fs';
const content = fs.readFileSync('{PIPELINE}', 'utf8');
const lines = content.split('\\n');

function isWrapped(funcCall) {{
  for (let i = 0; i < lines.length; i++) {{
    if (lines[i].includes(funcCall)) {{
      const ctx = lines.slice(Math.max(0, i - 3), i + 1).join('\\n');
      if (ctx.includes('tryRecord')) return true;
    }}
  }}
  return false;
}}

const funcs = [
  'validateContextVariableLValues(hir)',
  'validateUseMemo(hir)',
  'validateHooksUsage(hir)',
  'validateNoCapitalizedCalls(hir)',
];

const missing = funcs.filter(f => !isWrapped(f));
if (missing.length > 0) {{
  console.error('Not wrapped in tryRecord:', missing.join(', '));
  process.exit(1);
}}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"


def test_tryrecord_wraps_inference_and_render_passes():
    """Inference and render-related validation passes must be wrapped in tryRecord."""
    content = Path(PIPELINE).read_text()
    funcs = [
        "inferMutationAliasingEffects(hir)",
        "inferMutationAliasingRanges(hir",
        "validateLocalsNotReassignedAfterRender(hir)",
        "validateNoRefAccessInRender(hir)",
        "validateNoSetStateInRender(hir)",
    ]
    for func in funcs:
        assert _is_wrapped_in_tryrecord(content, func), \
            f"{func} should be wrapped in env.tryRecord()"


def test_tryrecord_wraps_late_passes():
    """Late-pipeline passes must be wrapped in tryRecord."""
    content = Path(PIPELINE).read_text()
    funcs = [
        "validateNoDerivedComputationsInEffects(hir)",
        "validateExhaustiveDependencies(hir)",
        "validatePreservedManualMemoization(reactiveFunction)",
        "validateSourceLocations(func, ast, env)",
    ]
    for func in funcs:
        assert _is_wrapped_in_tryrecord(content, func), \
            f"{func} should be wrapped in env.tryRecord()"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — recordErrors batch normalization
# ---------------------------------------------------------------------------

def test_record_errors_normalization():
    """Validation files must use batch recordErrors(), not manual for-loop."""
    checks = [
        (VALIDATE_DERIVED, "ValidateNoDerivedComputationsInEffects.ts"),
        (VALIDATE_MEMO, "ValidatePreservedManualMemoization.ts"),
        (VALIDATE_SOURCE, "ValidateSourceLocations.ts"),
    ]
    for filepath, name in checks:
        content = Path(filepath).read_text()
        assert ".recordErrors(" in content, \
            f"{name} should use batch .recordErrors() method"
        # The old pattern iterated details and called singular recordError
        has_loop = "for (const detail of" in content
        has_singular = "recordError(detail)" in content
        assert not (has_loop and has_singular), \
            f"{name} should not use manual for-loop with recordError(detail)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — BuildHIR simplified conditional
# ---------------------------------------------------------------------------

def test_build_hir_simplified_conditional():
    """BuildHIR must use simplified category check, not redundant instanceof ternary."""
    r = _run_node(f"""
import fs from 'node:fs';
const content = fs.readFileSync('{BUILD_HIR}', 'utf8');

// The redundant ternary should be removed
if (content.includes('detail instanceof CompilerDiagnostic')) {{
  console.error('Redundant instanceof CompilerDiagnostic ternary still present');
  process.exit(1);
}}

// The simplified form should exist
if (!content.includes('detail.category === ErrorCategory.Invariant')) {{
  console.error('Simplified detail.category === ErrorCategory.Invariant not found');
  process.exit(1);
}}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — merged enableValidations guard blocks
# ---------------------------------------------------------------------------

def test_merged_validation_guard_blocks():
    """Two consecutive if(env.enableValidations) blocks should be merged into one."""
    content = Path(PIPELINE).read_text()
    # Find section between validateLocalsNotReassignedAfterRender and assertValidMutableRanges
    start = content.index("validateLocalsNotReassignedAfterRender")
    end = content.index("assertValidMutableRanges")
    section = content[start:end]
    # In the merged version, there should be NO if(env.enableValidations) between them
    # In the base, there IS one (the second guard block opens)
    assert "if (env.enableValidations)" not in section, \
        "Should not have a separate if(env.enableValidations) block between " \
        "validateLocalsNotReassignedAfterRender and assertValidMutableRanges"


# ---------------------------------------------------------------------------
# Pass-to-pass — pipeline structural integrity
# ---------------------------------------------------------------------------

def test_pipeline_has_required_functions():
    """Pipeline.ts must still reference all expected compiler pass functions."""
    content = Path(PIPELINE).read_text()
    required = [
        "validateContextVariableLValues",
        "validateUseMemo",
        "inferMutationAliasingEffects",
        "inferMutationAliasingRanges",
        "validateHooksUsage",
        "validateNoCapitalizedCalls",
        "validateNoRefAccessInRender",
        "validateNoSetStateInRender",
        "validateNoDerivedComputationsInEffects",
        "validateExhaustiveDependencies",
        "validatePreservedManualMemoization",
        "validateSourceLocations",
        "validateLocalsNotReassignedAfterRender",
    ]
    for func_name in required:
        assert func_name in content, f"Pipeline.ts must reference {func_name}"


# ---------------------------------------------------------------------------
# Pass-to-pass — repo CI/CD checks (p2p enrichment)
# ---------------------------------------------------------------------------

def test_repo_lint():
    """Repo's ESLint passes on babel-plugin-react-compiler (pass_to_pass)."""
    # Install dependencies first
    r = subprocess.run(
        ["yarn", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"yarn install failed:\n{r.stderr[-500:]}"
    r = subprocess.run(
        ["yarn", "workspace", "babel-plugin-react-compiler", "lint"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_typecheck():
    """Repo's TypeScript typecheck passes on babel-plugin-react-compiler (pass_to_pass)."""
    # Install dependencies first
    r = subprocess.run(
        ["yarn", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"yarn install failed:\n{r.stderr[-500:]}"
    r = subprocess.run(
        ["yarn", "tsc", "--noEmit", "-p", "packages/babel-plugin-react-compiler/tsconfig.json"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_jest_unit():
    """Repo's Jest unit tests pass on babel-plugin-react-compiler (pass_to_pass)."""
    # Install dependencies first
    r = subprocess.run(
        ["yarn", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"yarn install failed:\n{r.stderr[-500:]}"
    # Run a subset of Jest tests (quick unit tests only)
    r = subprocess.run(
        ["yarn", "workspace", "babel-plugin-react-compiler", "jest", "--testPathPattern=DisjointSet-test|Result-test|envConfig-test|parseConfigPragma-test|Logger-test", "--maxWorkers=1"],
        capture_output=True, text=True, timeout=180, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"Jest unit tests failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_build():
    """Repo's build passes on babel-plugin-react-compiler (pass_to_pass)."""
    # Install dependencies first
    r = subprocess.run(
        ["yarn", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"yarn install failed:\n{r.stderr[-500:]}"
    # Run the build for babel-plugin-react-compiler
    r = subprocess.run(
        ["yarn", "workspace", "babel-plugin-react-compiler", "build"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"
