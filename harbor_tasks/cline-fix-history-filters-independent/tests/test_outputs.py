"""
Task: cline-fix-history-filters-independent
Repo: cline/cline @ 9fc9785aa2ab3985ae5030330566499d26fb6192
PR:   8292

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path
import pytest

REPO = "/workspace/cline"
HISTORY_VIEW = f"{REPO}/webview-ui/src/components/history/HistoryView.tsx"
CLAUDE_MD = f"{REPO}/CLAUDE.md"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js inline script and return the result."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout,
        cwd=REPO,
    )


@pytest.fixture(scope="session", autouse=True)
def run_biome_format():
    """Run biome format to fix any formatting issues before tests."""
    subprocess.run(
        ["npm", "ci"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    subprocess.run(
        ["npx", "biome", "format", "--write", "--no-errors-on-unmatched",
         "--files-ignore-unknown=true", HISTORY_VIEW],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax / compilation checks
# ---------------------------------------------------------------------------


def test_syntax_check():
    """pass_to_pass | HistoryView.tsx has valid JSX structure with balanced tags."""
    content = Path(HISTORY_VIEW).read_text()
    assert len(content) > 100, "File is unexpectedly empty or tiny"
    assert content.count("<VSCodeRadioGroup") == content.count(
        "</VSCodeRadioGroup>"
    ), "Unbalanced VSCodeRadioGroup tags"
    assert content.count("<VSCodeRadio") >= 5, "Should have multiple VSCodeRadio elements"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------


def test_filters_outside_radio_group():
    """fail_to_pass | Workspace and Favorites filters are outside VSCodeRadioGroup."""
    result = _run_node(
        """
const fs = require('fs');
const content = fs.readFileSync('%s', 'utf8');
const lines = content.split(/\\r?\\n/);

let radioGroupCloseLine = -1;
let workspaceLine = -1;
let favoritesLine = -1;

for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('</VSCodeRadioGroup>')) radioGroupCloseLine = i;
    if (lines[i].includes('showCurrentWorkspaceOnly')) workspaceLine = i;
    if (lines[i].includes('showFavoritesOnly')) favoritesLine = i;
}

if (radioGroupCloseLine < 0) {
    console.log('FAIL: no VSCodeRadioGroup close tag found');
    process.exit(1);
}
if (workspaceLine < 0) {
    console.log('FAIL: no Workspace filter found');
    process.exit(1);
}
if (favoritesLine < 0) {
    console.log('FAIL: no Favorites filter found');
    process.exit(1);
}
if (workspaceLine < radioGroupCloseLine) {
    console.log('FAIL: Workspace filter is inside VSCodeRadioGroup');
    process.exit(1);
}
if (favoritesLine < radioGroupCloseLine) {
    console.log('FAIL: Favorites filter is inside VSCodeRadioGroup');
    process.exit(1);
}
console.log('OK: both filters are outside VSCodeRadioGroup');
""" % HISTORY_VIEW
    )
    assert result.returncode == 0, f"Filter structure check failed: {result.stdout}"


def test_independent_filter_container():
    """fail_to_pass | Workspace and Favorites are in a separate flex div container."""
    result = _run_node(
        """
const fs = require('fs');
const content = fs.readFileSync('%s', 'utf8');
const lines = content.split(/\\r?\\n/);

let containerStart = -1;
for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('marginTop') && lines[i].includes('flex')) {
        containerStart = i;
        break;
    }
}

if (containerStart < 0) {
    console.log('FAIL: No independent container div found');
    process.exit(1);
}

const containerLine = lines[containerStart];
const marginMatch = containerLine.match(/marginTop:\s*(-?\d+)/);
if (!marginMatch) {
    console.log('FAIL: marginTop not found');
    process.exit(1);
}
const marginValue = parseInt(marginMatch[1], 10);
if (marginValue >= 0) {
    console.log('FAIL: marginTop should be negative, got ' + marginValue);
    process.exit(1);
}

let foundWorkspace = false;
let foundFavorites = false;
let closed = false;
for (let i = containerStart; i < lines.length && !closed; i++) {
    if (lines[i].includes('showCurrentWorkspaceOnly')) foundWorkspace = true;
    if (lines[i].includes('showFavoritesOnly')) foundFavorites = true;
    if (lines[i].trim() === '</div>' && foundWorkspace && foundFavorites) {
        closed = true;
    }
}

