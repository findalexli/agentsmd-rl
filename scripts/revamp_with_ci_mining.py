#!/usr/bin/env python3
"""Revamp harbor tasks: append CI-mined p2p/f2p tests to existing test_outputs.

Per task:
  1. Read source.repo / base_commit / merge_commit / pr from eval_manifest.yaml
  2. Mine CI check-runs via taskforge.ci_check_miner.mine_task
  3. If mining produced at least 1 step, generate `tests/test_ci_mined.py` and
     add new entries to eval_manifest.yaml's `checks:` list.
  4. Back up the original test_outputs.py and eval_manifest.yaml under
     pipeline_logs/ci_revamp_<ts>/backups/<task>/ before any write.

Existing tests are preserved. The new pytest file is auto-discovered by
test.sh's `pytest /tests` invocation alongside test_outputs.py.

Output: pipeline_logs/ci_revamp_<ts>/{summary.json, mined_specs.jsonl}
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from taskforge.ci_check_miner import mine_task            # noqa: E402
from taskforge.ci_test_generator import (                  # noqa: E402
    generate_test_file, generate_manifest_checks,
    _gather_unique_steps, _collapse_matrix,
)
from taskforge.models import EvalManifest                  # noqa: E402


def revamp_one(task_dir: Path, repo_path: str, dry_run: bool, repair_dir: Path) -> dict:
    """Mine + generate + (optionally) write for one task."""
    name = task_dir.name
    rec = {"task": name, "n_checks": 0, "n_p2p": 0, "n_f2p": 0, "n_steps": 0,
           "wrote_test_file": False, "manifest_updated": False, "errors": []}

    em = task_dir / "eval_manifest.yaml"
    if not em.exists():
        rec["errors"].append("no eval_manifest.yaml"); return rec
    try:
        manifest = yaml.safe_load(em.read_text())
    except Exception as e:
        rec["errors"].append(f"manifest yaml error: {e}"); return rec
    src = (manifest or {}).get("source") or {}
    repo = src.get("repo")
    base = src.get("base_commit")
    merge = src.get("merge_commit")
    pr = int(src.get("pr") or 0)
    if not (repo and base and merge):
        rec["errors"].append("manifest missing repo/base/merge"); return rec

    # Mine CI check-runs (cached per-task; re-runs skip API)
    try:
        spec = mine_task(repo, base, merge, task=name, pr=pr)
    except Exception as e:
        rec["errors"].append(f"mine_task error: {e}"); return rec

    rec["mined_errors"] = spec.get("errors", [])
    rec["from_cache"] = spec.get("_from_cache", False)
    checks = _collapse_matrix(spec.get("checks", []))
    pairs = _gather_unique_steps(checks)
    rec["n_checks"] = len(checks)
    rec["n_steps"] = len(pairs)
    rec["n_p2p"] = sum(1 for c, _ in pairs if c.get("kind") == "p2p")
    rec["n_f2p"] = sum(1 for c, _ in pairs if c.get("kind") == "f2p")

    if not pairs:
        return rec  # nothing minable — leave task unchanged

    # Generate the test file content
    test_content = generate_test_file(spec, repo_path=repo_path)
    new_check_entries = generate_manifest_checks(spec)

    # Skip writes if any new check id collides with existing manifest entries
    existing_ids = {c.get("id") for c in (manifest.get("checks") or [])}
    deduped = [c for c in new_check_entries if c["id"] not in existing_ids]
    rec["n_new_manifest_entries"] = len(deduped)

    if dry_run:
        return rec

    # Backup originals
    backup = repair_dir / "backups" / name
    backup.mkdir(parents=True, exist_ok=True)
    if (task_dir / "tests" / "test_outputs.py").exists():
        shutil.copy2(task_dir / "tests" / "test_outputs.py", backup / "test_outputs.py")
    if em.exists():
        shutil.copy2(em, backup / "eval_manifest.yaml")

    # Append generated content to existing test_outputs.py.
    # The header docstring is dropped; only test functions get appended,
    # plus a `# === CI-mined tests ===` separator.
    existing_path = task_dir / "tests" / "test_outputs.py"
    existing_text = existing_path.read_text() if existing_path.exists() else ""
    # Strip our generator's docstring header to avoid duplicate """...""" blocks
    body = test_content
    if body.startswith('"""'):
        end = body.find('"""', 3)
        if end != -1:
            body = body[end + 3:].lstrip("\n")
    # Drop the imports/REPO line — they will already be present in existing test_outputs.py
    body_lines = []
    skip = True
    for line in body.splitlines():
        if skip and (line.startswith("import ") or line.startswith("REPO ") or line.strip() == ""):
            continue
        skip = False
        body_lines.append(line)
    body = "\n".join(body_lines)

    import re as _re
    # If there's a prior CI-mined section, strip it BEFORE de-duping.
    # This way an updated filter can shrink/replace the section, not just append.
    if "# === CI-mined tests" in existing_text:
        existing_text = _re.split(r"\n+# === CI-mined tests.*", existing_text, maxsplit=1)[0].rstrip() + "\n"

    existing_names = set(_re.findall(r"^def\s+(test_\w+)", existing_text, _re.M))
    new_names = set(_re.findall(r"^def\s+(test_\w+)", body, _re.M))
    keep_names = new_names - existing_names
    if keep_names != new_names:
        # Filter body to keep only NEW tests (collisions with hand-written existing tests)
        kept = []
        cur_name = None
        for line in body.split("\n"):
            m = _re.match(r"^def\s+(test_\w+)", line)
            if m:
                cur_name = m.group(1)
            if cur_name is None or cur_name in keep_names:
                kept.append(line)
        body = "\n".join(kept).strip("\n") + "\n"
    rec["n_new_test_funcs"] = len(keep_names)

    if not keep_names:
        # No CI tests survived the filter — write the file with just the existing
        # tests (no CI section). This handles the "stricter filter, was previously
        # populated" case correctly.
        if existing_text.strip() and existing_path.read_text() != existing_text:
            backup = repair_dir / "backups" / name
            backup.mkdir(parents=True, exist_ok=True)
            shutil.copy2(existing_path, backup / "test_outputs.py")
            existing_path.write_text(existing_text)
            rec["wrote_test_file"] = True
            rec["ci_section_cleared"] = True
        return rec

    sep = "\n\n# === CI-mined tests (taskforge.ci_check_miner) ===\n"
    new_full = existing_text.rstrip() + sep + body
    existing_path.write_text(new_full)
    rec["wrote_test_file"] = True

    # Append new check entries to manifest
    if deduped:
        manifest.setdefault("checks", [])
        manifest["checks"].extend(deduped)
        # Validate before writing
        try:
            EvalManifest.model_validate(manifest)
            em.write_text(yaml.dump(manifest, default_flow_style=False, sort_keys=False,
                                    allow_unicode=True, width=10000))
            rec["manifest_updated"] = True
        except Exception as e:
            rec["errors"].append(f"manifest validate failed: {str(e)[:200]}")
            # Roll back the test file write too
            (task_dir / "tests" / "test_ci_mined.py").unlink(missing_ok=True)
            rec["wrote_test_file"] = False

    return rec


