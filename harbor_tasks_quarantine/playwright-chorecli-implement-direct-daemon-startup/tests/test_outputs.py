"""
Task: playwright-chorecli-implement-direct-daemon-startup
Repo: microsoft/playwright @ 25d303f03424011dc0ad36d027a7af3368618eab
PR:   39162

Refactors daemon startup to launch browser directly via stdout communication
instead of polling. Renames the CLI session flag from -b to -s. Updates
SKILL.md and session-management reference docs accordingly.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
MCP_DIR = Path(REPO) / "packages" / "playwright" / "src" / "mcp"
SKILL_DIR = Path(REPO) / "packages" / "playwright" / "src" / "skill"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - File structure and content checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified TypeScript files exist and are non-empty (pass_to_pass)."""
    files = [
        MCP_DIR / "terminal" / "program.ts",
        MCP_DIR / "terminal" / "daemon.ts",
        MCP_DIR / "terminal" / "helpGenerator.ts",
        MCP_DIR / "browser" / "browserContextFactory.ts",
        MCP_DIR / "program.ts",
    ]
    for f in files:
        assert f.exists(), f"Missing file: {f}"
        content = f.read_text()
        assert len(content) > 100, f"File suspiciously small: {f}"


def test_all_modified_files_exist():
    """All files modified in PR exist and have valid content (pass_to_pass)."""
    modified_files = [
        # MCP source files
        MCP_DIR / "browser" / "browserContextFactory.ts",
        MCP_DIR / "browser" / "browserServerBackend.ts",
        MCP_DIR / "browser" / "context.ts",
        MCP_DIR / "extension" / "cdpRelay.ts",
        MCP_DIR / "program.ts",
        MCP_DIR / "sdk" / "server.ts",
        MCP_DIR / "terminal" / "DEPS.list",
        MCP_DIR / "terminal" / "daemon.ts",
        MCP_DIR / "terminal" / "helpGenerator.ts",
        MCP_DIR / "terminal" / "program.ts",
        # Documentation files
        SKILL_DIR / "SKILL.md",
        SKILL_DIR / "references" / "session-management.md",
        # Test files
        Path(REPO) / "tests" / "mcp" / "cli-isolated.spec.ts",
        Path(REPO) / "tests" / "mcp" / "cli-misc.spec.ts",
        Path(REPO) / "tests" / "mcp" / "cli-session.spec.ts",
    ]
    for f in modified_files:
        assert f.exists(), f"Modified file missing: {f}"
        content = f.read_text()
        assert len(content) > 50, f"File suspiciously small: {f}"


def test_typescript_syntax_valid():
    """All modified TypeScript files have valid basic syntax (pass_to_pass)."""
    ts_files = [
        MCP_DIR / "browser" / "browserContextFactory.ts",
        MCP_DIR / "browser" / "browserServerBackend.ts",
        MCP_DIR / "browser" / "context.ts",
        MCP_DIR / "extension" / "cdpRelay.ts",
        MCP_DIR / "program.ts",
        MCP_DIR / "sdk" / "server.ts",
        MCP_DIR / "terminal" / "daemon.ts",
        MCP_DIR / "terminal" / "helpGenerator.ts",
        MCP_DIR / "terminal" / "program.ts",
    ]

    for f in ts_files:
        content = f.read_text()
        # Basic TypeScript syntax validation
        # Check for balanced braces
        open_count = content.count("{")
        close_count = content.count("}")
        assert open_count == close_count, f"Unbalanced braces in {f}"
        # Check for balanced parentheses
        open_parens = content.count("(")
        close_parens = content.count(")")
        assert open_parens == close_parens, f"Unbalanced parentheses in {f}"
        # Check file ends properly - use string concatenation to avoid f-string issue
        stripped = content.strip()
        assert stripped.endswith("}"), "File " + str(f) + " doesn't end with closing brace"


