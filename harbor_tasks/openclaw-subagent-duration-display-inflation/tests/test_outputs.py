"""
Task: openclaw-subagent-duration-display-inflation
Repo: openclaw/openclaw @ f011d0be28afbc7868f5e55c1117c779bd0a9f10
PR:   57739

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/openclaw"

# ---------------------------------------------------------------------------
# Helper: evaluate formatDurationCompact via Node.js
# ---------------------------------------------------------------------------

_EVAL_SCRIPT = r"""
const fs = require('fs');
const path = require('path');
const REPO = '/workspace/openclaw';

function loadFunc() {
  const src = fs.readFileSync(REPO + '/src/shared/subagents-format.ts', 'utf8');
  const reExport = src.match(
    /export\s*\{[^}]*\bformatDurationCompact\b[^}]*\}\s*from\s*['"]([^'"]+)['"]/
  );
  let targetSrc;
  if (reExport) {
    let resolved = path.resolve(REPO + '/src/shared', reExport[1]);
    for (const ext of ['', '.ts', '.js']) {
      const p = resolved + ext;
      if (fs.existsSync(p)) { targetSrc = fs.readFileSync(p, 'utf8'); break; }
    }
    if (!targetSrc) return null;
  } else {
    targetSrc = src;
  }
  const lines = targetSrc.split('\n');
  let start = -1, braceDepth = 0, end = -1, opened = false;
  for (let i = 0; i < lines.length; i++) {
    if (start === -1 && /(?:export\s+)?function\s+formatDurationCompact\b/.test(lines[i])) {
      start = i; braceDepth = 0;
    }
    if (start !== -1) {
      for (const ch of lines[i]) {
        if (ch === '{') { braceDepth++; opened = true; }
        if (ch === '}') braceDepth--;
      }
      if (opened && braceDepth === 0) { end = i; break; }
    }
  }
  if (start === -1 || end === -1) return null;
  let funcText = lines.slice(start, end + 1).join('\n');
  funcText = funcText
    .replace(/export\s+function/, 'function')
    .replace(/(function\s+formatDurationCompact)\s*\(([^)]*)\)\s*(?::\s*[^{]*?)?\s*\{/,
      (_, name, params) => {
        const cleanParams = params.replace(/\?\s*:\s*[^,)]+/g, '').replace(/:\s*[^,)]+/g, '');
        return name + '(' + cleanParams + ') {';
      })
    .replace(/(?:const|let|var)\s+(\w+)\s*:\s*[\w|<>[\]\s]+\s*=/g, 'const $1 =');
  try {
    eval(funcText);
    return eval('formatDurationCompact');
  } catch(e) { return null; }
}

const fn = loadFunc();
if (!fn) { console.log(JSON.stringify({error: true})); process.exit(0); }

const inputs = [30000, 5000, 45000, 90000, 150000, 3600000, 86400000, 0, undefined, -1000];
const results = {};
for (const v of inputs) {
  const key = String(v);
  try {
    const out = fn(v);
    results[key] = { value: out === undefined ? null : out, ok: true, isUndefined: out === undefined };
  } catch(e) {
    results[key] = { value: null, ok: false, error: e.message };
  }
}
console.log(JSON.stringify(results));
"""


def _run_formatter():
    """Evaluate formatDurationCompact with test inputs, return results dict."""
    r = subprocess.run(
        ["node", "-e", _EVAL_SCRIPT],
        capture_output=True, timeout=15, cwd=REPO,
    )
    assert r.returncode == 0, f"Node eval failed: {r.stderr.decode()}"
    data = json.loads(r.stdout.decode().strip())
    assert "error" not in data, "Could not extract formatDurationCompact"
    return data


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_seconds_precision():
    """Sub-minute durations display second-level precision (not rounded to 1m)."""
    results = _run_formatter()
    for ms, expected_fragment in [("30000", "30"), ("5000", "5"), ("45000", "45")]:
        val = results[ms]["value"]
        assert val is not None, f"{ms}ms returned undefined"
        assert re.search(rf"{expected_fragment}\s*s", val), (
            f"formatDurationCompact({ms}) = {val!r}, expected ~{expected_fragment}s"
        )
        assert val != "1m", f"formatDurationCompact({ms}) = '1m' — still buggy"


# [pr_diff] fail_to_pass
def test_minute_second_precision():
    """Durations with both minutes and seconds show combined format."""
    results = _run_formatter()
    # 90000ms = 1m30s
    v90 = results["90000"]["value"]
    assert v90 is not None, "90000ms returned undefined"
    assert re.search(r"(1.*m.*30.*s|1:30|90\s*s)", v90), (
        f"formatDurationCompact(90000) = {v90!r}, expected ~1m30s"
    )
    # 150000ms = 2m30s
    v150 = results["150000"]["value"]
    assert v150 is not None, "150000ms returned undefined"
    assert re.search(r"(2.*m.*30.*s|2:30|150\s*s)", v150), (
        f"formatDurationCompact(150000) = {v150!r}, expected ~2m30s"
    )


# [pr_diff] pass_to_pass
def test_hour_format():
    """Hour-level durations display as hours (rejects trivial seconds-only stub)."""
    results = _run_formatter()
    v = results["3600000"]["value"]
    assert v is not None, "3600000ms returned undefined"
    assert re.search(r"^1\s*h|^60\s*m", v, re.IGNORECASE), (
        f"formatDurationCompact(3600000) = {v!r}, expected ~1h"
    )


# [pr_diff] pass_to_pass
def test_edge_cases_no_crash():
    """Edge inputs (0, undefined, negative) don't crash the formatter."""
    results = _run_formatter()
    for key in ["0", "undefined", "-1000"]:
        entry = results[key]
        assert entry["ok"], f"formatDurationCompact({key}) threw: {entry.get('error')}"
        # Should NOT return a positive duration string for invalid input
        if entry["value"] is not None:
            assert not re.match(r"^\d+[smhd]", entry["value"]), (
                f"formatDurationCompact({key}) = {entry['value']!r} — should not show positive duration"
            )


