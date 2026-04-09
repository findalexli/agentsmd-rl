"""
Task: cline-fix-history-filters-independent
Repo: cline/cline @ 9fc9785aa2ab3985ae5030330566499d26fb6192
PR:   8292

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/cline"
HISTORY_VIEW = f"{REPO}/webview-ui/src/components/history/HistoryView.tsx"
CLAUDE_MD = f"{REPO}/CLAUDE.md"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js inline script and return the result."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """HistoryView.tsx is readable and has valid JSX structure."""
    content = Path(HISTORY_VIEW).read_text()
    assert len(content) > 100, "File is unexpectedly empty or tiny"
    assert content.count("<VSCodeRadioGroup") == content.count(
        "</VSCodeRadioGroup>"
    ), "Unbalanced VSCodeRadioGroup tags"
    assert content.count("<VSCodeRadio") >= 5, "Should have multiple VSCodeRadio elements"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_filters_outside_radio_group():
    """Workspace and Favorites filters must be outside VSCodeRadioGroup.

    Before the fix, both were inside VSCodeRadioGroup, making them mutually
    exclusive with sort options (radio button behavior). After the fix, they
    appear after the closing </VSCodeRadioGroup> tag.
    """
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
// After fix: workspace and favorites lines must be AFTER radio group close
if (workspaceLine < radioGroupCloseLine) {
    console.log('FAIL: Workspace filter is inside VSCodeRadioGroup (line ' + workspaceLine + ' < close ' + radioGroupCloseLine + ')');
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


# [pr_diff] fail_to_pass
def test_independent_filter_container():
    """Workspace and Favorites must be in a separate div container.

    The fix wraps them in a flex div outside VSCodeRadioGroup, allowing
    independent toggling while maintaining visual continuity.
    """
    content = Path(HISTORY_VIEW).read_text()
    lines = content.splitlines()

    # Find the div with marginTop: -8 (the new container from the fix)
    container_start = -1
    for i, line in enumerate(lines):
        if "marginTop" in line and "flex" in line:
            container_start = i
            break

    assert container_start >= 0, (
        "No independent container div found for filters. "
        "Expected a div with flex styling and negative margin."
    )

    # Verify both filters exist after the container start
    found_workspace = False
    found_favorites = False
    for i in range(container_start, len(lines)):
        if "showCurrentWorkspaceOnly" in lines[i]:
            found_workspace = True
        if "showFavoritesOnly" in lines[i]:
            found_favorites = True
        # Stop at the closing </div> of this container
        if lines[i].strip() == "</div>" and found_workspace and found_favorites:
            break

    assert found_workspace, "Workspace filter not found in independent container"
    assert found_favorites, "Favorites filter not found in independent container"


# [pr_diff] fail_to_pass
def test_claude_md_documents_package_json():
    """CLAUDE.md must document checking package.json for available scripts.

    The PR adds a Miscellaneous section noting that package.json should be
    checked for available scripts (e.g., npm run compile, not npm run build).
    """
    content = Path(CLAUDE_MD).read_text()
    assert "package.json" in content, (
        "CLAUDE.md should mention package.json for discovering available scripts"
    )
    assert "npm run compile" in content, (
        "CLAUDE.md should give the example of npm run compile vs npm run build"
    )
    assert "Miscellaneous" in content, (
        "CLAUDE.md should have a Miscellaneous section for this tip"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD checks
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_biome_lint():
    """Repo's Biome linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "biome", "lint", "--no-errors-on-unmatched",
         "--files-ignore-unknown=true", "--diagnostic-level=error",
         "src/", "webview-ui/src/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Biome lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_biome_format():
    """Repo's Biome format check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "biome", "format", "--no-errors-on-unmatched",
         "--files-ignore-unknown=true", "--diagnostic-level=error",
         "src/", "webview-ui/src/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Biome format check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression checks
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_sort_options_in_radio_group():
    """Sort options (Newest, Oldest, Most Relevant) remain in VSCodeRadioGroup."""
    result = _run_node(
        """
const fs = require('fs');
const content = fs.readFileSync('%s', 'utf8');
const lines = content.split(/\\r?\\n/);

let radioGroupOpenLine = -1;
let radioGroupCloseLine = -1;
let newestLine = -1;
let oldestLine = -1;
let mostRelevantLine = -1;

for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('<VSCodeRadioGroup')) radioGroupOpenLine = i;
    if (lines[i].includes('</VSCodeRadioGroup>')) radioGroupCloseLine = i;
    if (lines[i].includes('Newest')) newestLine = i;
    if (lines[i].includes('Oldest')) oldestLine = i;
    if (lines[i].includes('Most Relevant')) mostRelevantLine = i;
}

if (radioGroupOpenLine < 0 || radioGroupCloseLine < 0) {
    console.log('FAIL: VSCodeRadioGroup tags not found');
    process.exit(1);
}
// All sort options must be between open and close tags
if (newestLine < radioGroupOpenLine || newestLine > radioGroupCloseLine) {
    console.log('FAIL: Newest not inside VSCodeRadioGroup');
    process.exit(1);
}
if (oldestLine < radioGroupOpenLine || oldestLine > radioGroupCloseLine) {
    console.log('FAIL: Oldest not inside VSCodeRadioGroup');
    process.exit(1);
}
if (mostRelevantLine < radioGroupOpenLine || mostRelevantLine > radioGroupCloseLine) {
    console.log('FAIL: Most Relevant not inside VSCodeRadioGroup');
    process.exit(1);
}
console.log('OK: all sort options are in VSCodeRadioGroup');
""" % HISTORY_VIEW
    )
    assert result.returncode == 0, f"Sort options check failed: {result.stdout}"
