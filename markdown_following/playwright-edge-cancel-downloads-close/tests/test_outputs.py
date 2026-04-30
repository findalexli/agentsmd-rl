"""
Task: playwright-edge-cancel-downloads-close
Repo: playwright @ 72310c757282e397fcd280e85602adcdf0d581ca
PR:   40034

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"

DOWNLOAD_TS = f"{REPO}/packages/playwright-core/src/server/download.ts"
CR_BROWSER_TS = f"{REPO}/packages/playwright-core/src/server/chromium/crBrowser.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "npm ci 2>&1 >/dev/null && npm run build 2>&1 >/dev/null && npm run tsc"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


# [static] pass_to_pass
def test_repo_check_deps():
    """Repo's dependency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "npm ci 2>&1 >/dev/null && npm run build 2>&1 >/dev/null && npm run check-deps"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Check deps failed:\n{r.stderr[-500:]}"


# [static] pass_to_pass
def test_repo_lint_tests():
    """Repo's test linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "npm ci 2>&1 >/dev/null && npm run build 2>&1 >/dev/null && npm run lint-tests"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint tests failed:\n{r.stderr[-500:]}"


# [static] pass_to_pass
def test_repo_build():
    """Repo's build passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "npm ci 2>&1 >/dev/null && npm run build 2>&1 >/dev/null"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files have valid syntax (balanced braces)."""
    for fpath in [DOWNLOAD_TS, CR_BROWSER_TS]:
        src = Path(fpath).read_text()
        assert len(src) > 100, f"{fpath} appears empty or truncated"
        opens = src.count("{")
        closes = src.count("}")
        assert opens == closes, (
            f"Unbalanced braces in {fpath}: {opens} opens vs {closes} closes"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_download_cancel_method():
    """Download class exposes a cancel() method that calls cancelDownload."""
    # Use node subprocess to analyze the Download class in context
    script = r"""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright-core/src/server/download.ts', 'utf-8');

// Verify export class Download exists
if (src.indexOf('export class Download') === -1) {
    console.error('ERROR: export class Download not found');
    process.exit(1);
}

// Extract class body (everything from 'export class Download' to the end)
const classBody = src.slice(src.indexOf('export class Download'));

// Look for a cancel() method at class level (2-space indent, not inside constructor)
// Must be a standalone method, not just a lambda in the constructor
const lines = classBody.split('\n');
let inConstructor = false;
let braceDepth = 0;
let foundCancelMethod = false;

for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Track brace depth for constructor
    if (/^\s{2}constructor\s*\(/.test(line)) inConstructor = true;

    // Save current depth BEFORE counting braces on this line
    const currentDepth = braceDepth;

    for (const ch of line) {
        if (ch === '{') braceDepth++;
        if (ch === '}') braceDepth--;
    }

    // Exit constructor when we return to class body level
    if (inConstructor && braceDepth === 1) {
        inConstructor = false;
    }

    // At class body level (depth 1, not in constructor), look for cancel method
    if (!inConstructor && currentDepth === 1 && /^\s{2}cancel\s*\(/.test(line)) {
        foundCancelMethod = true;
    }

    if (braceDepth === 0 && i > 0) break; // class ended
}

if (!foundCancelMethod) {
    console.error('ERROR: No cancel() method found at class level on Download');
    process.exit(1);
}

// Verify cancel() body calls cancelDownload with an instance field
const cancelMatch = classBody.match(/cancel\s*\(\s*\)\s*(?::\s*[\w<>|]+\s*)?\{([\s\S]*?)\n\s{2}\}/);
if (cancelMatch) {
    const body = cancelMatch[1];
    if (!/cancelDownload\(this\.\w+\)/.test(body)) {
        console.error('ERROR: cancel() does not call cancelDownload(this.<field>)');
        process.exit(1);
    }
}

console.log('OK');
"""
    r = subprocess.run(
        ["node", "-e", script],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Download cancel() method check failed:\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_context_close_cancels_downloads():
    """CRBrowserContext cancels all downloads before disposing the browser context."""
    src = Path(CR_BROWSER_TS).read_text()

    # Find the actual disposeBrowserContext call (not the comment)
    # Look for the pattern with the await and send call
    dispose_idx = src.find("send('Target.disposeBrowserContext'")
    assert dispose_idx != -1, "disposeBrowserContext call not found in crBrowser.ts"

    # The 50 lines before disposeBrowserContext must reference download cancellation
    pre_dispose = src[:dispose_idx]
    recent_lines = pre_dispose.split("\n")[-50:]
    recent_block = "\n".join(recent_lines)

    # Accept various patterns: download.cancel(), d.cancel(), map(d => d.cancel()), etc.
    assert re.search(r"\.cancel\(\)", recent_block), (
        "No .cancel() call found before disposeBrowserContext in crBrowser.ts. "
        "Downloads must be cancelled before context disposal."
    )

    # Also verify _downloads is referenced (to confirm it's iterating downloads)
    assert "_downloads" in recent_block, (
        "No reference to _downloads found before disposeBrowserContext. "
        "Must iterate and cancel all context downloads."
    )


# [pr_diff] fail_to_pass
def test_cancel_uses_instance_field():
    """cancel() uses a stored instance field (this.xxx), not a closure-captured constructor arg."""
    src = Path(DOWNLOAD_TS).read_text()

    # Find a standalone cancel() method on the class
    cancel_match = re.search(
        r"(?:^  |\t)cancel\s*\(\s*\)\s*(?::\s*[\w<>|\s]+)?\{([\s\S]*?)\n(?:  |\t)\}",
        src,
        re.MULTILINE,
    )
    assert cancel_match, "No cancel() method found at class level on Download"

    cancel_body = cancel_match.group(1)

    # Must reference this.<something> — proves it uses an instance field, not a closure variable
    assert re.search(r"this\.\w+", cancel_body), (
        f"cancel() does not reference any instance field (this.xxx). "
        f"It should use a stored field, not a closure-captured variable. Body: {cancel_body.strip()}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Download.cancel() has real logic, not an empty body."""
    src = Path(DOWNLOAD_TS).read_text()

    # Look for cancel method body
    cancel_match = re.search(
        r"cancel\s*\(\s*\)\s*(?::\s*[\w<>|\s]+)?\{([\s\S]*?)\n\s{2}\}",
        src,
    )
    assert cancel_match, "No cancel() method found"

    body = cancel_match.group(1).strip()
    assert len(body) > 5, f"cancel() body is too short to be real logic: '{body}'"
    assert "cancelDownload" in body, (
        f"cancel() does not call cancelDownload. Body: '{body}'"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:99-102 @ 72310c757282e397fcd280e85602adcdf0d581ca
def test_cancel_method_public_naming():
    """cancel() follows CLAUDE.md naming convention: public method (no underscore) since it's used in other files."""
    src = Path(DOWNLOAD_TS).read_text()
    cr_src = Path(CR_BROWSER_TS).read_text()

    # Per CLAUDE.md lines 99-102: For exported classes,
    #   method() (public) — used in other files
    #   _method() (no private) — used by other code in the same file only
    # cancel() is called from crBrowser.ts → must be public (no underscore prefix)

    # Verify Download has cancel() (not _cancel)
    has_cancel = re.search(r"^\s{2}cancel\s*\(", src, re.MULTILINE)
    has_underscore_cancel = re.search(r"^\s{2}_cancel\s*\(", src, re.MULTILINE)

    assert has_cancel, (
        "Download class needs a cancel() method (public name, no underscore). "
        "Per CLAUDE.md: methods used in other files must use public naming."
    )
    assert not has_underscore_cancel, (
        "cancel method uses _cancel() but is called from crBrowser.ts (another file). "
        "Per CLAUDE.md line 102: methods used in other files must be public: method() not _method()."
    )

    # Confirm cross-file usage exists
    assert ".cancel()" in cr_src, (
        "cancel() is not called from crBrowser.ts — cross-file usage expected"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_lint_snippets_npm():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_pip():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pip install -r utils/doclint/linting-code-snippets/python/requirements.txt'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_mvn():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'mvn package'], cwd=os.path.join(REPO, 'utils/doclint/linting-code-snippets/java'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_node():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'node utils/doclint/linting-code-snippets/cli.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npm():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npx():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npx playwright install --with-deps'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npm_2():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_verify_clean_tree():
    """pass_to_pass | CI job 'docs & lint' → step 'Verify clean tree'"""
    r = subprocess.run(
        ["bash", "-lc", 'if [[ -n $(git status -s) ]]; then\n  echo "ERROR: tree is dirty after npm run build:"\n  git diff\n  exit 1\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify clean tree' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_audit_prod_npm_dependencies():
    """pass_to_pass | CI job 'docs & lint' → step 'Audit prod NPM dependencies'"""
    r = subprocess.run(
        ["bash", "-lc", 'node utils/check_audit.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Audit prod NPM dependencies' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")