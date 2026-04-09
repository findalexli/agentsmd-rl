"""
Task: remix-componentchange-handleupdate-promise-cascading-update
Repo: remix-run/remix @ 649aecadeb54fc3027a2b6a85020dd31421b5327
PR:   11060

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/remix"
COMPONENT = f"{REPO}/packages/component"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files parse without errors."""
    files = [
        Path(f"{COMPONENT}/src/lib/component.ts"),
        Path(f"{COMPONENT}/src/lib/scheduler.ts"),
    ]
    for f in files:
        assert f.exists(), f"File not found: {f}"
        content = f.read_text()
        assert len(content) > 100, f"File suspiciously small: {f}"
        assert "export" in content, f"Missing exports in {f}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_update_returns_promise():
    """handle.update() must return Promise<AbortSignal> instead of void."""
    component_ts = Path(f"{COMPONENT}/src/lib/component.ts").read_text()

    # The Handle interface must declare update() returning Promise<AbortSignal>
    assert "Promise<AbortSignal>" in component_ts, \
        "Handle.update() must return Promise<AbortSignal>"

    # The old signature accepting a task callback must be removed
    # Find the Handle interface block and check update doesn't take task param
    interface_match = re.search(
        r'export\s+interface\s+Handle\b.*?\{(.*?)\n\}',
        component_ts,
        re.DOTALL,
    )
    assert interface_match, "Handle interface not found in component.ts"
    interface_body = interface_match.group(1)
    # update should not accept task parameter in the interface
    assert re.search(r'update\s*\(\s*task', interface_body) is None, \
        "Handle.update() should no longer accept a task parameter"


# [pr_diff] fail_to_pass
def test_update_implementation_creates_promise():
    """The update() implementation must create and return a Promise."""
    component_ts = Path(f"{COMPONENT}/src/lib/component.ts").read_text()

    # The implementation must use new Promise to wrap the task queue
    assert "new Promise" in component_ts, \
        "update() implementation must create a new Promise"
    assert "resolve" in component_ts, \
        "update() implementation must resolve the promise with a signal"


# [pr_diff] fail_to_pass
def test_cascading_update_guard():
    """scheduler.ts must detect and prevent infinite cascading updates."""
    scheduler_ts = Path(f"{COMPONENT}/src/lib/scheduler.ts").read_text()

    # Must have a maximum update limit
    has_max = re.search(r'(?:MAX|max).*(?:UPDATE|CASCAD|update|cascad)', scheduler_ts)
    has_counter = "cascad" in scheduler_ts.lower() or "updateCount" in scheduler_ts
    assert has_max or has_counter, \
        "scheduler.ts must have a cascading update limit/counter"

    # Must dispatch an error when the limit is exceeded
    assert "infinite" in scheduler_ts.lower() or "loop" in scheduler_ts.lower(), \
        "scheduler.ts must report an error message about infinite loops"

    # Must have a counter variable tracking cascading depth
    has_count_var = re.search(r'(?:count|depth|level)\s*[\+\=]', scheduler_ts, re.IGNORECASE)
    assert has_count_var, \
        "scheduler.ts must track cascading update count/depth"


# [pr_diff] fail_to_pass
def test_schedule_update_no_task_param():
    """scheduleUpdate internal function must not accept a task parameter."""
    component_ts = Path(f"{COMPONENT}/src/lib/component.ts").read_text()

    # The scheduleUpdate variable should be typed as () => void, not (task?) => void
    # Check that the scheduleUpdate declaration doesn't reference Task
    schedule_decl = re.search(
        r'let\s+scheduleUpdate\s*:\s*\((.*?)\)\s*=>\s*void',
        component_ts,
    )
    assert schedule_decl, "scheduleUpdate variable declaration not found"
    params = schedule_decl.group(1).strip()
    assert "task" not in params.lower() and "Task" not in params, \
        "scheduleUpdate should not accept a task parameter"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — upstream regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_tests_pass():
    """Upstream vitest suite for the component package still passes."""
    r = subprocess.run(
        ["pnpm", "--filter", "@remix-run/component", "run", "test"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    output = (r.stdout.decode() + r.stderr.decode())[-3000:]
    assert r.returncode == 0, f"Component tests failed:\n{output}"


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — documentation/config file updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass — packages/component/AGENTS.md

    # Must show the await handle.update() usage pattern
    assert "await handle.update()" in agents_md, \
        "AGENTS.md must show 'await handle.update()' pattern"

    # Must mention the signal returned by update()
    agents_lower = agents_md.lower()
    assert "signal" in agents_lower and "abort" in agents_lower, \
        "AGENTS.md should mention AbortSignal returned by handle.update()"

    # The handle.update heading should NOT show the old task? parameter
    heading_matches = re.findall(r'#+\s*`?handle\.update\((.*?)\)', agents_md)
    for match in heading_matches:
        assert "task" not in match.lower(), \
            f"AGENTS.md heading still shows old task parameter: handle.update({match})"


# [config_edit] fail_to_pass — packages/component/README.md

    # Must mention await or Promise for handle.update()
    has_new_api = (
        "await handle.update()" in readme
        or ("Promise" in readme and "handle.update" in readme)
        or ("AbortSignal" in readme and "handle.update" in readme)
    )
    assert has_new_api, \
        "README.md must document that handle.update() returns Promise<AbortSignal>"

    # The API summary line for handle.update should not show old task parameter
    for line in readme.split("\n"):
        if "handle.update" in line and ("**" in line or "##" in line):
            assert "task" not in line.lower() or "promise" in line.lower() \
                or "signal" in line.lower() or "await" in line.lower(), \
                f"README API line still shows old parameter: {line.strip()}"
