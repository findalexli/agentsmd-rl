"""Execution-based fail-to-pass miner.

For each task with a working Docker image and an extractable test command:
  1. Boot a container at base — run the test suite, capture output
  2. Apply solve.sh, re-run the test suite, capture output
  3. Parse both outputs (per-framework) → per-test pass/fail status maps
  4. Diff → f2p = failed_at_base ∩ passed_at_gold; p2p = passed_at_base ∩ passed_at_gold

This matches the SWE-rebench V2 / SWE-bench approach to f2p extraction
(execution-based, not patch-parse-based). Catches f2p tests anywhere in
the suite, not only those literally added by the gold patch.

Driven through E2B so we get parallel docker-in-docker without polluting
the local docker daemon, and so this scales to ~60 concurrent task mines.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from taskforge import exec_log_parsers as parsers

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pick the right parser for a given test command head
# ---------------------------------------------------------------------------

def _parse_log_js_smart(log: str) -> dict[str, str]:
    """JS test runner dispatcher: vitest, jest, mocha, jest-json, tap.

    Many pnpm/npm/yarn/bun test commands invoke whichever runner the project
    uses internally. We don't know which from the head — so try them all and
    return the one that produced the most parseable test names.
    """
    candidates = [
        parsers.parse_log_vitest,
        parsers.parse_log_jest,
        parsers.parse_log_jest_json,
        parsers.parse_log_tap,
        parsers.parse_log_pytest,    # last fallback for PASS/FAIL prefix output
    ]
    best = {}
    for fn in candidates:
        try:
            out = fn(log)
        except Exception:
            continue
        if len(out) > len(best):
            best = out
    return best


PARSER_MAP = {
    "pytest":     parsers.parse_log_pytest,
    "tox":        parsers.parse_log_pytest,
    "nox":        parsers.parse_log_pytest,
    "go test":    parsers.parse_log_gotest,
    "go ":        parsers.parse_log_gotest,
    "mage":       parsers.parse_log_gotest,    # mage is a Go magefile runner
    "cargo test": parsers.parse_log_cargo,
    "cargo ":     parsers.parse_log_cargo,
    "phpunit":    parsers.parse_log_phpunit,
    "mvn":        parsers.parse_log_maven,
    "gradle":     parsers.parse_log_gradle_custom,
    # JS family — route through the smart dispatcher because the head doesn't
    # tell us which runner the project actually uses inside.
    "vitest":     parsers.parse_log_vitest,
    "jest":       parsers.parse_log_jest,
    "pnpm":       _parse_log_js_smart,
    "npm":        _parse_log_js_smart,
    "yarn":       _parse_log_js_smart,
    "bun":        _parse_log_js_smart,
    "node":       _parse_log_js_smart,
    "deno":       _parse_log_js_smart,
}

# Step-command and step-name patterns we strongly prefer (test runs).
_TEST_CMD_HINT = re.compile(r"\b(test|tests|spec|specs)\b", re.IGNORECASE)
# Step-command we definitely want to skip even if it has a recognized head.
_DENY_CMD = re.compile(
    r"\b(install|setup|cache|checkout|fetch|clone|download|upload|"
    r"configure|login|credential|build-only|prepare|publish|deploy|"
    r"benchmark)\b",
    re.IGNORECASE,
)


def _norm(cmd: str) -> str:
    """Lowercase + collapse whitespace."""
    return re.sub(r"\s+", " ", (cmd or "").strip().lower())


def pick_parser(cmd: str):
    """Return the most appropriate log parser for a test command, or None."""
    n = _norm(cmd)
    if not n: return None
    # Try the longest matching prefix first
    for head in sorted(PARSER_MAP, key=len, reverse=True):
        if n.startswith(head):
            return PARSER_MAP[head]
    return None


# Generic install fallbacks per runner family. We try these BEFORE the test
# command if the chosen test job has no prior setup steps in our extracted spec.
# Each entry is best-effort: failures are masked so downstream tests still run.
GENERIC_INSTALL = {
    "pytest": [
        # PEP 668 in slim images blocks naked pip — pass --break-system-packages
        "pip install --break-system-packages -e . 2>&1 | tail -10 "
        "|| pip install --break-system-packages -r requirements.txt 2>&1 | tail -10 "
        "|| pip install -e . 2>&1 | tail -10 || true",
        "pip install --break-system-packages pytest pytest-mock 2>&1 | tail -3 || true",
    ],
    "tox":  ["pip install --break-system-packages -e . 2>&1 | tail -5 || true"],
    "nox":  ["pip install --break-system-packages -e . 2>&1 | tail -5 || true"],
    "pnpm": ["pnpm install --frozen-lockfile 2>&1 | tail -10 || pnpm install 2>&1 | tail -10 || true"],
    "npm":  ["npm ci 2>&1 | tail -10 || npm install 2>&1 | tail -10 || true"],
    "yarn": ["yarn install --frozen-lockfile 2>&1 | tail -10 || yarn install 2>&1 | tail -10 || true"],
    "bun":  ["bun install 2>&1 | tail -10 || true"],
    "cargo": ["cargo fetch 2>&1 | tail -3 || true"],
    "go":   ["go mod download 2>&1 | tail -3 || true"],
    "go test": ["go mod download 2>&1 | tail -3 || true"],
    "mage": ["go install github.com/magefile/mage@latest 2>&1 | tail -3 || true",
             "go mod download 2>&1 | tail -3 || true"],
}

# Pip install commands often need --break-system-packages on Debian/Ubuntu slim
# (PEP 668). Patch any pip install command in setup_cmds to add the flag.
def _patch_pip_install(cmd: str) -> str:
    return re.sub(
        r"\bpip(3?)\s+install\s+(?!.*--break-system-packages)(?!.*--user)",
        r"pip\1 install --break-system-packages ",
        cmd,
    )


def pick_setup_and_test_commands(ci_spec: dict) -> tuple[list[str], str, str] | None:
    """Pick the full (setup_cmds, test_cmd, parser_key) for a check.

    Strategy:
      1. Find the chosen test step (across f2p first, then p2p)
      2. Collect prior steps in the SAME check as setup
      3. Also collect install steps from OTHER checks (cross-job setup —
         many CI workflows put install in a setup job, then test in a separate
         job that depends on it)
      4. Fall back to generic installs (pip install -e ., pnpm install, etc.)
         if no install steps were found.

    Returns None if nothing usable.
    """
    chosen_check = chosen_test_step = None
    for check_kind in ("f2p", "p2p"):
        for check in [c for c in (ci_spec.get("checks") or []) if c.get("kind") == check_kind]:
            for step in check.get("steps", []) or []:
                cmd = (step.get("command") or "").strip()
                name = (step.get("step_name") or "").lower()
                if not cmd or "${{" in cmd: continue
                if re.search(r"\bdocker\s+(run|exec|compose)\b", cmd): continue
                if pick_parser(cmd) is None: continue
                if _DENY_CMD.search(name) or _DENY_CMD.search(cmd[:80]): continue
                if _TEST_CMD_HINT.search(name) or _TEST_CMD_HINT.search(cmd[:200]):
                    chosen_check, chosen_test_step = check, step
                    break
            if chosen_test_step: break
        if chosen_test_step: break
    if not chosen_test_step: return None

    setup_cmds: list[str] = []
    INSTALL_RE = re.compile(
        r"\b(pip\s+install|pnpm\s+install|npm\s+(ci|install)|yarn\s+install|"
        r"bundle\s+install|bundle\s+exec|cargo\s+(build|fetch)|"
        r"go\s+mod\s+(download|tidy)|mvn\s+install|gradle\s+build|"
        r"composer\s+install)\b",
        re.IGNORECASE,
    )

    # 1. Prior steps in same check
    for step in chosen_check.get("steps", []) or []:
        if step is chosen_test_step: break
        cmd = (step.get("command") or "").strip()
        if not cmd or "${{" in cmd: continue
        cond = (step.get("if_cond") or "").lower()
        if "windows" in cond or "macos" in cond: continue
        if re.search(r"\bdocker\s+(run|exec|compose|build|push)\b", cmd): continue
        cmd = re.sub(r"^sudo\s+", "", cmd)
        setup_cmds.append(cmd)

    # 2. Install commands from OTHER checks (cross-job setup pattern)
    if not any(INSTALL_RE.search(c[:200]) for c in setup_cmds):
        cross_install: list[str] = []
        for c in (ci_spec.get("checks") or []):
            if c is chosen_check: continue
            for step in c.get("steps", []) or []:
                cmd = (step.get("command") or "").strip()
                if not cmd or "${{" in cmd: continue
                cond = (step.get("if_cond") or "").lower()
                if "windows" in cond or "macos" in cond: continue
                if not INSTALL_RE.search(cmd[:200]): continue
                cmd = re.sub(r"^sudo\s+", "", cmd)
                # Take only the install line(s), drop the rest of multi-line scripts
                kept = "\n".join(ln for ln in cmd.split("\n") if INSTALL_RE.search(ln))
                if kept and kept not in cross_install:
                    cross_install.append(kept)
        setup_cmds = cross_install + setup_cmds  # cross-install first, then in-check

    test_cmd = chosen_test_step["command"].strip()
    head = _norm(test_cmd).split()[0]

    # 3. ALWAYS append generic install fallback. Even if cross-job installs exist,
    # they may miss test-only deps (pytest-mock, etc.). Best-effort `|| true` so
    # they don't fail the chain.
    generic = []
    for k, v in GENERIC_INSTALL.items():
        if _norm(test_cmd).startswith(k) or _norm(test_cmd).split()[0] == k:
            generic = v; break
    # Real installs come first (so they win cache); then generic top-up
    setup_cmds = setup_cmds + generic

    # Patch all pip-install commands to use --break-system-packages (Debian/Ubuntu PEP 668)
    setup_cmds = [_patch_pip_install(c) for c in setup_cmds]
    return (setup_cmds, test_cmd, head)


def pick_test_command(ci_spec: dict) -> tuple[str, str] | None:
    """Legacy single-command picker. Prefer pick_setup_and_test_commands."""
    full = pick_setup_and_test_commands(ci_spec)
    if not full: return None
    _setup, test_cmd, head = full
    return (test_cmd, head)


# ---------------------------------------------------------------------------
# Dual-pass executor (E2B + docker-in-docker)
# ---------------------------------------------------------------------------

@dataclass
class ExecResult:
    task: str
    image: str = ""
    test_cmd: str = ""
    parser_used: str = ""
    base_count: int = 0
    gold_count: int = 0
    f2p: list[str] = field(default_factory=list)
    p2p: list[str] = field(default_factory=list)
    f2p_count: int = 0
    p2p_count: int = 0
    elapsed_s: float = 0.0
    error: str = ""
    base_log_tail: str = ""
    gold_log_tail: str = ""


async def run_dual_pass(
    sandbox,                       # AsyncSandbox with docker available
    task_name: str,
    docker_image: str,             # e.g. ghcr.io/owner/repo/<task>:<tag>
    test_cmd: str,
    solve_sh_text: str,
    *,
    setup_cmds: list[str] | None = None,
    test_timeout: int = 600,
    quiet: bool = True,
    gh_token: str = "",
) -> ExecResult:
    """Run the suite at base, then apply solve.sh, then run again. Diff."""
    import asyncio as _asyncio
    import time
    t0 = time.monotonic()
    r = ExecResult(task=task_name, image=docker_image, test_cmd=test_cmd)
    try:
        parser = pick_parser(test_cmd)
        if parser is None:
            r.error = f"no parser for command head: {test_cmd[:50]!r}"
            return r
        r.parser_used = parser.__name__

        # Wait for docker daemon to be ready (first sandbox boot can take a few s)
        for _ in range(15):
            code, _, _ = await _run_cmd(sandbox, "docker info >/dev/null 2>&1", timeout=10)
            if code == 0: break
            await _asyncio.sleep(2)
        else:
            r.error = "docker daemon never became ready in sandbox"
            return r

        # Login to ghcr (private packages need auth)
        if gh_token:
            code, _, err = await _run_cmd(sandbox,
                f"echo {shlex.quote(gh_token)} | docker login ghcr.io -u findalexli --password-stdin",
                timeout=30)
            if code != 0 and "Login Succeeded" not in (err or ""):
                r.error = f"docker login failed: {err[:200]}"
                # Continue anyway — image might be public
        # Pull the image
        code, _, err = await _run_cmd(sandbox,
            f"docker pull --quiet {shlex.quote(docker_image)}",
            timeout=900)
        if code != 0:
            r.error = f"docker pull failed: {err[:300]}"
            return r

        # Upload solve.sh into the sandbox
        await sandbox.files.write(f"/tmp/{task_name}__solve.sh", solve_sh_text.encode())

        # Build the full inline test command: setup + test, joined with ; so
        # one failing setup line doesn't kill the test run (CI installs are
        # often best-effort; missing optional deps are common).
        full_test = test_cmd + " 2>&1; exit 0"
        if setup_cmds:
            # Wrap each setup line so failures don't abort the chain
            setup_join = "; ".join(c.replace("\n", " && ") + " 2>&1 || true" for c in setup_cmds)
            full_test = f"{setup_join}; echo '====TEST===='; {full_test}"

        # Pass 1: base — merge stderr into stdout so parser sees everything
        bcode, bstdout, bstderr = await _run_cmd(sandbox,
            f"docker run --rm -e PYTHONUNBUFFERED=1 "
            f"  {shlex.quote(docker_image)} "
            f"  bash -c {shlex.quote(full_test)} 2>&1",
            timeout=test_timeout)
        base_log = (bstdout or "") + (bstderr or "")

        # Pass 2: gold — apply solve.sh, then setup + test in the SAME container
        full_gold = "bash /solution/solve.sh > /tmp/solve.log 2>&1; " + full_test
        gcode, gstdout, gstderr = await _run_cmd(sandbox,
            f"docker rm -f {task_name}-gold 2>/dev/null; "
            f"docker run --name {task_name}-gold "
            f"  -v /tmp/{task_name}__solve.sh:/solution/solve.sh:ro "
            f"  -e PYTHONUNBUFFERED=1 "
            f"  {shlex.quote(docker_image)} "
            f"  bash -c {shlex.quote(full_gold)} 2>&1; "
            f"docker rm -f {task_name}-gold 2>/dev/null || true",
            timeout=test_timeout + 600)
        gold_log = (gstdout or "") + (gstderr or "")

        # Strip everything before "====TEST====" so the parser only sees test output
        if "====TEST====" in base_log:
            base_log = base_log.split("====TEST====", 1)[1]
        if "====TEST====" in gold_log:
            gold_log = gold_log.split("====TEST====", 1)[1]

        # Strip ANSI escape codes before parsing — vitest, jest, cargo, et al.
        # all emit ANSI colors by default, and most parsers' regex don't handle
        # them. SWE-rebench V2 handles this in their pipeline outside the parser.
        base_log_clean = parsers.ansi_escape(base_log) if base_log else ""
        gold_log_clean = parsers.ansi_escape(gold_log) if gold_log else ""
        # Save tails of CLEANED log for debugging (so we can see what parser saw)
        r.base_log_tail = base_log_clean[-2500:]
        r.gold_log_tail = gold_log_clean[-2500:]
        # Parse both logs
        base_status = parser(base_log_clean)
        gold_status = parser(gold_log_clean)
        r.base_count = len(base_status)
        r.gold_count = len(gold_status)

        # f2p: failed at base AND passed at gold, OR only-in-gold AND passed
        # (PR-added tests don't exist at base — SWE-bench treats those as f2p)
        f2p_set = set()
        for name, gstat in gold_status.items():
            if gstat.upper() != "PASSED": continue
            bstat = base_status.get(name, "").upper()
            if bstat in {"FAILED", "ERROR"}:
                f2p_set.add(name)
            elif bstat == "" and base_status:
                # Only in gold — newly added by PR. Sanity check: base must have
                # produced *some* tests (else base run failed entirely and the
                # diff is meaningless).
                f2p_set.add(name)
        f2p = sorted(f2p_set)
        # p2p: passed at base AND gold
        p2p = sorted([
            name for name, status in base_status.items()
            if status.upper() == "PASSED"
            and gold_status.get(name, "").upper() == "PASSED"
        ])
        r.f2p = f2p
        r.p2p = p2p
        r.f2p_count = len(f2p)
        r.p2p_count = len(p2p)
    except Exception as e:
        r.error = f"{type(e).__name__}: {str(e)[:300]}"
    r.elapsed_s = round(time.monotonic() - t0, 1)
    return r


async def _run_cmd(sandbox, cmd: str, *, timeout: int = 600,
                    user: str = "root") -> tuple[int, str, str]:
    """Run cmd as `user` (default root, has docker access). Returns (code, stdout, stderr).
    Never raises — test commands legitimately exit non-zero when tests fail."""
    try:
        from e2b.sandbox.commands.command_handle import CommandExitException
    except Exception:
        CommandExitException = Exception
    try:
        result = await sandbox.commands.run(cmd, timeout=timeout, user=user)
        return result.exit_code, result.stdout or "", result.stderr or ""
    except CommandExitException as e:
        return e.exit_code, getattr(e, "stdout", "") or "", getattr(e, "stderr", "") or ""
    except Exception as e:
        return -1, "", f"sandbox-error: {type(e).__name__}: {str(e)[:200]}"
