#!/usr/bin/env python3
"""Audit p2p / f2p test coverage across `harbor_tasks/`.

For each task, score how well its tests cover real CI/CD behavior:

- **p2p (pass-to-pass)**: tests that should pass on BOTH the base commit and
  the gold patch. Strong p2p tests run the upstream repo's actual CI/CD
  test suite (pytest / vitest / jest / npm test / cargo test / go test).
  Weak p2p tests are invented assertions that don't exercise real behavior.

- **f2p (fail-to-pass)**: tests that fail on base, pass on gold. Strong f2p
  tests call the actual functions modified by the PR with bug-triggering
  inputs and assert correct outputs. Weak f2p tests use AST inspection or
  string/keyword matching against source code.

The audit is purely static — reads `eval_manifest.yaml` and `tests/test_outputs.py`
of each task. No code execution.

Output: a JSONL audit + a markdown summary at `research/test_coverage_audit.md`.

Usage:
    .venv/bin/python scripts/audit_test_coverage.py
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

import yaml

ROOT = Path("/home/alex/agentsmd-rl")
TASK_DIR = ROOT / "harbor_tasks"

# Patterns for "calls real test runner" — strong p2p signal.
REAL_RUNNER_RE = re.compile(
    r"\bsubprocess\.(run|check_call|check_output|Popen)\b.*?"
    r"(pytest|unittest|vitest|jest|mocha|"
    r"npm\s+test|yarn\s+test|pnpm\s+test|"
    r"cargo\s+test|go\s+test|cargo\s+check|"
    r"tsc\s+--noEmit|mypy)",
    re.IGNORECASE | re.DOTALL,
)

# Patterns suggesting structural / weak tests.
STRUCTURAL_RE = re.compile(
    r"\b(ast\.parse|ast\.walk|inspect\.|"
    r"open\(.*?\)\.read\(\).*?in\s|"
    r"['\"][^'\"]+['\"]?\s+in\s+(content|source|text|contents))\b",
    re.IGNORECASE,
)

BEHAVIORAL_RE = re.compile(
    r"\b(assert|assertEqual|assertIs|assertIn|assertGreater|assertRaises|"
    r"raises\s*\(|expect\s*\()",
    re.IGNORECASE,
)


def audit_one(task: Path) -> dict:
    em = task / "eval_manifest.yaml"
    tests = task / "tests" / "test_outputs.py"
    out: dict = {
        "task": task.name,
        "has_manifest": em.is_file(),
        "has_tests_py": tests.is_file(),
    }
    if not em.is_file():
        return out

    try:
        m = yaml.safe_load(em.read_text()) or {}
    except Exception as e:
        out["yaml_error"] = str(e)[:80]
        return out

    checks = m.get("checks") or []
    f2p = [c for c in checks if (c or {}).get("type") == "fail_to_pass"]
    p2p = [c for c in checks if (c or {}).get("type") == "pass_to_pass"]
    out["f2p_declared"] = len(f2p)
    out["p2p_declared"] = len(p2p)

    # Origin breakdown — pr_diff vs repo_tests vs agent_config vs static.
    origins: dict[str, int] = {}
    for c in checks:
        o = (c or {}).get("origin", "unknown")
        origins[o] = origins.get(o, 0) + 1
    out["origins"] = origins

    if not tests.is_file():
        return out

    try:
        src = tests.read_text(errors="replace")
    except Exception as e:
        out["tests_read_error"] = str(e)[:80]
        return out

    # Count def test_* declarations
    test_defs = len(re.findall(r"^\s*def\s+test_\w+\s*\(", src, re.MULTILINE))
    out["test_def_count"] = test_defs

    # Real-runner signal
    real_runners = REAL_RUNNER_RE.findall(src)
    out["calls_real_runner"] = bool(real_runners)
    out["real_runner_kinds"] = sorted({r[1].lower().strip()
                                        for r in real_runners})

    # Structural / behavioral signals
    structural_hits = len(STRUCTURAL_RE.findall(src))
    behavioral_hits = len(BEHAVIORAL_RE.findall(src))
    out["structural_assertion_hits"] = structural_hits
    out["behavioral_assertion_hits"] = behavioral_hits
    # Weak if mostly structural
    if behavioral_hits == 0:
        out["test_quality"] = "no_behavioral_assertions"
    elif structural_hits > behavioral_hits * 2:
        out["test_quality"] = "mostly_structural"
    elif out["calls_real_runner"]:
        out["test_quality"] = "calls_real_runner"
    elif behavioral_hits >= 3:
        out["test_quality"] = "behavioral_only"
    else:
        out["test_quality"] = "minimal"

    # P2P CI/CD signal — does ANY test call a real runner AND have origin repo_tests?
    out["has_real_p2p_ci"] = bool(real_runners) and origins.get("repo_tests", 0) > 0

    # F2P coverage — does each f2p check have a matching test_*?
    f2p_ids = [c.get("id", "") for c in f2p]
    matched = [tid for tid in f2p_ids
               if re.search(r"def\s+test_" + re.escape(tid) + r"\s*\(", src)
               or re.search(r"def\s+test_\w*" + re.escape(tid.split('_')[0]) + r"\w*\s*\(", src, re.IGNORECASE)]
    out["f2p_matched"] = len(matched)
    out["f2p_unmatched"] = max(0, len(f2p_ids) - len(matched))

    return out


def aggregate(rows: list[dict]) -> dict:
    n = len(rows)
    runner_count = sum(1 for r in rows if r.get("calls_real_runner"))
    p2p_ci_count = sum(1 for r in rows if r.get("has_real_p2p_ci"))
    no_behav = sum(1 for r in rows
                   if r.get("test_quality") == "no_behavioral_assertions")
    structural = sum(1 for r in rows
                     if r.get("test_quality") == "mostly_structural")
    minimal = sum(1 for r in rows if r.get("test_quality") == "minimal")
    f2p_unmatched = sum(r.get("f2p_unmatched", 0) for r in rows)
    runner_kinds: dict[str, int] = {}
    for r in rows:
        for k in r.get("real_runner_kinds") or []:
            runner_kinds[k] = runner_kinds.get(k, 0) + 1
    return {
        "total_tasks": n,
        "calls_real_runner": runner_count,
        "calls_real_runner_pct": 100 * runner_count / max(1, n),
        "has_real_p2p_ci": p2p_ci_count,
        "has_real_p2p_ci_pct": 100 * p2p_ci_count / max(1, n),
        "no_behavioral_assertions": no_behav,
        "mostly_structural": structural,
        "minimal_tests": minimal,
        "total_f2p_unmatched": f2p_unmatched,
        "runner_kinds": runner_kinds,
    }


def write_markdown(rows: list[dict], summary: dict, out_path: Path) -> None:
    weakest = [r for r in rows
               if r.get("test_quality") in
               ("no_behavioral_assertions", "mostly_structural", "minimal")
               or r.get("f2p_unmatched", 0) > 0]
    weakest.sort(key=lambda r: (
        0 if r.get("calls_real_runner") else 1,
        -r.get("f2p_unmatched", 0),
        r.get("behavioral_assertion_hits", 0),
    ))

    md = []
    md.append("# Test-coverage audit — `harbor_tasks/`\n")
    md.append("Static audit of each task's `tests/test_outputs.py` and "
              "`eval_manifest.yaml`. Reports whether tests call real CI/CD "
              "test runners (`pytest` / `vitest` / `jest` / `cargo test` / "
              "`go test`) and whether every declared `fail_to_pass` check "
              "has a matching `def test_*` function in the test file.\n")
    md.append(f"## Aggregate ({summary['total_tasks']} tasks)\n")
    md.append("| Metric | Count | % |")
    md.append("|---|---:|---:|")
    md.append(f"| Tasks calling a real test runner via `subprocess.run(...)` | "
              f"{summary['calls_real_runner']} | "
              f"{summary['calls_real_runner_pct']:.1f}% |")
    md.append(f"| Tasks with a real-runner p2p test (`origin: repo_tests`) | "
              f"{summary['has_real_p2p_ci']} | "
              f"{summary['has_real_p2p_ci_pct']:.1f}% |")
    md.append(f"| Tasks with no behavioral assertions | "
              f"{summary['no_behavioral_assertions']} | — |")
    md.append(f"| Tasks dominated by structural / AST inspection | "
              f"{summary['mostly_structural']} | — |")
    md.append(f"| Tasks with minimal tests (≤ 2 assertions) | "
              f"{summary['minimal_tests']} | — |")
    md.append(f"| Total `fail_to_pass` checks declared but not matched in "
              f"test file | {summary['total_f2p_unmatched']} | — |\n")

    if summary['runner_kinds']:
        md.append("### Real-runner mix\n")
        md.append("| Runner | Tasks |")
        md.append("|---|---:|")
        for k, n in sorted(summary['runner_kinds'].items(),
                           key=lambda x: -x[1]):
            md.append(f"| `{k}` | {n} |")
        md.append("")

    md.append(f"## Weakest tasks (top 50 of {len(weakest)})\n")
    md.append("Quality flag legend:")
    md.append("- `no_behavioral_assertions`: zero `assert*` / `expect()` calls in test_outputs.py")
    md.append("- `mostly_structural`: tests inspect source via AST or string-matching, don't run code")
    md.append("- `minimal`: ≤ 2 behavioral assertions and no real runner")
    md.append("- `unmatched_f2p`: declared f2p check has no matching `def test_*` function\n")
    md.append("| Task | Quality | Real runner | f2p declared | f2p matched | f2p unmatched |")
    md.append("|---|---|---:|---:|---:|---:|")
    for r in weakest[:50]:
        md.append(f"| `{r['task']}` | {r.get('test_quality', '?')} | "
                  f"{'yes' if r.get('calls_real_runner') else '—'} | "
                  f"{r.get('f2p_declared', 0)} | "
                  f"{r.get('f2p_matched', 0)} | "
                  f"{r.get('f2p_unmatched', 0)} |")
    md.append("")
    out_path.write_text("\n".join(md))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", type=Path, default=TASK_DIR)
    ap.add_argument("--audit-jsonl", type=Path,
                    default=ROOT / "pipeline_logs" / "test_coverage_audit.jsonl")
    ap.add_argument("--report-md", type=Path,
                    default=ROOT / "research" / "test_coverage_audit.md")
    args = ap.parse_args()

    rows: list[dict] = []
    for d in sorted(args.task_dir.iterdir()):
        if not d.is_dir():
            continue
        rows.append(audit_one(d))

    args.audit_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with open(args.audit_jsonl, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    summary = aggregate(rows)
    print(json.dumps(summary, indent=2))

    write_markdown(rows, summary, args.report_md)
    print(f"\nReport: {args.report_md}")


if __name__ == "__main__":
    main()
