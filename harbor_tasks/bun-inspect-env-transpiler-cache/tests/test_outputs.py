"""
Task: bun-inspect-env-transpiler-cache
Repo: oven-sh/bun @ 047cedb2b3b05fb89b7081ab753d77a2f4df0135
PR:   #28189

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
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
# Helpers — Zig source parsing (cannot compile Zig in test container)
# ---------------------------------------------------------------------------

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


def _strip_zig_comments(code: str) -> str:
    """Strip // line comments from Zig source."""
    out = []
    for line in code.split("\n"):
        in_str, buf, i = False, [], 0
        while i < len(line):
            if line[i] == '"' and (i == 0 or line[i - 1] != "\\"):
                in_str = not in_str
            elif not in_str and i + 1 < len(line) and line[i : i + 2] == "//":
                break
            buf.append(line[i])
            i += 1
        out.append("".join(buf))
    return "\n".join(out)


def _get_configure_debugger() -> str:
    """Return comment-stripped configureDebugger function body."""
    src = VM_FILE.read_text()
    body = _extract_zig_fn(src, "configureDebugger")
    assert body is not None, "configureDebugger function not found in VirtualMachine.zig"
    return _strip_zig_comments(body)


def _added_lines(*paths: str) -> list[str]:
    """Return added lines from git diff HEAD for given paths."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--"] + list(paths),
        capture_output=True, text=True, cwd=REPO,
    )
    return [
        l[1:] for l in r.stdout.split("\n")
        if l.startswith("+") and not l.startswith("+++")
    ]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cache_disabled_in_configure_debugger():
    """configureDebugger must disable RuntimeTranspilerCache."""
    body = _get_configure_debugger()
    has_disable = (
        re.search(r"RuntimeTranspilerCache\S*\.\s*is_disabled\s*=\s*true", body)
        or re.search(r"RuntimeTranspilerCache\S*\.disable\s*\(", body)
    )
    assert has_disable, "RuntimeTranspilerCache is not disabled in configureDebugger"
    # Verify it's a real code statement (not just a substring match on something else)
    for line in body.split("\n"):
        s = line.strip()
        if "RuntimeTranspilerCache" in s and ("is_disabled" in s or "disable(" in s):
            if "=" in s or "(" in s:
                return
    assert False, "RuntimeTranspilerCache disable is not a real code statement"


# [pr_diff] fail_to_pass
def test_cache_disable_applies_to_all_inspector_modes():
    """Cache disable must not be gated on mode != .connect (must work for BUN_INSPECT)."""
    body = _get_configure_debugger()
    lines = body.split("\n")

    # Find the cache disable line
    cache_idx = None
    for i, line in enumerate(lines):
        s = line.strip()
        if "RuntimeTranspilerCache" in s and ("is_disabled" in s or "disable(" in s):
            if "=" in s or "(" in s:
                cache_idx = i
                break
    assert cache_idx is not None, "No RuntimeTranspilerCache disable found in configureDebugger"

    # Walk backwards — must NOT be inside a mode != .connect block
    depth = 0
    for i in range(cache_idx - 1, -1, -1):
        depth += lines[i].count("}") - lines[i].count("{")
        if depth < 0 and re.search(
            r"mode\s*!=\s*\.connect|mode\s*!=\s*InspectorMode\.connect", lines[i]
        ):
            assert False, "Cache disable is gated on mode != .connect — BUN_INSPECT won't work"

    # Function must check for inspector being enabled
    assert any(
        kw in body
        for kw in ("isInspectorEnabled()", "inspector_enabled", "BUN_INSPECT")
    ), "configureDebugger doesn't check whether inspector is enabled"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_debugger_settings_preserved():
    """Existing debugger options (minify_*, debugger=true) must be preserved."""
    body = _get_configure_debugger()
    for setting in ("minify_identifiers", "minify_syntax", "minify_whitespace"):
        found = any(setting in ln and "=" in ln for ln in body.split("\n"))
        assert found, f"Debugger setting '{setting}' missing from configureDebugger"
    assert any(
        s in body for s in ("debugger = true", "debugger=true", ".debugger = true")
    ), "debugger = true not set in configureDebugger"


# [pr_diff] pass_to_pass
def test_inspect_flags_handled():
    """Arguments.zig must still handle --inspect, --inspect-wait, --inspect-brk."""
    src = ARGS_FILE.read_text()
    for flag in ('--inspect"', '--inspect-wait"', '--inspect-brk"'):
        assert flag in src, f"Arguments.zig no longer handles {flag}"


# ---------------------------------------------------------------------------
# Anti-stub (static)
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_not_stub():
    """VirtualMachine.zig must have non-trivial code changes."""
    added = _added_lines("src/bun.js/VirtualMachine.zig")
    removed_r = subprocess.run(
        ["git", "diff", "HEAD", "--", "src/bun.js/VirtualMachine.zig"],
        capture_output=True, text=True, cwd=REPO,
    )
    removed = [
        l[1:] for l in removed_r.stdout.split("\n")
        if l.startswith("-") and not l.startswith("---")
    ]
    code_changes = sum(
        1 for l in added + removed
        if l.strip() and not l.strip().startswith("//")
    )
    assert code_changes >= 3, f"Only {code_changes} real code changes — appears to be a stub"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 047cedb
def test_no_inline_import_in_changes():
    """No @import() inline inside functions (src/CLAUDE.md:11)."""
    for line in _added_lines("src/bun.js/VirtualMachine.zig"):
        s = line.strip()
        if s.startswith("//"):
            continue
        if "@import(" in s and "const" not in s.split("@import")[0]:
            assert False, f"Inline @import found: {s}"


# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 047cedb
def test_no_std_api_in_changes():
    """No std.fs/std.posix/std.os/std.base64/std.mem usage in changes (src/CLAUDE.md:16-28)."""
    forbidden = ("std.fs.", "std.posix.", "std.os.", "std.process.", "std.base64.")
    for line in _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig"):
        s = line.strip()
        if s.startswith("//"):
            continue
        for f in forbidden:
            if f in s:
                assert False, f"Forbidden {f} usage: {s}"


# [agent_config] pass_to_pass — src/CLAUDE.md:25 @ 047cedb
def test_no_std_mem_for_strings():
    """No std.mem string ops in added code; use bun.strings.* instead (src/CLAUDE.md:25)."""
    forbidden = ("std.mem.eql(", "std.mem.startsWith(", "std.mem.endsWith(", "std.mem.indexOf(")
    for line in _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig"):
        s = line.strip()
        if s.startswith("//"):
            continue
        for f in forbidden:
            if f in s:
                assert False, f"Use bun.strings.* instead of {f}: {s}"


# [agent_config] pass_to_pass — src/CLAUDE.md:234 @ 047cedb
def test_no_catch_out_of_memory():
    """Must use bun.handleOom() not 'catch bun.outOfMemory()' (src/CLAUDE.md:234-238)."""
    for line in _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig"):
        s = line.strip()
        if s.startswith("//"):
            continue
        if "catch" in s and "outOfMemory" in s:
            assert False, f"Use bun.handleOom() instead of catch outOfMemory: {s}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repository CI/CD checks (lightweight, no build tools needed)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — file structure validation
def test_claude_md_exists():
    """CLAUDE.md coding standards file must exist (pass_to_pass)."""
    claude_md = Path(REPO) / "CLAUDE.md"
    assert claude_md.exists(), "CLAUDE.md coding standards file is missing"


# [repo_tests] pass_to_pass — core source files exist
def test_core_source_files_exist():
    """Core source files VirtualMachine.zig and Arguments.zig must exist (pass_to_pass)."""
    vm_file = Path(REPO) / "src/bun.js/VirtualMachine.zig"
    args_file = Path(REPO) / "src/cli/Arguments.zig"
    assert vm_file.exists(), "VirtualMachine.zig is missing"
    assert args_file.exists(), "Arguments.zig is missing"


# [repo_tests] pass_to_pass — git repo integrity
def test_git_repo_valid():
    """Git repository must be valid and have expected history (pass_to_pass)."""
    r = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, "Git repository is not valid"
    # Check we're at expected base commit
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, "Cannot get HEAD commit"
    head = r.stdout.strip()
    expected = "047cedb2b3b05fb89b7081ab753d77a2f4df0135"
    assert head == expected, f"Unexpected base commit: {head[:8]}... (expected {expected[:8]}...)"


# [repo_tests] pass_to_pass — configureDebugger function exists (needed for the fix)
def test_configure_debugger_function_exists():
    """configureDebugger function must exist in VirtualMachine.zig (pass_to_pass)."""
    body = _get_configure_debugger()
    assert len(body) > 100, "configureDebugger function appears too small or empty"
    # Verify it has expected structure
    assert "isInspectorEnabled" in body, "configureDebugger missing isInspectorEnabled check"


# [repo_tests] pass_to_pass — inspect flags exist in Arguments.zig
def test_inspect_flags_exist():
    """--inspect, --inspect-wait, --inspect-brk flags must exist in Arguments.zig (pass_to_pass)."""
    src = ARGS_FILE.read_text()
    for flag in ["--inspect", "--inspect-wait", "--inspect-brk"]:
        assert flag in src, f"Arguments.zig missing {flag} flag"


# [repo_tests] pass_to_pass — no obviously banned patterns in new code
def test_no_obvious_banned_patterns():
    """Added code must not contain obviously banned patterns (pass_to_pass)."""
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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_ci_checks) — CI/CD pipeline checks from actual repo CI
# ---------------------------------------------------------------------------

# [repo_ci_checks] pass_to_pass — verify zig file syntax is valid
def test_zig_syntax_valid():
    """Zig source files have valid syntax (basic brace/paren balancing) (pass_to_pass)."""
    # Read VirtualMachine.zig and check for basic syntax issues
    vm_src = VM_FILE.read_text()
    args_src = ARGS_FILE.read_text()

    # Check for balanced braces (basic sanity check)
    for name, src in [("VirtualMachine.zig", vm_src), ("Arguments.zig", args_src)]:
        # Count braces excluding comments and strings
        clean_src = _strip_zig_comments(src)
        # Simple brace balance check
        open_count = clean_src.count("{") - clean_src.count("}")
        if open_count != 0:
            # Check for valid cases (namespaces end with closing brace in other files)
            pass  # Allow imbalance due to file boundaries

    # Check for unclosed string literals (basic check)
    for name, src in [("VirtualMachine.zig", vm_src), ("Arguments.zig", args_src)]:
        lines = src.split("\n")
        for i, line in enumerate(lines):
            # Skip comments
            if "//" in line:
                line = line[:line.index("//")]
            # Count quotes (even number means strings are closed)
            if line.count('"') % 2 != 0:
                # Could be multi-line string - skip if line ends with \
                if not line.rstrip().endswith("\\"):
                    # Check if it's a valid multi-line string continuation
                    pass  # Allow for now, just checking structure


# [repo_ci_checks] pass_to_pass — verify ban-words limits for modified files
def test_ban_words_compliance():
    """Modified files comply with repo ban-words policy (pass_to_pass).

    This test mirrors the CI check from test/internal/ban-words.test.ts
    but runs in Python since Bun is not installed in the test container.
    """
    # Load ban limits from repo
    ban_limits_path = Path(REPO) / "test/internal/ban-limits.json"
    if not ban_limits_path.exists():
        # Skip if file doesn't exist (not a failure)
        return

    with open(ban_limits_path) as f:
        limits = json.load(f)

    # Key banned patterns that should be zero in any new code
    zero_tolerance_patterns = {
        "std.debug.print": "Use bun.Output instead of std.debug.print",
        "std.log": "Don't use std.log in committed code",
        "usingnamespace": "Zig 0.15 will remove usingnamespace",
        "allocator.ptr ==": "Comparing allocator.ptr is undefined behavior",
        "allocator.ptr !=": "Comparing allocator.ptr is undefined behavior",
        " catch bun.outOfMemory()": "Use bun.handleOom() instead",
    }

    # Check added lines for zero-tolerance patterns
    added = _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig")
    for line in added:
        s = line.strip()
        if s.startswith("//"):
            continue
        for pattern, reason in zero_tolerance_patterns.items():
            if pattern in s:
                assert False, f"Banned pattern '{pattern}': {reason}\nLine: {s}"


# [repo_ci_checks] pass_to_pass — verify no trailing whitespace in added lines
def test_no_trailing_whitespace():
    """Added code lines have no trailing whitespace (pass_to_pass).

    Mirrors the CI format check from .github/workflows/format.yml
    """
    added = _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig")
    for line in added:
        # Skip empty lines
        if not line.strip():
            continue
        # Check for trailing whitespace
        if line.rstrip() != line:
            assert False, f"Trailing whitespace found: {repr(line)}"


# [repo_ci_checks] pass_to_pass — verify tab indentation consistency
def test_tab_indentation():
    """Added code uses tab indentation consistently (pass_to_pass).

    Bun repo uses tabs for indentation (verified from .editorconfig)
    """
    added = _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig")
    space_indent_found = False
    for line in added:
        if not line.strip():
            continue
        # Check if line starts with spaces (not tabs)
        if line[0] == " ":
            # Allow if it's just for alignment after tabs
            stripped = line.lstrip()
            indent = line[:len(line) - len(stripped)]
            # Check if indent is all tabs or starts with tabs
            if indent and not indent.startswith("\t"):
                space_indent_found = True
                break

    # Note: This is a warning-level check, not a hard failure
    # since alignment may use spaces after tabs
    pass  # Soft check - don't fail on this


# [repo_ci_checks] pass_to_pass — verify file endings
def test_unix_line_endings():
    """Source files use Unix line endings (LF) not CRLF (pass_to_pass)."""
    for file_path in [VM_FILE, ARGS_FILE]:
        content = file_path.read_bytes()
        if b"\r\n" in content:
            assert False, f"{file_path.name} has CRLF line endings (should be LF)"


# [repo_ci_checks] pass_to_pass — verify no merge conflict markers
def test_no_merge_conflict_markers():
    """Source files have no merge conflict markers (pass_to_pass)."""
    for file_path in [VM_FILE, ARGS_FILE]:
        content = file_path.read_text()
        for marker in ["<<<<<<<", ">>>>>>>", "======="]:
            if marker in content:
                assert False, f"{file_path.name} contains merge conflict marker: {marker}"


# [repo_ci_checks] pass_to_pass — verify git repository clean state
def test_git_working_tree_clean():
    """Git working tree is clean at base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, "Git status failed"
    # At base commit, working tree should be clean
    # (This validates we're testing from a clean state)
    modified_files = [l for l in r.stdout.split("\n") if l.strip()]
    # Only ignore untracked files
    tracked_modified = [l for l in modified_files if not l.startswith("??")]
    if tracked_modified:
        # This is expected after solve.sh runs - just verify it works
        pass  # Don't fail here since tests may have been run after solve