def test_mcp_module_structure():
    """MCP module imports and exports are structurally valid (pass_to_pass)."""
    # Check that key imports exist in modified files
    program_src = (MCP_DIR / "program.ts").read_text()
    daemon_src = (MCP_DIR / "terminal" / "daemon.ts").read_text()

    # Verify key imports are present (structural check)
    assert "import" in program_src, "program.ts should have imports"
    assert "import" in daemon_src, "daemon.ts should have imports"
    assert "export" in program_src, "program.ts should have exports"


def test_documentation_files_valid():
    """Documentation files are valid markdown (pass_to_pass)."""
    skill_md = (SKILL_DIR / "SKILL.md").read_text()
    session_md = (SKILL_DIR / "references" / "session-management.md").read_text()

    # Check markdown structure
    assert "#" in skill_md, "SKILL.md should have headings"
    assert "#" in session_md, "session-management.md should have headings"
    # Check for code blocks
    assert "```" in skill_md, "SKILL.md should have code blocks"
    assert "```" in session_md, "session-management.md should have code blocks"


def test_test_files_valid():
    """MCP test files are valid spec files (pass_to_pass)."""
    test_files = [
        Path(REPO) / "tests" / "mcp" / "cli-isolated.spec.ts",
        Path(REPO) / "tests" / "mcp" / "cli-misc.spec.ts",
        Path(REPO) / "tests" / "mcp" / "cli-session.spec.ts",
    ]

    for f in test_files:
        content = f.read_text()
        # Check for Playwright test patterns
        assert "test(" in content or "test.describe" in content, f"{f} missing test definitions"
        assert "import" in content, f"{f} missing imports"


def test_mcp_deps_structure():
    """MCP DEPS.list files are valid and all imports respect DEPS constraints (pass_to_pass)."""
    # List of DEPS.list files in MCP module
    deps_files = [
        MCP_DIR / "DEPS.list",
        MCP_DIR / "browser" / "DEPS.list",
        MCP_DIR / "browser" / "tools" / "DEPS.list",
        MCP_DIR / "extension" / "DEPS.list",
        MCP_DIR / "sdk" / "DEPS.list",
        MCP_DIR / "terminal" / "DEPS.list",
        MCP_DIR / "test" / "DEPS.list",
    ]

    for deps_file in deps_files:
        assert deps_file.exists(), f"DEPS.list missing: {deps_file}"
        content = deps_file.read_text()

        # Parse DEPS.list format: [filename] sections followed by allowed imports
        sections = []
        current_section = None
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                # New section: [filename] or [*] for all files in directory
                current_section = {"file": line[1:-1], "deps": []}
                sections.append(current_section)
            elif current_section is not None:
                current_section["deps"].append(line)

        # Validate that DEPS.list has at least one section
        assert len(sections) > 0, f"DEPS.list {deps_file} has no valid sections"

        # Check that referenced files exist (if specific file, not [*])
        # Note: Some DEPS.list entries may reference files that exist with
        # different naming (e.g., case differences) or are legacy entries.
        # We only verify the DEPS.list structure is valid, not strict file naming.
        deps_dir = deps_file.parent
        for section in sections:
            file_spec = section["file"]
            if file_spec != "*":
                # Check specific file exists (allowing for case variations)
                target_file = deps_dir / file_spec
                if not target_file.exists():
                    # Check for case-insensitive match
                    found = False
                    try:
                        for existing_file in deps_dir.iterdir():
                            if existing_file.name.lower() == file_spec.lower():
                                found = True
                                break
                    except OSError:
                        pass
                    # Some legacy DEPS.list entries may reference removed files
                    # Only assert for critical files that are part of the PR
                    if not found and file_spec in ['daemon.ts', 'cli.ts', 'program.ts', 'socketConnection.ts']:
                        assert False, f"DEPS.list references non-existent critical file: {target_file}"

        # Validate strict mode consistency in terminal/DEPS.list
        if "terminal" in str(deps_file):
            # Check that cli.ts, program.ts, socketConnection.ts have "strict" marker
            for section in sections:
                if section["file"] in ["cli.ts", "program.ts", "socketConnection.ts"]:
                    assert '"strict"' in section["deps"] or "strict" in section["deps"], \
                        f"Terminal {section['file']} should have strict mode in DEPS.list"


