#!/usr/bin/env python3
"""
Test suite for the Move IDE activity indicator feature.

Tests verify:
1. Rust code compiles and has correct types
2. TypeScript files are syntactically valid
3. SymbolicatorMessage enum variants are correctly defined
4. ActivityMonitor state machine works correctly
"""

import subprocess
import sys
import os
from pathlib import Path

# Repository paths
REPO_ROOT = Path("/workspace/sui")
MOVE_ANALYZER_DIR = REPO_ROOT / "external-crates/move/crates/move-analyzer"
VSCODE_EXT_DIR = MOVE_ANALYZER_DIR / "editors/code"


def test_rust_code_compiles():
    """Verify the Rust code compiles successfully.

    This is a fail-to-pass test: the base commit has Result<BTreeMap> type,
    while the fix introduces SymbolicatorMessage enum.
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "move-analyzer"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Rust compilation failed:\n{result.stderr}"


def test_symbolicator_message_enum_exists():
    """Verify the SymbolicatorMessage enum is defined with all variants.

    F2P: Base commit uses Result<BTreeMap<...>>, fix uses SymbolicatorMessage.
    """
    runner_rs = MOVE_ANALYZER_DIR / "src/symbols/runner.rs"
    content = runner_rs.read_text()

    # Check enum definition exists
    assert "pub enum SymbolicatorMessage" in content, "SymbolicatorMessage enum not found"

    # Check all expected variants
    variants = [
        "Diagnostics(BTreeMap<PathBuf, Vec<Diagnostic>>)",
        "Error(anyhow::Error)",
        "FatalError(anyhow::Error)",
        "SymbolicationStart",
        "SymbolicationEnd",
    ]
    for variant in variants:
        assert variant in content, f"Variant {variant} not found in SymbolicatorMessage"


def test_symbolicator_sender_type_changed():
    """Verify the channel sender type uses SymbolicatorMessage.

    F2P: Base has Sender<Result<...>>, fix has Sender<SymbolicatorMessage>.
    """
    runner_rs = MOVE_ANALYZER_DIR / "src/symbols/runner.rs"
    content = runner_rs.read_text()

    # Should use SymbolicatorMessage, not the old Result type
    assert "Sender<SymbolicatorMessage>" in content, "Sender type should be SymbolicatorMessage"
    assert "Sender<Result<BTreeMap<PathBuf, Vec<Diagnostic>>>>" not in content, \
        "Old Result sender type should not exist"


def test_progress_token_constant_exists():
    """Verify PROGRESS_TOKEN constant is defined in both Rust and TypeScript."""
    # Rust side
    analyzer_rs = MOVE_ANALYZER_DIR / "src/analyzer.rs"
    rust_content = analyzer_rs.read_text()
    assert 'const PROGRESS_TOKEN: &str = "symbolication"' in rust_content, \
        "PROGRESS_TOKEN constant not found in analyzer.rs"

    # TypeScript side
    context_ts = VSCODE_EXT_DIR / "src/context.ts"
    ts_content = context_ts.read_text()
    assert 'const PROGRESS_TOKEN = \'symbolication\';' in ts_content or \
           'PROGRESS_TOKEN = "symbolication"' in ts_content, \
        "PROGRESS_TOKEN not found in context.ts"


def test_progress_notifications_handled():
    """Verify analyzer.rs handles SymbolicationStart and SymbolicationEnd.

    F2P: Base doesn't send progress notifications, fix does.
    """
    analyzer_rs = MOVE_ANALYZER_DIR / "src/analyzer.rs"
    content = analyzer_rs.read_text()

    # Check for progress begin notification
    assert "SymbolicatorMessage::SymbolicationStart" in content, \
        "SymbolicationStart handler not found"
    assert "SymbolicatorMessage::SymbolicationEnd" in content, \
        "SymbolicationEnd handler not found"

    # Check for WorkDoneProgress notifications
    assert "WorkDoneProgress::Begin" in content, "WorkDoneProgress::Begin not found"
    assert "WorkDoneProgress::End" in content, "WorkDoneProgress::End not found"


def test_fatal_error_handling():
    """Verify fatal errors cause server exit.

    F2P: Base treats all errors the same, fix distinguishes fatal vs non-fatal.
    """
    analyzer_rs = MOVE_ANALYZER_DIR / "src/analyzer.rs"
    content = analyzer_rs.read_text()

    # Check FatalError variant is handled
    assert "SymbolicatorMessage::FatalError(err)" in content, \
        "FatalError handler not found"

    # Check that fatal errors cause process exit
    assert "std::process::exit(1)" in content, \
        "Fatal error should call std::process::exit(1)"


def test_activity_monitor_file_exists():
    """Verify activity_monitor.ts file exists with correct structure.

    F2P: Base doesn't have this file, fix adds it.
    """
    monitor_ts = VSCODE_EXT_DIR / "src/activity_monitor.ts"
    assert monitor_ts.exists(), "activity_monitor.ts file not found"

    content = monitor_ts.read_text()

    # Check license header
    assert "Copyright (c) Mysten Labs, Inc." in content, "Missing license header"
    assert "SPDX-License-Identifier: Apache-2.0" in content, "Missing SPDX identifier"

    # Check ServerActivityMonitor class exists
    assert "export class ServerActivityMonitor" in content, \
        "ServerActivityMonitor class not found"

    # Check ServerState type
    assert "type ServerState = 'starting' | 'idle' | 'busy' | 'slow' | 'stopped'" in content, \
        "ServerState type not found"


def test_activity_monitor_state_methods():
    """Verify ServerActivityMonitor has required state transition methods."""
    monitor_ts = VSCODE_EXT_DIR / "src/activity_monitor.ts"
    content = monitor_ts.read_text()

    required_methods = [
        "onClientStateChange",
        "onCompilationStart",
        "onCompilationEnd",
        "onRequestSent",
        "onResponseReceived",
        "transitionTo",
        "dispose",
    ]

    for method in required_methods:
        assert f"{method}(" in content or f"{method}:" in content, \
            f"Method {method} not found in ServerActivityMonitor"


def test_activity_monitor_render():
    """Verify activity monitor renders correct status bar UI."""
    monitor_ts = VSCODE_EXT_DIR / "src/activity_monitor.ts"
    content = monitor_ts.read_text()

    # Check for status bar item
    assert "vscode.StatusBarAlignment.Left" in content, "Status bar alignment not found"

    # Check for rendering logic
    assert "private render():" in content, "render method not found"

    # Check for state-based styling
    assert "statusBarItem.errorBackground" in content, "Error background color not found"
    assert "statusBarItem.warningBackground" in content, "Warning background color not found"


def test_context_wires_activity_monitor():
    """Verify context.ts initializes and wires the activity monitor.

    F2P: Base doesn't have activity monitor integration.
    """
    context_ts = VSCODE_EXT_DIR / "src/context.ts"
    content = context_ts.read_text()

    # Check import
    assert "ServerActivityMonitor" in content, "ServerActivityMonitor import not found"

    # Check initActivityMonitor method exists
    assert "initActivityMonitor(" in content, "initActivityMonitor method not found"

    # Check activityMonitor field
    assert "activityMonitor: ServerActivityMonitor" in content or \
           "activityMonitor?: ServerActivityMonitor" in content, \
        "activityMonitor field not found in Context class"


def test_context_progress_notifications():
    """Verify context.ts handles $/progress notifications from server."""
    context_ts = VSCODE_EXT_DIR / "src/context.ts"
    content = context_ts.read_text()

    # Check for $/progress notification handler
    assert "client.onNotification('$/progress'" in content, \
        "$/progress notification handler not found"

    # Check for progress token matching
    assert "PROGRESS_TOKEN" in content, "PROGRESS_TOKEN usage not found"


def test_context_request_wrapping():
    """Verify context.ts wraps sendRequest to track latency."""
    context_ts = VSCODE_EXT_DIR / "src/context.ts"
    content = context_ts.read_text()

    # Check for request wrapping
    assert "client.sendRequest =" in content or "client.sendRequest = async" in content, \
        "sendRequest wrapping not found"

    # Check for tracking ID generation
    assert "trackingId" in content or "tracking_id" in content.lower(), \
        "Request tracking ID not found"


def test_context_error_handler():
    """Verify context.ts sets error handler to prevent auto-restart."""
    context_ts = VSCODE_EXT_DIR / "src/context.ts"
    content = context_ts.read_text()

    # Check for errorHandler
    assert "errorHandler:" in content, "errorHandler not found in clientOptions"

    # Check for DoNotRestart action
    assert "DoNotRestart" in content, "DoNotRestart action not found"


def test_main_initializes_monitor():
    """Verify main.ts initializes activity monitor with version info.

    F2P: Base doesn't initialize activity monitor.
    """
    main_ts = VSCODE_EXT_DIR / "src/main.ts"
    content = main_ts.read_text()

    # Check for activity monitor initialization
    assert "initActivityMonitor(" in content, "initActivityMonitor call not found in main.ts"

    # Check for version gathering
    assert "--version" in content, "Server version check not found"


def test_typescript_syntax_valid():
    """Verify TypeScript files have valid syntax.

    This checks for basic syntax errors that would prevent compilation.
    """
    src_dir = VSCODE_EXT_DIR / "src"
    ts_files = list(src_dir.glob("*.ts"))

    for ts_file in ts_files:
        content = ts_file.read_text()

        # Basic syntax checks
        open_braces = content.count("{")
        close_braces = content.count("}")
        assert open_braces == close_braces, \
            f"Mismatched braces in {ts_file.name}: {open_braces} vs {close_braces}"

        open_parens = content.count("(")
        close_parens = content.count(")")
        # Allow for some unbalanced parens in comments/strings
        assert abs(open_parens - close_parens) < 10, \
            f"Potentially mismatched parens in {ts_file.name}"


def test_runner_sends_start_message():
    """Verify runner sends SymbolicationStart at batch start."""
    runner_rs = MOVE_ANALYZER_DIR / "src/symbols/runner.rs"
    content = runner_rs.read_text()

    assert "SymbolicatorMessage::SymbolicationStart" in content, \
        "SymbolicationStart message not sent in runner"


def test_runner_sends_end_message():
    """Verify runner sends SymbolicationEnd at batch end."""
    runner_rs = MOVE_ANALYZER_DIR / "src/symbols/runner.rs"
    content = runner_rs.read_text()

    # Check for SymbolicationEnd being sent
    assert "SymbolicatorMessage::SymbolicationEnd" in content, \
        "SymbolicationEnd message not sent in runner"

    # Check that it's sent both in fatal and non-fatal paths
    fatal_count = content.count("SymbolicatorMessage::SymbolicationEnd")
    assert fatal_count >= 2, "SymbolicationEnd should be sent in both normal and error paths"


def test_runner_distinguishes_error_types():
    """Verify runner distinguishes between Error and FatalError.

    F2P: Base sends all errors the same way, fix uses different variants.
    """
    runner_rs = MOVE_ANALYZER_DIR / "src/symbols/runner.rs"
    content = runner_rs.read_text()

    # Check for non-fatal Error usage (missing manifest)
    assert "SymbolicatorMessage::Error(anyhow!" in content, \
        "Non-fatal Error usage not found"

    # Check for fatal Error usage (symbolication failure)
    assert "SymbolicatorMessage::FatalError(err)" in content or \
           "SymbolicatorMessage::FatalError" in content, \
        "FatalError usage not found"


def test_move_output_channel_persisted():
    """Verify moveOutputChannel is created and reused across restarts."""
    context_ts = VSCODE_EXT_DIR / "src/context.ts"
    content = context_ts.read_text()

    # Check for outputChannel field
    assert "moveOutputChannel: vscode.OutputChannel" in content or \
           "moveOutputChannel:" in content, \
        "moveOutputChannel field not found"

    # Check it's passed to clientOptions
    assert "outputChannel: this.moveOutputChannel" in content, \
        "moveOutputChannel not passed to clientOptions"


# =============================================================================
# Pass-to-pass tests: Repo CI/CD checks that should pass on BOTH base and fix
# =============================================================================


def test_cargo_check_move_analyzer():
    """cargo check -p move-analyzer passes (pass_to_pass).

    Verifies the Rust code for move-analyzer compiles without errors.
    """
    r = subprocess.run(
        ["cargo", "check", "-p", "move-analyzer"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-500:]}"


def test_cargo_fmt_check():
    """cargo fmt --check passes for move-analyzer (pass_to_pass).

    Verifies Rust code formatting follows the project's style conventions.
    """
    r = subprocess.run(
        ["cargo", "fmt", "--check"],
        cwd=MOVE_ANALYZER_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"cargo fmt --check failed:\n{r.stdout[-500:]}"


def test_cargo_clippy_move_analyzer():
    """cargo clippy -p move-analyzer passes (pass_to_pass).

    Verifies no clippy warnings or errors in move-analyzer.
    """
    r = subprocess.run(
        ["cargo", "clippy", "-p", "move-analyzer"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-500:]}"


def test_tsc_no_emit():
    """TypeScript compilation (tsc --noEmit) passes (pass_to_pass).

    Verifies the VSCode extension TypeScript sources compile without errors.
    """
    # First install npm dependencies
    r = subprocess.run(
        ["npm", "install"],
        cwd=VSCODE_EXT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"npm install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["./node_modules/.bin/tsc", "--noEmit"],
        cwd=VSCODE_EXT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"tsc --noEmit failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_eslint_check():
    """ESLint passes for VSCode extension (pass_to_pass).

    Verifies TypeScript files pass linting with zero warnings.
    """
    # First install npm dependencies (if not already installed)
    r = subprocess.run(
        ["npm", "install"],
        cwd=VSCODE_EXT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # npm install may fail if already installed, which is ok

    r = subprocess.run(
        ["./node_modules/.bin/eslint", ".", "--ext", "ts", "--max-warnings", "0"],
        cwd=VSCODE_EXT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"eslint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_cargo_move_clippy():
    """cargo move-clippy passes for external-crates/move (pass_to_pass).

    Verifies no clippy warnings or errors across all move crates.
    This is the specialized clippy command used in the external.yml CI workflow.
    """
    # Run from external-crates/move where the move-clippy alias is defined
    r = subprocess.run(
        ["cargo", "move-clippy"],
        cwd=REPO_ROOT / "external-crates" / "move",
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"cargo move-clippy failed:\n{r.stderr[-500:]}"


def test_move_analyzer_ide_testsuite():
    """move-analyzer IDE testsuite passes (pass_to_pass).

    Runs the full IDE testsuite for move-analyzer (33 tests covering
    completion, inlay hints, symbolication, go-to-def, etc.).
    """
    r = subprocess.run(
        ["cargo", "test", "-p", "move-analyzer", "--test", "ide_testsuite"],
        cwd=REPO_ROOT / "external-crates" / "move",
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"IDE testsuite failed:\n{r.stderr[-500:]}"
    # Verify tests actually ran and passed
    assert "test result: ok" in r.stdout, "Tests did not complete successfully"
    assert "passed" in r.stdout, "No tests passed"
