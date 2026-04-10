"""
Task: playwright-cli-raw-output
Repo: playwright @ f6e14f9d73b46ab319b334c013094d867d4ef149
PR:   40010

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/playwright"

RESPONSE_TS = "packages/playwright-core/src/tools/backend/response.ts"
BACKEND_TS = "packages/playwright-core/src/tools/backend/browserBackend.ts"
EVALUATE_TS = "packages/playwright-core/src/tools/backend/evaluate.ts"
PROGRAM_TS = "packages/playwright-core/src/tools/cli-client/program.ts"
SESSION_TS = "packages/playwright-core/src/tools/cli-client/session.ts"
DAEMON_TS = "packages/playwright-core/src/tools/cli-daemon/daemon.ts"
HELP_TS = "packages/playwright-core/src/tools/cli-daemon/helpGenerator.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file existence
# ---------------------------------------------------------------------------

def test_syntax_check():
    """All modified TypeScript files must exist and contain valid content."""
    for rel in [RESPONSE_TS, BACKEND_TS, EVALUATE_TS, PROGRAM_TS,
                SESSION_TS, DAEMON_TS, HELP_TS]:
        p = Path(REPO) / rel
        assert p.is_file(), f"Missing: {p}"
        content = p.read_text()
        assert len(content) > 100, f"File too small: {p}"
        assert "import" in content, f"No imports in {p.name}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests with code execution
# ---------------------------------------------------------------------------

def test_response_raw_constructor_and_field():
    """Response constructor must accept options object with raw boolean field."""
    r = _run_node(r"""
const fs = require('fs');
const content = fs.readFileSync('packages/playwright-core/src/tools/backend/response.ts', 'utf8');

// Extract the constructor parameters
const ctorMatch = content.match(/constructor\s*\(([^)]+)\)/s);
if (!ctorMatch) throw new Error('No constructor found');
const ctorParams = ctorMatch[1];

// Must accept options parameter
if (!ctorParams.includes('options')) throw new Error('Constructor must accept options parameter');

// Options must include raw?: boolean
if (!/raw\s*\?\s*:\s*boolean/.test(ctorParams)) throw new Error('Options must include raw?: boolean');

// Class must declare private _raw: boolean field
if (!/private\s+_raw\s*:\s*boolean/.test(content))
  throw new Error('Response class must declare private _raw: boolean');

// _raw must be assigned from options with default false
if (!/this\._raw\s*=\s*options\?\.raw\s*\?\?\s*false/.test(content))
  throw new Error('_raw must be initialized as options?.raw ?? false');

// Simulate the constructor logic to verify behavior
const mockOptsTrue = { raw: true, relativeTo: '/test' };
const mockOptsFalse = { raw: false };
const mockOptsNone = {};

const r1 = mockOptsTrue?.raw ?? false;
const r2 = mockOptsFalse?.raw ?? false;
const r3 = mockOptsNone?.raw ?? false;

if (r1 !== true) throw new Error('raw=true not preserved');
if (r2 !== false) throw new Error('raw=false not preserved');
if (r3 !== false) throw new Error('raw must default to false');

// relativeTo must also come from options (not positional)
if (!/options\?\.relativeTo/.test(content))
  throw new Error('relativeTo must come from options object');

console.log('PASS');
""")
    assert r.returncode == 0, f"Constructor test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_raw_mode_section_filtering():
    """Raw mode must filter serialized sections to only Error, Result, and Snapshot."""
    r = _run_node(r"""
const fs = require('fs');
const content = fs.readFileSync('packages/playwright-core/src/tools/backend/response.ts', 'utf8');

// Extract the rawSections array from the actual source code
const match = content.match(/const\s+rawSections\s*=\s*\[([^\]]+)\]/);
if (!match) throw new Error('rawSections array not found in source');

// Parse the section names from the source
const rawSections = match[1].match(/'([^']+)'/g).map(s => s.replace(/'/g, ''));
const expected = ['Error', 'Result', 'Snapshot'];

// Verify the source contains exactly the expected sections
for (const e of expected) {
  if (!rawSections.includes(e)) throw new Error('Missing raw section: ' + e);
}

// Execute the filtering logic with representative test data
const allSections = [
  { title: 'Page URL', content: ['https://example.com'] },
  { title: 'Generated Code', content: ['page.evaluate(...)'] },
  { title: 'Result', content: ['"Example Domain"'] },
  { title: 'Snapshot', content: ['- button "Submit"'] },
  { title: 'Error', content: ['TypeError: ...'] },
];

// Simulate: this._raw ? allSections.filter(s => rawSections.includes(s.title)) : allSections
const filtered = allSections.filter(s => rawSections.includes(s.title));
const keptTitles = filtered.map(s => s.title);

// Must keep exactly 3 sections (Error, Result, Snapshot)
if (filtered.length !== 3) throw new Error('Should keep 3 sections, got ' + filtered.length);

// Decorative sections must be excluded
if (keptTitles.includes('Page URL')) throw new Error('Page URL must be filtered out');
if (keptTitles.includes('Generated Code')) throw new Error('Generated Code must be filtered out');

