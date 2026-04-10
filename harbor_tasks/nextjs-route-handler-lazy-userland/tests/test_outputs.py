"""
Task: nextjs-route-handler-lazy-userland
Repo: next.js @ a43cf0c247b72915d82b44539c0dbde13efccfc9
PR:   92271

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"

TEMPLATE = f"{REPO}/packages/next/src/build/templates/app-route.ts"
MODULE = f"{REPO}/packages/next/src/server/route-modules/app-route/module.ts"
ROUTE_MODULE_BASE = f"{REPO}/packages/next/src/server/route-modules/route-module.ts"
EXPORT_ROUTE = f"{REPO}/packages/next/src/export/routes/app-route.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax():
    """All modified TypeScript files must parse without syntax errors."""
    files = [TEMPLATE, MODULE, ROUTE_MODULE_BASE, EXPORT_ROUTE]
    for fpath in files:
        r = subprocess.run(
            ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{fpath}', 'utf8');
// Basic TS syntax check: look for unmatched braces (class/function balance)
let depth = 0;
for (const ch of src) {{
    if (ch === '{{') depth++;
    else if (ch === '}}') depth--;
}}
if (depth !== 0) {{
    console.error('Unbalanced braces in {fpath}: depth=' + depth);
    process.exit(1);
}}
// Check no obvious syntax issues: unterminated strings, stray backticks
const lines = src.split('\\n');
for (let i = 0; i < lines.length; i++) {{
    const line = lines[i];
    // Detect stray triple-backticks (markdown in TS)
    if (line.trim().startsWith('```')) {{
        console.error('Markdown fence at line ' + (i+1) + ' in {fpath}');
        process.exit(1);
    }}
}}
console.log('OK: {fpath}');
"""],
            capture_output=True,
            timeout=30,
        )
        assert r.returncode == 0, (
            f"Syntax check failed for {fpath}:\n{r.stderr.decode()}"
        )