def test_modified_files_deps_updated():
    """Modified files in terminal/ have proper DEPS.list entries (pass_to_pass)."""
    # PR #39162 modified terminal/daemon.ts to add new imports
    terminal_deps = (MCP_DIR / "terminal" / "DEPS.list").read_text()

    # Check that daemon.ts has a DEPS section (validates DEPS.list structure)
    daemon_section = False
    daemon_deps = []
    for line in terminal_deps.splitlines():
        if line.strip() == "[daemon.ts]":
            daemon_section = True
            continue
        if daemon_section:
            if line.strip().startswith("[") and line.strip().endswith("]"):
                break
            if line.strip() and not line.strip().startswith("#"):
                daemon_deps.append(line.strip())

    # daemon.ts should have a valid DEPS section with dependencies
    assert len(daemon_deps) > 0, "daemon.ts DEPS.list should have dependencies defined"

    # NOTE: After PR #39162 is applied, daemon.ts will have browserServerBackend.ts
    # in its DEPS. This test passes on base commit; the DEPS entry is added by the fix.


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - Real CI commands via subprocess.run()
# ---------------------------------------------------------------------------

def test_repo_node_syntax_check():
    """Node.js can parse modified TypeScript files without syntax errors (pass_to_pass)."""
    ts_files = [
        "packages/playwright/src/mcp/browser/browserContextFactory.ts",
        "packages/playwright/src/mcp/browser/browserServerBackend.ts",
        "packages/playwright/src/mcp/browser/context.ts",
        "packages/playwright/src/mcp/extension/cdpRelay.ts",
        "packages/playwright/src/mcp/program.ts",
        "packages/playwright/src/mcp/sdk/server.ts",
        "packages/playwright/src/mcp/terminal/daemon.ts",
        "packages/playwright/src/mcp/terminal/helpGenerator.ts",
        "packages/playwright/src/mcp/terminal/program.ts",
    ]

    for f in ts_files:
        r = subprocess.run(
            ["node", "--check", f],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Syntax check failed for {f}:\n{r.stderr[:500]}"


def test_repo_import_validation():
    """Modified files have valid import paths that exist (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const path = require('path');

const files = [
  'packages/playwright/src/mcp/terminal/daemon.ts',
  'packages/playwright/src/mcp/terminal/program.ts',
  'packages/playwright/src/mcp/program.ts',
];

const importRegex = /import\\s+.*?\\s+from\\s+['"]([^'"]+)['"];?/g;
let errors = [];

for (const file of files) {
  const content = fs.readFileSync(file, 'utf8');
  let match;
  while ((match = importRegex.exec(content)) !== null) {
    const imp = match[1];
    if (imp.startsWith('.')) {
      const resolved = path.resolve(path.dirname(file), imp);
      // Check if file or directory exists with various extensions
      const exists = fs.existsSync(resolved) ||
                     fs.existsSync(resolved + '.ts') ||
                     fs.existsSync(resolved + '.d.ts') ||
                     fs.existsSync(resolved + '.js') ||
                     fs.existsSync(resolved + '/index.ts') ||
                     fs.existsSync(resolved + '/index.js');
      if (!exists && !imp.includes('node_modules')) {
        errors.push(`${file}: import '${imp}' not found`);
      }
    }
  }
}

if (errors.length > 0) {
  console.error(errors.join('\\n'));
  process.exit(1);
}
console.log('PASS');
"""],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Import validation failed:\n{r.stderr[:500]}"


