"""
Task: prisma-featcli-update-bundled-prismastudiocore-to
Repo: prisma/prisma @ 32fb24b53c2a46971f3093eee9934c18e0f47642
PR:   29376

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/prisma"
STUDIO_TS = Path(REPO) / "packages" / "cli" / "src" / "Studio.ts"
AGENTS_MD = Path(REPO) / "AGENTS.md"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# pass_to_pass (static) — syntax / regression checks
# ---------------------------------------------------------------------------

def test_repo_prettier():
    """Repo's Prettier formatting check passes (pass_to_pass)."""
    # Run in bash with corepack enabled
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/prisma && corepack enable && pnpm install --frozen-lockfile >/dev/null 2>&1 && pnpm run prettier-check"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_engines_override():
    """Repo's engines override check passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/prisma && corepack enable && pnpm install --frozen-lockfile >/dev/null 2>&1 && pnpm run check-engines-override"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Engines override check failed:\n{r.stderr[-500:]}"


def test_studio_syntax_node_check():
    """Studio.ts must pass Node.js syntax validation (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", str(STUDIO_TS)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Studio.ts syntax check failed:\n{r.stderr}"


def test_syntax_check():
    """Studio.ts must be valid TypeScript (no unterminated strings or brackets)."""
    content = STUDIO_TS.read_text()
    opens = content.count("{") + content.count("(") + content.count("[")
    closes = content.count("}") + content.count(")") + content.count("]")
    assert abs(opens - closes) < 10, (
        f"Bracket imbalance detected: opens={opens}, closes={closes}"
    )
    assert "Studio" in content, "Studio class/reference missing"


def test_existing_bff_procedures_preserved():
    """Existing BFF procedures (query, sequence, sql-lint) must still be present."""
    content = STUDIO_TS.read_text()
    for proc in ["query", "sequence", "sql-lint"]:
        assert re.search(
            rf"procedure\s*===?\s*['\"]{ re.escape(proc) }['\"]", content
        ), f"BFF procedure '{proc}' must still be handled in Studio.ts"


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — behavioral code-execution tests
# ---------------------------------------------------------------------------

def test_transaction_procedure_handler():
    """BFF must handle 'transaction' procedure with executeTransaction and error handling."""
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/cli/src/Studio.ts', 'utf8');

// 1. Must have a transaction procedure check
const txMatch = src.match(/if\\s*\\(\\s*procedure\\s*===\\s*['"]transaction['"]\\s*\\)/);
if (!txMatch) {
    console.error('NO_TX_HANDLER: no procedure === "transaction" check found');
    process.exit(1);
}

// 2. Extract the handler block (from match to the next procedure check)
const start = txMatch.index;
const rest = src.slice(start);
const nextProc = rest.slice(1).search(/if\\s*\\(\\s*procedure\\s*===/);
const block = nextProc > 0 ? rest.slice(0, nextProc + 1) : rest.slice(0, 600);

// 3. Must call executeTransaction
if (!block.includes('executeTransaction')) {
    console.error('NO_EXECUTE_TRANSACTION: handler must call executor.executeTransaction');
    process.exit(1);
}

// 4. Must have error handling (serializeBffError or error check)
if (!block.includes('serializeBffError') && !block.match(/error/i)) {
    console.error('NO_ERROR_HANDLING: handler must handle errors');
    process.exit(1);
}

// 5. Must return a response via ctx.json
if (!block.includes('ctx.json')) {
    console.error('NO_RESPONSE: handler must return ctx.json(...)');
    process.exit(1);
}

// 6. Must have substantive logic (not a one-liner stub)
const lines = block.split('\\n').filter(l => l.trim().length > 0);
if (lines.length < 5) {
    console.error('STUB: handler has only ' + lines.length + ' lines — too short');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Transaction handler validation failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_favicon_endpoint():
    """Studio must serve a valid SVG favicon at /favicon.ico with link tag in HTML."""
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/cli/src/Studio.ts', 'utf8');

// 1. Must register a /favicon.ico route
if (!src.match(/['"]\\/favicon\\.ico['"]/)) {
    console.error('NO_FAVICON_ROUTE');
    process.exit(1);
}

// 2. Must serve as image/svg+xml content type
if (!src.includes('image/svg+xml')) {
    console.error('NO_SVG_CONTENT_TYPE');
    process.exit(1);
}

// 3. Must contain an SVG element (the favicon body)
const svgMatch = src.match(/<svg[\\s\\S]*?<\\/svg>/);
if (!svgMatch) {
    console.error('NO_SVG_CONTENT: no <svg>...</svg> found');
    process.exit(1);
}
const svg = svgMatch[0];
if (!svg.includes('viewBox') || !svg.includes('xmlns')) {
    console.error('INVALID_SVG: missing viewBox or xmlns');
    process.exit(1);
}

// 4. HTML template must have <link rel="icon"> referencing the favicon
if (!src.includes('rel="icon"')) {
    console.error('NO_ICON_LINK: HTML template missing <link rel="icon">');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Favicon validation failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_import_map_includes_radix_toggle():
    """Import map must include @radix-ui/react-toggle with React dep pinning."""
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/cli/src/Studio.ts', 'utf8');

// 1. Must reference @radix-ui/react-toggle somewhere
if (!src.includes('@radix-ui/react-toggle')) {
    console.error('NO_RADIX_TOGGLE');
    process.exit(1);
}

// 2. Find the import map block in the HTML template
// Look from 'importmap' to the closing </script> tag
const mapStart = src.indexOf('importmap');
if (mapStart === -1) {
    console.error('NO_IMPORT_MAP');
    process.exit(1);
}
const mapEnd = src.indexOf('</script>', mapStart);
const mapBlock = mapEnd > 0 ? src.slice(mapStart, mapEnd) : src.slice(mapStart, mapStart + 2000);

// 3. Check that imports section exists and contains @radix-ui/react-toggle
const importsMatch = mapBlock.match(/"imports"\\s*:\\s*\\{/);
if (!importsMatch) {
    console.error('NO_IMPORTS_SECTION');
    process.exit(1);
}

// 4. @radix-ui/react-toggle must be a key in the imports
if (!mapBlock.includes('@radix-ui/react-toggle')) {
    console.error('RADIX_NOT_IN_IMPORTS: found in file but not in import map');
    process.exit(1);
}

// 5. The URL (constant or literal) must pin React deps to avoid hook crashes
// Check either a literal ?deps=react@ in the import map URL,
// or a constant that resolves to such a URL
const hasLiteralPin = mapBlock.includes('deps=react@');
const constName = mapBlock.match(/@radix-ui\\/react-toggle"\\s*:\\s*"\\$\\{(\\w+)\\}"/);
let hasConstPin = false;
if (constName) {
    const constDef = src.match(new RegExp('const\\\\s+' + constName[1] + '\\\\s*='));
    // Check that the constant definition includes deps=react@
    const constLine = src.slice(src.indexOf('const ' + constName[1]));
    const endOfConst = constLine.indexOf('\\n');
    const constVal = constLine.slice(0, endOfConst > 0 ? endOfConst : 200);
    hasConstPin = constVal.includes('deps=react@');
}
if (!hasLiteralPin && !hasConstPin) {
    // Fallback: check if anywhere a constant with radix in the name has deps=react@
    const radixConst = src.match(/const\\s+\\w*(?:RADIX|radix)\\w*\\s*=\\s*[`'"][^`'"]*deps=react@/i);
    if (!radixConst) {
        console.error('NO_REACT_PIN: radix toggle URL must pin React deps');
        process.exit(1);
    }
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Radix toggle validation failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_import_map_includes_chartjs():
    """Import map must include chart.js/auto via esm.sh."""
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/cli/src/Studio.ts', 'utf8');

// 1. Must reference chart.js/auto
if (!src.includes('chart.js/auto')) {
    console.error('NO_CHARTJS');
    process.exit(1);
}

// 2. Find the import map block
// Look from 'importmap' to the closing </script> tag
const mapStart = src.indexOf('importmap');
if (mapStart === -1) {
    console.error('NO_IMPORT_MAP');
    process.exit(1);
}
const mapEnd = src.indexOf('</script>', mapStart);
const mapBlock = mapEnd > 0 ? src.slice(mapStart, mapEnd) : src.slice(mapStart, mapStart + 2000);

// 3. Check that imports section exists
const importsMatch = mapBlock.match(/"imports"\\s*:\\s*\\{/);
if (!importsMatch) {
    console.error('NO_IMPORTS_SECTION');
    process.exit(1);
}

// 4. chart.js/auto must be a key in the imports block
if (!mapBlock.includes('chart.js/auto')) {
    console.error('CHARTJS_NOT_IN_IMPORTS');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Chart.js validation failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_react_version_constant():
    """React version must be a constant, not hardcoded in multiple import map URLs."""
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/cli/src/Studio.ts', 'utf8');

// 1. Locate the import map section
const mapStart = src.indexOf('importmap');
if (mapStart === -1) {
    console.error('NO_IMPORT_MAP');
    process.exit(1);
}
const mapEnd = src.indexOf('</script>', mapStart);
const mapBlock = src.slice(mapStart, mapEnd);

// 2. Count hardcoded React version URLs (e.g. esm.sh/react@19.2.0)
const hardcoded = (mapBlock.match(/esm\\.sh\\/react@\\d+\\.\\d+\\.\\d+/g) || []).length;
if (hardcoded >= 2) {
    console.error('HARDCODED_REACT: found ' + hardcoded + ' hardcoded React version URLs');
    process.exit(1);
}

// 3. Verify a REACT_VERSION (or similar) constant exists
const hasConst = src.match(/const\\s+REACT[_A-Z]*VERSION\\s*=\\s*['"`]/);
if (!hasConst) {
    // Also accept template variable usage in the import map
    const hasTemplateVar = mapBlock.includes('${') && mapBlock.match(/REACT/);
    if (!hasTemplateVar) {
        console.error('NO_REACT_CONSTANT');
        process.exit(1);
    }
}

console.log('PASS');
""")
    assert r.returncode == 0, f"React version constant check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — AGENTS.md documentation tests
# ---------------------------------------------------------------------------

def test_agents_md_studio_import_map_docs():
    """AGENTS.md must document Studio import map alignment with new browser imports."""
    content = AGENTS_MD.read_text()
    has_import_map = "import map" in content.lower() or "importmap" in content.lower()
    has_specific = any(term in content for term in [
        "@radix-ui/react-toggle",
        "bare browser imports",
        "chart.js/auto",
    ])
    assert has_import_map and has_specific, (
        "AGENTS.md must document that Studio import map needs alignment "
        "with new browser imports (e.g. @radix-ui/react-toggle, chart.js/auto)"
    )


def test_agents_md_react_pinning_docs():
    """AGENTS.md must document esm.sh React version pinning pattern."""
    content = AGENTS_MD.read_text()
    has_esm_sh = "esm.sh" in content
    has_react_pin = any(term in content for term in [
        "deps=react@",
        "pin",
    ])
    assert has_esm_sh and has_react_pin, (
        "AGENTS.md must document the esm.sh React pinning pattern "
        "to avoid invalid-hook-call crashes"
    )
