"""
Task: vscode-plugin-skill-prefix
Repo: microsoft/vscode @ 559cb3e74d075670b9a03f84751e8fdcd3c52443
PR:   307305

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/vscode"

PLUGIN_SERVICE = "src/vs/workbench/contrib/chat/common/plugins/agentPluginService.ts"
PROMPTS_SERVICE = "src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsServiceImpl.ts"


def _read(rel_path: str) -> str:
    return Path(f"{REPO}/{rel_path}").read_text()


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a CommonJS Node.js script in the repo directory."""
    tmp = Path(REPO) / "_eval_tmp.cjs"
    tmp.write_text(script)
    try:
        return subprocess.run(
            ["node", str(tmp)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via TypeScript AST analysis
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_plugin_prefix_in_discovery():
    """Plugin skills get canonical plugin prefix applied during slash command discovery."""
    r = _run_node(r"""
const ts = require('typescript');
const fs = require('fs');

const src = fs.readFileSync(
    'src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsServiceImpl.ts',
    'utf8'
);
const sf = ts.createSourceFile('test.ts', src, ts.ScriptTarget.Latest, true);

let methodFound = false;
let hasCanonicalCall = false;
let hasInlinePrefix = false;

function visit(node) {
    if (ts.isMethodDeclaration(node) && node.name &&
        ts.isIdentifier(node.name) && node.name.text === 'computeSlashCommandDiscoveryInfo') {
        methodFound = true;
        if (node.body) {
            const bodyText = node.body.getText(sf);
            // Check for direct call to getCanonicalPluginCommandId
            function findCall(n) {
                if (ts.isCallExpression(n) && ts.isIdentifier(n.expression) &&
                    n.expression.text === 'getCanonicalPluginCommandId') {
                    hasCanonicalCall = true;
                }
                ts.forEachChild(n, findCall);
            }
            ts.forEachChild(node.body, findCall);
            // Alternative: inline prefix logic using pluginUri + basename/normalize
            if (bodyText.includes('pluginUri') &&
                (bodyText.includes('basename') || bodyText.includes('normalizePluginToken'))) {
                hasInlinePrefix = true;
            }
        }
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (!methodFound) {
    console.error('FAIL: computeSlashCommandDiscoveryInfo method not found');
    process.exit(1);
}
if (!hasCanonicalCall && !hasInlinePrefix) {
    console.error('FAIL: no plugin prefix logic found in computeSlashCommandDiscoveryInfo');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"AST check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_frontmatter_override_prefixed():
    """Even when SKILL.md frontmatter overrides the name, plugin prefix is preserved."""
    r = _run_node(r"""
const ts = require('typescript');
const fs = require('fs');

const src = fs.readFileSync(
    'src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsServiceImpl.ts',
    'utf8'
);
const sf = ts.createSourceFile('test.ts', src, ts.ScriptTarget.Latest, true);

let methodBody = null;

function findMethod(node) {
    if (ts.isMethodDeclaration(node) && node.name &&
        ts.isIdentifier(node.name) && node.name.text === 'computeSlashCommandDiscoveryInfo' && node.body) {
        methodBody = node.body;
    }
    if (!methodBody) ts.forEachChild(node, findMethod);
}
findMethod(sf);

if (!methodBody) {
    console.error('FAIL: computeSlashCommandDiscoveryInfo method not found');
    process.exit(1);
}

// On base commit: const name = parsedPromptFile?.header?.name ?? ...
// After fix: const rawName = parsedPromptFile?.header?.name ?? ... (intermediate var)
// Check that header?.name is NOT directly assigned to 'name' without transformation.
let directNameAssignment = false;
let hasIntermediate = false;

function checkDecls(node) {
    if (ts.isVariableDeclaration(node) && node.initializer) {
        const initText = node.initializer.getText(sf);
        const varName = node.name.getText(sf);
        // Match the header name extraction pattern
        if (initText.includes('header') && initText.includes('name') &&
            initText.includes('parsedPromptFile')) {
            if (varName === 'name') {
                directNameAssignment = true;
            } else {
                hasIntermediate = true;
            }
        }
    }
    ts.forEachChild(node, checkDecls);
}
checkDecls(methodBody);

const bodyText = methodBody.getText(sf);
const hasTransform = bodyText.includes('getCanonicalPluginCommandId') ||
    (bodyText.includes('pluginUri') && bodyText.includes('normalizePluginToken'));

if (directNameAssignment && !hasIntermediate && !hasTransform) {
    console.error('FAIL: header name assigned directly to const name without plugin prefix transformation');
    process.exit(1);
}
if (!hasIntermediate && !directNameAssignment && !hasTransform) {
    console.error('FAIL: no header name extraction pattern found in method');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"AST check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_type_signature_widened():
    """getCanonicalPluginCommandId accepts a type wider than IAgentPlugin."""
    r = _run_node(r"""
const ts = require('typescript');
const fs = require('fs');

const pluginSrc = fs.readFileSync(
    'src/vs/workbench/contrib/chat/common/plugins/agentPluginService.ts',
    'utf8'
);
const sf1 = ts.createSourceFile('plugin.ts', pluginSrc, ts.ScriptTarget.Latest, true);

let funcFound = false;
let firstParamType = '';

function visitPlugin(node) {
    if (ts.isFunctionDeclaration(node) && node.name &&
        node.name.text === 'getCanonicalPluginCommandId') {
        funcFound = true;
        if (node.parameters.length > 0 && node.parameters[0].type) {
            firstParamType = node.parameters[0].type.getText(sf1);
        }
    }
    ts.forEachChild(node, visitPlugin);
}
visitPlugin(sf1);

if (!funcFound) {
    console.error('FAIL: getCanonicalPluginCommandId function not found');
    process.exit(1);
}

const typeIsWidened = firstParamType !== 'IAgentPlugin';

// Alternative: agent inlined prefix logic in discovery method instead
let hasInlinePrefix = false;
if (!typeIsWidened) {
    const promptsSrc = fs.readFileSync(
        'src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsServiceImpl.ts',
        'utf8'
    );
    const sf2 = ts.createSourceFile('prompts.ts', promptsSrc, ts.ScriptTarget.Latest, true);
    let methodBody = null;
    function findMethod(node) {
        if (ts.isMethodDeclaration(node) && node.name &&
            ts.isIdentifier(node.name) && node.name.text === 'computeSlashCommandDiscoveryInfo' && node.body) {
            methodBody = node.body;
        }
        if (!methodBody) ts.forEachChild(node, findMethod);
    }
    findMethod(sf2);
    if (methodBody) {
        const bodyText = methodBody.getText(sf2);
        hasInlinePrefix = bodyText.includes('pluginUri') &&
            (bodyText.includes('basename') || bodyText.includes('normalize'));
    }
}

if (!typeIsWidened && !hasInlinePrefix) {
    console.error('FAIL: first param is still IAgentPlugin and no inline prefix logic found');
    process.exit(1);
}
console.log('PASS: type=' + firstParamType);
""")
    assert r.returncode == 0, f"AST check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_plugin_source_guard():
    """Prefix is only applied when source is Plugin, not for all prompt sources."""
    r = _run_node(r"""
const ts = require('typescript');
const fs = require('fs');

const src = fs.readFileSync(
    'src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsServiceImpl.ts',
    'utf8'
);
const sf = ts.createSourceFile('test.ts', src, ts.ScriptTarget.Latest, true);

let methodBody = null;

function findMethod(node) {
    if (ts.isMethodDeclaration(node) && node.name &&
        ts.isIdentifier(node.name) && node.name.text === 'computeSlashCommandDiscoveryInfo' && node.body) {
        methodBody = node.body;
    }
    if (!methodBody) ts.forEachChild(node, findMethod);
}
findMethod(sf);

if (!methodBody) {
    console.error('FAIL: computeSlashCommandDiscoveryInfo method not found');
    process.exit(1);
}

const bodyText = methodBody.getText(sf);

// Must have some form of prefix logic
const hasPrefix = bodyText.includes('getCanonicalPluginCommandId') ||
    (bodyText.includes('pluginUri') &&
     (bodyText.includes('basename') || bodyText.includes('normalizePluginToken')));

// Must guard prefix to plugin sources only
const hasGuard = bodyText.includes('PromptFileSource.Plugin') ||
    (bodyText.includes('.source') && bodyText.includes('Plugin')) ||
    bodyText.includes('isPlugin');

if (!hasPrefix) {
    console.error('FAIL: no plugin prefix logic found');
    process.exit(1);
}
if (!hasGuard) {
    console.error('FAIL: prefix is not guarded to plugin sources only');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"AST check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_non_plugin_sources_unaffected():
    """Non-plugin sources still use unmodified name (no false prefix application)."""
    src = _read(PROMPTS_SERVICE)

    assert "getCleanPromptName" in src, (
        "getCleanPromptName must still be used as fallback for non-plugin prompt names"
    )
    assert "slashCommandsFromDiscoveryInfo" in src, (
        "slashCommandsFromDiscoveryInfo method must still exist"
    )


# [static] pass_to_pass
def test_canonical_function_still_exported():
    """getCanonicalPluginCommandId remains exported and functional."""
    src = _read(PLUGIN_SERVICE)

    assert re.search(
        r"export\s+function\s+getCanonicalPluginCommandId", src
    ), "getCanonicalPluginCommandId must remain exported"

    # Function body must still reference basename and normalizePluginToken
    lines = src.splitlines()
    for i, line in enumerate(lines):
        if "getCanonicalPluginCommandId" in line and "export" in line:
            func_region = "\n".join(lines[i:i + 15])
            assert "basename" in func_region, (
                "getCanonicalPluginCommandId must still use basename"
            )
            assert "normalizePluginToken" in func_region, (
                "getCanonicalPluginCommandId must still use normalizePluginToken"
            )
            break


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:126
def test_no_arrow_function_for_export():
    """Exported function uses function keyword, not arrow expression."""
    src = _read(PLUGIN_SERVICE)

    assert re.search(
        r"export\s+function\s+getCanonicalPluginCommandId", src
    ), (
        "getCanonicalPluginCommandId must use 'export function' declaration, "
        "not 'export const' arrow function (per copilot-instructions.md)"
    )


# [agent_config] pass_to_pass — .github/copilot-instructions.md:72
def test_tab_indentation_in_modified_files():
    """Modified files use tab indentation as required by VS Code coding guidelines."""
    for rel_path in [PLUGIN_SERVICE, PROMPTS_SERVICE]:
        src = _read(rel_path)
        indented_lines = [l for l in src.splitlines() if l and l[0] in ("\t", " ")]
        tab_lines = [l for l in indented_lines if l.startswith("\t")]
        space_only = [l for l in indented_lines if l.startswith("    ") and not l.startswith("\t")]
        assert len(tab_lines) > len(space_only) * 10, (
            f"{rel_path}: must use tab indentation "
            f"({len(tab_lines)} tab lines vs {len(space_only)} space-only lines)"
        )


# [agent_config] pass_to_pass — .github/copilot-instructions.md:94
def test_single_quotes_for_strings():
    """Non-localized strings use single quotes, not double quotes."""
    src = _read(PROMPTS_SERVICE)
    # Check in the discovery method region for consistent quoting
    lines = src.splitlines()
    method_start = None
    for i, line in enumerate(lines):
        if "computeSlashCommandDiscoveryInfo" in line and ("private" in line or "async" in line):
            method_start = i
            break
    if method_start is None:
        return

    block = "\n".join(lines[method_start:method_start + 45])
    non_localized_doubles = re.findall(
        r'(?<!localize\()\"[^"]+\"', block
    )
    single_quoted = re.findall(r"'[^']+'", block)

    if non_localized_doubles and single_quoted:
        assert len(single_quoted) >= len(non_localized_doubles), (
            "Non-localized strings should use single quotes per copilot-instructions.md"
        )
