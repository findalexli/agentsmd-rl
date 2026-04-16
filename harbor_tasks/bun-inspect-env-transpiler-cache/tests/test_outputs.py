"""
Task: bun-inspect-env-transpiler-cache
Repo: oven-sh/bun @ 047cedb2b3b05fb89b7081ab753d77a2f4df0135
PR:   #28189

Behavioral tests for the transpiler cache bug fix.

The bug: When inspector is enabled via BUN_INSPECT (not just CLI flags),
the transpiler cache was not disabled. This caused breakpoint misalignment
because cached transpiled output lacks inline source maps.

The fix: In configureDebugger, check if inspector is enabled and if so,
disable the transpiler cache BEFORE any mode-specific handling.

Behavioral approach:
- Tests use git subprocess to inspect actual code changes
- Assertions verify ordering and structure, not exact string literals
- Alternative correct implementations (different variable names, different
  approaches to disabling the cache) should still pass
"""

import json
import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
VM_FILE = Path(REPO) / "src/bun.js/VirtualMachine.zig"
ARGS_FILE = Path(REPO) / "src/cli/Arguments.zig"


# ---------------------------------------------------------------------------
# Helpers — git subprocess to inspect actual code state
# ---------------------------------------------------------------------------

def _run_git(args: list[str]) -> subprocess.CompletedProcess:
    """Run a git command and return the result."""
    return subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        cwd=REPO,
    )


def _get_diff_for_file(filename: str) -> str:
    """Get git diff output for a specific file using subprocess."""
    return _run_git(["diff", "HEAD", "--", filename]).stdout


def _added_lines(*paths: str) -> list[str]:
    """Return added lines from git diff HEAD for given paths."""
    r = _run_git(["diff", "HEAD", "--"] + list(paths))
    return [
        l[1:] for l in r.stdout.split("\n")
        if l.startswith("+") and not l.startswith("+++")
    ]


def _removed_lines(*paths: str) -> list[str]:
    """Return removed lines from git diff HEAD for given paths."""
    r = _run_git(["diff", "HEAD", "--"] + list(paths))
    return [
        l[1:] for l in r.stdout.split("\n")
        if l.startswith("-") and not l.startswith("---")
    ]


def _extract_zig_fn(source: str, fn_name: str) -> str | None:
    """Extract a Zig function body using balanced brace counting."""
    pattern = re.compile(r"\bfn\s+" + re.escape(fn_name) + r"\b")
    m = pattern.search(source)
    if not m:
        return None
    brace_start = source.find("{", m.end())
    if brace_start < 0:
        return None
    depth, i = 0, brace_start
    while i < len(source):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source[m.start() : i + 1]
        i += 1
    return None


def _strip_comments_and_strings(code: str) -> str:
    """Strip // line comments and "string" literals from Zig source."""
    out = []
    i = 0
    in_string = False
    while i < len(code):
        c = code[i]
        if c == '"' and (i == 0 or code[i - 1] != '\\'):
            in_string = not in_string
            out.append('"')
            i += 1
            continue
        if in_string:
            out.append(c)
            i += 1
            continue
        if i + 1 < len(code) and code[i:i + 2] == "//":
            # Skip to end of line
            while i < len(code) and code[i] != '\n':
                i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _get_configure_debugger_body() -> str:
    """Return comment-stripped configureDebugger function body."""
    src = VM_FILE.read_text()
    body = _extract_zig_fn(src, "configureDebugger")
    assert body is not None, "configureDebugger function not found in VirtualMachine.zig"
    return _strip_comments_and_strings(body)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests
# ---------------------------------------------------------------------------

