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
_SYMLINK = Path(REPO) / "packages/playwright-core/src/mcpBundleImpl.ts"


def _run_tsx(script: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a TypeScript snippet using npx tsx.

    Creates a temporary symlink for mcpBundleImpl so tsx can resolve imports,
    then removes it after execution to avoid interfering with the repo build.
    """
    script_path = Path(REPO) / "_eval_tmp.ts"
    script_path.write_text(script)
    # Create symlink for import resolution
    symlink_target = Path("../bundles/mcp/src/mcpBundleImpl.ts")
    if not _SYMLINK.exists():
        _SYMLINK.symlink_to(symlink_target)
    try:
        return subprocess.run(
            ["npx", "tsx", str(script_path)],
            capture_output=True, text=True, timeout=timeout,
            cwd=REPO,
        )
    finally:
        script_path.unlink(missing_ok=True)
        _SYMLINK.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

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

def test_asref_function_classifies_inputs():
    """CLI classification helper correctly distinguishes refs from selectors.

    Tests the actual classification logic by calling parseCommand on the
    real click command with various inputs and checking the toolParams output.
    """
    result = _run_tsx("""
import { commands } from "./packages/playwright-core/src/cli/daemon/commands.ts";
import { parseCommand } from "./packages/playwright-core/src/cli/daemon/command.ts";

const tests = [
    // Valid refs => should produce { ref: value }, no selector
    { args: ["click", "e15"], expectRef: "e15", expectSelector: undefined },
    { args: ["click", "f1e2"], expectRef: "f1e2", expectSelector: undefined },
    { args: ["click", "f12e99"], expectRef: "f12e99", expectSelector: undefined },
    // CSS/role selectors => should produce { ref: "", selector: value }
    { args: ["click", "#main"], expectRef: "", expectSelector: "#main" },
    { args: ["click", "role=button"], expectRef: "", expectSelector: "role=button" },
    { args: ["click", "#main >> role=button"], expectRef: "", expectSelector: "#main >> role=button" },
    { args: ["click", "button.submit"], expectRef: "", expectSelector: "button.submit" },
];

const results = tests.map(t => {
    const parsed = parseCommand(commands.click, { _: t.args });
    return {
        input: t.args[1],
        ref: parsed.toolParams.ref,
        selector: parsed.toolParams.selector,
        expectRef: t.expectRef,
        expectSelector: t.expectSelector,
        pass: parsed.toolParams.ref === t.expectRef && parsed.toolParams.selector === t.expectSelector,
    };
});

console.log(JSON.stringify({ results }));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip().split('\n')[-1])
    for r in data["results"]:
        assert r["pass"], \
            f"classify('{r['input']}'): expected ref={r['expectRef']}, selector={r['expectSelector']}; " \
            f"got ref={r['ref']}, selector={r['selector']}"


