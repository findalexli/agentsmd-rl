"""
Task: nextjs-turbopack-build-all-script
Repo: vercel/next.js @ 46761a321042e8ac1863f4cfc8d73d527956e181
PR:   90543

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This task verifies:
1. Code changes: build-all script added, build renamed to build-native-auto in turbo.jsonc
2. Config changes: AGENTS.md updated to distinguish pnpm build vs pnpm build-all
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"


def _read_json(path: str) -> dict:
    """Read and parse a JSON file."""
    content = Path(path).read_text()
    return json.loads(content)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) -- CI command checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_prettier_check():
    """Modified JSON files pass Prettier formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "package.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"package.json failed prettier check:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_next_swc_prettier_check():
    """packages/next-swc/package.json passes Prettier formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "packages/next-swc/package.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"packages/next-swc/package.json failed prettier check:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_turbo_json_prettier_check():
    """Root turbo.json passes Prettier formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "turbo.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"turbo.json failed prettier check:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_package_json_valid():
    """Root package.json is valid JSON (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "JSON.parse(require('fs').readFileSync('package.json', 'utf8')); console.log('OK')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"package.json is not valid JSON:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_next_swc_package_json_valid():
    """packages/next-swc/package.json is valid JSON (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "JSON.parse(require('fs').readFileSync('packages/next-swc/package.json', 'utf8')); console.log('OK')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"packages/next-swc/package.json is not valid JSON:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_turbo_jsonc_exists():
    """packages/next-swc/turbo.jsonc or turbo.json exists and is readable (pass_to_pass)."""
    jsonc_path = f"{REPO}/packages/next-swc/turbo.jsonc"
    json_path = f"{REPO}/packages/next-swc/turbo.json"
    r1 = subprocess.run(
        ["test", "-r", jsonc_path],
        capture_output=True, text=True, timeout=60,
    )
    r2 = subprocess.run(
        ["test", "-r", json_path],
        capture_output=True, text=True, timeout=60,
    )
    assert r1.returncode == 0 or r2.returncode == 0, \
        f"Neither turbo.jsonc nor turbo.json is readable"


# [repo_tests] pass_to_pass
def test_repo_build_script_exists():
    """Root package.json has build script (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-p", "require('./package.json').scripts.build"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"build script not found:\n{r.stderr[-500:]}"
    assert "turbo" in r.stdout, f"build script should use turbo: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_agents_md_exists():
    """AGENTS.md exists and is readable (pass_to_pass)."""
    r = subprocess.run(
        ["test", "-r", f"{REPO}/AGENTS.md"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"AGENTS.md not readable:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - turbo.json or turbo.jsonc must exist with expected structure
def test_repo_turbo_json_valid():
    """packages/next-swc/turbo.json (original) or turbo.jsonc (after patch) exists with valid structure."""
    turbo_path = f"{REPO}/packages/next-swc/turbo.json"
    jsonc_path = f"{REPO}/packages/next-swc/turbo.jsonc"

    r = subprocess.run(
        ["test", "-r", turbo_path],
        capture_output=True, text=True, timeout=60,
    )
    if r.returncode == 0:
        r = subprocess.run(
            ["node", "-e",
             f"const turbo=require('{REPO}/packages/next-swc/turbo.json'); " +
             "if (!turbo.tasks || !turbo.tasks.build) { console.error('Missing build task'); process.exit(1); } " +
             "if (!turbo.tasks['rust-check']) { console.error('Missing rust-check'); process.exit(1); } " +
             "console.log('OK');"],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"turbo.json validation failed:\n{r.stderr[-500:]}"
    else:
        r = subprocess.run(
            ["test", "-r", jsonc_path],
            capture_output=True, text=True, timeout=60,
        )
        assert r.returncode == 0, f"Neither turbo.json nor turbo.jsonc exists"


# [repo_tests] pass_to_pass
def test_repo_root_scripts_valid():
    """Root package.json has expected CI scripts: build, lint, test-unit (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e",
         "const pkg=require('./package.json'); " +
         "const required=['build', 'lint', 'test-unit', 'test-types']; " +
         "const missing=required.filter(s=>!pkg.scripts[s]); " +
         "if (missing.length>0) { console.error('Missing scripts:', missing); process.exit(1); } " +
         "console.log('OK');"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Root package.json scripts validation failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_agents_md_readable():
    """AGENTS.md is readable via Node.js fs (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e",
         "const fs=require('fs'); " +
         "fs.accessSync('AGENTS.md', fs.constants.R_OK); " +
         "console.log('OK');"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"AGENTS.md not readable:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_next_swc_package_scripts_valid():
    """packages/next-swc/package.json has expected build scripts (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e",
         "const pkg=require('./packages/next-swc/package.json'); " +
         "if (!pkg.scripts) { console.error('No scripts'); process.exit(1); } " +
         "/* Base commit has \"build\", gold patch has \"build-native-auto\" */\n" +
         "const hasBuild = pkg.scripts['build'] || pkg.scripts['build-native-auto']; " +
         "if (!hasBuild) { console.error('Missing build or build-native-auto script'); process.exit(1); } " +
         "const required=['clean', 'build-native']; " +
         "const missing=required.filter(s=>!pkg.scripts[s]); " +
         "if (missing.length>0) { console.error('Missing scripts:', missing); process.exit(1); } " +
         "console.log('OK');"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"next-swc package.json scripts validation failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_turbo_json_tasks_exist():
    """packages/next-swc/turbo.json or turbo.jsonc has expected tasks including build and rust-check (pass_to_pass)."""
    turbo_path = f"{REPO}/packages/next-swc/turbo.json"
    jsonc_path = f"{REPO}/packages/next-swc/turbo.jsonc"

    r_json = subprocess.run(
        ["test", "-r", turbo_path],
        capture_output=True, text=True, timeout=60,
    )
    if r_json.returncode == 0:
        r = subprocess.run(
            ["node", "-e",
             "const turbo=require('./packages/next-swc/turbo.json'); " +
             "if (!turbo.tasks) { console.error('No tasks'); process.exit(1); } " +
             "if (!turbo.tasks.build && !turbo.tasks['build-native-auto']) { " +
             "  console.error('Missing build or build-native-auto task'); process.exit(1); } " +
             "if (!turbo.tasks['rust-check']) { console.error('Missing rust-check'); process.exit(1); } " +
             "console.log('OK');"],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
    else:
        r = subprocess.run(
            ["test", "-r", jsonc_path],
            capture_output=True, text=True, timeout=60,
        )
        if r.returncode != 0:
            r = subprocess.run(
                ["node", "-e", "console.error('Neither turbo.json nor turbo.jsonc exists'); process.exit(1);"],
                capture_output=True, text=True, timeout=60, cwd=REPO,
            )
        else:
            r = subprocess.run(
                ["node", "-e", "console.log('OK');"],
                capture_output=True, text=True, timeout=60, cwd=REPO,
            )
    assert r.returncode == 0, f"turbo.json/turbo.jsonc tasks validation failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_json_syntax_valid():
    """Modified JSON files must be syntactically valid."""
    root_pkg = Path(f"{REPO}/package.json")
    next_swc_pkg = Path(f"{REPO}/packages/next-swc/package.json")

    _read_json(str(root_pkg))
    _read_json(str(next_swc_pkg))


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_build_all_script_exists():
    """Root package.json must have build-all script that includes build-native-auto task."""
    r = subprocess.run(
        ["node", "-e",
         "const pkg = require('./package.json'); " +
         "const scripts = pkg.scripts || {}; " +
         "if (!scripts['build-all']) { " +
         "  console.error('FAIL: build-all script does not exist'); " +
         "  process.exit(1); " +
         "} " +
         "const buildAll = scripts['build-all']; " +
         "const hasTurbo = buildAll.includes('turbo run'); " +
         "const hasBuildNativeAuto = buildAll.includes('build-native-auto'); " +
         "if (!hasTurbo) { " +
         "  console.error('FAIL: build-all does not use turbo run'); " +
         "  process.exit(1); " +
         "} " +
         "if (!hasBuildNativeAuto) { " +
         "  console.error('FAIL: build-all does not include build-native-auto task'); " +
         "  process.exit(1); " +
         "} " +
         "console.log('OK: build-all script correctly configured');"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"build-all script validation failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_next_swc_script_renamed():
    """packages/next-swc/package.json build script must be renamed to build-native-auto."""
    r = subprocess.run(
        ["node", "-e",
         "const pkg = require('./packages/next-swc/package.json'); " +
         "const scripts = pkg.scripts || {}; " +
         "if (scripts.build && scripts.build.includes('maybe-build-native')) { " +
         "  console.error('FAIL: Old build script still calls maybe-build-native.mjs'); " +
         "  process.exit(1); " +
         "} " +
         "if (!scripts['build-native-auto']) { " +
         "  console.error('FAIL: build-native-auto script does not exist'); " +
         "  process.exit(1); " +
         "} " +
         "const autoScript = scripts['build-native-auto']; " +
         "if (!autoScript.includes('maybe-build-native')) { " +
         "  console.error('FAIL: build-native-auto does not call maybe-build-native.mjs'); " +
         "  process.exit(1); " +
         "} " +
         "console.log('OK: build-native-auto script correctly configured');"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"next-swc script rename validation failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_turbo_jsonc_task_renamed():
    """turbo.jsonc must have build-native-auto task instead of build task."""
    turbo_path = Path(f"{REPO}/packages/next-swc/turbo.jsonc")
    assert turbo_path.exists(), "turbo.jsonc must exist (renamed from turbo.json)"

    r = subprocess.run(
        ["node", "-e",
         "const fs = require('fs'); " +
         "const content = fs.readFileSync('./packages/next-swc/turbo.jsonc', 'utf8'); " +
         "/* Verify build-native-auto task exists (quoted key in JSON) */ " +
         "if (!content.includes('\"build-native-auto\"')) { " +
         "  console.error('FAIL: build-native-auto task does not exist in turbo.jsonc'); " +
         "  process.exit(1); " +
         "} " +
         "/* Verify the comment block explaining the auto behavior */ " +
         "if (!content.includes('precompiled')) { " +
         "  console.error('FAIL: turbo.jsonc must contain explanatory comment about precompiled binary'); " +
         "  process.exit(1); " +
         "} " +
         "console.log('OK: turbo.jsonc has build-native-auto task with comment');"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"turbo.jsonc task validation failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- Config update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agents_md_documents_build_all():
    """AGENTS.md must document pnpm build-all for building JS + Rust code."""
    r = subprocess.run(
        ["node", "-e",
         "const fs = require('fs'); " +
         "const content = fs.readFileSync('AGENTS.md', 'utf8'); " +
         "if (!content.includes('build-all')) { " +
         "  console.error('FAIL: AGENTS.md does not mention build-all command'); " +
         "  process.exit(1); " +
         "} " +
         "const hasBuildAll = content.includes('pnpm build-all'); " +
         "if (!hasBuildAll) { " +
         "  console.error('FAIL: AGENTS.md does not document pnpm build-all'); " +
         "  process.exit(1); " +
         "} " +
         "const jsOnlyPatterns = ['JS code', 'JavaScript']; " +
         "const jsRustPatterns = ['Rust', 'Turbopack', 'native']; " +
         "const hasJsRef = jsOnlyPatterns.some(p => content.toLowerCase().includes(p.toLowerCase())); " +
         "const hasRustRef = jsRustPatterns.some(p => content.toLowerCase().includes(p.toLowerCase())); " +
         "if (!hasJsRef) { " +
         "  console.error('FAIL: AGENTS.md does not reference JavaScript/JS builds'); " +
         "  process.exit(1); " +
         "} " +
         "if (!hasRustRef) { " +
         "  console.error('FAIL: AGENTS.md does not reference Rust/Turbopack builds'); " +
         "  process.exit(1); " +
         "} " +
         "console.log('OK: AGENTS.md documents build scope distinctions');"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"AGENTS.md build documentation validation failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_agents_md_branch_switch_uses_build_all():
    """AGENTS.md should recommend build-all for branch switches and when editing Turbopack."""
    r = subprocess.run(
        ["node", "-e",
         "const fs = require('fs'); " +
         "const content = fs.readFileSync('AGENTS.md', 'utf8'); " +
         "/* Check branch switching guidance recommends build-all */ " +
         "const switchIdx = content.toLowerCase().indexOf('switching branches'); " +
         "if (switchIdx !== -1) { " +
         "  const context = content.substring(switchIdx, switchIdx + 800); " +
         "  if (!context.includes('build-all')) { " +
         "    console.error('FAIL: Branch switching section does not recommend build-all'); " +
         "    process.exit(1); " +
         "  } " +
         "} " +
         "/* Check Turbopack (Rust) editing guidance recommends build-all */ " +
         "const turbopackRustIdx = content.indexOf('Turbopack (Rust)'); " +
         "if (turbopackRustIdx !== -1) { " +
         "  const context = content.substring(Math.max(0, turbopackRustIdx - 200), turbopackRustIdx + 200); " +
         "  if (!context.includes('build-all')) { " +
         "    console.error('FAIL: Turbopack/Rust section does not reference build-all'); " +
         "    process.exit(1); " +
         "  } " +
         "} " +
         "console.log('OK: AGENTS.md has correct workflow guidance');"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"AGENTS.md workflow guidance validation failed:\n{r.stderr}"


# === CI-mined test: Prettier formatting check via bash ===
def test_ci_prettier_package_json():
    """pass_to_pass | CI: prettier --check package.json via bash login shell"""
    r = subprocess.run(
        ["bash", "-lc", "npx prettier --check package.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"CI prettier check failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_wasm_pnpm():
    """pass_to_pass | CI job 'build-wasm' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm install'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_wasm_pnpm_2():
    """pass_to_pass | CI job 'build-wasm' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_validate_docs_links_run_link_checker():
    """pass_to_pass | CI job 'validate-docs-links' → step 'Run link checker'"""
    r = subprocess.run(
        ["bash", "-lc", 'node ./.github/actions/validate-docs-links/dist/index.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run link checker' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")