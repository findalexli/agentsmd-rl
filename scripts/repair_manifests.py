#!/usr/bin/env python3
"""Mechanically repair eval_manifest.yaml drift to canonical Pydantic schema.

Idempotent. Run with --dry-run first to preview impact, then again to apply.
Backs up original to <repair_dir>/backups/<task>/eval_manifest.yaml on apply.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
import yaml
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from taskforge.models import EvalManifest  # noqa: E402
from pydantic import ValidationError  # noqa: E402


# Heuristic mapping from drifted origin values → canonical 4.
# When a value is genuinely ambiguous, we err toward `pr_diff` (most common
# meaning when an agent invented a new value).
ORIGIN_MAP = {
    "pr_behavior": "pr_diff",
    "behavioral": "pr_diff",
    "behavior": "pr_diff",
    "pr_added_test": "pr_diff",
    "gold_diff": "pr_diff",
    "task_specific": "pr_diff",
    "task_spec": "static",
    "scope": "static",
    "scaffold": "static",
    "structural": "static",
    "structural_signal": "static",
    "anti_hardcode": "static",
    "pr_test": "repo_tests",
    "pr_tests": "repo_tests",
    "regression_guard": "repo_tests",
    "regression": "repo_tests",
    "repo_state": "repo_tests",
}
CANONICAL_ORIGINS = {"pr_diff", "repo_tests", "agent_config", "static"}


# Parse a free-form rubric source string into a dict.
# Examples it handles:
#   "AGENTS.md (base commit abc123, lines 35-46)"
#   "AGENTS.md (base commit abc123, line 30)"
#   "src/foo/AGENTS.md (base commit abc, point 3)"
_SRC_RE_LINES = re.compile(
    r"^\s*(?P<path>[^()]+?)\s*\(\s*base commit\s+(?P<commit>[A-Fa-f0-9]+)\s*,"
    r"\s*lines?\s+(?P<lines>[\d\-,\s]+)\s*\)\s*$"
)
_SRC_RE_DESC = re.compile(
    r"^\s*(?P<path>[^()]+?)\s*\(\s*base commit\s+(?P<commit>[A-Fa-f0-9]+)\s*,"
    r"\s*(?P<descriptor>[^)]+)\)\s*$"
)


def parse_rubric_source(s: str) -> dict | None:
    """Best-effort parse a free-form source string into SourceRef-shape dict."""
    s = s.strip()
    m = _SRC_RE_LINES.match(s)
    if m:
        return {"path": m.group("path").strip(),
                "lines": m.group("lines").strip().rstrip(","),
                "commit": m.group("commit")}
    m = _SRC_RE_DESC.match(s)
    if m:
        # Fallback: no explicit line numbers — leave lines empty.
        return {"path": m.group("path").strip(),
                "lines": "",
                "commit": m.group("commit")}
    # Last resort: just `path` from a bare filename.
    if "/" in s or s.endswith(".md"):
        # Strip everything after the first '(' if present
        path_only = s.split("(")[0].strip()
        if path_only:
            return {"path": path_only, "lines": "", "commit": ""}
    return None


# ---------------------------------------------------------------------------
# Transform passes (each idempotent and order-independent unless noted)
# ---------------------------------------------------------------------------

def fix_toplevel_source(d: dict) -> bool:
    """Move metadata.source_pr -> source; coerce pr_url/pr_number into pr int."""
    changed = False

    # Move metadata.source_pr → toplevel `source` if needed
    md = d.get("metadata")
    if isinstance(md, dict) and isinstance(md.get("source_pr"), dict) and "source" not in d:
        d["source"] = md.pop("source_pr")
        changed = True

    src = d.get("source")
    if not isinstance(src, dict):
        return changed

    # pr is required as int
    if "pr" not in src or not isinstance(src.get("pr"), int):
        # Try pr_number, then pr_url
        if isinstance(src.get("pr_number"), int):
            src["pr"] = src["pr_number"]; changed = True
        elif isinstance(src.get("pr_number"), str) and src["pr_number"].isdigit():
            src["pr"] = int(src["pr_number"]); changed = True
        elif isinstance(src.get("pr_url"), str):
            m = re.search(r"/pull/(\d+)", src["pr_url"])
            if m:
                src["pr"] = int(m.group(1)); changed = True
        elif isinstance(src.get("pr"), str) and src["pr"].isdigit():
            src["pr"] = int(src["pr"]); changed = True
    return changed


def fix_origins(d: dict) -> bool:
    """Map illegal check.origin values to canonical 4 via ORIGIN_MAP heuristic."""
    changed = False
    for c in d.get("checks", []) or []:
        if not isinstance(c, dict):
            continue
        o = c.get("origin")
        if isinstance(o, str) and o not in CANONICAL_ORIGINS:
            mapped = ORIGIN_MAP.get(o)
            if mapped:
                c["origin"] = mapped; changed = True
            else:
                # Unknown — fall back to pr_diff (most common intent)
                c["origin"] = "pr_diff"; changed = True
    return changed


def fix_source_path_keys(d: dict) -> bool:
    """In any source: dict, rename `file:` → `path:` and `ref:` → `commit:`.
    Preserve the SHA — it's important provenance even if Pydantic accepts blank."""
    changed = False

    def normalize_source(node: Any) -> None:
        nonlocal changed
        if not isinstance(node, dict):
            return
        if "file" in node and "path" not in node:
            node["path"] = node.pop("file"); changed = True
        if "ref" in node and "commit" not in node:
            node["commit"] = node.pop("ref"); changed = True

    for collection in ("checks", "rubric", "distractors"):
        for r in d.get(collection, []) or []:
            if isinstance(r, dict) and isinstance(r.get("source"), dict):
                normalize_source(r["source"])
    return changed