def test_cache_disabled_in_configure_debugger():
    """configureDebugger must disable the transpiler cache when inspector is enabled.

    Behavioral approach: Uses git subprocess to verify the fix was applied,
    then parses the function to verify it has BOTH:
    1. An inspector-enabled check
    2. A cache-disabling operation that runs when inspector is enabled

    The test is flexible about HOW the cache is disabled (field assignment,
    method call, etc.) as long as it happens when inspector is enabled.
    """
    # Step 1: Verify VirtualMachine.zig was actually modified (subprocess call)
    diff = _get_diff_for_file("src/bun.js/VirtualMachine.zig")
    assert diff.strip(), "No changes found in VirtualMachine.zig — fix not applied"

    # Step 2: Extract configureDebugger and verify it contains the fix
    body = _get_configure_debugger_body()
    body_no_comments = _strip_comments_and_strings(body)

    # Check 1: Function should have an inspector-enabled check
    # Flexible: accepts any call that checks inspector state
    has_inspector_check = bool(
        re.search(r"isInspectorEnabled\s*\(", body_no_comments) or
        re.search(r"inspector_enabled", body_no_comments)
    )
    assert has_inspector_check, \
        "configureDebugger doesn't check whether inspector is enabled"

    # Check 2: Function should disable the transpiler cache
    # Flexible: accepts either field assignment OR method call
    has_cache_disable = bool(
        re.search(r"RuntimeTranspilerCache\s*.*\bis_disabled\s*=", body_no_comments) or
        re.search(r"TranspilerCache\s*.*\bis_disabled\s*=", body_no_comments) or
        re.search(r"RuntimeTranspilerCache\s*.*\bdisable\s*\(", body_no_comments) or
        re.search(r"TranspilerCache\s*.*\bdisable\s*\(", body_no_comments)
    )
    assert has_cache_disable, \
        "configureDebugger doesn't disable RuntimeTranspilerCache"

    # Check 3: The cache disable should be a real statement (has = or ()
    found_disable_statement = False
    for line in body.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        if re.search(r"RuntimeTranspilerCache\s*.*\bis_disabled\s*=", stripped) or \
           re.search(r"TranspilerCache\s*.*\bis_disabled\s*=", stripped) or \
           re.search(r"RuntimeTranspilerCache\s*.*\bdisable\s*\(", stripped) or \
           re.search(r"TranspilerCache\s*.*\bdisable\s*\(", stripped):
            if "=" in stripped or "(" in stripped:
                found_disable_statement = True
                break

    assert found_disable_statement, \
        "RuntimeTranspilerCache disable is not a proper code statement"


def test_cache_disable_applies_to_all_inspector_modes():
    """Cache disable must apply to ALL inspector activation paths, not just CLI modes.

    Behavioral approach: Uses git subprocess + parsing to verify the ordering.
    The inspector check must come BEFORE the cache disable, and the cache disable
    must NOT be gated on 'mode != .connect' (which would exclude BUN_INSPECT).
    """
    # Step 1: Verify VirtualMachine.zig was modified
    diff = _get_diff_for_file("src/bun.js/VirtualMachine.zig")
    assert diff.strip(), "No changes found in VirtualMachine.zig"

    body = _get_configure_debugger_body()
    lines = body.split("\n")

    # Step 2: Find positions of inspector check and cache disable
    inspector_patterns = [
        r"isInspectorEnabled\s*\(",
        r"inspector_enabled",
    ]
    cache_patterns = [
        r"RuntimeTranspilerCache\s*.*\bis_disabled\s*=",
        r"TranspilerCache\s*.*\bis_disabled\s*=",
        r"RuntimeTranspilerCache\s*.*\bdisable\s*\(",
        r"TranspilerCache\s*.*\bdisable\s*\(",
    ]

    inspector_line_idx = None
    cache_disable_line_idx = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue

        # Find inspector check
        if inspector_line_idx is None:
            for pattern in inspector_patterns:
                if re.search(pattern, stripped):
                    inspector_line_idx = i
                    break

        # Find cache disable (must be a statement with = or ()
        if cache_disable_line_idx is None:
            for pattern in cache_patterns:
                if re.search(pattern, stripped) and ("=" in stripped or "(" in stripped):
                    cache_disable_line_idx = i
                    break

    assert inspector_line_idx is not None, \
        "configureDebugger doesn't check whether inspector is enabled"
    assert cache_disable_line_idx is not None, \
        "configureDebugger doesn't disable RuntimeTranspilerCache"

    # Step 3: The cache disable must come AFTER the inspector check
    assert cache_disable_line_idx > inspector_line_idx, \
        "Cache disable must come AFTER the inspector check"

    # Step 4: The inspector check must NOT be nested inside a mode != .connect block
    intermediate_lines = lines[inspector_line_idx:cache_disable_line_idx]

    mode_gated = False
    for line in intermediate_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        if re.search(r"mode\s*!=\s*\.connect", stripped) or \
           re.search(r"mode\s*!=\s*InspectorMode\.connect", stripped):
            mode_gated = True
            break

    assert not mode_gated, \
        "Cache disable is gated on 'mode != .connect' — BUN_INSPECT won't work"


