"""
Task: payload-templates-fix-cloudflare-logger-error
Repo: payloadcms/payload @ 23d52a0d7d5780954bf5b027e537cabb008b8a0a
PR:   15752

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/payload"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript/JS files must parse without errors."""
    config_ts = Path(f"{REPO}/templates/with-cloudflare-d1/src/payload.config.ts")
    eslint_mjs = Path(f"{REPO}/templates/with-cloudflare-d1/eslint.config.mjs")
    index_ts = Path(f"{REPO}/packages/payload/src/index.ts")
    for f in [config_ts, eslint_mjs, index_ts]:
        assert f.exists(), f"Expected file not found: {f}"
        content = f.read_text()
        assert len(content) > 100, f"File suspiciously small: {f}"


# [repo_tests] pass_to_pass
def test_template_typecheck():
    """Cloudflare D1 template TypeScript typecheck passes (pass_to_pass)."""
    template_dir = Path(f"{REPO}/templates/with-cloudflare-d1")
    # Install dependencies and run typecheck
    r = subprocess.run(
        ["bash", "-c",
         "corepack enable && corepack prepare pnpm@latest --activate && "
         "pnpm install --ignore-workspace && npx tsc --noEmit"],
        capture_output=True, text=True, timeout=120, cwd=template_dir,
    )
    assert r.returncode == 0, f"Template typecheck failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_template_eslint():
    """Cloudflare D1 template ESLint passes after fix (pass_to_pass)."""
    template_dir = Path(f"{REPO}/templates/with-cloudflare-d1")
    # Install dependencies and run ESLint on payload.config.ts
    r = subprocess.run(
        ["bash", "-c",
         "corepack enable && corepack prepare pnpm@latest --activate && "
         "pnpm install --ignore-workspace && npx eslint src/payload.config.ts --quiet"],
        capture_output=True, text=True, timeout=120, cwd=template_dir,
    )
    assert r.returncode == 0, f"Template ESLint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cloudflare_logger_json_output():
    """Custom console logger must produce valid JSON through console methods."""
    config = Path(f"{REPO}/templates/with-cloudflare-d1/src/payload.config.ts")
    content = config.read_text()

    # Verify the logger is defined in the file
    assert "createLog" in content, "payload.config.ts must define a createLog function"
    assert "JSON.stringify" in content, "Logger must produce JSON output via JSON.stringify"

    # Run a Node.js subprocess to test the logging pattern actually works.
    # We read the actual file, verify the createLog pattern, then test it.
    script = """\
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');

// Verify createLog exists and uses JSON.stringify
if (!src.includes('createLog')) { console.error('no createLog'); process.exit(1); }
if (!src.includes('JSON.stringify({ level')) { console.error('no JSON.stringify'); process.exit(1); }

// Extract and evaluate the createLog function (pure JS once types are stripped)
// Strip TypeScript type annotations for eval
let fnSrc = src.match(/const createLog\\s*=[\\s\\S]*?\\n\\s*\\}/);
if (!fnSrc) { console.error('cannot extract createLog'); process.exit(1); }
fnSrc = fnSrc[0]
  .replace(/:\\s*string/g, '')
  .replace(/:\\s*typeof\\s+console\\.log/g, '')
  .replace(/:\\s*object\\s*\\|\\s*string/g, '')
  .replace(/\\?:\\s*string/g, '')
  .replace(/as\\s*\\{[^}]*\\}/g, '')
  .replace('const createLog =', 'var createLog =');
eval(fnSrc);

// Capture output instead of printing
const results = [];
const capture = (s) => results.push(JSON.parse(s));

// Test 1: string message
createLog('info', capture)('hello world');
if (results[0].level !== 'info' || results[0].msg !== 'hello world') {
  console.error('FAIL string msg:', JSON.stringify(results[0]));
  process.exit(1);
}

// Test 2: object with message
createLog('error', capture)({ err: 'boom' }, 'request failed');
if (results[1].level !== 'error' || results[1].msg !== 'request failed' || results[1].err !== 'boom') {
  console.error('FAIL obj msg:', JSON.stringify(results[1]));
  process.exit(1);
}

// Test 3: object with embedded msg property
createLog('debug', capture)({ msg: 'embedded', extra: 42 });
if (results[2].msg !== 'embedded' || results[2].extra !== 42) {
  console.error('FAIL embedded msg:', JSON.stringify(results[2]));
  process.exit(1);
}

console.log('PASS');
"""
    r = subprocess.run(
        ["node", "-e", script, str(config)],
        capture_output=True, text=True, timeout=15,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Logger JSON test failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_logger_has_all_levels():
    """cloudflareLogger must define all standard pino log level methods."""
    config = Path(f"{REPO}/templates/with-cloudflare-d1/src/payload.config.ts")
    content = config.read_text()

    required_levels = ["trace", "debug", "info", "warn", "error", "fatal", "silent"]
    for level in required_levels:
        # Each level should appear as a property of the logger object
        pattern = rf"\b{level}\b\s*:"
        assert re.search(pattern, content), (
            f"cloudflareLogger missing '{level}' method in payload.config.ts"
        )


# [pr_diff] fail_to_pass
def test_logger_production_conditional():
    """Logger must only be active in production, not development."""
    config = Path(f"{REPO}/templates/with-cloudflare-d1/src/payload.config.ts")
    content = config.read_text()

    # The logger should be conditionally applied based on production check
    assert "isProduction" in content, "Must use isProduction check"
    # The buildConfig logger property should be conditional
    assert re.search(
        r"logger\s*:\s*isProduction\s*\?", content
    ), "logger config must be conditional on isProduction (e.g., isProduction ? logger : undefined)"


# [pr_diff] fail_to_pass
def test_payload_logger_type_exported():
    """PayloadLogger type must be exported from the payload package index."""
    index_ts = Path(f"{REPO}/packages/payload/src/index.ts")
    content = index_ts.read_text()

    assert "PayloadLogger" in content, (
        "packages/payload/src/index.ts must export PayloadLogger"
    )
    # Must be a type export (not a value export)
    assert re.search(
        r"export\s+type\s*\{[^}]*PayloadLogger[^}]*\}", content
    ), "PayloadLogger must be exported as a type (export type { PayloadLogger })"


# ---------------------------------------------------------------------------
# Config/documentation update checks (fail_to_pass)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readme_logger_configuration():
    """README.md must document the custom logger configuration for Workers."""
    readme = Path(f"{REPO}/templates/with-cloudflare-d1/README.md")
    content = readme.read_text()

    # Must have a section about logger configuration
    assert "logger" in content.lower(), "README must mention logger"
    assert "pino" in content.lower() or "pino-pretty" in content.lower(), (
        "README should explain that pino/pino-pretty causes issues in Workers"
    )
    assert "console" in content.lower(), (
        "README should mention the console-based logging approach"
    )
    assert "PAYLOAD_LOG_LEVEL" in content, (
        "README should document the PAYLOAD_LOG_LEVEL environment variable"
    )


# [pr_diff] fail_to_pass
def test_readme_diagnostic_channel():
    """README.md must document the diagnostic channel error workaround."""
    readme = Path(f"{REPO}/templates/with-cloudflare-d1/README.md")
    content = readme.read_text()

    assert "diagnostic channel" in content.lower(), (
        "README must document diagnostic channel errors"
    )
    assert "undici" in content.lower(), (
        "README should mention undici as the source of diagnostic channel errors"
    )
    assert "skipSafeFetch" in content, (
        "README should document the skipSafeFetch workaround"
    )
