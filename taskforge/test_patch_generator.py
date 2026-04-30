#!/usr/bin/env python3
"""Convert mined test_patch JSON → f2p test assertions in test_outputs.py.

For each test function the PR added to a test file, generate a pytest
function that runs the underlying framework's test command targeting just
that test name and asserts exit-code 0.

Frameworks supported: pytest, jest, vitest (vitest_or_jest), go_test.

Output: appends to harbor_tasks/<task>/tests/test_outputs.py under a
`# === PR-added f2p tests (taskforge.test_patch_miner) ===` separator.
"""
from __future__ import annotations

import re

# Per-framework subprocess command template
def _cmd_for(framework: str, test_path: str, test_name: str) -> tuple[str, list[str]]:
    """Return ((env_setup), [bash_lc_command]) for running ONE test."""
    p = test_path.replace('"', '\\"')
    n = test_name.replace('"', '\\"')

    if framework == "pytest":
        # pytest <file>::<func> with strict reporting
        cmd = f'python3 -m pytest -x --no-header -p no:cacheprovider "{p}::{n}" 2>&1 | tail -50'
        return ("pytest", cmd)

    if framework in ("jest", "vitest", "vitest_or_jest"):
        # Try to detect which by file context. Default: vitest.
        # Use `pnpm vitest run` with -t (test-name pattern) and the file path.
        # Falls back to plain `npx vitest run` if pnpm fails.
        cmd = (
            f'(pnpm vitest run "{p}" -t "{n}" 2>&1 || '
            f'npx vitest run "{p}" -t "{n}" 2>&1 || '
            f'pnpm jest "{p}" -t "{n}" 2>&1 || '
            f'npx jest "{p}" -t "{n}" 2>&1) | tail -50'
        )
        return ("vitest_or_jest", cmd)

    if framework == "go_test":
        # `go test ./<dir>/ -run <TestName>$ -count=1`
        d = "./" + "/".join(p.split("/")[:-1]) if "/" in p else "./"
        cmd = f'go test {d} -run "^{n}$" -count=1 -v 2>&1 | tail -50'
        return ("go_test", cmd)

    if framework == "cargo_test":
        cmd = f'cargo test "{n}" -- --exact --nocapture 2>&1 | tail -50'
        return ("cargo_test", cmd)

    # unknown: try pytest as best guess
    cmd = f'python3 -m pytest -x --no-header "{p}::{n}" 2>&1 | tail -50'
    return ("unknown", cmd)


def _python_id(name: str, idx: int = 0) -> str:
    s = re.sub(r"[^a-zA-Z0-9_]+", "_", name).strip("_")
    if not s or not s[0].isalpha(): s = f"t_{s}" if s else f"t_{idx}"
    return s[:48]


def generate_test_file_block(spec: dict, repo_path: str = "/workspace/REPO") -> str:
    """Render the body to APPEND to existing test_outputs.py (no header)."""
    if not spec.get("test_files"): return ""
    lines: list[str] = []
    seen: set[str] = set()
    for tf in spec["test_files"]:
        for t in tf.get("added_tests", []):
            fw, cmd = _cmd_for(tf["framework"], tf["path"], t["name"])
            fname = f"test_pr_added_{_python_id(t['name'])}"
            base = fname; n = 1
            while fname in seen:
                n += 1; fname = f"{base}_{n}"
            seen.add(fname)
            lines.append(f'def {fname}():')
            lines.append(f'    """fail_to_pass | PR added test {t["name"]!r} in {tf["path"]!r} ({fw})"""')
            lines.append(f'    r = subprocess.run(')
            lines.append(f'        ["bash", "-lc", {cmd!r}], cwd=REPO,')
            lines.append(f'        capture_output=True, text=True, timeout=300)')
            lines.append(f'    assert r.returncode == 0, (')
            lines.append(f'        f"PR-added test {t["name"]!r} failed (returncode={{r.returncode}}):\\n"')
            lines.append(f'        f"stdout: {{r.stdout[-1500:]}}\\nstderr: {{r.stderr[-1500:]}}")')
            lines.append('')
    return "\n".join(lines)


def generate_manifest_checks(spec: dict) -> list[dict]:
    """Manifest checks list entries (Pydantic-shape). All f2p, origin=pr_diff."""
    out = []
    seen: set[str] = set()
    for tf in spec.get("test_files", []) or []:
        for t in tf.get("added_tests", []):
            fname = f"test_pr_added_{_python_id(t['name'])}"
            base = fname; n = 1
            while fname in seen:
                n += 1; fname = f"{base}_{n}"
            seen.add(fname)
            out.append({
                "id": fname,
                "type": "fail_to_pass",
                "origin": "pr_diff",
                "description": f"PR added test {t['name']!r} in {tf['path']}",
            })
    return out