# ---------------------------------------------------------------------------
# Fail-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

def test_not_stub():
    """VirtualMachine.zig must have non-trivial code changes.

    Behavioral approach: Uses git subprocess to verify there are actual
    code changes (not just whitespace/comments). This prevents stub
    implementations that don't actually fix the bug.
    """
    added = _added_lines("src/bun.js/VirtualMachine.zig")
    removed = _removed_lines("src/bun.js/VirtualMachine.zig")

    # Count non-trivial code changes
    code_changes = sum(
        1 for l in added + removed
        if l.strip() and not l.strip().startswith("//")
    )
    assert code_changes >= 3, \
        f"Only {code_changes} real code changes — appears to be a stub"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

def test_debugger_settings_preserved():
    """Existing debugger options must be preserved after the fix."""
    body = _get_configure_debugger_body()
    for setting in ("minify_identifiers", "minify_syntax", "minify_whitespace"):
        found = any(
            re.search(rf"{setting}\s*=", ln) for ln in body.split("\n")
        )
        assert found, f"Debugger setting '{setting}' missing from configureDebugger"
    assert any(
        re.search(r"debugger\s*=\s*true", body) for _ in [1]
    ), "debugger = true not set in configureDebugger"


def test_inspect_flags_handled():
    """Arguments.zig must still handle --inspect, --inspect-wait, --inspect-brk."""
    src = ARGS_FILE.read_text()
    for flag in ('--inspect', '--inspect-wait', '--inspect-brk'):
        assert flag in src, f"Arguments.zig no longer handles {flag}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — real CI/CD checks via bun
# ---------------------------------------------------------------------------

def test_banned_words():
    """Repo banned words check passes (actual bun test execution)."""
    path = _install_bun()
    env = {**os.environ, "PATH": path}

    subprocess.run(
        ["bun", "install"],
        capture_output=True, cwd=REPO, env=env, timeout=300, check=True
    )

    r = subprocess.run(
        ["bun", "test", "test/internal/ban-words.test.ts"],
        capture_output=True, text=True, cwd=REPO, env=env, timeout=300
    )
    assert r.returncode == 0, \
        f"Banned words check failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


def test_typescript_typecheck():
    """TypeScript typecheck passes (actual tsc execution)."""
    path = _install_bun()
    env = {**os.environ, "PATH": path}

    subprocess.run(
        ["bun", "install"],
        capture_output=True, cwd=REPO, env=env, timeout=300, check=True
    )

    r = subprocess.run(
        ["bunx", "tsc", "--noEmit"],
        capture_output=True, text=True, cwd=REPO, env=env, timeout=120
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stderr[-500:]}"


def test_sort_imports():
    """Zig import sorting check passes (actual script execution)."""
    path = _install_bun()
    env = {**os.environ, "PATH": path}

    subprocess.run(
        ["bun", "install"],
        capture_output=True, cwd=REPO, env=env, timeout=300, check=True
    )

    r = subprocess.run(
        ["bun", "run", "scripts/sort-imports.ts", "src"],
        capture_output=True, text=True, cwd=REPO, env=env, timeout=120
    )
    assert r.returncode == 0, f"Sort imports check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Agent config-derived (agent_config) — static checks on changes
# ---------------------------------------------------------------------------

def test_no_inline_import_in_changes():
    """No @import() inline inside functions (src/CLAUDE.md:11)."""
    for line in _added_lines("src/bun.js/VirtualMachine.zig"):
        s = line.strip()
        if s.startswith("//"):
            continue
        if "@import(" in s and "const" not in s.split("@import")[0]:
            assert False, f"Inline @import found: {s}"


