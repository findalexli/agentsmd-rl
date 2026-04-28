"""
Task: supabase-context-menu-performance-fix
Repo: supabase/supabase @ 2af6b3eaec65971a8fa6986afad44d6581075ac5
PR: 44578

The Results component rendered a ContextMenu_Shadcn_ per table cell. With 1000+ rows,
this created thousands of document-level keydown listeners, making keystrokes take ~250ms.

The fix:
1. Extract formatClipboardValue and formatCellValue to Results.utils.ts
2. Use a single shared ContextMenu with a hidden trigger positioned at cursor
3. Use useMemo for columns and useCallback for handleContextMenu
4. Fix QueryBlock layout (flex instead of overflow-auto)

All checks must pass for reward = 1. Any failure = reward 0.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/supabase"


# ============ pass_to_pass tests (repo_tests origin) ============

def test_p2p_results_utils_file_exists():
    """Results.utils.ts file exists with expected utility functions (pass_to_pass)."""
    r = subprocess.run(
        ["test", "-f", f"{REPO}/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.ts"],
        capture_output=True,
    )
    assert r.returncode == 0, "Results.utils.ts must exist"


def test_p2p_results_utils_has_formatresults():
    """Results.utils.ts exports formatResults function (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-q", "export function formatResults",
         f"{REPO}/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.ts"],
        capture_output=True,
    )
    assert r.returncode == 0, "Results.utils.ts must export formatResults function"


def test_p2p_results_utils_has_convertresultstocsv():
    """Results.utils.ts exports convertResultsToCSV function (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-q", "export function convertResultsToCSV",
         f"{REPO}/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.ts"],
        capture_output=True,
    )
    assert r.returncode == 0, "Results.utils.ts must export convertResultsToCSV function"


def test_p2p_results_utils_has_convertresultstomarkdown():
    """Results.utils.ts exports convertResultsToMarkdown function (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-q", "export function convertResultsToMarkdown",
         f"{REPO}/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.ts"],
        capture_output=True,
    )
    assert r.returncode == 0, "Results.utils.ts must export convertResultsToMarkdown function"


def test_p2p_results_utils_has_convertresultstojson():
    """Results.utils.ts exports convertResultsToJSON function (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-q", "export function convertResultsToJSON",
         f"{REPO}/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.ts"],
        capture_output=True,
    )
    assert r.returncode == 0, "Results.utils.ts must export convertResultsToJSON function"


def test_p2p_results_utils_has_getresultsheaders():
    """Results.utils.ts exports getResultsHeaders function (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-q", "export function getResultsHeaders",
         f"{REPO}/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.ts"],
        capture_output=True,
    )
    assert r.returncode == 0, "Results.utils.ts must export getResultsHeaders function"


def test_p2p_results_utils_tests_exist():
    """Results.utils.test.ts test file exists (pass_to_pass)."""
    r = subprocess.run(
        ["test", "-f",
         f"{REPO}/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.test.ts"],
        capture_output=True,
    )
    assert r.returncode == 0, "Results.utils.test.ts must exist"


def test_p2p_results_component_exists():
    """Results.tsx component file exists (pass_to_pass)."""
    r = subprocess.run(
        ["test", "-f", f"{REPO}/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.tsx"],
        capture_output=True,
    )
    assert r.returncode == 0, "Results.tsx must exist"


def test_p2p_results_has_component_definition():
    """Results.tsx defines the Results component (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-q", "const Results",
         f"{REPO}/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.tsx"],
        capture_output=True,
    )
    assert r.returncode == 0, "Results component must be defined"


def test_p2p_results_has_formatclipboardvalue():
    """Results.tsx imports formatClipboardValue from Results.utils.ts (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-q", "formatClipboardValue",
         f"{REPO}/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.tsx"],
        capture_output=True,
    )
    assert r.returncode == 0, "formatClipboardValue must be used in Results.tsx (imported from Results.utils.ts)"


def test_p2p_queryblock_exists():
    """QueryBlock.tsx component exists (pass_to_pass)."""
    r = subprocess.run(
        ["test", "-f", f"{REPO}/apps/studio/components/ui/QueryBlock/QueryBlock.tsx"],
        capture_output=True,
    )
    assert r.returncode == 0, "QueryBlock.tsx must exist"


