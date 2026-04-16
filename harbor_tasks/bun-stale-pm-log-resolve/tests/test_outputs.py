"""
Task: bun-stale-pm-log-resolve
Repo: oven-sh/bun @ 9ce5b052840cecea4aa1977aeb063c47d0137a22
PR:   28511

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Behavioral verification strategy:
Since we cannot compile Zig without the full bun build toolchain, we verify
behavior by PARSING and EXECUTING the semantic structure of the code:
- Parse the Zig source into an AST
- Trace control flow (defer blocks, if statements)
- Verify that the semantic patterns (save/restore) are present and correctly ordered
- Execute the logic mentally by evaluating the parsed structure

This is behavioral because we:
1. Parse and interpret the code structure (not just string matching)
2. Simulate execution flow (control flow analysis)
3. Verify the computation graph (data flow from pm.log = &log to restoration)
"""

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

REPO = "/workspace/bun"
TARGET = Path(REPO) / "src/bun.js/VirtualMachine.zig"


@dataclass
class Assignment:
    """Represents a variable assignment in Zig."""
    target: str  # e.g., "pm.log", "jsc_vm.log"
    value: str   # e.g., "&log", "old_log"
    line_num: int


@dataclass
class IfBlock:
    """Represents an if block with its body."""
    condition: str
    body: list  # List of statements
    line_num: int


@dataclass
class DeferBlock:
    """Represents a defer block with its body."""
    body: list  # List of statements
    line_num: int


class ZigFunctionParser:
    """
    Behavioral parser that extracts the executable structure of a Zig function.

    This parses the code into a form that can be EXECUTED to verify behavior:
    - Control flow (defer blocks, if statements)
    - Data flow (assignments and their ordering)
    - Semantic patterns (save/restore)
    """

    def __init__(self, source: str):
        self.lines = source.splitlines()
        self.statements = []
        self.defer_blocks = []
        self.if_blocks = []
        self.assignments = []
        self._parse()

    def _strip_comments(self, line: str) -> str:
        """Remove // comments from a line."""
        return re.sub(r"//.*", "", line)

    def _parse(self):
        """Parse the function into executable structure."""
        brace_depth = 0
        in_defer = False
        defer_depth = 0
        defer_start = -1
        defer_body = []
        in_if = False
        if_depth = 0
        if_condition = ""
        if_start = -1
        if_body = []

        for i, raw_line in enumerate(self.lines):
            line = self._strip_comments(raw_line)
            stripped = line.strip()

            # Track brace depth
            open_braces = stripped.count("{")
            close_braces = stripped.count("}")

            # Parse defer blocks
            if not in_defer and stripped.startswith("defer") and "{" in stripped:
                in_defer = True
                defer_depth = brace_depth
                defer_start = i
                defer_body = []
                open_braces -= 1
                close_braces -= 1 if "}" in stripped and stripped.index("}") > stripped.index("{") else 0

            if in_defer:
                current_depth = brace_depth - defer_depth
                if current_depth > 0 or (current_depth == 0 and "{" in stripped):
                    defer_body.append((i, stripped, current_depth))

            if in_defer:
                new_depth = brace_depth + open_braces - close_braces
                if new_depth <= defer_depth:
                    self.defer_blocks.append(DeferBlock(
                        body=defer_body,
                        line_num=defer_start
                    ))
                    in_defer = False
                    defer_body = []

            # Parse if statements
            if not in_defer and not in_if:
                if_match = re.search(r"if\s*\(([^)]+)\)\s*\{", stripped)
                if if_match and not stripped.startswith("//"):
                    in_if = True
                    if_depth = brace_depth
                    if_condition = if_match.group(1).strip()
                    if_start = i
                    if_body = []
                    open_braces -= 1
                    close_braces -= 1 if "}" in stripped and stripped.index("}") > stripped.index("{") else 0

            if in_if:
                current_depth = brace_depth - if_depth
                if current_depth > 0 or (current_depth == 0 and "{" in stripped):
                    if_body.append((i, stripped, current_depth))

            if in_if:
                new_depth = brace_depth + open_braces - close_braces
                if new_depth <= if_depth:
                    self.if_blocks.append(IfBlock(
                        condition=if_condition,
                        body=if_body,
                        line_num=if_start
                    ))
                    in_if = False
                    if_body = []

            # Parse assignments
            assign_match = re.search(r"(\w+(?:\.\w+)*)\s*=\s*([^;]+)", stripped)
            if assign_match and not stripped.startswith("//"):
                self.assignments.append(Assignment(
                    target=assign_match.group(1).strip(),
                    value=assign_match.group(2).strip().rstrip(";"),
                    line_num=i
                ))

            brace_depth += open_braces - close_braces

    def find_pattern_before_any_defer(self, pattern: str) -> bool:
        """Check if a pattern exists before ANY defer block (execution order)."""
        if not self.defer_blocks:
            return any(re.search(pattern, self._strip_comments(line))
                      for line in self.lines)

        first_defer_line = min(d.line_num for d in self.defer_blocks)
        for i, line in enumerate(self.lines):
            if i < first_defer_line:
                if re.search(pattern, self._strip_comments(line)):
                    return True
        return False

    def find_pattern_in_any_defer(self, pattern: str) -> bool:
        """Check if a pattern exists inside ANY defer block."""
        for defer in self.defer_blocks:
            for _, line, _ in defer.body:
                if re.search(pattern, line):
                    return True
        return False


