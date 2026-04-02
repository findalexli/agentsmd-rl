"""
Task: opencode-mockmodule-test-pollution
Repo: anomalyco/opencode @ e973bbf54a519566bfdccce3474178b26b163a6d
PR:   19445

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/opencode"
THREAD_TEST = f"{REPO}/packages/opencode/test/cli/tui/thread.test.ts"
CONFIG_TEST = f"{REPO}/packages/opencode/test/config/config.test.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_mock_leakage_canary():
    """Thread test mocks must not leak to subsequent test files."""
    canary = Path(f"{REPO}/packages/opencode/test/cli/tui/zzz_canary_leak.test.ts")
    canary.write_text(textwrap.dedent("""\
        import { describe, expect, test } from "bun:test"

        describe("canary: mock leakage detection", () => {
          test("@/util/timeout module is not globally mocked", async () => {
            const mod = await import("../../../src/util/timeout")
            expect(mod).toBeDefined()
            const keys = Object.keys(mod)
            expect(keys.length).toBeGreaterThan(0)
            if (mod.withTimeout && typeof mod.withTimeout === "function") {
              const src = mod.withTimeout.toString()
              expect(src.length).toBeGreaterThan(50)
            }
          })

          test("@/config/tui module is not globally mocked", async () => {
            const mod = await import("../../../src/config/tui")
            expect(mod).toBeDefined()
            const keys = Object.keys(mod)
            expect(keys.length).toBeGreaterThan(0)
            if (mod.TuiConfig) {
              const configKeys = Object.keys(mod.TuiConfig)
              expect(configKeys.length).toBeGreaterThan(1)
            }
          })

          test("@/util/rpc module is not globally mocked", async () => {
            const mod = await import("../../../src/util/rpc")
            expect(mod).toBeDefined()
            expect(typeof mod.Rpc).not.toBe("undefined")
          })
        })
    """))
    try:
        r = subprocess.run(
            ["bun", "test", THREAD_TEST, str(canary)],
            cwd=REPO, capture_output=True, timeout=120,
        )
        assert r.returncode == 0, (
            f"Mock leakage detected or thread test failed:\n"
            f"{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-2000:]}"
        )
    finally:
        canary.unlink(missing_ok=True)


# [pr_diff] fail_to_pass
def test_no_mock_module_in_thread_test():
    """thread.test.ts must not use mock.module() (leaks globally in Bun)."""
    src = Path(THREAD_TEST).read_text()
    # Strip comments before checking
    lines = src.split("\n")
    code_lines = []
    in_block = False
    for line in lines:
        t = line.strip()
        if t.startswith("/*"):
            in_block = True
        if in_block:
            if "*/" in t:
                in_block = False
            continue
        if t.startswith("//"):
            continue
        code_lines.append(line)
    code = "\n".join(code_lines)
    assert not re.search(r"mock\s*\.\s*module\s*\(", code), (
        "mock.module() found in thread.test.ts — it leaks globally in Bun"
    )


# [pr_diff] fail_to_pass
def test_config_mock_filters_by_cwd():
    """config.test.ts BunProc.run mock must filter calls by working directory."""
    src = Path(CONFIG_TEST).read_text()
    # The fix adds cwd-based filtering so only relevant BunProc.run calls
    # are counted. Look for cwd comparison patterns in the mock impl.
    has_cwd_filter = bool(re.search(
        r"(opts\??\.\s*cwd|options\??\.\s*cwd).*(?:normalize|===|==|includes|startsWith)",
        src,
    ))
    has_hit_pattern = bool(re.search(
        r"(const|let|var)\s+\w+\s*=.*(?:normalize|cwd).*(?:===|==)", src,
    ))
    assert has_cwd_filter or has_hit_pattern, (
        "config.test.ts BunProc.run mock does not filter by cwd — "
        "unrelated calls will inflate counters"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — modified tests must still pass
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_thread_tests_pass():
    """thread.test.ts must run successfully with bun test."""
    r = subprocess.run(
        ["bun", "test", THREAD_TEST],
        cwd=REPO, capture_output=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"thread.test.ts failed:\n"
        f"{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-2000:]}"
    )


# [pr_diff] pass_to_pass
def test_config_tests_pass():
    """config.test.ts must run successfully with bun test."""
    r = subprocess.run(
        ["bun", "test", CONFIG_TEST],
        cwd=REPO, capture_output=True, timeout=180,
    )
    assert r.returncode == 0, (
        f"config.test.ts failed:\n"
        f"{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:122 @ e973bbf5
def test_mock_cleanup_in_lifecycle_hook():
    """thread.test.ts must clean up mocks in afterEach/afterAll."""
    src = Path(THREAD_TEST).read_text()
    has_after_hook = bool(re.search(r"after(?:Each|All)\s*\(", src))
    has_restore = bool(re.search(r"mock\s*\.\s*restore|mockRestore", src))
    assert has_after_hook and has_restore, (
        "thread.test.ts must have afterEach/afterAll calling mock.restore()"
    )


# [agent_config] pass_to_pass — AGENTS.md:13 @ e973bbf5
def test_no_any_type_added():
    """Changes must not introduce the `any` type."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--",
         "packages/opencode/test/cli/tui/thread.test.ts",
         "packages/opencode/test/config/config.test.ts"],
        cwd=REPO, capture_output=True, timeout=10,
    )
    diff = r.stdout.decode()
    added_lines = [l for l in diff.split("\n")
                   if l.startswith("+") and not l.startswith("+++")]
    any_lines = [l for l in added_lines if re.search(r":\s*any\b", l)]
    assert not any_lines, f"Added `any` type annotations:\n" + "\n".join(any_lines)