def fix_rubric(d: dict) -> bool:
    """rubric items: `description:` → `rule:`, parse string sources to dicts."""
    changed = False
    for r in d.get("rubric", []) or []:
        if not isinstance(r, dict):
            continue
        # description → rule
        if "rule" not in r and isinstance(r.get("description"), str):
            r["rule"] = r.pop("description"); changed = True
        # source as string → dict
        if isinstance(r.get("source"), str):
            parsed = parse_rubric_source(r["source"])
            if parsed:
                r["source"] = parsed; changed = True
    # Same for distractors
    for r in d.get("distractors", []) or []:
        if not isinstance(r, dict):
            continue
        if "rule" not in r and isinstance(r.get("description"), str):
            r["rule"] = r.pop("description"); changed = True
        if isinstance(r.get("source"), str):
            parsed = parse_rubric_source(r["source"])
            if parsed:
                r["source"] = parsed; changed = True
    return changed


def fix_config_edits(d: dict) -> bool:
    """config_edits items: file→path, added→gold_added, removed→gold_removed.
    Also coerce non-string gold_added/gold_removed to string, and dict→[dict]."""
    changed = False
    ce_root = d.get("config_edits")
    if isinstance(ce_root, dict):
        # Single dict instead of list — wrap
        d["config_edits"] = [ce_root]; changed = True
    for ce in d.get("config_edits", []) or []:
        if not isinstance(ce, dict):
            continue
        if "path" not in ce and isinstance(ce.get("file"), str):
            ce["path"] = ce.pop("file"); changed = True
        if "gold_added" not in ce and "added" in ce:
            ce["gold_added"] = ce.pop("added") or ""; changed = True
        if "gold_removed" not in ce and "removed" in ce:
            ce["gold_removed"] = ce.pop("removed") or ""; changed = True
        # Coerce list/dict gold_added → string
        for k in ("gold_added", "gold_removed"):
            v = ce.get(k)
            if v is None:
                ce[k] = ""; changed = True
            elif isinstance(v, list):
                ce[k] = "\n".join(str(x) for x in v); changed = True
            elif isinstance(v, dict):
                ce[k] = yaml.dump(v, default_flow_style=False); changed = True
            elif not isinstance(v, str):
                ce[k] = str(v); changed = True
    return changed


def fix_check_sources(d: dict) -> bool:
    """checks[*].source as string → dict, like rubric.source."""
    changed = False
    for c in d.get("checks", []) or []:
        if isinstance(c, dict) and isinstance(c.get("source"), str):
            parsed = parse_rubric_source(c["source"])
            if parsed:
                c["source"] = parsed; changed = True
    return changed


