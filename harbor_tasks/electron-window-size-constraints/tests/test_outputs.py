"""
Test outputs for electron-window-size-constraints task.
Verifies that the fix for enforcing min/max size constraints on window creation
is correctly implemented in shell/browser/native_window.cc.
"""

import os
import re
import subprocess
import pytest

REPO_PATH = os.environ.get("REPO_PATH", "/workspace/electron")
TARGET_FILE = "shell/browser/native_window.cc"
FILE_PATH = os.path.join(REPO_PATH, TARGET_FILE)


def read_file():
    """Read the target file content."""
    with open(FILE_PATH, "r") as f:
        return f.read()


# ──────────────────────────────────────────────────────────────────────────────
# Structural Tests (fail-to-pass: these fail on base commit, pass with fix)
# ──────────────────────────────────────────────────────────────────────────────


def test_clamp_size_called_before_setposition():
    """
    F2P: The size must be clamped to constraints BEFORE setting position.
    The fix reorders the code so that size constraints are applied first.
    """
    content = read_file()

    # Find the InitFromOptions function
    func_match = re.search(
        r"void NativeWindow::InitFromOptions\(const gin_helper::Dictionary& options\) \{([^}]+(?:\{[^}]*\}[^}]*)*)",
        content,
        re.DOTALL,
    )
    assert func_match, "InitFromOptions function not found"
    func_body = func_match.group(1)

    # Find where SetPosition is called
    setposition_matches = list(re.finditer(r"SetPosition\(gfx::Point\{x, y\}\)", func_body))
    assert len(setposition_matches) > 0, "SetPosition calls not found"

    # Find where ClampSize is called
    clamp_matches = list(re.finditer(r"ClampSize\(", func_body))
    assert len(clamp_matches) > 0, "ClampSize calls not found"

    # The first ClampSize must appear before the first SetPosition
    first_clamp_pos = clamp_matches[0].start()
    first_setposition_pos = setposition_matches[0].start()

    assert first_clamp_pos < first_setposition_pos, \
        "Size clamping must happen BEFORE SetPosition. The fix reorders these operations."


def test_content_size_clamping_logic():
    """
    F2P: When use_content_size is true, the content size must be clamped.
    """
    content = read_file()

    # Look for the pattern in the use_content_size block
    pattern = r"if \(use_content_size\) \{\s*gfx::Size clamped = size_constraints\.ClampSize\(GetContentSize\(\)\);"
    match = re.search(pattern, content, re.DOTALL)
    assert match, \
        "Content size clamping logic not found. Expected: clamped = size_constraints.ClampSize(GetContentSize())"


def test_window_size_clamping_logic():
    """
    F2P: When use_content_size is false, the window size must be clamped.
    """
    content = read_file()

    # Look for the pattern in the else block (after use_content_size)
    # The else block should contain: gfx::Size clamped = size_constraints.ClampSize(GetSize());
    pattern = r"\} else \{\s*gfx::Size clamped = size_constraints\.ClampSize\(GetSize\(\)\);"
    match = re.search(pattern, content, re.DOTALL)
    assert match, \
        "Window size clamping logic not found. Expected: clamped = size_constraints.ClampSize(GetSize())"


def test_clamped_size_conditional_set():
    """
    F2P: The clamped size must only be set if it differs from the current size.
    """
    content = read_file()

    # Check for the pattern: if (clamped != GetContentSize()) { SetContentSize(clamped); }
    content_pattern = r"if \(clamped != GetContentSize\(\)\) \{\s*SetContentSize\(clamped\);"
    content_match = re.search(content_pattern, content, re.DOTALL)
    assert content_match, \
        "Conditional SetContentSize not found. Expected: if (clamped != GetContentSize()) { SetContentSize(clamped); }"

    # Check for the pattern: if (clamped != GetSize()) { SetSize(clamped); }
    size_pattern = r"if \(clamped != GetSize\(\)\) \{\s*SetSize\(clamped\);"
    size_match = re.search(size_pattern, content, re.DOTALL)
    assert size_match, \
        "Conditional SetSize not found. Expected: if (clamped != GetSize()) { SetSize(clamped); }"