def test_repo_mcp_config_valid():
    """MCP playwright.config.ts is valid and can be parsed (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const content = fs.readFileSync('tests/mcp/playwright.config.ts', 'utf8');

// Basic validation: check for required config patterns
const checks = [
  ['export default', content.includes('export default')],
  ['defineConfig', content.includes('defineConfig')],
  ['testDir', content.includes('testDir')],
  ['projects', content.includes('projects')],
];

for (const [name, found] of checks) {
  if (!found) {
    console.error(`Missing: ${name}`);
    process.exit(1);
  }
}
console.log('PASS');
"""],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"MCP config validation failed:\n{r.stderr[:500]}"


def test_repo_mcp_test_files_exist():
    """MCP test spec files referenced in CI exist and are non-empty (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const path = require('path');

const testFiles = [
  'tests/mcp/cli-isolated.spec.ts',
  'tests/mcp/cli-misc.spec.ts',
  'tests/mcp/cli-session.spec.ts',
];

for (const file of testFiles) {
  const fullPath = path.join(file);
  if (!fs.existsSync(fullPath)) {
    console.error(`Missing test file: ${file}`);
    process.exit(1);
  }
  const content = fs.readFileSync(fullPath, 'utf8');
  if (content.length < 100) {
    console.error(`Test file too small: ${file}`);
    process.exit(1);
  }
  // Verify it's a valid Playwright test file
  if (!content.includes('test(') && !content.includes('test.describe')) {
    console.error(`Not a valid Playwright test file: ${file}`);
    process.exit(1);
  }
}
console.log('PASS');
"""],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"MCP test files check failed:\n{r.stderr[:500]}"


def test_repo_cli_deps_check():
    """Repo DEPS.list checker passes for MCP terminal module (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const path = require('path');

// Read DEPS.list and validate structure
const depsPath = 'packages/playwright/src/mcp/terminal/DEPS.list';
const content = fs.readFileSync(depsPath, 'utf8');

// Check DEPS.list has proper sections for modified files
const requiredSections = ['[daemon.ts]', '[program.ts]', '[cli.ts]'];
for (const section of requiredSections) {
  if (!content.includes(section)) {
    console.error(`Missing DEPS.list section: ${section}`);
    process.exit(1);
  }
}

// Check that daemon.ts section has dependencies
const daemonMatch = content.match(/\\[daemon.ts\\][\\s\\S]*?(?=\\[|$)/);
if (!daemonMatch) {
  console.error('Could not parse daemon.ts section');
  process.exit(1);
}

const daemonSection = daemonMatch[0];
const hasDeps = daemonSection.split('\\n').some(line => {
  const trimmed = line.trim();
  return trimmed && !trimmed.startsWith('#') && !trimmed.startsWith('[');
});

if (!hasDeps) {
  console.error('daemon.ts section has no dependencies');
  process.exit(1);
}

console.log('PASS');
"""],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"DEPS.list check failed:\n{r.stderr[:500]}"


def test_repo_cli_help_valid():
    """CLI help generator produces valid output structure (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');

// Read helpGenerator.ts and verify it produces valid structure
const helpGenPath = 'packages/playwright/src/mcp/terminal/helpGenerator.ts';
const content = fs.readFileSync(helpGenPath, 'utf8');

// Check for required help generation components
const checks = [
  ['commands import', content.includes('commands')],
  ['generateCommandHelp function', content.includes('generateCommandHelp')],
  ['categories defined', content.includes('categories')],
  ['commandArgs function', content.includes('commandArgs')],
  ['CommandArg type', content.includes('CommandArg')],
];

for (const [name, found] of checks) {
  if (!found) {
    console.error(`Missing: ${name}`);
    process.exit(1);
  }
}

// Verify categories array has expected browser sessions category
if (!content.includes("'Browser sessions'") && !content.includes('"Browser sessions"')) {
  console.error('Missing Browser sessions category');
  process.exit(1);
}

console.log('PASS');
"""],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"CLI help check failed:\n{r.stderr[:500]}"


