"""
Tests for TanStack Router PR #6915: Fix backslash escaping in markdown sanitization.

The sanitizeMarkdown function in scripts/llms-generate.mjs was missing backslash
escaping, which could cause issues when markdown content contains backslashes
that need to be escaped for template literal interpolation.
"""

import subprocess
import os
import tempfile

REPO = "/workspace/router"


def run_node_code(code: str) -> subprocess.CompletedProcess:
    """Run Node.js code and return the result."""
    result = subprocess.run(
        ["node", "-e", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    return result


def get_sanitize_markdown_output(input_str: str) -> str:
    """
    Import and call the sanitizeMarkdown function with the given input.
    Returns the sanitized output string.
    """
    # Escape the input for use in JavaScript string
    escaped_input = input_str.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$").replace("\n", "\\n")

    code = f'''
const fs = require('fs');
const path = require('path');

// Read the script file
const scriptPath = path.join(process.cwd(), 'scripts/llms-generate.mjs');
const scriptContent = fs.readFileSync(scriptPath, 'utf-8');

// Extract the sanitizeMarkdown function using regex
const functionMatch = scriptContent.match(/function sanitizeMarkdown\\(markdownContent\\)\\s*\\{{([^}}]+)\\}}/s);
if (!functionMatch) {{
    console.error('Could not find sanitizeMarkdown function');
    process.exit(1);
}}

// Create and execute the function
const functionBody = functionMatch[1];
const sanitizeMarkdown = new Function('markdownContent', functionBody);

// Test with input
const input = `{escaped_input}`;
const result = sanitizeMarkdown(input);
console.log(result);
'''
    result = run_node_code(code)
    if result.returncode != 0:
        raise RuntimeError(f"Node.js execution failed: {result.stderr}")
    return result.stdout.strip()


# ============================================================================
# FAIL-TO-PASS TESTS: These should fail before the fix and pass after
# ============================================================================

def test_backslash_escaping_basic():
    """
    Test that a single backslash in markdown is properly escaped to double backslash.

    The sanitizeMarkdown function is used to prepare markdown content for use in
    JavaScript template literals. Backslashes must be escaped to prevent them from
    being interpreted as escape sequences.

    Input: "Hello\\nWorld" (literal backslash + n, not newline)
    Expected: "Hello\\\\nWorld" (backslash escaped)
    """
    # Test with a literal backslash-n (not a newline character)
    input_str = "Hello\\nWorld"
    output = get_sanitize_markdown_output(input_str)

    # After proper escaping, the backslash should be doubled
    # The output should contain \\ before the n
    assert "\\\\" in output or output.count("\\") >= 2, \
        f"Backslash not properly escaped. Input: {repr(input_str)}, Output: {repr(output)}"


def test_backslash_escaping_multiple():
    """
    Test that multiple backslashes are all properly escaped.

    Input: "path\\to\\file"
    Expected: "path\\\\to\\\\file"
    """
    input_str = "path\\to\\file"
    output = get_sanitize_markdown_output(input_str)

    # Count the backslashes - should be doubled
    input_backslash_count = input_str.count("\\")
    output_backslash_count = output.count("\\")

    assert output_backslash_count >= input_backslash_count * 2, \
        f"Not all backslashes were escaped. Input had {input_backslash_count}, output has {output_backslash_count}. Output: {repr(output)}"


def test_backslash_escaping_windows_path():
    """
    Test Windows-style file paths are properly escaped.

    Input: "C:\\Users\\name\\Documents"
    Expected: "C:\\\\Users\\\\name\\\\Documents"
    """
    input_str = "C:\\Users\\name\\Documents"
    output = get_sanitize_markdown_output(input_str)

    # Should have 6 backslashes (3 original * 2)
    assert output.count("\\") >= 6, \
        f"Windows path backslashes not properly escaped. Output: {repr(output)}"


def test_backslash_escaping_latex():
    """
    Test LaTeX-style content with backslashes.

    Input: "\\frac{a}{b}"
    Expected: "\\\\frac{a}{b}"
    """
    input_str = "\\frac{a}{b}"
    output = get_sanitize_markdown_output(input_str)

    # The leading backslash should be escaped
    assert output.startswith("\\\\") or "\\\\" in output, \
        f"LaTeX backslash not properly escaped. Output: {repr(output)}"


# ============================================================================
# PASS-TO-PASS TESTS: These should pass both before and after the fix
# ============================================================================

def test_backtick_escaping():
    """
    Test that backticks are properly escaped for template literals.
    (pass_to_pass - this worked before and should still work)
    """
    input_str = "Use `code` here"
    output = get_sanitize_markdown_output(input_str)

    # Backticks should be escaped with backslash
    assert "\\`" in output, \
        f"Backticks not properly escaped. Output: {repr(output)}"


def test_template_variable_escaping():
    """
    Test that template literal variable syntax is escaped.
    (pass_to_pass - this worked before and should still work)
    """
    input_str = "Value is ${value}"
    output = get_sanitize_markdown_output(input_str)

    # ${} should be escaped
    assert "\\${" in output, \
        f"Template variable syntax not escaped. Output: {repr(output)}"


def test_plain_text_unchanged():
    """
    Test that plain text without special characters passes through.
    (pass_to_pass)
    """
    input_str = "Hello World"
    output = get_sanitize_markdown_output(input_str)

    assert output == input_str, \
        f"Plain text was modified. Expected: {repr(input_str)}, Got: {repr(output)}"


def test_backslash_with_template_sequences():
    """
    Test backslash and template sequence combination.
    (pass_to_pass - coincidentally passes on both due to escaping interaction)

    When backslash precedes a backtick, the backtick escaping adds another
    backslash, so the test happens to pass even without explicit backslash escaping.
    """
    input_str = "\\`code\\`"
    output = get_sanitize_markdown_output(input_str)

    # The output should have escaped backslashes
    assert "\\\\" in output, \
        f"Backslash before backtick not properly escaped. Output: {repr(output)}"


def test_script_file_exists():
    """
    Verify the target script file exists (pass_to_pass).
    """
    script_path = os.path.join(REPO, "scripts/llms-generate.mjs")
    assert os.path.exists(script_path), f"Script file not found at {script_path}"


def test_script_has_sanitize_function():
    """
    Verify the sanitizeMarkdown function exists in the script (pass_to_pass).
    """
    script_path = os.path.join(REPO, "scripts/llms-generate.mjs")
    with open(script_path, 'r') as f:
        content = f.read()

    assert "function sanitizeMarkdown" in content, \
        "sanitizeMarkdown function not found in script"


# ============================================================================
# REPO CI/CD PASS-TO-PASS TESTS: These run actual repo CI commands
# ============================================================================

def test_repo_node_syntax():
    """
    Node.js syntax check passes on the modified script file (pass_to_pass).

    This verifies the script has valid JavaScript/ESM syntax without needing
    to install dependencies. The same syntax is validated by Node.js when
    the script is executed in CI.
    """
    result = subprocess.run(
        ["node", "--check", "scripts/llms-generate.mjs"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, \
        f"Node syntax check failed:\nstdout: {result.stdout[-500:]}\nstderr: {result.stderr[-500:]}"


def test_repo_script_shebang():
    """
    Script has proper Node.js shebang (pass_to_pass).

    The script must start with #!/usr/bin/env node to be executable.
    This is enforced by the repo's script conventions.
    """
    script_path = os.path.join(REPO, "scripts/llms-generate.mjs")
    with open(script_path, 'r') as f:
        first_line = f.readline().strip()

    assert first_line == "#!/usr/bin/env node", \
        f"Script missing or incorrect shebang. Got: {repr(first_line)}"


def test_repo_script_exports_valid_js():
    """
    Script can be parsed as a module and functions are valid (pass_to_pass).

    This uses Node's ability to parse and check the AST of the module
    without executing it.
    """
    # Use node to parse the script and verify it's valid ESM
    code = '''
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const scriptPath = path.join(process.cwd(), "scripts/llms-generate.mjs");
const content = fs.readFileSync(scriptPath, "utf-8");

// Check that the script parses as valid JavaScript
// We use vm.compileFunction to verify syntax without executing
try {
    // Just verify the content is valid JavaScript
    new Function(content.replace(/^#!.*\\n/, "").replace(/import\\s+.*from\\s+['"][^'"]+['"];?/g, "").replace(/export\\s+/g, ""));
    console.log("OK");
    process.exit(0);
} catch (e) {
    console.error("Parse error:", e.message);
    process.exit(1);
}
'''
    result = subprocess.run(
        ["node", "-e", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, \
        f"Script parse check failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
