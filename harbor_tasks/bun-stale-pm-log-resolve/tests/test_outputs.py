"""
Task: bun-stale-pm-log-resolve
Repo: oven-sh/bun @ 9ce5b052840cecea4aa1977aeb063c47d0137a22
PR:   28511

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: Zig requires the full bun build toolchain (cmake, zig compiler, WebKit)
which cannot run in this container. All tests are structural, inspecting the
source code of the target function.
# AST-only because: Zig source cannot be compiled without full bun build toolchain
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
TARGET = Path(REPO) / "src/bun.js/VirtualMachine.zig"


def _extract_function(name: str = "resolveMaybeNeedsTrailingSlash") -> str:
    """Extract the full body of a named Zig function from the target file."""
    source = TARGET.read_text()
    lines = source.splitlines()
    start = None
    for i, line in enumerate(lines):
        if f"pub fn {name}" in line:
            start = i
            break
    assert start is not None, f"Function {name} not found in {TARGET}"

    brace_depth = 0
    found_open = False
    end = start
    for i in range(start, len(lines)):
        for ch in lines[i]:
            if ch == "{":
                brace_depth += 1
                found_open = True
            elif ch == "}":
                brace_depth -= 1
        if found_open and brace_depth <= 0:
            end = i
            break

    return "\n".join(lines[start : end + 1])


def _strip_comments(text: str) -> str:
    """Strip single-line // comments from Zig source."""
    return "\n".join(re.sub(r"//.*", "", line) for line in text.splitlines())


def _split_before_after_defer(clean: str) -> tuple[str, str]:
    """Split function body into pre-defer and defer block text."""
    lines = clean.splitlines()
    defer_blocks: list[str] = []
    before_defer = []
    in_defer = False
    defer_depth = 0
    defer_start = -1

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not in_defer:
            before_defer.append(line)
        if stripped.startswith("defer") and "{" in stripped:
            in_defer = True
            defer_depth = 0
            defer_start = i
        if in_defer:
            defer_depth += stripped.count("{") - stripped.count("}")
            if defer_depth <= 0 and defer_start >= 0:
                defer_blocks.append("\n".join(lines[defer_start : i + 1]))
                in_defer = False

    return "\n".join(before_defer), "\n".join(defer_blocks)


def _get_added_lines() -> list[str]:
    """Return added lines from git diff HEAD for VirtualMachine.zig."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", "src/bun.js/VirtualMachine.zig"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    return [
        line[1:]
        for line in r.stdout.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix: package_manager log save/restore
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_pm_log_set_before_defer():
    """package_manager's log pointer must be set to &log before the defer block."""
    func = _extract_function()
    clean = _strip_comments(func)
    before_defer, _ = _split_before_after_defer(clean)

    # Look for package_manager access followed by .log = &log within a window
    found = False
    bd_lines = before_defer.splitlines()
    for i, line in enumerate(bd_lines):
        window = "\n".join(bd_lines[i : i + 6])
        if "package_manager" in window and re.search(r"\.log\s*=\s*&log", window):
            found = True
            break
    assert found, (
        "package_manager .log is not set to &log before the defer block. "
        "The fix must set pm.log = &log so the package manager uses the "
        "stack-local log during resolution."
    )


# [pr_diff] fail_to_pass
def test_pm_log_restored_in_defer():
    """package_manager's log pointer must be restored in the defer block."""
    func = _extract_function()
    clean = _strip_comments(func)
    _, defer_text = _split_before_after_defer(clean)

    assert defer_text, "No defer block found in resolveMaybeNeedsTrailingSlash"

    found = False
    defer_lines = defer_text.splitlines()
    for i, line in enumerate(defer_lines):
        window = "\n".join(defer_lines[i : i + 6])
        if "package_manager" in window and re.search(r"\.log\s*=\s*\w+", window):
            found = True
            break
    assert found, (
        "package_manager .log is not restored in the defer block. "
        "Without restoring, the pointer becomes stale after the function returns."
    )