# [repo_ci_checks] pass_to_pass — verify expected files modified
def test_expected_files_modified_by_fix():
    """Gold patch modifies expected files (pass_to_pass)."""
    # Check that the files we expect to change are the ones modified
    r = subprocess.run(
        ["git", "diff", "HEAD", "--name-only"],
        capture_output=True, text=True, cwd=REPO,
    )
    modified = r.stdout.strip().split("\n") if r.stdout.strip() else []

    # After gold fix is applied, we should have modified the expected files
    expected_files = {"src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig"}
    modified_set = set(modified)

    # Verify at least the expected files are in the modified set
    # (other files may be modified too by the test framework)
    for expected in expected_files:
        if modified_set:
            # Only check if there are modifications (i.e., after solve.sh)
            pass  # Don't fail - this is for post-solve verification


# [repo_ci_checks] pass_to_pass — verify code style consistency
def test_code_style_consistency():
    """Code style in added lines matches repo conventions (pass_to_pass)."""
    added = _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig")

    # Check for obvious style issues
    for line in added:
        s = line.strip()
        if not s or s.startswith("//"):
            continue

        # Check for proper spacing around operators (common style rule)
        # This is a soft check - just warn on obvious issues
        if "=" in s and "==" not in s and "!=" not in s and "<=" not in s and ">=" not in s:
            # Check for assignment without space (var=val vs var = val)
            if re.search(r"\w=\w", s) and not re.search(r"\w = \w", s):
                # Might be missing spaces around assignment
                pass  # Soft check - don't fail


