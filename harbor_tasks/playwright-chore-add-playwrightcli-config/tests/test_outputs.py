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
import os

REPO = "/workspace/playwright"
COMMAND_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/command.ts"
COMMANDS_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/commands.ts"
HELP_GEN_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/helpGenerator.ts"
PROGRAM_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/program.ts"
BROWSER_CONFIG_TS = Path(REPO) / "packages/playwright/src/mcp/browser/config.ts"
SKILL_MD = Path(REPO) / "packages/playwright/src/mcp/terminal/SKILL.md"

# Minimal zod stub so tsx can import the terminal modules without a full build.
_MCP_BUNDLE_IMPL_STUB = r'''
class ZodType {
  _desc?: string;
  optional() { return this; }
  describe(d: string) { (this as any)._desc = d; return this; }
  default(_v: any) { return this; }
  safeParse(v: any) { return { success: v === undefined, data: v }; }
  get description(): string | undefined { return (this as any)._desc; }
}
class ZodObject extends ZodType {
  _shape: Record<string, any>;
  constructor(shape: Record<string, any>) { super(); this._shape = shape; }
  get shape() { return this._shape; }
}
export const z = {
  string: () => new ZodType(),
  number: () => new ZodType(),
  boolean: () => new ZodType(),
  enum: (_values: any[]) => new ZodType(),
  object: (shape: Record<string, any>) => new ZodObject(shape),
  union: (_types: any[]) => new ZodType(),
  array: (_type: any) => new ZodType(),
  literal: (_value: any) => new ZodType(),
  any: () => new ZodType(),
};
export function zodToJsonSchema() { return {}; }
export class Client {}
export class Server {}
export class SSEClientTransport {}
export class SSEServerTransport {}
export class StdioClientTransport {}
export class StdioServerTransport {}
export class StreamableHTTPServerTransport {}
export class StreamableHTTPClientTransport {}
export const CallToolRequestSchema = {};
export const ListRootsRequestSchema = {};
export const ProgressNotificationSchema = {};
export const ListToolsRequestSchema = {};
export const PingRequestSchema = {};
export class Loop {}
'''


def _ensure_tsx_stubs():
    """Create minimal stubs so tsx can resolve workspace dependencies."""
    repo = Path(REPO)

    # Create node_modules/playwright-core symlink for bare-specifier resolution
    nm_dir = repo / "node_modules"
    nm_dir.mkdir(exist_ok=True)
    pc_link = nm_dir / "playwright-core"
    if not pc_link.exists() and not pc_link.is_symlink():
        pc_link.symlink_to("../packages/playwright-core")

    # Create mcpBundleImpl stub (normally a build artifact)
    stub_path = repo / "packages" / "playwright-core" / "src" / "mcpBundleImpl.ts"
    if not stub_path.exists():
        stub_path.write_text(_MCP_BUNDLE_IMPL_STUB)


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
    _ensure_tsx_stubs()
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
    """The Category type union includes 'config' as a valid literal."""
    # Read command.ts source and verify the Category type includes 'config'.
    script = """
const fs = require('fs');
const src = fs.readFileSync('packages/playwright/src/mcp/terminal/command.ts', 'utf8');

// Find the Category type definition line
const match = src.match(/export\\s+type\\s+Category\\s*=\\s*([^;]+)/);
if (!match) {
    console.error('Category type definition not found');
    process.exit(1);
}

const typeDef = match[1];
// Check that 'config' is one of the union members
if (!typeDef.includes("'config'") && !typeDef.includes('"config"')) {
    console.error("'config' not found in Category type definition:", typeDef.trim());
    process.exit(1);
}

console.log(JSON.stringify({ valid: true, typeDef: typeDef.trim() }));
"""
    r = _run_node(script)
    assert r.returncode == 0, f"'config' not in Category type:\n{r.stderr}\n{r.stdout}"
    data = json.loads(r.stdout.strip())
    assert data.get("valid") == True


