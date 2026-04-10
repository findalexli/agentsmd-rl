"""
Task: playwright-chore-add-playwrightcli-config
Repo: microsoft/playwright @ 71e5079b735eda08a72b0fac58a3dd02fde6bb9f
PR:   38971

Adds a `config` command to playwright-cli that restarts a session with
a new configuration file.  Updates SKILL.md to document the command.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
COMMAND_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/command.ts"
COMMANDS_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/commands.ts"
HELP_GEN_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/helpGenerator.ts"
PROGRAM_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/program.ts"
BROWSER_CONFIG_TS = Path(REPO) / "packages/playwright/src/mcp/browser/config.ts"
SKILL_MD = Path(REPO) / "packages/playwright/src/mcp/terminal/SKILL.md"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a JavaScript snippet via Node in the repo directory."""
    tmp = Path(REPO) / "_eval_tmp.cjs"  # Use .cjs for CommonJS mode
    tmp.write_text(script)
    try:
        return subprocess.run(
            ["node", str(tmp)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structural checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files have balanced braces and are non-empty."""
    for ts_file in [COMMAND_TS, COMMANDS_TS, HELP_GEN_TS, PROGRAM_TS, BROWSER_CONFIG_TS]:
        content = ts_file.read_text()
        assert len(content) > 200, f"{ts_file.name}: file too short"
        assert content.count("{") == content.count("}"), \
            f"Unbalanced braces in {ts_file.name}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) — Repo CI tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint_packages():
    """Repo workspace packages are consistent (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"lint-packages failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ts_syntax():
    """Modified TypeScript files have valid syntax (balanced braces/parens) (pass_to_pass)."""
    script = """
const fs = require('fs');
const files = [
  'packages/playwright/src/mcp/terminal/command.ts',
  'packages/playwright/src/mcp/terminal/commands.ts',
  'packages/playwright/src/mcp/terminal/helpGenerator.ts',
  'packages/playwright/src/mcp/terminal/program.ts',
  'packages/playwright/src/mcp/browser/config.ts'
];
let allOk = true;
for (const f of files) {
  const src = fs.readFileSync(f, 'utf8');
  const open = (src.match(/\\{/g) || []).length;
  const close = (src.match(/\\}/g) || []).length;
  const openParen = (src.match(/\\(/g) || []).length;
  const closeParen = (src.match(/\\)/g) || []).length;
  if (open !== close || openParen !== closeParen) {
    console.log('FAIL: ' + f + ' braces: ' + open + '/' + close + ', parens: ' + openParen + '/' + closeParen);
    allOk = false;
  }
}
process.exit(allOk ? 0 : 1);
"""
    tmp = Path(REPO) / "_syntax_check.cjs"  # Use .cjs for CommonJS mode
    tmp.write_text(script)
    try:
        r = subprocess.run(
            ["node", str(tmp)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"TypeScript syntax check failed:\n{r.stdout}\n{r.stderr}"
    finally:
        tmp.unlink(missing_ok=True)


# [repo_tests] pass_to_pass
def test_repo_package_json_valid():
    """package.json files are valid JSON (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "JSON.parse(require('fs').readFileSync('package.json', 'utf8')); console.log('OK');"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Root package.json invalid:\n{r.stderr}"

    r = subprocess.run(
        ["node", "-e", "JSON.parse(require('fs').readFileSync('packages/playwright/package.json', 'utf8')); console.log('OK');"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Playwright package.json invalid:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_config_category_in_type():
    """command.ts Category union type must include 'config'."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright/src/mcp/terminal/command.ts', 'utf8');
// Extract the Category type definition line
const match = src.match(/export type Category\\s*=\\s*([^;]+);/);
if (!match) { console.error('Category type not found'); process.exit(1); }
const typeBody = match[1];
const categories = [...typeBody.matchAll(/'([^']+)'/g)].map(m => m[1]);
console.log(JSON.stringify({ categories }));
if (!categories.includes('config')) {
    console.error('config not in Category type');
    process.exit(1);
}
""")
    assert r.returncode == 0, f"config not in Category type:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "config" in data["categories"], \
        f"'config' missing from Category: {data['categories']}"


# [pr_diff] fail_to_pass
def test_config_command_declared():
    """commands.ts must declare a config command with category 'config'."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright/src/mcp/terminal/commands.ts', 'utf8');
// Check for the config command declaration block
const hasDecl = /declareCommand\\(\\{[^}]*name:\\s*'config'/.test(src);
const hasCat = /declareCommand\\(\\{[^}]*category:\\s*'config'/.test(src);
// Check the commandsArray includes config
const inArray = /\\/\\/ config[\\s\\S]{0,40}config,/.test(src);
console.log(JSON.stringify({ hasDecl, hasCat, inArray }));
if (!hasDecl || !hasCat || !inArray) process.exit(1);
""")
    assert r.returncode == 0, f"config command not declared properly:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["hasDecl"], "Missing config command declaration"
    assert data["hasCat"], "Config command missing category: 'config'"
    assert data["inArray"], "Config command not added to commandsArray"


# [pr_diff] fail_to_pass
def test_help_has_configuration_category():
    """helpGenerator.ts must include a 'Configuration' category entry."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright/src/mcp/terminal/helpGenerator.ts', 'utf8');
// Extract the categories array entries
const matches = [...src.matchAll(/\\{\\s*name:\\s*'(\\w+)',\\s*title:\\s*'([^']+)'\\s*\\}/g)];
const cats = matches.map(m => ({ name: m[1], title: m[2] }));
console.log(JSON.stringify({ cats }));
const hasConfig = cats.some(c => c.name === 'config' && c.title === 'Configuration');
if (!hasConfig) {
    console.error('Configuration category not found in helpGenerator');
    process.exit(1);
}
""")
    assert r.returncode == 0, f"Configuration category missing from help:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    config_cats = [c for c in data["cats"] if c["name"] == "config"]
    assert len(config_cats) == 1, f"Expected 1 config category, got {len(config_cats)}"
    assert config_cats[0]["title"] == "Configuration"


# [pr_diff] fail_to_pass
def test_configure_method_logic():
    """program.ts must have a configure() method that stops existing session and reconnects."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright/src/mcp/terminal/program.ts', 'utf8');

// Extract the configure method body
const configureMatch = src.match(/async configure\\(args[^)]*\\)[^{]*\\{([\\s\\S]*?)\\n  \\}/);
if (!configureMatch) {
    console.error('configure method not found');
    process.exit(1);
}
const body = configureMatch[1];
const checks = {
    resolvesSession: body.includes('_resolveSessionName'),
    checksConnection: body.includes('_canConnect'),
    stopsOld: body.includes('.stop()'),
    updatesConfig: body.includes('this._options.config'),
    reconnects: body.includes('_connect'),
};
console.log(JSON.stringify(checks));
const allPassed = Object.values(checks).every(v => v);
if (!allPassed) process.exit(1);
""")
    assert r.returncode == 0, f"configure() method missing or incomplete:\n{r.stderr}"
    checks = json.loads(r.stdout.strip())
    assert checks["resolvesSession"], "configure must resolve session name"
    assert checks["checksConnection"], "configure must check if session is connectable"
    assert checks["stopsOld"], "configure must stop existing session"
    assert checks["updatesConfig"], "configure must update config option"
    assert checks["reconnects"], "configure must reconnect with new config"


# [pr_diff] fail_to_pass
def test_config_command_routing():
    """program.ts must route the 'config' command to the session handler."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright/src/mcp/terminal/program.ts', 'utf8');

// Check that 'config' is handled in the main program routing
const hasConfigRoute = /commandName\\s*===\\s*'config'/.test(src);
// Check that handleSessionCommand receives 'config' as subcommand
const passesConfig = /handleSessionCommand\\(sessionManager,\\s*'config'/.test(src);
// Check that handleSessionCommand dispatches config to configure()
const dispatchesConfig = /subcommand\\s*===\\s*'config'[\\s\\S]*?\\.configure\\(/.test(src);

console.log(JSON.stringify({ hasConfigRoute, passesConfig, dispatchesConfig }));
if (!hasConfigRoute || !passesConfig || !dispatchesConfig) process.exit(1);
""")
    assert r.returncode == 0, f"config routing missing:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["hasConfigRoute"], "program.ts must check commandName === 'config'"
    assert data["passesConfig"], "Must pass 'config' to handleSessionCommand"
    assert data["dispatchesConfig"], "handleSessionCommand must dispatch config to configure()"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update test (REQUIRED)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_documents_config():
    """SKILL.md must document the config command with usage examples."""
    content = SKILL_MD.read_text()

    # Must have a Configuration section header
    assert "### Configuration" in content, \
        "SKILL.md should have a '### Configuration' section"

    # Must document the config command usage
    assert "playwright-cli config" in content, \
        "SKILL.md should show 'playwright-cli config' usage"

    # Must show how to use with a named session
    assert "--session=" in content and "config" in content, \
        "SKILL.md should document config with named sessions"

    # Must document --config flag for open command
    assert "--config=" in content, \
        "SKILL.md should document the --config flag"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — viewport defaults in daemon config
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_daemon_config_has_viewport():
    """browser/config.ts daemon config must set contextOptions with viewport."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright/src/mcp/browser/config.ts', 'utf8');

const hasContextOptions = /contextOptions/.test(src);
const hasViewport = /viewport.*width.*1280.*height.*720/.test(src);
console.log(JSON.stringify({ hasContextOptions, hasViewport }));
if (!hasContextOptions || !hasViewport) process.exit(1);
""")
    assert r.returncode == 0, f"Daemon config missing viewport:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["hasContextOptions"], "config.ts must have contextOptions"
    assert data["hasViewport"], "config.ts must set default viewport 1280x720"
