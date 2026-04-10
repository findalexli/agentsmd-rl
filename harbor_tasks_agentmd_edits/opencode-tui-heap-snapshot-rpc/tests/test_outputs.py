"""
Task: opencode-tui-heap-snapshot-rpc
Repo: anomalyco/opencode @ 1398674e531acc845e062b219f718cac1cd89a44
PR:   19028

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/opencode"


def _run_ts(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute TypeScript code via Bun in the repo directory."""
    script = Path(REPO) / "_eval_tmp.ts"
    script.write_text(code)
    try:
        return subprocess.run(
            ["bun", "run", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def _run_bun_build(target: str) -> subprocess.CompletedProcess:
    """Run bun build to verify TypeScript compiles."""
    return subprocess.run(
        ["bun", "build", "--target=bun", "--outdir", "/tmp/build", target],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files exist and have valid extensions."""
    files_to_check = [
        "packages/opencode/src/cli/cmd/tui/worker.ts",
        "packages/opencode/src/cli/cmd/tui/thread.ts",
        "packages/opencode/src/cli/cmd/tui/app.tsx",
    ]

    for file_path in files_to_check:
        full_path = Path(f"{REPO}/{file_path}")
        assert full_path.exists(), f"File {file_path} does not exist"

        # Check file has valid TypeScript/TSX extension
        assert file_path.endswith(('.ts', '.tsx')), f"File {file_path} must be TypeScript"

        # Verify the file is readable TypeScript by checking for basic syntax patterns
        content = full_path.read_text()
        # Check for balanced braces (basic sanity check)
        open_braces = content.count('{')
        close_braces = content.count('}')
        assert open_braces == close_braces, f"File {file_path} has unbalanced braces"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_worker_has_snapshot_rpc():
    """Worker RPC has snapshot method that calls writeHeapSnapshot."""
    # Test by importing and checking the rpc object structure
    r = _run_ts("""
import { writeHeapSnapshot } from "node:v8";

// Read and evaluate the worker.ts file to extract the rpc object
const workerCode = await Bun.file("packages/opencode/src/cli/cmd/tui/worker.ts").text();

// Check for required imports
if (!workerCode.includes('writeHeapSnapshot')) {
    console.error("FAIL: worker.ts does not import writeHeapSnapshot");
    process.exit(1);
}
if (!workerCode.includes('node:v8') && !workerCode.includes('"v8"')) {
    console.error("FAIL: worker.ts does not import from node:v8 or v8");
    process.exit(1);
}

// Check for snapshot method in rpc object
if (!workerCode.includes('snapshot()')) {
    console.error("FAIL: rpc object missing snapshot() method");
    process.exit(1);
}

// Check for server.heapsnapshot in the snapshot method
if (!workerCode.includes('server.heapsnapshot')) {
    console.error("FAIL: snapshot method must write to server.heapsnapshot");
    process.exit(1);
}

console.log("PASS: Worker has snapshot RPC method that calls writeHeapSnapshot");
""")
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [pr_diff] fail_to_pass
def test_thread_implements_onsnapshot():
    """Thread implements onSnapshot callback coordinating TUI and server snapshots."""
    r = _run_ts("""
const threadCode = await Bun.file("packages/opencode/src/cli/cmd/tui/thread.ts").text();

// Check for writeHeapSnapshot import
if (!threadCode.includes('writeHeapSnapshot')) {
    console.error("FAIL: thread.ts does not import writeHeapSnapshot");
    process.exit(1);
}

// Check for onSnapshot callback in tui() call
if (!threadCode.includes('onSnapshot')) {
    console.error("FAIL: thread.ts does not reference onSnapshot");
    process.exit(1);
}

// Check for async onSnapshot implementation
const hasAsyncOnSnapshot = threadCode.includes('async onSnapshot()') ||
    threadCode.includes('async onSnapshot ()') ||
    threadCode.match(/onSnapshot\\s*\\(\\s*\\)\\s*\\{/);
if (!hasAsyncOnSnapshot && !threadCode.includes('async onSnapshot')) {
    console.error("FAIL: thread.ts must implement onSnapshot as async function");
    process.exit(1);
}

// Check for tui.heapsnapshot write
if (!threadCode.includes('tui.heapsnapshot')) {
    console.error("FAIL: onSnapshot must write TUI heap snapshot to tui.heapsnapshot");
    process.exit(1);
}

// Check for RPC call to snapshot method
const hasRpcCall = threadCode.includes('client.call("snapshot"') ||
    threadCode.includes("client.call('snapshot'") ||
    threadCode.includes('client.call(`snapshot`') ||
    threadCode.match(/client\\.call\\s*\\(\\s*["'`]snapshot["'`]/);
if (!hasRpcCall) {
    console.error("FAIL: onSnapshot must call RPC snapshot method via client.call");
    process.exit(1);
}

console.log("PASS: Thread implements onSnapshot callback with TUI and server coordination");
""")
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [pr_diff] fail_to_pass
def test_app_accepts_onsnapshot_prop():
    """TUI App component accepts onSnapshot prop and passes it to heap snapshot command."""
    r = _run_ts("""
const appCode = await Bun.file("packages/opencode/src/cli/cmd/tui/app.tsx").text();

// Check for onSnapshot in tui function input type
if (!appCode.includes('onSnapshot')) {
    console.error("FAIL: app.tsx must reference onSnapshot");
    process.exit(1);
}

// Check that onSnapshot is optional prop in tui input
const hasOptionalOnSnapshot = appCode.includes('onSnapshot?:') ||
    appCode.match(/onSnapshot\\s*\\?\\:\\s*\\(\\s*\\)\\s*=>\\s*Promise/);
if (!hasOptionalOnSnapshot) {
    console.error("FAIL: onSnapshot must be optional in tui input type");
    process.exit(1);
}

// Check that onSnapshot is passed to App component
const passesOnSnapshot = appCode.includes('onSnapshot={input.onSnapshot}') ||
    appCode.match(/onSnapshot\\s*=\\s*\\{\\s*input\\.onSnapshot\\s*\\}/);
if (!passesOnSnapshot) {
    console.error("FAIL: onSnapshot must be passed from input to App component");
    process.exit(1);
}

// Check that App function accepts props with onSnapshot
const appAcceptsProps = appCode.match(/function\\s+App\\s*\\(\\s*props\\s*:\\s*\\{[^}]*onSnapshot/) ||
    appCode.match(/function\\s+App\\s*\\([^)]*props[^)]*\\)/);
if (!appAcceptsProps) {
    console.error("FAIL: App component must accept props parameter with onSnapshot");
    process.exit(1);
}

// Check that heap snapshot onSelect is async
const heapSnapshotSection = appCode.substring(
    appCode.indexOf('"Write heap snapshot"'),
    appCode.indexOf('"Write heap snapshot"') + 800
);
if (!heapSnapshotSection.includes('async')) {
    console.error("FAIL: heap snapshot onSelect must be async");
    process.exit(1);
}

// Check that onSnapshot is called in heap snapshot command
const callsOnSnapshot = appCode.includes('props.onSnapshot') ||
    appCode.includes('await input.onSnapshot') ||
    appCode.match(/await\\s+props\\.onSnapshot/);
if (!callsOnSnapshot) {
    console.error("FAIL: heap snapshot command must call onSnapshot");
    process.exit(1);
}

console.log("PASS: App component accepts onSnapshot prop and uses it in heap snapshot command");
""")
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [pr_diff] fail_to_pass
def test_changelog_command_updated():
    """.opencode/command/changelog.md has updated instructions with TUI/Desktop/Core/Misc sections."""
    r = _run_ts("""
const changelogCode = await Bun.file(".opencode/command/changelog.md").text();

// Check for new section headers
if (!changelogCode.includes('# TUI')) {
    console.error("FAIL: changelog.md must have # TUI section header");
    process.exit(1);
}
if (!changelogCode.includes('# Desktop')) {
    console.error("FAIL: changelog.md must have # Desktop section header");
    process.exit(1);
}
if (!changelogCode.includes('# Core')) {
    console.error("FAIL: changelog.md must have # Core section header");
    process.exit(1);
}
if (!changelogCode.includes('# Misc')) {
    console.error("FAIL: changelog.md must have # Misc section header");
    process.exit(1);
}

// Check that it mentions creating UPCOMING_CHANGELOG.md
if (!changelogCode.includes('UPCOMING_CHANGELOG.md')) {
    console.error("FAIL: changelog.md must mention creating UPCOMING_CHANGELOG.md");
    process.exit(1);
}

// Check that it mentions appending to appropriate sections
const mentionsSections = changelogCode.toLowerCase().includes('appropriate section') ||
    changelogCode.toLowerCase().includes('into the') ||
    changelogCode.match(/append.*section/i);
if (!mentionsSections) {
    console.error("FAIL: changelog.md must mention appending summaries to appropriate sections");
    process.exit(1);
}

// Count section headers - should have at least 4
const sectionHeaders = changelogCode.split('\\n').filter(l => l.startsWith('# '));
if (sectionHeaders.length < 4) {
    console.error("FAIL: changelog.md should have at least 4 section headers (TUI, Desktop, Core, Misc)");
    process.exit(1);
}

console.log("PASS: changelog.md has updated instructions with section structure");
""")
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "typecheck"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_tui_thread_tests():
    """TUI thread tests pass (pass_to_pass) — covers modified thread.ts."""
    r = subprocess.run(
        ["bun", "test", "test/cli/tui/thread.test.ts"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"TUI thread tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_tui_prompt_part_tests():
    """TUI prompt part tests pass (pass_to_pass) — covers TUI components."""
    r = subprocess.run(
        ["bun", "test", "test/cli/cmd/tui/prompt-part.test.ts"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"TUI prompt part tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_tui_config_tests():
    """TUI config tests pass (pass_to_pass) — covers TUI configuration."""
    r = subprocess.run(
        ["bun", "test", "test/config/tui.test.ts"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/opencode",
    )
    # This specific test is known to fail on the base commit (pre-existing issue)
    # The test "continues loading tui config when legacy source cannot be stripped" fails
    # due to a bug in the test setup, not the PR changes. Allow 1 failure.
    output = r.stdout + r.stderr

    # Parse pass/fail counts from summary lines like "19 pass" and "1 fail"
    pass_count = 0
    fail_count = 0
    for line in output.split('\n'):
        line = line.strip()
        if line.endswith(' pass') and line.split()[0].isdigit():
            pass_count = int(line.split()[0])
        if line.endswith(' fail') and line.split()[0].isdigit():
            fail_count = int(line.split()[0])

    # Should have at least 19 passes and at most 1 failure (the known pre-existing issue)
    assert pass_count >= 19, f"Expected at least 19 passing tests, got {pass_count}"
    assert fail_count <= 1, f"Expected at most 1 failing test, got {fail_count}. Output: {output[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_tui_transcript_tests():
    """TUI transcript tests pass (pass_to_pass) — covers TUI functionality."""
    r = subprocess.run(
        ["bun", "test", "test/cli/tui/transcript.test.ts"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"TUI transcript tests failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """RPC snapshot method has real implementation, not just a stub."""
    r = _run_ts("""
const workerCode = await Bun.file("packages/opencode/src/cli/cmd/tui/worker.ts").text();

// Find the snapshot method and check it has real implementation
const snapshotMatch = workerCode.match(/snapshot\\s*\\(\\s*\\)\\s*\\{([^}]*)\\}/s) ||
    workerCode.match(/snapshot\\s*\\(\\s*\\)\\s*:\\s*[^}]*\\{([^}]*)\\}/s);

if (!snapshotMatch) {
    // Try multi-line matching with proper brace counting
    const snapshotStart = workerCode.indexOf('snapshot()');
    if (snapshotStart === -1) {
        console.error("FAIL: snapshot method not found");
        process.exit(1);
    }

    // Find the method body using brace counting
    let braceCount = 0;
    let inMethod = false;
    let bodyStart = 0;
    let bodyEnd = 0;

    for (let i = snapshotStart; i < workerCode.length; i++) {
        if (workerCode[i] === '{') {
            if (!inMethod) {
                inMethod = true;
                bodyStart = i + 1;
            }
            braceCount++;
        } else if (workerCode[i] === '}') {
            braceCount--;
            if (inMethod && braceCount === 0) {
                bodyEnd = i;
                break;
            }
        }
    }

    const body = workerCode.substring(bodyStart, bodyEnd);

    // Check that body calls writeHeapSnapshot
    if (!body.includes('writeHeapSnapshot')) {
        console.error("FAIL: snapshot method body must call writeHeapSnapshot");
        process.exit(1);
    }
    if (!body.includes('server.heapsnapshot')) {
        console.error("FAIL: snapshot method must specify server.heapsnapshot filename");
        process.exit(1);
    }
} else {
    const body = snapshotMatch[1];
    if (!body.includes('writeHeapSnapshot')) {
        console.error("FAIL: snapshot method body must call writeHeapSnapshot");
        process.exit(1);
    }
    if (!body.includes('server.heapsnapshot')) {
        console.error("FAIL: snapshot method must specify server.heapsnapshot filename");
        process.exit(1);
    }
}

console.log("PASS: RPC snapshot method has real implementation");
""")
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"
