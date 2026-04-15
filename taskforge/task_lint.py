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
    return findings


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


# ═════════════════════════════ Orchestrator ══════════════════════════════════

def lint_task(task_dir: Path) -> list[Finding]:
    """Run all programmatic checks on a task. Returns all findings sorted by tier."""
    findings: list[Finding] = []
    findings.extend(lint_dockerfile(task_dir))
    findings.extend(lint_test_sh(task_dir))
    findings.extend(lint_test_outputs(task_dir))
    findings.extend(lint_manifest(task_dir))
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
    p.add_argument("task_dir", help="Path to a task dir or a harbor_tasks/ root")
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