if (!foundWorkspace) {
    console.log('FAIL: Workspace filter not found');
    process.exit(1);
}
if (!foundFavorites) {
    console.log('FAIL: Favorites filter not found');
    process.exit(1);
}
console.log('OK: filters in flex container with negative margin');
""" % HISTORY_VIEW
    )
    assert result.returncode == 0, f"Container check failed: {result.stdout}"


def test_claude_md_documents_package_json():
    """fail_to_pass | CLAUDE.md documents checking package.json for available scripts."""
    content = Path(CLAUDE_MD).read_text()
    assert "package.json" in content
    assert "npm run compile" in content
    assert "Miscellaneous" in content


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - repo CI/CD checks
# ---------------------------------------------------------------------------


def test_repo_biome_lint():
    """pass_to_pass | Repo Biome linting passes on src/ and webview-ui/src/."""
    subprocess.run(["npm", "ci"], capture_output=True, text=True, timeout=180, cwd=REPO)
    r = subprocess.run(
        ["npx", "biome", "lint", "--no-errors-on-unmatched",
         "--files-ignore-unknown=true", "--diagnostic-level=error",
         "src/", "webview-ui/src/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Biome lint failed: {r.stderr[-500:]}"


def test_repo_biome_format():
    """pass_to_pass | Repo Biome format check passes on src/ and webview-ui/src/."""
    r = subprocess.run(
        ["npx", "biome", "format", "--no-errors-on-unmatched",
         "--files-ignore-unknown=true", "--diagnostic-level=error",
         "src/", "webview-ui/src/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Biome format check failed: {r.stderr[-500:]}"


def test_repo_protos():
    """pass_to_pass | Proto generation succeeds (npm run protos)."""
    r = subprocess.run(
        ["npm", "run", "protos"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Proto generation failed: {r.stderr[-500:]}"


def test_repo_compile_tests():
    """pass_to_pass | Test compilation succeeds (npm run compile-tests)."""
    r = subprocess.run(
        ["npm", "run", "compile-tests"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Test compilation failed: {r.stderr[-500:]}"


def test_repo_proto_lint():
    """pass_to_pass | Proto files linting passes (npm run lint:proto)."""
    r = subprocess.run(
        ["npm", "run", "lint:proto"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Proto lint failed: {r.stderr[-500:]}"


def test_repo_biome_format_full():
    """pass_to_pass | Biome format check on all source files passes."""
    r = subprocess.run(
        ["npx", "biome", "format", "--no-errors-on-unmatched",
         "--files-ignore-unknown=true", "--diagnostic-level=error"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Biome full format check failed: {r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Regression checks
# ---------------------------------------------------------------------------


def test_sort_options_in_radio_group():
    """pass_to_pass | Sort options (Newest, Oldest, Most Relevant) remain in VSCodeRadioGroup."""
    result = _run_node(
        """
const fs = require('fs');
const content = fs.readFileSync('%s', 'utf8');
const lines = content.split(/\\r?\\n/);

let openLine = -1, closeLine = -1;
let newestLine = -1, oldestLine = -1, relevantLine = -1;

for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('<VSCodeRadioGroup')) openLine = i;
    if (lines[i].includes('</VSCodeRadioGroup>')) closeLine = i;
    if (lines[i].includes('Newest')) newestLine = i;
    if (lines[i].includes('Oldest')) oldestLine = i;
    if (lines[i].includes('Most Relevant')) relevantLine = i;
}

if (openLine < 0 || closeLine < 0) {
    console.log('FAIL: VSCodeRadioGroup tags not found');
    process.exit(1);
}
if (newestLine < openLine || newestLine > closeLine) {
    console.log('FAIL: Newest not inside VSCodeRadioGroup');
    process.exit(1);
}
if (oldestLine < openLine || oldestLine > closeLine) {
    console.log('FAIL: Oldest not inside VSCodeRadioGroup');
    process.exit(1);
}
if (relevantLine < openLine || relevantLine > closeLine) {
    console.log('FAIL: Most Relevant not inside VSCodeRadioGroup');
    process.exit(1);
}
console.log('OK: all sort options in VSCodeRadioGroup');
""" % HISTORY_VIEW
    )
    assert result.returncode == 0, f"Sort options check failed: {result.stdout}"
