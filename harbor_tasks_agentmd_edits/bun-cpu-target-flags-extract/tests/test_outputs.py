"""
Task: bun-cpu-target-flags-extract
Repo: oven-sh/bun @ 871f660f5816a48dacc6c53e104f42d775852e6b
PR:   #28859

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This task tests a build-system refactoring: extracting CPU target flags
from globalFlags into a separate cpuTargetFlags table, adding a
computeCpuTargetFlags() function, and forwarding it to local WebKit builds.
Both code and documentation (CLAUDE.md) must be updated.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/bun"
FLAGS_TS = Path(REPO) / "scripts/build/flags.ts"
WEBKIT_TS = Path(REPO) / "scripts/build/deps/webkit.ts"
CLAUDE_MD = Path(REPO) / "scripts/build/CLAUDE.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js analysis script via subprocess."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_source_files_exist():
    """All three modified files must exist and be non-empty."""
    for f in [FLAGS_TS, WEBKIT_TS, CLAUDE_MD]:
        assert f.exists(), f"{f} does not exist"
        assert f.stat().st_size > 0, f"{f} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavior tests using subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cpu_target_flags_table_exported():
    """flags.ts must export a cpuTargetFlags array with -march/-mcpu entries."""
    script = r'''
const fs = require("fs");
const code = fs.readFileSync("{flags_ts}", "utf8");
const hasExport = /export\s+const\s+cpuTargetFlags\s*:\s*Flag\[\s*\]/.test(code);
const hasMarch = code.includes("-march=haswell") || code.includes("march=armv8");
const hasMcpu = code.includes("-mcpu=apple-m1");
if (hasExport && (hasMarch || hasMcpu)) {
    console.log("PASS");
} else {
    console.log("FAIL:" + JSON.stringify({hasExport, hasMarch, hasMcpu}));
}
'''.replace("{flags_ts}", str(FLAGS_TS))
    r = _run_node(script)
    assert r.returncode == 0, f"Node error: {r.stderr}"
    assert "PASS" in r.stdout, f"cpuTargetFlags check failed: {r.stdout.strip()}"


# [pr_diff] fail_to_pass
def test_compute_cpu_target_flags_exported():
    """flags.ts must export a computeCpuTargetFlags function that returns string[]."""
    script = r'''
const fs = require("fs");
const code = fs.readFileSync("{flags_ts}", "utf8");
const hasFunc = /export\s+function\s+computeCpuTargetFlags/.test(code);
const takesConfig = /computeCpuTargetFlags\s*\(\s*cfg\s*:\s*Config\s*\)/.test(code);
const iteratesFlags = code.includes("cpuTargetFlags") && /for\s*\(.*cpuTargetFlags/.test(code);
const usesResolveFlagValue = /resolveFlagValue/.test(code.slice(
    code.indexOf("computeCpuTargetFlags"),
    code.indexOf("computeCpuTargetFlags") + 500
));
if (hasFunc && takesConfig && iteratesFlags && usesResolveFlagValue) {
    console.log("PASS");
} else {
    console.log("FAIL:" + JSON.stringify({hasFunc, takesConfig, iteratesFlags, usesResolveFlagValue}));
}
'''.replace("{flags_ts}", str(FLAGS_TS))
    r = _run_node(script)
    assert r.returncode == 0, f"Node error: {r.stderr}"
    assert "PASS" in r.stdout, f"computeCpuTargetFlags check failed: {r.stdout.strip()}"


# [pr_diff] fail_to_pass
def test_webkit_imports_compute_function():
    """webkit.ts must import computeCpuTargetFlags from flags.ts."""
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
if (found) {
    console.log("PASS");
} else {
    console.log("FAIL:no_import");
}
'''.replace("{webkit_ts}", str(WEBKIT_TS))
    r = _run_node(script)
    assert r.returncode == 0, f"Node error: {r.stderr}"
    assert "PASS" in r.stdout, f"Import check failed: {r.stdout.strip()}"


# [pr_diff] fail_to_pass
def test_webkit_opt_flags_seeded_with_cpu_targets():
    """webkit.ts must initialize optFlags with computeCpuTargetFlags(cfg),
    not an empty array."""
    script = r'''
const fs = require("fs");
const code = fs.readFileSync("{webkit_ts}", "utf8");
// Must NOT have the old pattern: const optFlags: string[] = [];
const hasOldEmpty = /const\s+optFlags\s*:\s*string\[\s*\]\s*=\s*\[\s*\]/.test(code);
// Must have the new pattern using computeCpuTargetFlags
const hasNewPattern = /const\s+optFlags\s*:\s*string\[\s*\]\s*=\s*computeCpuTargetFlags/.test(code);
if (!hasOldEmpty && hasNewPattern) {
    console.log("PASS");
} else {
    console.log("FAIL:" + JSON.stringify({hasOldEmpty, hasNewPattern}));
}
'''.replace("{webkit_ts}", str(WEBKIT_TS))
    r = _run_node(script)
    assert r.returncode == 0, f"Node error: {r.stderr}"
    assert "PASS" in r.stdout, f"optFlags seeding check failed: {r.stdout.strip()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — config/documentation update tests
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass -- scripts/build/CLAUDE.md:122
def test_claude_md_documents_cpu_target_flags():
    """CLAUDE.md must list cpuTargetFlags in the flag tables section.
    The existing documentation pattern requires all flag tables to be listed."""
    content = CLAUDE_MD.read_text()
    assert "cpuTargetFlags" in content, \
        "CLAUDE.md must mention cpuTargetFlags in the flag tables"
    # Check it appears in context of the tables listing
    assert "-march" in content or "march" in content, \
        "CLAUDE.md should describe what cpuTargetFlags contains (-march/-mcpu/-mtune)"


# [agent_config] fail_to_pass -- scripts/build/CLAUDE.md:182
def test_claude_md_documents_compute_function():
    """CLAUDE.md must list computeCpuTargetFlags in the module inventory
    for flags.ts. The existing inventory pattern requires all exported
    functions to be listed."""
    content = CLAUDE_MD.read_text()
    assert "computeCpuTargetFlags" in content, \
        "CLAUDE.md must mention computeCpuTargetFlags in the flags.ts module inventory"
    # Verify it's in the flags.ts row of the inventory table
    flags_row = None
    for line in content.split("\n"):
        if "flags.ts" in line and "|" in line:
            flags_row = line
            break
    assert flags_row is not None, "CLAUDE.md must have a flags.ts row in the inventory"
    assert "computeCpuTargetFlags" in flags_row, \
        "The flags.ts inventory row must list computeCpuTargetFlags"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_global_flags_includes_cpu_targets():
    """globalFlags must still include cpu target entries (spread from
    cpuTargetFlags). The refactoring must not change globalFlags behavior."""
    code = FLAGS_TS.read_text()
    # globalFlags must contain ...cpuTargetFlags spread
    assert "...cpuTargetFlags" in code, \
        "globalFlags must spread cpuTargetFlags to maintain backward compatibility"
    # globalFlags must still be exported
    assert "export const globalFlags" in code, \
        "globalFlags must still be exported"


# [pr_diff] pass_to_pass
def test_compute_function_not_stub():
    """computeCpuTargetFlags must have real implementation — iterate flags,
    check predicates, call resolveFlagValue. Not just return []."""
    code = FLAGS_TS.read_text()
    # Extract function body
    start = code.find("export function computeCpuTargetFlags")
    assert start >= 0, "computeCpuTargetFlags not found"
    body = code[start:start + 500]

    has_iteration = "for" in body and "cpuTargetFlags" in body
    has_predicate = ".when" in body or "when(" in body
    has_resolve = "resolveFlagValue" in body
    has_return = "return out" in body

    assert has_iteration, "Must iterate over cpuTargetFlags"
    assert has_predicate, "Must check when predicates"
    assert has_resolve, "Must call resolveFlagValue"
    assert has_return, "Must return the result"


# [static] pass_to_pass
def test_webkit_comment_describes_forwarding():
    """webkit.ts comments must explain that CPU target flags are forwarded
    to local WebKit builds, and why (WebKit never sets -march itself)."""
    code = WEBKIT_TS.read_text()
    # The updated comment must mention CPU target forwarding
    has_cpu_target_mention = "CPU target" in code or "cpu target" in code
    has_march_mention = "-march" in code or "march" in code
    has_webkit_explanation = "WebKit" in code and ("never sets" in code or "doesn't set" in code)
    assert has_cpu_target_mention or has_march_mention, \
        "webkit.ts comments must mention CPU target / -march forwarding"
    assert has_webkit_explanation, \
        "webkit.ts comments must explain why: WebKit never sets CPU target flags"
