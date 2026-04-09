"""
Task: wrangler-compat-date-format-snippet
Repo: workers-sdk @ 7d318e1b7e5af62c0ed09d3e5a51af84294c372e
PR:   13205

Tests verify that the compatibility_date warning in wrangler dev uses
format-aware snippet generation (e.g. formatConfigSnippet) to render
the correct format (TOML or JSON) based on the user's config file type,
instead of hardcoding TOML format.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/workers-sdk"
TARGET_FILE = f"{REPO}/packages/wrangler/src/api/startDevWorker/ConfigController.ts"


def _get_compat_date_function() -> str:
    """Extract the getDevCompatibilityDate function body from ConfigController.ts."""
    source = Path(TARGET_FILE).read_text()
    m = re.search(
        r"function getDevCompatibilityDate\b.*?(?=\n(?:export )?(?:class|function) )",
        source,
        re.DOTALL,
    )
    assert m, "getDevCompatibilityDate function not found in ConfigController.ts"
    return m.group(0)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_compat_date_warning_not_hardcoded_toml():
    """The compat date warning must not hardcode TOML format for the config snippet.
    On base, the template literal contains: file: compatibility_date = "<date>"
    which is TOML-only and incorrect for JSON config files."""
    func_body = _get_compat_date_function()
    # The base commit has this literal in the template string:
    #   file: compatibility_date = "${todaysDate}", or
    # Any correct fix removes this hardcoded TOML pattern and replaces it
    # with dynamic format-aware logic.
    assert 'file: compatibility_date = "' not in func_body, (
        'Compat date warning still hardcodes TOML format (compatibility_date = "..."). '
        "Should use formatConfigSnippet or equivalent to support JSON configs."
    )


# [pr_diff] fail_to_pass
def test_compat_date_format_dynamic():
    """The compat date warning must use a format-aware mechanism that produces
    the correct snippet format (TOML vs JSON) based on the config file type.
    Runs a Node.js script to analyze the function body."""
    r = subprocess.run(
        [
            "node",
            "-e",
            """
const fs = require('fs');
const source = fs.readFileSync(process.argv[1], 'utf8');

// Extract getDevCompatibilityDate function
const funcMatch = source.match(
    /function getDevCompatibilityDate\\b[\\s\\S]*?(?=\\n(?:export )?(?:class|function) )/
);
if (!funcMatch) {
    console.error('FAIL: getDevCompatibilityDate not found');
    process.exit(1);
}
const funcBody = funcMatch[0];

// The function must contain format-aware config snippet generation.
// Accept any of these valid approaches:
const formatAwarePatterns = [
    'formatConfigSnippet',
    'configFormat',
    'JSON.stringify',
    ".endsWith('.json')",
    '.endsWith(".json")',
    ".endsWith('.jsonc')",
    '.endsWith(".jsonc")',
    "toml",
];

const found = formatAwarePatterns.filter(p => funcBody.includes(p));
if (found.length === 0) {
    console.error('FAIL: No format-aware config snippet generation found');
    console.error('The function must produce format-appropriate output (TOML vs JSON)');
    process.exit(1);
}

console.log('PASS: found format-aware patterns: ' + found.join(', '));
""",
            TARGET_FILE,
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Format not dynamic: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_config_controller_parseable():
    """ConfigController.ts must have valid structure and not be truncated."""
    r = subprocess.run(
        [
            "node",
            "-e",
            """
const fs = require('fs');
const source = fs.readFileSync(process.argv[1], 'utf8');

if (source.length < 1000) {
    console.error('FAIL: File appears truncated');
    process.exit(1);
}
if (!source.includes('class ConfigController')) {
    console.error('FAIL: ConfigController class not found');
    process.exit(1);
}
if (!source.includes('getDevCompatibilityDate')) {
    console.error('FAIL: getDevCompatibilityDate function not found');
    process.exit(1);
}
// Check for unclosed template literals
const backtickCount = (source.match(/`/g) || []).length;
if (backtickCount % 2 !== 0) {
    console.error('FAIL: Odd number of backticks - likely unclosed template literal');
    process.exit(1);
}
console.log('PASS');
""",
            TARGET_FILE,
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Parse check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — convention checks
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — packages/wrangler/AGENTS.md:25 @ 7d318e1b7e5af62c0ed09d3e5a51af84294c372e
def test_uses_logger_not_console():
    """ConfigController must use logger singleton, not console.* for warnings.
    Rule: 'No console.* - use logger singleton' (packages/wrangler/AGENTS.md)."""
    func_body = _get_compat_date_function()
    assert "console.warn" not in func_body, (
        "getDevCompatibilityDate uses console.warn - must use logger.warn per wrangler AGENTS.md"
    )
    assert "console.log" not in func_body, (
        "getDevCompatibilityDate uses console.log - must use logger per wrangler AGENTS.md"
    )
    assert "logger.warn" in func_body, (
        "getDevCompatibilityDate should use logger.warn for the compat date warning"
    )