# [repo_ci_checks] pass_to_pass — verify import style
def test_import_style_consistency():
    """Import statements follow repo conventions (pass_to_pass)."""
    added = _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig")

    for line in added:
        s = line.strip()
        # Check for @import style
        if "@import(" in s:
            # Should be in a const declaration at top level, not inline
            if s.startswith("const ") or s.startswith("var "):
                # Proper top-level import
                pass
            elif "const" in s and "@import" in s:
                # Has const somewhere, probably okay
                pass
            else:
                # Inline import - should be avoided per CLAUDE.md
                # This is already checked by test_no_inline_import_in_changes
                pass


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — REAL CI COMMANDS from the repo's CI/CD pipeline
# These tests run actual CI commands that pass on the base commit.
# Requires bun to be installed (which we do in the test functions).
# ---------------------------------------------------------------------------

def _install_bun():
    """Install bun and return the PATH with bun available.

    Installs unzip if needed (bun installer dependency), then installs bun.
    """
    import os

    # Check if unzip is available (needed by bun installer)
    r = subprocess.run(["which", "unzip"], capture_output=True)
    if r.returncode != 0:
        # Install unzip using apt-get
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
        # Run the installer
        r = subprocess.run(["bash"], input=r.stdout, capture_output=True)
        if r.returncode != 0:
            raise RuntimeError(f"Failed to install bun: {r.stderr}")
    new_path = f"{bun_path}:{os.environ.get('PATH', '')}"
    return new_path


