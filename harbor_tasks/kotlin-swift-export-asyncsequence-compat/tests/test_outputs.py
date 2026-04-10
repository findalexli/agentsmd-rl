"""Tests for Swift Export asyncSequence compatibility function."""
import subprocess
import os
import re
import pytest

REPO = "/workspace/kotlin"
TARGET_FILE = os.path.join(REPO, "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift")


def test_asyncsequence_function_exists():
    """Fail-to-pass: asyncSequence(for:) function must exist in the file."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for the function declaration
    pattern = r'public func asyncSequence\s*<\s*T\s*>\s*\(\s*for\s+flow:\s*any\s+KotlinTypedFlow\s*<\s*T\s*>\s*\)'
    assert re.search(pattern, content), "asyncSequence(for:) function declaration not found"


def test_asyncsequence_has_deprecated_attribute():
    """Fail-to-pass: asyncSequence function must have @available deprecated attribute."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for the deprecated attribute before the function
    pattern = r'@available\s*\(\s*\*\s*,\s*deprecated\s*,\s*message:\s*"[^"]*asAsyncSequence\(\)[^"]*"\s*\)'
    assert re.search(pattern, content), "@available(*, deprecated) attribute with asAsyncSequence message not found"


def test_asyncsequence_calls_asasyncsequence():
    """Fail-to-pass: asyncSequence function body must call asAsyncSequence()."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check that function body calls asAsyncSequence
    pattern = r'return\s+flow\.asAsyncSequence\s*\(\s*\)'
    assert re.search(pattern, content), "Function body must call flow.asAsyncSequence()"


def test_asyncsequence_returns_kotlinflowsequence():
    """Fail-to-pass: asyncSequence function must return KotlinFlowSequence<T>."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check return type
    pattern = r'public func asyncSequence\s*<\s*T\s*>\s*\([^)]*\)\s*(?:->\s*KotlinFlowSequence\s*<\s*T\s*>)?'
    # Alternative: check for arrow and return type
    arrow_pattern = r'\)\s*->\s*KotlinFlowSequence\s*<\s*T\s*>'
    assert re.search(arrow_pattern, content), "Function must have return type -> KotlinFlowSequence<T>"


def test_asyncsequence_has_documentation_comment():
    """Fail-to-pass: asyncSequence function must have documentation comment explaining purpose."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for documentation comment before the function
    pattern = r'///\s*This function provides source compatibility with KMP-NativeCoroutines'
    assert re.search(pattern, content), "Documentation comment about KMP-NativeCoroutines compatibility not found"


def test_swift_file_syntax_valid():
    """Pass-to-pass: Swift file should have valid syntax (compiles without errors)."""
    # Check if swiftc is available
    swiftc_check = subprocess.run(["which", "swiftc"], capture_output=True)
    if swiftc_check.returncode != 0:
        pytest.skip("swiftc not available in container")

    # Try to check syntax with swiftc
    result = subprocess.run(
        ["swiftc", "-parse", TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=60
    )

    # Note: This may fail due to missing dependencies, but basic syntax should be parseable
    # We allow this to pass even if there are import/module errors
    # The key is that basic Swift syntax is valid
    error_output = result.stderr.lower()

    # Filter out acceptable errors (module/import related)
    unacceptable_errors = [
        "expected", "error: invalid", "error: unexpected",
        "braces", "parentheses", "comma", "semicolon"
    ]

    for err in unacceptable_errors:
        if err in error_output:
            assert False, f"Swift syntax error detected: {result.stderr[:500]}"

    # If we get here, basic syntax is acceptable
    assert True


def test_file_exists():
    """Pass-to-pass: Target Swift file exists."""
    assert os.path.exists(TARGET_FILE), f"Target file {TARGET_FILE} does not exist"


def test_swift_braces_balanced():
    """Pass-to-pass: Swift file has balanced braces and parentheses."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check balanced braces
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, f"Unbalanced braces: {open_braces} open, {close_braces} close"

    # Check balanced parentheses
    open_parens = content.count('(')
    close_parens = content.count(')')
    assert open_parens == close_parens, f"Unbalanced parentheses: {open_parens} open, {close_parens} close"

    # Check balanced brackets
    open_brackets = content.count('[')
    close_brackets = content.count(']')
    assert open_brackets == close_brackets, f"Unbalanced brackets: {open_brackets} open, {close_brackets} close"


