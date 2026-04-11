"""
Task: opencode-tui-heap-snapshot-rpc
Repo: anomalyco/opencode @ 1398674e531acc845e062b219f718cac1cd89a44
PR:   19028

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
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
        assert file_path.endswith((".ts", ".tsx")), f"File {file_path} must be TypeScript"
        content = full_path.read_text()
        open_braces = content.count("{")
        close_braces = content.count("}")
        assert open_braces == close_braces, f"File {file_path} has unbalanced braces"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_worker_has_snapshot_rpc():
    """Worker RPC has snapshot method that calls writeHeapSnapshot."""
    r = _run_ts("""
import { writeHeapSnapshot } from "node:v8";
const workerCode = await Bun.file("packages/opencode/src/cli/cmd/tui/worker.ts").text();
if (!workerCode.includes("writeHeapSnapshot")) {
    console.error("FAIL: worker.ts does not import writeHeapSnapshot");
    process.exit(1);
}
if (!workerCode.includes("node:v8") && !workerCode.includes('"v8"')) {
    console.error("FAIL: worker.ts does not import from node:v8 or v8");
    process.exit(1);
}
if (!workerCode.includes("snapshot()")) {
    console.error("FAIL: rpc object missing snapshot() method");
    process.exit(1);
}
if (!workerCode.includes("server.heapsnapshot")) {
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
if (!threadCode.includes("writeHeapSnapshot")) {
    console.error("FAIL: thread.ts does not import writeHeapSnapshot");
    process.exit(1);
}
if (!threadCode.includes("onSnapshot")) {
    console.error("FAIL: thread.ts does not reference onSnapshot");
    process.exit(1);
}
if (!threadCode.includes("tui.heapsnapshot")) {
    console.error("FAIL: onSnapshot must write TUI heap snapshot to tui.heapsnapshot");
    process.exit(1);
}
const hasRpcCall = threadCode.includes('client.call("snapshot"') ||
    threadCode.includes("client.call('snapshot'") ||
    /client\.call\s*\(\s*["'`]snapshot["'`]/.test(threadCode);
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
if (!appCode.includes("onSnapshot")) {
    console.error("FAIL: app.tsx must reference onSnapshot");
    process.exit(1);
}
const hasOptionalOnSnapshot = appCode.includes("onSnapshot?:") ||
    /onSnapshot\s*\?\:\s*\(\s*\)\s*=>\s*Promise/.test(appCode);
if (!hasOptionalOnSnapshot) {
    console.error("FAIL: onSnapshot must be optional in tui input type");
    process.exit(1);
}
const passesOnSnapshot = appCode.includes("onSnapshot={input.onSnapshot}") ||
    /onSnapshot\s*=\s*\{\s*input\.onSnapshot\s*\}/.test(appCode);
if (!passesOnSnapshot) {
    console.error("FAIL: onSnapshot must be passed from input to App component");
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
if (!changelogCode.includes("# TUI")) {
    console.error("FAIL: changelog.md must have # TUI section header");
    process.exit(1);
}
if (!changelogCode.includes("# Desktop")) {
    console.error("FAIL: changelog.md must have # Desktop section header");
    process.exit(1);
}
if (!changelogCode.includes("# Core")) {
    console.error("FAIL: changelog.md must have # Core section header");
    process.exit(1);
}
if (!changelogCode.includes("# Misc")) {
    console.error("FAIL: changelog.md must have # Misc section header");
    process.exit(1);
}
if (!changelogCode.includes("UPCOMING_CHANGELOG.md")) {
    console.error("FAIL: changelog.md must mention creating UPCOMING_CHANGELOG.md");
    process.exit(1);
}
const mentionsSections = changelogCode.toLowerCase().includes("appropriate section") ||
    changelogCode.toLowerCase().includes("into the") ||
    /append.*section/i.test(changelogCode);
if (!mentionsSections) {
    console.error("FAIL: changelog.md must mention appending summaries to appropriate sections");
    process.exit(1);
}
const sectionHeaders = changelogCode.split("\\n").filter(l => l.startsWith("# "));
if (sectionHeaders.length < 4) {
    console.error("FAIL: changelog.md should have at least 4 section headers");
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
    assert r.returncode == 0, f"Typecheck failed"


# [repo_tests] pass_to_pass
def test_repo_tui_thread_tests():
    """TUI thread tests pass (pass_to_pass) — covers modified thread.ts."""
    r = subprocess.run(
        ["bun", "test", "test/cli/tui/thread.test.ts"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"TUI thread tests failed"


# [repo_tests] pass_to_pass
def test_repo_tui_prompt_part_tests():
    """TUI prompt part tests pass (pass_to_pass) — covers TUI components."""
    r = subprocess.run(
        ["bun", "test", "test/cli/cmd/tui/prompt-part.test.ts"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"TUI prompt part tests failed"


# [repo_tests] pass_to_pass
def test_repo_tui_config_tests():
    """TUI config tests pass (pass_to_pass) — covers TUI configuration."""
    r = subprocess.run(
        ["bun", "test", "test/config/tui.test.ts"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/opencode",
    )
    output = r.stdout + r.stderr
    pass_count = 0
    fail_count = 0
    for line in output.split(chr(10)):
        line = line.strip()
        parts = line.split()
        if len(parts) == 2 and parts[0].isdigit():
            if parts[1] == "pass":
                pass_count = int(parts[0])
            elif parts[1] == "fail":
                fail_count = int(parts[0])
    assert pass_count >= 19, f"Expected at least 19 passing tests, got {pass_count}"
    assert fail_count <= 1, f"Expected at most 1 failing test, got {fail_count}"


# [repo_tests] pass_to_pass
def test_repo_tui_transcript_tests():
    """TUI transcript tests pass (pass_to_pass) — covers TUI functionality."""
    r = subprocess.run(
        ["bun", "test", "test/cli/tui/transcript.test.ts"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"TUI transcript tests failed"


# [repo_tests] pass_to_pass
def test_repo_snapshot_tests():
    """Snapshot tests pass (pass_to_pass) — covers file snapshot functionality."""
    r = subprocess.run(
        ["bun", "test", "test/snapshot/snapshot.test.ts"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Snapshot tests failed"


# [repo_tests] pass_to_pass
def test_repo_tool_read_tests():
    """Tool read tests pass (pass_to_pass) — covers core file reading functionality."""
    r = subprocess.run(
        ["bun", "test", "test/tool/read.test.ts"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Tool read tests failed"


# [repo_tests] pass_to_pass
def test_repo_tool_edit_tests():
    """Tool edit tests pass (pass_to_pass) — covers core file editing functionality."""
    r = subprocess.run(
        ["bun", "test", "test/tool/edit.test.ts"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Tool edit tests failed"


# [repo_tests] pass_to_pass
def test_repo_config_tests():
    """Main config tests pass (pass_to_pass) — covers configuration loading."""
    r = subprocess.run(
        ["bun", "test", "test/config/config.test.ts"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Config tests failed"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """RPC snapshot method has real implementation, not just a stub."""
    r = _run_ts("""
const workerCode = await Bun.file("packages/opencode/src/cli/cmd/tui/worker.ts").text();
const snapshotStart = workerCode.indexOf("snapshot()");
if (snapshotStart === -1) {
    console.error("FAIL: snapshot method not found");
    process.exit(1);
}
let braceCount = 0;
let inMethod = false;
let bodyStart = 0;
let bodyEnd = 0;
for (let i = snapshotStart; i < workerCode.length; i++) {
    if (workerCode[i] === "{") {
        if (!inMethod) {
            inMethod = true;
            bodyStart = i + 1;
        }
        braceCount++;
    } else if (workerCode[i] === "}") {
        braceCount--;
        if (inMethod && braceCount === 0) {
            bodyEnd = i;
            break;
        }
    }
}
const body = workerCode.substring(bodyStart, bodyEnd);
if (!body.includes("writeHeapSnapshot")) {
    console.error("FAIL: snapshot method body must call writeHeapSnapshot");
    process.exit(1);
}
if (!body.includes("server.heapsnapshot")) {
    console.error("FAIL: snapshot method must specify server.heapsnapshot filename");
    process.exit(1);
}
console.log("PASS: RPC snapshot method has real implementation");
""")
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"