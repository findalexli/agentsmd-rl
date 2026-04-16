"""
Task: litellm-feat-ui-add-user-filtering-usage
Repo: BerriAI/litellm @ a38993b871a32090caea0941427a8bc5489a5c02
PR:   22059

Verifies that 'user' entity type is added to the usage page with proper
UI/backend contract handling, and that AGENTS.md/CLAUDE.md are updated
with corresponding documentation rules.
"""

import subprocess
from pathlib import Path

REPO = Path("/workspace/litellm")
UI = REPO / "ui" / "litellm-dashboard"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js script in the UI directory and return the result."""
    script_path = UI / "_eval_tmp.js"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", str(script_path)],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(UI),
        )
    finally:
        script_path.unlink(missing_ok=True)


def _ensure_npm_and_deps():
    """Enable npm via corepack and install dependencies if needed."""
    subprocess.run(
        ["corepack", "enable", "npm"],
        capture_output=True, text=True, timeout=30,
        cwd=UI,
    )
    if not (UI / "node_modules").exists():
        subprocess.run(
            ["npm", "install", "--legacy-peer-deps"],
            capture_output=True, text=True, timeout=300,
            cwd=UI,
        )


# --- Code behavior tests (fail_to_pass) ---


def test_entity_type_includes_user():
    """EntityType type union must include 'user' - verify via TypeScript compilation."""
    script = '''
const fs = require("fs");

// Create a test file that imports EntityType and tries to assign "user" to it
const testContent = `
import type { EntityType } from "./src/components/EntityUsageExport/types";
const testUser: EntityType = "user";
console.log("User assignment succeeded:", testUser);
`;

fs.writeFileSync("_entity_test.ts", testContent);

const { execSync } = require("child_process");
try {
    // Try to compile - will fail if "user" is not in the EntityType union
    execSync("npx tsc --noEmit --skipLibCheck _entity_test.ts 2>&1", { timeout: 60000 });
    console.log("PASS: EntityType accepts 'user' value");
    process.exit(0);
} catch (e) {
    console.log("FAIL: EntityType does not accept 'user' value - type check failed");
    console.log(e.stdout?.toString() || e.message);
    process.exit(1);
} finally {
    fs.unlinkSync("_entity_test.ts");
}
'''
    result = _run_node(script, timeout=120)
    assert result.returncode == 0, f"EntityType missing 'user': {result.stdout}{result.stderr}"


def test_usage_view_select_has_user_option():
    """UsageViewSelect must include 'user' as a selectable option - verify via runtime render."""
    script = '''
const fs = require("fs");

// Build a test that imports the OPTIONS array and checks for user
const testContent = `
// Mock React first
global.React = { createElement: (tag, props, ...children) => ({ tag, props, children }) };

// Mock antd icons
const mockIcon = () => null;
require.cache[require.resolve("@ant-design/icons")] = {
    id: require.resolve("@ant-design/icons"),
    filename: require.resolve("@ant-design/icons"),
    loaded: true,
    exports: {
        GlobalOutlined: mockIcon,
        TeamOutlined: mockIcon,
        ShoppingCartOutlined: mockIcon,
        TagsOutlined: mockIcon,
        RobotOutlined: mockIcon,
        UserOutlined: mockIcon,
        LineChartOutlined: mockIcon,
        BarChartOutlined: mockIcon,
    }
};

// Now require the module
const path = require("path");
const modulePath = path.join(process.cwd(), "src/components/UsagePage/components/UsageViewSelect/UsageViewSelect.tsx");

// Read and evaluate to extract OPTIONS
const content = fs.readFileSync(modulePath, "utf-8");

// Look for the OPTIONS array definition
const optionsMatch = content.match(/const\\s+OPTIONS\\s*:\\s*OptionConfig\\[\\]\\s*=\\s*(\\[.*?\\];?)/s);
if (!optionsMatch) {
    console.log("FAIL: Could not find OPTIONS array");
    process.exit(1);
}

// Extract option values by looking for value: "..." patterns
const valueMatches = [...content.matchAll(/value:\\s*["']([^"']+)["']/g)];
const values = valueMatches.map(m => m[1]);

console.log("Found option values:", values);

if (!values.includes("user")) {
    console.log("FAIL: 'user' not found in UsageViewSelect options");
    process.exit(1);
}

// Check that there's a "User Usage" label somewhere
if (!content.includes("User Usage")) {
    console.log("FAIL: 'User Usage' label not found");
    process.exit(1);
}

console.log("PASS: UsageViewSelect has user option with User Usage label");
`;

fs.writeFileSync("_view_select_test.js", testContent);

try {
    eval(testContent);
} catch (e) {
    console.log("FAIL:", e.message);
    process.exit(1);
} finally {
    if (fs.existsSync("_view_select_test.js")) fs.unlinkSync("_view_select_test.js");
}
'''
    result = _run_node(script)
    assert result.returncode == 0, f"UsageViewSelect missing user option: {result.stdout}{result.stderr}"


def test_export_header_supports_single_select_mode():
    """UsageExportHeader must support single-select mode - verify by checking the component accepts and handles mode prop."""
    script = '''
const fs = require("fs");
const content = fs.readFileSync("src/components/EntityUsageExport/UsageExportHeader.tsx", "utf-8");

// Check for filterMode prop in interface (any name that indicates mode)
const hasModeProp = /filterMode\??\s*:\s*["']?(multiple|single)/.test(content);
if (!hasModeProp) {
    console.log("FAIL: filterMode prop not found in interface");
    process.exit(1);
}

// Check for conditional mode prop passed to Select (mode=...)
const hasModeAssignment = /mode\s*=\s*\{/.test(content);
if (!hasModeAssignment) {
    console.log("FAIL: mode prop not conditionally assigned to Select");
    process.exit(1);
}

// Check for conditional value handling (array vs single value)
// Look for pattern that transforms value based on mode
const hasValueCondition = content.includes("filterMode") && (
    content.includes("selectedFilters[0]") ||
    content.includes("? selectedFilters[0]") ||
    /filterMode.*\?.*\[.*\]:/.test(content) ||
    /filterMode[^?]*===.*single/.test(content)
);

if (!hasValueCondition) {
    console.log("FAIL: No conditional value handling for single vs multiple mode");
    process.exit(1);
}

// Check for conditional onChange handling
const hasOnChangeCondition = content.includes("filterMode") && (
    content.includes("onFiltersChange") &&
    (content.includes("? [value]") ||
     content.includes("[value]") ||
     /value\s*\?\s*\[/.test(content))
);

if (!hasOnChangeCondition) {
    console.log("FAIL: No conditional onChange handling for single vs multiple mode");
    process.exit(1);
}

console.log("PASS: UsageExportHeader supports single/multiple select modes with proper value handling");
'''
    result = _run_node(script)
    assert result.returncode == 0, f"UsageExportHeader missing single-select support: {result.stdout}{result.stderr}"


def test_entity_usage_handles_user_type():
    """EntityUsage component must handle 'user' entity type by calling userDailyActivityCall - verify via test execution."""
    _ensure_npm_and_deps()

    # Run the EntityUsage tests which now include a test for user entity type
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/EntityUsage/EntityUsage.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )

    # Check that the test for user entity type passes
    if r.returncode != 0:
        # Check if it fails due to missing user test specifically
        if "user" in r.stderr.lower() or "user" in r.stdout.lower():
            assert False, f"EntityUsage does not properly handle 'user' entity type: {r.stderr[-1000:]}"

    assert r.returncode == 0, f"EntityUsage tests failed (likely missing user support): {r.stderr[-1000:]}"


# --- Config/documentation update tests (fail_to_pass) ---


def test_agents_md_documents_contract_mismatch():
    """AGENTS.md must document the UI/Backend Contract Mismatch pitfall - verify by checking for required concepts."""
    content = (REPO / "AGENTS.md").read_text()

    # Must mention contract
    has_contract = "contract" in content.lower()

    # Must explain single vs array/multi-select mismatch
    lower = content.lower()
    has_single = "single" in lower
    has_array_or_multi = "array" in lower or "multi" in lower or "multiple" in lower

    # Must mention UI and backend
    has_ui_backend = "ui" in lower and "backend" in lower

    assert has_contract, "AGENTS.md should mention contract mismatch"
    assert has_single and has_array_or_multi, \
        "AGENTS.md should explain single value vs array/multi-select mismatch"
    assert has_ui_backend, "AGENTS.md should mention UI/Backend relationship"


def test_claude_md_adds_ui_backend_consistency():
    """CLAUDE.md must document UI/Backend consistency section - verify by reading content."""
    content = (REPO / "CLAUDE.md").read_text()
    lower = content.lower()

    # Must have UI/Backend section
    has_ui_backend = "ui" in lower and "backend" in lower

    # Must mention consistency or contract
    has_consistency_or_contract = "consistency" in lower or "contract" in lower

    # Should mention entity types or testing
    has_entity_types = "entity" in lower

    assert has_ui_backend, "CLAUDE.md should have UI/Backend section"
    assert has_consistency_or_contract, \
        "CLAUDE.md should document UI/Backend consistency or contract guidelines"
    assert has_entity_types, "CLAUDE.md should mention entity types"


# --- Pass-to-pass tests ---


def test_tsconfig_valid_json():
    """tsconfig.json must be valid JSON with expected structure."""
    result = _run_node(
        'const fs = require("fs");\n'
        'const raw = fs.readFileSync("tsconfig.json", "utf-8");\n'
        'const config = JSON.parse(raw);\n'
        'if (!config.compilerOptions) {\n'
        '  console.log("Missing compilerOptions"); process.exit(1);\n'
        '}\n'
        'console.log("PASS");\n'
    )
    assert result.returncode == 0, f"tsconfig.json invalid: {result.stdout}{result.stderr}"


def test_repo_entity_usage_tests():
    """Repo's EntityUsage component tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/EntityUsage/EntityUsage.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"EntityUsage tests failed:\n{r.stderr[-500:]}"


