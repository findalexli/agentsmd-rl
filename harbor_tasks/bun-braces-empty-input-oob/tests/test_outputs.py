"""
Task: bun-braces-empty-input-oob
Repo: oven-sh/bun @ 5b7fe81279a40f3fccebe6e7f52278c81b39dfb6
PR:   28490

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
TARGET = Path(REPO) / "src" / "shell" / "braces.zig"


def _src():
    return TARGET.read_text()


def _get_diff():
    r = subprocess.run(["git", "diff", "HEAD"], capture_output=True, text=True, cwd=REPO)
    diff = r.stdout
    if not diff:
        r = subprocess.run(
            ["git", "diff", "--cached"], capture_output=True, text=True, cwd=REPO
        )
        diff = r.stdout
    return diff


def _added_lines(diff):
    return [
        line[1:]
        for line in diff.split("\n")
        if line.startswith("+") and not line.startswith("+++")
    ]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_braces_zig_structure_intact():
    """braces.zig exists and contains core Parser struct with key functions."""
    content = _src()
    assert "pub const Parser = struct" in content
    for fn_name in ("flattenTokens", "advance", "prev", "peek", "is_at_end"):
        assert f"fn {fn_name}(" in content, f"Missing function: {fn_name}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_flatten_tokens_empty_guard():
    """flattenTokens must guard against empty token list before first items[] access.

    Bug: flattenTokens calls items[0] unconditionally — panics when token list is empty.
    Valid fixes: 'if (len == 0) return', 'if (len < 1) return', wrap body, etc.
    """
    lines = _src().splitlines()

    # Find the flattenTokens function definition line
    fn_line = next(
        (i for i, l in enumerate(lines) if "fn flattenTokens(" in l), None
    )
    assert fn_line is not None, "flattenTokens not found in braces.zig"

    # Find first unconditional items[] access after the function start
    first_access = None
    for i in range(fn_line + 1, min(fn_line + 80, len(lines))):
        stripped = lines[i].strip()
        if stripped.startswith("//"):
            continue
        if re.search(r"items\[", stripped):
            first_access = i
            break

    assert first_access is not None, "No items[] access found near flattenTokens"

    # There must be an empty/length guard BEFORE the first items[] access
    guard_found = False
    for i in range(fn_line + 1, first_access):
        stripped = lines[i].strip()
        if stripped.startswith("//"):
            continue
        # Guard patterns: .len == 0, .len < 1, tokens.items.len check
        if re.search(r"\.len\s*(==\s*0|<\s*1)", stripped) and "return" in stripped:
            guard_found = True
            break
        # Early-return guard split across two lines
        if re.search(r"\.len\s*(==\s*0|<\s*1)", stripped):
            for j in range(i + 1, min(i + 3, first_access)):
                if "return" in lines[j].strip():
                    guard_found = True
                    break
            if guard_found:
                break
        # Wrap body in if (len > 0) { ... }
        if re.search(r"if\s*\(.*\.len\s*(>|!=|>=)", stripped):
            guard_found = True
            break

    assert guard_found, (
        f"No empty-token guard found in flattenTokens before items[] access "
        f"at line {first_access + 1}"
    )


# [pr_diff] fail_to_pass
def test_advance_prev_no_underflow():
    """advance()/prev() must not underflow when current == 0.

    Bug: advance() calls self.prev() which does current-1; u32 underflows at 0.
    Valid fixes:
      A) advance() uses conditional: 'return if (self.current > 0) self.prev() else ...'
      B) prev() guards: 'if (self.current == 0) return .eof;'
      C) Either uses saturating subtraction (-|)
    """
    lines = _src().splitlines()

    # Find the Parser struct
    parser_line = next(
        (i for i, l in enumerate(lines) if "pub const Parser = struct" in l), None
    )
    assert parser_line is not None, "pub const Parser = struct not found"

    # Find advance() and prev() inside Parser (search from parser_line)
    advance_line = next(
        (
            i
            for i, l in enumerate(lines)
            if i > parser_line and "fn advance(" in l
        ),
        None,
    )
    prev_line = next(
        (
            i
            for i, l in enumerate(lines)
            if i > parser_line and "fn prev(" in l
        ),
        None,
    )
    assert advance_line is not None, "fn advance( not found in Parser"
    assert prev_line is not None, "fn prev( not found in Parser"

    fixed = False

    # Approach A: advance() uses conditional return instead of bare prev()
    for i in range(advance_line, min(advance_line + 20, len(lines))):
        stripped = lines[i].strip()
        if stripped.startswith("//"):
            continue
        # Conditional return pattern
        if re.search(r"return\s+if\s*\(.*current", stripped) and "prev" in stripped:
            fixed = True
            break
        # Guard: if (current > 0 || != 0) before calling prev
        if re.search(r"current\s*(>|!=|>=)\s*(0|1)", stripped) and "prev" in stripped:
            fixed = True
            break
        # Saturating sub in advance
        if "-|" in stripped and "current" in stripped:
            fixed = True
            break

    # Approach B: prev() guards against current == 0
    if not fixed:
        for i in range(prev_line, min(prev_line + 15, len(lines))):
            stripped = lines[i].strip()
            if stripped.startswith("//"):
                continue
            if re.search(r"current\s*==\s*0", stripped) and "return" in stripped:
                fixed = True
                break
            # Saturating sub in prev
            if "-|" in stripped and "current" in stripped:
                fixed = True
                break
            if "@max" in stripped and "current" in stripped:
                fixed = True
                break

    assert fixed, (
        "advance()/prev() still vulnerable to u32 underflow: "
        "no guard found for current==0 in either function"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_prev_normal_case_intact():
    """prev() still accesses current-1 for the non-zero case (not replaced by stub)."""
    content = _src()
    assert any(s in content for s in ("current - 1", "current -| 1")), (
        "prev() no longer accesses current-1 — normal case may be broken"
    )


# [static] pass_to_pass
def test_flatten_tokens_not_stub():
    """flattenTokens still has real brace-expansion logic (not a stub return)."""
    content = _src()
    assert "brace_count" in content, "brace_count variable missing — flattenTokens may be stubbed"
    assert ".open" in content, ".open token reference missing"
    lines = content.splitlines()
    fn_line = next((i for i, l in enumerate(lines) if "fn flattenTokens(" in l), None)
    assert fn_line is not None
    # Count substantive lines in the ~60 lines after the function signature
    body = [
        l
        for l in lines[fn_line : fn_line + 70]
        if l.strip() and not l.strip().startswith("//")
    ]
    assert len(body) >= 15, f"flattenTokens only {len(body)} lines — likely stubbed"


# ---------------------------------------------------------------------------
# Repo CI/CD checks (pass_to_pass) — from .github/workflows/*.yml
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass — JS lint from lint.yml
def test_repo_oxlint_brace_test():
    """Repo's oxlint passes on shell/brace.test.ts (pass_to_pass).

    From .github/workflows/lint.yml:
      - name: Lint
        run: bun lint  # which runs oxlint
    """
    r = subprocess.run(
        ["npx", "oxlint", "test/js/bun/shell/brace.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Check for "0 errors" in output since --deny-warnings causes exit 1 on warnings
    assert "0 errors" in r.stdout, f"oxlint found errors in brace.test.ts:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — JS lint on shell lex tests
def test_repo_oxlint_shell_lex():
    """Repo's oxlint passes on shell/lex.test.ts (pass_to_pass).

    Tests that the shell lexer test file has no lint errors.
    From .github/workflows/lint.yml: bun lint (oxlint on src/js and test)
    """
    r = subprocess.run(
        ["npx", "oxlint", "test/js/bun/shell/lex.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Check for "0 errors" in output since --deny-warnings causes exit 1 on warnings
    assert "0 errors" in r.stdout, f"oxlint found errors in lex.test.ts:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — JS lint on shell bunshell tests
def test_repo_oxlint_shell_bunshell():
    """Repo's oxlint passes on shell/bunshell.test.ts (pass_to_pass).

    Tests that the main shell test file has no lint errors.
    From .github/workflows/lint.yml: bun lint (oxlint on src/js and test)
    """
    r = subprocess.run(
        ["npx", "oxlint", "test/js/bun/shell/bunshell.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Check for "0 errors" in output since --deny-warnings causes exit 1 on warnings
    assert "0 errors" in r.stdout, f"oxlint found errors in bunshell.test.ts:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — JS lint on shell parse tests
def test_repo_oxlint_shell_parse():
    """Repo's oxlint passes on shell/parse.test.ts (pass_to_pass).

    Tests that the shell parser test file has no lint errors.
    From .github/workflows/lint.yml: bun lint (oxlint on src/js and test)
    """
    r = subprocess.run(
        ["npx", "oxlint", "test/js/bun/shell/parse.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Check for "0 errors" in output since --deny-warnings causes exit 1 on warnings
    assert "0 errors" in r.stdout, f"oxlint found errors in parse.test.ts:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Prettier format check on shell test files
def test_repo_prettier_shell_tests():
    """Repo's shell test files are properly formatted (pass_to_pass).

    From .github/workflows/format.yml:
      - bun run prettier (checks formatting on scripts, packages, src, test)
    """
    r = subprocess.run(
        ["npx", "prettier", "--check", "test/js/bun/shell/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"prettier check failed on shell tests:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [static] pass_to_pass — Banned words check for Zig files
def test_repo_banned_words_zig():
    """Modified Zig files do not contain banned words (pass_to_pass).

    From test/internal/ban-words.test.ts:
      - std.debug.assert: Use bun.assert instead
      - std.debug.print: Don't let this be committed
      - std.log: Don't let this be committed
      - std.fs: Prefer bun.sys + bun.FD instead of std.fs
      - std.posix: Prefer bun.sys APIs
      - std.os: Prefer bun.sys APIs
      - std.process: Use bun.spawn instead
    """
    # Get diff to see what Zig files were modified
    diff = _get_diff()
    if not diff:
        # No changes yet - check the base file itself for banned words
        content = _src()
    else:
        # Check only added lines in Zig files
        content = "\n".join(_added_lines(diff))

    # Banned words/patterns from ban-words.test.ts that apply to Zig
    banned_patterns = [
        ("std.debug.assert", "Use bun.assert instead"),
        ("std.debug.print", "Don't let this be committed"),
        ("std.debug.dumpStackTrace", "Use bun.handleErrorReturnTrace instead"),
        ("std.log", "Don't let this be committed"),
        ("std.fs.Dir", "Prefer bun.sys + bun.FD instead of std.fs"),
        ("std.fs.cwd", "Prefer bun.FD.cwd()"),
        ("std.fs.File", "Prefer bun.sys + bun.FD instead of std.fs"),
        ("std.fs.openFileAbsolute", "Prefer bun.sys + bun.FD instead of std.fs"),
        (".stdFile()", "Prefer bun.sys + bun.FD instead of std.fs.File"),
        (".stdDir()", "Prefer bun.sys + bun.FD instead of std.fs.File"),
        ("std.posix", "Prefer bun.sys APIs instead of std.posix"),
        ("std.os.", "Prefer bun.sys APIs instead of std.os"),
        ("std.process", "Use bun.spawn instead of std.process"),
        ("allocator.ptr ==", "Allocator pointer comparison is undefined behavior"),
        ("allocator.ptr !=", "Allocator pointer comparison is undefined behavior"),
        ("alloc.ptr ==", "Allocator pointer comparison is undefined behavior"),
        ("alloc.ptr !=", "Allocator pointer comparison is undefined behavior"),
        ("usingnamespace", "Zig 0.15 will remove usingnamespace"),
    ]

    for pattern, reason in banned_patterns:
        assert pattern not in content, f"Banned word '{pattern}' found: {reason}"


# [static] pass_to_pass — git repository integrity
def test_repo_git_status_clean():
    """Git repository has clean status at base commit (pass_to_pass).

    Verifies the repo was properly checked out and is in expected state.
    """
    # Check we are at expected commit
    r = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert r.returncode == 0, "git rev-parse failed"
    commit = r.stdout.strip()
    # Accept either the full or short base commit
    base_commit = "5b7fe81279a40f3fccebe6e7f52278c81b39dfb6"
    assert commit in [base_commit, base_commit[:7]], (
        f"Not at expected base commit: {commit}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 5b7fe81
def test_no_prohibited_std_apis():
    """New code must not use std.fs, std.posix, std.os, std.process (src/CLAUDE.md:16)."""
    diff = _get_diff()
    if not diff:
        return  # no changes — vacuously passes
    prohibited = ["std.fs", "std.posix", "std.os", "std.process"]
    for line in _added_lines(diff):
        for api in prohibited:
            assert api not in line, f"Prohibited API '{api}' in added line: {line.strip()}"


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 5b7fe81
def test_no_inline_imports():
    """@import() must not appear inline inside function bodies (src/CLAUDE.md:11)."""
    diff = _get_diff()
    if not diff:
        return  # no changes — vacuously passes
    for line in _added_lines(diff):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        if "@import(" in stripped and not re.match(r"^\s*(pub\s+)?const\s+", stripped):
            assert False, f"Inline @import found in added code: {stripped}"


# [agent_config] pass_to_pass — src/CLAUDE.md:25 @ 5b7fe81
def test_no_std_mem_for_strings():
    """Must not use std.mem.eql/indexOf/startsWith for strings; use bun.strings.* (src/CLAUDE.md:25)."""
    diff = _get_diff()
    if not diff:
        return  # no changes — vacuously passes
    prohibited_string_fns = ["std.mem.eql", "std.mem.indexOf", "std.mem.startsWith", "std.mem.endsWith"]
    for line in _added_lines(diff):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        for fn in prohibited_string_fns:
            assert fn not in stripped, (
                f"Use bun.strings.* instead of '{fn}' for string operations: {stripped}"
            )


# [agent_config] pass_to_pass — src/CLAUDE.md:234 @ 5b7fe81
def test_no_catch_outofmemory_pattern():
    """Must use bun.handleOom() not 'catch bun.outOfMemory()' (src/CLAUDE.md:234)."""
    diff = _get_diff()
    if not diff:
        return  # no changes — vacuously passes
    for line in _added_lines(diff):
        assert "catch bun.outOfMemory()" not in line, (
            f"Use bun.handleOom() not catch bun.outOfMemory(): {line.strip()}"
        )


# [repo_tests] pass_to_pass — TypeScript typecheck
def test_repo_typecheck():
    """TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "-p", "typescript", "tsc", "--noEmit"], capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"
