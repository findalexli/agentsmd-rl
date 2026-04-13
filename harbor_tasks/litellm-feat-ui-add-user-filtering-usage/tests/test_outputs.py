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
    script_path = UI / "_eval_tmp.js"  # Use .js not .mjs to avoid ES module issues
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
    # Enable npm via corepack
    subprocess.run(
        ["corepack", "enable", "npm"],
        capture_output=True, text=True, timeout=30,
        cwd=UI,
    )
    # Install dependencies if node_modules doesn't exist
    if not (UI / "node_modules").exists():
        subprocess.run(
            ["npm", "install", "--legacy-peer-deps"],
            capture_output=True, text=True, timeout=300,
            cwd=UI,
        )


# --- Code behavior tests (fail_to_pass) ---


def test_entity_type_includes_user():
    """EntityType type union must include 'user'."""
    result = _run_node(
        'const fs = require("fs");\n'
        'const content = fs.readFileSync("src/components/EntityUsageExport/types.ts", "utf-8");\n'
        'const match = content.match(/export\\s+type\\s+EntityType\\s*=\\s*([^;]+);/);\n'
        'if (!match) { console.log("EntityType not found"); process.exit(1); }\n'
        'const values = match[1].split("|").map(v => v.trim().replace(/"/g, ""));\n'
        'if (!values.includes("user")) { console.log("user not in EntityType"); process.exit(1); }\n'
        'console.log("PASS");\n'
    )
    assert result.returncode == 0, f"EntityType missing 'user': {result.stdout}{result.stderr}"


def test_usage_view_select_has_user_option():
    """UsageViewSelect must include 'user' as a selectable view option."""
    result = _run_node(
        'const fs = require("fs");\n'
        'const content = fs.readFileSync("src/components/UsagePage/components/UsageViewSelect/UsageViewSelect.tsx", "utf-8");\n'
        'const typeMatch = content.match(/UsageOption\\s*=\\s*([^;]+)/);\n'
        'if (!typeMatch || !typeMatch[1].includes(\'"user"\')) {\n'
        '  console.log("UsageOption type missing user"); process.exit(1);\n'
        '}\n'
        'if (!content.includes(\'value: "user"\')) {\n'
        '  console.log("OPTIONS array missing user entry"); process.exit(1);\n'
        '}\n'
        'console.log("PASS");\n'
    )
    assert result.returncode == 0, f"UsageViewSelect missing user: {result.stdout}{result.stderr}"


def test_export_header_supports_filter_mode():
    """UsageExportHeader must accept filterMode prop for single/multiple select."""
    result = _run_node(
        'const fs = require("fs");\n'
        'const content = fs.readFileSync("src/components/EntityUsageExport/UsageExportHeader.tsx", "utf-8");\n'
        'if (!content.includes("filterMode")) {\n'
        '  console.log("filterMode not found in UsageExportHeader"); process.exit(1);\n'
        '}\n'
        'if (!content.includes("mode={filterMode")) {\n'
        '  console.log("filterMode not wired to Select component"); process.exit(1);\n'
        '}\n'
        'console.log("PASS");\n'
    )
    assert result.returncode == 0, f"UsageExportHeader missing filterMode: {result.stdout}{result.stderr}"


# --- Config/documentation update tests (fail_to_pass) ---


def test_agents_md_documents_contract_mismatch():
    """AGENTS.md must document the UI/Backend Contract Mismatch pitfall."""
    content = (REPO / "AGENTS.md").read_text()
    lower = content.lower()
    assert "contract" in lower, "AGENTS.md should mention contract mismatch"
    assert "single" in lower and ("array" in lower or "multi" in lower), \
        "AGENTS.md should explain single vs array/multi-select mismatch"


def test_claude_md_adds_ui_backend_consistency():
    """CLAUDE.md must document UI/Backend consistency section."""
    content = (REPO / "CLAUDE.md").read_text()
    lower = content.lower()
    assert "ui" in lower and "backend" in lower, \
        "CLAUDE.md should mention UI and backend together"
    assert "consistency" in lower or "contract" in lower, \
        "CLAUDE.md should have UI/Backend consistency or contract section"


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
    _ensure_npm_and_deps()  # Enable npm and install deps
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/EntityUsage/EntityUsage.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"EntityUsage tests failed:\n{r.stderr[-500:]}"


def test_repo_usage_view_select_tests():
    """Repo's UsageViewSelect component tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()  # Enable npm and install deps
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/UsageViewSelect/UsageViewSelect.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"UsageViewSelect tests failed:\n{r.stderr[-500:]}"




def test_repo_usage_page_view_tests():
    """Repo's UsagePageView component tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()  # Enable npm and install deps
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/UsagePageView.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"UsagePageView tests failed:\n{r.stderr[-500:]}"


def test_repo_key_model_usage_view_tests():
    """Repo's KeyModelUsageView component tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()  # Enable npm and install deps
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/KeyModelUsageView.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"KeyModelUsageView tests failed:\n{r.stderr[-500:]}"


def test_repo_usage_ai_chat_panel_tests():
    """Repo's UsageAIChatPanel component tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()  # Enable npm and install deps
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/UsageAIChatPanel.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"UsageAIChatPanel tests failed:\n{r.stderr[-500:]}"


def test_repo_entity_usage_spend_by_provider_tests():
    """Repo's EntityUsage SpendByProvider tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()  # Enable npm and install deps
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/EntityUsage/SpendByProvider.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"SpendByProvider tests failed:\n{r.stderr[-500:]}"
def test_repo_entity_usage_export_utils_tests():
    """Repo's EntityUsageExport utils tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()  # Enable npm and install deps
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/EntityUsageExport/utils.test.ts"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"EntityUsageExport utils tests failed:\n{r.stderr[-500:]}"


def test_repo_entity_usage_export_modal_tests():
    """Repo's EntityUsageExport modal tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()  # Enable npm and install deps
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/EntityUsageExport/EntityUsageExportModal.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"EntityUsageExportModal tests failed:\n{r.stderr[-500:]}"


def test_repo_usage_value_formatters_tests():
    """Repo's UsagePage value formatters tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()  # Enable npm and install deps
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/utils/value_formatters.test.ts"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"value_formatters tests failed:\n{r.stderr[-500:]}"


def test_repo_endpoint_usage_tests():
    """Repo's EndpointUsage component tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()  # Enable npm and install deps
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/EndpointUsage/EndpointUsage.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"EndpointUsage tests failed:\n{r.stderr[-500:]}"


def test_repo_top_key_view_tests():
    """Repo's TopKeyView component tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()  # Enable npm and install deps
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/EntityUsage/TopKeyView.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"TopKeyView tests failed:\n{r.stderr[-500:]}"


def test_repo_top_model_view_tests():
    """Repo's TopModelView component tests pass (pass_to_pass)."""
    _ensure_npm_and_deps()  # Enable npm and install deps
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run",
         "src/components/UsagePage/components/EntityUsage/TopModelView.test.tsx"],
        capture_output=True, text=True, timeout=600,
        cwd=UI,
    )
    assert r.returncode == 0, f"TopModelView tests failed:\n{r.stderr[-500:]}"