# [static] pass_to_pass
def test_module_exports_class():
    """Module still exports AppRouteRouteModule class and AppRouteUserlandModule type."""
    content = Path(MODULE).read_text()
    assert "export class AppRouteRouteModule" in content, (
        "AppRouteRouteModule class not exported from module.ts"
    )
    assert "export type AppRouteUserlandModule" in content or \
           "export interface AppRouteUserlandModule" in content, (
        "AppRouteUserlandModule type not exported from module.ts"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_template_lazy_userland_factory():
    """Template must use lazy require factory instead of static import for userland."""
    # Use node subprocess to parse and check the template
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const content = fs.readFileSync('{TEMPLATE}', 'utf8');

// Must NOT have static import of userland at top level
if (/^import\\s+\\*\\s+as\\s+userland\\s+from\\s+['\"]VAR_USERLAND['\"]/m.test(content)) {{
    console.error('Template still has static userland import');
    process.exit(1);
}}

// Must use a lazy factory: userland as a function that calls require()
// Match pattern like: userland: () => require('VAR_USERLAND')
if (!/userland:\\s*\\(\\)\\s*=>\\s*require\\s*\\(['\"]VAR_USERLAND['\"]\\)/m.test(content)) {{
    console.error('Template missing lazy require factory for userland');
    process.exit(1);
}}

console.log('OK: template uses lazy require factory');
"""],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Template check failed:\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_module_ensure_userland():
    """AppRouteRouteModule must have a public async ensureUserland() method."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const content = fs.readFileSync('{MODULE}', 'utf8');

// Check ensureUserland method exists as async
if (!/async\\s+ensureUserland\\s*\\(/.test(content)) {{
    console.error('ensureUserland() async method not found');
    process.exit(1);
}}

// Verify it handles _pendingUserland (not just an empty stub)
if (!/this\\._pendingUserland|this\\.userland/.test(content.substring(
    content.indexOf('ensureUserland'),
    content.indexOf('ensureUserland') + 1500
))) {{
    console.error('ensureUserland() appears to be a stub');
    process.exit(1);
}}

console.log('OK: ensureUserland found');
"""],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"ensureUserland check failed:\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_module_init_from_userland():
    """Module must have _initFromUserland() as a separate method (extracted from constructor)."""
    content = Path(MODULE).read_text()
    # Must have _initFromUserland as a method definition
    assert "_initFromUserland()" in content, (
        "_initFromUserland() method not found in module.ts"
    )
    # Must call autoImplementMethods inside _initFromUserland (not in constructor directly)
    init_idx = content.rindex("_initFromUserland()")
    # Find the method body (next ~2000 chars to handle larger methods)
    method_region = content[init_idx:init_idx + 2000]
    assert "autoImplementMethods" in method_region, (
        "_initFromUserland() does not call autoImplementMethods"
    )
    assert "_methods" in method_region or "this._methods" in method_region, (
        "_initFromUserland() does not assign to _methods"
    )


# [pr_diff] fail_to_pass
def test_getUserland_synchronous():
    """getUserland option must return synchronously (not wrapped in Promise)."""
    content = Path(MODULE).read_text()
    # Find the getUserland type in AppRouteRouteModuleOptions interface
    # On base: readonly getUserland?: () => Promise<AppRouteUserlandModule>
    # On fix:  readonly getUserland?: () => AppRouteUserlandModule
    import re
    match = re.search(
        r'readonly\s+getUserland\?\s*:\s*\(\)\s*=>\s*(.+)',
        content,
    )
    assert match is not None, "getUserland type declaration not found in options"
    return_type = match.group(1).strip()
    assert "Promise" not in return_type, (
        f"getUserland still returns Promise: {return_type}"
    )
    assert "AppRouteUserlandModule" in return_type, (
        f"getUserland does not return AppRouteUserlandModule: {return_type}"
    )


# [pr_diff] fail_to_pass
def test_export_route_calls_ensure_userland():
    """Export route must call ensureUserland() before accessing module.userland."""
    content = Path(EXPORT_ROUTE).read_text()
    assert "ensureUserland" in content, (
        "export/routes/app-route.ts does not call ensureUserland()"
    )
    # Verify ensureUserland is called BEFORE module.userland access
    ensure_idx = content.index("ensureUserland")
    # Find the next reference to module.userland or .userland after the try block
    userland_after = content.find("module.userland", ensure_idx)
    if userland_after == -1:
        userland_after = content.find(".userland", ensure_idx)
    assert userland_after > ensure_idx, (
        "ensureUserland() is not called before userland access"
    )


# [pr_diff] fail_to_pass
def test_base_class_userland_getter():
    """Base RouteModule must use protected _userland with a getter for lazy loading support."""
    content = Path(ROUTE_MODULE_BASE).read_text()
    # Must have protected _userland (not public readonly userland)
    assert "protected _userland" in content, (
        "route-module.ts does not have protected _userland"
    )
    # Must have a getter
    assert "get userland()" in content, (
        "route-module.ts does not have userland getter"
    )
    # Must NOT have public readonly userland
    assert "public readonly userland" not in content, (
        "route-module.ts still has public readonly userland (should be getter)"
    )


# [pr_diff] fail_to_pass
def test_module_accepts_userland_factory():
    """AppRouteRouteModuleOptions must accept a factory function for userland."""
    content = Path(MODULE).read_text()
    import re
    # The options interface should have userland that accepts a function type
    # On fix: readonly userland: AppRouteUserlandModule | (() => ...)
    # On base: extends RouteModuleOptions<...> (inherits plain userland)
    opts_match = re.search(
        r'interface\s+AppRouteRouteModuleOptions([\s\S]{0,600}?)readonly\s+resolvedPagePath',
        content,
    )
    assert opts_match is not None, "AppRouteRouteModuleOptions interface not found"
    opts_body = opts_match.group(1)
    # Must have a function type for userland (arrow function syntax)
    assert "() =>" in opts_body, (
        "AppRouteRouteModuleOptions does not accept factory function for userland"
    )
    # Must accept both direct module and factory
    assert "AppRouteUserlandModule" in opts_body, (
        "userland type doesn't reference AppRouteUserlandModule"
    )


# [pr_diff] fail_to_pass
def test_handle_calls_ensure_userland():
    """The handle() method must call ensureUserland() before resolving handlers."""
    content = Path(MODULE).read_text()
    import re
    # Find the execute/handle method that processes requests
    # On fix: await this.ensureUserland() is called before resolveHandler
    # On base: no ensureUserland call, uses this.resolve() or this.resolveWithGetter()

    # Check that ensureUserland is called in the request handling path
    handle_match = re.search(
        r'(execute|handle)\s*\([^)]*req:\s*NextRequest',
        content,
    )
    assert handle_match is not None, "handle/execute method not found"
    handle_start = handle_match.start()
    # Look at the next ~1000 chars for ensureUserland call
    handle_body = content[handle_start:handle_start + 1500]
    assert "ensureUserland" in handle_body, (
        "handle() does not call ensureUserland() before processing request"
    )
    # Verify resolveHandler is used (not old resolve method)
    assert "resolveHandler" in handle_body, (
        "handle() does not use resolveHandler() method"
    )


# ---------------------------------------------------------------------------
# Repo CI checks (pass_to_pass) — verify existing functionality not broken
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint_eslint():
    """ESLint passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        [
            "pnpm", "lint-eslint",
            "packages/next/src/server/route-modules/app-route/module.ts",
            "packages/next/src/build/templates/app-route.ts",
            "packages/next/src/export/routes/app-route.ts",
            "packages/next/src/server/route-modules/route-module.ts",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_ast_grep():
    """ast-grep scan passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "lint-ast-grep"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ast-grep scan failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_language():
    """Language lint (alex) passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "lint-language"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Language lint failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier():
    """Prettier formatting check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        [
            "pnpm",
            "prettier",
            "--check",
            "packages/next/src/server/route-modules/app-route/module.ts",
            "packages/next/src/build/templates/app-route.ts",
            "packages/next/src/export/routes/app-route.ts",
            "packages/next/src/server/route-modules/route-module.ts",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_error_codes():
    """Error codes check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "packages/next/check-error-codes.js"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Error codes check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"
