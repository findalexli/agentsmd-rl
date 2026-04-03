"""
Task: playwright-feat-support-nonref-selectors-in
Repo: microsoft/playwright @ 8bb752159dcd7bdf914a9b6d310c15dda84d0682
PR:   39581

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
COMMANDS_TS = Path(REPO) / "packages/playwright-core/src/cli/daemon/commands.ts"
TAB_TS = Path(REPO) / "packages/playwright-core/src/tools/tab.ts"
TOOLS_TS = Path(REPO) / "packages/playwright-core/src/tools/tools.ts"
SNAPSHOT_TS = Path(REPO) / "packages/playwright-core/src/tools/snapshot.ts"
SKILL_MD = Path(REPO) / "packages/playwright-core/src/skill/SKILL.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_commands_structure():
    """commands.ts retains core CLI command structure."""
    src = COMMANDS_TS.read_text()
    assert "declareCommand" in src, "commands.ts must use declareCommand"
    assert "browser_click" in src, "click command must map to browser_click tool"
    assert "browser_hover" in src, "hover command must map to browser_hover tool"
    assert "browser_type" in src, "fill command must map to browser_type tool"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_asref_classification():
    """Ref/selector classification logic correctly distinguishes element refs from CSS/role selectors.

    Element refs match the pattern ^(f\\d+)?e\\d+$ (e.g. e5, f1e2, f99e100).
    Everything else (CSS selectors, role selectors) should be classified as a selector.
    """
    src = COMMANDS_TS.read_text()

    # Must have a function or logic that uses the ref-detection regex
    assert re.search(r'\(f\\d\+\)\?e\\d\+', src), \
        "commands.ts must contain the ref-detection regex pattern /^(f\\d+)?e\\d+$/"

    # Extract the ref-classification function (could be named anything)
    # Look for a function that takes a string, returns ref/selector
    match = re.search(
        r'(function\s+\w+\([^)]*\)[^{]*\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\})',
        src
    )
    # Find the function containing the ref regex
    func_match = None
    for m in re.finditer(
        r'(function\s+(\w+)\([^)]*\)[^{]*\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\})',
        src
    ):
        if r'(f\d+)?e\d+' in m.group(0):
            func_match = m
            break

    assert func_match, "Must have a function containing the ref-detection regex"
    func_name = func_match.group(2)
    func_body = func_match.group(1)

    # Strip TypeScript type annotations to make it valid JS
    func_js = re.sub(r':\s*string\s*\|\s*undefined', '', func_body)
    func_js = re.sub(r'\)\s*:\s*\{[^}]*\}', ')', func_js)

    # Test it via Node.js with various inputs
    test_script = func_js + r"""
    const cases = [
        ['e5', true, false],
        ['e0', true, false],
        ['f1e2', true, false],
        ['f99e100', true, false],
        ['button', false, true],
        ['#main > .btn', false, true],
        ['role=button[name=Submit]', false, true],
        ['#footer >> role=button', false, true],
        ['.class-name', false, true],
        [undefined, false, false],
    ];
    let failures = [];
    for (const [input, expectRef, expectSelector] of cases) {
        const result = """ + func_name + r"""(input);
        const hasRef = result.ref !== undefined && result.ref !== '';
        const hasSel = result.selector !== undefined && result.selector !== '';
        if (hasRef !== expectRef || hasSel !== expectSelector) {
            failures.push(
                `${func_name}(${JSON.stringify(input)}) = ${JSON.stringify(result)} ` +
                `(ref=${hasRef}, sel=${hasSel}), expected ref=${expectRef}, sel=${expectSelector}`
            );
        }
    }
    if (failures.length > 0) {
        console.error(failures.join('\n'));
        process.exit(1);
    }
    console.log('ALL_PASSED');
    """
    r = subprocess.run(
        ['node', '-e', test_script],
        capture_output=True, text=True, timeout=10
    )
    assert r.returncode == 0, f"Ref/selector classification failed:\n{r.stderr}\n{r.stdout}"
    assert 'ALL_PASSED' in r.stdout


# [pr_diff] fail_to_pass
def test_cli_commands_accept_target():
    """CLI commands (click, fill, hover, check, uncheck, select) must use 'target' parameter."""
    src = COMMANDS_TS.read_text()

    # Find all command blocks that interact with elements
    # These commands previously used 'ref' and should now use 'target'
    element_commands = ['click', 'fill', 'hover', 'select', 'check', 'uncheck']

    for cmd_name in element_commands:
        # Find the declareCommand block for this command
        # Look for: name: 'cmd_name', ... args: z.object({ target: ...
        pattern = rf"name:\s*'{cmd_name}'.*?args:\s*z\.object\(\{{(.*?)\}}\)"
        match = re.search(pattern, src, re.DOTALL)
        assert match, f"Could not find command definition for '{cmd_name}'"
        args_block = match.group(1)
        assert 'target' in args_block, \
            f"Command '{cmd_name}' must accept 'target' parameter (not 'ref')"


# [pr_diff] fail_to_pass
def test_selector_in_tool_schemas():
    """MCP tool schemas (elementSchema, verify tools) must include 'selector' field."""
    snapshot_src = SNAPSHOT_TS.read_text()

    # elementSchema must include selector
    schema_match = re.search(
        r'export const elementSchema\s*=\s*z\.object\(\{(.*?)\}\)',
        snapshot_src, re.DOTALL
    )
    assert schema_match, "elementSchema must exist in snapshot.ts"
    schema_body = schema_match.group(1)
    assert 'selector' in schema_body, \
        "elementSchema must include 'selector' field"

    # verify.ts must also pass selector to refLocator
    verify_src = Path(f"{REPO}/packages/playwright-core/src/tools/verify.ts").read_text()
    assert 'selector' in verify_src, \
        "verify.ts must include selector support"
    # Check that refLocator calls include selector
    assert re.search(r'refLocator\(\{[^}]*selector', verify_src), \
        "verify.ts refLocator calls must pass selector parameter"


# [pr_diff] fail_to_pass
def test_reflocator_handles_selector():
    """Tab.refLocator/refLocators must accept and handle a 'selector' parameter."""
    src = TAB_TS.read_text()

    # refLocator signature must include selector
    assert re.search(r'refLocator\(params:\s*\{[^}]*selector', src), \
        "refLocator must accept selector in its params type"

    # refLocators must have a branch for selector
    assert re.search(r'param\.selector', src), \
        "refLocators must check param.selector to handle selector-based targeting"

    # When selector is provided, it should use page.locator(selector) not aria-ref
    assert re.search(r'page\.locator\(param\.selector\)', src) or \
           re.search(r'page\.locator\(params?\.selector\)', src), \
        "When selector is provided, must use page.locator(selector)"


# [pr_diff] fail_to_pass

    # After filteredTools definition, must have omit logic for selector
    ft_section = src[src.index('filteredTools'):] if 'filteredTools' in src else ''
    assert '.omit(' in ft_section or 'omit' in ft_section, \
        "filteredTools must use .omit() to strip selector fields from MCP schemas"
    assert 'selector' in ft_section, \
        "filteredTools must reference 'selector' in its schema transformation"


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — SKILL.md documentation test
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass — packages/playwright-core/src/skill/SKILL.md

    The skill documentation should explain that in addition to element refs,
    users can target elements using CSS selectors and role selectors.
    """
    content = SKILL_MD.read_text()
    content_lower = content.lower()

    # Must have a section about targeting/selectors
    assert 'targeting' in content_lower or 'selector' in content_lower, \
        "SKILL.md must mention element targeting or selectors"

    # Must show CSS selector usage (e.g., #id, .class, or element selectors)
    assert re.search(r'#\w+|\.[\w-]+\s|css', content_lower), \
        "SKILL.md must show CSS selector examples"

    # Must show role selector usage
    assert 'role=' in content, \
        "SKILL.md must show role selector examples (role=...)"

    # Must clarify that refs are still the default
    assert re.search(r'ref|snapshot', content_lower), \
        "SKILL.md should mention that refs from snapshots are the default"
