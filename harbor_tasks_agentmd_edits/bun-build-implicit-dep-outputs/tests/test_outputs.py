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
# Pass-to-pass — repo CI/CD tests
# ---------------------------------------------------------------------------


def test_repo_build_scripts_parseable():
    """Build scripts are syntactically valid TypeScript (pass_to_pass)."""
    assert _NODE_OK, "Node.js is required for syntax validation"

    for ts_file in [BUN_TS, COMPILE_TS]:
        code = r"""
const fs = require('fs');
const text = fs.readFileSync('%s', 'utf8');

// Basic structural validation for TypeScript files
const checks = {
    hasImports: /import\s*\{/.test(text) || /import\s+\w+\s+from/.test(text),
    hasExports: /export\s+(function|const|interface|class|type)/.test(text),
    balancedBraces: (text.match(/\{/g) || []).length === (text.match(/\}/g) || []).length,
    balancedParens: (text.match(/\(/g) || []).length === (text.match(/\)/g) || []).length,
    noUnclosedComments: !/\/\*[^*]*\*+(?:[^/*][^*]*\*+)*\//.test(text.replace(/\/\*[\s\S]*?\*\//g, ''))
};

console.log(JSON.stringify({pass: Object.values(checks).every(Boolean), checks, file: '%s'}));
""" % (str(ts_file).replace('\\', '/'), ts_file.name)

        r = _run_node(code, timeout=30)
        assert r.returncode == 0, f"Node.js error parsing {ts_file.name}: {r.stderr}"
        result = json.loads(r.stdout.strip().split('\n')[-1])
        assert result["pass"], f"{ts_file.name} failed syntax checks: {result.get('checks', {})}"


def test_repo_claude_md_valid():
    """CLAUDE.md is valid markdown with expected sections (pass_to_pass)."""
    text = CLAUDE_MD.read_text()

    # Check for required sections
    required_sections = ["## Ninja primer", "## Gotchas", "## Iterating"]
    for section in required_sections:
        assert section in text, f"CLAUDE.md missing section: {section}"

    # Check markdown structure
    assert text.count("#") > 5, "CLAUDE.md should have multiple headings"
    assert "```" in text, "CLAUDE.md should have code blocks"
    assert len(text.split('\n')) > 50, "CLAUDE.md should have substantial content"