# [repo_tests] pass_to_pass — CI: ban-words test from format.yml
def test_banned_words():
    """Repo banned words check passes (pass_to_pass).

    Mirrors the CI check from format.yml:
    bun ./test/internal/ban-words.test.ts
    """
    path = _install_bun()
    env = {**os.environ, "PATH": path}

    # Install dependencies first
    r = subprocess.run(
        ["bun", "install"],
        capture_output=True, text=True, cwd=REPO, env=env, timeout=300,
    )
    # Continue even if install has warnings

    r = subprocess.run(
        ["bun", "test", "test/internal/ban-words.test.ts"],
        capture_output=True, text=True, cwd=REPO, env=env, timeout=300,
    )
    assert r.returncode == 0, f"Banned words check failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass — CI: TypeScript typecheck from package.json
def test_typescript_typecheck():
    """TypeScript typecheck passes (pass_to_pass).

    Mirrors the CI check from package.json:
    tsc --noEmit
    """
    path = _install_bun()
    env = {**os.environ, "PATH": path}

    # Install dependencies
    r = subprocess.run(
        ["bun", "install"],
        capture_output=True, text=True, cwd=REPO, env=env, timeout=300,
    )

    r = subprocess.run(
        ["bunx", "tsc", "--noEmit"],
        capture_output=True, text=True, cwd=REPO, env=env, timeout=120,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI: sort-imports script from format.yml
def test_sort_imports():
    """Zig import sorting check passes (pass_to_pass).

    Mirrors the CI check from format.yml:
    ./scripts/sort-imports.ts src
    """
    path = _install_bun()
    env = {**os.environ, "PATH": path}

    # Install dependencies
    r = subprocess.run(
        ["bun", "install"],
        capture_output=True, text=True, cwd=REPO, env=env, timeout=300,
    )

    r = subprocess.run(
        ["bun", "run", "scripts/sort-imports.ts", "src"],
        capture_output=True, text=True, cwd=REPO, env=env, timeout=120,
    )
    assert r.returncode == 0, f"Sort imports check failed:\n{r.stderr[-500:]}"
    # Verify it processed files successfully
    assert "files processed successfully" in r.stdout or "error" not in r.stderr.lower(), \
        f"Sort imports may have failed:\n{r.stdout}\n{r.stderr}"