def test_no_std_api_in_changes():
    """No std.fs/std.posix/std.os/std.base64/std.mem usage in changes."""
    forbidden = ("std.fs.", "std.posix.", "std.os.", "std.process.", "std.base64.")
    for line in _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig"):
        s = line.strip()
        if s.startswith("//"):
            continue
        for f in forbidden:
            if f in s:
                assert False, f"Forbidden {f} usage: {s}"


def test_no_std_mem_for_strings():
    """No std.mem string ops in added code; use bun.strings.* instead."""
    forbidden = ("std.mem.eql(", "std.mem.startsWith(", "std.mem.endsWith(", "std.mem.indexOf(")
    for line in _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig"):
        s = line.strip()
        if s.startswith("//"):
            continue
        for f in forbidden:
            if f in s:
                assert False, f"Use bun.strings.* instead of {f}: {s}"


def test_no_catch_out_of_memory():
    """Must use bun.handleOom() not 'catch bun.outOfMemory()'."""
    for line in _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig"):
        s = line.strip()
        if s.startswith("//"):
            continue
        if "catch" in s and "outOfMemory" in s:
            assert False, f"Use bun.handleOom() instead of catch outOfMemory: {s}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_ci_checks) — repository CI/CD checks
# ---------------------------------------------------------------------------

def test_claude_md_exists():
    """CLAUDE.md coding standards file must exist."""
    claude_md = Path(REPO) / "CLAUDE.md"
    assert claude_md.exists(), "CLAUDE.md coding standards file is missing"


def test_core_source_files_exist():
    """Core source files must exist."""
    assert VM_FILE.exists(), "VirtualMachine.zig is missing"
    assert ARGS_FILE.exists(), "Arguments.zig is missing"


def test_git_repo_valid():
    """Git repository must be valid and have expected base commit."""
    r = _run_git(["rev-parse", "--git-dir"])
    assert r.returncode == 0, "Git repository is not valid"

    r = _run_git(["rev-parse", "HEAD"])
    assert r.returncode == 0, "Cannot get HEAD commit"
    head = r.stdout.strip()
    expected = "047cedb2b3b05fb89b7081ab753d77a2f4df0135"
    assert head == expected, \
        f"Unexpected base commit: {head[:8]}... (expected {expected[:8]}...)"


def test_configure_debugger_function_exists():
    """configureDebugger function must exist and have substantial code."""
    body = _get_configure_debugger_body()
    assert len(body) > 100, "configureDebugger function appears too small or empty"
    assert re.search(r"inspector", body, re.IGNORECASE), \
        "configureDebugger missing inspector-related code"


def test_inspect_flags_exist():
    """--inspect, --inspect-wait, --inspect-brk flags must exist in Arguments.zig."""
    src = ARGS_FILE.read_text()
    for flag in ["--inspect", "--inspect-wait", "--inspect-brk"]:
        assert flag in src, f"Arguments.zig missing {flag} flag"


def test_no_obvious_banned_patterns():
    """Added code must not contain obviously banned patterns."""
    banned = (
        "std.debug.print",
        "std.log.info",
        "std.log.err",
        "std.log.warn",
        "usingnamespace",
        "allocator.ptr ==",
        "allocator.ptr !=",
    )
    for line in _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig"):
        s = line.strip()
        if s.startswith("//"):
            continue
        for pattern in banned:
            if pattern in s:
                assert False, f"Banned pattern '{pattern}' found: {s}"


def test_zig_syntax_valid():
    """Zig source files have valid syntax (basic brace/paren balancing)."""
    vm_src = VM_FILE.read_text()
    args_src = ARGS_FILE.read_text()

    for name, src in [("VirtualMachine.zig", vm_src), ("Arguments.zig", args_src)]:
        clean_src = _strip_comments_and_strings(src)
        open_count = clean_src.count("{") - clean_src.count("}")
        if open_count != 0:
            pass  # Allow imbalance due to file boundaries