def repo_path_for(task_dir: Path) -> str:
    """Heuristic: extract /workspace/<repo-short>/ from the Dockerfile."""
    df = task_dir / "environment" / "Dockerfile"
    if not df.exists(): return "/workspace/repo"
    txt = df.read_text()
    import re
    m = re.search(r"^WORKDIR\s+(/workspace/[\w.-]+)", txt, re.M)
    if m: return m.group(1)
    m = re.search(r"git init (/workspace/[\w.-]+)", txt)
    if m: return m.group(1)
    m = re.search(r"git clone .* (/workspace/[\w.-]+)", txt)
    if m: return m.group(1)
    return "/workspace/repo"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", default="harbor_tasks")
    ap.add_argument("--tasks", help="Comma-sep list of task names (skip otherwise)")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--apply", action="store_true", help="Write changes (default: dry-run)")
    ap.add_argument("--repair-dir", default=None)
    args = ap.parse_args()

    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    repair_dir = Path(args.repair_dir or f"pipeline_logs/ci_revamp_{ts}")
    if args.apply:
        repair_dir.mkdir(parents=True, exist_ok=True)

    task_root = Path(args.task_dir)
    candidates = sorted(t for t in task_root.iterdir() if t.is_dir())
    if args.tasks:
        wanted = set(args.tasks.split(","))
        candidates = [t for t in candidates if t.name in wanted]
    if args.limit:
        candidates = candidates[:args.limit]

    print(f"Targets: {len(candidates)} tasks  apply={args.apply}  repair_dir={repair_dir}", file=sys.stderr)
    summary = []
    spec_jsonl = []
    for t in candidates:
        rp = repo_path_for(t)
        rec = revamp_one(t, rp, dry_run=not args.apply, repair_dir=repair_dir)
        summary.append(rec)
        flag = "WROTE" if rec["wrote_test_file"] else ("WOULD-WRITE" if rec["n_steps"] else "skip")
        cache = "[c]" if rec.get("from_cache") else "[F]"  # F=fetched
        print(f"  {flag:11s} {cache} {t.name[:48]:48s} steps={rec['n_steps']:3d} p2p={rec['n_p2p']} f2p={rec['n_f2p']}  err={'; '.join(rec['errors'])[:50]}",
              file=sys.stderr, flush=True)

    if args.apply:
        (repair_dir / "summary.json").write_text(json.dumps(summary, indent=2))
        print(f"\nSummary: {repair_dir/'summary.json'}", file=sys.stderr)
    n_with_steps = sum(1 for r in summary if r["n_steps"] > 0)
    n_wrote = sum(1 for r in summary if r["wrote_test_file"])
    total_new_tests = sum(r["n_steps"] for r in summary)
    print(f"\n{n_with_steps}/{len(summary)} tasks have minable CI; {n_wrote} written; "
          f"+{total_new_tests} new tests total", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
