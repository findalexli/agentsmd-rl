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
    """Worker RPC exposes a callable snapshot method that writes server.heapsnapshot."""
    r = _run_ts("""
const mod = await import("./packages/opencode/src/cli/cmd/tui/worker.ts");
const { rpc } = mod;

// rpc must export a snapshot function
if (typeof rpc.snapshot !== "function") {
    console.error("FAIL: rpc.snapshot is not a function, got " + typeof rpc.snapshot);
    process.exit(1);
}

// Call snapshot and verify it returns a path to server.heapsnapshot
const result = await Promise.resolve(rpc.snapshot());
if (typeof result !== "string") {
    console.error("FAIL: snapshot() must return a string path, got " + typeof result);
    process.exit(1);
}
if (!result.includes("server.heapsnapshot")) {
    console.error("FAIL: snapshot() must return path containing server.heapsnapshot, got: " + result);
    process.exit(1);
}

// Verify the snapshot file was actually written to disk
const fs = await import("node:fs");
if (!fs.existsSync(result)) {
    console.error("FAIL: Heap snapshot file not created at: " + result);
    process.exit(1);
}
fs.unlinkSync(result);

console.log("PASS: Worker rpc.snapshot method works correctly");
process.exit(0);
""")
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [pr_diff] fail_to_pass
def test_thread_implements_onsnapshot():
    """Thread implements onSnapshot callback that coordinates TUI and server heap snapshots."""
    thread_path = Path(REPO) / "packages/opencode/src/cli/cmd/tui/thread.ts"
    content = thread_path.read_text()

    # onSnapshot callback must exist
    assert "onSnapshot" in content, "thread.ts must define an onSnapshot callback"

    # Must import writeHeapSnapshot for TUI-side snapshot
    assert "writeHeapSnapshot" in content, "thread.ts must import writeHeapSnapshot"

    # Must write TUI heap to tui.heapsnapshot
    assert "tui.heapsnapshot" in content, "onSnapshot must write TUI heap to tui.heapsnapshot"

    # onSnapshot must be wired into the tui() call
    tui_call_idx = content.find("await tui(")
    assert tui_call_idx != -1, "thread.ts must call tui()"
    tui_call_block = content[tui_call_idx:tui_call_idx + 800]
    assert "onSnapshot" in tui_call_block, "onSnapshot must be passed in the tui() call arguments"


# [pr_diff] fail_to_pass
def test_app_accepts_onsnapshot_prop():
    """TUI App component accepts onSnapshot prop and uses it in the heap snapshot command."""
    app_path = Path(REPO) / "packages/opencode/src/cli/cmd/tui/app.tsx"
    content = app_path.read_text()

    # tui input type must include optional onSnapshot
    assert "onSnapshot?" in content, "onSnapshot must be an optional property in tui input type"

    # App function must accept onSnapshot in its parameters
    # (via props object with inline type, separate interface, or destructuring)
    app_start = content.find("function App(")
    assert app_start != -1, "App function must exist"
    # Check a window around the function declaration for onSnapshot in the signature/type
    app_decl_region = content[app_start:app_start + 300]
    assert "onSnapshot" in app_decl_region, \
        "App function declaration must include onSnapshot in its parameter type"

    # The heap snapshot command handler must reference onSnapshot
    heap_cmd_idx = content.find("app.heap_snapshot")
    assert heap_cmd_idx != -1, "Heap snapshot command must exist"
    heap_cmd_block = content[heap_cmd_idx:heap_cmd_idx + 500]
    assert "onSnapshot" in heap_cmd_block, "Heap snapshot command handler must use onSnapshot"


# [pr_diff] fail_to_pass
def test_changelog_command_updated():
    """.opencode/command/changelog.md has updated instructions with TUI/Desktop/Core/Misc sections."""
    r = _run_ts("""
const content = await Bun.file(".opencode/command/changelog.md").text();
const required = ["# TUI", "# Desktop", "# Core", "# Misc", "UPCOMING_CHANGELOG.md"];
for (const term of required) {
    if (!content.includes(term)) {
        console.error("FAIL: changelog.md missing: " + term);
        process.exit(1);
    }
}
const sectionCount = content.split("\\n").filter(l => l.startsWith("# ")).length;
if (sectionCount < 4) {
    console.error("FAIL: Expected at least 4 section headers, found " + sectionCount);
    process.exit(1);
}
console.log("PASS: changelog.md has section structure");
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
def test_repo_tui_tests():
    """TUI CLI tests pass (pass_to_pass) — covers modified thread.ts and related TUI functionality."""
    r = subprocess.run(
        ["bun", "test", "test/cli/tui/"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"TUI CLI tests failed"


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
# Fail-to-pass (pr_diff) — anti-stub check
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_not_stub():
    """RPC snapshot method has real writeHeapSnapshot implementation, not just a stub."""
    worker_path = Path(REPO) / "packages/opencode/src/cli/cmd/tui/worker.ts"
    content = worker_path.read_text()
    # Must import writeHeapSnapshot from v8/node:v8
    has_v8_import = "node:v8" in content or '"v8"' in content
    assert has_v8_import, "worker.ts must import from node:v8 or v8"
    assert "writeHeapSnapshot" in content, "worker.ts must use writeHeapSnapshot"
    assert "server.heapsnapshot" in content, "snapshot method must write to server.heapsnapshot"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_run_app_e2e_tests():
    """pass_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")