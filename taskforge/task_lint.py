"""Programmatic (deterministic, no-LLM) checks for the rubrics defined in
taskforge.rubrics that can be verified by regex / file inspection.

Runs in ~100ms per task. Designed to be called:
  - inside node_qgate (scaffold pipeline, post-scaffold)
  - by retroactive retrofit script (batch)
  - as a pre-commit check

Each check returns zero or more Findings. A Finding is a Tier-A/B/C rubric failure
with a concrete pointer (file, line, snippet) so downstream steps can repair.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class Finding:
    rubric: str                     # rubric name from rubrics.RUBRICS
    tier: str                       # A / B / C
    severity: str                   # fail | warn
    path: str                       # file path (relative to task_dir) or "" if manifest-wide
    line: int                       # 0 if not line-specific
    snippet: str                    # offending text (trimmed)
    detail: str                     # human message

    def __str__(self) -> str:
        loc = f"{self.path}:{self.line}" if self.line else self.path or "<task>"
        return f"[{self.tier}] {self.rubric} @ {loc}: {self.detail}"


# ═════════════════════════════ Dockerfile checks ══════════════════════════════

_LATEST_TAG_RE = re.compile(r"^\s*FROM\s+(\S+?):latest(\s|$)", re.MULTILINE | re.IGNORECASE)
_UNTAGGED_FROM_RE = re.compile(r"^\s*FROM\s+([a-z0-9./-]+)(?:\s|$)", re.MULTILINE | re.IGNORECASE)
# pip install where no token has == or @ or a local path
_PIP_INSTALL_RE = re.compile(
    r"(?:^|\s|&&|\|\|)\s*(?:python\d?\s+-m\s+)?pip\d?\s+install\s+([^\n&|;]+)",
    re.IGNORECASE,
)
_COPY_DANGEROUS_RE = re.compile(
    r"^\s*COPY\s+(?:--\S+\s+)*(?:\./?)?(solution|tests)(?:/|\b)",
    re.MULTILINE | re.IGNORECASE,
)
_CURL_PIPE_BASH_RE = re.compile(r"curl\s+[^|\n]*\|\s*(?:sudo\s+)?(?:ba|z|)sh", re.IGNORECASE)


def lint_dockerfile(task_dir: Path) -> list[Finding]:
    df = task_dir / "environment" / "Dockerfile"
    if not df.exists():
        return []
    text = df.read_text(errors="ignore")
    findings: list[Finding] = []

    # dockerfile_determinism: :latest tag
    for m in _LATEST_TAG_RE.finditer(text):
        line = text[: m.start()].count("\n") + 1
        findings.append(Finding(
            rubric="dockerfile_determinism", tier="B", severity="fail",
            path="environment/Dockerfile", line=line,
            snippet=m.group(0).strip(),
            detail=f"`:latest` tag on base image `{m.group(1)}` — pin to exact version",
        ))

    # dockerfile_determinism: untagged FROM (no colon = default latest)
    for m in _UNTAGGED_FROM_RE.finditer(text):
        image = m.group(1)
        if ":" in image or image.lower() == "scratch":
            continue
        line = text[: m.start()].count("\n") + 1
        findings.append(Finding(
            rubric="dockerfile_determinism", tier="B", severity="fail",
            path="environment/Dockerfile", line=line,
            snippet=m.group(0).strip(),
            detail=f"untagged FROM `{image}` pulls :latest implicitly",
        ))

    # no_hidden_solution_artifacts / tests_or_solution_in_image
    for m in _COPY_DANGEROUS_RE.finditer(text):
        line = text[: m.start()].count("\n") + 1
        target = m.group(1).lower()
        findings.append(Finding(
            rubric="no_hidden_solution_artifacts" if target == "solution" else "tests_or_solution_in_image",
            tier="A" if target == "solution" else "C",
            severity="fail",
            path="environment/Dockerfile", line=line,
            snippet=m.group(0).strip(),
            detail=f"COPY {target}/ leaks {target} into image — harness mounts externally",
        ))

    # dockerfile_determinism: curl|bash
    for m in _CURL_PIPE_BASH_RE.finditer(text):
        line = text[: m.start()].count("\n") + 1
        findings.append(Finding(
            rubric="dockerfile_determinism", tier="B", severity="warn",
            path="environment/Dockerfile", line=line,
            snippet=m.group(0).strip()[:80],
            detail="curl|bash pulls moving-target script — pin script SHA or inline",
        ))

    # pinned_dependencies: pip install without ==
    for m in _PIP_INSTALL_RE.finditer(text):
        args = m.group(1).strip()
        # Drop flags and continuations
        tokens = [t for t in re.split(r"\s+", args) if t and not t.startswith("-") and t != "\\"]
        # Skip if it's a file install (-r requirements.txt or local path)
        if any(t.startswith(("/", ".", "-r", "@", "git+")) or t.endswith((".txt", ".whl")) for t in tokens):
            continue
        unpinned = [t for t in tokens if "==" not in t and "@" not in t]
        if unpinned:
            line = text[: m.start()].count("\n") + 1
            findings.append(Finding(
                rubric="pinned_dependencies", tier="B", severity="fail",
                path="environment/Dockerfile", line=line,
                snippet=f"pip install {args}"[:100],
                detail=f"unpinned pip deps: {', '.join(unpinned[:5])}",
            ))
    return findings


# ═════════════════════════════ test.sh checks ═════════════════════════════════

_NETWORK_AT_TEST_RE = re.compile(
    r"(?:^|\s|&&|\|\|)\s*"
    r"(pip\s+install|apt(?:-get)?\s+install|npm\s+install|yarn\s+add|"
    r"pnpm\s+(?:add|install)|curl\s+(?!-I\b)|wget\s+|go\s+(?:get|mod\s+download)|"
    r"cargo\s+(?:fetch|install))",
    re.IGNORECASE,
)

# Template pytest-bootstrap guard: `if ! python3 -c "import pytest"` … `fi`
# Network installs inside this guard are the standardized harness pattern —
# they only run when pytest is missing on the base image (node/rust slims),
# which is the harness's responsibility, not the task's.
_PYTEST_BOOTSTRAP_GUARD_RE = re.compile(
    r"if\s+!\s*python3?\s+-c\s+['\"]import\s+pytest['\"][^\n]*\n"
    r"(?:.*?\n)*?"
    r"fi\b",
    re.DOTALL | re.IGNORECASE,
)


def _find_bootstrap_line_range(text: str) -> set[int]:
    """Return 1-indexed line numbers inside a pytest-bootstrap guard block."""
    skip: set[int] = set()
    for m in _PYTEST_BOOTSTRAP_GUARD_RE.finditer(text):
        start_line = text[: m.start()].count("\n") + 1
        end_line = text[: m.end()].count("\n") + 1
        skip.update(range(start_line, end_line + 1))
    return skip


def lint_test_sh(task_dir: Path) -> list[Finding]:
    ts = task_dir / "tests" / "test.sh"
    if not ts.exists():
        return []
    text = ts.read_text(errors="ignore")
    findings: list[Finding] = []
    skip_lines = _find_bootstrap_line_range(text)

    for i, line_text in enumerate(text.splitlines(), start=1):
        if i in skip_lines:
            continue
        stripped = line_text.strip()
        if stripped.startswith("#") or not stripped:
            continue
        for m in _NETWORK_AT_TEST_RE.finditer(line_text):
            findings.append(Finding(
                rubric="no_network_during_tests", tier="B", severity="fail",
                path="tests/test.sh", line=i,
                snippet=line_text.strip()[:100],
                detail=f"network call at test time: `{m.group(1).strip()}`",
            ))

    # ─── reward_is_pure_pytest (Change 1) ───────────────────────────────────
    # The reward MUST be pytest's exit code, written to /logs/verifier/reward.txt,
    # with value literally "0" or "1". Anything else — grep gates, early exits,
    # wrong path, wrong format — makes the oracle unreliable.
    findings.extend(_lint_reward_computation(text))

    return findings


# Wrong reward-file paths or formats (must be /logs/verifier/reward.txt with "0"/"1")
_REWARD_WRONG_PATH_RE = re.compile(
    r"/logs/verifier/reward(?!\.txt\b)(?:\.json|\.yaml|\.yml|\b)",
)
# Grep/awk/sed deciding reward based on pytest output text
_REWARD_GREP_GATE_RE = re.compile(
    r"(?:pytest|python\s+-m\s+pytest|python3?\s+-m\s+pytest)[^\n|]*\|[^\n]*"
    r"(?:grep|awk|sed|egrep|fgrep)\b",
    re.IGNORECASE,
)
# Silent-failure pip/apt install on critical deps (|| true catches pip ENOTFOUND etc.)
_SILENT_INSTALL_RE = re.compile(
    r"(?:pip\d?\s+install|apt(?:-get)?\s+install|npm\s+install)[^\n]*\|\|\s*true\b",
    re.IGNORECASE,
)
# Reward written with JSON-ish content ({reward: 1.0}, {"reward": 1})
_REWARD_JSON_VALUE_RE = re.compile(
    r"echo\s+['\"]\s*\{[^}\n]*(?:reward|status)[^}\n]*\}",
    re.IGNORECASE,
)
# Early `exit` that could terminate before the judge block runs.
# Allowed: `exit 0` / `exit 1` at the very end (last non-blank/non-comment line).
_EXIT_STMT_RE = re.compile(r"^\s*exit\s+(?:\$\?|\$exit_code|\$\{[^}]+\}|\d+|\$\w+)\s*$",
                           re.MULTILINE)


def _lint_reward_computation(text: str) -> list[Finding]:
    """Enforce reward_is_pure_pytest rubric (2026-04-24 Change 1)."""
    out: list[Finding] = []

    # 1. Wrong reward-file path or missing .txt
    for m in _REWARD_WRONG_PATH_RE.finditer(text):
        # Only flag if this is actually on a write line (echo/cat/tee into the path)
        line_start = text.rfind("\n", 0, m.start()) + 1
        line_end = text.find("\n", m.end())
        line = text[line_start:line_end if line_end != -1 else len(text)]
        if any(tok in line for tok in ("echo ", "cat ", "tee ", "printf ", "cp ", "> ")):
            ln = text[: m.start()].count("\n") + 1
            out.append(Finding(
                rubric="reward_is_pure_pytest", tier="A", severity="fail",
                path="tests/test.sh", line=ln, snippet=line.strip()[:120],
                detail="reward written to non-canonical path — Harbor only reads /logs/verifier/reward.txt",
            ))
            break  # one hit is enough

    # 2. Grep/awk/sed gate on pytest output that decides reward
    m = _REWARD_GREP_GATE_RE.search(text)
    if m:
        ln = text[: m.start()].count("\n") + 1
        out.append(Finding(
            rubric="reward_is_pure_pytest", tier="A", severity="fail",
            path="tests/test.sh", line=ln, snippet=m.group(0)[:120],
            detail="pytest output piped to grep/awk/sed — reward must come from pytest exit code, not output text",
        ))

    # 3. Reward echoed as JSON (should be literal "0" or "1")
    m = _REWARD_JSON_VALUE_RE.search(text)
    if m:
        ln = text[: m.start()].count("\n") + 1
        out.append(Finding(
            rubric="reward_is_pure_pytest", tier="A", severity="fail",
            path="tests/test.sh", line=ln, snippet=m.group(0)[:120],
            detail='reward must be literal "0" or "1", not a JSON object',
        ))

    # 4. `|| true` on install of pytest/plugin/core deps — silent failure
    for m in _SILENT_INSTALL_RE.finditer(text):
        ln = text[: m.start()].count("\n") + 1
        snippet = m.group(0).lower()
        # Allow `|| true` on OPTIONAL deps (pyyaml for judge). Flag on pytest + plugins.
        if any(dep in snippet for dep in ("pytest", "pytest-json-ctrf", "pytest-json-report")):
            out.append(Finding(
                rubric="reward_is_pure_pytest", tier="A", severity="fail",
                path="tests/test.sh", line=ln, snippet=m.group(0)[:120],
                detail="critical pytest/plugin install with `|| true` — silent dep failure makes reward unreliable",
            ))

    # 5. Early `exit` that prevents judge block from running.
    # Find all exit statements. Find the line where the judge block starts
    # ("--- LLM Judge ---" or "standalone_judge.py" first appears). If any
    # `exit` appears BEFORE that line, it short-circuits the judge.
    judge_marker = text.find("LLM Judge")
    if judge_marker < 0:
        judge_marker = text.find("standalone_judge.py")
    if judge_marker > 0:
        judge_line = text[:judge_marker].count("\n") + 1
        for m in _EXIT_STMT_RE.finditer(text):
            ln = text[: m.start()].count("\n") + 1
            if ln < judge_line:
                out.append(Finding(
                    rubric="reward_is_pure_pytest", tier="A", severity="fail",
                    path="tests/test.sh", line=ln, snippet=m.group(0).strip()[:100],
                    detail=(
                        f"`exit` at line {ln} terminates script before LLM judge "
                        f"block at line {judge_line} — judge never runs"
                    ),
                ))
                break
    return out


# ═════════════════════════════ test_outputs.py checks ═════════════════════════

_TEST_DEF_RE = re.compile(r"^([ \t]*)def\s+(test_\w+)\s*\(", re.MULTILINE)
_SUBPROCESS_OR_IMPORT_CALL_RE = re.compile(
    r"(subprocess\.|Popen\(|importlib|__import__|\.check_output|\.Popen|"
    r"docker\s|exec\s*\(|\bimport\s+\w+\s*(?:;|\n)|pytest\.|from\s+\w+\s+import)",
)
_OPEN_READ_ONLY_RE = re.compile(r"open\([^)]+\)\.read\(\)")

# Tautological assert patterns (each MIGHT be a guard before a real test;
# we only flag when a test function contains ONLY these and no other asserts).
_TAUTOLOGICAL_PATTERNS = [
    re.compile(r"assert\s+\S+\s+is\s+not\s+None\b", re.IGNORECASE),
    re.compile(r"assert\s+[a-z_][\w\.]*\s*(?:,|$|#)", re.IGNORECASE | re.MULTILINE),  # bare `assert x`
    re.compile(r"assert\s+len\s*\([^)]+\)\s*>=?\s*0\b"),                   # len >= 0 always
    re.compile(r"assert\s+isinstance\s*\([^)]+\)\s*(?:,|$|#)", re.MULTILINE),
    re.compile(r"assert\s+\S+\s+is\s+True\s*(?:,|$|#)", re.MULTILINE),
    # `assert x > 0` with x bound to len() or count() — only trivially non-empty
    re.compile(r"assert\s+len\s*\([^)]+\)\s*>\s*0\b"),
]
_ANY_ASSERT_RE = re.compile(r"^\s*assert\s+", re.MULTILINE)


def _iter_test_functions(text: str) -> Iterable[tuple[str, int, str]]:
    """Yield (name, start_line, body) for each `def test_*` in text.

    Uses ast to correctly handle multiline strings, HEREDOCs, nested defs.
    Falls back to regex-based span if AST fails (e.g., syntax error).
    """
    import ast
    try:
        tree = ast.parse(text)
    except SyntaxError:
        # Fallback: yield nothing rather than crash
        return
    lines = text.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            start = node.lineno
            end = node.end_lineno or start
            # ast line numbers are 1-indexed; lines list is 0-indexed
            body_lines = lines[start - 1: end]
            yield node.name, start, "\n".join(body_lines)


def lint_test_outputs(task_dir: Path) -> list[Finding]:
    tp = task_dir / "tests" / "test_outputs.py"
    if not tp.exists():
        return []
    text = tp.read_text(errors="ignore")
    findings: list[Finding] = []

    for name, body_line, body in _iter_test_functions(text):
        has_execution = bool(_SUBPROCESS_OR_IMPORT_CALL_RE.search(body))
        has_open_read = bool(_OPEN_READ_ONLY_RE.search(body))
        if has_open_read and not has_execution:
            findings.append(Finding(
                rubric="tests_verify_behavior_not_text", tier="A", severity="fail",
                path="tests/test_outputs.py", line=body_line,
                snippet=f"def {name}(...) — open().read() with no execution",
                detail=f"test `{name}` only reads file text; invoke the API or run subprocess",
            ))

        # Tautological: flag ONLY when EVERY assert in this function is tautological.
        assert_stmts = [
            m.group(0) for m in re.finditer(r"^\s*assert\s+[^\n]+", body, re.MULTILINE)
        ]
        if not assert_stmts:
            continue
        taut_count = sum(
            1 for stmt in assert_stmts
            if any(pat.search(stmt) for pat in _TAUTOLOGICAL_PATTERNS)
        )
        if taut_count == len(assert_stmts):
            findings.append(Finding(
                rubric="test_not_tautological", tier="A", severity="fail",
                path="tests/test_outputs.py", line=body_line,
                snippet=f"def {name}(...) — {taut_count} asserts, all tautological",
                detail=(f"test `{name}` has {taut_count} assert(s), all pass on a stub "
                        f"impl (is not None / isinstance / len>0 / bare assert)"),
            ))

    return findings


# ═════════════════════════════ manifest-level checks ══════════════════════════

def lint_manifest(task_dir: Path) -> list[Finding]:
    mp = task_dir / "eval_manifest.yaml"
    if not yaml or not mp.exists():
        return []
    try:
        m = yaml.safe_load(mp.read_text()) or {}
    except Exception as e:
        return [Finding(
            rubric="f2p_p2p_classification_correct", tier="B", severity="fail",
            path="eval_manifest.yaml", line=0,
            snippet=str(e)[:80],
            detail=f"yaml parse error: {e}",
        )]

    if not isinstance(m, dict):
        return [Finding(
            rubric="f2p_p2p_classification_correct", tier="B", severity="fail",
            path="eval_manifest.yaml", line=0, snippet=str(type(m).__name__),
            detail=f"eval_manifest.yaml parses as {type(m).__name__}, expected dict",
        )]
    checks = m.get("checks", []) or []
    f2p = [c for c in checks if c.get("type") == "fail_to_pass"]
    p2p = [c for c in checks if c.get("type") == "pass_to_pass"]

    findings: list[Finding] = []
    if not p2p:
        findings.append(Finding(
            rubric="pass_to_pass_coverage", tier="A", severity="fail",
            path="eval_manifest.yaml", line=0,
            snippet=f"{len(checks)} checks, 0 pass_to_pass",
            detail="no p2p regression guards — agent can delete failing code path and 'win'",
        ))
    if len(f2p) < 2:
        findings.append(Finding(
            rubric="f2p_p2p_classification_correct", tier="B", severity="warn",
            path="eval_manifest.yaml", line=0,
            snippet=f"{len(f2p)} f2p",
            detail="<2 fail_to_pass checks — single-point reward is fragile",
        ))
    return findings


# ══════════════════════ Solve.sh / oracle integrity checks ════════════════════

# Fetches gold from external source — lets the agent game the oracle.
_ORACLE_EXTERNAL_FETCH_RES = {
    "curl_gh_diff":    re.compile(r"curl[^\n]*github\.com[^\n]*\.diff", re.IGNORECASE),
    "curl_gh_patch":   re.compile(r"curl[^\n]*github\.com[^\n]*\.patch", re.IGNORECASE),
    "git_show_sha":    re.compile(r"\bgit\s+show\s+[a-f0-9]{7,}", re.IGNORECASE),
    "gh_pr_diff":      re.compile(r"\bgh\s+pr\s+diff\b", re.IGNORECASE),
    "wget_github":     re.compile(r"wget[^\n]*github\.com", re.IGNORECASE),
    "git_fetch_pr":    re.compile(r"git\s+fetch\s[^\n]*pull/\d+", re.IGNORECASE),
    "git_apply_url":   re.compile(r"git\s+apply[^\n]*https?://", re.IGNORECASE),
}

# Heuristic: docs-only files. Patch touching only these is trivial.
_DOCS_ONLY_SUFFIXES = (
    ".md", ".mdx", ".txt", ".rst",
)
_DOCS_ONLY_BASENAMES = (
    "CHANGELOG", "CHANGES", "HISTORY", "NOTES", "README", "CLAUDE", "AGENTS",
    "CONTRIBUTING", "LICENSE", "NOTICE", "AUTHORS",
)

_PATCH_FILE_RE = re.compile(r"^(?:---|\+\+\+)\s+[ab]/([^\s\n]+)", re.MULTILINE)
_PATCH_ADD_RE  = re.compile(r"^\+(?!\+\+).*$", re.MULTILINE)


def _docs_only(path: str) -> bool:
    """True if this path is documentation/config, not runtime code."""
    # Strip to basename
    base = path.rsplit("/", 1)[-1]
    stem = base.split(".")[0].upper()
    return any(path.lower().endswith(s) for s in _DOCS_ONLY_SUFFIXES) \
        or stem in _DOCS_ONLY_BASENAMES


def lint_solve_sh(task_dir: Path) -> list[Finding]:
    """Check solve.sh for broken-oracle + trivial-gold patterns."""
    sv = task_dir / "solution" / "solve.sh"
    if not sv.exists():
        return []
    text = sv.read_text(errors="ignore")
    findings: list[Finding] = []

    # oracle_no_external_fetch — hard Tier-A fail
    for tag, pat in _ORACLE_EXTERNAL_FETCH_RES.items():
        m = pat.search(text)
        if m:
            line = text[: m.start()].count("\n") + 1
            findings.append(Finding(
                rubric="oracle_no_external_fetch", tier="A", severity="fail",
                path="solution/solve.sh", line=line,
                snippet=m.group(0)[:120],
                detail=f"solve.sh fetches gold via `{tag}` — agent can game the oracle",
            ))
            break  # one hit is enough

    # gold_diff_non_trivial — count added lines and touched files (from embedded patch heredoc)
    files = _PATCH_FILE_RE.findall(text)
    adds = _PATCH_ADD_RE.findall(text)
    # Filter out the diff's own '+++' line noise (already excluded by lookahead)
    # and whitespace-only additions
    nonblank_adds = [a for a in adds if a[1:].strip()]
    unique_files = sorted(set(files))
    code_files = [f for f in unique_files if not _docs_only(f)]
    if unique_files and len(nonblank_adds) < 15 and not code_files:
        findings.append(Finding(
            rubric="gold_diff_non_trivial", tier="A", severity="fail",
            path="solution/solve.sh", line=0,
            snippet=", ".join(unique_files[:3]),
            detail=(
                f"gold patch is trivial: {len(nonblank_adds)} non-blank added lines "
                f"across {len(unique_files)} docs-only file(s) — no code differentiation"
            ),
        ))
    elif unique_files and len(nonblank_adds) < 4:
        # Strong signal regardless of file type
        findings.append(Finding(
            rubric="gold_diff_non_trivial", tier="A", severity="fail",
            path="solution/solve.sh", line=0,
            snippet=", ".join(unique_files[:3]),
            detail=f"gold patch adds only {len(nonblank_adds)} non-blank lines",
        ))
    return findings


def lint_instruction_leakage(task_dir: Path) -> list[Finding]:
    """Check instruction.md for direct naming of gold-patch target files."""
    instr = task_dir / "instruction.md"
    sv = task_dir / "solution" / "solve.sh"
    if not (instr.exists() and sv.exists()):
        return []
    itxt = instr.read_text(errors="ignore")
    stxt = sv.read_text(errors="ignore")
    # Extract paths modified by the gold diff
    files = sorted({f for f in _PATCH_FILE_RE.findall(stxt)})
    findings: list[Finding] = []
    hits: list[str] = []
    for f in files:
        # Only flag for "real" code paths; skip README-style leakage
        if _docs_only(f):
            continue
        # Match full path OR the basename if path has ≥2 segments (very specific)
        if f in itxt:
            hits.append(f)
        else:
            parts = f.split("/")
            if len(parts) >= 2 and parts[-1] in itxt and "/" in parts[-1] in itxt:
                hits.append(parts[-1])
    if hits:
        # Always warn (not fail): ~54% of the corpus names gold-diff paths in
        # narrative (e.g. "The file foo.py contains the Bar class"). This is
        # endemic and often legitimate context-setting. Treat as a signal for
        # filtering clean eval samples, not a hard quarantine trigger. New
        # scaffolded tasks should avoid this via prompt guardrails instead.
        code_files_in_diff = [
            f for f in _PATCH_FILE_RE.findall(stxt) if not _docs_only(f)
        ]
        total_code = len(set(code_files_in_diff))
        findings.append(Finding(
            rubric="instruction_no_path_leak", tier="A", severity="warn",
            path="instruction.md", line=0,
            snippet=", ".join(hits[:3]),
            detail=(
                f"instruction.md names {len(hits)}/{total_code} gold-diff code file(s): "
                f"{hits[:3]} — localization partially spoiled"
            ),
        ))
    return findings


# ══════════════════════ tests_have_subprocess gate ═══════════════════════════

_SUBPROCESS_CALL_RE = re.compile(
    r"\b(?:subprocess\.run|subprocess\.check_output|subprocess\.Popen|"
    r"os\.system|os\.popen|pexpect\.spawn)\s*\(",
)


# ══════════════════════ test_deps_in_dockerfile (Change 2A) ═════════════════

# Binaries we can safely assume are on any Linux base image + common
# python/js/go/rust CI runtimes. Not flagged when tests call these.
_BUILTIN_BINARIES = frozenset({
    "bash", "sh", "dash", "zsh",
    "python", "python3", "pip", "pip3", "pipx",
    "true", "false", ":",
    "echo", "printf", "cat", "head", "tail", "tee", "sort", "uniq",
    "grep", "egrep", "fgrep", "rg", "sed", "awk", "tr", "cut", "wc",
    "find", "xargs", "ls", "pwd", "cd", "mkdir", "rm", "cp", "mv",
    "ln", "chmod", "chown", "touch", "stat", "file", "which", "command",
    "git", "curl", "wget",
    "tar", "gzip", "gunzip", "unzip", "zip",
    "env", "test", "diff", "tput",
    "jq", "yq",
})

# Extract the first arg of each subprocess.run / check_output / Popen /
# os.system call from test_outputs.py. We only parse the literal list form
# subprocess.run(["cargo", ...]) — string form `os.system("cargo build")`
# handled by separate regex.
_SUBPROC_LIST_BIN_RE = re.compile(
    r"""subprocess\.(?:run|check_output|Popen|call|check_call)
        \s*\(\s*\[\s*["']([^"']+)["']""",
    re.VERBOSE,
)
_SUBPROC_STRING_BIN_RE = re.compile(
    r"""os\.(?:system|popen)\s*\(\s*["']\s*([a-zA-Z_][a-zA-Z0-9_-]*)""",
)


def _extract_test_binaries(tests_text: str) -> set[str]:
    """Return set of binary names tests invoke (excluding builtins)."""
    found: set[str] = set()
    for m in _SUBPROC_LIST_BIN_RE.finditer(tests_text):
        found.add(m.group(1))
    for m in _SUBPROC_STRING_BIN_RE.finditer(tests_text):
        found.add(m.group(1))
    return {b for b in found if b and b not in _BUILTIN_BINARIES}


# Base-image implicit binaries: if Dockerfile does `FROM <key>`, the image
# ships with these binaries pre-installed. Keys match via `startswith`.
_BASE_IMAGE_TOOLS: dict[str, tuple[str, ...]] = {
    "node":       ("node", "npm", "npx", "yarn", "pnpm"),
    "oven/bun":   ("bun", "node", "npm", "npx"),
    "python":     ("python", "python3", "pip", "pip3"),
    "rust":       ("cargo", "rustc", "rustup", "rustfmt", "clippy"),
    "golang":     ("go", "gofmt"),
    "go":         ("go", "gofmt"),
    "ruby":       ("ruby", "gem", "bundle"),
    "openjdk":    ("java", "javac"),
    "ghcr.io/astral-sh/uv": ("uv", "uvx"),
    "mcr.microsoft.com/dotnet/sdk": ("dotnet",),
    "denoland/deno": ("deno",),
}


def _implicit_base_tools(df_text: str) -> set[str]:
    """Return tools implicitly provided by the Dockerfile's base image."""
    tools: set[str] = set()
    for line in df_text.splitlines():
        line = line.strip()
        if not line.upper().startswith("FROM "):
            continue
        image_part = line[5:].strip().split()[0].lower()
        for key, binaries in _BASE_IMAGE_TOOLS.items():
            if image_part.startswith(key.lower()):
                tools.update(binaries)
    return tools


def lint_test_deps_in_dockerfile(task_dir: Path) -> list[Finding]:
    """Change 2A: every tool tests invoke via subprocess must appear in Dockerfile."""
    tp = task_dir / "tests" / "test_outputs.py"
    df = task_dir / "environment" / "Dockerfile"
    if not (tp.exists() and df.exists()):
        return []
    tools = _extract_test_binaries(tp.read_text(errors="ignore"))
    if not tools:
        return []
    df_text_raw = df.read_text(errors="ignore")
    df_text = df_text_raw.lower()
    implicit = _implicit_base_tools(df_text_raw)
    missing: list[str] = []
    for tool in sorted(tools):
        # Base image implicitly includes this (e.g., FROM node:* → npx)
        if tool in implicit:
            continue
        # Match as whole word anywhere in Dockerfile (RUN, FROM, COPY, etc.)
        if re.search(rf"\b{re.escape(tool.lower())}\b", df_text):
            continue
        # Also accept `FROM <tool>:...` (base image named after the tool)
        if re.search(rf"^\s*FROM\s+{re.escape(tool.lower())}[:/\s]",
                     df_text, re.MULTILINE):
            continue
        missing.append(tool)
    if not missing:
        return []
    return [Finding(
        rubric="test_deps_in_dockerfile", tier="A", severity="fail",
        path="environment/Dockerfile", line=0,
        snippet=", ".join(missing[:5]),
        detail=(
            f"tests call {len(missing)} binar{'y' if len(missing)==1 else 'ies'} "
            f"not installed in Dockerfile: {missing[:5]}"
        ),
    )]


# ══════════════════════ substring_assertions_are_instructed (Change 3) ══════

# Match `assert "LITERAL" in something`, `assert '...' in something`,
# `assert "LITERAL" not in something`, and the reverse `assert x in "literal"`.
# Case-insensitive pattern; we extract the literal side.
_ASSERT_STR_IN_RE = re.compile(
    r"""\bassert\s+
        (?:
            (?P<q1>["'])(?P<lit1>[^"'\n]{6,})(?P=q1)\s+
            (?:not\s+)?in\s+\w+
        |
            \w+\s+(?:not\s+)?in\s+
            (?P<q2>["'])(?P<lit2>[^"'\n]{6,})(?P=q2)
        )""",
    re.VERBOSE,
)


def lint_substring_assertions_instructed(task_dir: Path) -> list[Finding]:
    """Change 3: literal strings in `assert "X" in output` must appear in instruction.md."""
    tp = task_dir / "tests" / "test_outputs.py"
    ip = task_dir / "instruction.md"
    if not (tp.exists() and ip.exists()):
        return []
    tests_text = tp.read_text(errors="ignore")
    instr_text = ip.read_text(errors="ignore")

    literals: set[str] = set()
    for m in _ASSERT_STR_IN_RE.finditer(tests_text):
        lit = m.group("lit1") or m.group("lit2") or ""
        lit = lit.strip()
        # Filter:
        # - must contain whitespace (indicates it's prose, not an identifier)
        # - ≥6 chars already enforced by regex
        # - not a common short string / symbol-like
        if not lit or " " not in lit:
            continue
        if lit.startswith("/") or lit.startswith("--"):  # path / flag — noise
            continue
        literals.add(lit)

    missing = [lit for lit in literals if lit not in instr_text]
    if not missing:
        return []
    return [Finding(
        rubric="substring_assertions_are_instructed", tier="A", severity="warn",
        path="tests/test_outputs.py", line=0,
        snippet=missing[0][:80],
        detail=(
            f"{len(missing)} test literal(s) not in instruction.md: "
            f"{[l[:40] for l in missing[:3]]} — agent may produce equivalent "
            f"wording that test rejects"
        ),
    )]


# ══════════════════════ lint_requirement_stated (Change 5) ═══════════════════

# Linters + formatters that agents must satisfy. Match both binary-invocation
# and subprocess-argv-list patterns.
_LINT_TOOLS = {
    "ruff":      re.compile(r"\bruff\b(?:\s*,|\s+(?:check|format|--))"),
    "black":     re.compile(r"\bblack\b(?:\s*,|\s+(?:--|[\w/.]))"),
    "prettier":  re.compile(r"\bprettier\b"),
    "eslint":    re.compile(r"\beslint\b"),
    "stylelint": re.compile(r"\bstylelint\b"),
    "clippy":    re.compile(r"cargo\s+clippy\b|\bclippy\b"),
    "cargo_fmt": re.compile(r"cargo\s+fmt\b|\brustfmt\b"),
    "gofmt":     re.compile(r"\bgofmt\b"),
    "golangci":  re.compile(r"\bgolangci-?lint\b"),
    "mypy":      re.compile(r"\bmypy\b"),
    "pyright":   re.compile(r"\bpyright\b"),
    "pylint":    re.compile(r"\bpylint\b"),
    "typos":     re.compile(r"\btypos\b"),
}


def lint_lint_requirement_stated(task_dir: Path) -> list[Finding]:
    """Change 5: if tests use linters, instruction must say so."""
    tp = task_dir / "tests" / "test_outputs.py"
    ip = task_dir / "instruction.md"
    if not (tp.exists() and ip.exists()):
        return []
    tests_text = tp.read_text(errors="ignore")
    instr_text = ip.read_text(errors="ignore").lower()
    used: list[str] = []
    for tool, pat in _LINT_TOOLS.items():
        if pat.search(tests_text):
            # Instruction should mention this tool by name
            name = tool.replace("_", " ")
            if name.lower() not in instr_text and tool.lower() not in instr_text:
                used.append(tool)
    if not used:
        return []
    return [Finding(
        rubric="lint_requirement_stated", tier="B", severity="warn",
        path="instruction.md", line=0,
        snippet=", ".join(used[:5]),
        detail=(
            f"tests invoke {len(used)} linter(s)/formatter(s) not mentioned "
            f"in instruction: {used[:5]} — agents won't know style is graded"
        ),
    )]


# ══════════════════════ Post-validation pytest-pass check ════════════════════

def check_all_gold_tests_passed(ctrf_path: Path) -> list[Finding]:
    """Post-validation gate (Change 4): every individual pytest test in the
    gold run must PASS. Reads a CTRF JSON file (what `pytest --ctrf <path>`
    emits) and returns a Finding per failed test.

    Call this from e2b_worker.node_validate_and_fix AFTER the gold trial
    completes, passing the path to that trial's /logs/verifier/ctrf.json.

    Scaffold-time: if any test failed in the gold run, the task is broken
    (test has a bug, or gold doesn't cover what the test demands) — quarantine.

    Returns empty list if ctrf.json is missing or all tests passed.
    """
    if not ctrf_path.exists():
        return []
    try:
        data = json.loads(ctrf_path.read_text())
    except Exception:
        return []
    # CTRF schema: results.tests = [{"name": ..., "status": "passed"|"failed"|"skipped", ...}]
    tests = (data.get("results") or {}).get("tests") or []
    out: list[Finding] = []
    for t in tests:
        if t.get("status") == "failed":
            out.append(Finding(
                rubric="every_gold_test_passes", tier="A", severity="fail",
                path="tests/test_outputs.py", line=0,
                snippet=t.get("name", "<unknown>")[:100],
                detail=(
                    f"gold solve produced FAILED test `{t.get('name')}` — "
                    f"either the test has a bug (wrong invocation, brittle "
                    f"assertion) or gold doesn't cover what the test demands"
                ),
            ))
    return out


def lint_tests_subprocess(task_dir: Path) -> list[Finding]:
    """Require at least one genuine subprocess invocation in test_outputs.py."""
    tp = task_dir / "tests" / "test_outputs.py"
    if not tp.exists():
        return []
    text = tp.read_text(errors="ignore")
    if _SUBPROCESS_CALL_RE.search(text):
        return []
    return [Finding(
        rubric="tests_have_subprocess", tier="A", severity="fail",
        path="tests/test_outputs.py", line=0, snippet="",
        detail=(
            "no subprocess.run/check_output/Popen/os.system — tests cannot execute "
            "the fixed code; grep-only tests don't verify behavior"
        ),
    )]


# ═════════════════════════════ Orchestrator ══════════════════════════════════

def lint_task(task_dir: Path) -> list[Finding]:
    """Run all programmatic checks on a task. Returns all findings sorted by tier."""
    findings: list[Finding] = []
    findings.extend(lint_dockerfile(task_dir))
    findings.extend(lint_test_sh(task_dir))
    findings.extend(lint_test_outputs(task_dir))
    findings.extend(lint_manifest(task_dir))
    findings.extend(lint_solve_sh(task_dir))
    findings.extend(lint_instruction_leakage(task_dir))
    findings.extend(lint_tests_subprocess(task_dir))
    findings.extend(lint_test_deps_in_dockerfile(task_dir))
    findings.extend(lint_substring_assertions_instructed(task_dir))
    findings.extend(lint_lint_requirement_stated(task_dir))
    # Dedupe: drop repeated findings at same (path, line, rubric, detail) — common
    # when Dockerfile has `pip install X || pip install X` fallback pattern
    seen: set[tuple[str, int, str, str]] = set()
    uniq: list[Finding] = []
    for f in findings:
        key = (f.path, f.line, f.rubric, f.detail)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(f)
    # Sort: Tier A first, then by path
    uniq.sort(key=lambda f: (f.tier, f.severity == "warn", f.path, f.line))
    return uniq


def summarize(findings: Iterable[Finding]) -> dict:
    """Group findings by tier + severity for a compact JSON summary."""
    by_tier = {"A": 0, "B": 0, "C": 0}
    by_rubric: dict[str, int] = {}
    fails = 0
    warns = 0
    for f in findings:
        by_tier[f.tier] = by_tier.get(f.tier, 0) + 1
        by_rubric[f.rubric] = by_rubric.get(f.rubric, 0) + 1
        if f.severity == "fail":
            fails += 1
        else:
            warns += 1
    return {
        "total": fails + warns,
        "fails": fails,
        "warns": warns,
        "by_tier": by_tier,
        "by_rubric": by_rubric,
        "tier_a_fails": sum(1 for f in findings if f.tier == "A" and f.severity == "fail"),
    }


# ═════════════════════════════ CLI ══════════════════════════════════════════

def _cli():
    import argparse
    import json
    import sys

    p = argparse.ArgumentParser(description="Programmatic task-quality linter.")
    p.add_argument("task_dir", help="Path to a task dir or a markdown_following/ root")
    p.add_argument("--json", action="store_true", help="Output JSON summary")
    p.add_argument("--fail-on", choices=["A", "B", "C", "any"], default="A",
                   help="Exit nonzero if any finding of this tier or higher (default A)")
    args = p.parse_args()

    root = Path(args.task_dir)
    # Detect if this is a single task or a dir-of-tasks
    if (root / "eval_manifest.yaml").exists() or (root / "instruction.md").exists():
        tasks = [root]
    else:
        tasks = sorted(t for t in root.iterdir() if t.is_dir() and (t / "environment").exists())

    all_results = {}
    tier_order = {"A": 3, "B": 2, "C": 1, "any": 0}
    threshold = tier_order[args.fail_on]
    total_hits = 0

    for t in tasks:
        findings = lint_task(t)
        summary = summarize(findings)
        all_results[t.name] = {
            "summary": summary,
            "findings": [str(f) for f in findings],
        }
        # Count findings at or above threshold
        hits = sum(1 for f in findings
                   if tier_order[f.tier] >= threshold and f.severity == "fail")
        total_hits += hits

    if args.json:
        print(json.dumps(all_results, indent=2))
    else:
        for name, r in all_results.items():
            s = r["summary"]
            if s["total"] == 0:
                continue
            print(f"\n── {name} ── ({s['fails']} fails, {s['warns']} warns, "
                  f"tier A: {s['by_tier']['A']})")
            for f in r["findings"]:
                print(f"  {f}")

        # Summary roll-up
        total_tasks = len(tasks)
        clean = sum(1 for r in all_results.values() if r["summary"]["total"] == 0)
        with_a = sum(1 for r in all_results.values() if r["summary"]["tier_a_fails"] > 0)
        print(f"\n═══ {clean}/{total_tasks} clean | {with_a}/{total_tasks} have Tier-A fails ═══")

    sys.exit(1 if total_hits else 0)


if __name__ == "__main__":
    _cli()
