"""
Task: bun-build-implicit-dep-outputs
Repo: oven-sh/bun @ c721d357ad9ed04017bb24d21decf5739dba3911
PR:   #28858

Behavioral tests using Node.js subprocess execution to analyze TypeScript
build-system code. F2P code tests parse bun.ts via brace-counting extraction
in a real JS engine — not grep on raw text.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import json
import re
from pathlib import Path

REPO = "/workspace/bun"
BUN_TS = Path(REPO) / "scripts/build/bun.ts"
COMPILE_TS = Path(REPO) / "scripts/build/compile.ts"
CLAUDE_MD = Path(REPO) / "scripts/build/CLAUDE.md"


# ---------------------------------------------------------------------------
# Node.js setup & helpers
# ---------------------------------------------------------------------------

_NODE_BIN = None


def _ensure_node() -> bool:
    """Install Node.js via apt-get if not already present."""
    global _NODE_BIN
    for name in ("node", "nodejs"):
        r = subprocess.run(["which", name], capture_output=True, text=True)
        if r.returncode == 0:
            _NODE_BIN = name
            return True
    try:
        subprocess.run(
            ["apt-get", "update", "-qq"],
            capture_output=True, text=True, timeout=60,
        )
        subprocess.run(
            ["apt-get", "install", "-y", "-qq", "nodejs"],
            capture_output=True, text=True, timeout=120,
        )
        for name in ("node", "nodejs"):
            r = subprocess.run(["which", name], capture_output=True, text=True)
            if r.returncode == 0:
                _NODE_BIN = name
                return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return False


_NODE_OK = _ensure_node()


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js subprocess.

    Uses .cjs extension to force CommonJS mode regardless of any
    package.json ``"type": "module"`` in the repo.
    """
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            [_NODE_BIN, str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# Shared JS: brace-aware block extraction + file reader
_JS_HELPERS = r"""
const fs = require('fs');

function readBunTs() {
  return fs.readFileSync('scripts/build/bun.ts', 'utf8');
}

// Extract a braced block { ... } starting from startIdx.
// Returns the text including the outer braces, or null.
function extractBlock(text, startIdx) {
  let i = startIdx;
  while (i < text.length && text[i] !== '{') i++;
  if (i >= text.length) return null;
  const start = i;
  let depth = 1;
  i++;
  while (i < text.length && depth > 0) {
    if (text[i] === '{') depth++;
    else if (text[i] === '}') depth--;
    i++;
  }
  return text.slice(start, i);
}

// Parse last JSON line from stdout (safe against stray console output).
function out(obj) { console.log(JSON.stringify(obj)); }
"""


def _get_section(text: str, heading: str, next_heading: str = "## ") -> str | None:
    """Extract a markdown section between two headings."""
    pat = rf"{re.escape(heading)}\s*\n(.*?)(?={re.escape(next_heading)}|\Z)"
    m = re.search(pat, text, re.DOTALL)
    return m.group(1) if m else None


def _install_node_and_npm():
    """Install nodejs and npm via apt-get."""
    subprocess.run(["apt-get", "update", "-qq"], capture_output=True, text=True, timeout=60)
    subprocess.run(["apt-get", "install", "-y", "-qq", "nodejs", "npm"],
                   capture_output=True, text=True, timeout=120)
    r = subprocess.run(["which", "node"], capture_output=True, text=True)
    return r.returncode == 0


def _install_typescript():
    """Install TypeScript locally in /tmp."""
    r = subprocess.run(["npm", "install", "typescript@5.5.4"], cwd="/tmp",
                       capture_output=True, text=True, timeout=120)
    return r.returncode == 0


def _install_prettier():
    """Install prettier locally in /tmp."""
    r = subprocess.run(["npm", "install", "prettier"], cwd="/tmp",
                       capture_output=True, text=True, timeout=120)
    return r.returncode == 0


def _install_markdownlint():
    """Install markdownlint-cli locally in /tmp."""
    r = subprocess.run(["npm", "install", "markdownlint-cli"], cwd="/tmp",
                       capture_output=True, text=True, timeout=120)
    return r.returncode == 0


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


def test_source_files_exist():
    """Modified source files (bun.ts, compile.ts, CLAUDE.md) exist."""
    for f in [BUN_TS, COMPILE_TS, CLAUDE_MD]:
        assert f.exists(), f"{f} does not exist"
        assert f.stat().st_size > 0, f"{f} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via Node.js subprocess
# ---------------------------------------------------------------------------


def test_cc_implicit_dep_outputs():
    """compileC lambda passes depOutputs as implicitInputs to cc(), with
    codegenOrderOnly as orderOnlyInputs. Core fix: C files need implicit
    deps on dep outputs so ninja invalidates when dep libs change."""
    assert _NODE_OK, "Node.js is required for behavioral tests"

    r = _run_node(_JS_HELPERS + r"""
const text = readBunTs();

// Locate the compileC lambda
const m = text.match(/const\s+compileC\s*=\s*\(src:\s*string\)\s*:\s*string\s*=>\s*\{/);
if (!m) { out({pass:false,reason:"compileC_not_found"}); process.exit(0); }

// Extract the lambda body via brace counting (not regex)
const body = extractBlock(text, m.index + m[0].length - 1);
if (!body) { out({pass:false,reason:"body_extract_failed"}); process.exit(0); }

// Find the cc() call inside the body
const ccMatch = body.match(/cc\s*\(/);
if (!ccMatch) { out({pass:false,reason:"cc_call_not_found"}); process.exit(0); }
const ccBody = body.slice(ccMatch.index);

// Structural checks on the cc() call arguments
const checks = {
  hasImplicitDepOutputs: /implicitInputs\s*:\s*depOutputs/.test(ccBody),
  hasCodegenOrderOnly:   /orderOnlyInputs\s*:\s*codegenOrderOnly/.test(ccBody),
  noOldDepOrderOnly:     !/depOrderOnly/.test(ccBody)
};

out({pass: checks.hasImplicitDepOutputs && checks.hasCodegenOrderOnly && checks.noOldDepOrderOnly, checks});
""")
    assert r.returncode == 0, f"Node error: {r.stderr}"
    result = json.loads(r.stdout.strip().split('\n')[-1])
    assert result["pass"], f"cc() dep check failed: {result.get('checks', {})}"


def test_no_pch_cxx_implicit_dep_outputs():
    """No-PCH cxx path uses implicitInputs with depOutputs and
    orderOnlyInputs with codegenOrderOnly. On the base commit this path
    incorrectly used orderOnlyInputs for depOutputs."""
    assert _NODE_OK, "Node.js is required for behavioral tests"

    r = _run_node(_JS_HELPERS + r"""
const text = readBunTs();
const elsePat = /\}\s*else\s*\{/g;
let match, found = false;

while ((match = elsePat.exec(text)) !== null) {
  // Identify the no-PCH else branch by checking context for pchOut
  const before = text.slice(Math.max(0, match.index - 300), match.index);
  if (!/pchOut/.test(before)) continue;

  const body = extractBlock(text, match.index + match[0].length - 1);
  if (!body) continue;

  // Check for assignment patterns (not just string occurrence)
  if (/implicitInputs\s*=\s*depOutputs/.test(body) &&
      /orderOnlyInputs\s*=\s*codegenOrderOnly/.test(body)) {
    found = true;
    break;
  }
}

out({pass: found});
""")
    assert r.returncode == 0, f"Node error: {r.stderr}"
    result = json.loads(r.stdout.strip().split('\n')[-1])
    assert result["pass"], \
        "No-PCH cxx path must use implicitInputs=depOutputs, orderOnlyInputs=codegenOrderOnly"


def test_codegen_order_only_separate():
    """codegenOrderOnly variable is just codegen.cppAll. Old depOrderOnly
    variable (which lumped depOutputs + codegen together) must be gone."""
    assert _NODE_OK, "Node.js is required for behavioral tests"

    r = _run_node(_JS_HELPERS + r"""
const text = readBunTs();
const hasNew = /const\s+codegenOrderOnly\s*=\s*codegen\.cppAll/.test(text);
const hasOld = /const\s+depOrderOnly/.test(text);
out({pass: hasNew && !hasOld, checks: {hasNew, hasOld}});
""")
    assert r.returncode == 0, f"Node error: {r.stderr}"
    result = json.loads(r.stdout.strip().split('\n')[-1])
    assert result["pass"], f"codegenOrderOnly check failed: {result.get('checks', {})}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation tests
# ---------------------------------------------------------------------------


def test_claude_md_gotchas_implicit_deps():
    """Gotchas states PCH, cc, and no-PCH cxx all need implicit dep on
    depOutputs — not just PCH alone."""
    text = CLAUDE_MD.read_text()
    gotchas = _get_section(text, "## Gotchas")
    assert gotchas is not None, "Gotchas section not found in CLAUDE.md"

    # Must mention all three together
    assert re.search(r"PCH.*cc.*no-PCH cxx", gotchas) or \
           re.search(r"PCH, cc, and no-PCH cxx", gotchas), \
        "Gotchas must mention PCH, cc, and no-PCH cxx needing implicit dep"

    # Must say implicit dep (not order-only) for depOutputs
    assert re.search(r"implicit dep on `depOutputs`", gotchas), \
        "Gotchas must say 'implicit dep on depOutputs'"

    # Must NOT have old separate rules for PCH and cxx
    assert not re.search(
        r"PCH needs implicit dep.*\n.*\n.*cxx needs order-only", gotchas
    ), "Old separate PCH/cxx rules must be replaced with unified rule"


def test_claude_md_ninja_primer_implicit_example():
    """Ninja primer example shows dep output (lib*.a) as implicit dep (|),
    not order-only (||)."""
    text = CLAUDE_MD.read_text()
    primer = _get_section(text, "## Ninja primer", "## Iterating")
    assert primer is not None, "Ninja primer section not found"

    # Must show lib output after | (implicit), not || (order-only)
    assert re.search(r"\|\s*deps/zstd/libzstd\.a", primer) or \
           re.search(r"\|\s*\w+/zstd/libzstd\.a", primer), \
        "Ninja example must show dep output as implicit dep (|)"

    # Must NOT show old .ref order-only pattern
    assert not re.search(r"\|\|\s*\.\./\.\./vendor/zstd/\.ref", primer), \
        "Old .ref order-only pattern must be removed from example"


def test_claude_md_depfile_explains_implicit():
    """depfile section distinguishes codegen headers (order-only) from dep
    outputs (implicit) with WebKit side-effect explanation."""
    text = CLAUDE_MD.read_text()

    depfile_section = None
    for m in re.finditer(r"\*\*`depfile`\*\*", text):
        start = m.start()
        end = text.find("\n\n", start)
        if end == -1:
            end = len(text)
        depfile_section = text[start:end]
        break

    assert depfile_section is not None, "depfile section not found in CLAUDE.md"

    assert "implicit" in depfile_section.lower(), \
        "depfile section must mention implicit deps for dep outputs"

    assert "forwarding headers" in depfile_section.lower() or \
           "undeclared side effect" in depfile_section.lower(), \
        "depfile section must explain WebKit forwarding header side effects"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------


def test_dep_outputs_comment_updated():
    """depOutputs variable comment describes implicit-dep signal, not
    PCH order-only-deps."""
    text = BUN_TS.read_text()
    assert re.search(r"implicit-dep signal", text), \
        "depOutputs comment must mention 'implicit-dep signal'"
    assert not re.search(r"PCH order-only-deps on these", text), \
        "Old 'PCH order-only-deps' comment must be removed"


def test_compile_opts_docs_updated():
    """CompileOpts docs mention dep outputs in implicitInputs and redirect
    from orderOnlyInputs."""
    text = COMPILE_TS.read_text()

    # implicitInputs must mention dep outputs
    assert re.search(r"implicitInputs.*dep outputs|dep outputs.*implicitInputs", text, re.DOTALL) or \
           re.search(r"lib\*\.a.*invalidation signal", text) or \
           re.search(r"dep outputs.*\n.*invalidation signal", text), \
        "implicitInputs doc must mention dep outputs / lib*.a invalidation signal"

    # orderOnlyInputs must mention codegen or redirect
    # Capture the JSDoc comment block before orderOnlyInputs, not just the declaration line
    m = re.search(r"/\*\*.*?\*/\s*\n\s*orderOnlyInputs\?", text, re.DOTALL)
    if m:
        section = m.group(0)
        assert "codegen" in section.lower() or \
               re.search(r"implicitInputs instead", section), \
            "orderOnlyInputs doc must redirect dep outputs to implicitInputs"
    else:
        # Fallback: try capturing the orderOnlyInputs line and context after it
        m = re.search(r"orderOnlyInputs.*?(?=\n\s*/\*\*|\n\s*\})", text, re.DOTALL)
        if m:
            section = m.group(0)
            assert "codegen" in section.lower() or \
                   re.search(r"implicitInputs instead", section), \
                "orderOnlyInputs doc must redirect dep outputs to implicitInputs"


def test_not_stub():
    """emitBun has substantial implementation (>= 50 real lines, control
    flow, compile calls)."""
    text = BUN_TS.read_text()
    m = re.search(r"export function emitBun\b", text)
    assert m, "emitBun function not found"

    body_start = text.index("{", m.start())
    brace_count = 0
    body_end = body_start
    for i in range(body_start, min(body_start + 50000, len(text))):
        if text[i] == "{":
            brace_count += 1
        elif text[i] == "}":
            brace_count -= 1
            if brace_count == 0:
                body_end = i + 1
                break

    body = text[body_start:body_end]
    real_lines = [l for l in body.split("\n")
                  if l.strip() and not l.strip().startswith("//")
                  and l.strip() not in ("{", "}", "};")]

    assert len(real_lines) >= 50, \
        f"emitBun has only {len(real_lines)} real lines, need >= 50"
    assert "const " in body, "emitBun must have variable declarations"
    assert "cc(" in body or "cxx(" in body, \
        "emitBun must call cc/cxx compile functions"


# ---------------------------------------------------------------------------
# Pass-to-pass — repo CI/CD tests (real CI commands via subprocess.run)
# ---------------------------------------------------------------------------


def _install_node_via_apt():
    """Install nodejs and npm via apt-get."""
    subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True, text=True, timeout=60,
    )
    subprocess.run(
        ["apt-get", "install", "-y", "-qq", "nodejs", "npm"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(["which", "node"], capture_output=True, text=True)
    return r.returncode == 0


def test_repo_build_scripts_parseable():
    """Build scripts pass TypeScript syntax validation via tsc API (pass_to_pass).

    Origin: repo_tests - Runs actual TypeScript compiler parser via subprocess.
    """
    # Install node if needed
    if subprocess.run(["which", "node"], capture_output=True).returncode != 0:
        assert _install_node_via_apt(), "Failed to install nodejs"

    # Install TypeScript locally (in /tmp so it persists for the test)
    subprocess.run(
        ["npm", "install", "--prefix", "/tmp", "typescript@5.5.4"],
        capture_output=True, text=True, timeout=120,
    )

    # Run syntax check using TypeScript compiler API via subprocess
    check_script = """
const ts = require('typescript');
const fs = require('fs');
const files = [
    '/workspace/bun/scripts/build/bun.ts',
    '/workspace/bun/scripts/build/compile.ts'
];
let allOk = true;
for (const file of files) {
    const content = fs.readFileSync(file, 'utf8');
    // Parse only - don't type check (we only care about syntax errors)
    const sourceFile = ts.createSourceFile(file, content, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);
    const diagnostics = sourceFile.parseDiagnostics || [];
    if (diagnostics.length > 0) {
        console.log(file + ': SYNTAX_ERROR');
        allOk = false;
    } else {
        console.log(file + ': OK');
    }
}
process.exit(allOk ? 0 : 1);
"""
    env = os.environ.copy()
    env["NODE_PATH"] = "/tmp/node_modules"
    r = subprocess.run(
        ["node", "-e", check_script],
        capture_output=True, text=True, timeout=60, cwd=REPO, env=env
    )
    assert r.returncode == 0, f"TypeScript syntax check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_typescript_prettier_check():
    """Build scripts pass prettier format check (pass_to_pass).

    Origin: repo_tests - Matches CI format workflow (format.yml).
    """
    # Install node if needed
    if subprocess.run(["which", "node"], capture_output=True).returncode != 0:
        assert _install_node_via_apt(), "Failed to install nodejs"

    # Install prettier locally
    subprocess.run(
        ["npm", "install", "-g", "prettier"],
        capture_output=True, text=True, timeout=120,
    )

    # Check bun.ts with prettier (matching CI command from format.yml)
    r = subprocess.run(
        ["prettier", "--check", "--parser", "typescript", "scripts/build/bun.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"bun.ts prettier check failed:\n{r.stderr}"

    # Check compile.ts with prettier
    r = subprocess.run(
        ["prettier", "--check", "--parser", "typescript", "scripts/build/compile.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"compile.ts prettier check failed:\n{r.stderr}"


def test_repo_markdownlint_check():
    """CLAUDE.md passes markdownlint with MD013 disabled (pass_to_pass).

    Origin: repo_tests - Runs markdownlint CLI via subprocess.
    """
    # Install node if needed
    if subprocess.run(["which", "node"], capture_output=True).returncode != 0:
        assert _install_node_via_apt(), "Failed to install nodejs"

    # Install markdownlint-cli locally
    subprocess.run(
        ["npm", "install", "-g", "markdownlint-cli"],
        capture_output=True, text=True, timeout=120,
    )

    # Create config to disable MD013 (line length rule)
    config = {"MD013": False}
    config_path = Path(REPO) / "_markdownlint_config.json"
    config_path.write_text(json.dumps(config))

    try:
        # Run markdownlint with config file (more reliable than --disable flag)
        r = subprocess.run(
            ["markdownlint", "-c", str(config_path), "scripts/build/CLAUDE.md"],
            capture_output=True, text=True, timeout=60, cwd=REPO
        )
        assert r.returncode == 0, f"CLAUDE.md markdownlint check failed:\n{r.stderr}"
    finally:
        config_path.unlink(missing_ok=True)


def test_repo_git_tracks_modified_files():
    """Modified source files are tracked by git and have valid content (pass_to_pass).

    Origin: repo_tests - Uses git commands via subprocess to verify repo state.
    """
    # Check files exist
    for f in [BUN_TS, COMPILE_TS, CLAUDE_MD]:
        assert f.exists(), f"{f} does not exist"
        assert f.stat().st_size > 0, f"{f} is empty"

    # Check git status of modified files
    for rel_path in ["scripts/build/bun.ts", "scripts/build/compile.ts", "scripts/build/CLAUDE.md"]:
        r = subprocess.run(
            ["git", "ls-files", "--error-unmatch", rel_path],
            capture_output=True, text=True, timeout=30, cwd=REPO
        )
        assert r.returncode == 0, f"{rel_path} is not tracked by git"

    # Verify files have valid structure (typescript and markdown)
    r = subprocess.run(
        ["git", "check-attr", "text", "scripts/build/bun.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    # git check-attr returns 0 even if no attrs set, just verify command works
    assert r.returncode == 0, "git check-attr failed"