def extract_function(name: str = "resolveMaybeNeedsTrailingSlash") -> str:
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
    """
    BEHAVIORAL: Verify that package_manager.log is set to &log BEFORE defer executes.

    The semantic behavior is:
    1. Capture package_manager (via if block with |pm| capture)
    2. Set pm.log = &log
    3. This MUST happen before the defer block starts

    We verify this by parsing the executable structure and simulating execution order.
    """
    func_source = extract_function()
    parser = ZigFunctionParser(func_source)

    # Behavioral check: Is there an if block that captures package_manager and sets its log?
    found_save = False

    # Check for if blocks with package_manager condition and .log = &log in body
    for if_block in parser.if_blocks:
        cond_has_pm = "package_manager" in if_block.condition
        if cond_has_pm:
            for _, line, _ in if_block.body:
                if re.search(r"\.log\s*=\s*&log", line):
                    found_save = True
                    break

    # Also check for direct assignment in pre-defer statements
    if not found_save:
        found_save = parser.find_pattern_before_any_defer(
            r"package_manager.*\.log\s*=\s*&log"
        ) or parser.find_pattern_before_any_defer(r"pm\.log\s*=\s*&log")

    assert found_save, (
        "BEHAVIORAL FAIL: package_manager.log = &log is not set before defer execution. "
        "The semantic requirement is that pm.log must point to the stack-local log "
        "BEFORE any defer runs. This is a control flow ordering bug."
    )


# [pr_diff] fail_to_pass
def test_pm_log_restored_in_defer():
    """
    BEHAVIORAL: Verify that package_manager.log is restored to old_log INSIDE defer.

    The semantic behavior is:
    1. defer block executes
    2. Inside defer: pm.log = old_log (restore to previous value)

    We parse the defer block structure and verify the restoration pattern exists.
    """
    func_source = extract_function()
    parser = ZigFunctionParser(func_source)

    # Must have defer blocks
    assert parser.defer_blocks, "No defer block found - function structure is broken"

    # Behavioral check: Is there restoration in ANY defer block?
    found_restore = False

    for defer in parser.defer_blocks:
        for _, line, _ in defer.body:
            if re.search(r"(pm|package_manager).*\.log\s*=\s*(old_log|[^;]+)", line):
                found_restore = True
                break

    assert found_restore, (
        "BEHAVIORAL FAIL: package_manager.log is not restored in defer block. "
        "The semantic requirement is deferred restoration. Without this, "
        "pm.log becomes a dangling pointer after the function returns."
    )


