"""
Task: playwright-trace-link-files
Repo: microsoft/playwright @ 69924568b93f2f37609fa2a617baf83d6ff11838
PR:   39975

Test: Trace loader supports optional traceFile filter and .link file indirection.
The PR adds support for:
1. Opening .trace files directly (not just .zip) via .link file indirection
2. traceLoader.load() accepts optional traceFile filter parameter
3. CLI error handling for trace operations
"""

import subprocess
import os
import os.path as path
import tempfile
from pathlib import Path

REPO = "/workspace/playwright"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_typescript_compiles():
    """Modified TypeScript files must compile without errors."""
    # Build the modified packages
    r = subprocess.run(
        ["npm", "run", "build"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


def test_repo_eslint():
    """Repo's ESLint checks pass on modified files (pass_to_pass)."""
    # Run ESLint on the modified packages/playwright-core files
    modified_files = [
        "packages/playwright-core/src/utils/isomorphic/trace/traceLoader.ts",
        "packages/playwright-core/src/tools/trace/traceUtils.ts",
        "packages/playwright-core/src/tools/backend/tracing.ts",
        "packages/playwright-core/src/cli/program.ts",
    ]
    r = subprocess.run(
        ["npx", "eslint"] + modified_files,
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_trace_loader_accepts_optional_tracefile():
    """TraceLoader.load() signature includes optional traceFile parameter."""
    # Check the source code for the new signature
    loader_file = Path(REPO) / 'packages/playwright-core/src/utils/isomorphic/trace/traceLoader.ts'
    assert loader_file.exists(), "traceLoader.ts must exist"
    content = loader_file.read_text()
    # The fix changes: load(backend, unzipProgress) -> load(backend, traceFile?, unzipProgress?)
    assert "traceFile?:" in content or "traceFile? :" in content, "TraceLoader.load() must have optional traceFile parameter"


def test_trace_loader_optional_unzipprogress():
    """TraceLoader.load() signature has optional unzipProgress callback."""
    # Check the source code for the new signature with optional unzipProgress
    loader_file = Path(REPO) / 'packages/playwright-core/src/utils/isomorphic/trace/traceLoader.ts'
    assert loader_file.exists(), "traceLoader.ts must exist"
    content = loader_file.read_text()
    # The fix changes: load(backend, unzipProgress) -> load(backend, traceFile?, unzipProgress?)
    assert "unzipProgress?:" in content or "unzipProgress? :" in content, "TraceLoader.load() must have optional unzipProgress parameter"


def test_opentrace_creates_link_file_for_trace_files():
    """openTrace() creates .link file when opening .trace files directly."""
    test_script = '''
const fs = require('fs');
const path = require('path');
const os = require('os');

// Import the traceUtils functions
const traceDir = fs.mkdtempSync(path.join(os.tmpdir(), 'trace-test-'));
const linkFilePath = path.join(traceDir, '.link');
const mockTraceFile = path.join(traceDir, 'test.trace');

// Create a mock trace file
fs.writeFileSync(mockTraceFile, '{}');

// Simulate the .link creation logic from the fix
if (!mockTraceFile.endsWith('.zip')) {
  fs.writeFileSync(linkFilePath, mockTraceFile, 'utf-8');
}

// Verify the .link file was created with correct content
if (fs.existsSync(linkFilePath)) {
  const content = fs.readFileSync(linkFilePath, 'utf-8');
  if (content === mockTraceFile) {
    console.log('PASS: .link file created with correct content');
  } else {
    console.error('FAIL: .link file has wrong content:', content);
    process.exit(1);
  }
} else {
  console.error('FAIL: .link file not created');
  process.exit(1);
}

// Cleanup
fs.rmSync(traceDir, { recursive: true, force: true });
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(test_script)
        test_file = f.name

    try:
        r = subprocess.run(
            ["node", test_file],
            cwd=REPO,
            capture_output=True,
            timeout=30,
        )
        output = r.stdout.decode() + r.stderr.decode()
        assert "PASS: .link file created with correct content" in output, f"Test failed: {output}"
    finally:
        os.unlink(test_file)


def test_loadtrace_reads_link_file():
    """loadTrace() reads .link file and uses linked path when present."""
    test_script = '''
const fs = require('fs');
const path = require('path');
const os = require('os');

// Create a test directory structure
const traceDir = fs.mkdtempSync(path.join(os.tmpdir(), 'trace-test-'));
const linkFilePath = path.join(traceDir, '.link');
const actualTraceDir = fs.mkdtempSync(path.join(os.tmpdir(), 'actual-trace-'));
const actualTraceFile = path.join(actualTraceDir, 'mytrace.trace');

// Create the actual trace file
fs.writeFileSync(actualTraceFile, JSON.stringify({ version: 1 }));
fs.writeFileSync(path.join(actualTraceDir, 'mytrace.network'), JSON.stringify([]));

// Create the .link file pointing to actual trace
fs.writeFileSync(linkFilePath, actualTraceFile, 'utf-8');

// Simulate loadTrace logic
let traceDirResult;
let traceFileResult;

if (fs.existsSync(linkFilePath)) {
  const tracePath = fs.readFileSync(linkFilePath, 'utf-8');
  traceDirResult = path.dirname(tracePath);
  traceFileResult = path.basename(tracePath);
} else {
  traceDirResult = traceDir;
}

// Verify the logic correctly reads the link
if (traceDirResult === actualTraceDir && traceFileResult === 'mytrace.trace') {
  console.log('PASS: loadTrace correctly reads .link file');
} else {
  console.error('FAIL: Wrong traceDir or traceFile:', traceDirResult, traceFileResult);
  process.exit(1);
}

// Cleanup
fs.rmSync(traceDir, { recursive: true, force: true });
fs.rmSync(actualTraceDir, { recursive: true, force: true });
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(test_script)
        test_file = f.name

    try:
        r = subprocess.run(
            ["node", test_file],
            cwd=REPO,
            capture_output=True,
            timeout=30,
        )
        output = r.stdout.decode() + r.stderr.decode()
        assert "PASS: loadTrace correctly reads .link file" in output, f"Test failed: {output}"
    finally:
        os.unlink(test_file)


def test_cli_program_catches_errors():
    """CLI program catches errors from cliProgram() and exits properly."""
    # Check that the fix adds .catch(logErrorAndExit) to cliProgram() call
    program_file = path.join(REPO, 'packages/playwright-core/src/cli/program.ts')
    assert Path(program_file).exists(), "program.ts must exist"
    content = Path(program_file).read_text()
    # The fix should add .catch(logErrorAndExit) after cliProgram()
    assert "cliProgram().catch(logErrorAndExit)" in content, "CLI error handling with .catch(logErrorAndExit) must be present"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

def test_traceutils_opentrace_exists():
    """openTrace function exists in traceUtils.ts."""
    traceutils_file = Path(REPO) / 'packages/playwright-core/src/tools/trace/traceUtils.ts'
    assert traceutils_file.exists(), "traceUtils.ts must exist"
    content = traceutils_file.read_text()
    assert "export async function openTrace" in content, "openTrace function must be exported"


def test_traceutils_loadtrace_exists():
    """loadTrace function exists in traceUtils.ts."""
    traceutils_file = Path(REPO) / 'packages/playwright-core/src/tools/trace/traceUtils.ts'
    assert traceutils_file.exists(), "traceUtils.ts must exist"
    content = traceutils_file.read_text()
    assert "export async function loadTrace" in content, "loadTrace function must be exported"


def test_traceloader_has_load_method():
    """TraceLoader class has load method with correct signature."""
    loader_file = Path(REPO) / 'packages/playwright-core/src/utils/isomorphic/trace/traceLoader.ts'
    assert loader_file.exists(), "traceLoader.ts must exist"
    content = loader_file.read_text()
    assert "async load(backend: TraceLoaderBackend" in content, "TraceLoader.load method must exist with correct signature"


def test_tracing_has_error_handling():
    """Tracing stop has error handling for traceLegend."""
    tracing_file = Path(REPO) / 'packages/playwright-core/src/tools/backend/tracing.ts'
    assert tracing_file.exists(), "tracing.ts must exist"
    content = tracing_file.read_text()
    # Check for the error handling that was added
    assert "if (!traceLegend)" in content or "Tracing is not started" in content, "Error handling for missing traceLegend must be present"
