"""
Task: react-compiler-remove-dead-code
Repo: facebook/react @ ab18f33d46171ed1963ae1ac955c5110bb1eb199
PR:   35827

Dead-code removal in the React Compiler: delete ValidateNoUntransformedReferences,
remove CompileProgramMetadata type, strip retryErrors from ProgramContext, remove
client-no-memo output mode, and make compileProgram return void.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react/compiler/packages/babel-plugin-react-compiler"
SRC = Path(REPO) / "src"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral: TypeScript AST checks via Node.js
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_compileprogram_returns_void():
    """compileProgram returns void and CompileProgramMetadata type is removed (TS AST)."""
    r = _run_node("""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('src/Entrypoint/Program.ts', 'utf8');
const sf = ts.createSourceFile('Program.ts', src, ts.ScriptTarget.Latest, true);

let foundFn = false;
let foundDeadType = false;

function visit(node) {
  if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'compileProgram') {
    foundFn = true;
    const typeText = node.type ? src.substring(node.type.pos, node.type.end).trim() : '(none)';
    if (typeText !== 'void') {
      console.error('compileProgram return type is "' + typeText + '", expected "void"');
      process.exit(1);
    }
  }
  if (ts.isTypeAliasDeclaration(node) && node.name && node.name.text === 'CompileProgramMetadata') {
    foundDeadType = true;
  }
  ts.forEachChild(node, visit);
}
visit(sf);

if (!foundFn) { console.error('compileProgram function declaration not found'); process.exit(1); }
if (foundDeadType) { console.error('CompileProgramMetadata type alias still declared'); process.exit(1); }
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_retryerrors_removed_from_class():
    """ProgramContext class has no retryErrors property (TS AST check)."""
    r = _run_node("""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('src/Entrypoint/Imports.ts', 'utf8');
const sf = ts.createSourceFile('Imports.ts', src, ts.ScriptTarget.Latest, true);

let foundClass = false;
function visit(node) {
  if (ts.isClassDeclaration(node) && node.name && node.name.text === 'ProgramContext') {
    foundClass = true;
    for (const member of node.members) {
      if (ts.isPropertyDeclaration(member) && member.name &&
          ts.isIdentifier(member.name) && member.name.text === 'retryErrors') {
        console.error('ProgramContext still has retryErrors property');
        process.exit(1);
      }
    }
  }
  ts.forEachChild(node, visit);
}
visit(sf);

if (!foundClass) { console.error('ProgramContext class not found'); process.exit(1); }
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_schema_rejects_client_no_memo():
    """CompilerOutputModeSchema z.enum does not include 'client-no-memo' (TS AST check)."""
    r = _run_node("""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('src/Entrypoint/Options.ts', 'utf8');
const sf = ts.createSourceFile('Options.ts', src, ts.ScriptTarget.Latest, true);

let enumValues = [];
function visit(node) {
  if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression) &&
      node.expression.name.text === 'enum') {
    const arg = node.arguments[0];
    if (arg && ts.isArrayLiteralExpression(arg)) {
      for (const el of arg.elements) {
        if (ts.isStringLiteral(el)) enumValues.push(el.text);
      }
    }
  }
  ts.forEachChild(node, visit);
}
visit(sf);

if (enumValues.includes('client-no-memo')) {
  console.error('client-no-memo still in z.enum: ' + JSON.stringify(enumValues));
  process.exit(1);
}
if (enumValues.length === 0) {
  console.error('No z.enum string values found in Options.ts');
  process.exit(1);
}
console.log('PASS: ' + JSON.stringify(enumValues));
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_validate_file_deleted():
    """ValidateNoUntransformedReferences.ts must be deleted (unused validation pass)."""
    dead_file = SRC / "Entrypoint" / "ValidateNoUntransformedReferences.ts"
    assert not dead_file.exists(), (
        "ValidateNoUntransformedReferences.ts still exists but should be deleted"
    )