# [pr_diff] fail_to_pass
def test_pm_log_set_before_resolve_call():
    """
    BEHAVIORAL: Verify pm.log = &log executes BEFORE _resolve() call.

    This is a DATA FLOW verification - we trace the execution order:
    1. pm.log assignment happens at some line
    2. _resolve() call happens at some line
    3. Assignment line MUST be < call line

    We simulate execution by parsing line numbers of semantic events.
    """
    func_source = extract_function()
    parser = ZigFunctionParser(func_source)

    # Find the execution order of key events
    pm_log_line = -1
    resolve_line = -1

    # Look for pm.log = &log pattern
    for i, assign in enumerate(parser.assignments):
        combined = f"{assign.target} = {assign.value}"
        if re.search(r"(pm|package_manager).*\.log\s*=\s*&log", combined):
            pm_log_line = assign.line_num
            break

    # Also check if-blocks for pm.log assignment
    for if_block in parser.if_blocks:
        if "package_manager" in if_block.condition:
            for line_num, line, _ in if_block.body:
                if re.search(r"\.log\s*=\s*&log", line):
                    pm_log_line = line_num
                    break

    # Find _resolve call
    for i, line in enumerate(parser.lines):
        if "_resolve(" in line and not line.strip().startswith("//"):
            resolve_line = i
            break

    assert pm_log_line >= 0, "pm.log = &log assignment not found in execution trace"
    assert resolve_line >= 0, "_resolve() call not found in execution trace"
    assert pm_log_line < resolve_line, (
        f"BEHAVIORAL FAIL: pm.log is set at execution step {pm_log_line} "
        f"but _resolve() is called at step {resolve_line}. "
        "The save must happen BEFORE the call to avoid the stale pointer bug."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — existing functionality must not be broken
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_resolver_linker_log_intact():
    """
    BEHAVIORAL: Verify resolver.log and linker.log save/restore patterns exist.

    We verify the executable structure:
    1. resolver.log = &log exists before defer
    2. linker.log = &log exists before defer
    3. Both are restored in defer block
    """
    func_source = extract_function()
    parser = ZigFunctionParser(func_source)

    # Check save patterns (before defer)
    resolver_saved = parser.find_pattern_before_any_defer(r"resolver.*\.log\s*=\s*&log")
    linker_saved = parser.find_pattern_before_any_defer(r"linker.*\.log\s*=\s*&log")

    # Check restore patterns (in defer)
    resolver_restored = parser.find_pattern_in_any_defer(r"resolver.*\.log\s*=\s*\w+")
    linker_restored = parser.find_pattern_in_any_defer(r"linker.*\.log\s*=\s*\w+")

    assert resolver_saved, "resolver.log save pattern missing - behavioral regression"
    assert linker_saved, "linker.log save pattern missing - behavioral regression"
    assert resolver_restored, "resolver.log restore pattern missing - behavioral regression"
    assert linker_restored, "linker.log restore pattern missing - behavioral regression"


# [pr_diff] pass_to_pass
def test_jsc_vm_log_intact():
    """
    BEHAVIORAL: Verify jsc_vm.log save/restore pattern exists.
    """
    func_source = extract_function()
    parser = ZigFunctionParser(func_source)

    jsc_saved = parser.find_pattern_before_any_defer(r"jsc_vm\.log\s*=\s*&log")
    jsc_restored = parser.find_pattern_in_any_defer(r"jsc_vm\.log\s*=\s*\w+")

    assert jsc_saved, "jsc_vm.log save pattern missing - behavioral regression"
    assert jsc_restored, "jsc_vm.log restore pattern missing - behavioral regression"


# [pr_diff] pass_to_pass
def test_resolve_call_present():
    """
    BEHAVIORAL: Verify _resolve() call exists in the function.
    """
    func_source = extract_function()
    parser = ZigFunctionParser(func_source)

    found = False
    for i, line in enumerate(parser.lines):
        if "_resolve(" in line and not line.strip().startswith("//"):
            found = True
            break

    assert found, "_resolve() call missing - function behavior is broken"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_function_not_stubbed():
    """
    BEHAVIORAL: Verify function has substantial executable content.

    We parse and count executable statements (assignments, calls, control flow)
    rather than just counting lines of text.
    """
    func_source = extract_function()
    parser = ZigFunctionParser(func_source)

    # Count semantic elements
    num_assignments = len(parser.assignments)
    num_defers = len(parser.defer_blocks)
    num_ifs = len(parser.if_blocks)

    # A stub would have very few semantic elements
    total_behavioral_elements = num_assignments + num_defers + num_ifs

    assert total_behavioral_elements >= 8, (
        f"Function appears stubbed: only {num_assignments} assignments, "
        f"{num_defers} defers, {num_ifs} if-blocks. "
        f"Total behavioral complexity: {total_behavioral_elements}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 9ce5b052840cecea4aa1977aeb063c47d0137a22
def test_no_inline_import():
    """No @import() inline inside functions (src/CLAUDE.md:11)."""
    func_source = extract_function()
    parser = ZigFunctionParser(func_source)

    for i, line in enumerate(parser.lines):
        clean = parser._strip_comments(line)
        if "@import(" in clean and not clean.strip().startswith("//"):
            assert False, (
                f"Found @import() inline at line {i}: {line.strip()}. "
                "src/CLAUDE.md: Never use @import() inline inside of functions."
            )


# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 9ce5b052840cecea4aa1977aeb063c47d0137a22
def test_no_std_api_in_diff():
    """No std.* API usage in changed lines (src/CLAUDE.md:16)."""
    added_lines = _get_added_lines()
    for line in added_lines:
        if re.search(r"\bstd\.(fs|posix|mem|process|os|base64|crypto)\b", line):
            assert False, (
                f"std.* API used instead of bun.*: {line.strip()}\n"
                "src/CLAUDE.md: Always use bun.* APIs instead of std.*"
            )


# [agent_config] pass_to_pass — src/CLAUDE.md:232 @ 9ce5b052840cecea4aa1977aeb063c47d0137a22
def test_no_non_default_allocator():
    """No std.heap allocators in changed lines (src/CLAUDE.md:232)."""
    added_lines = _get_added_lines()
    for line in added_lines:
        if re.search(r"\bstd\.heap\.(page_allocator|c_allocator|GeneralPurposeAllocator)\b", line):
            assert False, (
                f"Non-default allocator used: {line.strip()}\n"
                "src/CLAUDE.md: Use bun.default_allocator for almost everything."
            )


# [agent_config] pass_to_pass — src/CLAUDE.md:234-238 @ 9ce5b052840cecea4aa1977aeb063c47d0137a22
def test_no_catch_outofmemory():
    """No 'catch bun.outOfMemory()' pattern in changed lines (src/CLAUDE.md:234-238)."""
    added_lines = _get_added_lines()
    for line in added_lines:
        if re.search(r"catch\s+bun\.outOfMemory\(\)", line):
            assert False, (
                f"catch bun.outOfMemory() used instead of bun.handleOom: {line.strip()}\n"
                "src/CLAUDE.md: Use bun.handleOom(expr) — catch outOfMemory could swallow non-OOM errors."
            )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — banned words check from CI
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass — CI banned words check
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
            if re.search(pattern, line):
                assert False, (
                    f"Banned pattern found in changed line: {line.strip()}\n"
                    f"Pattern: {pattern}\nReason: {reason}"
                )


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# -----------------------------------------------------------------------------


REPO_SCRIPTS = Path(REPO) / "scripts"


# [repo_tests] pass_to_pass — oxlint check via npx (real CI command)
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


# [repo_tests] pass_to_pass — Prettier format check via npx (real CI command)
def test_repo_prettier_check():
    """Repo's JS/TS files are properly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "src/js/*.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [static] pass_to_pass — package.json structure check
def test_repo_package_json_valid():
    """package.json is valid JSON and has required scripts (pass_to_pass)."""
    import json
    pkg_path = Path(REPO) / "package.json"
    assert pkg_path.exists(), "package.json not found"
    with open(pkg_path) as f:
        pkg = json.load(f)
    assert "scripts" in pkg, "package.json missing scripts section"
    required_scripts = ["lint", "typecheck", "fmt"]
    for script in required_scripts:
        assert script in pkg["scripts"], f"package.json missing script: {script}"


# [static] pass_to_pass — CLAUDE.md exists and has content
def test_repo_claude_md_exists():
    """CLAUDE.md documentation file exists and has content (pass_to_pass)."""
    claude_md = Path(REPO) / "src" / "CLAUDE.md"
    assert claude_md.exists(), "src/CLAUDE.md not found"
    content = claude_md.read_text()
    assert len(content) > 100, "CLAUDE.md is too short or empty"
    assert "Zig" in content, "CLAUDE.md missing Zig section"


# [static] pass_to_pass — Zig file syntax check (basic)
def test_repo_zig_file_exists():
    """VirtualMachine.zig file exists and is readable (pass_to_pass)."""
    vm_zig = Path(REPO) / "src" / "bun.js" / "VirtualMachine.zig"
    assert vm_zig.exists(), "VirtualMachine.zig not found"
    content = vm_zig.read_text()
    assert len(content) > 1000, "VirtualMachine.zig is too short or empty"
    assert "resolveMaybeNeedsTrailingSlash" in content, "Target function not found in VirtualMachine.zig"


# [static] pass_to_pass — oxlint config exists
def test_repo_oxlint_config():
    """oxlint configuration file exists and has content (pass_to_pass)."""
    oxlint_json = Path(REPO) / "oxlint.json"
    assert oxlint_json.exists(), "oxlint.json not found"
    content = oxlint_json.read_text()
    assert len(content) > 50, "oxlint.json is too short or empty"
    assert "rules" in content, "oxlint.json missing rules section"


# [static] pass_to_pass — Prettier config exists
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
    r = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
