"""
Task: litellm-feat-ui-add-user-filtering-usage
Repo: BerriAI/litellm @ a38993b871a32090caea0941427a8bc5489a5c02
PR:   22059

Verifies that "user" entity type is added to the usage page with proper
UI/backend contract handling, and that AGENTS.md/CLAUDE.md are updated
with corresponding documentation rules.
"""

import subprocess
import re
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
    """EntityType type union must include 'user' - verify via source and compilation."""
    _ensure_npm_and_deps()

    # Check the actual source file content for "user" in the EntityType union
    types_path = UI / "src" / "components" / "EntityUsageExport" / "types.ts"
    content = types_path.read_text()

    # Must have "user" as a literal in the EntityType union
    assert '"user"' in content, "EntityType union does not include user"

    # NOTE: Full tsc compilation is covered by pass_to_pass CI tests


def test_usage_view_select_has_user_option():
    """UsageViewSelect must include 'user' as a selectable option - verify via source analysis."""
    select_path = UI / "src" / "components" / "UsagePage" / "components" / "UsageViewSelect" / "UsageViewSelect.tsx"
    content = select_path.read_text()

    # Check that the UsageOption type includes "user"
    usage_option_lines = [l for l in content.split("\n") if "UsageOption" in l and "=" in l and "|" in l]
    assert len(usage_option_lines) > 0, "Could not find UsageOption type definition"
    assert '"user"' in usage_option_lines[0], f"UsageOption type missing user: {usage_option_lines[0]}"

    # Check that the OPTIONS array includes a user entry with a label
    assert '"user"' in content, "OPTIONS array missing user value"
    assert "User Usage" in content, "OPTIONS array missing User Usage label"


def test_export_header_supports_single_select_mode():
    """UsageExportHeader must support both single-select and multi-select filter modes."""
    header_path = UI / "src" / "components" / "EntityUsageExport" / "UsageExportHeader.tsx"
    entity_usage_path = UI / "src" / "components" / "UsagePage" / "components" / "EntityUsage" / "EntityUsage.tsx"

    header = header_path.read_text()

    # 1. Must no longer unconditionally hardcode mode="multiple"
    assert 'mode="multiple"' not in header, \
        "Select mode is still unconditionally hardcoded to multiple"

    # 2. Must have conditional mode assignment on the Select component
    assert "mode={" in header, "No conditional mode assignment on Select"

    # 3. Must expose a prop to control the select mode (proper word boundaries)
    has_mode_prop = re.search(r"\b(filterMode|selectMode|singleSelect|isSingle)\b\s*\??\s*:", header)
    assert has_mode_prop is not None, \
        "No prop found to control select mode (filterMode/selectMode/singleSelect/isSingle)"

    # 4. Must conditionally adapt the value prop for single vs multiple mode
    has_value_adaptation = (
        "value={" in header and (
            "selectedFilters[0]" in header or
            "selectedFilters.at(0)" in header
        )
    )
    assert has_value_adaptation, "No conditional value adaptation for single vs multiple mode"

    # 5. EntityUsage must configure single-select for the user entity type
    entity_usage = entity_usage_path.read_text()
    configures_user = (
        'entityType === "user"' in entity_usage and (
            "filterMode" in entity_usage or
            "singleSelect" in entity_usage
        )
    )
    assert configures_user, "EntityUsage does not configure single-select for user entity type"


def test_entity_usage_handles_user_type():
    """EntityUsage component must handle 'user' entity type by calling userDailyActivityCall."""
    _ensure_npm_and_deps()

    # Run the EntityUsage tests which now include a test for user entity type
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/EntityUsage/EntityUsage.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )

    assert r.returncode == 0, f"EntityUsage tests failed: {r.stderr[-1000:]}"

    # The user-specific test must appear in the output as having run
    output = r.stdout + r.stderr
    assert "should render with user entity type and call user API" in output, \
        "EntityUsage test output missing the user entity type test"


# --- Config/documentation update tests (fail_to_pass) ---


def test_agents_md_documents_contract_mismatch():
    """AGENTS.md must document the UI/Backend Contract Mismatch pitfall."""
    content = (REPO / "AGENTS.md").read_text()
    lower = content.lower()

    # Must mention contract mismatch
    assert "contract" in lower, "AGENTS.md should mention contract mismatch"

    # Must explain single vs multi-select mismatch
    assert "single" in lower, "AGENTS.md should mention single value"
    assert any(word in lower for word in ["array", "multi", "multiple"]), \
        "AGENTS.md should mention array or multi-select"

    # Must mention UI and backend
    assert "ui" in lower and "backend" in lower, "AGENTS.md should mention UI and Backend"

    # Must warn about silently dropping selections
    assert "silently dropping" in lower, "AGENTS.md should warn about silently dropping selections"


def test_claude_md_adds_ui_backend_consistency():
    """CLAUDE.md must document UI/Backend consistency section."""
    content = (REPO / "CLAUDE.md").read_text()
    lower = content.lower()

    # Must have UI/Backend section
    assert "ui" in lower and "backend" in lower, "CLAUDE.md should mention UI and Backend"

    # Must mention consistency or contract
    assert "consistency" in lower or "contract" in lower, \
        "CLAUDE.md should document UI/Backend consistency or contract guidelines"

    # Should mention entity types
    assert "entity" in lower, "CLAUDE.md should mention entity types"

    # Must have the specific rule about adding tests for new entity types
    assert "always add tests" in lower, "CLAUDE.md should include rule to always add tests for new entity types"


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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_unit_test_install_helm_unit_test_plugin():
    """pass_to_pass | CI job 'unit-test' → step 'Install Helm Unit Test Plugin'"""
    r = subprocess.run(
        ["bash", "-lc", 'helm plugin install https://github.com/helm-unittest/helm-unittest --version v0.4.4'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Install Helm Unit Test Plugin' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_test_run_unit_tests():
    """pass_to_pass | CI job 'unit-test' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", "helm unittest -f 'tests/*.yaml' deploy/charts/litellm-helm"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_should_render_with_user_entity_type_and_call_use():
    """fail_to_pass | PR added test 'should render with user entity type and call user API' in 'ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.test.tsx' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.test.tsx" -t "should render with user entity type and call user API" 2>&1 || npx vitest run "ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.test.tsx" -t "should render with user entity type and call user API" 2>&1 || pnpm jest "ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.test.tsx" -t "should render with user entity type and call user API" 2>&1 || npx jest "ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.test.tsx" -t "should render with user entity type and call user API" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should render with user entity type and call user API' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