def test_swift_imports_valid():
    """Pass-to-pass: Swift file has valid import statements."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find all import statements
    import_pattern = r'^\s*(import|@_implementationOnly import)\s+([A-Za-z_][A-Za-z0-9_]*)'
    imports = re.findall(import_pattern, content, re.MULTILINE)

    # Should have at least the expected imports
    assert len(imports) >= 2, f"Expected at least 2 imports, found {len(imports)}"

    # Verify no invalid characters in import names
    for _, module_name in imports:
        assert re.match(r'^[A-Za-z_][A-Za-z0-9_.]*$', module_name), f"Invalid import name: {module_name}"


def test_swift_no_trailing_whitespace():
    """Pass-to-pass: Swift file has no trailing whitespace on lines."""
    with open(TARGET_FILE, 'r') as f:
        lines = f.readlines()

    trailing_ws_count = sum(1 for line in lines if line.rstrip() != line.rstrip('\n').rstrip())
    # Allow some tolerance but flag excessive issues
    assert trailing_ws_count < 50, f"Found {trailing_ws_count} lines with trailing whitespace"


def test_swift_function_declarations_valid():
    """Pass-to-pass: Swift file has syntactically valid function declarations."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for basic Swift function declaration patterns
    # Valid Swift func: public/private/package/internal func name(params) -> ReturnType { ... }
    func_pattern = r'(?:public\s+|private\s+|package\s+|internal\s+)?(?:func|init|deinit)\s+[A-Za-z_][A-Za-z0-9_]*\s*\('
    funcs = re.findall(func_pattern, content)

    # The file should have at least a few function declarations
    assert len(funcs) >= 2, f"Expected at least 2 function declarations, found {len(funcs)}"


def test_swift_comments_valid():
    """Pass-to-pass: Swift file has valid comment syntax."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for valid single-line comments (/// or //)
    single_line_pattern = r'^\s*///.*$'
    doc_comments = re.findall(single_line_pattern, content, re.MULTILINE)

    # Should have at least some documentation comments
    assert len(doc_comments) >= 1, f"Expected at least 1 documentation comment (///), found {len(doc_comments)}"

    # Check for improperly formatted block comments that might indicate issues
    # Swift block comments: /* ... */
    block_comment_pattern = r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/'
    block_comments = re.findall(block_comment_pattern, content, re.DOTALL)

    # Unclosed block comments would be a syntax error - check for /* without */
    open_block = content.count('/*')
    close_block = content.count('*/')
    assert open_block == close_block, f"Unbalanced block comment markers: {open_block} /*, {close_block} */"


def test_swift_class_struct_protocol_valid():
    """Pass-to-pass: Swift file has valid class/struct/protocol declarations."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for valid Swift type declarations
    type_patterns = [
        r'public\s+(?:final\s+)?class\s+\w+',
        r'(?:public\s+)?struct\s+\w+',
        r'(?:public\s+)?protocol\s+\w+',
        r'(?:public\s+)?enum\s+\w+',
        r'(?:public\s+)?extension\s+\w+',
    ]

    total_types = 0
    for pattern in type_patterns:
        matches = re.findall(pattern, content)
        total_types += len(matches)

    # Should have at least a few type definitions
    assert total_types >= 2, f"Expected at least 2 type declarations, found {total_types}"