def test_repo_node_npm_ci_check():
    """Repo package.json is valid and npm can install dependencies (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "ci", "--dry-run"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    # npm ci --dry-run returns 0 if package-lock.json is valid
    # It may warn but should not error
    assert r.returncode == 0, f"npm ci dry-run failed:\n{r.stderr[:500]}"


def test_repo_eslint_mcp():
    """ESLint passes on MCP module files (pass_to_pass)."""
    # Install deps and build first (required for ESLint to resolve imports)
    r = subprocess.run(
        ["npm", "ci", "--silent"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"npm ci failed: {r.stderr[:500]}"

    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"npm run build failed: {r.stderr[:500]}"

    r = subprocess.run(
        ["npm", "run", "eslint", "--", "--max-warnings=1000", "packages/playwright/src/mcp"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed on MCP files:\n{r.stderr[:500]}\n{r.stdout[:500]}"


def test_repo_lint_tests():
    """Repo test linting passes (pass_to_pass)."""
    # Install deps and build first
    r = subprocess.run(
        ["npm", "ci", "--silent"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"npm ci failed: {r.stderr[:500]}"

    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"npm run build failed: {r.stderr[:500]}"

    r = subprocess.run(
        ["npm", "run", "lint-tests"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"lint-tests failed:\n{r.stderr[:500]}\n{r.stdout[:500]}"


def test_repo_lint_packages():
    """Repo package consistency check passes (pass_to_pass)."""
    # Install deps and build first
    r = subprocess.run(
        ["npm", "ci", "--silent"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"npm ci failed: {r.stderr[:500]}"

    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"npm run build failed: {r.stderr[:500]}"

    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"lint-packages failed:\n{r.stderr[:500]}\n{r.stdout[:500]}"


def test_repo_check_deps():
    """Repo DEPS.list check passes (pass_to_pass)."""
    # Install deps and build first
    r = subprocess.run(
        ["npm", "ci", "--silent"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"npm ci failed: {r.stderr[:500]}"

    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"npm run build failed: {r.stderr[:500]}"

    r = subprocess.run(
        ["npm", "run", "check-deps"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"check-deps failed:\n{r.stderr[:500]}\n{r.stdout[:500]}"


def test_repo_build():
    """Repo builds successfully without errors (pass_to_pass)."""
    # Install deps first
    r = subprocess.run(
        ["npm", "ci", "--silent"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"npm ci failed: {r.stderr[:500]}"

    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"npm run build failed:\n{r.stderr[:500]}\n{r.stdout[:500]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- behavioral tests via subprocess
# ---------------------------------------------------------------------------

def test_session_flag_normalization_behavior():
    """The arg parser normalizes -s to --session, verified by executing the logic."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const src = fs.readFileSync('packages/playwright/src/mcp/terminal/program.ts', 'utf8');

// Find the session-alias normalization block (matches both old -b and new -s)
const match = src.match(/\\/\\/ Normalize -[sb] alias to --session[\\s\\S]*?delete args\\.[sb];?\\s*\\}/);
if (!match) {
  console.error('No session alias normalization block found');
  process.exit(1);
}

// Strip comments and execute the block with a test args object
const code = match[0].replace(/\\/\\/.*/g, '');
const args = { s: 'my-session' };
eval(code);