def test_cli_commands_use_target_param():
    """CLI click/fill/hover/select/check/uncheck all route selectors correctly.

    Calls parseCommand on multiple CLI commands with both refs and CSS selectors,
    verifying each command correctly classifies the input.
    """
    result = _run_tsx("""
import { commands } from "./packages/playwright-core/src/cli/daemon/commands.ts";
import { parseCommand } from "./packages/playwright-core/src/cli/daemon/command.ts";

// Commands that accept a single target element (first positional arg)
const singleTargetCmds = ["click", "dblclick", "hover", "check", "uncheck"];

const results: any[] = [];
for (const name of singleTargetCmds) {
    const cmd = commands[name];
    if (!cmd) { results.push({ name, error: "not found" }); continue; }

    // With a snapshot ref
    const refResult = parseCommand(cmd, { _: [name, "e15"] });
    // With a CSS selector
    const selResult = parseCommand(cmd, { _: [name, "#my-element"] });

    results.push({
        name,
        refHasRef: refResult.toolParams.ref === "e15",
        refNoSelector: refResult.toolParams.selector === undefined,
        selHasSelector: selResult.toolParams.selector === "#my-element",
        selRefEmpty: selResult.toolParams.ref === "",
    });
}

// Also test fill (has extra 'text' arg)
const fillRef = parseCommand(commands.fill, { _: ["fill", "e10", "hello"] });
const fillSel = parseCommand(commands.fill, { _: ["fill", "#input", "hello"] });
results.push({
    name: "fill",
    refHasRef: fillRef.toolParams.ref === "e10",
    refNoSelector: fillRef.toolParams.selector === undefined,
    selHasSelector: fillSel.toolParams.selector === "#input",
    selRefEmpty: fillSel.toolParams.ref === "",
});

// Test select (has extra 'val' arg)
const selectRef = parseCommand(commands.select, { _: ["select", "e3", "option1"] });
const selectSel = parseCommand(commands.select, { _: ["select", "#dropdown", "option1"] });
results.push({
    name: "select",
    refHasRef: selectRef.toolParams.ref === "e3",
    refNoSelector: selectRef.toolParams.selector === undefined,
    selHasSelector: selectSel.toolParams.selector === "#dropdown",
    selRefEmpty: selectSel.toolParams.ref === "",
});

console.log(JSON.stringify({ results }));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip().split('\n')[-1])
    for r in data["results"]:
        assert "error" not in r, f"Command {r['name']} not found"
        assert r["refHasRef"], f"{r['name']}: ref input should produce ref='e15' (or similar)"
        assert r["refNoSelector"], f"{r['name']}: ref input should not produce selector field"
        assert r["selHasSelector"], f"{r['name']}: selector input should produce selector field"
        assert r["selRefEmpty"], f"{r['name']}: selector input should produce ref=''"


def test_drag_uses_start_end_element():
    """Drag command maps startElement/endElement to startRef/startSelector/endRef/endSelector.

    Calls parseCommand on the drag command with various input combinations
    to verify the full parameter mapping behavior.
    """
    result = _run_tsx("""
import { commands } from "./packages/playwright-core/src/cli/daemon/commands.ts";
import { parseCommand } from "./packages/playwright-core/src/cli/daemon/command.ts";

// Drag with two refs
const r1 = parseCommand(commands.drag, { _: ["drag", "e15", "e20"] });
// Drag with two selectors
const r2 = parseCommand(commands.drag, { _: ["drag", "#start", ".end-zone"] });
// Drag with mixed (ref -> selector)
const r3 = parseCommand(commands.drag, { _: ["drag", "e5", "#target"] });

console.log(JSON.stringify({
    refs: r1.toolParams,
    sels: r2.toolParams,
    mixed: r3.toolParams,
}));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip().split('\n')[-1])

    # Two refs
    refs = data["refs"]
    assert refs.get("startRef") == "e15", f"drag refs: startRef should be 'e15', got {refs}"
    assert refs.get("endRef") == "e20", f"drag refs: endRef should be 'e20', got {refs}"

    # Two selectors
    sels = data["sels"]
    assert sels.get("startSelector") == "#start", f"drag sels: startSelector should be '#start', got {sels}"
    assert sels.get("endSelector") == ".end-zone", f"drag sels: endSelector should be '.end-zone', got {sels}"
    assert sels.get("startRef") == "", f"drag sels: startRef should be '', got {sels}"
    assert sels.get("endRef") == "", f"drag sels: endRef should be '', got {sels}"

    # Mixed
    mixed = data["mixed"]
    assert mixed.get("startRef") == "e5", f"drag mixed: startRef should be 'e5', got {mixed}"
    assert mixed.get("endSelector") == "#target", f"drag mixed: endSelector should be '#target', got {mixed}"


def test_tab_reflocator_accepts_selector():
    """Tab.refLocator and refLocators accept optional selector parameter.

    Verifies that the method signatures include a selector parameter and
    the implementation creates a page.locator when a selector is provided.
    """
    tab_path = Path(REPO) / "packages/playwright-core/src/tools/tab.ts"
    src = tab_path.read_text()

    # Check refLocator signature includes 'selector' in params
    ref_locator_match = re.search(r'async\s+refLocator\(params:\s*\{([^}]+)\}', src)
    assert ref_locator_match, "refLocator method not found"
    assert "selector" in ref_locator_match.group(1), \
        "refLocator signature should include selector param"

    # Check refLocators signature includes 'selector' in params
    ref_locators_match = re.search(r'async\s+refLocators\(params:\s*\{([^}]+)\}', src)
    assert ref_locators_match, "refLocators method not found"
    assert "selector" in ref_locators_match.group(1), \
        "refLocators signature should include selector param"

    # Verify page.locator is called with selector in the selector branch
    assert re.search(r'page\.locator\([^)]*selector', src), \
        "Should create locator from selector when provided"

    # Verify error message for no-match selectors
    assert "does not match any elements" in src, \
        "Should throw error when selector matches no elements"