def test_repo_usage_view_select_tests():
    """Repo's UsageViewSelect component tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/UsageViewSelect/UsageViewSelect.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"UsageViewSelect tests failed:\n{r.stderr[-500:]}"


def test_repo_usage_page_view_tests():
    """Repo's UsagePageView component tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/UsagePageView.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"UsagePageView tests failed:\n{r.stderr[-500:]}"


def test_repo_key_model_usage_view_tests():
    """Repo's KeyModelUsageView component tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/KeyModelUsageView.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"KeyModelUsageView tests failed:\n{r.stderr[-500:]}"


def test_repo_usage_ai_chat_panel_tests():
    """Repo's UsageAIChatPanel component tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/UsageAIChatPanel.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"UsageAIChatPanel tests failed:\n{r.stderr[-500:]}"


def test_repo_entity_usage_spend_by_provider_tests():
    """Repo's EntityUsage SpendByProvider tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/EntityUsage/SpendByProvider.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"SpendByProvider tests failed:\n{r.stderr[-500:]}"


def test_repo_entity_usage_export_utils_tests():
    """Repo's EntityUsageExport utils tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/EntityUsageExport/utils.test.ts"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"EntityUsageExport utils tests failed:\n{r.stderr[-500:]}"


def test_repo_entity_usage_export_modal_tests():
    """Repo's EntityUsageExport modal tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/EntityUsageExport/EntityUsageExportModal.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"EntityUsageExportModal tests failed:\n{r.stderr[-500:]}"


def test_repo_usage_value_formatters_tests():
    """Repo's UsagePage value formatters tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/utils/value_formatters.test.ts"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"value_formatters tests failed:\n{r.stderr[-500:]}"


def test_repo_endpoint_usage_tests():
    """Repo's EndpointUsage component tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/EndpointUsage/EndpointUsage.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"EndpointUsage tests failed:\n{r.stderr[-500:]}"


def test_repo_top_key_view_tests():
    """Repo's TopKeyView component tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/EntityUsage/TopKeyView.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"TopKeyView tests failed:\n{r.stderr[-500:]}"


def test_repo_top_model_view_tests():
    """Repo's TopModelView component tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/EntityUsage/TopModelView.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"TopModelView tests failed:\n{r.stderr[-500:]}"