// After fix: the -s flag should be normalized to --session
if (args.session !== 'my-session') {
  console.error('Expected args.session=\"my-session\", got:', args.session);
  process.exit(1);
}
if ('s' in args) {
  console.error('args.s should have been deleted after normalization');
  process.exit(1);
}
console.log('PASS');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_browser_error_includes_channel_name():
    """throwBrowserIsNotInstalledError includes the specific browser channel in the error."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const src = fs.readFileSync('packages/playwright/src/mcp/browser/browserContextFactory.ts', 'utf8');

// Extract the throwBrowserIsNotInstalledError function
const match = src.match(/function\\s+throwBrowserIsNotInstalledError[\\s\\S]*?\\n\\}/);
if (!match) {
  console.error('throwBrowserIsNotInstalledError function not found');
  process.exit(1);
}

// Strip TS type annotations to produce valid JS
let fn = match[0]
  .replace(/\\(config:\\s*FullConfig\\)/g, '(config)')
  .replace(/:\\s*never/g, '');
eval(fn);

// Test: uses launchOptions.channel when available
try {
  throwBrowserIsNotInstalledError({
    browser: { launchOptions: { channel: 'chrome' }, browserName: 'chromium' },
    skillMode: false
  });
} catch (e) {
  if (!e.message.includes('chrome')) {
    console.error('Error should mention \"chrome\", got:', e.message);
    process.exit(1);
  }
}

// Test: falls back to browserName when no channel specified
try {
  throwBrowserIsNotInstalledError({
    browser: { browserName: 'firefox' },
    skillMode: false
  });
} catch (e) {
  if (!e.message.includes('firefox')) {
    console.error('Error should mention \"firefox\", got:', e.message);
    process.exit(1);
  }
}

console.log('PASS');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- structural tests
# ---------------------------------------------------------------------------

def test_help_generator_shows_new_flag():
    """Help text uses -s=<session>, not -b=<session>."""
    src = (MCP_DIR / "terminal" / "helpGenerator.ts").read_text()
    assert "-s=" in src, "helpGenerator should show -s= in usage text"
    for line in src.splitlines():
        if line.strip().startswith("//"):
            continue
        if "-b=" in line and "session" in line.lower():
            assert False, "helpGenerator still shows old -b= session usage"


def test_direct_daemon_startup():
    """daemon.ts creates browser context directly, not via ServerBackendFactory."""
    src = (MCP_DIR / "terminal" / "daemon.ts").read_text()
    assert "createContext" in src, \
        "daemon.ts should call createContext for direct browser launch"
    assert "BrowserContextFactory" in src or "browserContextFactory" in src, \
        "daemon.ts should reference BrowserContextFactory"
    for line in src.splitlines():
        if line.strip().startswith("//"):
            continue
        if "ServerBackendFactory" in line and "import" in line:
            assert False, "daemon.ts should not import ServerBackendFactory anymore"


def test_daemon_stdout_communication():
    """program.ts uses stdout markers for daemon communication instead of polling."""
    src = (MCP_DIR / "program.ts").read_text()
    assert "### Success" in src, "program.ts should output '### Success' marker"
    assert "<EOF>" in src, "program.ts should output '<EOF>' marker"


def test_session_flag_in_error_messages():
    """Error messages and console output use -s= not -b for session references."""
    src = (MCP_DIR / "terminal" / "program.ts").read_text()
    found_s_flag = False
    for line in src.splitlines():
        if line.strip().startswith("//"):
            continue
        if "-s=" in line and ("open" in line or "session" in line.lower()):
            found_s_flag = True
            break
    assert found_s_flag, "program.ts error messages should reference -s= flag"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- documentation updates
# ---------------------------------------------------------------------------

def test_skill_md_session_flag_updated():
    """SKILL.md uses -s= for session examples, not -b."""
    src = (SKILL_DIR / "SKILL.md").read_text()
    assert "-s=" in src, "SKILL.md should use -s= for session flag"
    in_code_block = False
    for line in src.splitlines():
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
        if in_code_block and "playwright-cli -b" in line:
            assert False, f"SKILL.md still uses -b in code: {line.strip()}"


def test_session_management_md_updated():
    """session-management.md uses -s= for session flag, not -b."""
    src = (SKILL_DIR / "references" / "session-management.md").read_text()
    assert "-s=" in src, "session-management.md should use -s= flag"
    in_code_block = False
    for line in src.splitlines():
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
        if in_code_block and "playwright-cli -b" in line:
            assert False, f"session-management.md still uses -b: {line.strip()}"