def test_tool_schemas_include_selector():
    """MCP tool schemas (snapshot, evaluate, verify, form) include selector field.

    Imports actual tool definitions and uses Zod safeParse to verify schemas
    accept an optional selector field.
    """
    result = _run_tsx("""
import { elementSchema } from "./packages/playwright-core/src/tools/snapshot.ts";
import evaluateTools from "./packages/playwright-core/src/tools/evaluate.ts";
import formTools from "./packages/playwright-core/src/tools/form.ts";
import verifyTools from "./packages/playwright-core/src/tools/verify.ts";

const results: any[] = [];

// elementSchema (shared by click, hover, etc.)
const elemWithSel = elementSchema.safeParse({ element: "btn", ref: "e5", selector: "#btn" });
const elemNoSel = elementSchema.safeParse({ element: "btn", ref: "e5" });
results.push({ name: "elementSchema", acceptsSelector: elemWithSel.success, optionalSelector: elemNoSel.success });

// evaluate
const evalTool = evaluateTools.find((t: any) => t.schema?.name === "browser_evaluate");
if (evalTool) {
    const r1 = evalTool.schema.inputSchema.safeParse({ "function": "() => 1", ref: "e5", selector: "#el" });
    const r2 = evalTool.schema.inputSchema.safeParse({ "function": "() => 1", ref: "e5" });
    results.push({ name: "evaluate", acceptsSelector: r1.success, optionalSelector: r2.success });
}

// form (fields array with selector)
const formTool = formTools.find((t: any) => t.schema?.name === "browser_fill_form");
if (formTool) {
    const r1 = formTool.schema.inputSchema.safeParse({ fields: [{ name: "user", type: "textbox", ref: "e5", selector: "#user", value: "test" }] });
    const r2 = formTool.schema.inputSchema.safeParse({ fields: [{ name: "user", type: "textbox", ref: "e5", value: "test" }] });
    results.push({ name: "form", acceptsSelector: r1.success, optionalSelector: r2.success });
}

// verify_list
const verifyList = verifyTools.find((t: any) => t.schema?.name === "browser_verify_list_visible");
if (verifyList) {
    const r1 = verifyList.schema.inputSchema.safeParse({ element: "list", ref: "e5", selector: "#list", items: ["a"] });
    const r2 = verifyList.schema.inputSchema.safeParse({ element: "list", ref: "e5", items: ["a"] });
    results.push({ name: "verify_list", acceptsSelector: r1.success, optionalSelector: r2.success });
}

// verify_value
const verifyValue = verifyTools.find((t: any) => t.schema?.name === "browser_verify_value");
if (verifyValue) {
    const r1 = verifyValue.schema.inputSchema.safeParse({ type: "textbox", element: "input", ref: "e5", selector: "#input", value: "hello" });
    const r2 = verifyValue.schema.inputSchema.safeParse({ type: "textbox", element: "input", ref: "e5", value: "hello" });
    results.push({ name: "verify_value", acceptsSelector: r1.success, optionalSelector: r2.success });
}

console.log(JSON.stringify({ results }));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip().split('\n')[-1])
    for r in data["results"]:
        assert r["acceptsSelector"], \
            f"{r['name']}: schema should accept selector field"
        assert r["optionalSelector"], \
            f"{r['name']}: selector field should be optional"

    # Also verify screenshot.ts has selector in source (can't import due to utilsBundle dep)
    screenshot_path = Path(REPO) / "packages/playwright-core/src/tools/screenshot.ts"
    screenshot_src = screenshot_path.read_text()
    assert re.search(r'selector.*z\.string\(\)\.optional\(\)', screenshot_src), \
        "screenshot.ts should have selector: z.string().optional() in schema"


def test_filtered_tools_strips_selector():
    """filteredTools() omits selector/startSelector/endSelector from MCP schemas.

    Verifies that tools.ts transforms tool schemas to strip selector fields
    before they are exposed via MCP.
    """
    tools_path = Path(REPO) / "packages/playwright-core/src/tools/tools.ts"
    src = tools_path.read_text()

    # filteredTools must exist
    assert "filteredTools" in src, "filteredTools function should exist"

    # It must use omit to strip selector fields
    assert re.search(r'\.omit\(', src), \
        "filteredTools should use .omit() to strip fields from schemas"

    # All three selector fields should be mentioned for omission
    assert "selector" in src, "filteredTools should handle selector field"
    assert "startSelector" in src, "filteredTools should handle startSelector field"
    assert "endSelector" in src, "filteredTools should handle endSelector field"


def test_skill_md_documents_selector_targeting():
    """SKILL.md must document how to use CSS/role selectors for targeting elements."""
    skill_md = Path(REPO) / "packages/playwright-core/src/skill/SKILL.md"
    assert skill_md.exists(), "SKILL.md not found"
    content = skill_md.read_text()
    content_lower = content.lower()

    assert "targeting" in content_lower or "selector" in content_lower, \
        "SKILL.md should document element targeting with selectors"

    assert "css" in content_lower, \
        "SKILL.md should mention CSS selectors"

    assert "role" in content_lower and "selector" in content_lower, \
        "SKILL.md should mention role selectors"

    assert ('click "#' in content or "click '#" in content or
            'click "role=' in content or "click 'role=" in content), \
        "SKILL.md should show example of click with a CSS or role selector"


def test_skill_md_shows_ref_and_selector_examples():
    """SKILL.md must show both ref-based and selector-based interaction examples."""
    skill_md = Path(REPO) / "packages/playwright-core/src/skill/SKILL.md"
    content = skill_md.read_text()

    assert re.search(r"click\s+[ef]\d+", content), \
        "SKILL.md should show ref-based click example (e.g., 'click e15')"

    assert "#" in content and ("click" in content.lower()), \
        "SKILL.md should show CSS selector example with click"

    assert "role=" in content, \
        "SKILL.md should show role selector example"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD checks
# ---------------------------------------------------------------------------

def test_repo_check_deps():
    """Repo dependency checks pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "check-deps"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"check-deps failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_eslint_tools():
    """ESLint passes on modified tool files (pass_to_pass)."""
    modified_tool_files = [
        "packages/playwright-core/src/tools/tab.ts",
        "packages/playwright-core/src/tools/tools.ts",
        "packages/playwright-core/src/tools/snapshot.ts",
        "packages/playwright-core/src/tools/evaluate.ts",
        "packages/playwright-core/src/tools/screenshot.ts",
        "packages/playwright-core/src/tools/verify.ts",
        "packages/playwright-core/src/tools/form.ts",
    ]
    for f in modified_tool_files:
        p = Path(REPO) / f
        assert p.exists(), f"File not found: {f}"
    r = subprocess.run(
        ["npm", "run", "eslint", "--", "--no-cache"] + modified_tool_files,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed on tools:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_eslint_cli():
    """ESLint passes on modified CLI files (pass_to_pass)."""
    modified_cli_files = [
        "packages/playwright-core/src/cli/daemon/commands.ts",
    ]
    for f in modified_cli_files:
        p = Path(REPO) / f
        assert p.exists(), f"File not found: {f}"
    r = subprocess.run(
        ["npm", "run", "eslint", "--", "--no-cache"] + modified_cli_files,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed on CLI files:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_lint_packages():
    """Repo workspace packages are consistent (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"lint-packages failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


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


def test_repo_build():
    """Repo builds successfully (pass_to_pass)."""
    # Clean up any stale symlinks from tsx-based tests before building
    symlink = Path(REPO) / "packages/playwright-core/src/mcpBundleImpl.ts"
    symlink.unlink(missing_ok=True)
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression
# ---------------------------------------------------------------------------

def test_ref_pattern_still_works():
    """Classification returns correct toolParams for valid ref patterns, preserving existing behavior."""
    result = _run_tsx("""
import { commands } from "./packages/playwright-core/src/cli/daemon/commands.ts";
import { parseCommand } from "./packages/playwright-core/src/cli/daemon/command.ts";

// Verify all ref patterns produce ref in toolParams (not selector)
const refPatterns = ["e0", "e15", "e999", "f1e2", "f12e99"];
const results = refPatterns.map(ref => {
    const parsed = parseCommand(commands.click, { _: ["click", ref] });
    return {
        input: ref,
        ref: parsed.toolParams.ref,
        hasSelector: parsed.toolParams.selector !== undefined,
    };
});

console.log(JSON.stringify({ results }));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip().split('\n')[-1])
    for r in data["results"]:
        assert r["ref"] == r["input"], \
            f"Ref pattern '{r['input']}' should produce ref='{r['input']}', got ref='{r['ref']}'"
        assert not r["hasSelector"], \
            f"Ref pattern '{r['input']}' should NOT produce a selector field"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_docs___lint_npm():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npm_2():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npx():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npx playwright install --with-deps'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npm_3():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_verify_clean_tree():
    """pass_to_pass | CI job 'docs & lint' → step 'Verify clean tree'"""
    r = subprocess.run(
        ["bash", "-lc", 'if [[ -n $(git status -s) ]]; then\n  echo "ERROR: tree is dirty after npm run build:"\n  git diff\n  exit 1\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify clean tree' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_audit_prod_npm_dependencies():
    """pass_to_pass | CI job 'docs & lint' → step 'Audit prod NPM dependencies'"""
    r = subprocess.run(
        ["bash", "-lc", 'node utils/check_audit.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Audit prod NPM dependencies' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_pip():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pip install -r utils/doclint/linting-code-snippets/python/requirements.txt'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_mvn():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'mvn package'], cwd=os.path.join(REPO, 'utils/doclint/linting-code-snippets/java'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_node():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'node utils/doclint/linting-code-snippets/cli.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")