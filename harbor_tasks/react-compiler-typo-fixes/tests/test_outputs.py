"""
Task: react-compiler-typo-fixes
Repo: facebook/react @ ba833da405d44260e94bd47c13eec90816bf44f1

Three typos in the React compiler: 'explicitlyu' in compiler/CLAUDE.md,
'intialized' in InferMutationAliasingEffects.ts and InferReactiveScopeVariables.ts.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
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
# Fail-to-pass (pr_diff) — each typo must be corrected
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_infer_mutation_typo_fixed():
    """InferMutationAliasingEffects.ts error message says 'initialized' not 'intialized'."""
    r = _run_node(f"""
import fs from 'node:fs';
const content = fs.readFileSync('{INFER_MUTATION}', 'utf8');
if (content.includes('intialized')) {{
    console.error('Old typo "intialized" still present in InferMutationAliasingEffects.ts');
    process.exit(1);
}}
if (!content.includes('initialized with a DeclareLocal Catch instruction')) {{
    console.error('Corrected error message not found in InferMutationAliasingEffects.ts');
    process.exit(1);
}}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_claude_md_typo_fixed():
    """compiler/CLAUDE.md says 'explicitly added/removed' not 'explicitlyu added/removed'."""
    r = _run_node(f"""
import fs from 'node:fs';
const content = fs.readFileSync('{CLAUDE_MD}', 'utf8');
if (content.includes('explicitlyu')) {{
    console.error('Old typo "explicitlyu" still present in compiler/CLAUDE.md');
    process.exit(1);
}}
if (!content.includes('explicitly added/removed')) {{
    console.error('Corrected text "explicitly added/removed" not found');
    process.exit(1);
}}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_reactive_scope_typo_fixed():
    """InferReactiveScopeVariables.ts comment says 'initialized' not 'intialized'."""
    r = _run_node(f"""
import fs from 'node:fs';
const content = fs.readFileSync('{INFER_REACTIVE}', 'utf8');
if (content.includes('intialized')) {{
    console.error('Old typo "intialized" still present in InferReactiveScopeVariables.ts');
    process.exit(1);
}}
if (!content.includes('properly initialized, valid mutable ranges')) {{
    console.error('Corrected comment not found in InferReactiveScopeVariables.ts');
    process.exit(1);
}}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass — files intact and structurally sound
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_files_intact():
    """Modified files still exist and retain their structural content."""
    r = _run_node(f"""
import fs from 'node:fs';
const mutation = fs.readFileSync('{INFER_MUTATION}', 'utf8');
if (!mutation.includes('CompilerError.invariant')) {{
    console.error('InferMutationAliasingEffects.ts missing CompilerError.invariant');
    process.exit(1);
}}
const reactive = fs.readFileSync('{INFER_REACTIVE}', 'utf8');
if (!reactive.includes('inferReactiveScopeVariables')) {{
    console.error('InferReactiveScopeVariables.ts missing function');
    process.exit(1);
}}
const md = fs.readFileSync('{CLAUDE_MD}', 'utf8');
if (!md.includes('Sapling')) {{
    console.error('CLAUDE.md missing Sapling section');
    process.exit(1);
}}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout
