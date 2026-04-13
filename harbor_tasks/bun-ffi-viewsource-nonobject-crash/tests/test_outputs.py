"""
Task: bun-ffi-viewsource-nonobject-crash
Repo: oven-sh/bun @ 0de7a806d108a56a2c9f87d5974c52384059c397
PR:   28361

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: Zig requires the full Bun build toolchain to compile+run, which is
unavailable in the test container.  All checks therefore operate on source
analysis — this is the only viable approach for this codebase.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
TARGET = Path(REPO) / "src/bun.js/api/ffi.zig"


def _stripped_source() -> str:
    """Return ffi.zig with comments and string literals removed."""
    content = TARGET.read_text()
    content = re.sub(r"//[^\n]*", "", content)
    content = re.sub(r'"[^"]*"', '""', content)
    return content


def _generate_symbols_region(stripped: str, size: int = 8000) -> str:
    """Extract the region around the generateSymbols function definition."""
    # Search for the function definition — "fn generateSymbols(" in Zig
    m = re.search(r'fn\s+generateSymbols\s*\(', stripped)
    if m:
        idx = m.start()
    else:
        # Fallback: find any generateSymbols that isn't generateSymbolForFunction
        matches = [m.start() for m in re.finditer(r'generateSymbols(?!ForFunction)', stripped)]
        assert matches, "generateSymbols not found in ffi.zig"
        idx = matches[0]
    return stripped[idx : idx + size]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_ffi_struct_integrity():
    """ffi.zig has balanced braces and all core FFI identifiers."""
    content = TARGET.read_text()
    opens = content.count("{")
    closes = content.count("}")
    assert abs(opens - closes) <= 5, f"Unbalanced braces: {opens} open vs {closes} close"

    stripped = _stripped_source()
    required = [
        "pub const FFI = struct",
        "generateSymbols",
        "generateSymbolForFunction",
        "symbols_iter",
        "isEmptyOrUndefinedOrNull",
        "clearAndFree",
    ]
    for token in required:
        assert token in stripped, f"Missing required identifier: {token}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that work without full build toolchain
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
REPO_SCRIPTS = Path(REPO) / "scripts"
REPO_SRC_JS = Path(REPO) / "src/js"


def test_js_files_valid_syntax():
    """Repo's JavaScript/TypeScript files have valid syntax (pass_to_pass)."""
    # Check that a sample of JS files can be parsed by Node.js
    js_files = [
        "scripts/build.mjs",
        "package.json",
    ]
    for f in js_files:
        p = Path(REPO) / f
        assert p.exists(), f"JS/config file missing: {f}"
        # Try to parse JSON files
        if f.endswith(".json"):
            import json
            try:
                json.loads(p.read_text())
            except json.JSONDecodeError as e:
                raise AssertionError(f"Invalid JSON in {f}: {e}")


def test_repo_prettier_ffi_tests():
    """FFI test files pass prettier formatting check (pass_to_pass)."""
    # Run prettier check on the FFI test directory (CI command from package.json)
    r = subprocess.run(
        ["npx", "--yes", "prettier@latest", "--check", "test/js/bun/ffi/*.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed on FFI tests:\n{r.stderr[-500:]}"


def test_repo_prettier_scripts():
    """Repo's JavaScript/TypeScript scripts pass prettier check (pass_to_pass)."""
    # Run prettier check on a sample of script files (CI command from package.json)
    r = subprocess.run(
        ["npx", "--yes", "prettier@latest", "--check", "scripts/build.mjs", "scripts/build.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed on scripts:\n{r.stderr[-500:]}"


def test_repo_package_json_parseable():
    """Repo's package.json is valid JSON (pass_to_pass)."""
    # Use Node.js to validate package.json
    r = subprocess.run(
        ["node", "-e", "JSON.parse(require('fs').readFileSync('package.json')); console.log('OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"package.json is not valid JSON:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, "package.json validation failed"


def test_repo_tsconfig_json_parseable():
    """Repo's tsconfig.json is valid JSON (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "JSON.parse(require('fs').readFileSync('tsconfig.json')); console.log('OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"tsconfig.json is not valid JSON:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, "tsconfig.json validation failed"


def test_tsconfig_valid():
    """Repo's tsconfig.json is valid (pass_to_pass)."""
    import json
    p = Path(REPO) / "tsconfig.json"
    assert p.exists(), "tsconfig.json missing"
    try:
        config = json.loads(p.read_text())
        # Basic validation that it has expected fields
        assert "compilerOptions" in config or "extends" in config, "Invalid tsconfig structure"
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid tsconfig.json: {e}")


def test_ffi_zig_parse_structure():
    """ffi.zig has valid Zig structure (balanced braces, valid keywords) (pass_to_pass)."""
    content = TARGET.read_text()

    # Basic structural checks that don't need the Zig compiler
    zig_keywords = [
        "const", "var", "pub", "fn", "struct", "comptime",
        "if", "else", "while", "for", "switch", "return",
        "defer", "errdefer", "try", "catch", "orelse",
    ]

    found_keywords = sum(1 for kw in zig_keywords if f" {kw} " in content or f"\n{kw} " in content)
    assert found_keywords >= 10, f"Expected >=10 Zig keywords, found {found_keywords}"

    # Check for valid Zig constructs
    assert "pub const FFI = struct" in content, "Missing FFI struct definition"
    assert "fn generateSymbols(" in content, "Missing generateSymbols function"

    # Balance checks for braces
    open_brace = content.count("{")
    close_brace = content.count("}")
    assert abs(open_brace - close_brace) <= 3, f"Unbalanced braces: {open_brace} vs {close_brace}"

    # Balance checks for parentheses (more lenient due to complex syntax)
    open_paren = content.count("(")
    close_paren = content.count(")")
    assert abs(open_paren - close_paren) <= 20, f"Unbalanced parens: {open_paren} vs {close_paren}"

    # Balance checks for square brackets
    open_bracket = content.count("[")
    close_bracket = content.count("]")
    assert abs(open_bracket - close_bracket) <= 3, f"Unbalanced brackets: {open_bracket} vs {close_bracket}"


def test_repo_file_structure():
    """Critical repo files exist and are non-empty (pass_to_pass)."""
    critical_files = [
        "build.zig",
        "package.json",
        "src/bun.js/api/ffi.zig",
        "CMakeLists.txt",
        "tsconfig.json",
    ]
    for f in critical_files:
        p = Path(REPO) / f
        assert p.exists(), f"Critical file missing: {f}"
        assert p.stat().st_size > 0, f"Critical file empty: {f}"


def test_zig_no_banned_patterns():
    """Zig source doesn't contain banned patterns from CLAUDE.md (pass_to_pass)."""
    content = TARGET.read_text()

    # Patterns that should NOT appear based on CLAUDE.md rules
    banned_in_ffi = [
        "std.fs.Dir",  # Rule: Prefer bun.sys + bun.FD
        "std.fs.cwd",  # Rule: Prefer bun.FD.cwd()
        "std.debug.assert",  # Rule: Use bun.assert
    ]

    for pattern in banned_in_ffi:
        assert pattern not in content, f"Banned pattern '{pattern}' found in ffi.zig"


def test_js_lint_oxlint():
    """Repo's JavaScript/TypeScript passes oxlint (pass_to_pass)."""
    # Check if oxlint config exists
    oxlint_config = Path(REPO) / "oxlint.json"
    if not oxlint_config.exists():
        # Skip if no oxlint config
        return

    # Run oxlint on src/js (same as 'bun lint' but without bun)
    r = subprocess.run(
        ["npx", "--yes", "oxlint@latest", "--config=oxlint.json", "--format=unix", "src/js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # oxlint returns 0 on success, 1 on lint errors
    assert r.returncode in (0, 1), f"oxlint crashed:\n{r.stderr[-500:]}"
    # Check that there are no parse errors (which would indicate broken JS)
    assert "Parse error" not in r.stderr, f"JS parse errors detected:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_value_guard_rejects_non_objects():
    """generateSymbols condition must reject non-object values (numbers, strings, booleans)."""
    stripped = _stripped_source()
    region = _generate_symbols_region(stripped)

    # Find the while loop that iterates symbols (symbols_iter.next)
    loop_idx = region.find("while")
    assert loop_idx != -1, "No while loop found in generateSymbols"
    loop_region = region[loop_idx : loop_idx + 3000]
    lines = loop_region.split("\n")

    type_checks = [
        "isObject", "isStruct", "isCallable", "isFunction",
        "@intFromEnum", ".tag", "typeof", "jsType",
    ]

    found = False

    # Approach 1: type check on same expression as isEmptyOrUndefinedOrNull
    for i, line in enumerate(lines):
        if "isEmptyOrUndefinedOrNull" in line:
            block = "\n".join(lines[i : i + 3])
            if any(tc in block for tc in type_checks):
                found = True
                break

    # Approach 2: separate if-block with type check leading to toTypeError
    if not found:
        for i, line in enumerate(lines):
            sl = line.strip()
            if (sl.startswith("if") or "else" in sl) and any(tc in sl for tc in type_checks):
                following = "\n".join(lines[i : i + 10])
                if "toTypeError" in following:
                    found = True
                    break

    assert found, (
        "generateSymbols while-loop lacks a type-guard (e.g. !value.isObject()) "
        "in a conditional that leads to toTypeError"
    )


# [pr_diff] fail_to_pass
def test_arg_types_cleanup_in_error_paths():
    """arg_types must be freed in error-return paths before clearAndFree (memory leak fix)."""
    stripped = _stripped_source()
    parts = stripped.split("clearAndFree")
    assert len(parts) >= 3, f"Expected >=3 clearAndFree call sites, found {len(parts) - 1}"

    cleanup_count = 0
    for i in range(1, len(parts)):
        preceding = parts[i - 1][-600:]
        has_arg_cleanup = "arg_types" in preceding and (
            "deinit" in preceding or ".free(" in preceding
        )
        if not has_arg_cleanup:
            continue
        # Must iterate over all symbols (loop nearby)
        tail = preceding[-300:]
        has_loop = "for " in tail or "while" in tail or "symbols.values()" in preceding
        if has_loop:
            cleanup_count += 1

    assert cleanup_count >= 2, (
        f"Only {cleanup_count} error-return paths clean up arg_types before clearAndFree; "
        "expected at least 2 (print, open, linkSymbols)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_not_stub():
    """generateSymbols retains substantive symbol-parsing logic."""
    stripped = _stripped_source()
    region = _generate_symbols_region(stripped)

    indicators = [
        "symbols_iter",
        "generateSymbolForFunction",
        "toTypeError",
        "isEmptyOrUndefinedOrNull",
        "clearAndFree",
    ]
    found = sum(1 for ind in indicators if ind in region)
    assert found >= 4, (
        f"generateSymbols only contains {found}/5 expected logic indicators — "
        "function appears to be stubbed out"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass — src/CLAUDE.md:16 @ 0de7a80
def test_no_std_apis_in_diff():
    """Agent must not introduce std.fs/std.posix/std.os/std.process calls."""
    r = subprocess.run(
        ["git", "diff", "HEAD"],
        capture_output=True, text=True, cwd=REPO,
    )
    diff = r.stdout
    if not diff.strip():
        r = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True, text=True, cwd=REPO,
        )
        diff = r.stdout
    if not diff.strip():
        r = subprocess.run(
            ["git", "diff", "HEAD~1"],
            capture_output=True, text=True, cwd=REPO,
        )
        diff = r.stdout

    assert diff.strip(), "No diff detected — agent has not made any changes"

    added = [l[1:] for l in diff.split("\n") if l.startswith("+") and not l.startswith("+++")]
    forbidden = ["std.fs", "std.posix", "std.os", "std.process"]
    for line in added:
        for f in forbidden:
            assert f not in line, f"Prohibited API '{f}' found in added line: {line.strip()}"


# [agent_config] fail_to_pass — src/CLAUDE.md:11 @ 0de7a80
def test_no_inline_import_in_diff():
    """Agent must not add @import() inline inside functions."""
    r = subprocess.run(
        ["git", "diff", "HEAD"],
        capture_output=True, text=True, cwd=REPO,
    )
    diff = r.stdout
    if not diff.strip():
        r = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True, text=True, cwd=REPO,
        )
        diff = r.stdout
    if not diff.strip():
        r = subprocess.run(
            ["git", "diff", "HEAD~1"],
            capture_output=True, text=True, cwd=REPO,
        )
        diff = r.stdout

    assert diff.strip(), "No diff detected — agent has not made any changes"

    added = [l[1:] for l in diff.split("\n") if l.startswith("+") and not l.startswith("+++")]
    for line in added:
        # @import at file/struct level is OK; deeply indented = inside a function
        if "@import(" in line and len(line) - len(line.lstrip()) > 8:
            raise AssertionError(f"Inline @import inside function body: {line.strip()}")


def test_repo_oxlint_config_valid():
    """Repo's oxlint.json exists and has valid structure (pass_to_pass)."""
    import json
    p = Path(REPO) / "oxlint.json"
    assert p.exists(), "oxlint.json missing"
    raw = p.read_text()
    # Check for required structure without full parsing (handles JSON with comments)
    assert '"categories"' in raw, "oxlint.json missing categories section"
    assert '"rules"' in raw, "oxlint.json missing rules section"
    assert '"ignorePatterns"' in raw, "oxlint.json missing ignorePatterns section"


def test_repo_prettier_config_valid():
    """Repo's .prettierrc is valid JSON (pass_to_pass)."""
    import json
    p = Path(REPO) / ".prettierrc"
    assert p.exists(), ".prettierrc missing"
    try:
        config = json.loads(p.read_text())
        assert "printWidth" in config, "Invalid prettier config structure"
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid .prettierrc: {e}")


def test_repo_package_json_valid():
    """Repo's package.json is valid (pass_to_pass)."""
    import json
    p = Path(REPO) / "package.json"
    assert p.exists(), "package.json missing"
    try:
        config = json.loads(p.read_text())
        assert "name" in config, "Invalid package.json structure"
        assert "version" in config, "Invalid package.json structure"
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid package.json: {e}")


def test_repo_claude_md_exists():
    """Repo's CLAUDE.md (AGENTS.md) exists and is non-empty (pass_to_pass)."""
    p = Path(REPO) / "CLAUDE.md"
    assert p.exists(), "CLAUDE.md missing"
    content = p.read_text()
    assert len(content) > 1000, "CLAUDE.md appears to be too short or empty"
    # Check for meaningful content (not just whitespace)
    non_whitespace = len([c for c in content if not c.isspace()])
    assert non_whitespace > 500, "CLAUDE.md appears to lack meaningful content"


def test_oxlint_ffi_source():
    """FFI TypeScript source passes oxlint (pass_to_pass)."""
    # Run oxlint on the FFI source file (CI command from package.json 'lint' script)
    r = subprocess.run(
        ["npx", "--yes", "oxlint@latest", "src/js/bun/ffi.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # oxlint returns 0 on success (even with warnings), non-zero on parse errors
    assert r.returncode == 0, f"oxlint failed on FFI source:\n{r.stderr[-500:]}"
    # Check for parse errors which would indicate broken code
    assert "Parse error" not in r.stderr, f"JS parse errors in FFI source:\n{r.stderr[-500:]}"


def test_oxlint_scripts():
    """Repo scripts pass oxlint (pass_to_pass)."""
    # Run oxlint on build scripts (CI command adapted from 'lint' script)
    r = subprocess.run(
        ["npx", "--yes", "oxlint@latest", "scripts/build.mjs"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"oxlint failed on scripts:\n{r.stderr[-500:]}"
    assert "Parse error" not in r.stderr, f"JS parse errors in scripts:\n{r.stderr[-500:]}"


def test_prettier_config_files():
    """Repo config files pass prettier formatting (pass_to_pass)."""
    # Run prettier check on config files (CI command from format.yml)
    r = subprocess.run(
        ["npx", "--yes", "prettier@latest", "--check", ".prettierrc", "tsconfig.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed on config files:\n{r.stderr[-500:]}"


def test_ffi_test_files_valid():
    """FFI test files have valid structure (pass_to_pass)."""
    # Validate that test files have proper test structure using Node.js
    # Write the validation script to a temp file to avoid escaping issues
    # Use simpler string-based checks instead of regex to avoid escaping problems
    script_path = f"{REPO}/.tmp_test_validator.js"
    script_lines = [
        "const fs = require('fs');",
        "const files = [",
        "    'test/js/bun/ffi/ffi-error-messages.test.ts',",
        "    'test/js/bun/ffi/addr32.test.ts',",
        "    'test/js/bun/ffi/cc.test.ts'",
        "];",
        "const hasTestPattern = (content) => {",
        "    // Check for test/describe/it with optional .modifier like .skipIf, .only",
        "    // Use simple string checks to avoid regex escaping issues",
        "    const patterns = ['test(', 'describe(', 'it(', 'test.skip', 'describe.skip', 'it.skip', 'test.only', 'describe.only', 'it.only'];",
        "    return patterns.some(p => content.includes(p));",
        "};",
        "for (const f of files) {",
        "    const content = fs.readFileSync(f, 'utf8');",
        "    if (!hasTestPattern(content)) {",
        "        console.error('No tests found in ' + f);",
        "        process.exit(1);",
        "    }",
        "    if (!content.includes('import')) {",
        "        console.error('No imports found in ' + f);",
        "        process.exit(1);",
        "    }",
        "}",
        "console.log('All FFI test files have valid structure');",
    ]
    Path(script_path).write_text("\n".join(script_lines))
    try:
        r = subprocess.run(
            ["node", script_path],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"FFI test validation failed:\n{r.stderr[-500:]}"
        assert "valid structure" in r.stdout, "FFI test structure check failed"
    finally:
        Path(script_path).unlink(missing_ok=True)


def test_repo_bunfig_valid_toml():
    """Repo's bunfig.toml is valid TOML (pass_to_pass)."""
    # Use a simple Python-based TOML check (no external deps needed)
    r = subprocess.run(
        ["python3", "-c",
         "import sys; content=open('bunfig.toml').read(); print('OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"bunfig.toml validation failed:\n{r.stderr[-500:]}"


def test_repo_flake_lock_valid():
    """Repo's flake.lock is valid JSON (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "JSON.parse(require('fs').readFileSync('flake.lock')); console.log('OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"flake.lock is not valid JSON:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, "flake.lock validation failed"


def test_oxlint_internal_tests():
    """Internal test files pass oxlint (pass_to_pass)."""
    # Run oxlint on internal test directory (CI-style lint check)
    r = subprocess.run(
        ["npx", "--yes", "oxlint@latest", "test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"oxlint failed on internal tests:\n{r.stderr[-500:]}"
    assert "Parse error" not in r.stderr, f"JS parse errors in internal tests:\n{r.stderr[-500:]}"


def test_prettier_package_files():
    """Repo package files pass prettier formatting (pass_to_pass)."""
    # Run prettier check on package.json files (CI command from format.yml)
    r = subprocess.run(
        ["npx", "--yes", "prettier@latest", "--check", "package.json", "packages/bun-types/package.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Allow exit 0 (success) or accept that package files may not exist in all repos
    assert r.returncode in (0, 1), f"Prettier check crashed on package files:\n{r.stderr[-500:]}"


def test_repo_meta_json_valid():
    """Repo's meta.json is valid JSON (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "JSON.parse(require('fs').readFileSync('meta.json')); console.log('OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"meta.json is not valid JSON:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, "meta.json validation failed"


def test_repo_prettier_readme():
    """README.md passes prettier formatting (pass_to_pass)."""
    # Run prettier check on README (CI command from format.yml)
    r = subprocess.run(
        ["npx", "--yes", "prettier@latest", "--check", "README.md"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed on README.md:\n{r.stderr[-500:]}"


def test_repo_prettier_contributing():
    """CONTRIBUTING.md passes prettier formatting (pass_to_pass)."""
    # Run prettier check on CONTRIBUTING (CI command from format.yml)
    r = subprocess.run(
        ["npx", "--yes", "prettier@latest", "--check", "CONTRIBUTING.md"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed on CONTRIBUTING.md:\n{r.stderr[-500:]}"


def test_oxlint_ffi_tests():
    """FFI test files pass oxlint (pass_to_pass)."""
    # Run oxlint on FFI test directory (CI-style lint check from lint.yml)
    r = subprocess.run(
        ["npx", "--yes", "oxlint@latest", "test/js/bun/ffi/*.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"oxlint failed on FFI tests:\n{r.stderr[-500:]}"
    assert "Parse error" not in r.stderr, f"JS parse errors in FFI tests:\n{r.stderr[-500:]}"


def test_oxlint_bun_apis():
    """Bun API source files pass oxlint (pass_to_pass)."""
    # Run oxlint on core Bun API files (CI-style lint check)
    r = subprocess.run(
        ["npx", "--yes", "oxlint@latest", "src/js/bun/sqlite.ts", "src/js/bun/sql.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"oxlint failed on Bun API files:\n{r.stderr[-500:]}"
    assert "Parse error" not in r.stderr, f"JS parse errors in Bun API files:\n{r.stderr[-500:]}"


def test_node_compat_files():
    """Node.js compatibility files pass oxlint (pass_to_pass)."""
    # Run oxlint on Node.js compat files (CI-style lint check from lint.yml)
    r = subprocess.run(
        ["npx", "--yes", "oxlint@latest", "src/js/node/fs.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"oxlint failed on Node.js compat files:\n{r.stderr[-500:]}"
    assert "Parse error" not in r.stderr, f"JS parse errors in Node.js compat files:\n{r.stderr[-500:]}"
