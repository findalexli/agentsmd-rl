#!/usr/bin/env python3
"""Convert mined CI check-runs JSON → tests/test_outputs.py + manifest checks.

For each kept check-run:
  - Collapse matrix variants of the same job into one canonical test (the
    Docker image pins one Python/Node version anyway).
  - Extract the meaningful "test step" command (drops setup/install/cache).
  - Emit a pytest test that runs the command via subprocess and asserts
    returncode==0.

Skipped commands: install (already done in Dockerfile), checkout, cache,
upload-artifact, codecov-upload, etc.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Steps we don't re-run inside our Docker (already done at image build time)
SETUP_STEP_DENYLIST = re.compile(
    r"\b(install|setup|cache|checkout|fetch|clone|download|upload[- ]?artifact|"
    r"codecov|coveralls|create[- ]?artifact|store[- ]?artifact|configure|"
    r"login|credential)\b",
    re.IGNORECASE,
)

# Step names that are explicitly the test step
TEST_STEP_HINT = re.compile(
    r"\b(test|tests|pytest|jest|vitest|cargo[- ]?test|go[- ]?test|spec|"
    r"unit|integration|e2e|lint|format|typecheck|tsc|build|compile|"
    r"check|verify|validate|coverage)\b",
    re.IGNORECASE,
)

# Allowlist: command must START with one of these recognized runners.
# This is the strictest filter — stops GHA-template-only commands and
# shell-bookkeeping junk from leaking through.
_RECOGNIZED_RUNNER_HEAD = re.compile(
    r"^\s*("
    r"npm|npx|pnpm|yarn|bun|"                      # JS package managers
    r"node\b|deno\b|"
    r"python\b|python3\b|pip\b|pip3\b|uv\b|uvx\b|"
    r"pytest|tox|nox|"
    r"cargo|rustup|"
    r"go\s+(test|build|vet|fmt|run)|"
    r"mvn|gradle|ant|"
    r"make|just|task|mage\b|"                       # mage = Go magefile runner
    r"docker\s+(run|exec|build)|docker-compose|"
    r"bash\s+(\./|/|scripts/|test|run)|"           # bash <script>
    r"sh\s+(\./|/|scripts/|test|run)|"
    r"ruff|mypy|black|isort|flake8|prettier|eslint|tslint|staticcheck|"
    r"vitest|jest|mocha|cypress|playwright|"
    r"tsc\b|tsx\b|swc\b|vite\b|esbuild\b|webpack\b|"
    r"phpunit|"                                     # PHP
    r"bundle\s+exec|rspec|"                         # Ruby
    r"dotnet\s+(test|build|run)|"                   # C#
    r"swift\s+(test|build|run)|"                    # Swift
    r"dub\s+(test|build)|"                          # D
    r"clojure|lein\s+test|"                         # Clojure
    r"jq\s+|"
    r"\.[/].*?\.(sh|py|rb|pl)\b"                  # ./script.sh style — no trailing |
    r")",
    re.IGNORECASE,
)


_BOOKKEEPING_TOKENS = {
    "if", "else", "elif", "fi", "for", "while", "case",
    "echo", "printf", "exit", "return", "set", "export",
    "mv", "cp", "rm", "mkdir", "rmdir", "touch", "ln",
    "cd", "pwd", "ls", "cat", "head", "tail", "grep",
    "awk", "sed", "tr", "sort", "uniq", "wc", "tee",
    "true", "false", ":", "source", ".",
}

# Hard rejection patterns from the v3 audit:
# - Docker-in-Docker (no daemon in our test sandbox)
# - Hardware-specific scripts (ROCm/AMD/CUDA/VRAM)
# - Background processes (&, &>) — would hang or false-pass
# - Snapshot/mutation modes (don't validate, they MUTATE)
# - Env vars beyond a tiny safe-set (CI-time only — won't expand in our Docker)
_REJECT_HARDWARE = re.compile(
    r"\b(rocm|amd_ci|amd_gpu|vram_clear|cuda_visible_devices|nvidia[- ]smi)\b",
    re.IGNORECASE,
)
_REJECT_DOCKER_IN_DOCKER = re.compile(
    r"\bdocker\s+(run|exec|compose|buildx|build|push|pull|tag|kill|rm)\b",
    re.IGNORECASE,
)
_REJECT_MUTATION_MODES = re.compile(
    r"--(update[- ]?snapshots?|update[- ]?baselines?|write|fix|in[- ]?place)\b",
    re.IGNORECASE,
)
# Env vars: bare $VAR or ${VAR}. Allow a tiny safe-set common in repos.
_SAFE_ENV_VARS = {"HOME", "PATH", "PWD", "USER", "TMPDIR", "PYTHONPATH",
                  "REPO", "WORKSPACE", "CI"}
_BARE_ENV_VAR = re.compile(r"\$\{?([A-Z_][A-Z0-9_]*)\}?")
# Background process suffix: trailing & (not && or 2>&1)
_BACKGROUND_SUFFIX = re.compile(r"(?:^|[^&])&\s*(?:>|$)")
_TRAILING_BACKSLASH = re.compile(r"\\\s*$")
# Subshell substitution — both $(...) and `...`
_SUBSHELL = re.compile(r"\$\([^)]*\)|`[^`]*`")


def _split_shell(cmd: str) -> list[str]:
    """Split a shell command on &&, ||, |, ; — best-effort, ignoring those inside quotes."""
    out, cur = [], ""
    in_sq = in_dq = False
    i = 0
    while i < len(cmd):
        c = cmd[i]
        if c == "'" and not in_dq: in_sq = not in_sq
        elif c == '"' and not in_sq: in_dq = not in_dq
        elif not in_sq and not in_dq:
            if c in (";", "|") and i+1 < len(cmd) and cmd[i+1] == c:
                out.append(cur.strip()); cur = ""; i += 2; continue
            if c == "&" and i+1 < len(cmd) and cmd[i+1] == "&":
                out.append(cur.strip()); cur = ""; i += 2; continue
            if c == ";":
                out.append(cur.strip()); cur = ""; i += 1; continue
        cur += c
        i += 1
    if cur.strip(): out.append(cur.strip())
    return [x for x in out if x]


def _segment_is_runnable(seg: str) -> bool:
    """Check a single shell segment (already split off `&&` / `;` / etc.)."""
    s = (seg or "").strip()
    if not s or s.startswith("#"): return False
    if "${{" in s: return False
    # Trailing backslash → truncated multi-line command (broken)
    if _TRAILING_BACKSLASH.search(s): return False
    # Background process (&, &>) → would hang or always-pass
    if _BACKGROUND_SUFFIX.search(s): return False
    # Subshell substitution → won't expand in our Docker
    if _SUBSHELL.search(s): return False
    # Hardware-specific
    if _REJECT_HARDWARE.search(s): return False
    # Docker-in-Docker
    if _REJECT_DOCKER_IN_DOCKER.search(s): return False
    # Mutation-mode flags (don't validate, they mutate)
    if _REJECT_MUTATION_MODES.search(s): return False
    # CI env vars beyond safe-set
    for m in _BARE_ENV_VAR.finditer(s):
        if m.group(1) not in _SAFE_ENV_VARS: return False
    # Bookkeeping head
    first_tok = s.split()[0] if s.split() else ""
    if first_tok in _BOOKKEEPING_TOKENS: return False
    return bool(_RECOGNIZED_RUNNER_HEAD.match(s))


def _line_is_runnable(line: str) -> bool:
    """Single-line runnable check. A line may itself contain && separators —
    accept the line if ANY segment is a recognized runner."""
    return any(_segment_is_runnable(seg) for seg in _split_shell(line))


def _is_runnable_command(cmd: str) -> bool:
    """Return True if command looks like a runnable test/lint/build invocation.

    For multi-line `run:` blocks: accept if AT LEAST ONE non-bookkeeping line
    is a recognized runner. Caller may also call `extract_runnable_lines` to
    get just those lines.
    """
    if not cmd or not cmd.strip(): return False
    if "${{" in cmd: return False
    lines = cmd.split("\n")
    # If single-line, do the same check (no continuation merging)
    if len(lines) == 1:
        return _line_is_runnable(lines[0])
    # Multi-line: require at least one runnable line
    return any(_line_is_runnable(ln) for ln in lines)


def extract_runnable_lines(cmd: str) -> str:
    """For a multi-line `run:` block, return only runnable segments joined with &&.

    Drops setup/install/cd/echo lines AND the bookkeeping segments inside
    a single line like `cd packages/x && pnpm install && pnpm test` →
    keeps `pnpm test`.
    Preserves order. Single-segment commands pass through unchanged.
    """
    if not cmd: return ""
    kept = []
    for line in cmd.split("\n"):
        for seg in _split_shell(line):
            if _segment_is_runnable(seg):
                kept.append(seg)
    if not kept: return cmd.strip()
    if len(kept) == 1: return kept[0]
    return " && ".join(kept)


def _collapse_matrix(checks: list[dict]) -> list[dict]:
    """Group check-runs by base name (strip matrix). Pick canonical for each."""
    groups: dict[str, list[dict]] = {}
    for c in checks:
        name = c.get("name", "")
        # Strip matrix in parens: 'test (22)' → 'test'
        base = re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()
        groups.setdefault(base, []).append(c)
    out = []
    for base, items in groups.items():
        # Prefer one with steps available
        with_steps = [c for c in items if c.get("steps")]
        canonical = (with_steps or items)[0]
        # Annotate the canonical with how many matrix variants it represents
        canonical = {**canonical, "matrix_count": len(items), "base_name": base}
        out.append(canonical)
    return out


def _meaningful_steps(steps: list[dict]) -> list[dict]:
    """Filter to runnable test/lint/build steps. Stricter as of v2:
      - command must pass `_is_runnable_command` (allowlist by runner head)
      - drops GHA `${{...}}` templating
      - drops shell bookkeeping (mv/mkdir/echo/if/etc.)
      - drops setup-flavored step names (install/cache/checkout)

    Step-name escape hatch: if the step `name` clearly says it's a test step
    (matches TEST_STEP_HINT), trust it even when the command head isn't on
    our allowlist (e.g. project-specific runners like `mage -v test`,
    `./run_tests.sh`, etc.). Hard rejects (GHA template, hardware,
    docker-in-docker, mutation modes) still apply.
    """
    kept = []
    for s in steps or []:
        cmd = s.get("command", "") or ""
        name = s.get("step_name", "") or ""
        if not cmd.strip(): continue
        if SETUP_STEP_DENYLIST.search(name) and not TEST_STEP_HINT.search(name):
            continue
        # Trust the step name when it strongly hints "this is the test step"
        if TEST_STEP_HINT.search(name):
            if "${{" in cmd: continue
            if _REJECT_HARDWARE.search(cmd): continue
            if _REJECT_DOCKER_IN_DOCKER.search(cmd): continue
            if _REJECT_MUTATION_MODES.search(cmd): continue
            kept.append(s); continue
        if not _is_runnable_command(cmd):
            continue
        kept.append(s)
    return kept


def _python_test_id(check: dict, idx: int) -> str:
    """Make a valid Python identifier from the check name."""
    base = check.get("base_name", check.get("name", f"check_{idx}"))
    s = re.sub(r"[^a-zA-Z0-9_]+", "_", base.lower()).strip("_")
    if not s or not s[0].isalpha(): s = f"ci_{s}" if s else f"ci_check_{idx}"
    return f"test_ci_{s}"


def _select_main_command(steps: list[dict]) -> dict | None:
    """Pick the single most-test-like step from a list."""
    meaningful = _meaningful_steps(steps)
    if not meaningful: return None
    # Prefer steps whose name explicitly mentions "test"
    test_named = [s for s in meaningful if re.search(r"\btest", s.get("step_name","") or "", re.I) or re.search(r"\btest", s.get("command","") or "", re.I)]
    if test_named: return test_named[0]
    return meaningful[-1]  # last meaningful step (often the test step in CI)


def _step_id(step: dict, idx: int) -> str:
    """Make a Python identifier from a step name/command."""
    raw = step.get("step_name") or step.get("command","").split()[0]
    s = re.sub(r"[^a-zA-Z0-9_]+", "_", str(raw).lower()).strip("_")
    if not s or not s[0].isalpha(): s = f"step_{s}" if s else f"step_{idx}"
    return s[:40]


MAX_TESTS_PER_TASK = 12  # cap mined tests per task (avoids 30-test bloat)


def _gather_unique_steps(checks: list[dict]) -> list[tuple[dict, dict]]:
    """Return list of (check, step) — one per UNIQUE (check.base_name, step.command).

    We want one test per CI gate (lint, build, test, dist:check, etc.), not just
    one per check-run. Capped at MAX_TESTS_PER_TASK.
    """
    seen_cmds: set[tuple[str, str]] = set()
    seen_extracted: set[str] = set()
    out = []
    for c in checks:
        meaningful = _meaningful_steps(c.get("steps", []))
        for s in meaningful:
            raw_cmd = s["command"].strip()
            extracted = extract_runnable_lines(s["command"]).strip()
            # Dedup on the EXTRACTED command (after filtering bookkeeping out),
            # so identical effective commands across matrix variants collapse.
            key = (c.get("base_name",""), raw_cmd)
            if key in seen_cmds or extracted in seen_extracted: continue
            seen_cmds.add(key); seen_extracted.add(extracted)
            out.append((c, s))
            if len(out) >= MAX_TESTS_PER_TASK:
                return out
    return out


def generate_test_file(spec: dict, repo_path: str = "/workspace/REPO") -> str:
    """Render tests/test_outputs.py source from a mined-spec dict."""
    task = spec.get("task", "?")
    checks = _collapse_matrix(spec.get("checks", []))
    if not checks:
        return f"# CI miner: no check-runs found for {task}\n"

    pairs = _gather_unique_steps(checks)
    if not pairs:
        return f"# CI miner: no actionable steps for {task}\n"

    lines: list[str] = []
    lines.append(f'"""Auto-generated from CI check-runs for {task}.')
    lines.append(f'Source: {spec.get("repo")}#{spec.get("merge_commit","?")[:8]}')
    lines.append(f'Mined: {spec.get("fetched_at","?")}')
    lines.append(f'Total: {len(pairs)} CI step(s) across {len(checks)} job(s)')
    lines.append('"""')
    lines.append('import os, subprocess')
    lines.append('')
    lines.append(f'REPO = {repo_path!r}')
    lines.append('')

    seen_fnames: set[str] = set()
    for idx, (c, s) in enumerate(pairs):
        # For multi-line `run:`, keep only the runnable lines
        cmd = extract_runnable_lines(s["command"]).strip()
        wd = s.get("working_directory") or ""
        wd_clause = f', cwd=os.path.join(REPO, {wd!r})' if wd else ', cwd=REPO'
        kind = c.get("kind", "p2p")
        ttl = "fail_to_pass" if kind == "f2p" else "pass_to_pass"

        fname = f"test_ci_{c.get('base_name','x').replace(' ','_').replace('-','_')[:30]}_{_step_id(s, idx)}"
        fname = re.sub(r"[^a-zA-Z0-9_]+", "_", fname.lower()).strip("_")
        if not fname.startswith("test_"): fname = "test_" + fname.lstrip("_")
        # Always-unique suffix to prevent silent overrides (pytest only keeps
        # the last def of a given name). Audit found 6+ tasks where 2-4
        # tests collided on the same name and only one ran.
        base = fname
        n = 1
        while fname in seen_fnames:
            n += 1
            fname = f"{base}_{n}"
        seen_fnames.add(fname)

        # Sanitize step_name: strip embedded quotes so it survives BOTH a `# comment`
        # AND an f-string without breaking parsing. Many YAML step names contain
        # quotes (e.g. step_name='"Check ... pyproject.toml"').
        _step_name_safe = (
            (s.get("step_name", "") or "")
            .replace('"', "'")
            .replace("\n", " ")
            .replace("\r", " ")
        )[:140]
        _base_name_safe = (c.get("base_name", "") or "").replace('"', "'")[:80]
        _ttl_safe = f"{ttl} | CI job {_base_name_safe!r} → step {_step_name_safe!r}"
        lines.append(f'def {fname}():')
        lines.append(f'    # {_ttl_safe}')
        lines.append(f'    r = subprocess.run(')
        lines.append(f'        ["bash", "-lc", {cmd!r}]{wd_clause},')
        # 5 min per CI command — caps total test.sh wall time for tasks with many
        # mined gates so we stay inside Harbor's verifier-timeout budget.
        lines.append(f'        capture_output=True, text=True, timeout=300)')
        lines.append(f'    assert r.returncode == 0, (')
        lines.append(f'        f"CI step {_step_name_safe!r} failed (returncode={{r.returncode}}):\\n"')
        lines.append(f'        f"stdout: {{r.stdout[-1500:]}}\\nstderr: {{r.stderr[-1500:]}}")')
        lines.append('')
    return "\n".join(lines)