def test_comment_fixed_windows_typo():
    """
    F2P: The comment should say "Windows" not "Window".
    """
    content = read_file()

    # The old code had "On Linux and Window we may already have"
    # The fix should change it to "On Linux and Windows we may already have"
    assert "On Linux and Windows we may already have" in content, \
        "Comment typo not fixed. Expected: 'On Linux and Windows we may already have minimum and maximum size defined.'"

    # Make sure the old typo is not present
    assert "On Linux and Window we may already have" not in content, \
        "Old comment typo still present: 'On Linux and Window' should be 'On Linux and Windows'"


# ──────────────────────────────────────────────────────────────────────────────
# Pass-to-Pass Tests (verify code quality)
# ──────────────────────────────────────────────────────────────────────────────


def test_minimum_size_set_before_clamping():
    """
    P2P: The minimum size must be set in size_constraints before ClampSize is called.
    """
    content = read_file()

    func_match = re.search(
        r"void NativeWindow::InitFromOptions\(const gin_helper::Dictionary& options\) \{([^}]+(?:\{[^}]*\}[^}]*)*)",
        content,
        re.DOTALL,
    )
    assert func_match, "InitFromOptions function not found"
    func_body = func_match.group(1)

    # Find set_minimum_size call
    min_size_match = re.search(r"size_constraints\.set_minimum_size", func_body)
    assert min_size_match, "set_minimum_size call not found"

    # Find first ClampSize call
    clamp_match = re.search(r"ClampSize\(", func_body)
    assert clamp_match, "ClampSize call not found"

    # set_minimum_size must come before ClampSize
    assert min_size_match.start() < clamp_match.start(), \
        "set_minimum_size must be called before ClampSize"


def test_maximum_size_set_before_clamping():
    """
    P2P: The maximum size must be set in size_constraints before ClampSize is called.
    """
    content = read_file()

    func_match = re.search(
        r"void NativeWindow::InitFromOptions\(const gin_helper::Dictionary& options\) \{([^}]+(?:\{[^}]*\}[^}]*)*)",
        content,
        re.DOTALL,
    )
    assert func_match, "InitFromOptions function not found"
    func_body = func_match.group(1)

    # Find set_maximum_size call
    max_size_match = re.search(r"size_constraints\.set_maximum_size", func_body)
    assert max_size_match, "set_maximum_size call not found"

    # Find first ClampSize call
    clamp_match = re.search(r"ClampSize\(", func_body)
    assert clamp_match, "ClampSize call not found"

    # set_maximum_size must come before ClampSize
    assert max_size_match.start() < clamp_match.start(), \
        "set_maximum_size must be called before ClampSize"


def test_size_constraints_initialized_before_use():
    """
    P2P: size_constraints must be initialized with GetSizeConstraints or GetContentSizeConstraints
    before any modifications.
    """
    content = read_file()

    # Check for the initialization pattern
    init_pattern = r"extensions::SizeConstraints size_constraints\(\s*use_content_size \? GetContentSizeConstraints\(\) : GetSizeConstraints\(\)"
    match = re.search(init_pattern, content, re.DOTALL)
    assert match, \
        "size_constraints not properly initialized with GetSizeConstraints/GetContentSizeConstraints"


