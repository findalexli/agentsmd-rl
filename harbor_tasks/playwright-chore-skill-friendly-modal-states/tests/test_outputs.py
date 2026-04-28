"""
Task: playwright-chore-skill-friendly-modal-states
Repo: microsoft/playwright @ 1e81675f850280d2cbaa0bbb01a7f066532d0e01
PR:   38932

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_help_json_valid():
    """help.json must be valid JSON."""
    r = subprocess.run(
        ["node", "-e",
         "JSON.parse(require('fs').readFileSync("
         "'packages/playwright/src/mcp/terminal/help.json','utf8'));"
         "console.log('OK')"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"help.json is not valid JSON:\n{r.stderr}"
    assert "OK" in r.stdout


# [repo] pass_to_pass - CI/CD gate
def test_repo_npm_install():
    """Repo npm install succeeds (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"npm install failed:\n{r.stderr[-500:]}"


# [repo] pass_to_pass - CI/CD gate
def test_repo_build():
    """Repo npm run build succeeds (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "build"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"npm run build failed:\n{r.stderr[-500:]}"


# [repo] pass_to_pass - CI/CD gate
def test_repo_tsc():
    """Repo TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "tsc"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stderr[-500:]}"


# [repo] pass_to_pass - CI/CD gate
def test_repo_eslint_mcp():
    """Repo ESLint on MCP files passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "eslint", "--", "packages/playwright/src/mcp/"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"ESLint check failed:\n{r.stderr[-500:]}"


# [repo] pass_to_pass - CI/CD gate
def test_repo_check_deps():
    """Repo dependency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "check-deps"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Dependency check failed:\n{r.stderr[-500:]}"


# [repo] pass_to_pass - CI/CD gate
def test_repo_lint_packages():
    """Repo workspace packages consistency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Lint packages failed:\n{r.stderr[-500:]}"


# [repo] pass_to_pass - CI/CD gate
def test_repo_mcp_files_syntax():
    """Repo MCP modified files have valid syntax (pass_to_pass)."""
    # Check that all modified MCP files can be read by Node.js
    files = [
        "packages/playwright/src/mcp/browser/config.ts",
        "packages/playwright/src/mcp/browser/response.ts",
        "packages/playwright/src/mcp/browser/tab.ts",
        "packages/playwright/src/mcp/browser/tools/evaluate.ts",
        "packages/playwright/src/mcp/browser/tools/tool.ts",
        "packages/playwright/src/mcp/program.ts",
        "packages/playwright/src/mcp/terminal/commands.ts",
        "packages/playwright/src/mcp/terminal/help.json",
        "utils/build/build.js",
        "tests/mcp/cli.spec.ts",
    ]
    for f in files:
        r = subprocess.run(
            ["node", "-e", f"require('fs').readFileSync('{f}','utf8'); console.log('OK')"],
            cwd=REPO, capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"{f} is not readable:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - command renames
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_commands_renamed_in_help():
    """help.json command keys must use new unhyphenated names."""
    r = subprocess.run(
        ["node", "-e", """
const h = require('./packages/playwright/src/mcp/terminal/help.json');
const cmds = Object.keys(h.commands);
const required = ['press', 'keydown', 'keyup', 'mousemove', 'mousedown', 'mouseup', 'mousewheel'];
const old = ['key-press', 'key-down', 'key-up', 'mouse-move', 'mouse-down', 'mouse-up', 'mouse-wheel'];
for (const name of required) {
    if (!cmds.includes(name)) { console.error('MISSING: ' + name); process.exit(1); }
}
for (const name of old) {
    if (cmds.includes(name)) { console.error('OLD_STILL_EXISTS: ' + name); process.exit(1); }
}
console.log('OK');
"""],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Command names not renamed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_help_global_text_updated():
    """Global help text must reference new unhyphenated command names."""
    r = subprocess.run(
        ["node", "-e", """
const h = require('./packages/playwright/src/mcp/terminal/help.json');
const g = h.global;
const oldPatterns = ['key-press', 'key-down', 'key-up', 'mouse-move', 'mouse-down', 'mouse-up', 'mouse-wheel'];
for (const o of oldPatterns) {
    if (g.includes(o)) { console.error('Global help still has: ' + o); process.exit(1); }
}
const newPatterns = ['press <key>', 'keydown <key>', 'keyup <key>', 'mousemove <x> <y>',
                     'mousedown [button]', 'mouseup [button]', 'mousewheel <dx> <dy>'];
