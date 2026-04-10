"""
Task: react-flight-markup-types
Repo: facebook/react @ 10680271fab565e0edf948d3a6dc9d30e83df94c
PR:   35634

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
MARKUP_CONFIG = f"{REPO}/packages/react-client/src/forks/ReactFlightClientConfig.markup.js"
ACTION_SERVER = f"{REPO}/packages/react-server/src/ReactFlightActionServer.js"


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
# Fail-to-pass (pr_diff) — behavioral tests via AST parsing
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_server_reference_id_not_opaque():
    """ServerReferenceId type must not use the 'opaque' modifier — verified via AST parse."""
    r = _run_node("""
const { parse } = require('@babel/parser');
const fs = require('fs');

const src = fs.readFileSync('%s', 'utf8');
const ast = parse(src, { sourceType: 'module', plugins: ['flow'] });

let found = false;
for (const node of ast.program.body) {
  if (node.type === 'ExportNamedDeclaration' && node.declaration) {
    const decl = node.declaration;
    if ((decl.type === 'TypeAlias' || decl.type === 'OpaqueType') && decl.id.name === 'ServerReferenceId') {
      found = true;
      if (decl.type === 'OpaqueType') {
        console.log('FAIL: ServerReferenceId is opaque');
        process.exit(1);
      }
      console.log('PASS: ServerReferenceId is a plain TypeAlias');
    }
  }
}

if (!found) {
  console.log('FAIL: ServerReferenceId type declaration not found');
  process.exit(1);
}
""" % MARKUP_CONFIG)
    assert r.returncode == 0, f"AST check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_resolve_server_reference_parameter_type():
    """resolveServerReference id parameter must use ServerReferenceId, not mixed — verified via AST parse."""
    r = _run_node("""
const { parse } = require('@babel/parser');
const fs = require('fs');

const src = fs.readFileSync('%s', 'utf8');
const ast = parse(src, { sourceType: 'module', plugins: ['flow'] });

for (const node of ast.program.body) {
  if (node.type === 'ExportNamedDeclaration' && node.declaration &&
      node.declaration.type === 'FunctionDeclaration' &&
      node.declaration.id.name === 'resolveServerReference') {
    const params = node.declaration.params;
    const idParam = params.find(p => p.name === 'id');
    if (!idParam) {
      console.log('FAIL: id parameter not found');
      process.exit(1);
    }
    const ta = idParam.typeAnnotation && idParam.typeAnnotation.typeAnnotation;
    if (!ta) {
      console.log('FAIL: id parameter has no type annotation');
      process.exit(1);
    }
    if (ta.type === 'MixedTypeAnnotation') {
      console.log('FAIL: id parameter is typed as mixed');
      process.exit(1);
    }
    if (ta.type === 'GenericTypeAnnotation' && ta.id.name === 'ServerReferenceId') {
      console.log('PASS: id parameter is typed as ServerReferenceId');
      process.exit(0);
    }
    console.log('FAIL: unexpected type: ' + ta.type);
    process.exit(1);
  }
}
console.log('FAIL: resolveServerReference function not found');
process.exit(1);
""" % MARKUP_CONFIG)
    assert r.returncode == 0, f"AST check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_load_server_reference_metadata_id_type():
    """loadServerReference metaData.id must use ServerReferenceId, not string — verified via AST parse."""
    r = _run_node("""
const { parse } = require('@babel/parser');
const fs = require('fs');

const src = fs.readFileSync('%s', 'utf8');
const ast = parse(src, { sourceType: 'module', plugins: ['flow'] });

function findFunction(body, name) {
  for (const node of body) {
    if (node.type === 'FunctionDeclaration' && node.id && node.id.name === name) return node;
    if (node.type === 'ExportNamedDeclaration' && node.declaration &&
        node.declaration.type === 'FunctionDeclaration' && node.declaration.id.name === name) return node.declaration;
  }
  return null;
}

const fn = findFunction(ast.program.body, 'loadServerReference');
if (!fn) {
  console.log('FAIL: loadServerReference function not found');
  process.exit(1);
}

const metaDataParam = fn.params[1];
if (!metaDataParam) {
  console.log('FAIL: metaData parameter not found');
  process.exit(1);
}

const ta = metaDataParam.typeAnnotation && metaDataParam.typeAnnotation.typeAnnotation;
if (!ta || ta.type !== 'ObjectTypeAnnotation') {
  console.log('FAIL: metaData type annotation is not an object type');
  process.exit(1);
}

const idProp = ta.properties.find(p => p.key && p.key.name === 'id');
if (!idProp) {
  console.log('FAIL: id property not found in metaData type');
  process.exit(1);
}

const idType = idProp.value;
if (idType.type === 'StringTypeAnnotation') {
  console.log('FAIL: metaData.id is typed as bare string');
  process.exit(1);
}
if (idType.type === 'GenericTypeAnnotation' && idType.id.name === 'ServerReferenceId') {
  console.log('PASS: metaData.id is typed as ServerReferenceId');
  process.exit(0);
}
console.log('FAIL: unexpected type for metaData.id: ' + idType.type);
process.exit(1);
""" % ACTION_SERVER)
    assert r.returncode == 0, f"AST check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_server_manifest_remains_opaque():
    """ServerManifest must stay opaque — only ServerReferenceId type was changed."""
    src = Path(MARKUP_CONFIG).read_text()
    assert "export opaque type ServerManifest = null" in src, (
        "ServerManifest must remain an opaque type (not changed by this fix)"
    )


# [static] pass_to_pass
def test_resolve_server_reference_throws_error():
    """resolveServerReference must still throw its error (body not stubbed out)."""
    src = Path(MARKUP_CONFIG).read_text()
    assert "renderToHTML should not have emitted Server References" in src, (
        "resolveServerReference must still contain its throw statement — "
        "the fix is only a type annotation change, not a logic change"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint passes on the codebase (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "lint"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\\n{r.stderr[-500:]}\\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flow_markup():
    """Flow type checking passes for markup renderer (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "flow", "markup"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Flow check failed:\\n{r.stderr[-500:]}\\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_react_flight_server():
    """ReactFlightServer unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test", "ReactFlightServer", "-r=stable", "--env=development"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"ReactFlightServer tests failed:\\n{r.stderr[-500:]}\\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_react_flight():
    """ReactFlight client unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test", "ReactFlight-test", "-r=stable", "--env=development"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"ReactFlight tests failed:\\n{r.stderr[-500:]}\\n{r.stdout[-500:]}"
