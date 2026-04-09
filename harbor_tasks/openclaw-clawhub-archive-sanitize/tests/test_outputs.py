"""
Task: openclaw-clawhub-archive-sanitize
Repo: openclaw/openclaw @ 7a16a481983e62bc3394c7c5f90d320b6be82f0e
PR:   56779

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/openclaw"
TARGET = Path(REPO) / "src/infra/clawhub.ts"

# Shared node script that extracts safeDirName, finds the archivePath expression
# in a given function, evaluates it with test inputs, and checks paths are flat.
_EVAL_ARCHIVE_PATH_SCRIPT = r"""
const fs = require('fs');
const path = require('path');

const src = fs.readFileSync('src/infra/clawhub.ts', 'utf8');
const safeSrc = fs.readFileSync('src/infra/install-safe-path.ts', 'utf8');

// Extract safeDirName from repo source so eval can use it
const sdnMatch = safeSrc.match(/function\s+safeDirName\(input[^)]*\)[^{]*\{([\s\S]*?)\n\}/);
if (!sdnMatch) { console.error('safeDirName not found in install-safe-path.ts'); process.exit(1); }
const safeDirName = new Function('input', sdnMatch[1]);

const funcName = process.argv[1];
const paramKey = process.argv[2];
const testInputs = JSON.parse(process.argv[3]);

// Find the target function
const funcIdx = src.indexOf('function ' + funcName);
if (funcIdx === -1) { console.error(funcName + ' not found'); process.exit(1); }

// Find archivePath assignment within the function (search the next ~3000 chars)
const afterFunc = src.slice(funcIdx, funcIdx + 3000);
const archiveMatch = afterFunc.match(/(?:const|let|var)\s+archivePath\s*=\s*(.+?);/);
if (!archiveMatch) { console.error('archivePath assignment not found in ' + funcName); process.exit(1); }

const expr = archiveMatch[1].trim();
const tmpDir = '/tmp/test-archive';

for (const input of testInputs) {
    const params = { name: input, slug: input, version: '1.0.0' };
    let result;
    try {
        result = eval(expr);
    } catch (e) {
        console.error('Eval error for "' + input + '": ' + e.message);
        process.exit(1);
    }

    // The archive path must be directly under tmpDir (no nested subdirectories)
    const rel = path.relative(tmpDir, result);
    if (rel.includes('/') || rel.includes('\\')) {
        console.error('Nested path for "' + input + '": ' + result);
        process.exit(1);
    }
    if (!rel.endsWith('.zip')) {
        console.error('Missing .zip suffix for "' + input + '": ' + result);
        process.exit(1);
    }
}
"""


def _check_archive_path(func_name: str, param_key: str, test_inputs: list) -> None:
    """Run the shared node script to verify flat archive paths."""
    r = subprocess.run(
        ["node", "-e", _EVAL_ARCHIVE_PATH_SCRIPT,
         func_name, param_key, json.dumps(test_inputs)],
        capture_output=True, text=True, timeout=15, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"{func_name}: scoped/slashed names produce nested paths\n"
        f"{r.stdout}\n{r.stderr}"
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_target_exists():
    """Target file src/infra/clawhub.ts must exist."""
    assert TARGET.is_file(), f"{TARGET} does not exist"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_package_archive_flat_filename():
    """Scoped package names like @scope/name produce flat archive temp filenames."""
    _check_archive_path(
        "downloadClawHubPackageArchive", "name",
        ["@soimy/dingtalk", "@scope/name", "org/sub/deep"],
    )


# [pr_diff] fail_to_pass
def test_skill_archive_flat_filename():
    """Slash-containing skill slugs like ops/calendar produce flat archive filenames."""
    _check_archive_path(
        "downloadClawHubSkillArchive", "slug",
        ["ops/calendar", "team/sub/tool", "a/b"],
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint_clawhub():
    """Repo's oxlint passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "oxlint", "src/infra/clawhub.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_format_clawhub():
    """Repo's oxfmt format check passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "oxfmt", "--check", "src/infra/clawhub.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_functions_not_stub():
    """Both download functions have substantial bodies (not just stubs)."""
    src = TARGET.read_text()
    for func_name in ["downloadClawHubPackageArchive", "downloadClawHubSkillArchive"]:
        idx = src.find(f"function {func_name}")
        assert idx != -1, f"{func_name} not found in clawhub.ts"
        # Walk from first '{' counting braces to find the function body
        after = src[idx:idx + 5000]
        brace_start = after.index("{")
        depth = 0
        body_lines = []
        for line in after[brace_start:].split("\n"):
            depth += line.count("{") - line.count("}")
            stripped = line.strip()
            if stripped and not stripped.startswith("//") and not stripped.startswith("*"):
                body_lines.append(stripped)
            if depth <= 0 and body_lines:
                break
        assert len(body_lines) >= 5, (
            f"{func_name} body too short ({len(body_lines)} lines) — likely a stub"
        )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:146 @ 7a16a481983e62bc3394c7c5f90d320b6be82f0e
def test_no_ts_nocheck():
    """No @ts-nocheck or @ts-ignore directives in the target file."""
    src = TARGET.read_text()
    assert "@ts-nocheck" not in src, "@ts-nocheck found in clawhub.ts"
    assert "@ts-ignore" not in src, "@ts-ignore found in clawhub.ts"


# [agent_config] pass_to_pass — CLAUDE.md:147 @ 7a16a481983e62bc3394c7c5f90d320b6be82f0e
def test_no_eslint_disable_explicit_any():
    """no-explicit-any must not be disabled in the target file."""
    src = TARGET.read_text()
    assert "no-explicit-any" not in src, (
        "Found eslint no-explicit-any disable in clawhub.ts — prefer real types or unknown"
    )


# [agent_config] pass_to_pass — CLAUDE.md:153 @ 7a16a481983e62bc3394c7c5f90d320b6be82f0e
def test_no_prototype_mutation():
    """No prototype mutation patterns in the target file."""
    src = TARGET.read_text()
    assert "applyPrototypeMixins" not in src, (
        "applyPrototypeMixins found in clawhub.ts — use explicit inheritance/composition instead"
    )
    # Check for Object.defineProperty on .prototype
    assert not re.search(r'Object\.defineProperty\s*\(\s*\w+\.prototype', src), (
        "Object.defineProperty on .prototype found in clawhub.ts"
    )
    # Check for direct .prototype. assignment
    assert not re.search(r'\w+\.prototype\.\w+\s*=', src), (
        "Prototype mutation (.prototype.x =) found in clawhub.ts"
    )


# [agent_config] pass_to_pass — CLAUDE.md:148 @ 7a16a481983e62bc3394c7c5f90d320b6be82f0e
def test_no_mixed_dynamic_static_imports():
    """Do not mix `await import("x")` and static `import ... from "x"` for the same module."""
    src = TARGET.read_text()
    # Collect statically imported module specifiers
    static_imports = set(re.findall(r'import\s+.*?from\s+["\']([^"\']+)["\']', src))
    # Collect dynamically imported module specifiers
    dynamic_imports = set(re.findall(r'await\s+import\s*\(\s*["\']([^"\']+)["\']\s*\)', src))
    overlap = static_imports & dynamic_imports
    assert not overlap, (
        f"Same module(s) imported both statically and dynamically: {overlap}"
    )