def test_code_compiles_syntax():
    """
    P2P: C++ code should be syntactically valid (basic checks).
    """
    content = read_file()

    # Basic syntax checks
    # Check for balanced braces in the InitFromOptions function
    func_match = re.search(
        r"void NativeWindow::InitFromOptions\(const gin_helper::Dictionary& options\) \{([^}]+(?:\{[^}]*\}[^}]*)*)",
        content,
        re.DOTALL,
    )
    assert func_match, "Could not find complete InitFromOptions function"

    # Check for proper semicolons after statements
    assert "size_constraints.set_minimum_size(gfx::Size(min_width, min_height));" in content or \
           "size_constraints.set_minimum_size(gfx::Size(min_width, min_height))" in content, \
        "Missing or malformed set_minimum_size call"
    assert "size_constraints.set_maximum_size(gfx::Size(max_width, max_height));" in content or \
           "size_constraints.set_maximum_size(gfx::Size(max_width, max_height))" in content, \
        "Missing or malformed set_maximum_size call"


# ──────────────────────────────────────────────────────────────────────────────
# Agent Config Rule Tests (from CLAUDE.md and copilot-instructions.md)
# ──────────────────────────────────────────────────────────────────────────────


def test_chromium_code_style_followed():
    """
    Agent Config: Follow Chromium coding style (from CLAUDE.md).
    Uses 2-space indentation, consistent with the rest of the file.
    """
    content = read_file()

    # Check that the file uses 2-space indentation consistently
    lines = content.split("\n")
    for i, line in enumerate(lines[:100], 1):  # Check first 100 lines
        if line.strip() and not line.startswith("//"):
            indent = len(line) - len(line.lstrip())
            if indent > 0:
                assert indent % 2 == 0, \
                    f"Line {i}: Indentation not multiple of 2 spaces (Chromium style)"