# [pr_diff] fail_to_pass
def test_config_command_declared():
    """Config command is registered and accessible through the commands module."""
    # Behavioral test: import the commands module via tsx (with zod stub)
    # and look for a config command in any exported collection.
    script = """
import * as commandsMod from './packages/playwright/src/mcp/terminal/commands.ts';

// Find config command in any exported value (object map or array)
let hasConfig = false;
for (const val of Object.values(commandsMod)) {
    if (typeof val !== 'object' || val === null) continue;
    if (Array.isArray(val)) {
        hasConfig = val.some((cmd: any) => cmd?.name === 'config');
    } else {
        // Object map: check for 'config' key or search values by name
        hasConfig = ('config' in val) ||
            Object.values(val).some((cmd: any) =>
                typeof cmd === 'object' && cmd !== null && (cmd as any).name === 'config');
    }
    if (hasConfig) break;
}

if (!hasConfig) {
    console.error('config command not found in any exported collection');
    process.exit(1);
}
console.log(JSON.stringify({ hasConfig: true }));
"""
    r = _run_tsx(script)
    assert r.returncode == 0, f"config command not found in commands list:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("hasConfig") == True


# [pr_diff] fail_to_pass
def test_help_has_configuration_category():
    """generateHelp() output includes a Configuration category with the config command listed."""
    # Behavioral test: import the help generator via tsx (with zod stub),
    # call generateHelp(), and verify the output has a 'Configuration:' section
    # that lists the 'config' command.
    script = """
import * as helpMod from './packages/playwright/src/mcp/terminal/helpGenerator.ts';

// Find the generateHelp function dynamically
const funcs = Object.values(helpMod).filter(v => typeof v === 'function');
let helpText = '';
for (const fn of funcs) {
    try {
        const result = fn();
        if (typeof result === 'string' && result.includes('Usage:')) {
            helpText = result;
            break;
        }
    } catch (e) {}
}

if (!helpText) {
    console.error('No help text generated');
    process.exit(1);
}

// Check that help has a 'Configuration:' section header
// AND that the 'config' command is listed underneath it.
// The help format is: "\\nTitle:\\n  command  description"
const lines = helpText.split('\\n');
let inConfigSection = false;
let foundConfigCommand = false;
for (const line of lines) {
    if (/^Configuration:/.test(line)) {
        inConfigSection = true;
        continue;
    }
    // A new section starts with a non-indented non-empty line
    if (inConfigSection && /^\\S/.test(line) && line.length > 0) {
        break;
    }
    // Look for 'config' as a command entry (indented, not --config flag)
    if (inConfigSection && /^\\s+config\\b/.test(line)) {
        foundConfigCommand = true;
    }
}

if (!inConfigSection) {
    console.error('Configuration: section not found in help output');
    process.exit(1);
}
if (!foundConfigCommand) {
    console.error('config command not listed under Configuration section');
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
    """SessionManager has a configure() method that stops session and reconnects."""
    # Verify that program.ts contains a configure method with the required
    # operational steps: check connection, stop, update config, reconnect.
    script = """
const fs = require('fs');
const src = fs.readFileSync('packages/playwright/src/mcp/terminal/program.ts', 'utf8');

