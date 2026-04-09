"""
Task: bun-fixwatcher-handle-vim-atomic-save
Repo: oven-sh/bun @ dc36d5601c2c3e7aa191baed6db231d6a7ca5e04
PR:   23566

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/bun"

WATCHER_ZIG = Path(REPO) / "src" / "Watcher.zig"
HOT_RELOADER_ZIG = Path(REPO) / "src" / "bun.js" / "hot_reloader.zig"
VM_ZIG = Path(REPO) / "src" / "bun.js" / "VirtualMachine.zig"
FS_ZIG = Path(REPO) / "src" / "fs.zig"
SRC_CLAUDE_MD = Path(REPO) / "src" / "CLAUDE.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_zig_syntax_balanced():
    """Modified Zig files must have balanced braces and parentheses."""
    for filepath in [WATCHER_ZIG, HOT_RELOADER_ZIG, VM_ZIG, FS_ZIG]:
        text = filepath.read_text()
        assert text.count("{") > 0, f"{filepath.name} appears empty"
        brace_depth = 0
        paren_depth = 0
        for ch in text:
            if ch == "{":
                brace_depth += 1
            elif ch == "}":
                brace_depth -= 1
            elif ch == "(":
                paren_depth += 1
            elif ch == ")":
                paren_depth -= 1
        assert brace_depth == 0, (
            f"{filepath.name} has unbalanced braces (depth={brace_depth})"
        )
        assert paren_depth == 0, (
            f"{filepath.name} has unbalanced parens (depth={paren_depth})"
        )


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ dc36d560
def test_import_bun_not_root_bun():
    """Modified Zig files must use @import("bun"), not @import("root").bun."""
    for filepath in [WATCHER_ZIG, HOT_RELOADER_ZIG, VM_ZIG, FS_ZIG]:
        text = filepath.read_text()
        assert '@import("root").bun' not in text, (
            f'{filepath.name} uses @import("root").bun — '
            f'convention requires @import("bun") (src/CLAUDE.md)'
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_watcher_add_file_by_path_slow():
    """Watcher.zig must have addFileByPathSlow that opens with O_EVTONLY and calls addFile."""
    text = WATCHER_ZIG.read_text()

    # Function must exist
    assert "addFileByPathSlow" in text, (
        "Watcher.zig missing addFileByPathSlow function"
    )

    # Find the function body
    start = text.find("pub fn addFileByPathSlow")
    assert start != -1, "addFileByPathSlow not a pub fn"
    func_region = text[start:start + 2000]

    # Must open file with O_EVTONLY for kqueue watching on macOS
    assert "O_EVTONLY" in func_region, (
        "addFileByPathSlow must open files with O_EVTONLY for macOS kqueue"
    )

    # Must call addFile to register the watched file
    assert "this.addFile(" in func_region or "self.addFile(" in func_region, (
        "addFileByPathSlow must call addFile to register the file"
    )

    # Must handle already-watched case (indexOf check)
    assert "indexOf" in func_region, (
        "addFileByPathSlow must check if file is already watched"
    )


# [pr_diff] fail_to_pass
def test_hot_reloader_entrypoint_rename_defer():
    """hot_reloader.zig must track entrypoint with MainFile and defer reload on rename."""
    text = HOT_RELOADER_ZIG.read_text()

    # MainFile struct must exist
    assert "const MainFile = struct" in text or "MainFile = struct" in text, (
        "hot_reloader.zig missing MainFile struct definition"
    )

    # Must have is_waiting_for_dir_change flag
    assert "is_waiting_for_dir_change" in text, (
        "MainFile must have is_waiting_for_dir_change flag for vim atomic save"
    )

    # Find the MainFile struct and verify it has dir tracking
    mf_start = text.find("MainFile")
    assert mf_start != -1
    mf_region = text[mf_start:mf_start + 1500]
    assert "dir_hash" in mf_region, (
        "MainFile must track parent directory hash for detecting dir write events"
    )

    # The event handling must check for rename and set the flag
    assert "event.op.rename" in text, (
        "hot_reloader must check for rename events"
    )

    # Must use faccessat to verify file exists after directory write
    assert "faccessat" in text, (
        "hot_reloader must use faccessat to verify file exists after atomic save"
    )


# [pr_diff] fail_to_pass
def test_vm_report_exception_and_watcher():
    """VirtualMachine.zig must have renamed fn and addMainToWatcherIfNeeded."""
    text = VM_ZIG.read_text()

    # Renamed function must exist
    assert "reportExceptionInHotReloadedModuleIfNeeded" in text, (
        "VirtualMachine.zig missing reportExceptionInHotReloadedModuleIfNeeded "
        "(renamed from handlePendingInternalPromiseRejection)"
    )

    # New helper function must exist
    assert "addMainToWatcherIfNeeded" in text, (
        "VirtualMachine.zig missing addMainToWatcherIfNeeded function"
    )

    # addMainToWatcherIfNeeded must call addFileByPathSlow
    fn_start = text.find("pub fn addMainToWatcherIfNeeded")
    assert fn_start != -1, "addMainToWatcherIfNeeded must be a pub fn"
    fn_region = text[fn_start:fn_start + 500]
    assert "addFileByPathSlow" in fn_region, (
        "addMainToWatcherIfNeeded must call addFileByPathSlow on the watcher"
    )


# [pr_diff] fail_to_pass
def test_find_extname_implementation():
    """fs.zig must have findExtname that finds extension after last path separator."""
    # Use subprocess to run a Python script that parses and validates the Zig function
    script = textwrap.dedent(f"""\
        import sys

        text = open("{FS_ZIG}").read()

        # Function must exist as a pub fn
        marker = "pub fn findExtname"
        idx = text.find(marker)
        if idx == -1:
            print("FAIL: findExtname not found as pub fn in fs.zig")
            sys.exit(1)

        # Extract ~300 chars of function body
        body = text[idx:idx + 400]

        # Must handle path separator to find basename
        if "lastIndexOfSep" not in body and "separator" not in body.lower():
            print("FAIL: findExtname must find last path separator")
            sys.exit(1)

        # Must search for dot character in the basename
        if "'.' " not in body and "'.'" not in body and "dot" not in body.lower():
            print("FAIL: findExtname must search for dot in basename")
            sys.exit(1)

        # Must return the extension slice (base[dot..])
        if "return" not in body:
            print("FAIL: findExtname must return a value")
            sys.exit(1)

        # Must handle no-extension case (return empty string)
        if '""' not in body:
            print("FAIL: findExtname must return empty string when no extension")
            sys.exit(1)

        print("PASS: findExtname has correct algorithm structure")
    """)

    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"findExtname validation failed:\n{result.stdout}\n{result.stderr}"
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config update tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_src_claude_md_import_conventions():
    """src/CLAUDE.md must be updated with expanded @import conventions."""
    text = SRC_CLAUDE_MD.read_text()

    # Must mention auto formatter handling import placement
    assert "auto formatter" in text.lower() or "autoformatter" in text.lower(), (
        "src/CLAUDE.md should note that the auto formatter handles @import placement"
    )

    # Must exclude @import("../bun.zig") as an anti-pattern
    assert '@import("../bun.zig")' in text, (
        'src/CLAUDE.md should list @import("../bun.zig") as an import anti-pattern'
    )

    # Must still reference @import("bun") as the preferred form
    assert '@import("bun")' in text, (
        'src/CLAUDE.md should still reference @import("bun") as preferred'
    )

    # Must still exclude @import("root").bun
    assert '@import("root").bun' in text, (
        'src/CLAUDE.md should still list @import("root").bun as anti-pattern'
    )