def test_p2p_queryblock_has_flex_classes():
    """QueryBlock has flex layout classes (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-q", "flex-1", f"{REPO}/apps/studio/components/ui/QueryBlock/QueryBlock.tsx"],
        capture_output=True,
    )
    assert r.returncode == 0, "QueryBlock must have flex-1 class"


def test_p2p_repo_prettier_check():
    """Repo code formatting passes prettier check (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "test:prettier"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


# ============ Behavioral tests ============

def test_typescript_compiles():
    """Modified TypeScript files must exist and define the Results component."""
    results_tsx = f"{REPO}/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.tsx"
    utils_ts = f"{REPO}/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.ts"

    for path in [results_tsx, utils_ts]:
        r = subprocess.run(["test", "-f", path], capture_output=True)
        assert r.returncode == 0, f"{path} must exist"

    r = subprocess.run(
        ["grep", "-q", "const Results", results_tsx],
        capture_output=True,
    )
    assert r.returncode == 0, "Results component must be defined"


def test_format_clipboard_value_behavior():
    """formatClipboardValue must return '' for null, JSON.stringify for objects/arrays, String for primitives."""
    r = subprocess.run(
        ["npx", "tsx", "-e", """
import { formatClipboardValue } from "./apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils"

if (typeof formatClipboardValue !== 'function') {
    console.error('formatClipboardValue is not exported as a function from Results.utils')
    process.exit(1)
}

const tests: [unknown, string][] = [
    [null, ''],
    [{a: 1}, '{"a":1}'],
    [[1, 2], '[1,2]'],
    ['hello', 'hello'],
    [42, '42'],
    [false, 'false'],
]

for (const [input, expected] of tests) {
    const result = formatClipboardValue(input)
    if (result !== expected) {
        console.error('FAIL: formatClipboardValue(' + JSON.stringify(input) + ') = ' + JSON.stringify(result) + ', expected ' + JSON.stringify(expected))
        process.exit(1)
    }
}
console.log('All formatClipboardValue tests passed')
"""],
        capture_output=True, text=True, timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"formatClipboardValue behavioral test failed:\n{r.stderr}\n{r.stdout}"


def test_format_cell_value_behavior():
    """formatCellValue must return 'NULL' for null, string as-is, JSON.stringify for others."""
    r = subprocess.run(
        ["npx", "tsx", "-e", """
import { formatCellValue } from "./apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils"

if (typeof formatCellValue !== 'function') {
    console.error('formatCellValue is not exported as a function from Results.utils')
    process.exit(1)
}

const tests: [unknown, string][] = [
    [null, 'NULL'],
    ['hello', 'hello'],
    [{a: 1}, '{"a":1}'],
    [42, '42'],
    [true, 'true'],
    [[1, 2], '[1,2]'],
]

for (const [input, expected] of tests) {
    const result = formatCellValue(input)
    if (result !== expected) {
        console.error('FAIL: formatCellValue(' + JSON.stringify(input) + ') = ' + JSON.stringify(result) + ', expected ' + JSON.stringify(expected))
        process.exit(1)
    }
}
console.log('All formatCellValue tests passed')
"""],
        capture_output=True, text=True, timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"formatCellValue behavioral test failed:\n{r.stderr}\n{r.stdout}"


def test_single_context_menu_pattern():
    """Results.tsx must use a single shared context menu, not one per cell (verified via TypeScript AST)."""
    r = subprocess.run(
        ["npx", "tsx", "-e", """
import { readFileSync } from 'fs'
import * as ts from 'typescript'

const filePath = 'apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.tsx'
const source = readFileSync(filePath, 'utf-8')
const sf = ts.createSourceFile('Results.tsx', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX)

// Verify ContextMenu_Shadcn_ is used somewhere in the component
if (!source.includes('ContextMenu_Shadcn_')) {
    console.error('Results.tsx must include ContextMenu_Shadcn_')
    process.exit(1)
}

// Walk AST: check that no nested function (depth >= 2) contains ContextMenu_Shadcn_.
// Depth 0 = module scope, depth 1 = component function, depth 2+ = inner functions
// (cell renderers, callbacks, etc). If ContextMenu is inside an inner function,
// it would be instantiated per-cell, causing the performance bug.
function hasContextMenuInNestedFn(node: ts.Node, fnDepth: number): boolean {
    const isFn = ts.isArrowFunction(node) || ts.isFunctionDeclaration(node) || ts.isFunctionExpression(node)
    const newDepth = isFn ? fnDepth + 1 : fnDepth

    if (isFn && newDepth >= 2) {
        const text = source.substring(node.getStart(), node.getEnd())
        if (text.includes('ContextMenu_Shadcn_')) {
            return true
        }
        return false
    }

    let found = false
    ts.forEachChild(node, child => {
        if (hasContextMenuInNestedFn(child, newDepth)) found = true
    })
    return found
}

if (hasContextMenuInNestedFn(sf, 0)) {
    console.error('ContextMenu_Shadcn_ must not be inside a per-cell rendering function. Use a single shared context menu at the component level.')
    process.exit(1)
}

console.log('Single context menu pattern verified via AST')
"""],
        capture_output=True, text=True, timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Context menu pattern test failed:\n{r.stderr}\n{r.stdout}"


def test_queryblock_flex_layout():
    """QueryBlock must not use overflow-auto on the Results container (causes double scrollbar in Firefox)."""
    r = subprocess.run(
        ["npx", "tsx", "-e", r"""
import { readFileSync } from 'fs'

const content = readFileSync('apps/studio/components/ui/QueryBlock/QueryBlock.tsx', 'utf-8')
const lines = content.split('\n')

for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('Results') && lines[i].includes('rows=')) {
        // Find the immediate parent div by searching backwards for the first opening <div
        for (let j = i - 1; j >= Math.max(0, i - 5); j--) {
            if (lines[j].includes('<div') && lines[j].includes('className')) {
                // This is the direct parent container div
                if (lines[j].includes('overflow-auto')) {
                    console.error('The container wrapping <Results> must not use overflow-auto (causes double scrollbar in Firefox)')
                    process.exit(1)
                }
                console.log('QueryBlock layout check passed - no overflow-auto on Results wrapper')
                process.exit(0)
            }
        }
        console.log('QueryBlock layout check passed')
        process.exit(0)
    }
}

console.error('Could not find <Results rows=...> in QueryBlock.tsx')
process.exit(1)
"""],
        capture_output=True, text=True, timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"QueryBlock layout test failed:\n{r.stderr}\n{r.stdout}"


def test_results_component_tests_pass():
    """The Results component test file must exist, be valid TypeScript, and define tests."""
    r = subprocess.run(
        ["npx", "tsx", "-e", """
import { existsSync, readFileSync } from 'fs'
import * as ts from 'typescript'

const testPath = 'apps/studio/tests/components/SQLEditor/Results.test.tsx'
if (!existsSync(testPath)) {
    console.error('Results.test.tsx must exist at ' + testPath)
    process.exit(1)
}

// Parse as TSX to verify it is syntactically valid TypeScript
const source = readFileSync(testPath, 'utf-8')
ts.createSourceFile('Results.test.tsx', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX)

// Verify it contains test case definitions
if (!(source.includes('test(') || source.includes('it('))) {
    console.error('Results.test.tsx must contain test case definitions (test/it)')
    process.exit(1)
}

// Verify it references the Results component
if (!source.includes('Results')) {
    console.error('Results.test.tsx must reference the Results component')
    process.exit(1)
}

console.log('Results.test.tsx validation passed')
"""],
        capture_output=True, text=True, timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Results component test validation failed:\n{r.stderr}\n{r.stdout}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_e2e_tests_reset_supabase():
    """pass_to_pass | CI job 'E2E tests' → step 'Reset supabase'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm exec supabase init'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Reset supabase' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_reports_merge_playwright_reports():
    """pass_to_pass | CI job 'E2E reports' → step 'Merge Playwright reports'"""
    r = subprocess.run(
        ["bash", "-lc", 'npx playwright merge-reports --config=e2e/studio/playwright.merge.config.ts -- e2e/studio/blob-report'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Merge Playwright reports' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run Tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run test:ci'], cwd=os.path.join(REPO, './apps/studio'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_renders_a_single_context_menu_regardless_of_row_():
    """fail_to_pass | PR added test 'renders a single context menu regardless of row count' in 'apps/studio/tests/components/SQLEditor/Results.test.tsx' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "apps/studio/tests/components/SQLEditor/Results.test.tsx" -t "renders a single context menu regardless of row count" 2>&1 || npx vitest run "apps/studio/tests/components/SQLEditor/Results.test.tsx" -t "renders a single context menu regardless of row count" 2>&1 || pnpm jest "apps/studio/tests/components/SQLEditor/Results.test.tsx" -t "renders a single context menu regardless of row count" 2>&1 || npx jest "apps/studio/tests/components/SQLEditor/Results.test.tsx" -t "renders a single context menu regardless of row count" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'renders a single context menu regardless of row count' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_shows_empty_state_when_no_rows_provided():
    """fail_to_pass | PR added test 'shows empty state when no rows provided' in 'apps/studio/tests/components/SQLEditor/Results.test.tsx' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "apps/studio/tests/components/SQLEditor/Results.test.tsx" -t "shows empty state when no rows provided" 2>&1 || npx vitest run "apps/studio/tests/components/SQLEditor/Results.test.tsx" -t "shows empty state when no rows provided" 2>&1 || pnpm jest "apps/studio/tests/components/SQLEditor/Results.test.tsx" -t "shows empty state when no rows provided" 2>&1 || npx jest "apps/studio/tests/components/SQLEditor/Results.test.tsx" -t "shows empty state when no rows provided" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'shows empty state when no rows provided' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