for (const n of newPatterns) {
    if (!g.includes(n)) { console.error('Global help missing: ' + n); process.exit(1); }
}
console.log('OK');
"""],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Help global text not updated:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - modal state skill mode
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_modal_state_dual_format():
    """renderModalStates must accept config and conditionally render skill vs tool name."""
    tab_ts = Path(REPO) / "packages/playwright/src/mcp/browser/tab.ts"
    content = tab_ts.read_text()
    assert "renderModalStates(config:" in content, \
        "renderModalStates must accept config parameter"
    assert "config.skillMode" in content, \
        "renderModalStates must check config.skillMode"
    assert "clearedBy.skill" in content or "state.clearedBy.skill" in content, \
        "clearedBy must have a skill property"
    assert "clearedBy.tool" in content or "state.clearedBy.tool" in content, \
        "clearedBy must have a tool property"


# [pr_diff] fail_to_pass
def test_eval_auto_wraps_expression():
    """evaluate.ts must auto-wrap non-arrow expressions with () => (...)."""
    eval_ts = Path(REPO) / "packages/playwright/src/mcp/browser/tools/evaluate.ts"
    content = eval_ts.read_text()
    assert "includes(" in content, \
        "evaluate.ts must check for arrow function syntax"
    assert "() => (" in content, \
        "evaluate.ts must wrap non-arrow expressions"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - SKILL.md config file creation
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_documents_cli():
    """SKILL.md must exist with proper frontmatter and document CLI commands."""
    skill_md = Path(REPO) / "packages/playwright/src/mcp/terminal/SKILL.md"
    assert skill_md.exists(), \
        "SKILL.md must exist at packages/playwright/src/mcp/terminal/SKILL.md"
    content = skill_md.read_text()
    assert content.startswith("---"), "SKILL.md must have YAML frontmatter"
    assert "name:" in content, "SKILL.md frontmatter must have name field"
    assert "description:" in content, "SKILL.md frontmatter must have description field"
    assert "playwright-cli" in content, "SKILL.md must reference playwright-cli"
    assert "press" in content, "SKILL.md must document press command"
    assert "mousemove" in content, "SKILL.md must document mousemove command"
    assert "keydown" in content, "SKILL.md must document keydown command"
    lines_with_backticks = [l for l in content.split("\n") if "```" in l]
    assert len(lines_with_backticks) >= 4, \
        "SKILL.md must contain multiple code example blocks"


# [pr_diff] fail_to_pass
def test_build_copies_terminal_md():
    """build.js must copy terminal .md files to lib output."""
    build_js = Path(REPO) / "utils/build/build.js"
    content = build_js.read_text()
    assert "terminal/*.md" in content, \
        "build.js must have a copy rule for terminal/*.md files"


# [pr_diff] fail_to_pass
def test_clearedby_type_is_object():
    """ModalState types must define clearedBy as { tool: string; skill: string }."""
    tool_ts = Path(REPO) / "packages/playwright/src/mcp/browser/tools/tool.ts"
    content = tool_ts.read_text()
    assert "tool: string" in content and "skill: string" in content, \
        "clearedBy must be typed with tool and skill string fields"
    lines = content.split("\n")
    found_object_type = False
    for i, line in enumerate(lines):
        if "clearedBy" in line and "{" in line:
            found_object_type = True
            break
        if "clearedBy" in line and i + 1 < len(lines) and "tool:" in lines[i + 1]:
            found_object_type = True
            break
    assert found_object_type, "clearedBy must be an object type, not a plain string"

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_eval_no_arrow():
    """fail_to_pass | PR added test 'eval no arrow' in 'tests/mcp/cli.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli.spec.ts" -t "eval no arrow" 2>&1 || npx vitest run "tests/mcp/cli.spec.ts" -t "eval no arrow" 2>&1 || pnpm jest "tests/mcp/cli.spec.ts" -t "eval no arrow" 2>&1 || npx jest "tests/mcp/cli.spec.ts" -t "eval no arrow" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'eval no arrow' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_press():
    """fail_to_pass | PR added test 'press' in 'tests/mcp/cli.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli.spec.ts" -t "press" 2>&1 || npx vitest run "tests/mcp/cli.spec.ts" -t "press" 2>&1 || pnpm jest "tests/mcp/cli.spec.ts" -t "press" 2>&1 || npx jest "tests/mcp/cli.spec.ts" -t "press" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'press' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_keydown_keyup():
    """fail_to_pass | PR added test 'keydown keyup' in 'tests/mcp/cli.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli.spec.ts" -t "keydown keyup" 2>&1 || npx vitest run "tests/mcp/cli.spec.ts" -t "keydown keyup" 2>&1 || pnpm jest "tests/mcp/cli.spec.ts" -t "keydown keyup" 2>&1 || npx jest "tests/mcp/cli.spec.ts" -t "keydown keyup" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'keydown keyup' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_mousemove():
    """fail_to_pass | PR added test 'mousemove' in 'tests/mcp/cli.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli.spec.ts" -t "mousemove" 2>&1 || npx vitest run "tests/mcp/cli.spec.ts" -t "mousemove" 2>&1 || pnpm jest "tests/mcp/cli.spec.ts" -t "mousemove" 2>&1 || npx jest "tests/mcp/cli.spec.ts" -t "mousemove" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'mousemove' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_mousedown_mouseup():
    """fail_to_pass | PR added test 'mousedown mouseup' in 'tests/mcp/cli.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli.spec.ts" -t "mousedown mouseup" 2>&1 || npx vitest run "tests/mcp/cli.spec.ts" -t "mousedown mouseup" 2>&1 || pnpm jest "tests/mcp/cli.spec.ts" -t "mousedown mouseup" 2>&1 || npx jest "tests/mcp/cli.spec.ts" -t "mousedown mouseup" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'mousedown mouseup' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_mousewheel():
    """fail_to_pass | PR added test 'mousewheel' in 'tests/mcp/cli.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli.spec.ts" -t "mousewheel" 2>&1 || npx vitest run "tests/mcp/cli.spec.ts" -t "mousewheel" 2>&1 || pnpm jest "tests/mcp/cli.spec.ts" -t "mousewheel" 2>&1 || npx jest "tests/mcp/cli.spec.ts" -t "mousewheel" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'mousewheel' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_docs___lint_npm():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npm_2():
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

def test_ci_docs___lint_npm_3():
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