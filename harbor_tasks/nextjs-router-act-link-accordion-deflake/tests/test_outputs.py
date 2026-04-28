"""
Task: nextjs-router-act-link-accordion-deflake
Repo: vercel/next.js @ 8283b1260ba3eb187baf20727e739fbd8ba7bbf6
PR:   91492

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
TEST_DIR = f"{REPO}/test/e2e/app-dir/segment-cache/staleness"
PER_PAGE_DIR = f"{TEST_DIR}/app/per-page-config"

# ---------------------------------------------------------------------------
# Pass-to-pass (static) - existing infrastructure checks
# ---------------------------------------------------------------------------

def test_link_accordion_component_exists():
    """LinkAccordion component exists at the expected path (pre-existing fixture)."""
    component_path = Path(f"{TEST_DIR}/components/link-accordion.tsx")
    assert component_path.exists(), f"LinkAccordion component missing: {component_path}"
    content = component_path.read_text()
    assert "LinkAccordion" in content, "LinkAccordion component must export the component"
    assert "data-link-accordion" in content, "LinkAccordion must use data-link-accordion attribute"

# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - repo CI/CD checks
# ---------------------------------------------------------------------------

def test_repo_prettier_segment_cache():
    """Repo's Prettier check passes on segment-cache test files (pass_to_pass)."""
    r = subprocess.run(
        ["./node_modules/.bin/prettier", "--check", TEST_DIR],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"

def test_repo_deps_install():
    """Repo dependencies install cleanly (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Dependencies install failed:\n{r.stderr[-500:]}"

def test_repo_ast_grep_segment_cache():
    """Repo's ast-grep static analysis passes on segment-cache files (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "ast-grep", "scan", TEST_DIR],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ast-grep scan failed:\n{r.stderr[-500:]}"

def test_repo_prettier_segment_cache_src():
    """Repo's Prettier check passes on segment-cache source TSX files (pass_to_pass)."""
    r = subprocess.run(
        ["./node_modules/.bin/prettier", "--check", f"{TEST_DIR}/components", f"{TEST_DIR}/app"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check on source files failed:\n{r.stderr[-500:]}"

def test_repo_alex_next_docs():
    """Repo's language linting (alex) passes on Next.js documentation (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "alex", "-q", f"{REPO}/packages/next/README.md"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Alex language check failed:\n{r.stderr[-500:]}"

def test_repo_check_error_codes():
    """Repo's error code check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "packages/next/check-error-codes.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Error code check failed:\n{r.stderr[-500:]}"

def test_repo_eslint_segment_cache():
    """Repo's ESLint check passes on segment-cache test files (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "--config", "eslint.config.mjs",
         f"{TEST_DIR}/segment-cache-per-page-dynamic-stale-time.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint check failed:\n{r.stderr[-500:]}"

def test_repo_prettier_src():
    """Repo's Prettier check passes on segment-cache source TSX files (pass_to_pass)."""
    r = subprocess.run(
        ["./node_modules/.bin/prettier", "--check",
         f"{TEST_DIR}/components",
         f"{TEST_DIR}/app"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check on source files failed:\n{r.stderr[-500:]}"

def test_repo_alex_docs():
    """Repo's language linting (alex) passes on Next.js docs (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "alex", "-q", f"{REPO}/docs"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Alex language check failed:\n{r.stderr[-500:]}"

# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - behavioral code tests
# ---------------------------------------------------------------------------

def test_hub_pages_valid_tsx():
    """New intermediate hub pages exist as valid TSX with correct imports and default export."""
    script = Path(REPO) / "_eval_hub_check.js"
    script.write_text(r"""
const ts = require("typescript");
const fs = require("fs");
const path = require("path");

const base = process.argv[2];
const knownDirs = new Set(["dynamic-stale-10", "dynamic-stale-60", "parallel-slots"]);
const entries = fs.readdirSync(base, { withFileTypes: true });

// Find new page directories (hub pages added by the fix)
const hubDirs = entries.filter(d => d.isDirectory() && !knownDirs.has(d.name));
if (hubDirs.length < 3) {
    console.error("Need at least 3 new intermediate page directories, found " + hubDirs.length);
    console.error("All dirs: " + entries.filter(d => d.isDirectory()).map(d => d.name).join(", "));
    process.exit(1);
}

const errors = [];
for (const dir of hubDirs) {
    const pagePath = path.join(base, dir.name, "page.tsx");
    if (!fs.existsSync(pagePath)) {
        errors.push(dir.name + ": missing page.tsx");
        continue;
    }
    const src = fs.readFileSync(pagePath, "utf-8");

    // Parse as TSX using TypeScript compiler API
    const sf = ts.createSourceFile(pagePath, src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

    // Collect import module specifiers via AST
    const importSources = [];
    ts.forEachChild(sf, node => {
        if (ts.isImportDeclaration(node) &&
            node.moduleSpecifier &&
            ts.isStringLiteral(node.moduleSpecifier)) {
            importSources.push(node.moduleSpecifier.text);
        }
    });

    // Must import from link-accordion component (for controlled prefetching)
    if (!importSources.some(s => s.includes("link-accordion"))) {
        errors.push(dir.name + ": missing link-accordion import");
    }
    // Must import from next/server (for connection() / dynamic rendering)
    if (!importSources.some(s => s === "next/server")) {
        errors.push(dir.name + ": missing next/server import for dynamic rendering");
    }
    // Must import from react (for Suspense)
    if (!importSources.some(s => s === "react")) {
        errors.push(dir.name + ": missing react import");
    }

    // Must have a default export function (Next.js page component)
    let hasDefaultExport = false;
    ts.forEachChild(sf, node => {
        if (ts.isFunctionDeclaration(node) && node.modifiers) {
            const kinds = node.modifiers.map(m => m.kind);
            if (kinds.includes(ts.SyntaxKind.ExportKeyword) &&
                kinds.includes(ts.SyntaxKind.DefaultKeyword)) {
                hasDefaultExport = true;
            }
        }
    });
    if (!hasDefaultExport) {
        errors.push(dir.name + ": missing default export function (Next.js page)");
    }
}

if (errors.length > 0) {
    console.error(errors.join("\n"));
    process.exit(1);
}
console.log("OK: " + hubDirs.length + " hub pages validated");
""")
    try:
        result = subprocess.run(
            ["node", str(script), PER_PAGE_DIR],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert result.returncode == 0, f"Hub page validation failed:\n{result.stderr}"
    finally:
        script.unlink(missing_ok=True)

def test_stale_pages_link_to_hub_pages():
    """Dynamic stale pages import LinkAccordion for controlled hub navigation."""
    script = Path(REPO) / "_eval_stale_check.js"
    script.write_text(r"""
const ts = require("typescript");
const fs = require("fs");
const path = require("path");

const base = process.argv[2];
const stalePages = ["dynamic-stale-10", "dynamic-stale-60"];
const errors = [];

for (const pageName of stalePages) {
    const pagePath = path.join(base, pageName, "page.tsx");
    if (!fs.existsSync(pagePath)) {
        errors.push(pageName + ": page.tsx missing");
        continue;
    }
    const src = fs.readFileSync(pagePath, "utf-8");

    // Parse as TSX using TypeScript compiler API
    const sf = ts.createSourceFile(pagePath, src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

    // Check for link-accordion import via AST
    const importSources = [];
    ts.forEachChild(sf, node => {
        if (ts.isImportDeclaration(node) &&
            node.moduleSpecifier &&
            ts.isStringLiteral(node.moduleSpecifier)) {
            importSources.push(node.moduleSpecifier.text);
        }
    });

    if (!importSources.some(s => s.includes("link-accordion"))) {
        errors.push(pageName + ": must import LinkAccordion for controlled hub navigation");
    }
}

if (errors.length > 0) {
    console.error(errors.join("\n"));
    process.exit(1);
}
console.log("OK: stale pages updated with LinkAccordion imports");
""")
    try:
        result = subprocess.run(
            ["node", str(script), PER_PAGE_DIR],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert result.returncode == 0, f"Stale page validation failed:\n{result.stderr}"
    finally:
        script.unlink(missing_ok=True)

def test_deflaked_test_forward_navigation():
    """The flaky test uses forward navigation to intermediate pages instead of browser.back()."""
    script = Path(REPO) / "_eval_test_nav_check.js"
    script.write_text(r"""
const ts = require("typescript");
const fs = require("fs");

const testFile = process.argv[2];
const source = fs.readFileSync(testFile, "utf-8");

// Parse the test file using TypeScript compiler API
const sf = ts.createSourceFile(testFile, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

// Walk AST to find the it() call for "per-page value overrides global"
function findTestCall(node) {
    if (ts.isCallExpression(node)) {
        const expr = node.expression;
        if (ts.isIdentifier(expr) && expr.text === "it" && node.arguments.length > 0) {
            const arg = node.arguments[0];
            if (ts.isStringLiteral(arg) &&
                arg.text.includes("per-page value overrides global")) {
                return node;
            }
        }
    }
    let found = null;
    ts.forEachChild(node, child => {
        if (!found) found = findTestCall(child);
    });
    return found;
}

const testCall = findTestCall(sf);
if (!testCall) {
    console.error("Cannot find test: 'per-page value overrides global'");
    process.exit(1);
}

// Extract the source text of the test block
const testText = source.substring(testCall.pos, testCall.end);

// Verify no actual await browser.back() calls remain in this test
// (comments mentioning browser.back() are OK — only actual code calls matter)
const backMatches = testText.match(/await\s+browser\.back\(\)/g) || [];
if (backMatches.length > 0) {
    console.error("Test still uses await browser.back() (" + backMatches.length +
        " calls). Must use forward navigation to avoid BFCache flakiness.");
    process.exit(1);
}

// Verify the test navigates to intermediate pages (not the known existing pages)
const knownPages = new Set(["dynamic-stale-10", "dynamic-stale-60", "parallel-slots"]);
const pageRefs = testText.match(/\/per-page-config\/([a-z0-9-]+)/g) || [];
const intermediatePages = new Set(
    pageRefs.map(r => r.split("/").pop()).filter(n => !knownPages.has(n))
);

if (intermediatePages.size < 3) {
    console.error("Test should navigate to at least 3 unique intermediate pages, found " +
        intermediatePages.size + ": " + [...intermediatePages].join(", "));
    process.exit(1);
}

console.log("OK: 0 browser.back() calls, " + intermediatePages.size + " intermediate pages");
""")
    test_file = f"{TEST_DIR}/segment-cache-per-page-dynamic-stale-time.test.ts"
    try:
        result = subprocess.run(
            ["node", str(script), test_file],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert result.returncode == 0, f"Test navigation check failed:\n{result.stderr}"
    finally:
        script.unlink(missing_ok=True)

# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - documentation tests
# ---------------------------------------------------------------------------

def test_agents_md_documents_pattern():
    """AGENTS.md documents the LinkAccordion/router-act testing pattern."""
    agents_md = Path(REPO) / "AGENTS.md"
    assert agents_md.exists(), "AGENTS.md must exist"
    content = agents_md.read_text()
    content_lower = content.lower()

    assert "linkaccordion" in content_lower or "link-accordion" in content_lower, \
        "AGENTS.md must document the LinkAccordion pattern for prefetch control"
    assert "browser.back()" in content or "bfcache" in content_lower, \
        "AGENTS.md must warn about browser.back()/BFCache causing test flakiness"
    assert "router-act" in content_lower, \
        "AGENTS.md must reference the router-act skill"

def test_router_act_skill():
    """Router-act skill exists with frontmatter and documents key testing patterns."""
    script = Path(REPO) / "_eval_skill_check.js"
    script.write_text(r"""
const fs = require("fs");
const path = require("path");

const dir = ".agents/skills/router-act";
if (!fs.existsSync(dir)) {
    console.error("Missing skill directory: " + dir);
    process.exit(1);
}

const mds = fs.readdirSync(dir).filter(f => f.endsWith(".md"));
if (mds.length === 0) {
    console.error("No .md file found in " + dir);
    process.exit(1);
}

const content = fs.readFileSync(path.join(dir, mds[0]), "utf-8");

// Validate YAML frontmatter
if (!content.startsWith("---")) {
    console.error("Skill file must start with YAML frontmatter (---)");
    process.exit(1);
}
const fmEnd = content.indexOf("---", 3);
if (fmEnd < 0) {
    console.error("Frontmatter not properly closed");
    process.exit(1);
}
const fm = content.substring(3, fmEnd);
if (!/name:\s*router-act/.test(fm)) {
    console.error("Frontmatter must include name: router-act");
    process.exit(1);
}
if (!/description:/.test(fm)) {
    console.error("Frontmatter must include a description field");
    process.exit(1);
}

// Check key documentation topics
const lower = content.toLowerCase();
const errors = [];
if (!lower.includes("linkaccordion") && !lower.includes("link-accordion"))
    errors.push("Must document LinkAccordion pattern");
if (!lower.includes("no-requests"))
    errors.push("Must document no-requests assertion");
if (!lower.includes("hub"))
    errors.push("Must document hub/intermediate page pattern");
if (!lower.includes("browser.back()"))
    errors.push("Must warn about browser.back() flakiness");
if (!lower.includes("bfcache"))
    errors.push("Must explain BFCache state restoration issue");
if (!lower.includes("includes"))
    errors.push("Must document includes assertion matching");
if (!lower.includes("requestidlecallback"))
    errors.push("Must explain requestIdleCallback interception");

if (errors.length > 0) {
    console.error(errors.join("\n"));
    process.exit(1);
}
console.log("OK: skill validated");
""")
    try:
        result = subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=15, cwd=REPO,
        )
        assert result.returncode == 0, f"Skill validation failed:\n{result.stderr}"
    finally:
        script.unlink(missing_ok=True)


