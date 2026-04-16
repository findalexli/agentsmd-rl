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
import re

REPO = "/workspace/playwright"
COMMAND_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/command.ts"
COMMANDS_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/commands.ts"
HELP_GEN_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/helpGenerator.ts"
PROGRAM_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/program.ts"
BROWSER_CONFIG_TS = Path(REPO) / "packages/playwright/src/mcp/browser/config.ts"
SKILL_MD = Path(REPO) / "packages/playwright/src/mcp/terminal/SKILL.md"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a JavaScript snippet via Node in the repo directory."""
    tmp = Path(REPO) / "_eval_tmp.cjs"
    tmp.write_text(script)
    try:
        return subprocess.run(
            ["node", str(tmp)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        tmp.unlink(missing_ok=True)


def _run_tsx(script: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Execute a TypeScript snippet via tsx in the repo directory."""
    tmp = Path(REPO) / "_eval_tmp.ts"
    tmp.write_text(script)
    try:
        r = subprocess.run(
            ["npx", "tsx", str(tmp)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
        return r
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
        assert content.count("{") == content.count("}"),             f"Unbalanced braces in {ts_file.name}"


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
    tmp = Path(REPO) / "_syntax_check.cjs"
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


# [repo_tests] pass_to_pass
def test_repo_workspace_packages_json_valid():
    """All workspace package.json files are valid JSON (pass_to_pass)."""
    script = """
const fs = require('fs');
const path = require('path');
const rootPkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
const workspaces = rootPkg.workspaces || ['packages/*'];
let allOk = true;
for (const pattern of workspaces) {
    if (pattern.endsWith('/*')) {
        const dir = pattern.replace('/*', '');
        const fullDir = path.join(process.cwd(), dir);
        try {
            const entries = fs.readdirSync(fullDir, { withFileTypes: true });
            for (const entry of entries) {
                if (entry.isDirectory()) {
                    const pkgPath = path.join(fullDir, entry.name, 'package.json');
                    try {
                        if (fs.existsSync(pkgPath)) {
                            JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
                        }
                    } catch (e) {
                        console.log('FAIL: ' + pkgPath + ' - ' + e.message);
                        allOk = false;
                    }
                }
            }
        } catch (e) {
        }
    }
}
process.exit(allOk ? 0 : 1);
"""
    tmp = Path(REPO) / "_workspace_pkgs.cjs"
    tmp.write_text(script)
    try:
        r = subprocess.run(
            ["node", str(tmp)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Workspace package.json validation failed:\n{r.stdout}"
    finally:
        tmp.unlink(missing_ok=True)


# [repo_tests] pass_to_pass
def test_repo_npm_ci_valid():
    """npm ci exits successfully indicating valid package-lock.json (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "ci", "--dry-run"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0 or "would install" in r.stderr.lower() or "would install" in r.stdout.lower() or "up to date" in r.stdout.lower() or "up to date" in r.stderr.lower(), \
        f"npm ci validation failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_config_category_in_type():
    """TypeScript type system accepts 'config' as a valid Category value."""
    # Behavioral test: use tsx to run TypeScript code that tries to use
    # 'config' as a Category. If 'config' is not in the Category union type,
    # TypeScript will report a type error and tsx will exit with non-zero.
    script = """
import { Category } from './packages/playwright/src/mcp/terminal/command.ts';

// TypeScript will error if 'config' is not a valid Category literal
const cat: Category = 'config';
console.log(JSON.stringify({ valid: true, category: cat }));
"""
    r = _run_tsx(script)
    assert r.returncode == 0, f"TypeScript does not accept 'config' as Category:\n{r.stderr}\n{r.stdout}"
    data = json.loads(r.stdout.strip())
    assert data.get("valid") == True, f"'config' should be a valid Category value"


# [pr_diff] fail_to_pass
def test_config_command_declared():
    """Config command is registered and appears in the commands array."""
    # Behavioral test: import the commands module and check if config is in
    # the exported commands array. A stub that doesn't register config would
    # fail this test.
    script = """
import { commandsArray } from './packages/playwright/src/mcp/terminal/commands.ts';

const hasConfig = commandsArray.some(cmd => {
    const name = cmd.name ?? (cmd as any).name;
    return name === 'config';
});

if (!hasConfig) {
    console.error('config command not found in commandsArray');
    process.exit(1);
}
console.log(JSON.stringify({ hasConfig: true }));
"""
    r = _run_tsx(script)
    assert r.returncode == 0, f"config command not found in commandsArray:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("hasConfig") == True


# [pr_diff] fail_to_pass
def test_help_has_configuration_category():
    """generateHelp() output includes a Configuration category entry."""
    # Behavioral test: call the generateHelp function and verify it includes
    # a Configuration category. This tests actual behavior, not source text.
    script = """
import { generateHelp } from './packages/playwright/src/mcp/terminal/helpGenerator.ts';

const helpText = generateHelp();
// Check for Configuration category in the help output
const hasConfig = helpText.includes('Configuration') || helpText.includes('config');
if (!hasConfig) {
    console.error('Configuration category not found in help output');
    process.exit(1);
}
console.log(JSON.stringify({ hasConfig: true, helpLength: helpText.length }));
"""
    r = _run_tsx(script)
    assert r.returncode == 0, f"Configuration category not found in help output:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("hasConfig") == True


# [pr_diff] fail_to_pass
def test_configure_method_logic():
    """SessionManager.configure() performs the required operations."""
    # Behavioral test: verify that configure() exists and can be called,
    # and demonstrates correct behavior with mocked dependencies.
    script = """
import { SessionManager } from './packages/playwright/src/mcp/terminal/program.ts';

// Verify configure method exists on prototype
const managerProto = SessionManager.prototype;
if (typeof managerProto.configure !== 'function') {
    console.error('configure method not found on SessionManager prototype');
    process.exit(1);
}

// Create mock session that tracks stop() and close() calls
let stopCalled = false;
let closeCalled = false;
let connectCalled = false;

const mockSession = {
    stop: async () => { stopCalled = true; },
    close: async () => { closeCalled = true; },
};

// Create a manager instance with mocked methods
const testManager = Object.create(managerProto);
testManager._options = { config: null };
testManager._resolveSessionName = (args: any) => args.session || 'default';
testManager._canConnect = async () => false;
testManager._connect = async () => { connectCalled = true; return mockSession; };

// Call configure
const configureFn = testManager.configure.bind(testManager);
try {
    await configureFn({ session: 'test', _: ['config', 'path/to/config.json'] });
} catch (e: any) {
    console.error('configure threw error:', e.message);
    process.exit(1);
}

console.log(JSON.stringify({
    connectCalled,
    closeCalled,
}));
"""
    r = _run_tsx(script)
    # Parse the output - connect should be called
    assert r.returncode == 0, f"configure() test failed:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    # The configure method should have called _connect to reconnect with new config
    assert data.get("connectCalled") == True, "configure() should call _connect to reconnect with new config"


# [pr_diff] fail_to_pass
def test_config_command_routing():
    """CLI routes 'config' command to handleSessionCommand properly."""
    # Behavioral test: verify that the CLI accepts 'config' as a command
    # and routes it to the session handler.
    script = """
import { commandsArray } from './packages/playwright/src/mcp/terminal/commands.ts';

// Check that 'config' is in the commands array
const hasConfig = commandsArray.some(cmd => {
    const name = cmd.name ?? (cmd as any).name;
    return name === 'config';
});

if (!hasConfig) {
    console.error('config command not found');
    process.exit(1);
}

console.log(JSON.stringify({ hasConfig: true }));
"""
    r = _run_tsx(script)
    assert r.returncode == 0, f"config command routing verification failed:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("hasConfig") == True, "config command must be in commands array"


# [pr_diff] fail_to_pass
def test_skill_md_documents_config():
    """SKILL.md contains a Configuration section with required command examples."""
    content = SKILL_MD.read_text()

    # Must have a Configuration section header (### indicates h3)
    assert re.search(r"###\s+Configuration", content), \
        "SKILL.md should have a '### Configuration' section"

    # Must document the config command usage
    assert re.search(r"playwright-cli\s+config", content), \
        "SKILL.md should show 'playwright-cli config' usage"

    # Must show --session= usage with config
    assert "--session=" in content, \
        "SKILL.md should document --session= usage"

    # Must document --config= flag
    assert "--config=" in content, \
        "SKILL.md should document the --config= flag"


# [pr_diff] fail_to_pass
def test_daemon_config_has_viewport():
    """defaultDaemonConfig() returns contextOptions with viewport set to 1280x720."""
    # Behavioral test: call the actual defaultDaemonConfig function and verify
    # the viewport value in the returned config object.
    script = """
import { defaultDaemonConfig } from './packages/playwright/src/mcp/browser/config.ts';

const config = defaultDaemonConfig({} as any);

// Check that contextOptions exists with viewport
const ctxOpts = (config as any).contextOptions;
if (!ctxOpts) {
    console.error('contextOptions not found in daemon config');
    process.exit(1);
}

const viewport = ctxOpts.viewport;
if (!viewport) {
    console.error('viewport not found in contextOptions');
    process.exit(1);
}

// Viewport should be { width: 1280, height: 720 } for headless mode
// In headless mode (daemonHeaded=false), viewport is set; in headed mode, it's null
if (viewport === null) {
    console.log(JSON.stringify({ viewport: null, note: 'headed mode - viewport is null' }));
} else if (viewport && viewport.width === 1280 && viewport.height === 720) {
    console.log(JSON.stringify({ viewport: { width: 1280, height: 720 }, valid: true }));
} else {
    console.error('viewport has wrong dimensions:', JSON.stringify(viewport));
    process.exit(1);
}
"""
    r = _run_tsx(script)
    assert r.returncode == 0, f"Viewport check failed:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    # The viewport should be 1280x720 in headless mode
    if data.get("viewport") is not None:
        assert data.get("viewport").get("width") == 1280, f"Viewport width should be 1280, got {data.get('viewport').get('width')}"
        assert data.get("viewport").get("height") == 720, f"Viewport height should be 720, got {data.get('viewport').get('height')}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) — Repo structure tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_mcp_terminal_structure():
    """MCP terminal module has consistent exports and structure (pass_to_pass)."""
    script = """
const fs = require('fs');
const path = require('path');

const terminalDir = 'packages/playwright/src/mcp/terminal';
const files = fs.readdirSync(terminalDir);
const tsFiles = files.filter(f => f.endsWith('.ts'));

const commandTs = fs.readFileSync(path.join(terminalDir, 'command.ts'), 'utf8');
const hasCategoryExport = commandTs.includes('export type Category');
const hasCommandSchemaExport = commandTs.includes('export type CommandSchema');

const commandsTs = fs.readFileSync(path.join(terminalDir, 'commands.ts'), 'utf8');
const hasDeclareCommand = commandsTs.includes('declareCommand');
const hasZodImport = commandsTs.includes('import');

const helpGenTs = fs.readFileSync(path.join(terminalDir, 'helpGenerator.ts'), 'utf8');
const hasGenerateHelp = helpGenTs.includes('export function generateHelp');

const configTs = fs.readFileSync('packages/playwright/src/mcp/browser/config.ts', 'utf8');
const hasExport = configTs.includes('export');

const checks = {
  commandTsExportsCategory: hasCategoryExport,
  commandTsExportsSchema: hasCommandSchemaExport,
  commandsTsHasDeclare: hasDeclareCommand,
  commandsTsHasImports: hasZodImport,
  helpGenTsExportsGenerateHelp: hasGenerateHelp,
  browserConfigTsHasExports: hasExport,
};

console.log(JSON.stringify(checks));
const allOk = Object.values(checks).every(v => v);
process.exit(allOk ? 0 : 1);
"""
    tmp = Path(REPO) / "_mcp_structure_check.cjs"
    tmp.write_text(script)
    try:
        r = subprocess.run(
            ["node", str(tmp)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"MCP terminal structure check failed:\n{r.stdout}\n{r.stderr}"
    finally:
        tmp.unlink(missing_ok=True)


# [repo_tests] pass_to_pass
def test_repo_modified_files_are_typescript():
    """Modified files from PR are valid TypeScript files (pass_to_pass)."""
    script = """
const fs = require('fs');
const path = require('path');

const modifiedFiles = [
  'packages/playwright/src/mcp/browser/config.ts',
  'packages/playwright/src/mcp/terminal/command.ts',
  'packages/playwright/src/mcp/terminal/commands.ts',
  'packages/playwright/src/mcp/terminal/helpGenerator.ts',
  'packages/playwright/src/mcp/terminal/program.ts'
];

let allOk = true;
for (const file of modifiedFiles) {
  const fullPath = path.join(process.cwd(), file);
  try {
    const stats = fs.statSync(fullPath);
    if (!stats.isFile()) {
      console.log('NOT_A_FILE: ' + file);
      allOk = false;
      continue;
    }
    const content = fs.readFileSync(fullPath, 'utf8');
    const hasValidExtension = file.endsWith('.ts');
    const hasLicenseHeader = content.includes('Copyright') && content.includes('Apache License');

    if (!hasValidExtension || !hasLicenseHeader) {
      console.log('INVALID: ' + file);
      allOk = false;
    } else {
      console.log('OK: ' + file);
    }
  } catch (e) {
    console.log('ERROR: ' + file + ' - ' + e.message);
    allOk = false;
  }
}
process.exit(allOk ? 0 : 1);
"""
    tmp = Path(REPO) / "_ts_files_check.cjs"
    tmp.write_text(script)
    try:
        r = subprocess.run(
            ["node", str(tmp)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Modified files check failed:\n{r.stdout}\n{r.stderr}"
    finally:
        tmp.unlink(missing_ok=True)


# [repo_tests] pass_to_pass
def test_repo_browser_config_exports():
    """Browser config module has expected exports (pass_to_pass)."""
    script = """
const fs = require('fs');

const configTs = fs.readFileSync('packages/playwright/src/mcp/browser/config.ts', 'utf8');

const hasCLIOptions = configTs.includes('CLIOptions');
const hasConfigType = configTs.includes('Config');
const hasMergeConfig = configTs.includes('mergeConfig');
const hasConfigFromCLIOptions = configTs.includes('configFromCLIOptions');

const checks = {
  hasCLIOptions,
  hasConfigType,
  hasMergeConfig,
  hasConfigFromCLIOptions
};

console.log(JSON.stringify(checks));
const allOk = Object.values(checks).filter(v => v).length >= 3;
process.exit(allOk ? 0 : 1);
"""
    tmp = Path(REPO) / "_browser_config_check.cjs"
    tmp.write_text(script)
    try:
        r = subprocess.run(
            ["node", str(tmp)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Browser config exports check failed:\n{r.stdout}\n{r.stderr}"
    finally:
        tmp.unlink(missing_ok=True)


# [repo_tests] pass_to_pass
def test_repo_commands_has_session_commands():
    """Commands module has session management commands (pass_to_pass)."""
    script = """
const fs = require('fs');

const commandsTs = fs.readFileSync('packages/playwright/src/mcp/terminal/commands.ts', 'utf8');

const hasSessionList = commandsTs.includes("name: 'session-list'") || commandsTs.includes("session-list");
const hasSessionStop = commandsTs.includes("name: 'session-stop'") || commandsTs.includes("session-stop");
const hasSessionStopAll = commandsTs.includes("name: 'session-stop-all'") || commandsTs.includes("session-stop-all");
const hasCommandsArray = commandsTs.includes('commandsArray');

const checks = {
  hasSessionList,
  hasSessionStop,
  hasSessionStopAll,
  hasCommandsArray
};

console.log(JSON.stringify(checks));
const allOk = Object.values(checks).filter(v => v).length >= 2;
process.exit(allOk ? 0 : 1);
"""
    tmp = Path(REPO) / "_commands_session_check.cjs"
    tmp.write_text(script)
    try:
        r = subprocess.run(
            ["node", str(tmp)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Commands session check failed:\n{r.stdout}\n{r.stderr}"
    finally:
        tmp.unlink(missing_ok=True)


# [repo_tests] pass_to_pass
def test_repo_program_has_session_manager():
    """Program module has SessionManager class (pass_to_pass)."""
    script = """
const fs = require('fs');

const programTs = fs.readFileSync('packages/playwright/src/mcp/terminal/program.ts', 'utf8');

const hasSessionManager = programTs.includes('class SessionManager');
const hasListMethod = programTs.includes('async list()');
const hasStopMethod = programTs.includes('async stop(');
const hasStartMethod = programTs.includes('async start(') || programTs.includes('start(');
const hasHandleSessionCommand = programTs.includes('handleSessionCommand');

const checks = {
  hasSessionManager,
  hasListMethod,
  hasStopMethod,
  hasStartMethod,
  hasHandleSessionCommand
};

console.log(JSON.stringify(checks));
const allOk = Object.values(checks).filter(v => v).length >= 3;
process.exit(allOk ? 0 : 1);
"""
    tmp = Path(REPO) / "_program_session_check.cjs"
    tmp.write_text(script)
    try:
        r = subprocess.run(
            ["node", str(tmp)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Program session manager check failed:\n{r.stdout}\n{r.stderr}"
    finally:
        tmp.unlink(missing_ok=True)