# [pr_diff] fail_to_pass
def test_callers_handle_undefined():
    """Both callers guard against undefined return from formatDurationCompact."""
    ctrl = Path(f"{REPO}/src/agents/subagent-control.ts").read_text()
    shared = Path(f"{REPO}/src/auto-reply/reply/commands-subagents/shared.ts").read_text()

    for name, src in [("subagent-control.ts", ctrl), ("shared.ts", shared)]:
        assert re.search(
            r"formatDurationCompact\s*\([^)]*\)\s*(\?\?|\|\|)", src
        ) or "formatDurationHuman" in src, (
            f"{name} does not guard against undefined from formatDurationCompact"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_other_exports_preserved():
    """Other exports in subagents-format.ts (formatTokenShort, truncateLine) still exist."""
    src = Path(f"{REPO}/src/shared/subagents-format.ts").read_text()
    assert "formatTokenShort" in src, "formatTokenShort export missing from subagents-format.ts"
    assert "truncateLine" in src, "truncateLine export missing from subagents-format.ts"


# [agent_config] pass_to_pass — CLAUDE.md:144 @ f011d0be28afbc7868f5e55c1117c779bd0a9f10
def test_no_any_types():
    """No 'any' type annotations in modified file (CLAUDE.md: prefer strict typing)."""
    src = Path(f"{REPO}/src/shared/subagents-format.ts").read_text()
    assert ": any" not in src, "Found ': any' in subagents-format.ts — prefer strict typing"


# [agent_config] pass_to_pass — CLAUDE.md:146 @ f011d0be28afbc7868f5e55c1117c779bd0a9f10
def test_no_lint_suppressions():
    """No @ts-nocheck or inline lint suppressions in modified files (CLAUDE.md: fix root causes)."""
    modified_files = [
        "src/shared/subagents-format.ts",
        "src/agents/subagent-control.ts",
        "src/auto-reply/reply/commands-subagents/shared.ts",
    ]
    for rel in modified_files:
        p = Path(f"{REPO}/{rel}")
        if not p.exists():
            continue
        src = p.read_text()
        assert "@ts-nocheck" not in src, f"Found @ts-nocheck in {rel}"
        assert "@ts-ignore" not in src, f"Found @ts-ignore in {rel}"
        # @ts-expect-error is acceptable when justified, but check for blanket use
        for suppression in ["eslint-disable-next-line", "eslint-disable ", "oxlint-ignore"]:
            assert suppression not in src, f"Found '{suppression}' in {rel}"


# [agent_config] fail_to_pass — CLAUDE.md:164 @ f011d0be28afbc7868f5e55c1117c779bd0a9f10
def test_no_duplicate_implementation():
    """No full duplicate of formatDurationCompact (CLAUDE.md: extract helpers, no V2 copies)."""
    src = Path(f"{REPO}/src/shared/subagents-format.ts").read_text()
    matches = list(re.finditer(r"function\s+formatDurationCompact", src))
    if len(matches) == 0:
        # Re-export or delegation — no local function body → good
        return
    # If there's a local function, it should be a thin wrapper (<=10 lines)
    func_match = re.search(
        r"function\s+formatDurationCompact[^{]*\{([\s\S]*?)^\}",
        src, re.MULTILINE,
    )
    if func_match:
        body_lines = [l for l in func_match.group(1).strip().split("\n") if l.strip()]
        assert len(body_lines) <= 10, (
            f"Full duplicate formatDurationCompact ({len(body_lines)} body lines) — "
            "prefer re-export from infra/format-time"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass — repo CI/CD checks (ensures fix doesn't break existing tests)
# ---------------------------------------------------------------------------

# [repo_ci] pass_to_pass
def test_repo_lint():
    """Repo's oxlint passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "exec", "oxlint", "--type-aware"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\\n{r.stdout[-1000:]}{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_format_time_tests():
    """Repo's format-time unit tests pass (pass_to_pass) — related to fix module."""
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "src/infra/format-time/format-time.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"format-time tests failed:\\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_no_conflict_markers():
    """Repo has no conflict markers (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "check:no-conflict-markers"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Conflict markers check failed:\\n{r.stderr[-500:]}"
