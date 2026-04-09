"""
Task: bun-build-forward-marchmcpu-to-local
Repo: oven-sh/bun @ 871f660f5816a48dacc6c53e104f42d775852e6b
PR:   #28859

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Bug: local WebKit builds dropped -march/-mcpu flags because webkit.ts
initialized optFlags as []. Fix: extract cpuTargetFlags table, add
computeCpuTargetFlags(), seed optFlags with it. Also update CLAUDE.md.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/bun"
FLAGS_TS = Path(REPO) / "scripts/build/flags.ts"
WEBKIT_TS = Path(REPO) / "scripts/build/deps/webkit.ts"
CLAUDE_MD = Path(REPO) / "scripts/build/CLAUDE.md"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js analysis script via subprocess."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — files exist
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_source_files_exist():
    """All three modified files must exist and be non-empty."""
    for f in [FLAGS_TS, WEBKIT_TS, CLAUDE_MD]:
        assert f.exists(), f"{f} does not exist"
        assert f.stat().st_size > 0, f"{f} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests using subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cpu_target_flags_table_extracted():
    """flags.ts exports a cpuTargetFlags array containing ONLY -march/-mcpu/
    -mtune entries (no macOS SDK or other non-CPU flags mixed in)."""
    script = r'''
const fs = require("fs");
const code = fs.readFileSync("{flags_ts}", "utf8");
const hasExport = /export\s+const\s+cpuTargetFlags\s*:\s*Flag\[\s*\]/.test(code);
const hasHaswell = code.includes("-march=haswell");
const hasAppleM1 = code.includes("-mcpu=apple-m1");
// cpuTargetFlags section must NOT contain macOS SDK deployment flag
const secStart = code.indexOf("export const cpuTargetFlags");
const secEnd = code.indexOf("];", secStart) + 2;
const section = code.slice(secStart, secEnd);
const hasNonCpuFlag = section.includes("mmacosx-version-min");
if (hasExport && hasHaswell && hasAppleM1 && !hasNonCpuFlag) {
    console.log("PASS");
} else {
    console.log("FAIL:" + JSON.stringify({hasExport, hasHaswell, hasAppleM1, hasNonCpuFlag}));
}
'''.replace("{flags_ts}", str(FLAGS_TS))
    r = _run_node(script)
    assert r.returncode == 0, f"Node error: {r.stderr}"
    assert "PASS" in r.stdout, f"cpuTargetFlags check failed: {r.stdout.strip()}"


# [pr_diff] fail_to_pass
def test_compute_cpu_target_flags_function_exists():
    """flags.ts exports computeCpuTargetFlags(cfg) that iterates
    cpuTargetFlags, checks when predicates, calls resolveFlagValue."""
    script = r'''
const fs = require("fs");
const code = fs.readFileSync("{flags_ts}", "utf8");
const funcStart = code.indexOf("export function computeCpuTargetFlags");
if (funcStart === -1) { console.log("FAIL:no_function"); process.exit(0); }
const body = code.slice(funcStart, funcStart + 500);
const hasParam = /computeCpuTargetFlags\s*\(\s*cfg\s*:\s*Config\s*\)/.test(body);
const iterates = /for\s*\(\s*const\s+f\s+of\s+cpuTargetFlags/.test(body);
const checksWhen = body.includes(".when");
const resolves = body.includes("resolveFlagValue");
const returns = body.includes("return out");
if (hasParam && iterates && checksWhen && resolves && returns) {
    console.log("PASS");
} else {
    console.log("FAIL:" + JSON.stringify({hasParam, iterates, checksWhen, resolves, returns}));
}
'''.replace("{flags_ts}", str(FLAGS_TS))
    r = _run_node(script)
    assert r.returncode == 0, f"Node error: {r.stderr}"
    assert "PASS" in r.stdout, f"computeCpuTargetFlags check failed: {r.stdout.strip()}"


# [pr_diff] fail_to_pass
def test_webkit_seeds_optflags_with_cpu_targets():
    """webkit.ts initializes optFlags with computeCpuTargetFlags(cfg)
    instead of the old empty array []."""
    script = r'''
const fs = require("fs");
const code = fs.readFileSync("{webkit_ts}", "utf8");
const hasEmptyInit = /const\s+optFlags\s*:\s*string\[\s*\]\s*=\s*\[\s*\]\s*;/.test(code);
const hasCpuInit = /const\s+optFlags\s*:\s*string\[\s*\]\s*=\s*computeCpuTargetFlags\s*\(\s*cfg\s*\)/.test(code);
if (!hasEmptyInit && hasCpuInit) {
    console.log("PASS");
} else {
    console.log("FAIL:" + JSON.stringify({hasEmptyInit, hasCpuInit}));
}
'''.replace("{webkit_ts}", str(WEBKIT_TS))
    r = _run_node(script)
    assert r.returncode == 0, f"Node error: {r.stderr}"
    assert "PASS" in r.stdout, f"optFlags init check failed: {r.stdout.strip()}"


# [pr_diff] fail_to_pass
def test_webkit_imports_compute_cpu_target_flags():
    """webkit.ts imports computeCpuTargetFlags from flags.ts."""
    script = r'''
const fs = require("fs");
const code = fs.readFileSync("{webkit_ts}", "utf8");
const lines = code.split("\n");
let found = false;
for (const line of lines) {
    if (line.includes("import") && line.includes("computeCpuTargetFlags") && line.includes("flags.ts")) {
        found = true;
        break;
    }
}
console.log(found ? "PASS" : "FAIL:no_import");
'''.replace("{webkit_ts}", str(WEBKIT_TS))
    r = _run_node(script)
    assert r.returncode == 0, f"Node error: {r.stderr}"
    assert "PASS" in r.stdout, f"Import check failed: {r.stdout.strip()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — config/documentation update tests
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — scripts/build/CLAUDE.md:122 @ base_commit
def test_claude_md_documents_cpu_target_flags_table():
    """CLAUDE.md must list cpuTargetFlags in the flag tables section,
    describing it as the -march/-mcpu/-mtune table forwarded to local WebKit."""
    content = CLAUDE_MD.read_text()
    assert "cpuTargetFlags" in content, \
        "CLAUDE.md must mention cpuTargetFlags in the flag tables"
    # The table description must explain it covers CPU target flags
    idx = content.find("cpuTargetFlags")
    snippet = content[idx:idx + 200]
    assert "-march" in snippet or "march" in snippet or "WebKit" in snippet, \
        "cpuTargetFlags entry must describe its purpose (-march/-mcpu forwarded to WebKit)"


# [agent_config] fail_to_pass — scripts/build/CLAUDE.md:182 @ base_commit
def test_claude_md_documents_compute_function():
    """CLAUDE.md must list computeCpuTargetFlags in the flags.ts row
    of the module inventory table."""
    content = CLAUDE_MD.read_text()
    flags_row = None
    for line in content.split("\n"):
        if "flags.ts" in line and "|" in line:
            flags_row = line
            break
    assert flags_row is not None, "CLAUDE.md must have a flags.ts row in the inventory table"
    assert "computeCpuTargetFlags" in flags_row, \
        "flags.ts inventory row must list computeCpuTargetFlags()"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_global_flags_preserves_cpu_targets():
    """globalFlags must spread cpuTargetFlags back in so existing
    computeFlags/computeDepFlags behavior is unchanged."""
    code = FLAGS_TS.read_text()
    assert "export const globalFlags" in code, "globalFlags must still be exported"
    assert "...cpuTargetFlags" in code, \
        "globalFlags must spread cpuTargetFlags for backward compatibility"


# [static] pass_to_pass
def test_compute_function_not_stub():
    """computeCpuTargetFlags has a real implementation with iteration,
    predicate checks, and resolveFlagValue — not a stub."""
    code = FLAGS_TS.read_text()
    start = code.find("export function computeCpuTargetFlags")
    assert start >= 0, "computeCpuTargetFlags not found"
    body = code[start:start + 500]
    assert "for" in body and "cpuTargetFlags" in body, "Must iterate cpuTargetFlags"
    assert ".when" in body or "when(" in body, "Must check when predicates"
    assert "resolveFlagValue" in body, "Must call resolveFlagValue"
    assert "return out" in body, "Must return result"


# [pr_diff] pass_to_pass
def test_webkit_comment_explains_forwarding():
    """webkit.ts comments explain why CPU target flags are forwarded:
    WebKit's cmake never sets -march/-mcpu itself."""
    code = WEBKIT_TS.read_text()
    has_cpu_mention = "CPU target" in code or "-march" in code or "cpu target" in code
    has_webkit_explanation = (
        "WebKit" in code
        and ("never sets" in code or "doesn't set" in code or "does not set" in code)
    )
    assert has_cpu_mention, \
        "webkit.ts must mention CPU target / -march forwarding"
    assert has_webkit_explanation, \
        "webkit.ts must explain WebKit never sets CPU target flags itself"