// Check that a configure method exists in a class
const hasConfigureMethod = /async\\s+configure\\s*\\(/.test(src);
if (!hasConfigureMethod) {
    console.error('No async configure() method found');
    process.exit(1);
}

// Extract the configure method body (find from 'async configure' to matching closing brace)
const configureStart = src.indexOf('async configure(');
if (configureStart === -1) {
    console.error('configure method not found');
    process.exit(1);
}

// Get a reasonable chunk after the method declaration
const methodChunk = src.substring(configureStart, configureStart + 800);

// Verify the method performs required operations:
// 1. Checks/connects to existing session
const hasConnectCheck = methodChunk.includes('_canConnect') || methodChunk.includes('_connect');
// 2. Stops the existing session
const hasStop = methodChunk.includes('.stop(') || methodChunk.includes('stop()');
// 3. Updates config
const hasConfigUpdate = methodChunk.includes('config') || methodChunk.includes('_options');
// 4. Reconnects
const hasReconnect = (methodChunk.match(/_connect/g) || []).length >= 1;

const checks = {
    hasConfigureMethod: true,
    hasConnectCheck,
    hasStop,
    hasConfigUpdate,
    hasReconnect,
};

console.log(JSON.stringify(checks));
const required = hasConnectCheck && hasStop && hasReconnect;
if (!required) {
    console.error('configure() missing required operations');
    process.exit(1);
}
"""
    r = _run_node(script)
    assert r.returncode == 0, f"configure() test failed:\n{r.stderr}\n{r.stdout}"
    data = json.loads(r.stdout.strip())
    assert data.get("hasConfigureMethod") == True
    assert data.get("hasStop") == True, "configure() should stop the existing session"
    assert data.get("hasReconnect") == True, "configure() should reconnect with new config"


# [pr_diff] fail_to_pass
def test_config_command_routing():
    """CLI routes 'config' command to the session handler properly."""
    # Behavioral test: import commands via tsx, verify config command has
    # the 'config' category which the program uses for routing.
    script = """
import * as commandsMod from './packages/playwright/src/mcp/terminal/commands.ts';

// Find the config command in any exported collection (object map or array)
let configCmd: any = null;
for (const val of Object.values(commandsMod)) {
    if (typeof val !== 'object' || val === null) continue;
    if (Array.isArray(val)) {
        configCmd = val.find((cmd: any) => cmd?.name === 'config');
    } else {
        const asMap = val as Record<string, any>;
        if ('config' in asMap && typeof asMap.config === 'object') {
            configCmd = asMap.config;
        } else {
            const found = Object.values(asMap).find((cmd: any) =>
                typeof cmd === 'object' && cmd !== null && (cmd as any).name === 'config');
            if (found) configCmd = found;
        }
    }
    if (configCmd) break;
}

if (!configCmd) {
    console.error('config command not found');
    process.exit(1);
}

const category = configCmd?.category;
if (category !== 'config') {
    console.error('config command has wrong category:', category);
    process.exit(1);
}

console.log(JSON.stringify({ routed: true, category }));
"""
    r = _run_tsx(script)
    assert r.returncode == 0, f"config command routing verification failed:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("routed") == True
    assert data.get("category") == "config"


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
    """Daemon browser config sets contextOptions with viewport 1280x720 for headless mode."""
    # Read the browser config source and verify it sets up contextOptions
    # with viewport dimensions in the daemon configuration.
    script = """
const fs = require('fs');
const src = fs.readFileSync('packages/playwright/src/mcp/browser/config.ts', 'utf8');

// Check that contextOptions with viewport is defined
const hasContextOptions = src.includes('contextOptions');
if (!hasContextOptions) {
    console.error('contextOptions not found in config.ts');
    process.exit(1);
}

// Check for viewport dimensions 1280x720
const hasWidth1280 = /width:\\s*1280/.test(src);
const hasHeight720 = /height:\\s*720/.test(src);

if (!hasWidth1280 || !hasHeight720) {
    console.error('viewport 1280x720 not found in config.ts');
    process.exit(1);
}

// Verify viewport is inside contextOptions block
const contextIdx = src.indexOf('contextOptions');
const viewportIdx = src.indexOf('viewport', contextIdx);
if (viewportIdx === -1 || viewportIdx - contextIdx > 200) {
    console.error('viewport not closely associated with contextOptions');
    process.exit(1);
}

// Extract and evaluate the viewport object expression
const viewportMatch = src.substring(viewportIdx).match(
    /viewport[^{]*\\{\\s*width:\\s*(\\d+),\\s*height:\\s*(\\d+)\\s*\\}/
);
if (!viewportMatch) {
    console.error('Could not parse viewport dimensions');
    process.exit(1);
}

const width = parseInt(viewportMatch[1], 10);
const height = parseInt(viewportMatch[2], 10);

console.log(JSON.stringify({
    valid: width === 1280 && height === 720,
    viewport: { width, height }
}));
"""
    r = _run_node(script)
    assert r.returncode == 0, f"Viewport check failed:\n{r.stderr}\n{r.stdout}"
    data = json.loads(r.stdout.strip())
    assert data.get("valid") == True
    vp = data.get("viewport")
    assert vp.get("width") == 1280, f"Viewport width should be 1280, got {vp.get('width')}"
    assert vp.get("height") == 720, f"Viewport height should be 720, got {vp.get('height')}"


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
