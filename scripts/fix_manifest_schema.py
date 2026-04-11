#!/usr/bin/env python3
"""Fix eval_manifest.yaml files to conform to Pydantic EvalManifest v2.0.

Normalizes:
- source_pr variants → source: {repo, pr, base_commit, merge_commit}
- check type: pytest/programmatic/behavioral → fail_to_pass/pass_to_pass
- check origin: behavioral/code_structure → pr_diff/static
- check source.file → source.path
- rubric string sources → SourceRef objects
- Add version: "2.0" where missing

Usage:
    .venv/bin/python scripts/fix_manifest_schema.py --dry-run  # preview changes
    .venv/bin/python scripts/fix_manifest_schema.py             # apply fixes
"""

import argparse
import glob
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml
from taskforge.models import EvalManifest


def fix_manifest(data: dict, task_dir: Path) -> tuple[dict, list[str]]:
    """Fix a manifest dict to conform to v2.0. Returns (fixed_data, changes_made)."""
    changes = []

    # 1. Version
    if data.get("version") != "2.0":
        data["version"] = "2.0"
        changes.append("set version=2.0")

    # 2. Source normalization
    src = data.get("source")
    src_pr = data.get("source_pr")

    needs_source_fix = not isinstance(src, dict) or "pr" not in src or not isinstance(src.get("pr"), int)
    # Also fix if source.pr is a string like "owner/repo#123"
    if isinstance(src, dict) and isinstance(src.get("pr"), str) and "#" in str(src.get("pr", "")):
        needs_source_fix = True

    if needs_source_fix:
        new_source = {"repo": "", "pr": 0, "base_commit": "", "merge_commit": ""}

        # Collect all possible sources of repo/pr/commit info
        all_sources = []
        if isinstance(src, dict):
            all_sources.append(src)
        if isinstance(src_pr, dict):
            all_sources.append(src_pr)

        for s in all_sources:
            # Extract repo
            if not new_source["repo"]:
                owner = s.get("owner", "")
                repo_name = s.get("repo", "")
                if owner and repo_name and "/" not in repo_name:
                    new_source["repo"] = f"{owner}/{repo_name}"
                elif repo_name and "/" in repo_name:
                    new_source["repo"] = repo_name

            # Extract PR number (handle string "owner/repo#123" or int)
            if not new_source["pr"]:
                pr_val = s.get("pr", s.get("number", 0))
                if isinstance(pr_val, int):
                    new_source["pr"] = pr_val
                elif isinstance(pr_val, str):
                    m = re.search(r"#(\d+)", pr_val)
                    if m:
                        new_source["pr"] = int(m.group(1))
                        # Also extract repo from "owner/repo#123"
                        repo_m = re.match(r"([^#]+)#", pr_val)
                        if repo_m and not new_source["repo"]:
                            new_source["repo"] = repo_m.group(1)

            # Extract commits
            if not new_source["base_commit"]:
                new_source["base_commit"] = s.get("base_commit", "")
            if not new_source["merge_commit"]:
                new_source["merge_commit"] = s.get("merge_commit", "")

        if isinstance(src_pr, str):
            # source_pr: "owner/repo#123"
            m = re.match(r"([^#]+)#(\d+)", src_pr)
            if m:
                if not new_source["repo"]:
                    new_source["repo"] = m.group(1)
                if not new_source["pr"]:
                    new_source["pr"] = int(m.group(2))

        # Try to extract from Dockerfile if still missing
        if not new_source["repo"] or not new_source["base_commit"]:
            dockerfile = task_dir / "environment" / "Dockerfile"
            if dockerfile.exists():
                df_text = dockerfile.read_text()
                repo_match = re.search(r'github\.com/([a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+)', df_text)
                commit_match = re.search(r'(?:git checkout |ARG\s+BASE_COMMIT=)([a-f0-9]{7,40})', df_text)
                if repo_match and not new_source["repo"]:
                    new_source["repo"] = repo_match.group(1).rstrip("/")
                if commit_match and not new_source["base_commit"]:
                    new_source["base_commit"] = commit_match.group(1)

        # Try task.toml
        toml_path = task_dir / "task.toml"
        if toml_path.exists() and (not new_source["repo"] or not new_source["base_commit"]):
            for line in toml_path.read_text().splitlines():
                s = line.strip()
                if not new_source["base_commit"] and s.startswith("base_commit"):
                    new_source["base_commit"] = s.split("=", 1)[1].strip().strip('"')
                if not new_source["repo"]:
                    for key in ("source_repo", "repo"):
                        if s.startswith(f"{key} ") or s.startswith(f"{key}="):
                            new_source["repo"] = s.split("=", 1)[1].strip().strip('"')

        data["source"] = new_source
        data.pop("source_pr", None)
        changes.append("normalized source")

    # 3. Fix checks
    checks = data.get("checks", [])
    if checks:
        new_checks = []
        for c in checks:
            if not isinstance(c, dict):
                continue
            # Fix type
            ctype = c.get("type", "")
            if ctype in ("pytest", "programmatic", "behavioral"):
                # Guess based on description or default to fail_to_pass
                if c.get("category") == "pass_to_pass" or "pass_to_pass" in str(c):
                    c["type"] = "pass_to_pass"
                else:
                    c["type"] = "fail_to_pass"
                changes.append(f"fix check type {ctype}→{c['type']}")
            elif ctype not in ("fail_to_pass", "pass_to_pass"):
                c["type"] = "fail_to_pass"  # default
                changes.append(f"fix unknown check type {ctype}")

            # Fix origin
            origin = c.get("origin", "")
            if origin in ("behavioral", "code_structure"):
                c["origin"] = "pr_diff"
                changes.append(f"fix origin {origin}→pr_diff")
            elif origin not in ("pr_diff", "repo_tests", "agent_config", "static"):
                c["origin"] = "pr_diff"  # default

            # Fix source formats
            if isinstance(c.get("source"), str):
                # String source like "CLAUDE.md:15-20"
                src_str = c["source"]
                m = re.match(r'([^:]+):?([\d-]*)', src_str)
                if m:
                    c["source"] = {"path": m.group(1).strip(), "lines": m.group(2) or ""}
                else:
                    c["source"] = {"path": src_str}
                changes.append("fix string check source")
            if isinstance(c.get("source"), dict):
                src = c["source"]
                if "file" in src and "path" not in src:
                    src["path"] = src.pop("file")
                    changes.append("fix source.file→path")
                if "files" in src:
                    files = src.pop("files")
                    if isinstance(files, list) and files:
                        src["path"] = files[0]
                # Remove extra fields
                for extra in list(src.keys()):
                    if extra not in ("path", "lines", "commit"):
                        del src[extra]

            # Ensure id exists
            if "id" not in c:
                desc = c.get("description", "check")
                c["id"] = re.sub(r'[^a-z0-9]+', '_', desc.lower())[:50].strip('_')

            # Remove non-standard fields
            valid_keys = {"id", "type", "origin", "description", "source"}
            for k in list(c.keys()):
                if k not in valid_keys:
                    del c[k]

            new_checks.append(c)
        data["checks"] = new_checks

    # 4. Fix rubric
    rubric = data.get("rubric", [])
    if rubric:
        new_rubric = []
        for r in rubric:
            if isinstance(r, str):
                r = {"rule": r}
                changes.append("fix string rubric→dict")
            if not isinstance(r, dict):
                continue
            if "rule" not in r and "criterion" in r:
                r["rule"] = r.pop("criterion")
                changes.append("fix criterion→rule")
            if "rule" not in r and "description" in r:
                r["rule"] = r.pop("description")
            # Fix string sources
            if isinstance(r.get("source"), str):
                src_str = r["source"]
                m = re.match(r'([^:]+):(\d+(?:-\d+)?)', src_str)
                if m:
                    r["source"] = {"path": m.group(1), "lines": m.group(2)}
                else:
                    r["source"] = {"path": src_str}
                changes.append("fix string source→SourceRef")
            # Remove non-standard fields
            valid_keys = {"rule", "source", "reference", "evidence", "category",
                          "verification", "check_cmd"}
            for k in list(r.keys()):
                if k not in valid_keys:
                    del r[k]
            if r.get("rule"):
                new_rubric.append(r)
        data["rubric"] = new_rubric

    # 5. Fix distractors
    distractors = data.get("distractors", [])
    if distractors:
        new_dist = []
        for d in distractors:
            if not isinstance(d, dict) or not d.get("rule"):
                continue
            valid_keys = {"rule", "source", "collision_type", "why_distracting", "severity"}
            for k in list(d.keys()):
                if k not in valid_keys:
                    del d[k]
            new_dist.append(d)
        data["distractors"] = new_dist

    # 6. Remove non-standard top-level keys
    valid_top = {"version", "source", "checks", "config_edits", "rubric",
                 "distractors", "hierarchy_analysis"}
    for k in list(data.keys()):
        if k not in valid_top:
            del data[k]
            changes.append(f"removed extra key: {k}")

    return data, changes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    files = sorted(
        glob.glob("harbor_tasks/*/eval_manifest.yaml") +
        glob.glob("harbor_tasks_agentmd_edits/*/eval_manifest.yaml")
    )

    fixed = 0
    already_valid = 0
    still_broken = 0

    for f in files:
        task_dir = Path(f).parent
        data = yaml.safe_load(open(f)) or {}

        # Check if already valid
        try:
            EvalManifest.model_validate(data)
            already_valid += 1
            continue
        except Exception:
            pass

        # Try to fix
        fixed_data, changes = fix_manifest(data, task_dir)

        # Validate fixed version
        try:
            EvalManifest.model_validate(fixed_data)
            if not args.dry_run:
                Path(f).write_text(yaml.dump(
                    fixed_data, default_flow_style=False, sort_keys=False, allow_unicode=True
                ))
            fixed += 1
            if len(changes) <= 5:
                print(f"  FIXED {task_dir.name}: {', '.join(changes[:3])}")
        except Exception as e:
            still_broken += 1
            if still_broken <= 10:
                print(f"  BROKEN {task_dir.name}: {str(e)[:100]}")

    print(f"\n{'='*60}")
    print(f"Already valid: {already_valid}")
    print(f"Fixed: {fixed}")
    print(f"Still broken: {still_broken}")
    print(f"Total: {already_valid + fixed + still_broken}")
    if args.dry_run:
        print("(DRY RUN — no files modified)")


if __name__ == "__main__":
    main()