def generate_manifest_checks(spec: dict) -> list[dict]:
    """Emit the eval_manifest.yaml `checks:` block entries (Pydantic-shape) —
    one entry per unique (check_run, step) gate. Names match generate_test_file."""
    out = []
    checks = _collapse_matrix(spec.get("checks", []))
    pairs = _gather_unique_steps(checks)
    seen: set[str] = set()
    for idx, (c, s) in enumerate(pairs):
        kind = c.get("kind", "p2p")
        fname = f"test_ci_{c.get('base_name','x').replace(' ','_').replace('-','_')[:30]}_{_step_id(s, idx)}"
        fname = re.sub(r"[^a-zA-Z0-9_]+", "_", fname.lower()).strip("_")
        if not fname.startswith("test_"): fname = "test_" + fname.lstrip("_")
        base = fname
        n = 1
        while fname in seen:
            n += 1
            fname = f"{base}_{n}"
        seen.add(fname)
        out.append({
            "id": fname,
            "type": "fail_to_pass" if kind == "f2p" else "pass_to_pass",
            "origin": "repo_tests",
            "description": (f"CI: {c.get('base_name','?')} / {s.get('step_name','?')}")[:200],
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mined", required=True, help="Mined JSON file or JSONL")
    ap.add_argument("--task", help="If --mined is JSONL, only generate for this task")
    ap.add_argument("--out-dir", default="pipeline_logs/ci_miner_dogfood/generated")
    ap.add_argument("--repo-path", default="/workspace/REPO", help="Path the test will use as REPO")
    args = ap.parse_args()

    src = Path(args.mined).read_text()
    if args.mined.endswith(".jsonl"):
        rows = [json.loads(l) for l in src.splitlines() if l.strip()]
    else:
        rows = [json.loads(src)]
    if args.task:
        rows = [r for r in rows if r.get("task") == args.task]
    if not rows:
        return print(f"No matching task: {args.task}", file=sys.stderr) or 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for spec in rows:
        task = spec.get("task", "unnamed")
        d = out_dir / task
        d.mkdir(parents=True, exist_ok=True)
        (d / "test_outputs.py").write_text(generate_test_file(spec))
        (d / "manifest_checks.json").write_text(json.dumps(generate_manifest_checks(spec), indent=2))
        n_checks = len(_collapse_matrix(spec.get("checks", [])))
        n_emit = sum(1 for c in _collapse_matrix(spec.get("checks", [])) if _select_main_command(c.get("steps", [])))
        print(f"  {task}: {n_emit}/{n_checks} checks → {d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