# Mapping for non-canonical check.type values
TYPE_MAP = {
    "f2p": "fail_to_pass", "fail-to-pass": "fail_to_pass",
    "p2p": "pass_to_pass", "pass-to-pass": "pass_to_pass",
    "always_pass": "pass_to_pass", "regression": "pass_to_pass",
}
# Mapping for non-canonical rubric verification values
VERIFICATION_MAP = {
    "llm": "llm_judge", "judge": "llm_judge", "soft": "llm_judge",
    "deterministic": "programmatic", "automated": "programmatic",
    "diff": "semantic_diff",
}


def fix_check_types(d: dict) -> bool:
    """Map non-canonical check.type → fail_to_pass / pass_to_pass."""
    changed = False
    for c in d.get("checks", []) or []:
        if isinstance(c, dict):
            t = c.get("type")
            if isinstance(t, str) and t not in {"fail_to_pass", "pass_to_pass"}:
                if t in TYPE_MAP:
                    c["type"] = TYPE_MAP[t]; changed = True
    return changed


def fix_rubric_lines_str(d: dict) -> bool:
    """rubric/check source.lines must be a string. Coerce ints/lists to str."""
    changed = False
    for collection in ("rubric", "distractors", "checks"):
        for r in d.get(collection, []) or []:
            if not isinstance(r, dict):
                continue
            src = r.get("source")
            if isinstance(src, dict) and "lines" in src:
                v = src["lines"]
                if v is None:
                    src["lines"] = ""; changed = True
                elif isinstance(v, int):
                    src["lines"] = str(v); changed = True
                elif isinstance(v, list):
                    src["lines"] = "-".join(str(x) for x in v[:2]) if v else ""; changed = True
                elif not isinstance(v, str):
                    src["lines"] = str(v); changed = True
    return changed


def fix_verification(d: dict) -> bool:
    """rubric items: map non-canonical verification values."""
    changed = False
    for r in d.get("rubric", []) or []:
        if not isinstance(r, dict):
            continue
        v = r.get("verification")
        if isinstance(v, str) and v not in {"programmatic", "llm_judge", "semantic_diff"}:
            if v in VERIFICATION_MAP:
                r["verification"] = VERIFICATION_MAP[v]; changed = True
            else:
                r["verification"] = "llm_judge"; changed = True
    return changed


def fix_version(d: dict) -> bool:
    """Force version to '2.0' string."""
    if d.get("version") != "2.0":
        d["version"] = "2.0"
        return True
    return False


def fix_synthesize_source_from_metadata(d: dict) -> bool:
    """If toplevel `source` is missing but PR info is in metadata or task fields, synthesize it."""
    if isinstance(d.get("source"), dict) and "pr" in d["source"] and "repo" in d["source"]:
        return False
    # Try to scrape PR info from metadata, task, or root keys
    candidates = [d.get("metadata"), d.get("task"), d]
    for c in candidates:
        if not isinstance(c, dict):
            continue
        repo = c.get("repo")
        pr = c.get("pr") or c.get("pr_number")
        base_commit = c.get("base_commit", "")
        merge_commit = c.get("merge_commit", "")
        owner = c.get("owner")
        if owner and not repo:
            r = c.get("repo_name") or c.get("repo")
            if r and "/" not in str(r):
                repo = f"{owner}/{r}"
        if isinstance(pr, str) and pr.isdigit():
            pr = int(pr)
        if repo and isinstance(pr, int) and base_commit:
            d["source"] = {"repo": str(repo), "pr": pr,
                           "base_commit": str(base_commit),
                           "merge_commit": str(merge_commit or "")}
            return True
    return False


PASSES = [fix_version, fix_toplevel_source, fix_synthesize_source_from_metadata,
          fix_origins, fix_source_path_keys, fix_check_sources,
          fix_rubric, fix_rubric_lines_str, fix_check_types, fix_verification,
          fix_config_edits]


