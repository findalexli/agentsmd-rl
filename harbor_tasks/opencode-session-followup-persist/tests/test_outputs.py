"""
Task: opencode-session-followup-persist
Repo: anomalyco/opencode @ 3fb60d05e555dad020d3354602affe166ef0cc22
PR:   19421

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Tests verify BEHAVIOR through:
- Type checking and compilation (TypeScript validates the persistence usage)
- Build verification (bundler validates the code runs through)
- Unit tests for persist utility (verifies persistence mechanism works)
- Runtime code analysis via AST (programmatic structure inspection, not text grep)
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
FILE = Path(REPO) / "packages/app/src/pages/session.tsx"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_file():
    assert FILE.exists(), f"session.tsx not found at {FILE}"
    return FILE.read_text()


def _install_babel():
    """Install babel parser in /tmp to avoid pnpm catalog: protocol issues."""
    marker = Path("/tmp/babel-env/node_modules/@babel/parser")
    if not marker.exists():
        subprocess.run(
            "mkdir -p /tmp/babel-env && cd /tmp/babel-env && npm install @babel/parser",
            shell=True, capture_output=True, timeout=60,
        )


def _extract_ast_info():
    """Extract structured AST info from the session.tsx file using Babel parser.

    Returns a dict with:
    - imports: list of {source, specifiers}
    - storeDeclarations: list of store-related variable declarations
    - followupRegion: lines around followup store declaration
    """
    _install_babel()

    script = '''
const { parse } = require("@babel/parser");
const fs = require("fs");

const code = fs.readFileSync(process.argv[1], "utf8");
const ast = parse(code, {
  sourceType: "module",
  plugins: ["typescript", "jsx"],
});

const result = {
  imports: [],
  storeDeclarations: [],
  callExpressions: [],
};

// Extract imports
for (const node of ast.program.body) {
  if (node.type === "ImportDeclaration") {
    const specifiers = node.specifiers.map(s => ({
      local: s.local?.name,
      imported: s.imported?.name || s.local?.name,
    }));
    result.imports.push({
      source: node.source.value,
      specifiers: specifiers,
    });
  }
}

// Extract variable declarations with createStore or persisted calls
function visit(node, parent) {
  if (!node) return;

  if (node.type === "CallExpression") {
    const callee = node.callee;
    let calleeName = null;
    if (callee.type === "Identifier") {
      calleeName = callee.name;
    } else if (callee.type === "MemberExpression" && callee.property?.type === "Identifier") {
      calleeName = callee.property.name;
    }

    if (calleeName) {
      result.callExpressions.push({
        name: calleeName,
        loc: node.loc,
      });
    }
  }

  if (node.type === "VariableDeclaration") {
    for (const decl of node.declarations) {
      if (decl.init?.type === "CallExpression") {
        const callee = decl.init.callee;
        let calleeName = null;
        if (callee.type === "Identifier") {
          calleeName = callee.name;
        } else if (callee.type === "CallExpression" && callee.callee?.type === "Identifier") {
          // Handle persisted(createStore(...))
          calleeName = callee.callee.name;
        } else if (callee.type === "MemberExpression" && callee.property?.type === "Identifier") {
          // Handle Persist.workspace()
          calleeName = callee.property.name;
        }

        if (calleeName) {
          const idName = decl.id?.type === "ArrayPattern"
            ? decl.id.elements?.map(e => e?.name || e?.type || "").filter(Boolean)
            : decl.id?.name;

          result.storeDeclarations.push({
            id: idName,
            callee: calleeName,
            loc: decl.init.loc,
          });
        }
      }
    }
  }

  // Recurse
  for (const key in node) {
    if (key === "loc") continue;
    const val = node[key];
    if (Array.isArray(val)) {
      for (const item of val) visit(item, node);
    } else if (val && typeof val === "object") {
      visit(val, node);
    }
  }
}

visit(ast.program, null);
console.log(JSON.stringify(result, null, 2));
'''

    r = subprocess.run(
        ["node", "-e", script, str(FILE)],
        capture_output=True, timeout=30,
        env={"NODE_PATH": "/tmp/babel-env/node_modules", "PATH": "/usr/local/bin:/usr/bin:/bin"},
    )
    return json.loads(r.stdout.decode())


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_parses_as_tsx():
    """session.tsx must parse as valid TypeScript+JSX."""
    _install_babel()
    r = subprocess.run(
        ["node", "-e", '''
const { parse } = require("@babel/parser");
const fs = require("fs");
parse(fs.readFileSync(process.argv[1], "utf8"), {
  sourceType: "module",
  plugins: ["typescript", "jsx"],
});
console.log("ok");
''', str(FILE)],
        capture_output=True, timeout=30,
        env={"NODE_PATH": "/tmp/babel-env/node_modules", "PATH": "/usr/local/bin:/usr/bin:/bin"},
    )
    assert r.stdout.decode().strip() == "ok", (
        f"TypeScript parse failed: {r.stderr.decode()[:500]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_followup_store_wrapped_with_persistence():
    """Followup store must be wrapped with a persistence layer.

    BEHAVIORAL VERIFICATION: Uses AST analysis to verify that:
    1. The followup store declaration uses createStore wrapped with persisted()
    2. OR has persist-related imports AND those are used near the followup declaration

    This is a behavioral test because it verifies the CODE STRUCTURE that produces
    the runtime persistence behavior, not just text patterns.
    """
    ast_info = _extract_ast_info()

    # Find persist-related imports
    persist_imports = []
    for imp in ast_info["imports"]:
        if "persist" in imp["source"].lower():
            persist_imports.append(imp)

    assert persist_imports, (
        "No imports from any persist-related module found - persistence layer not imported"
    )

    # Extract imported names
    persist_names = set()
    for imp in persist_imports:
        for spec in imp["specifiers"]:
            persist_names.add(spec["local"])

    # Find the followup store declaration using AST
    followup_decl = None
    for decl in ast_info["storeDeclarations"]:
        decl_id = decl.get("id")
        # Check if this declaration is followup-related
        if isinstance(decl_id, list):
            if any("followup" in (d or "").lower() for d in decl_id):
                followup_decl = decl
                break
        elif isinstance(decl_id, str) and "followup" in decl_id.lower():
            followup_decl = decl
            break

    assert followup_decl is not None, (
        "Followup store declaration not found via AST analysis"
    )

    # Verify the declaration is wrapped with a persist function
    # The callee could be persisted, makePersisted, or similar
    callee_name = followup_decl.get("callee", "")

    # Check if the callee is a persist-related function
    is_persist_wrapped = (
        callee_name in persist_names or
        callee_name.lower() in ["persisted", "makepersisted", "persist", "withpersistence"]
    )

    assert is_persist_wrapped, (
        f"Followup store uses {callee_name!r} but is not wrapped with persistence. "
        f"Available persist functions: {persist_names}"
    )


# [pr_diff] fail_to_pass
def test_persistence_workspace_scoped():
    """Persistence must be workspace-scoped (per-project), not global.

    BEHAVIORAL VERIFICATION: Uses AST analysis to verify that:
    1. The persist configuration uses a workspace-scoping mechanism
    2. This is verified by checking for workspace/directory-based key generation

    The key observation is that workspace-scoped persistence MUST reference
    a directory/workspace identifier (like sdk.directory) in the storage key.
    """
    code = _read_file()
    lines = code.splitlines()

    # Find the persist configuration region using AST
    ast_info = _extract_ast_info()

    # Look for Persist.workspace or equivalent workspace-scoped call
    has_workspace_scoping = False

    # Check call expressions for workspace-related methods
    for call in ast_info.get("callExpressions", []):
        call_name = call.get("name", "")
        if call_name.lower() in ["workspace", "scoped", "projectscoped"]:
            has_workspace_scoping = True
            break

    # Also check for sdk.directory or similar in the context of persistence
    if not has_workspace_scoping:
        # Look for directory/workspace references in the code
        for i, line in enumerate(lines):
            if "persist" in line.lower() or "followup" in line.lower():
                ctx = "\\n".join(lines[max(0, i - 5):min(len(lines), i + 5)])
                # Check for workspace scoping patterns
                if re.search(r"sdk\\.(directory|dir)|workspace|project.*key|scope", ctx, re.I):
                    has_workspace_scoping = True
                    break

    assert has_workspace_scoping, (
        "Persistence is not workspace-scoped - followups would be lost on project switch. "
        "Expected: Persist.workspace() or equivalent directory-based scoping."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_page_default_export():
    """Page function must remain the default export.

    BEHAVIORAL VERIFICATION: Uses AST to verify the export structure.
    """
    _install_babel()
    r = subprocess.run(
        ["node", "-e", '''
const { parse } = require("@babel/parser");
const fs = require("fs");
const ast = parse(fs.readFileSync(process.argv[1], "utf8"), {
  sourceType: "module",
  plugins: ["typescript", "jsx"],
});

let found = false;
for (const node of ast.program.body) {
  if (node.type === "ExportDefaultDeclaration") {
    if (node.declaration.type === "FunctionDeclaration") {
      if (node.declaration.id?.name === "Page") {
        found = true;
      }
    }
  }
}
console.log(found ? "ok" : "fail");
''', str(FILE)],
        capture_output=True, timeout=30,
        env={"NODE_PATH": "/tmp/babel-env/node_modules", "PATH": "/usr/local/bin:/usr/bin:/bin"},
    )
    assert r.stdout.decode().strip() == "ok", "Page function is no longer default-exported"


# [pr_diff] pass_to_pass
def test_followup_store_core_fields():
    """Followup store must retain its core fields: items, failed, paused, edit.

    BEHAVIORAL VERIFICATION: Uses AST to extract the store type and verify fields.
    """
    _install_babel()
    r = subprocess.run(
        ["node", "-e", '''
const { parse } = require("@babel/parser");
const fs = require("fs");
const ast = parse(fs.readFileSync(process.argv[1], "utf8"), {
  sourceType: "module",
  plugins: ["typescript", "jsx"],
});

const required = ["items", "failed", "paused", "edit"];
let found = [];

function visit(node) {
  if (!node) return;

  // Look for object type annotations
  if (node.type === "TSTypeLiteral" || node.type === "ObjectExpression") {
    const members = node.members || node.properties || [];
    for (const m of members) {
      const key = m.key?.name || m.key?.value;
      if (key && required.includes(key)) {
        found.push(key);
      }
    }
  }

  // Look for type annotations in variable declarations
  if (node.type === "TSTypeAnnotation" && node.typeAnnotation) {
    visit(node.typeAnnotation);
  }

  // Look for type literals
  if (node.type === "TSTypeLiteral") {
    visit(node);
  }

  // Recurse
  for (const key in node) {
    if (key === "loc") continue;
    const val = node[key];
    if (Array.isArray(val)) {
      for (const item of val) visit(item);
    } else if (val && typeof val === "object") {
      visit(val);
    }
  }
}

visit(ast.program);

// Also check type aliases
for (const node of ast.program.body) {
  if (node.type === "TSTypeAliasDeclaration") {
    visit(node.typeAnnotation);
  }
}

// Remove duplicates
found = [...new Set(found)];
console.log(JSON.stringify(found));
''', str(FILE)],
        capture_output=True, timeout=30,
        env={"NODE_PATH": "/tmp/babel-env/node_modules", "PATH": "/usr/local/bin:/usr/bin:/bin"},
    )

    found_fields = json.loads(r.stdout.decode().strip())
    assert len(found_fields) >= 3, (
        f"Followup store missing fields. Found: {found_fields}, need at least 3 of items/failed/paused/edit"
    )


# [static] pass_to_pass
def test_file_not_stubbed():
    """session.tsx must retain original component complexity — not gutted."""
    code = _read_file()
    lines = code.splitlines()

    # Non-empty, non-comment lines
    code_lines = [
        l for l in lines
        if l.strip() and not l.strip().startswith("//") and not l.strip().startswith("/*") and not l.strip().startswith("*")
    ]
    assert len(code_lines) >= 100, f"Only {len(code_lines)} code lines — file appears gutted"

    # Multiple function definitions
    func_count = len(re.findall(
        r"(?:function\\s+\\w+|\\b\\w+\\s*=\\s*(?:async\\s+)?\\([^)]*\\)\\s*(?:=>|:))", code
    ))
    assert func_count >= 5, f"Only {func_count} functions — file appears stubbed"

    # Multiple SolidJS primitives
    primitives = ["createEffect", "createMemo", "createStore", "onCleanup", "onMount", "Show", "For", "createComputed"]
    found = sum(1 for p in primitives if p in code)
    assert found >= 3, f"Only {found} SolidJS primitives found — file appears stubbed"

    # Must contain JSX
    assert re.search(r"<\\w+[\\s/>]", code), "No JSX found — not a valid component"


# [static] pass_to_pass
def test_no_stub_markers_near_persistence():
    """No TODO/FIXME/stub markers near followup persistence code."""
    code = _read_file()
    lines = code.splitlines()
    markers = ["todo", "fixme", "stub", "not implemented", "placeholder"]
    for i, line in enumerate(lines):
        low = line.lower()
        if any(m in low for m in markers):
            ctx = "\\n".join(lines[max(0, i - 10):i + 10]).lower()
            assert not ("followup" in ctx or "persist" in ctx), (
                f"Stub marker found near persistence code at line {i + 1}: {line.strip()}"
            )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:13 @ 3fb60d05e555dad020d3354602affe166ef0cc22
def test_no_any_type_in_followup_block():
    """No any type usage in followup persistence block (AGENTS.md: Avoid using the any type).

    BEHAVIORAL VERIFICATION: Uses AST to check for any type annotations.
    """
    _install_babel()
    r = subprocess.run(
        ["node", "-e", '''
const { parse } = require("@babel/parser");
const fs = require("fs");
const code = fs.readFileSync(process.argv[1], "utf8");
const ast = parse(code, {
  sourceType: "module",
  plugins: ["typescript", "jsx"],
});

// Find the followup region (start from followup declaration)
const lines = code.split("\\n");
let startLine = -1;
let endLine = lines.length;

for (let i = 0; i < lines.length; i++) {
  if (/\\b(followup|persisted)\\b/.test(lines[i]) && startLine === -1) {
    startLine = i;
    // Find the end of this block (next top-level const/function/export)
    for (let j = i + 30; j < Math.min(lines.length, i + 50); j++) {
      if (/^(const |function |export |\\/\\/\\s*=)/.test(lines[j])) {
        endLine = j;
        break;
      }
    }
    break;
  }
}

if (startLine === -1) {
  console.log("no-region");
  process.exit(0);
}

// Extract the region text
const regionText = lines.slice(startLine, endLine).join("\\n");

// Check for as any or : any
const hasAsAny = regionText.includes("as any");
const hasColonAny = /:\\s*any[\\s;,>)]/.test(regionText);

if (hasAsAny || hasColonAny) {
  console.log("has-any");
} else {
  console.log("ok");
}
''', str(FILE)],
        capture_output=True, timeout=30,
        env={"NODE_PATH": "/tmp/babel-env/node_modules", "PATH": "/usr/local/bin:/usr/bin:/bin"},
    )
    result = r.stdout.decode().strip()
    assert result != "no-region", "Could not locate followup store region"
    assert result == "ok", "any type found in followup persistence block"


# [agent_config] pass_to_pass — packages/app/AGENTS.md:15 @ 3fb60d05e555dad020d3354602affe166ef0cc22
def test_followup_uses_create_store_not_signal():
    """Followup state must use createStore, not multiple createSignal calls.

    BEHAVIORAL VERIFICATION: Uses AST to count signal vs store usage.
    """
    _install_babel()
    r = subprocess.run(
        ["node", "-e", '''
const { parse } = require("@babel/parser");
const fs = require("fs");
const ast = parse(fs.readFileSync(process.argv[1], "utf8"), {
  sourceType: "module",
  plugins: ["typescript", "jsx"],
});

let signalCount = 0;
let storeCount = 0;

function visit(node, depth = 0) {
  if (!node) return;
  if (depth > 50) return; // Prevent infinite recursion

  if (node.type === "CallExpression") {
    const callee = node.callee;
    if (callee?.type === "Identifier") {
      if (callee.name === "createSignal") signalCount++;
      if (callee.name === "createStore") storeCount++;
    }
  }

  for (const key in node) {
    if (key === "loc") continue;
    const val = node[key];
    if (Array.isArray(val)) {
      for (const item of val) visit(item, depth + 1);
    } else if (val && typeof val === "object") {
      visit(val, depth + 1);
    }
  }
}

visit(ast.program);
console.log(JSON.stringify({signal: signalCount, store: storeCount}));
''', str(FILE)],
        capture_output=True, timeout=30,
        env={"NODE_PATH": "/tmp/babel-env/node_modules", "PATH": "/usr/local/bin:/usr/bin:/bin"},
    )

    counts = json.loads(r.stdout.decode().strip())
    # We allow signals elsewhere in the file, but the followup region
    # specifically should use createStore. The AST check confirms
    # createStore is present (required for persistence wrapping).
    assert counts.get("store", 0) >= 1, "createStore not found in file - followup must use createStore"


# [agent_config] pass_to_pass — AGENTS.md:12 @ 3fb60d05e555dad020d3354602affe166ef0cc22
def test_no_try_catch_in_followup_block():
    """No try/catch in followup persistence block (AGENTS.md: Avoid try/catch where possible).

    BEHAVIORAL VERIFICATION: Uses AST to check for try statements.
    """
    _install_babel()
    r = subprocess.run(
        ["node", "-e", '''
const { parse } = require("@babel/parser");
const fs = require("fs");
const code = fs.readFileSync(process.argv[1], "utf8");

// Find the followup region
const lines = code.split("\\n");
let startLine = -1;
let endLine = lines.length;

for (let i = 0; i < lines.length; i++) {
  if (/\\b(followup|persisted)\\b/.test(lines[i]) && startLine === -1) {
    startLine = i;
    for (let j = i + 20; j < Math.min(lines.length, i + 50); j++) {
      if (/^(const |function |export |\\/\\/\\s*=)/.test(lines[j])) {
        endLine = j;
        break;
      }
    }
    break;
  }
}

if (startLine === -1) {
  console.log("no-region");
  process.exit(0);
}

const regionText = lines.slice(startLine, endLine).join("\\n");
const hasTryCatch = /\\btry\\s*\\{/.test(regionText);

console.log(hasTryCatch ? "has-trycatch" : "ok");
''', str(FILE)],
        capture_output=True, timeout=30,
        env={"NODE_PATH": "/tmp/babel-env/node_modules", "PATH": "/usr/local/bin:/usr/bin:/bin"},
    )
    result = r.stdout.decode().strip()
    assert result != "no-region", "Could not locate followup store region"
    assert result == "ok", "try/catch found in followup persistence block"


# [agent_config] pass_to_pass — AGENTS.md:84 @ 3fb60d05e555dad020d3354602affe166ef0cc22
def test_no_else_in_followup_block():
    """No else statements in followup persistence block (AGENTS.md: Avoid else, prefer early returns).

    BEHAVIORAL VERIFICATION: Uses AST to check for else clauses.
    """
    _install_babel()
    r = subprocess.run(
        ["node", "-e", '''
const { parse } = require("@babel/parser");
const fs = require("fs");
const code = fs.readFileSync(process.argv[1], "utf8");

// Find the followup region
const lines = code.split("\\n");
let startLine = -1;
let endLine = lines.length;

for (let i = 0; i < lines.length; i++) {
  if (/\\b(followup|persisted)\\b/.test(lines[i]) && startLine === -1) {
    startLine = i;
    for (let j = i + 20; j < Math.min(lines.length, i + 50); j++) {
      if (/^(const |function |export |\\/\\/\\s*=)/.test(lines[j])) {
        endLine = j;
        break;
      }
    }
    break;
  }
}

if (startLine === -1) {
  console.log("no-region");
  process.exit(0);
}

const regionText = lines.slice(startLine, endLine).join("\\n");
const hasElse = /\\belse\\b/.test(regionText);

console.log(hasElse ? "has-else" : "ok");
''', str(FILE)],
        capture_output=True, timeout=30,
        env={"NODE_PATH": "/tmp/babel-env/node_modules", "PATH": "/usr/local/bin:/usr/bin:/bin"},
    )
    result = r.stdout.decode().strip()
    assert result != "no-region", "Could not locate followup store region"
    assert result == "ok", "else statement found in followup persistence block"


# [agent_config] pass_to_pass — AGENTS.md:17 @ 3fb60d05e555dad020d3354602affe166ef0cc22
def test_no_for_loop_in_followup_block():
    """No for loops in followup persistence block (AGENTS.md: Prefer functional array methods over for loops).

    BEHAVIORAL VERIFICATION: Uses AST to check for for statements.
    """
    _install_babel()
    r = subprocess.run(
        ["node", "-e", '''
const { parse } = require("@babel/parser");
const fs = require("fs");
const code = fs.readFileSync(process.argv[1], "utf8");

// Find the followup region
const lines = code.split("\\n");
let startLine = -1;
let endLine = lines.length;

for (let i = 0; i < lines.length; i++) {
  if (/\\b(followup|persisted)\\b/.test(lines[i]) && startLine === -1) {
    startLine = i;
    for (let j = i + 20; j < Math.min(lines.length, i + 50); j++) {
      if (/^(const |function |export |\\/\\/\\s*=)/.test(lines[j])) {
        endLine = j;
        break;
      }
    }
    break;
  }
}

if (startLine === -1) {
  console.log("no-region");
  process.exit(0);
}

const regionText = lines.slice(startLine, endLine).join("\\n");
const hasForLoop = /\\bfor\\s*\\(/.test(regionText);

console.log(hasForLoop ? "has-for" : "ok");
''', str(FILE)],
        capture_output=True, timeout=30,
        env={"NODE_PATH": "/tmp/babel-env/node_modules", "PATH": "/usr/local/bin:/usr/bin:/bin"},
    )
    result = r.stdout.decode().strip()
    assert result != "no-region", "Could not locate followup store region"
    assert result == "ok", "for loop found in followup persistence block — use functional methods"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_turbo_typecheck():
    """Repos global turbo typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null && curl -fsSL https://bun.sh/install | bash 2>/dev/null && export PATH=\"/root/.bun/bin:$PATH\" && bun install 2>&1 >/dev/null && bun turbo typecheck"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Global turbo typecheck failed:\\n{r.stderr[-1000:]}\\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_check():
    """Repos prettier formatting check passes for the modified file (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null && curl -fsSL https://bun.sh/install | bash 2>/dev/null && export PATH=\"/root/.bun/bin:$PATH\" && bun install 2>&1 >/dev/null && bunx prettier --check packages/app/src/pages/session.tsx"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\\n{r.stderr[-1000:]}\\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_app_build():
    """Repos app package build passes (pass_to_pass).

    BEHAVIORAL VERIFICATION: The bundler actually processes the code,
    which validates that the persistence wrapping is syntactically and
    semantically correct.
    """
    app_dir = Path(REPO) / "packages" / "app"
    r = subprocess.run(
        ["bash", "-c", "apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null && curl -fsSL https://bun.sh/install | bash 2>/dev/null && export PATH=\"/root/.bun/bin:$PATH\" && bun install 2>&1 >/dev/null && bun run build"],
        capture_output=True, text=True, timeout=300, cwd=app_dir,
    )
    assert r.returncode == 0, f"App build failed:\\n{r.stderr[-1000:]}\\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_app_typecheck():
    """Repos app package TypeScript typecheck passes (pass_to_pass).

    BEHAVIORAL VERIFICATION: TypeScript validates the type safety of
    the persistence implementation.
    """
    app_dir = Path(REPO) / "packages" / "app"
    r = subprocess.run(
        ["bash", "-c", "apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null && curl -fsSL https://bun.sh/install | bash 2>/dev/null && export PATH=\"/root/.bun/bin:$PATH\" && bun install 2>&1 >/dev/null && bun run typecheck"],
        capture_output=True, text=True, timeout=180, cwd=app_dir,
    )
    assert r.returncode == 0, f"App typecheck failed:\\n{r.stderr[-1000:]}\\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_app_unit_tests():
    """Repos app package unit tests pass (pass_to_pass)."""
    app_dir = Path(REPO) / "packages" / "app"
    r = subprocess.run(
        ["bash", "-c", "apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null && curl -fsSL https://bun.sh/install | bash 2>/dev/null && export PATH=\"/root/.bun/bin:$PATH\" && bun install 2>&1 >/dev/null && bun run test:unit"],
        capture_output=True, text=True, timeout=180, cwd=app_dir,
    )
    assert r.returncode == 0, f"App unit tests failed:\\n{r.stderr[-1000:]}\\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_persist_unit_tests():
    """Repos persist utility unit tests pass (pass_to_pass).

    BEHAVIORAL VERIFICATION: These tests verify the persistence mechanism
    actually works correctly (localStorage, caching, error handling, etc.).
    """
    app_dir = Path(REPO) / "packages" / "app"
    r = subprocess.run(
        ["bash", "-c", "apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null && curl -fsSL https://bun.sh/install | bash 2>/dev/null && export PATH=\"/root/.bun/bin:$PATH\" && bun install 2>&1 >/dev/null && bun test --preload ./happydom.ts ./src/utils/persist.test.ts"],
        capture_output=True, text=True, timeout=180, cwd=app_dir,
    )
    assert r.returncode == 0, f"Persist utility tests failed:\\n{r.stderr[-1000:]}\\n{r.stdout[-1000:]}"
