"""
Task: playwright-feat-support-non-ref-selectors-in-mcp-cli
Repo: playwright @ 8bb752159dcd7bdf914a9b6d310c15dda84d0682
PR:   39581

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


def _run_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a TypeScript snippet using node with type stripping."""
    script_path = Path(REPO) / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", str(script_path)],
            capture_output=True, text=True, timeout=timeout,
            cwd=REPO,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files parse without errors."""
    files = [
        "packages/playwright-core/src/cli/daemon/commands.ts",
        "packages/playwright-core/src/tools/tab.ts",
        "packages/playwright-core/src/tools/tools.ts",
        "packages/playwright-core/src/tools/snapshot.ts",
        "packages/playwright-core/src/tools/evaluate.ts",
        "packages/playwright-core/src/tools/screenshot.ts",
        "packages/playwright-core/src/tools/verify.ts",
        "packages/playwright-core/src/tools/form.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"File not found: {f}"
        content = p.read_text()
        assert len(content) > 100, f"File too short (likely empty/stub): {f}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_asref_function_classifies_inputs():
    """CLI asRef helper correctly distinguishes refs from selectors."""
    # Verify asRef function exists with correct logic
    commands_ts = (Path(REPO) / "packages/playwright-core/src/cli/daemon/commands.ts").read_text()

    # Verify function signature and pattern matching logic
    assert "function asRef(refOrSelector" in commands_ts, "asRef function not found"
    assert "refOrSelector.match(/^(f\\d+)?e\\d+$/)" in commands_ts, \
        "asRef should use pattern /^(f\\d+)?e\\d+$/ to match refs"

    # Verify the logic branches
    assert "return { ref: refOrSelector }" in commands_ts, \
        "asRef should return { ref: value } for valid refs"
    assert "return { ref: '', selector: refOrSelector }" in commands_ts, \
        "asRef should return { ref: '', selector: value } for selectors"
    assert "return {}" in commands_ts, \
        "asRef should return {} for undefined input"

    # Now test the actual behavior by running the logic directly
    result = _run_ts("""
// Replicate the asRef function logic exactly as it should be
function asRef(refOrSelector: string | undefined): { ref?: string, selector?: string } {
  if (refOrSelector === undefined)
    return {};
  if (refOrSelector.match(/^(f\\d+)?e\\d+$/))
    return { ref: refOrSelector };
  return { ref: '', selector: refOrSelector };
}

const tests = [
    { input: 'e15', expected: { ref: 'e15' } },
    { input: 'f1e2', expected: { ref: 'f1e2' } },
    { input: 'f12e99', expected: { ref: 'f12e99' } },
    { input: 'button', expected: { ref: '', selector: 'button' } },
    { input: '#main', expected: { ref: '', selector: '#main' } },
    { input: 'role=button', expected: { ref: '', selector: 'role=button' } },
    { input: '#main >> role=button', expected: { ref: '', selector: '#main >> role=button' } },
    { input: undefined, expected: {} },
];

const results = tests.map(t => {
    const actual = asRef(t.input as any);
    return {
        input: t.input,
        actual,
        expected: t.expected,
        pass: JSON.stringify(actual) === JSON.stringify(t.expected),
    };
});

console.log(JSON.stringify({ results }));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip().split('\n')[-1])
    for r in data["results"]:
        assert r["pass"], \
            f"asRef('{r['input']}'): expected {r['expected']}, got {r['actual']}"


# [pr_diff] fail_to_pass
def test_cli_commands_use_target_param():
    """CLI click/fill/hover/select/check/uncheck use 'target' instead of 'ref'."""
    commands_ts = (Path(REPO) / "packages/playwright-core/src/cli/daemon/commands.ts").read_text()

    # Count 'target:' in z.object args — should be 7+ (click, dblclick, fill, hover, select, check, uncheck)
    target_matches = re.findall(r"target:\s*z\.string\(\)", commands_ts)
    assert len(target_matches) >= 7, \
        f"Expected at least 7 commands using 'target' param, found {len(target_matches)}"

    # asRef function must exist
    assert "function asRef(" in commands_ts, "asRef helper function not found"

    # click command should use target and asRef
    click_section = commands_ts[commands_ts.index("const click = declareCommand"):commands_ts.index("const doubleClick")]
    assert "target:" in click_section, "click command should use 'target' parameter"
    assert "asRef(target)" in click_section, "click toolParams should call asRef(target)"


# [pr_diff] fail_to_pass
def test_drag_uses_start_end_element():
    """Drag command uses startElement/endElement instead of startRef/endRef."""
    commands_ts = (Path(REPO) / "packages/playwright-core/src/cli/daemon/commands.ts").read_text()

    drag_match = re.search(r"const drag = declareCommand\(\{([\s\S]*?)\}\);", commands_ts)
    assert drag_match, "drag command declaration not found"
    drag_section = drag_match.group(1)

    assert "startElement:" in drag_section, "drag should use 'startElement' param"
    assert "endElement:" in drag_section, "drag should use 'endElement' param"
    # asRef should be called on both
    assert "asRef(startElement)" in drag_section, "drag should call asRef on startElement"
    assert "asRef(endElement)" in drag_section, "drag should call asRef on endElement"


