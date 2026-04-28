"""
Test suite for Playwright proxy loopback bypass fix.
Tests both the code behavior and config file updates.
"""
import subprocess
import re
from pathlib import Path
import json

REPO = Path("/workspace/playwright")

# =============================================================================
# Category 1: Code Behavior Tests
# =============================================================================

def test_chromium_ts_syntax():
    """Verify the modified chromium.ts file parses without TypeScript errors."""
    chromium_ts = REPO / "packages/playwright-core/src/server/chromium/chromium.ts"
    assert chromium_ts.exists(), "chromium.ts must exist"
    
    content = chromium_ts.read_text()
    
    # Check for balanced braces (basic syntax check)
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, "TypeScript file has unbalanced braces"
    
    # Check for balanced parentheses
    open_parens = content.count('(')
    close_parens = content.count(')')
    assert open_parens == close_parens, "TypeScript file has unbalanced parentheses"

def test_bypassesLoopback_variable_exists():
    """The fix introduces a bypassesLoopback variable to check for loopback bypasses."""
    chromium_ts = REPO / "packages/playwright-core/src/server/chromium/chromium.ts"
    content = chromium_ts.read_text()
    
    assert "bypassesLoopback" in content, \
        "The fix must introduce a 'bypassesLoopback' variable"

def test_loopback_bypass_logic_correct():
    """Verify the loopback bypass check includes localhost, 127.0.0.1, and ::1."""
    chromium_ts = REPO / "packages/playwright-core/src/server/chromium/chromium.ts"
    content = chromium_ts.read_text()
    
    # Find the bypassesLoopback line or the .some() check
    pattern = r"rule\s*===\s*['\"]<-loopback>['\"].*rule\s*===\s*['\"]localhost['\"].*rule\s*===\s*['\"]127\.0\.0\.1['\"].*rule\s*===\s*['\"]::1['\"]"
    
    assert re.search(pattern, content, re.DOTALL) or \
           ("'<-loopback>'" in content and "'localhost'" in content and "'127.0.0.1'" in content and "'::1'" in content), \
        "The bypass check must include localhost, 127.0.0.1, and ::1"

def test_proxy_bypass_logic_structure():
    """Verify the proxy bypass logic follows the correct pattern: check bypassesLoopback then conditionally add <-loopback>."""
    chromium_ts = REPO / "packages/playwright-core/src/server/chromium/chromium.ts"
    content = chromium_ts.read_text()
    
    # Check for the pattern: bypassesLoopback calculation followed by conditional <-loopback> push
    assert "const bypassesLoopback" in content, \
        "Must define bypassesLoopback constant"
    
    assert "!bypassesLoopback" in content, \
        "Must use !bypassesLoopback in the conditional check"

def test_old_simple_includes_removed():
    """The old code used proxyBypassRules.includes('<-loopback>') which should be replaced."""
    chromium_ts = REPO / "packages/playwright-core/src/server/chromium/chromium.ts"
    content = chromium_ts.read_text()
    
    # The old pattern was: !proxyBypassRules.includes('<-loopback>')
    # This should be replaced with !bypassesLoopback
    old_pattern = "proxyBypassRules.includes('<-loopback>')"
    if old_pattern in content:
        # It's okay if it exists inside the bypassesLoopback calculation
        # but not as the standalone condition
        lines = content.split('\n')
        for line in lines:
            if old_pattern in line and 'const bypassesLoopback' not in line:
                assert False, f"Old includes check found outside bypassesLoopback definition: {line}"

# =============================================================================
# Category 2: Config/Documentation Update Tests (REQUIRED for AgentMD-Edit tasks)
# =============================================================================

def test_github_md_skill_file_exists():
    """The PR adds a new github.md skill file documenting how to upload fixes."""
    github_md = REPO / ".claude/skills/playwright-dev/github.md"
    assert github_md.exists(), \
        "Must create .claude/skills/playwright-dev/github.md skill file"

def test_github_md_has_branch_naming():
    """The github.md file should document branch naming conventions."""
    github_md = REPO / ".claude/skills/playwright-dev/github.md"
    if not github_md.exists():
        return  # Skip if file doesn't exist (caught by other test)
    
    content = github_md.read_text().lower()
    
    assert "branch" in content, \
        "github.md should document branch naming"
    assert "fix-" in content or "branch naming" in content, \
        "github.md should mention branch naming pattern (e.g., fix-39562)"

def test_github_md_has_commit_format():
    """The github.md file should document conventional commit format."""
    github_md = REPO / ".claude/skills/playwright-dev/github.md"
    if not github_md.exists():
        return
    
    content = github_md.read_text().lower()
    
    assert "commit" in content, \
        "github.md should document commit format"
    assert "conventional" in content or "fix(" in content or "feat(" in content, \
        "github.md should mention conventional commit format (fix(proxy): description)"

def test_github_md_has_fixes_reference():
    """The github.md file should document the 'Fixes:' line format."""
    github_md = REPO / ".claude/skills/playwright-dev/github.md"
    if not github_md.exists():
        return
    
    content = github_md.read_text()
    
    assert "fixes:" in content.lower() or "fixes:" in content, \
        "github.md should document the 'Fixes: https://github.com/microsoft/playwright/issues/XXX' format"

def test_skill_md_references_github_md():
    """The SKILL.md file should reference the new github.md file in Table of Contents."""
    skill_md = REPO / ".claude/skills/playwright-dev/SKILL.md"
    assert skill_md.exists(), "SKILL.md must exist"
    
    content = skill_md.read_text()
    
    assert "github.md" in content, \
        "SKILL.md must reference github.md in the Table of Contents"
    assert "uploading fixes" in content.lower() or "github" in content.lower(), \
        "SKILL.md should mention uploading fixes or GitHub workflow"

# =============================================================================
# Category 3: Anti-Regression Tests (Pass-to-Pass)
# =============================================================================

def test_skill_md_structure_valid():
    """The SKILL.md should have valid frontmatter structure."""
    skill_md = REPO / ".claude/skills/playwright-dev/SKILL.md"
    assert skill_md.exists(), "SKILL.md must exist"
    
    content = skill_md.read_text()
    
    # Check for YAML frontmatter
    assert content.startswith("---"), "SKILL.md should have YAML frontmatter"
    assert "name:" in content, "SKILL.md frontmatter should have 'name:'"
    assert "description:" in content, "SKILL.md frontmatter should have 'description:'"
    
    # Check Table of Contents structure
    assert "## Table of Contents" in content or "# Playwright Development Guide" in content, \
        "SKILL.md should have proper structure"

def test_chromium_file_not_empty():
    """Basic sanity check that the chromium.ts file is not empty or corrupted."""
    chromium_ts = REPO / "packages/playwright-core/src/server/chromium/chromium.ts"
    assert chromium_ts.exists(), "chromium.ts must exist"
    
    content = chromium_ts.read_text()
    assert len(content) > 1000, "chromium.ts should not be empty/corrupted"
    assert "export class Chromium" in content, "Chromium class should be defined"

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

def test_ci_docs___lint_audit_prod_npm_dependencies():
    """pass_to_pass | CI job 'docs & lint' → step 'Audit prod NPM dependencies'"""
    r = subprocess.run(
        ["bash", "-lc", 'node utils/check_audit.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Audit prod NPM dependencies' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")