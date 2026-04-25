#!/usr/bin/env python3
"""Combine triviality + causality + lint verdicts into a final corpus
recommendation.

Inputs:
- /tmp/triviality_combined.json   — list of {name, verdict: trivial|substantial}
- /tmp/causality_full.json        — list of {name, verdict: load_bearing|decorative}
- /tmp/lint_baseline.json         — {name: [findings]}
- harbor_tasks/<task>/quality.json — per-task quality verdicts

Outputs (one row per active task):
- /tmp/corpus_recommendations.json — full per-task data
- /tmp/quarantine_decorative.txt   — tasks to quarantine for being decorative
- /tmp/quarantine_trivial.txt      — extra trivials caught
- /tmp/keep.txt                    — tasks that survive

Decision tree (in priority order):
  1. trivial             → quarantine
  2. decorative + 0 markdown signal → quarantine (no causal connection)
  3. heavy lint fails   → fix queue (Tier-A severity=fail with non-trivial rubric)
  4. otherwise          → keep
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_triviality(p: Path) -> dict[str, str]:
    if not p.exists():
        return {}
    data = json.loads(p.read_text())
    return {r["name"]: r["verdict"] for r in data
            if r.get("verdict") in ("trivial", "substantial")}


def load_causality(p: Path) -> dict[str, dict]:
    if not p.exists():
        return {}
    data = json.loads(p.read_text())
    return {r["name"]: r for r in data
            if r.get("verdict") in ("load_bearing", "decorative")}


def load_lint(p: Path) -> dict[str, list]:
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def load_quality_fails(corpus: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for q in corpus.glob("*/quality.json"):
        try:
            d = json.loads(q.read_text())
        except Exception:
            continue
        fails = [k for k, v in (d.get("rubric_verdicts") or {}).items()
                 if v.get("outcome") == "fail"]
        if fails:
            out[q.parent.name] = fails
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path("harbor_tasks"))
    ap.add_argument("--triviality", type=Path, default=Path("/tmp/triviality_combined.json"))
    ap.add_argument("--causality",  type=Path, default=Path("/tmp/causality_full.json"))
    ap.add_argument("--lint",       type=Path, default=Path("/tmp/lint_baseline.json"))
    ap.add_argument("--out-dir",    type=Path, default=Path("/tmp"))
    args = ap.parse_args()

    triv = load_triviality(args.triviality)
    caus = load_causality(args.causality)
    lint = load_lint(args.lint)
    qfails = load_quality_fails(args.corpus)

    rows: list[dict] = []
    for d in sorted(args.corpus.iterdir()):
        if not d.is_dir():
            continue
        name = d.name
        row = {
            "name": name,
            "triviality":   triv.get(name, "?"),
            "causality":    caus.get(name, {}).get("verdict", "?"),
            "causality_reason": caus.get(name, {}).get("reason", ""),
            "md_paths_used": len(caus.get(name, {}).get("used_paths", [])),
            "lint_fails":   [f["rubric"] for f in lint.get(name, [])],
            "quality_fails": qfails.get(name, []),
        }

        # Decision
        decision = "keep"
        reasons: list[str] = []
        if row["triviality"] == "trivial":
            decision = "quarantine"
            reasons.append("trivial")
        elif row["causality"] == "decorative" and row["md_paths_used"] == 0:
            decision = "quarantine"
            reasons.append("decorative_no_md")
        elif row["causality"] == "decorative":
            # Has some markdown signal but causally irrelevant — quarantine per
            # user 4/24 directive: "trajectory wouldn't change after removing markdown"
            decision = "quarantine"
            reasons.append("decorative")
        else:
            # Any non-trivial lint fail or quality fail → fix queue.
            # Tier-A rubrics that demand semantic rewrites (skip mechanical
            # tier-B like pinned_dependencies and no_network — those are
            # auto-fixable with separate scripts).
            tier_a = {"oracle_no_external_fetch", "tests_have_subprocess",
                      "gold_diff_non_trivial", "test_not_tautological",
                      "tests_verify_behavior_not_text",
                      "no_hidden_solution_artifacts",
                      "reward_is_pure_pytest"}
            if any(r in tier_a for r in row["lint_fails"]) or row["quality_fails"]:
                decision = "fix"
                reasons.append("quality_or_lint_fail")
        row["decision"] = decision
        row["reasons"]  = reasons
        rows.append(row)

    # Summary
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["decision"]] = counts.get(r["decision"], 0) + 1
    print(f"=== Decisions across {len(rows)} active tasks ===")
    for k, v in sorted(counts.items()):
        print(f"  {k:>10s}: {v}")

    # Write outputs
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "corpus_recommendations.json").write_text(json.dumps(rows, indent=2))

    quarantine = [r for r in rows if r["decision"] == "quarantine"]
    fix       = [r for r in rows if r["decision"] == "fix"]
    keep      = [r for r in rows if r["decision"] == "keep"]

    (args.out_dir / "quarantine_decorative.txt").write_text(
        "\n".join(r["name"] for r in quarantine if "decorative" in " ".join(r["reasons"]))
    )
    (args.out_dir / "quarantine_trivial.txt").write_text(
        "\n".join(r["name"] for r in quarantine if "trivial" in r["reasons"])
    )
    (args.out_dir / "fix_queue.txt").write_text("\n".join(r["name"] for r in fix))
    (args.out_dir / "keep.txt").write_text("\n".join(r["name"] for r in keep))

    print(f"\nWrote: corpus_recommendations.json, quarantine_*.txt, fix_queue.txt, keep.txt")


if __name__ == "__main__":
    main()