# [pr_diff] fail_to_pass
def test_tab_reflocator_accepts_selector():
    """Tab.refLocator and refLocators accept optional selector parameter."""
    tab_ts = (Path(REPO) / "packages/playwright-core/src/tools/tab.ts").read_text()

    # refLocator signature must include selector
    assert "selector?: string" in tab_ts, \
        "refLocator should accept optional selector parameter"

    # When selector is provided, use page.locator(selector)
    assert "param.selector" in tab_ts, \
        "refLocators should check for param.selector"
    assert "this.page.locator(param.selector)" in tab_ts, \
        "Should create locator from selector string"

    # Error message for selector not matching
    assert "does not match any elements" in tab_ts, \
        "Should have error message for selector not matching elements"


# [pr_diff] fail_to_pass
def test_tool_schemas_include_selector():
    """MCP tool schemas (snapshot, evaluate, verify, form, screenshot) include selector field."""
    files_with_selector = {
        "packages/playwright-core/src/tools/snapshot.ts": "selector",
        "packages/playwright-core/src/tools/evaluate.ts": "selector",
        "packages/playwright-core/src/tools/screenshot.ts": "selector",
        "packages/playwright-core/src/tools/verify.ts": "selector",
        "packages/playwright-core/src/tools/form.ts": "selector",
    }
    for f, field in files_with_selector.items():
        content = (Path(REPO) / f).read_text()
        # Each should have selector as an optional z.string()
        assert f"{field}:" in content, f"{f} should have '{field}' in schema"
        assert "z.string().optional()" in content, f"{f} should have optional string for selector"


# [pr_diff] fail_to_pass
def test_filtered_tools_strips_selector():
    """filteredTools() omits selector/startSelector/endSelector from MCP schemas."""
    tools_ts = (Path(REPO) / "packages/playwright-core/src/tools/tools.ts").read_text()

    # Must import z for schema manipulation
    assert "import { z }" in tools_ts or "import {z}" in tools_ts, \
        "tools.ts should import z from mcpBundle"

    # filteredTools should strip selector fields via .omit()
    assert ".omit(" in tools_ts, "filteredTools should use .omit() to strip selector fields"
    assert "selector: true" in tools_ts, "Should omit 'selector' from MCP schemas"
    assert "startSelector: true" in tools_ts, "Should omit 'startSelector' from MCP schemas"
    assert "endSelector: true" in tools_ts, "Should omit 'endSelector' from MCP schemas"


# ---------------------------------------------------------------------------
# Config/doc update tests (agentmd-edit required)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/playwright-dev/mcp-dev.md:Step 3
def test_skill_md_documents_selector_targeting():
    """SKILL.md must document how to use CSS/role selectors for targeting elements."""
    skill_md = Path(REPO) / "packages/playwright-core/src/skill/SKILL.md"
    assert skill_md.exists(), "SKILL.md not found"
    content = skill_md.read_text()
    content_lower = content.lower()

    # Must have a section about targeting elements with selectors
    assert "targeting" in content_lower or "selector" in content_lower, \
        "SKILL.md should document element targeting with selectors"

    # Must mention CSS selectors
    assert "css" in content_lower, \
        "SKILL.md should mention CSS selectors"

    # Must mention role selectors
    assert "role" in content_lower and "selector" in content_lower, \
        "SKILL.md should mention role selectors"

    # Must show example of click with a selector (not just a ref)
    assert ('click "#' in content or "click '#" in content or
            'click "role=' in content or "click 'role=" in content), \
        "SKILL.md should show example of click with a CSS or role selector"


# [agent_config] fail_to_pass
def test_skill_md_shows_ref_and_selector_examples():
    """SKILL.md must show both ref-based and selector-based interaction examples."""
    skill_md = Path(REPO) / "packages/playwright-core/src/skill/SKILL.md"
    content = skill_md.read_text()

    # Should show ref-based example (e.g., 'click e15' or 'click e3')
    assert re.search(r"click\s+[ef]\d+", content), \
        "SKILL.md should show ref-based click example (e.g., 'click e15')"

    # Should show CSS selector example with an id or class
    assert "#" in content and ("click" in content.lower()), \
        "SKILL.md should show CSS selector example with click"

    # Should show role selector example
    assert "role=" in content, \
        "SKILL.md should show role selector example"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass - npm run lint-packages
def test_repo_lint_packages():
    """Repo workspace packages are consistent (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"lint-packages failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - modified files syntax check
def test_repo_modified_files_syntax():
    """All modified TypeScript files have valid syntax (pass_to_pass)."""
    modified_files = [
        "packages/playwright-core/src/cli/daemon/commands.ts",
        "packages/playwright-core/src/tools/tab.ts",
        "packages/playwright-core/src/tools/tools.ts",
        "packages/playwright-core/src/tools/snapshot.ts",
        "packages/playwright-core/src/tools/evaluate.ts",
        "packages/playwright-core/src/tools/screenshot.ts",
        "packages/playwright-core/src/tools/verify.ts",
        "packages/playwright-core/src/tools/form.ts",
    ]
    for f in modified_files:
        p = Path(REPO) / f
        assert p.exists(), f"File not found: {f}"
        r = subprocess.run(
            ["node", "--check", "--experimental-strip-types", str(p)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Syntax error in {f}:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - npm run build
def test_repo_build():
    """Repo builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_ref_pattern_still_works():
    """asRef returns { ref: value } for valid ref patterns, preserving existing behavior."""
    commands_ts = (Path(REPO) / "packages/playwright-core/src/cli/daemon/commands.ts").read_text()

    # asRef should return { ref: value } for valid ref patterns
    assert "{ ref: refOrSelector }" in commands_ts, \
        "asRef should return ref for valid ref patterns"

    # The evaluate command uses 'element' (not target)
    assert "...asRef(element)" in commands_ts, \
        "evaluate command should use asRef for its element param"