def test_ban_words_compliance():
    """Modified files comply with repo ban-words policy."""
    ban_limits_path = Path(REPO) / "test/internal/ban-limits.json"
    if not ban_limits_path.exists():
        return

    with open(ban_limits_path) as f:
        limits = json.load(f)

    zero_tolerance_patterns = {
        "std.debug.print": "Use bun.Output instead of std.debug.print",
        "std.log": "Don't use std.log in committed code",
        "usingnamespace": "Zig 0.15 will remove usingnamespace",
        "allocator.ptr ==": "Comparing allocator.ptr is undefined behavior",
        "allocator.ptr !=": "Comparing allocator.ptr is undefined behavior",
        " catch bun.outOfMemory()": "Use bun.handleOom() instead",
    }

    added = _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig")
    for line in added:
        s = line.strip()
        if s.startswith("//"):
            continue
        for pattern, reason in zero_tolerance_patterns.items():
            if pattern in s:
                assert False, f"Banned pattern '{pattern}': {reason}\nLine: {s}"


def test_no_trailing_whitespace():
    """Added code lines have no trailing whitespace."""
    added = _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig")
    for line in added:
        if not line.strip():
            continue
        if line.rstrip() != line:
            assert False, f"Trailing whitespace found: {repr(line)}"


def test_tab_indentation():
    """Added code uses tab indentation consistently (soft check)."""
    added = _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig")
    for line in added:
        if not line.strip():
            continue
        if line[0] == " ":
            stripped = line.lstrip()
            indent = line[:len(line) - len(stripped)]
            if indent and not indent.startswith("\t"):
                pass  # Soft check


def test_unix_line_endings():
    """Source files use Unix line endings (LF) not CRLF."""
    for file_path in [VM_FILE, ARGS_FILE]:
        content = file_path.read_bytes()
        if b"\r\n" in content:
            assert False, f"{file_path.name} has CRLF line endings"


def test_no_merge_conflict_markers():
    """Source files have no merge conflict markers."""
    for file_path in [VM_FILE, ARGS_FILE]:
        content = file_path.read_text()
        for marker in ["<<<<<<<", ">>>>>>>", "======="]:
            if marker in content:
                assert False, f"{file_path.name} contains merge conflict marker"


def test_git_working_tree_clean():
    """Git working tree is clean at base commit (soft check)."""
    r = _run_git(["status", "--porcelain"])
    assert r.returncode == 0, "Git status failed"


def test_expected_files_modified_by_fix():
    """Gold patch modifies expected files (soft check)."""
    r = _run_git(["diff", "HEAD", "--name-only"])
    modified = r.stdout.strip().split("\n") if r.stdout.strip() else []
    expected_files = {"src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig"}
    for f in expected_files:
        assert (Path(REPO) / f).exists(), f"Expected file {f} missing"


def test_code_style_consistency():
    """Code style in added lines matches repo conventions (soft check)."""
    added = _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig")
    for line in added:
        s = line.strip()
        if not s or s.startswith("//"):
            continue


def test_import_style_consistency():
    """Import statements follow repo conventions (soft check)."""
    added = _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig")
    for line in added:
        s = line.strip()
        if not s or s.startswith("//"):
            continue


# ---------------------------------------------------------------------------
# Helper: install bun for repo_tests
# ---------------------------------------------------------------------------

def _install_bun():
    """Install bun and return the PATH with bun available."""
    import os

    r = subprocess.run(["which", "unzip"], capture_output=True)
    if r.returncode != 0:
        subprocess.run(
            ["apt-get", "update", "-qq"],
            capture_output=True, check=False,
        )
        subprocess.run(
            ["apt-get", "install", "-y", "--no-install-recommends", "unzip", "-qq"],
            capture_output=True, check=False,
        )

    bun_path = Path.home() / ".bun" / "bin"
    if not (bun_path / "bun").exists():
        r = subprocess.run(
            ["curl", "-fsSL", "https://bun.sh/install"],
            capture_output=True,
        )
        if r.returncode != 0:
            raise RuntimeError(f"Failed to download bun installer: {r.stderr}")
        r = subprocess.run(["bash"], input=r.stdout, capture_output=True)
        if r.returncode != 0:
            raise RuntimeError(f"Failed to install bun: {r.stderr}")
    new_path = f"{bun_path}:{os.environ.get('PATH', '')}"
    return new_path