# [agent_config] pass_to_pass — AGENTS.md:12 @ e973bbf5
def test_no_try_catch_added():
    """Changes must not introduce try/catch blocks."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--",
         "packages/opencode/test/cli/tui/thread.test.ts",
         "packages/opencode/test/config/config.test.ts"],
        cwd=REPO, capture_output=True, timeout=10,
    )
    diff = r.stdout.decode()
    added_lines = [l for l in diff.split("\n")
                   if l.startswith("+") and not l.startswith("+++")]
    try_catch = [l for l in added_lines
                 if re.search(r"\btry\s*\{", l) or re.search(r"\bcatch\s*\(", l)]
    assert not try_catch, (
        f"Added try/catch (AGENTS.md: avoid try/catch):\n" + "\n".join(try_catch)
    )


# [agent_config] pass_to_pass — AGENTS.md:84 @ e973bbf5
def test_no_else_added():
    """Changes must not introduce else statements."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--",
         "packages/opencode/test/cli/tui/thread.test.ts",
         "packages/opencode/test/config/config.test.ts"],
        cwd=REPO, capture_output=True, timeout=10,
    )
    diff = r.stdout.decode()
    added_lines = [l for l in diff.split("\n")
                   if l.startswith("+") and not l.startswith("+++")]
    # Match standalone else or else-if but not variable names containing "else"
    else_lines = [l for l in added_lines
                  if re.search(r"}\s*else\b|\belse\s*\{|\belse\s+if\b", l)]
    assert not else_lines, (
        f"Added else statements (AGENTS.md: prefer early returns):\n"
        + "\n".join(else_lines)
    )


# ---------------------------------------------------------------------------
# Anti-stub (static) — prevent trivial/gutted solutions
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_thread_test_not_stubbed():
    """thread.test.ts must not be stubbed out."""
    src = Path(THREAD_TEST).read_text()
    lines = len(src.strip().split("\n"))
    assert lines >= 40, f"thread.test.ts looks stubbed ({lines} lines)"
    assert "TuiThreadCommand" in src, "thread.test.ts must import TuiThreadCommand"


# [static] pass_to_pass
def test_config_test_not_stubbed():
    """config.test.ts must not be stubbed and must have substantive mock logic."""
    src = Path(CONFIG_TEST).read_text()
    lines = len(src.strip().split("\n"))
    assert lines >= 200, f"config.test.ts looks stubbed ({lines} lines)"
    assert re.search(r"dedupes concurrent", src), "Missing 'dedupes concurrent' test block"
    assert re.search(r"serializes.*across dirs|serializes config", src), (
        "Missing serialization test block"
    )
    assert re.search(r"spyOn.*BunProc|BunProc.*mock", src), "Missing BunProc.run mock"