# [pr_diff] fail_to_pass
def test_validate_not_imported():
    """BabelPlugin.ts must not import or call validateNoUntransformedReferences."""
    babel_plugin = (SRC / "Babel" / "BabelPlugin.ts").read_text()
    assert "ValidateNoUntransformedReferences" not in babel_plugin, (
        "BabelPlugin.ts still references ValidateNoUntransformedReferences"
    )
    assert "validateNoUntransformedReferences" not in babel_plugin, (
        "BabelPlugin.ts still references validateNoUntransformedReferences"
    )


# [pr_diff] fail_to_pass
def test_babel_fn_import_removed():
    """BabelFn must no longer be imported in Imports.ts (was only used by retryErrors)."""
    imports_ts = (SRC / "Entrypoint" / "Imports.ts").read_text()
    program_import_lines = [
        line for line in imports_ts.splitlines()
        if "from" in line and "Program" in line
    ]
    for line in program_import_lines:
        assert "BabelFn" not in line, (
            f"BabelFn is still imported from Program in Imports.ts: {line.strip()}"
        )


# [pr_diff] fail_to_pass
def test_client_no_memo_removed_environment():
    """'client-no-memo' case must be removed from Environment.ts switch statements."""
    env_ts = (SRC / "HIR" / "Environment.ts").read_text()
    assert "client-no-memo" not in env_ts, (
        "'client-no-memo' case is still present in Environment.ts"
    )


# [pr_diff] fail_to_pass
def test_compile_result_not_captured():
    """BabelPlugin.ts must not capture the return value of compileProgram."""
    babel_plugin = (SRC / "Babel" / "BabelPlugin.ts").read_text()
    assert not re.search(
        r"(const|let|var)\s+\w+\s*=\s*compileProgram\s*\(", babel_plugin
    ), "BabelPlugin.ts still captures the return value of compileProgram"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — files intact, not accidentally deleted or hollowed
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_core_files_intact():
    """Key source files still exist and contain their essential content."""
    babel = (SRC / "Babel" / "BabelPlugin.ts").read_text()
    assert "compileProgram(" in babel, (
        "BabelPlugin.ts is missing compileProgram call"
    )
    assert "BabelPluginReactCompiler" in babel, (
        "BabelPlugin.ts is missing BabelPluginReactCompiler export"
    )

    program = (SRC / "Entrypoint" / "Program.ts").read_text()
    assert "export function compileProgram" in program, (
        "Program.ts is missing compileProgram export"
    )

    imports = (SRC / "Entrypoint" / "Imports.ts").read_text()
    assert "class ProgramContext" in imports, (
        "Imports.ts is missing ProgramContext class"
    )

    options = (SRC / "Entrypoint" / "Options.ts").read_text()
    assert "'client'" in options, "Options.ts is missing 'client' mode"
    assert "'ssr'" in options, "Options.ts is missing 'ssr' mode"

    env = (SRC / "HIR" / "Environment.ts").read_text()
    assert "class Environment" in env, (
        "Environment.ts is missing Environment class"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo CI) — repository's own CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (npx tsc --noEmit)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_build():
    """Repo's build passes (yarn build using tsup)."""
    r = subprocess.run(
        ["yarn", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_jest_unit():
    """Repo's Jest unit tests pass (npx jest --config scripts/jest/main.config.js)."""
    r = subprocess.run(
        ["npx", "jest", "--config", "scripts/jest/main.config.js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Jest unit tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier():
    """Repo's Prettier formatting check passes (npx prettier --check)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "src/**/*.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_dist_exists():
    """Build produces dist/index.js output file."""
    # First build
    r = subprocess.run(
        ["yarn", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
    # Check output exists
    dist_file = Path(REPO) / "dist" / "index.js"
    assert dist_file.exists(), "dist/index.js not found after build"


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint check runs (yarn lint). Note: base commit has 8 pre-existing lint errors."""
    r = subprocess.run(
        ["yarn", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # We check that the command runs, not that it passes (base has pre-existing errors)
    # The command should complete without crashing
    assert "eslint" in r.stdout or "eslint" in r.stderr or r.returncode in [0, 1], (
        "ESLint command did not run properly: " + r.stderr[-500:] + " " + r.stdout[-500:]
    )