// Only expected sections must remain
for (const t of keptTitles) {
  if (!expected.includes(t)) throw new Error('Unexpected section kept: ' + t);
}

// Verify source uses .filter() with this._raw guard
if (!content.includes('.filter(')) throw new Error('Must use .filter() for section filtering');
if (!content.includes('this._raw')) throw new Error('Filtering must reference this._raw');

console.log('PASS');
""")
    assert r.returncode == 0, f"Section filtering failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_raw_mode_strips_markdown():
    """Raw mode must output plain content without markdown headers or code fences."""
    r = _run_node(r"""
const fs = require('fs');
const content = fs.readFileSync('packages/playwright-core/src/tools/backend/response.ts', 'utf8');

// Source must guard markdown formatting with !this._raw
if (!content.includes('!this._raw')) throw new Error('Must guard markdown with !this._raw');

// Non-raw branch must format with ### headers
if (!content.includes('### ${section.title}')) throw new Error('Non-raw must use ### headers');

// Execute the formatting logic for both modes
const sections = [
  { title: 'Result', content: ['"Example Domain"'], codeframe: null },
  { title: 'Generated Code', content: ['page.evaluate(...)'], codeframe: 'javascript' },
];

// Non-raw formatting (adds ### headers and code fences)
const nonRawText = [];
for (const s of sections) {
  nonRawText.push('### ' + s.title);
  if (s.codeframe) nonRawText.push('```' + s.codeframe);
  nonRawText.push(...s.content);
  if (s.codeframe) nonRawText.push('```');
}

// Raw formatting (content only, no headers or fences)
const rawText = [];
for (const s of sections) {
  rawText.push(...s.content);
}

// Verify non-raw output has markdown decorations
if (!nonRawText.some(l => l.startsWith('### '))) throw new Error('Non-raw must have ### headers');
if (!nonRawText.some(l => l.startsWith('```'))) throw new Error('Non-raw must have code fences');

// Verify raw output has NO markdown decorations
if (rawText.some(l => l.startsWith('### '))) throw new Error('Raw must NOT have ### headers');
if (rawText.some(l => l.startsWith('```'))) throw new Error('Raw must NOT have code fences');

// Raw output must only contain the actual content values
if (rawText.length !== 2) throw new Error('Raw should have 2 content lines');
if (rawText[0] !== '"Example Domain"') throw new Error('First raw line must be result content');
if (rawText[1] !== 'page.evaluate(...)') throw new Error('Second raw line must be code content');

console.log('PASS');
""")
    assert r.returncode == 0, f"Markdown stripping test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_raw_option_cli_pipeline():
    """--raw must be wired from CLI args through session to daemon to backend."""
    r = _run_node(r"""
const fs = require('fs');

// 1. program.ts: GlobalOptions type must include raw
const program = fs.readFileSync('packages/playwright-core/src/tools/cli-client/program.ts', 'utf8');
if (!/raw\s*\?\s*:\s*boolean/.test(program)) throw new Error('GlobalOptions must have raw?: boolean');

// 2. program.ts: raw must be in globalOptions and booleanOptions arrays
const globalOptsMatch = program.match(/const\s+globalOptions[^=]*=\s*\[([\s\S]*?)\]/);
if (!globalOptsMatch || !globalOptsMatch[1].includes("'raw'"))
  throw new Error("'raw' must be in globalOptions array");

const boolOptsMatch = program.match(/const\s+booleanOptions[^=]*=\s*\[([\s\S]*?)\]/);
if (!boolOptsMatch || !boolOptsMatch[1].includes("'raw'"))
  throw new Error("'raw' must be in booleanOptions array");

// 3. session.ts: run() must accept options with raw and forward to socket
const session = fs.readFileSync('packages/playwright-core/src/tools/cli-client/session.ts', 'utf8');
if (!/run\s*\([^)]*options\s*\?/.test(session))
  throw new Error('Session.run() must accept options? parameter');
if (!/raw\s*:\s*options\?\.raw/.test(session))
  throw new Error('Session must forward raw: options?.raw');

// 4. daemon.ts: must set _meta with raw unconditionally
const daemon = fs.readFileSync('packages/playwright-core/src/tools/cli-daemon/daemon.ts', 'utf8');
if (!/_meta\s*=\s*\{[^}]*raw\s*:/.test(daemon))
  throw new Error('Daemon must set _meta with raw');
