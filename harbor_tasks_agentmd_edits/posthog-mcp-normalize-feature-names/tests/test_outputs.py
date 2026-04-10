"""
Task: posthog-mcp-normalize-feature-names
Repo: PostHog/posthog @ 283294a8e1c595e5762fa55a8d18b844c4667f2c
PR:   51901

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/posthog"
MCP = f"{REPO}/services/mcp"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """JSON schema files must be valid JSON."""
    for name in [
        "tool-definitions.json",
        "tool-definitions-all.json",
        "tool-definitions-v2.json",
    ]:
        p = Path(MCP) / "schema" / name
        data = json.loads(p.read_text())
        assert isinstance(data, dict), f"{name} should be a JSON object"


# ---------------------------------------------------------------------------
# Fail-to-pass (behavioral) — schema normalization
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass
def test_schema_feature_names_use_underscores():
    """All feature fields in schema JSON files must use underscores, not hyphens."""
    r = _run_node("""
const fs = require('fs');
const files = [
    'services/mcp/schema/tool-definitions.json',
    'services/mcp/schema/tool-definitions-all.json',
    'services/mcp/schema/tool-definitions-v2.json',
];
const bad = new Set(['error-tracking', 'llm-analytics', 'data-schema']);
const violations = [];
for (const f of files) {
    const data = JSON.parse(fs.readFileSync(f, 'utf8'));
    for (const [tool, defn] of Object.entries(data)) {
        if (bad.has(defn.feature)) {
            violations.push(f + ': ' + tool + ' has "' + defn.feature + '"');
        }
    }
}
if (violations.length > 0) {
    console.error('Hyphenated features found:\\n' + violations.join('\\n'));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Schema has hyphenated features:\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_feature_filtering_normalizes_hyphens():
    """Feature filtering normalizes hyphens to underscores so both conventions match."""
    r = _run_node(r"""
const fs = require('fs');

// Load the tool definitions and the filtering source
const defs = JSON.parse(fs.readFileSync('services/mcp/schema/tool-definitions-all.json', 'utf8'));
const src = fs.readFileSync('services/mcp/src/tools/toolDefinitions.ts', 'utf8');

// 1. The source must NOT use the broken direct-includes pattern
if (src.includes('features.includes(definition.feature)')) {
    console.error('FAIL: Still using direct features.includes(definition.feature)');
    process.exit(1);
}

// 2. The source must have normalization logic (replace hyphens with underscores)
const hasNormalize = /replace\s*\(\s*\/-\/g/.test(src) || /replace\s*\(\s*['"]-(All)?\s*['"]/.test(src);
if (!hasNormalize) {
    console.error('FAIL: No hyphen-to-underscore normalization in toolDefinitions.ts');
    process.exit(1);
}

// 3. Simulate filtering: both "error-tracking" and "error_tracking" should match same tools
const normalize = (n) => n.replace(/-/g, '_');
const getTools = (features) => {
    const nf = new Set(features.map(normalize));
    return Object.entries(defs)
        .filter(([_, d]) => d.feature && nf.has(normalize(d.feature)))
        .map(([name]) => name)
        .sort();
};

const hyphenResult = getTools(['error-tracking']);
const underscoreResult = getTools(['error_tracking']);

if (hyphenResult.length === 0) {
    console.error('FAIL: No tools found for error-tracking / error_tracking');
    process.exit(1);
}
if (JSON.stringify(hyphenResult) !== JSON.stringify(underscoreResult)) {
    console.error('FAIL: Hyphen and underscore queries return different results');
    process.exit(1);
}

console.log('PASS: ' + hyphenResult.length + ' tools matched for error_tracking');
""")
    assert r.returncode == 0, f"Feature filtering broken:\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — README documentation update
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readme_documents_all_features():
    """README.md must document all available MCP features, not just a subset."""
    readme = Path(f"{MCP}/README.md").read_text()
    missing = []
    for feat in [
        "data_schema", "data_warehouse", "error_tracking", "hog_functions",
        "llm_analytics", "prompts", "notebooks", "persons", "surveys",
        "annotations", "cohorts", "alerts", "early_access_features",
    ]:
        if feat not in readme:
            missing.append(feat)
    assert not missing, (
        f"README.md is missing documentation for features: {missing}. "
        f"All 28 available features should be documented."
    )


# [pr_diff] fail_to_pass
def test_readme_hyphen_underscore_equivalence_note():
    """README.md must note that hyphens and underscores are treated as equivalent."""
    readme = Path(f"{MCP}/README.md").read_text().lower()
    has_equivalence = (
        ("hyphen" in readme and "underscore" in readme)
        or ("equivalent" in readme and ("hyphen" in readme or "underscore" in readme))
    )
    assert has_equivalence, (
        "README.md should note that hyphens and underscores are equivalent "
        "in feature names for backward compatibility"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repo CI tests
# ---------------------------------------------------------------------------

def _ensure_pnpm():
    """Ensure pnpm is installed and available."""
    # Check if pnpm is already installed
    r = subprocess.run(["which", "pnpm"], capture_output=True, text=True)
    if r.returncode == 0:
        return
    # Install pnpm globally
    r = subprocess.run(["npm", "install", "-g", "pnpm"], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"Failed to install pnpm: {r.stderr}")


def _install_mcp_deps():
    """Install MCP dependencies if not already installed."""
    # Check if node_modules exists in MCP
    if Path(f"{MCP}/node_modules").exists():
        return
    # Install dependencies
    r = subprocess.run(
        ["pnpm", "--filter=@posthog/mcp", "install", "--frozen-lockfile"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Failed to install MCP deps: {r.stderr[-500:]}")


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's MCP unit tests pass (pass_to_pass)."""
    _ensure_pnpm()
    _install_mcp_deps()
    r = subprocess.run(
        ["pnpm", "test", "--", "--run"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=MCP,
    )
    assert r.returncode == 0, f"MCP unit tests failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_tool_filtering_tests():
    """Repo's tool-filtering unit tests pass (pass_to_pass) — most relevant to this PR."""
    _ensure_pnpm()
    _install_mcp_deps()
    r = subprocess.run(
        ["pnpm", "test", "--", "--run", "tests/unit/tool-filtering.test.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=MCP,
    )
    assert r.returncode == 0, f"Tool filtering tests failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_tool_names():
    """Repo's lint-tool-names check passes (pass_to_pass)."""
    _ensure_pnpm()
    _install_mcp_deps()
    r = subprocess.run(
        ["pnpm", "lint-tool-names"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=MCP,
    )
    assert r.returncode == 0, f"lint-tool-names failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_tool_definitions_structure():
    """Tool definitions have required fields (feature, category, description)."""
    p = Path(MCP) / "schema" / "tool-definitions.json"
    data = json.loads(p.read_text())
    for tool_name, defn in data.items():
        assert "feature" in defn, f"{tool_name} missing 'feature' field"
        assert "category" in defn, f"{tool_name} missing 'category' field"
        assert "description" in defn, f"{tool_name} missing 'description' field"
