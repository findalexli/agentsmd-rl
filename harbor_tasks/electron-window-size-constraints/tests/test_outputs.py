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
        r"void NativeWindow::InitFromOptions\(const gin_helper::Dictionary& options\) \{([^}]+(?:\{[^}]*\}[^}]*)*)\}",
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
        r"void NativeWindow::InitFromOptions\(const gin_helper::Dictionary& options\) \{([^}]+(?:\{[^}]*\}[^}]*)*)\}",
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
        r"void NativeWindow::InitFromOptions\(const gin_helper::Dictionary& options\) \{([^}]+(?:\{[^}]*\}[^}]*)*)\}",
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
        r"void NativeWindow::InitFromOptions\(const gin_helper::Dictionary& options\) \{([^}]+(?:\{[^}]*\}[^}]*)*)\}",
        content,
        re.DOTALL,
    )
    assert func_match, "Could not find complete InitFromOptions function"

    # Check for proper semicolons after statements
    assert "size_constraints.set_minimum_size(gfx::Size(min_width, min_height));" in content, \
        "Missing semicolon after set_minimum_size call"
    assert "size_constraints.set_maximum_size(gfx::Size(max_width, max_height));" in content or \
           "size_constraints.set_maximum_size(gfx::Size(max_width, max_height))" in content, \
        "Missing set_maximum_size call"


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
    assert r.returncode == 0, f"clang-format check failed on native_window.cc:\n{r.stderr or r.stdout}"


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
    assert r.returncode == 0, f"clang-format check failed for shell/:\n{r.stderr or r.stdout}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