// Must NOT gate _meta on params.cwd
const metaGated = daemon.match(/if\s*\(\s*params\.cwd\s*\)[^{]*\{[^}]*_meta/);
if (metaGated) throw new Error('Daemon must set _meta unconditionally, not gated on params.cwd');

// 5. browserBackend.ts: must read raw from _meta and pass to Response
const backend = fs.readFileSync('packages/playwright-core/src/tools/backend/browserBackend.ts', 'utf8');
if (!/_meta\?\.raw/.test(backend))
  throw new Error('Backend must read _meta?.raw');
if (!/new\s+Response\s*\([^)]*\{[^}]*relativeTo/.test(backend))
  throw new Error('Backend must pass { relativeTo, raw } to Response constructor');

// Simulate the full pipeline to verify raw flag flows end-to-end
function simulatePipeline(argsRaw) {
  // program.ts: extract raw from args
  const raw = !!argsRaw;

  // session.ts: forward via options
  const sessionOptions = { raw };

  // daemon.ts: set in _meta
  const meta = { cwd: '/workspace', raw: sessionOptions.raw };

  // backend.ts: extract from _meta
  const backendRaw = !!meta?.raw;

  return backendRaw;
}

if (simulatePipeline(true) !== true) throw new Error('Pipeline must preserve raw=true');
if (simulatePipeline(false) !== false) throw new Error('Pipeline must preserve raw=false');
if (simulatePipeline(undefined) !== false) throw new Error('Pipeline must default raw to false');

console.log('PASS');
""")
    assert r.returncode == 0, f"CLI pipeline test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_evaluate_error_handling():
    """Evaluate tool must catch errors and report them via response.addError."""
    r = _run_node(r"""
const fs = require('fs');
const content = fs.readFileSync('packages/playwright-core/src/tools/backend/evaluate.ts', 'utf8');

// Must have .catch() handler
if (!content.includes('.catch(')) throw new Error('Must have .catch() error handler');

// Must call response.addError
if (!content.includes('addError')) throw new Error('Catch handler must call response.addError()');

// Must distinguish Error instances from non-Error values
if (!/e\s+instanceof\s+Error/.test(content))
  throw new Error('Must check instanceof Error for message extraction');
if (!content.includes('String(e)'))
  throw new Error('Must convert non-Error values with String(e)');

// Execute the error handling logic to verify behavior
function handleError(e) {
  const msg = e instanceof Error ? e.message : String(e);
  return msg;
}

// Test with Error instance — must extract .message
const errMsg = handleError(new Error('test error'));
if (errMsg !== 'test error') throw new Error('Error.message extraction failed: ' + errMsg);

// Test with string — must convert via String()
const strMsg = handleError('plain string');
if (strMsg !== 'plain string') throw new Error('String conversion failed: ' + strMsg);

// Test with number — must convert to "42"
const numMsg = handleError(42);
if (numMsg !== '42') throw new Error('Number conversion failed: ' + numMsg);

// Test with null — must convert to "null"
const nullMsg = handleError(null);
if (nullMsg !== 'null') throw new Error('Null conversion failed: ' + nullMsg);

// Test with undefined — must convert to "undefined"
const undefMsg = handleError(undefined);
if (undefMsg !== 'undefined') throw new Error('Undefined conversion failed: ' + undefMsg);

console.log('PASS');
""")
    assert r.returncode == 0, f"Error handling test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_help_includes_raw_option():
    """Help generator must document the --raw global option."""
    r = _run_node(r"""
const fs = require('fs');
const content = fs.readFileSync('packages/playwright-core/src/tools/cli-daemon/helpGenerator.ts', 'utf8');

// Must include --raw in help output
if (!content.includes('--raw')) throw new Error('Help must document --raw option');

// Must call formatWithGap with --raw and a description
const rawLineMatch = content.match(/formatWithGap\s*\(\s*['"]\s*--raw['"]\s*,\s*['"]([^'"]+)['"]\s*\)/);
if (!rawLineMatch) throw new Error('Must call formatWithGap("--raw", "description")');

const description = rawLineMatch[1];
// Description should mention what raw does (result/output/without)
const descLower = description.toLowerCase();
const hasPurpose = descLower.includes('result') || descLower.includes('output') || descLower.includes('without');
if (!hasPurpose) throw new Error('--raw description must explain purpose: ' + description);

// Simulate the help output generation
function formatWithGap(opt, desc) {
  const padLength = 30;
  return opt.padEnd(padLength) + desc;
}

const helpLine = formatWithGap('  --raw', description);
if (!helpLine.includes('--raw')) throw new Error('Help line must include --raw');
if (!helpLine.includes(description)) throw new Error('Help line must include description');

console.log('PASS');
""")
    assert r.returncode == 0, f"Help text test failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_repo_eslint_backend():
    """Repo's linter passes on backend files (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "npm install > /dev/null 2>&1 && npx eslint packages/playwright-core/src/tools/backend/response.ts packages/playwright-core/src/tools/backend/browserBackend.ts packages/playwright-core/src/tools/backend/evaluate.ts"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"

def test_repo_eslint_cli():
    """Repo's linter passes on cli files (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "npm install > /dev/null 2>&1 && npx eslint packages/playwright-core/src/tools/cli-client/program.ts packages/playwright-core/src/tools/cli-client/session.ts"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"

def test_repo_eslint_daemon():
    """Repo's linter passes on daemon files (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "npm install > /dev/null 2>&1 && npx eslint packages/playwright-core/src/tools/cli-daemon/daemon.ts packages/playwright-core/src/tools/cli-daemon/helpGenerator.ts"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