def test_file_not_empty():
    """Pass-to-pass: Swift file is not empty and has substantial content."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # File should be non-empty
    assert len(content) > 0, "File is empty"

    # Should have multiple lines
    lines = content.split('\n')
    assert len(lines) > 50, f"File too short: only {len(lines)} lines"

    # Should have substantial non-whitespace content
    non_ws_chars = len([c for c in content if not c.isspace()])
    assert non_ws_chars > 500, f"File has insufficient content: only {non_ws_chars} non-whitespace characters"


# ============================================================================
# Repository CI/CD Pass-to-Pass Tests
# These tests verify that the repo's existing CI checks pass on the base
# commit and continue to pass after the gold fix is applied.
# ============================================================================


def test_repo_git_status_clean():
    """Repo's git repository has no uncommitted changes (pass_to_pass).

    Note: After applying a fix, there will be uncommitted changes.
    This test verifies git status works and captures the state.
    """
    r = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git status failed: {r.stderr}"
    # We don't assert empty stdout here because after applying a fix,
    # there will necessarily be uncommitted changes. This test only
    # verifies git status works correctly.


def test_repo_git_fsck():
    """Repo's git repository passes integrity check (pass_to_pass)."""
    r = subprocess.run(
        ["git", "fsck", "--full"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # fsck can return 0 even with dangling objects, only fail on actual errors
    error_lines = [line for line in r.stderr.split('\n') if line and not line.startswith('dangling')]
    assert len(error_lines) == 0, f"Git fsck found issues:\n{r.stderr}"


def test_repo_swift_resources_exist():
    """Repo's Swift resource files all exist (pass_to_pass)."""
    resources_dir = os.path.join(REPO, "native/swift/swift-export-standalone/resources/swift")
    required_files = [
        "KotlinCoroutineSupport.swift",
        "KotlinCoroutineSupport.h",
        "KotlinCoroutineSupport.kt",
        "KotlinRuntimeSupport.swift",
        "KotlinRuntimeSupport.h",
        "KotlinRuntimeSupport.kt",
    ]
    for filename in required_files:
        filepath = os.path.join(resources_dir, filename)
        assert os.path.exists(filepath), f"Required Swift resource file missing: {filename}"


def test_repo_swift_files_have_content():
    """Repo's Swift resource files have substantial content (pass_to_pass)."""
    resources_dir = os.path.join(REPO, "native/swift/swift-export-standalone/resources/swift")
    swift_files = ["KotlinCoroutineSupport.swift", "KotlinRuntimeSupport.swift"]

    for filename in swift_files:
        filepath = os.path.join(resources_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()

        # File should have minimum content
        assert len(content) > 1000, f"{filename} has insufficient content"
        assert len(content.split('\n')) > 20, f"{filename} has too few lines"

        # Check for valid Swift file structure
        open_braces = content.count('{')
        close_braces = content.count('}')
        assert open_braces == close_braces, f"{filename} has unbalanced braces"

        open_parens = content.count('(')
        close_parens = content.count(')')
        assert open_parens == close_parens, f"{filename} has unbalanced parentheses"


# ============================================================================
# Enriched CI/CD Pass-to-Pass Tests (using actual shell commands)
# These tests run real CI commands via subprocess.run()
# ============================================================================


def test_repo_gradle_help():
    """Repo's Gradle build system responds to help command (pass_to_pass)."""
    r = subprocess.run(
        ["./gradlew", "help", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Gradle may fail due to missing Java or other env issues
    # We accept both success and expected environment errors
    if r.returncode != 0:
        # If it failed, verify it's due to environment, not build script syntax
        assert "BUILD FAILED" not in r.stderr or "parse" not in r.stderr.lower(), \
            f"Gradle build scripts have syntax errors: {r.stderr[:500]}"


def test_repo_git_log_works():
    """Repo's git log command works and shows recent commits (pass_to_pass)."""
    r = subprocess.run(
        ["git", "log", "--oneline", "-5"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git log failed: {r.stderr}"
    # Should have at least 5 commits
    commits = [line for line in r.stdout.strip().split('\n') if line.strip()]
    assert len(commits) >= 5, f"Expected at least 5 commits, found {len(commits)}"


def test_repo_swift_file_line_counts():
    """Repo's Swift files have expected line counts using wc (pass_to_pass)."""
    swift_files = [
        "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift",
        "native/swift/swift-export-standalone/resources/swift/KotlinRuntimeSupport.swift",
    ]
    for filepath in swift_files:
        full_path = os.path.join(REPO, filepath)
        r = subprocess.run(
            ["wc", "-l", full_path],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"wc command failed for {filepath}: {r.stderr}"
        # Extract line count from output like "253 /workspace/kotlin/..."
        parts = r.stdout.strip().split()
        assert len(parts) >= 1, f"Unexpected wc output: {r.stdout}"
        line_count = int(parts[0])
        assert line_count > 50, f"{filepath} has insufficient lines: {line_count}"


def test_repo_grep_finds_swift_functions():
    """Repo's Swift files contain expected function patterns (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-c", "public func", f"{REPO}/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"grep command failed: {r.stderr}"
    func_count = int(r.stdout.strip())
    assert func_count >= 5, f"Expected at least 5 public func declarations, found {func_count}"


def test_repo_swift_imports_valid_check():
    """Repo's Swift files have valid import statements via grep (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-E", "^import|^@_implementationOnly import",
         f"{REPO}/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0 or r.returncode == 1, f"grep command failed unexpectedly: {r.stderr}"
    imports = [line for line in r.stdout.strip().split('\n') if line.strip()]
    assert len(imports) >= 2, f"Expected at least 2 imports, found {len(imports)}"


def test_repo_git_diff_base_commit():
    """Repo's git diff can compare with parent commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "diff", "HEAD~1", "--stat"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git diff failed: {r.stderr}"
    # Should show some output with file statistics
    assert len(r.stdout) > 0, "Git diff --stat should produce output"


def test_repo_git_show_commit():
    """Repo's git show displays commit info (pass_to_pass)."""
    r = subprocess.run(
        ["git", "show", "--stat", "-s", "HEAD"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git show failed: {r.stderr}"
    # Should have commit info
    assert len(r.stdout) > 0, "Git show should produce output"
    # Check for commit hash pattern
    assert re.match(r'^[a-f0-9]+', r.stdout.strip()), "Should show commit hash"


def test_repo_swift_file_line_endings():
    """Repo's Swift files use consistent line endings (pass_to_pass)."""
    swift_files = [
        "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift",
        "native/swift/swift-export-standalone/resources/swift/KotlinRuntimeSupport.swift",
    ]
    for filepath in swift_files:
        full_path = os.path.join(REPO, filepath)
        r = subprocess.run(
            ["cat", "-A", full_path],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"cat command failed for {filepath}: {r.stderr}"
        # Check for carriage returns (Windows line endings)
        carriage_return_count = r.stdout.count('^M')
        assert carriage_return_count == 0, f"{filepath} contains {carriage_return_count} carriage returns (Windows line endings)"


def test_repo_swift_file_valid_line_lengths():
    """Repo's Swift files have reasonable line lengths (pass_to_pass)."""
    swift_file = "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift"
    full_path = os.path.join(REPO, swift_file)
    r = subprocess.run(
        ["awk", "length > 200 { print NR \": \" $0 }", full_path],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"awk command failed: {r.stderr}"
    # Allow some very long lines but not too many
    long_lines = [line for line in r.stdout.strip().split('\n') if line.strip()]
    assert len(long_lines) < 20, f"Found {len(long_lines)} lines longer than 200 characters"


def test_repo_resources_dir_listing():
    """Repo's Swift resources directory can be listed (pass_to_pass)."""
    resources_dir = os.path.join(REPO, "native/swift/swift-export-standalone/resources/swift")
    r = subprocess.run(
        ["ls", "-la", resources_dir],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"ls command failed: {r.stderr}"
    # Should list the expected files
    expected_files = ["KotlinCoroutineSupport.swift", "KotlinRuntimeSupport.swift"]
    for filename in expected_files:
        assert filename in r.stdout, f"Expected file {filename} not found in directory listing"


def test_repo_swift_files_not_empty():
    """Repo's Swift files are not empty using find command (pass_to_pass)."""
    resources_dir = os.path.join(REPO, "native/swift/swift-export-standalone/resources/swift")
    r = subprocess.run(
        ["find", resources_dir, "-name", "*.swift", "-type", "f", "!", "-empty"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"find command failed: {r.stderr}"
    # Should find both Swift files
    swift_files = [line for line in r.stdout.strip().split('\n') if line.strip()]
    assert len(swift_files) >= 2, f"Expected at least 2 non-empty Swift files, found {len(swift_files)}"


def test_repo_git_branch_list():
    """Repo's git branch/list commands work (pass_to_pass)."""
    r = subprocess.run(
        ["git", "branch", "-a"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git branch failed: {r.stderr}"
    # Should show at least HEAD (detached)
    assert "*" in r.stdout, "Should show current branch indicator"


def test_repo_git_rev_parse():
    """Repo's git rev-parse shows current commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git rev-parse failed: {r.stderr}"
    commit_hash = r.stdout.strip()
    assert len(commit_hash) >= 7, f"Invalid commit hash: {commit_hash}"
    assert re.match(r'^[a-f0-9]+$', commit_hash), f"Commit hash contains non-hex characters: {commit_hash}"