def repair(data: dict) -> tuple[dict, list[str]]:
    """Apply all passes until stable. Return (repaired_data, applied_pass_names)."""
    applied = []
    for _ in range(4):  # converge
        any_change = False
        for fn in PASSES:
            if fn(data):
                applied.append(fn.__name__); any_change = True
        if not any_change:
            break
    return data, applied


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", default="harbor_tasks", help="Directory containing tasks")
    ap.add_argument("--apply", action="store_true", help="Write changes (default: dry-run)")
    ap.add_argument("--repair-log-dir", default=None, help="Where to put backups (default: pipeline_logs/manifest_repair_<ts>/)")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    task_root = Path(args.task_dir)
    if not task_root.exists():
        print(f"ERROR: {task_root} not found"); return 2

    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    repair_dir = Path(args.repair_log_dir) if args.repair_log_dir else Path(f"pipeline_logs/manifest_repair_{ts}")
    if args.apply:
        repair_dir.mkdir(parents=True, exist_ok=True)
        (repair_dir / "backups").mkdir(exist_ok=True)

    tasks = sorted(t for t in task_root.iterdir() if t.is_dir())
    if args.limit:
        tasks = tasks[:args.limit]

    pass_before = pass_after = fail_before = fail_after = no_manifest = yaml_err = unchanged = 0
    fixed_tasks = []
    still_failing = []
    for t in tasks:
        m = t / "eval_manifest.yaml"
        if not m.exists():
            no_manifest += 1; continue
        try:
            data = yaml.safe_load(m.read_text())
        except Exception:
            yaml_err += 1; continue
        if not isinstance(data, dict):
            yaml_err += 1; continue

        # Validate before — count errors
        errs_before: int
        try:
            EvalManifest.model_validate(data)
            ok_before = True
            errs_before = 0
            pass_before += 1
        except ValidationError as ve:
            ok_before = False
            errs_before = len(ve.errors())
            fail_before += 1

        # Repair (mutates a deep copy)
        import copy as _copy
        original_text = m.read_text()
        repaired = _copy.deepcopy(data)
        repaired, applied = repair(repaired)

        # Validate after — count errors
        try:
            EvalManifest.model_validate(repaired)
            errs_after = 0
            pass_after += 1
            if not ok_before:
                fixed_tasks.append((t.name, applied))
        except ValidationError as ve:
            errs_after = len(ve.errors())
            fail_after += 1
            if not ok_before:
                still_failing.append((t.name, errs_after))

        # Save policy: write iff we made the manifest STRICTLY better.
        # Either fully fixed (errs_after == 0 and ok_before false), or partially
        # fixed (errs_after < errs_before). Mechanical pass on already-clean
        # manifest also gets saved if text changed (e.g. ref→commit).
        new_text = yaml.dump(repaired, default_flow_style=False, sort_keys=False, allow_unicode=True, width=10000)
        text_changed = new_text != original_text
        is_improvement = (errs_after == 0 and not ok_before) or (errs_after < errs_before)
        if args.apply and (is_improvement or (ok_before and text_changed)):
            backup = repair_dir / "backups" / t.name / "eval_manifest.yaml"
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(m, backup)
            m.write_text(new_text)

    print(f"\n=== {task_root}/ : {len(tasks)} tasks ===")
    print(f"  pass before:  {pass_before}")
    print(f"  pass after:   {pass_after}    Δ +{pass_after - pass_before}")
    print(f"  fail before:  {fail_before}")
    print(f"  fail after:   {fail_after}    Δ -{fail_before - fail_after}")
    print(f"  no manifest:  {no_manifest}")
    print(f"  yaml error:   {yaml_err}")
    print(f"\n  newly fixed: {len(fixed_tasks)}")
    print(f"  still failing: {len(still_failing)}")

    if args.apply:
        print(f"\nBackups saved to: {repair_dir}/backups/")
        # Save manifest of changes
        log = repair_dir / "summary.txt"
        with log.open("w") as f:
            f.write(f"Repaired {len(fixed_tasks)} manifests in {task_root}\n")
            f.write(f"Pass: {pass_before} → {pass_after}\n\n")
            f.write("Fixed tasks:\n")
            for name, passes in fixed_tasks:
                f.write(f"  {name}: {','.join(sorted(set(passes)))}\n")
            f.write(f"\nStill failing ({len(still_failing)}):\n")
            for name, n in still_failing:
                f.write(f"  {name}: {n} errors\n")
        print(f"Summary: {log}")
    else:
        print("\n(dry-run — pass --apply to write changes)")
        print(f"\nSample of newly fixed ({min(8, len(fixed_tasks))}):")
        for name, passes in fixed_tasks[:8]:
            print(f"  {name}: {','.join(sorted(set(passes)))}")
        print(f"\nSample of still-failing ({min(8, len(still_failing))}):")
        for name, n in still_failing[:8]:
            print(f"  {name}: {n} errors remaining")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
