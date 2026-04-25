"""
Task: bun-braces-empty-input-oob
Repo: oven-sh/bun @ 5b7fe81279a40f3fccebe6e7f52278c81b39dfb6
PR:   28490

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import json
import tempfile
import os
from pathlib import Path

REPO = "/workspace/bun"
TARGET = Path(REPO) / "src" / "shell" / "braces.zig"

# Track if we've done setup for repo tests
_setup_done = {"bun": False, "zig": False}


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


def _ensure_bun():
    """Ensure bun is installed and available."""
    if _setup_done["bun"]:
        return os.environ.get("PATH", "")

    # Check if bun is already available
    r = subprocess.run(["which", "bun"], capture_output=True, text=True)
    if r.returncode == 0:
        _setup_done["bun"] = True
        return os.environ.get("PATH", "")

    # Install dependencies
    subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True, text=True, timeout=60,
    )
    subprocess.run(
        ["apt-get", "install", "-y", "-qq", "unzip", "curl"],
        capture_output=True, text=True, timeout=60,
    )

    # Install bun
    subprocess.run(
        "curl -fsSL https://bun.sh/install | bash",
        shell=True, capture_output=True, text=True, timeout=120,
    )

    # Set up PATH
    new_path = "/root/.bun/bin:" + os.environ.get("PATH", "")
    os.environ["PATH"] = new_path
    _setup_done["bun"] = True
    return new_path


def _ensure_zig():
    """Ensure zig is installed and available."""
    if _setup_done["zig"]:
        return

    # Check if zig is already available
    r = subprocess.run(["which", "zig"], capture_output=True, text=True)
    if r.returncode == 0:
        _setup_done["zig"] = True
        return

    # Install dependencies
    subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True, text=True, timeout=60,
    )
    subprocess.run(
        ["apt-get", "install", "-y", "-qq", "unzip", "wget"],
        capture_output=True, text=True, timeout=60,
    )

    # Install zig
    subprocess.run(
        "mkdir -p /tmp/zig && wget -q -O /tmp/zig/zig.zip https://github.com/oven-sh/zig/releases/download/autobuild-e0b7c318f318196c5f81fdf3423816a7b5bb3112/bootstrap-x86_64-linux-musl.zip && unzip -q -d /tmp/zig /tmp/zig/zig.zip",
        shell=True, capture_output=True, text=True, timeout=120,
    )

    # Set up PATH
    new_path = "/tmp/zig/bootstrap-x86_64-linux-musl:" + os.environ.get("PATH", "")
    os.environ["PATH"] = new_path
    _setup_done["zig"] = True


def _run_js_code(js_code, timeout=30):
    """Run JavaScript code using bun and return (returncode, stdout, stderr)."""
    _ensure_bun()

    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(js_code)
        f.flush()
        tmp_path = f.name

    try:
        r = subprocess.run(
            ["bun", "run", tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return r.returncode, r.stdout, r.stderr
    finally:
        os.unlink(tmp_path)


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
def test_braces_empty_string_no_crash():
    """Bun.$.braces("") must not crash and should return [""].

    Bug: flattenTokens calls items[0] unconditionally — panics when token list is empty.
    Bug: advance() calls self.prev() which does current-1; u32 underflows at 0.

    This test verifies the ACTUAL BEHAVIOR: running braces on empty input
    should return [""] without panicking.
    """
    js_code = """
        const result = Bun.$.braces("");
        console.log(JSON.stringify(result));
    """

    returncode, stdout, stderr = _run_js_code(js_code)

    # Must not crash (returncode 0)
    assert returncode == 0, (
        f"Bun.$.braces('') crashed with exit code {returncode}.\n"
        f"stderr: {stderr[:1000]}"
    )

    # Parse the output and verify it returns [""]
    try:
        result = json.loads(stdout.strip())
    except json.JSONDecodeError:
        assert False, f"Could not parse output as JSON: {stdout[:500]}"

    # Should return [""] for empty input
    assert result == [""], (
        f"Expected [''] for empty input, got {result}"
    )


# [pr_diff] fail_to_pass
def test_braces_empty_string_parse_true():
    """Bun.$.braces("", {parse: true}) must not crash and return valid object.

    Verifies the fix works with parse:true option.
    """
    js_code = """
        const result = Bun.$.braces("", { parse: true });
        console.log(JSON.stringify(result));
    """

    returncode, stdout, stderr = _run_js_code(js_code)

    assert returncode == 0, (
        f"Bun.$.braces('', {{parse: true}}) crashed with exit code {returncode}.\n"
        f"stderr: {stderr[:1000]}"
    )

    try:
        result = json.loads(stdout.strip())
    except json.JSONDecodeError:
        assert False, f"Could not parse output as JSON: {stdout[:500]}"

    # parse:true returns { expansions: [...], tokens: [...] }
    assert isinstance(result, dict), f"Expected object, got {type(result)}"
    assert "expansions" in result, f"Expected expansions field, got {result}"


# [pr_diff] fail_to_pass
def test_braces_empty_string_tokenize_true():
    """Bun.$.braces("", {tokenize: true}) must not crash and return valid tokens.

    Verifies the fix works with tokenize:true option.
    """
    js_code = """
        const result = Bun.$.braces("", { tokenize: true });
        console.log(JSON.stringify(result));
    """

    returncode, stdout, stderr = _run_js_code(js_code)

    assert returncode == 0, (
        f"Bun.$.braces('', {{tokenize: true}}) crashed with exit code {returncode}.\n"
        f"stderr: {stderr[:1000]}"
    )

    try:
        result = json.loads(stdout.strip())
    except json.JSONDecodeError:
        assert False, f"Could not parse output as JSON: {stdout[:500]}"

    # tokenize:true returns an array of tokens
    assert isinstance(result, list), f"Expected list, got {type(result)}"


# [pr_diff] fail_to_pass
def test_braces_nonempty_input_still_works():
    """Bun.$.braces("a{b,c}d") must still work correctly after the fix.

    Regression test: the fix for empty input shouldn't break normal brace expansion.
    """
    js_code = """
        const result = Bun.$.braces("a{b,c}d");
        console.log(JSON.stringify(result));
    """

    returncode, stdout, stderr = _run_js_code(js_code)

    assert returncode == 0, (
        f"Bun.$.braces('a{{b,c}}d') crashed with exit code {returncode}.\n"
        f"stderr: {stderr[:1000]}"
    )

    try:
        result = json.loads(stdout.strip())
    except json.JSONDecodeError:
        assert False, f"Could not parse output as JSON: {stdout[:500]}"

    # a{b,c}d should expand to ["abd", "acd"]
    assert result == ["abd", "acd"], (
        f"Expected ['abd', 'acd'] for 'a{{b,c}}d', got {result}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (behavioral) — anti-stub: verifying fix is complete not partial
# ---------------------------------------------------------------------------


# [behavioral] pass_to_pass
def test_prev_normal_case_behavioral():
    """prev() still works correctly for the non-zero case — verified behaviorally.

    This test uses a Zig test that exercises prev() through normal parsing.
    It compiles and runs a test that relies on prev() working for non-zero
    current positions. Any implementation that correctly parses brace patterns
    will pass, regardless of internal variable naming.
    """
    _ensure_zig()

    # Create a test file within the repo directory that imports braces.zig
    # We need to use a relative import from within the repo
    zig_test = '''
const std = @import("std");
const braces = @import("src/shell/braces.zig");

test "prev() works correctly for non-empty input" {
    const allocator = std.testing.allocator;

    // Test with input that requires looking at previous tokens
    // The parser needs to call prev() when advancing through tokens
    const input = "a{b,c}d";

    // Tokenize first (this exercises the Lexer)
    var lexer = braces.Lexer.init(input, allocator);
    defer lexer.deinit();
    try lexer.run();

    // Now parse - this exercises advance() and prev()
    var parser = braces.Parser.init(lexer.tokens.items, input, allocator);
    const result = try parser.parse();
    defer {
        for (result.items) |item| {
            allocator.free(item);
        }
        result.deinit();
    }

    // Verify we got the expected expansions
    try std.testing.expectEqual(@as(usize, 2), result.items.len);
    try std.testing.expectEqualStrings("abd", result.items[0]);
    try std.testing.expectEqualStrings("acd", result.items[1]);
}
'''
    # Write test file in the repo directory so relative imports work
    test_path = Path(REPO) / "test_prev_behavior.zig"
    with open(test_path, 'w') as f:
        f.write(zig_test)

    try:
        # Run zig test - compile and execute the behavioral test
        r = subprocess.run(
            ["zig", "test", str(test_path)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )

        # The test passes if compilation and execution succeed
        assert r.returncode == 0, (
            f"Zig test for prev() behavior failed:\nstdout: {r.stdout[-1000:]}\nstderr: {r.stderr[-1000:]}"
        )
    finally:
        # Clean up test file
        if test_path.exists():
            test_path.unlink()


# [behavioral] pass_to_pass
def test_flatten_tokens_behavioral():
    """flattenTokens still has real brace-expansion logic — verified behaviorally.

    This test uses complex brace patterns that require flattenTokens to have
    actual implementation. A stub that doesn't properly merge adjacent text
    tokens would produce incorrect expansions.
    """
    js_code = """
        // Test that complex brace expansion still works
        // This requires flattenTokens to have real implementation
        const result = Bun.$.braces("{a,b,c}{1,2}");
        console.log(JSON.stringify(result));
    """

    returncode, stdout, stderr = _run_js_code(js_code)

    assert returncode == 0, (
        f"Complex brace expansion crashed with exit code {returncode}.\n"
        f"stderr: {stderr[:1000]}"
    )

    try:
        result = json.loads(stdout.strip())
    except json.JSONDecodeError:
        assert False, f"Could not parse output as JSON: {stdout[:500]}"

    # {a,b,c}{1,2} should expand to ["a1", "a2", "b1", "b2", "c1", "c2"]
    # If flattenTokens is stubbed or broken, we wouldn't get this correct expansion
    expected = ["a1", "a2", "b1", "b2", "c1", "c2"]
    assert result == expected, (
        f"Expected {expected} for '{{a,b,c}}{{1,2}}', got {result}. "
        f"flattenTokens may be stubbed or broken."
    )


# [behavioral] pass_to_pass
def test_flatten_tokens_adjacent_text_merging():
    """flattenTokens correctly merges adjacent text tokens — verified behaviorally.

    This test verifies that adjacent text tokens are merged during lexing,
    which is flattenTokens' core responsibility. The pattern "abc" should
    be tokenized as a single text token (not ['a', 'b', 'c']).
    """
    js_code = """
        // Tokenize a simple string to check text token merging
        const result = Bun.$.braces("abc", { tokenize: true });
        console.log(JSON.stringify(result));
    """

    returncode, stdout, stderr = _run_js_code(js_code)

    assert returncode == 0, (
        f"Tokenize test crashed with exit code {returncode}.\n"
        f"stderr: {stderr[:1000]}"
    )

    try:
        result = json.loads(stdout.strip())
    except json.JSONDecodeError:
        assert False, f"Could not parse output as JSON: {stdout[:500]}"

    # tokenize:true returns an array of tokens
    assert isinstance(result, list), f"Expected list, got {type(result)}"

    # "abc" should result in minimal tokens due to flattenTokens merging:
    # text("abc") + eof, so 2 tokens total
    # Without flattenTokens working, we'd get separate tokens for each char
    assert len(result) <= 2, (
        f"Expected at most 2 tokens (text + eof) for 'abc', got {len(result)} tokens. "
        f"flattenTokens may not be merging adjacent text tokens correctly."
    )


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


# [repo_tests] pass_to_pass — Repo banned words test
def test_repo_ban_words():
    """Repo banned words check passes (pass_to_pass).

    From .github/workflows/format.yml:
      - bun ./test/internal/ban-words.test.ts
    """
    _ensure_bun()

    # Run bun install if needed
    if not Path(REPO).joinpath("node_modules").exists():
        subprocess.run(
            ["bun", "install"],
            capture_output=True, text=True, timeout=180, cwd=REPO,
        )

    r = subprocess.run(
        ["bun", "test", "test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Banned words check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Zig fmt check on modified file
def test_repo_zig_fmt_braces():
    """Zig fmt check passes on braces.zig (pass_to_pass).

    From .github/workflows/format.yml:
      - zig fmt src (checks formatting on all Zig files)
    """
    _ensure_zig()

    r = subprocess.run(
        ["zig", "fmt", "--check", "src/shell/braces.zig"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"zig fmt check failed on braces.zig:\n{r.stderr[-500:]}{r.stdout[-500:]}"


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
    _ensure_bun()

    # Run bun install if needed
    if not Path(REPO).joinpath("node_modules").exists():
        subprocess.run(
            ["bun", "install"],
            capture_output=True, text=True, timeout=180, cwd=REPO,
        )

    r = subprocess.run(
        ["npx", "tsc", "--noEmit"], capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Additional shell test lint checks
def test_repo_oxlint_shell_assignments():
    """Repo's oxlint passes on shell/assignments-in-pipeline.test.ts (pass_to_pass).

    From .github/workflows/lint.yml: bun lint (oxlint on test files)
    """
    r = subprocess.run(
        ["npx", "oxlint", "test/js/bun/shell/assignments-in-pipeline.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert "0 errors" in r.stdout, f"oxlint found errors:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Shell default test lint
def test_repo_oxlint_shell_default():
    """Repo's oxlint passes on shell/bunshell-default.test.ts (pass_to_pass).

    From .github/workflows/lint.yml: bun lint (oxlint on test files)
    """
    r = subprocess.run(
        ["npx", "oxlint", "test/js/bun/shell/bunshell-default.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert "0 errors" in r.stdout, f"oxlint found errors:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Prettier format check on brace.test.ts
def test_repo_prettier_brace_test():
    """Repo's brace.test.ts is properly formatted (pass_to_pass).

    From .github/workflows/format.yml: bun run prettier
    """
    r = subprocess.run(
        ["npx", "prettier", "--check", "test/js/bun/shell/brace.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"prettier check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [static] pass_to_pass — Shell source files structure
def test_shell_source_structure():
    """Shell source directory contains expected Zig files (pass_to_pass).

    Verifies the src/shell/ directory has the expected structure at base commit.
    """
    shell_dir = Path(REPO) / "src" / "shell"
    expected_files = [
        "braces.zig",
        "shell.zig",
        "interpreter.zig",
    ]
    for fname in expected_files:
        assert (shell_dir / fname).exists(), f"Missing expected file: {fname}"