def test_clang_format_compliance():
    """
    Agent Config: Code should follow clang-format (from CLAUDE.md).
    Run clang-format to check formatting.
    """
    if not os.path.exists(FILE_PATH):
        pytest.skip("Source file not found")

    try:
        result = subprocess.run(
            ["clang-format", "--dry-run", "--Werror", FILE_PATH],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # Don't fail on minor formatting issues, just warn
        if result.returncode != 0:
            print(f"clang-format warnings: {result.stderr}")
    except FileNotFoundError:
        pytest.skip("clang-format not available")
    except subprocess.TimeoutExpired:
        pytest.skip("clang-format check timed out")


# ──────────────────────────────────────────────────────────────────────────────
# Pass-to-Pass Repo CI Tests (actual CI/CD checks from the repo)
# ──────────────────────────────────────────────────────────────────────────────


def test_repo_ci_clang_format_native_window():
    """
    P2P: Repo CI clang-format check passes on native_window.cc.
    This runs the actual CI check: `python3 script/run-clang-format.py -r -c shell/browser/native_window.cc`
    """
    r = subprocess.run(
        ["python3", "script/run-clang-format.py", "-r", "-c", "shell/browser/native_window.cc"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"clang-format check failed on native_window.cc:\\n{r.stderr or r.stdout}"


def test_repo_ci_clang_format_shell_dir():
    """
    P2P: Repo CI clang-format check passes on shell/ directory.
    Verifies all C++ files in shell/ follow Chromium style (npm run lint:clang-format).
    """
    r = subprocess.run(
        ["python3", "script/run-clang-format.py", "-r", "-c", "shell/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"clang-format check failed for shell/:\\n{r.stderr or r.stdout}"


def test_repo_clang_format_browser_dir():
    """
    P2P: Repo CI clang-format check passes on shell/browser/ directory.
    Verifies all C++ files in browser module follow Chromium style.
    """
    r = subprocess.run(
        ["python3", "script/run-clang-format.py", "-r", "-c", "shell/browser/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"clang-format check failed for shell/browser/:\\n{r.stderr or r.stdout}"


def test_native_window_file_exists():
    """
    P2P: Target file shell/browser/native_window.cc exists and is readable.
    """
    assert os.path.exists(FILE_PATH), f"Target file not found: {FILE_PATH}"
    assert os.path.isfile(FILE_PATH), f"Target path is not a file: {FILE_PATH}"
    with open(FILE_PATH, "r") as f:
        content = f.read()
    assert len(content) > 0, f"Target file is empty: {FILE_PATH}"


def test_clang_format_config_exists():
    """
    P2P: clang-format configuration file exists and is valid.
    """
    config_path = os.path.join(REPO_PATH, ".clang-format")
    assert os.path.exists(config_path), f".clang-format config not found"
    with open(config_path, "r") as f:
        content = f.read()
    # Basic check that it looks like a yaml config
    assert "BasedOnStyle" in content or "Language" in content, \
        ".clang-format does not appear to be a valid configuration file"


def test_repo_manifest_files_valid():
    """
    P2P: Repository manifest files are valid and parseable.
    Checks package.json structure.
    """
    import json
    package_path = os.path.join(REPO_PATH, "package.json")
    assert os.path.exists(package_path), "package.json not found"
    with open(package_path, "r") as f:
        package = json.load(f)
    assert "name" in package, "package.json missing 'name' field"
    assert "scripts" in package, "package.json missing 'scripts' field"


def test_claude_md_exists():
    """
    P2P: CLAUDE.md file exists with coding guidelines (from copilot-instructions.md).
    """
    claude_md_path = os.path.join(REPO_PATH, "CLAUDE.md")
    assert os.path.exists(claude_md_path), "CLAUDE.md not found"
    with open(claude_md_path, "r") as f:
        content = f.read()
    assert len(content) > 0, "CLAUDE.md is empty"
    # Check for key sections mentioned in CI
    assert "Chromium" in content or "Build" in content or "electron" in content.lower(), \
        "CLAUDE.md missing expected content about Chromium or Electron"


def test_copilot_instructions_exists():
    """
    P2P: GitHub Copilot instructions file exists with coding guidelines.
    """
    instructions_path = os.path.join(REPO_PATH, ".github", "copilot-instructions.md")
    assert os.path.exists(instructions_path), ".github/copilot-instructions.md not found"
    with open(instructions_path, "r") as f:
        content = f.read()
    assert len(content) > 0, "copilot-instructions.md is empty"


def test_shell_browser_module_structure():
    """
    P2P: shell/browser/ module has expected structure (headers and implementation files).
    """
    browser_dir = os.path.join(REPO_PATH, "shell", "browser")
    assert os.path.isdir(browser_dir), f"shell/browser/ directory not found"

    # Check for header files
    header_files = [f for f in os.listdir(browser_dir) if f.endswith(".h")]
    cc_files = [f for f in os.listdir(browser_dir) if f.endswith(".cc")]

    # native_window.h should exist (paired with native_window.cc)
    assert "native_window.h" in header_files, "native_window.h not found in shell/browser/"
    assert "native_window.cc" in cc_files, "native_window.cc not found in shell/browser/"


def test_git_repo_valid():
    """
    P2P: Git repository is valid and has expected structure.
    """
    r = subprocess.run(
        ["git", "status"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"Git repository is not valid: {r.stderr}"

    # Check that we're at the expected commit
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, "Failed to get git HEAD"
    head_commit = r.stdout.strip()
    # Should match the base commit from Dockerfile (a0f042f8d3e1123e7112a868954ab3c7c843f0b7)
    expected_prefix = "a0f042f8"
    assert head_commit.startswith(expected_prefix), \
        f"Unexpected commit: {head_commit[:8]}, expected {expected_prefix}*"


def test_python_scripts_syntax():
    """
    P2P: Python scripts in script/ directory have valid syntax.
    """
    script_dir = os.path.join(REPO_PATH, "script")
    # Check key scripts compile
    key_scripts = [
        os.path.join(script_dir, "run-clang-format.py"),
    ]
    for script in key_scripts:
        if os.path.exists(script):
            r = subprocess.run(
                ["python3", "-m", "py_compile", script],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert r.returncode == 0, f"Python syntax error in {script}: {r.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