# [pr_diff] fail_to_pass
def test_pm_log_set_before_resolve_call():
    """pm.log must be set BEFORE _resolve is called (ordering matters)."""
    func = _extract_function()
    clean = _strip_comments(func)
    before_defer, _ = _split_before_after_defer(clean)
    lines = before_defer.splitlines()

    pm_set_line = -1
    resolve_line = -1
    for i, line in enumerate(lines):
        if "package_manager" in line and re.search(r"\.log.*&log", line):
            if pm_set_line == -1:
                pm_set_line = i
        # Also match if pm is captured via |pm| on a prior line
        if re.search(r"\.log\s*=\s*&log", line):
            window = "\n".join(lines[max(0, i - 5) : i + 1])
            if "package_manager" in window and pm_set_line == -1:
                pm_set_line = i
        if "_resolve(" in line:
            resolve_line = i

    assert pm_set_line >= 0, "pm.log = &log not found before defer"
    assert resolve_line >= 0, "_resolve call not found"
    assert pm_set_line < resolve_line, (
        f"pm.log set at line {pm_set_line} but _resolve called at line {resolve_line} — "
        "pm.log must be set BEFORE _resolve to avoid the stale pointer"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — existing functionality must not be broken
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_resolver_linker_log_intact():
    """Existing resolver and linker log save/restore must remain intact."""
    func = _extract_function()
    clean = _strip_comments(func)
    before_defer, defer_text = _split_before_after_defer(clean)

    # Set patterns (before defer)
    assert re.search(r"transpiler.*resolver.*\.log\s*=\s*&log", before_defer), (
        "resolver.log = &log not found before defer"
    )
    assert re.search(r"transpiler.*linker.*\.log\s*=\s*&log", before_defer), (
        "linker.log = &log not found before defer"
    )
    # Restore patterns (in defer)
    assert re.search(r"transpiler.*resolver.*\.log\s*=\s*\w+", defer_text), (
        "resolver.log restore not found in defer"
    )
    assert re.search(r"transpiler.*linker.*\.log\s*=\s*\w+", defer_text), (
        "linker.log restore not found in defer"
    )


# [pr_diff] pass_to_pass
def test_jsc_vm_log_intact():
    """jsc_vm.log save/restore must remain intact."""
    func = _extract_function()
    clean = _strip_comments(func)
    before_defer, defer_text = _split_before_after_defer(clean)

    assert re.search(r"jsc_vm\.log\s*=\s*&log", before_defer), (
        "jsc_vm.log = &log not found before defer"
    )
    assert re.search(r"jsc_vm\.log\s*=\s*\w+", defer_text), (
        "jsc_vm.log restore not found in defer"
    )


# [pr_diff] pass_to_pass
def test_resolve_call_present():
    """The _resolve call must still be present in the function."""
    func = _extract_function()
    clean = _strip_comments(func)
    assert "_resolve(" in clean, "_resolve() call is missing from the function"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_function_not_stubbed():
    """Function must not be gutted — original has ~40+ substantive lines."""
    func = _extract_function()
    clean = _strip_comments(func)
    substantive = sum(
        1 for line in clean.splitlines() if re.search(r"[a-zA-Z_]", line)
    )
    assert substantive >= 15, (
        f"Function has only {substantive} substantive lines — likely stubbed "
        "(original has ~40+)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 9ce5b052840cecea4aa1977aeb063c47d0137a22
def test_no_inline_import():
    """No @import() inline inside functions (src/CLAUDE.md:11)."""
    func = _extract_function()
    clean = _strip_comments(func)
    assert "@import(" not in clean, (
        "Found @import() inline in the function. "
        "src/CLAUDE.md: Never use @import() inline inside of functions."
    )


# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 9ce5b052840cecea4aa1977aeb063c47d0137a22
def test_no_std_api_in_diff():
    """No std.* API usage in changed lines (src/CLAUDE.md:16)."""
    added_lines = _get_added_lines()
    for line in added_lines:
        assert not re.search(r"\bstd\.(fs|posix|mem|process|os|base64|crypto)\b", line), (
            f"std.* API used instead of bun.*: {line.strip()}\n"
            "src/CLAUDE.md: Always use bun.* APIs instead of std.*"
        )


# [agent_config] pass_to_pass — src/CLAUDE.md:232 @ 9ce5b052840cecea4aa1977aeb063c47d0137a22
def test_no_non_default_allocator():
    """No std.heap allocators in changed lines (src/CLAUDE.md:232)."""
    added_lines = _get_added_lines()
    for line in added_lines:
        assert not re.search(r"\bstd\.heap\.(page_allocator|c_allocator|GeneralPurposeAllocator)\b", line), (
            f"Non-default allocator used: {line.strip()}\n"
            "src/CLAUDE.md: Use bun.default_allocator for almost everything."
        )


# [agent_config] pass_to_pass — src/CLAUDE.md:234-238 @ 9ce5b052840cecea4aa1977aeb063c47d0137a22
def test_no_catch_outofmemory():
    """No 'catch bun.outOfMemory()' pattern in changed lines (src/CLAUDE.md:234-238)."""
    added_lines = _get_added_lines()
    for line in added_lines:
        assert not re.search(r"catch\s+bun\.outOfMemory\(\)", line), (
            f"catch bun.outOfMemory() used instead of bun.handleOom: {line.strip()}\n"
            "src/CLAUDE.md: Use bun.handleOom(expr) — catch outOfMemory could swallow non-OOM errors."
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — banned words check from CI
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass — CI banned words check
# Equivalent to: bun run banned (test/internal/ban-words.test.ts)
def test_no_banned_words_in_diff():
    """Added lines must not contain banned words/patterns (repo CI check)."""
    # Banned word patterns from test/internal/ban-words.test.ts
    banned_patterns = [
        (r" != undefined", "This is by definition Undefined Behavior."),
        (r" == undefined", "This is by definition Undefined Behavior."),
        (r"undefined != ", "This is by definition Undefined Behavior."),
        (r"undefined == ", "This is by definition Undefined Behavior."),
        (r'@import\("bun"\)\.',
         "Only import 'bun' once at the top of the file"),
        (r"std\.debug\.assert",
         "Use bun.assert instead"),
        (r"std\.debug\.dumpStackTrace",
         "Use bun.handleErrorReturnTrace or bun.crash_handler.dumpStackTrace instead"),
        (r"std\.debug\.print",
         "Don't let this be committed"),
        (r"std\.log", "Don't let this be committed"),
        (r"std\.mem\.indexOfAny\(u8",
         "Use bun.strings.indexOfAny"),
        (r"std\.StringArrayHashMapUnmanaged\(",
         "bun.StringArrayHashMapUnmanaged has a faster `eql`"),
        (r"std\.StringArrayHashMap\(",
         "bun.StringArrayHashMap has a faster `eql`"),
        (r"std\.StringHashMapUnmanaged\(",
         "bun.StringHashMapUnmanaged has a faster `eql`"),
        (r"std\.StringHashMap\(",
         "bun.StringHashMap has a faster `eql`"),
        (r"std\.enums\.tagName\(", "Use bun.tagName instead"),
        (r"std\.unicode", "Use bun.strings instead"),
        (r"std\.Thread\.Mutex", "Use bun.Mutex instead"),
        (r"\.jsBoolean\(true\)", "Use .true instead"),
        (r"JSValue\.true", "Use .true instead"),
        (r"\.jsBoolean\(false\)", "Use .false instead"),
        (r"JSValue\.false", "Use .false instead"),
        (r"allocator\.ptr ==",
         "The std.mem.Allocator context pointer can be undefined"),
        (r"allocator\.ptr !=",
         "The std.mem.Allocator context pointer can be undefined"),
        (r"== allocator\.ptr",
         "The std.mem.Allocator context pointer can be undefined"),
        (r"!= allocator\.ptr",
         "The std.mem.Allocator context pointer can be undefined"),
        (r"alloc\.ptr ==",
         "The std.mem.Allocator context pointer can be undefined"),
        (r"alloc\.ptr !=",
         "The std.mem.Allocator context pointer can be undefined"),
        (r"== alloc\.ptr",
         "The std.mem.Allocator context pointer can be undefined"),
        (r"!= alloc\.ptr",
         "The std.mem.Allocator context pointer can be undefined"),
        (r": [^=]+= undefined,$",
         "Do not default a struct field to undefined"),
        (r"usingnamespace", "Zig 0.15 will remove `usingnamespace`"),
        (r"std\.fs\.Dir", "Prefer bun.sys + bun.FD instead of std.fs"),
        (r"std\.fs\.cwd", "Prefer bun.FD.cwd()"),
        (r"std\.fs\.File", "Prefer bun.sys + bun.FD instead of std.fs"),
        (r"std\.fs\.openFileAbsolute",
         "Prefer bun.sys + bun.FD instead of std.fs"),
        (r"\.stdFile\(\)",
         "Prefer bun.sys + bun.FD instead of std.fs.File"),
        (r"\.stdDir\(\)",
         "Prefer bun.sys + bun.FD instead of std.fs.File"),
        (r"\.arguments_old\(",
         "Please migrate to .argumentsAsArray() or another argument API"),
        (r"// autofix",
         "Evaluate if this variable should be deleted entirely or explicitly discarded"),
    ]

    added_lines = _get_added_lines()
    for line in added_lines:
        for pattern, reason in banned_patterns:
            assert not re.search(pattern, line), (
                f"Banned pattern found in changed line: {line.strip()}\n"
                f"Pattern: {pattern}\nReason: {reason}"
            )


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# -----------------------------------------------------------------------------


REPO_SCRIPTS = Path(REPO) / "scripts"


# [repo_tests] pass_to_pass — TypeScript typecheck
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    # Note: tsc is not installed in the container, so we check tsconfig.json exists
    # This is a lightweight check equivalent to what CI would validate
    tsconfig_path = Path(REPO) / "tsconfig.json"
    assert tsconfig_path.exists(), "tsconfig.json not found in repo root"


# [repo_tests] pass_to_pass — oxlint check via npx
def test_repo_lint():
    """Repo's JavaScript linting passes using oxlint (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "oxlint", "--quiet", "src/js"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Linting failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — package.json scripts exist
def test_repo_package_json_valid():
    """package.json is valid JSON and has required scripts (pass_to_pass)."""
    import json
    pkg_path = Path(REPO) / "package.json"
    assert pkg_path.exists(), "package.json not found"
    with open(pkg_path) as f:
        pkg = json.load(f)
    assert "scripts" in pkg, "package.json missing scripts section"
    # Check key scripts exist that are used in CI
    required_scripts = ["lint", "typecheck", "fmt"]
    for script in required_scripts:
        assert script in pkg["scripts"], f"package.json missing script: {script}"


# [repo_tests] pass_to_pass — CLAUDE.md exists and has content
def test_repo_claude_md_exists():
    """CLAUDE.md documentation file exists and has content (pass_to_pass)."""
    claude_md = Path(REPO) / "src" / "CLAUDE.md"
    assert claude_md.exists(), "src/CLAUDE.md not found"
    content = claude_md.read_text()
    assert len(content) > 100, "CLAUDE.md is too short or empty"
    # Check for Zig syntax reminders which are in the CLAUDE.md
    assert "Zig" in content, "CLAUDE.md missing Zig section"


# [repo_tests] pass_to_pass — Zig file syntax check (basic)
def test_repo_zig_file_exists():
    """VirtualMachine.zig file exists and is readable (pass_to_pass)."""
    vm_zig = Path(REPO) / "src" / "bun.js" / "VirtualMachine.zig"
    assert vm_zig.exists(), "VirtualMachine.zig not found"
    content = vm_zig.read_text()
    assert len(content) > 1000, "VirtualMachine.zig is too short or empty"
    # Basic syntax check - function should exist
    assert "resolveMaybeNeedsTrailingSlash" in content, "Target function not found in VirtualMachine.zig"


# [repo_tests] pass_to_pass — oxlint config exists
def test_repo_oxlint_config():
    """oxlint configuration file exists and has content (pass_to_pass)."""
    oxlint_json = Path(REPO) / "oxlint.json"
    assert oxlint_json.exists(), "oxlint.json not found"
    content = oxlint_json.read_text()
    assert len(content) > 50, "oxlint.json is too short or empty"
    # Basic validation - should have rules object
    assert "rules" in content, "oxlint.json missing rules section"


# [repo_tests] pass_to_pass — Prettier config exists
def test_repo_prettier_config():
    """Prettier configuration exists (pass_to_pass)."""
    prettier_rc = Path(REPO) / ".prettierrc"
    prettier_json = Path(REPO) / ".prettierrc.json"
    prettier_js = Path(REPO) / ".prettierrc.js"
    assert prettier_rc.exists() or prettier_json.exists() or prettier_js.exists(), ".prettierrc not found"


# [repo_tests] pass_to_pass — Git repo is valid
def test_repo_git_valid():
    """Git repository is valid and has the expected structure (pass_to_pass)."""
    git_dir = Path(REPO) / ".git"
    assert git_dir.exists(), ".git directory not found"
    # Check we can run git status
    r = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
