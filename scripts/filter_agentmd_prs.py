#!/usr/bin/env python3
"""Filter scouted agentmd PRs for quality.

Fetches the actual diff for each PR and filters out:
  1. Trivial config changes (version bumps, date updates, formatting only)
  2. Config-only PRs (no meaningful code changes)
  3. PRs where config change is just a changelog entry
  4. PRs with too-large diffs (would timeout during scaffold)
  5. PRs from bots

Also classifies each PR by config edit type:
  - new_feature_doc: documenting a new feature/API
  - rule_update: adding/modifying a coding rule or convention
  - architecture_doc: updating architecture/module documentation
  - troubleshooting: adding troubleshooting/gotcha notes
  - deprecation: documenting deprecation
  - other

Usage:
    python scripts/filter_agentmd_prs.py --input scouted_agentmd_prs.jsonl --output scouted_agentmd_prs_filtered.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Patterns that indicate a trivial config change
TRIVIAL_PATTERNS = [
    r"^[-+]\s*$",  # blank lines only
    r"^[-+]\s*#+\s*v?\d+\.\d+",  # version headers
    r"^[-+]\s*- \d{4}-\d{2}-\d{2}",  # changelog dates
    r"^[-+]\s*<!--",  # HTML comments
    r"^[-+]\s*\*\*Full Changelog\*\*",  # auto-generated changelog
]
TRIVIAL_RE = [re.compile(p) for p in TRIVIAL_PATTERNS]

# Bot authors to skip
BOT_PATTERNS = ["[bot]", "dependabot", "renovate", "github-actions"]


def gh_diff(repo: str, pr_number: int) -> str:
    """Fetch PR diff via gh CLI."""
    try:
        result = subprocess.run(
            ["gh", "pr", "diff", str(pr_number), "--repo", repo],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            return result.stdout
    except Exception:
        pass
    return ""


def classify_config_diff(diff_text: str, config_files: list[str]) -> dict:
    """Analyze the config file portions of a diff.

    Returns: {
        "meaningful": bool,
        "config_lines_changed": int,
        "edit_type": str,
        "reason": str,
    }
    """
    if not diff_text:
        return {"meaningful": False, "config_lines_changed": 0, "edit_type": "unknown", "reason": "no diff"}

    # Extract hunks for config files
    config_hunks = []
    in_config_file = False
    current_lines = []

    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            if in_config_file and current_lines:
                config_hunks.extend(current_lines)
            in_config_file = False
            current_lines = []
            # Check if this file is a config file
            for cf in config_files:
                if cf in line:
                    in_config_file = True
                    break
        elif in_config_file:
            current_lines.append(line)

    if in_config_file and current_lines:
        config_hunks.extend(current_lines)

    if not config_hunks:
        return {"meaningful": False, "config_lines_changed": 0, "edit_type": "unknown", "reason": "no config hunks found"}

    # Count non-trivial changed lines
    added_lines = []
    removed_lines = []
    for line in config_hunks:
        if line.startswith("+") and not line.startswith("+++"):
            # Check if trivial
            is_trivial = any(p.match(line) for p in TRIVIAL_RE)
            if not is_trivial and line.strip() not in ("+", ""):
                added_lines.append(line[1:].strip())
        elif line.startswith("-") and not line.startswith("---"):
            is_trivial = any(p.match(line) for p in TRIVIAL_RE)
            if not is_trivial and line.strip() not in ("-", ""):
                removed_lines.append(line[1:].strip())

    total_meaningful = len(added_lines) + len(removed_lines)

    if total_meaningful < 3:
        return {
            "meaningful": False,
            "config_lines_changed": total_meaningful,
            "edit_type": "trivial",
            "reason": f"only {total_meaningful} non-trivial config lines changed",
        }

    # Classify the edit type based on added content
    added_text = " ".join(added_lines).lower()

    edit_type = "other"
    if any(w in added_text for w in ["api", "endpoint", "function", "method", "parameter", "option", "flag"]):
        edit_type = "new_feature_doc"
    elif any(w in added_text for w in ["rule", "convention", "must", "should", "never", "always", "lint", "format"]):
        edit_type = "rule_update"
    elif any(w in added_text for w in ["module", "package", "architecture", "structure", "component", "directory"]):
        edit_type = "architecture_doc"
    elif any(w in added_text for w in ["deprecat", "removed", "replaced", "migration", "breaking"]):
        edit_type = "deprecation"
    elif any(w in added_text for w in ["troubleshoot", "gotcha", "caveat", "note", "warning", "known issue"]):
        edit_type = "troubleshooting"

    return {
        "meaningful": True,
        "config_lines_changed": total_meaningful,
        "edit_type": edit_type,
        "reason": f"{total_meaningful} meaningful config lines, type={edit_type}",
        "sample_additions": added_lines[:3],
    }


def is_bot_pr(pr: dict) -> bool:
    """Check if PR is from a bot."""
    title = pr.get("title", "").lower()
    return any(bot in title for bot in BOT_PATTERNS)


def main():
    parser = argparse.ArgumentParser(description="Filter agentmd PRs for quality")
    parser.add_argument("--input", default="scouted_agentmd_prs.jsonl")
    parser.add_argument("--output", default="scouted_agentmd_prs_filtered.jsonl")
    parser.add_argument("--skip-diff", action="store_true", help="Skip diff fetching (faster, less accurate)")
    parser.add_argument("--limit", type=int, help="Process only first N PRs")
    args = parser.parse_args()

    input_path = ROOT / args.input
    output_path = ROOT / args.output

    prs = []
    with open(input_path) as f:
        for line in f:
            if line.strip():
                prs.append(json.loads(line))

    if args.limit:
        prs = prs[:args.limit]

    print(f"Loaded {len(prs)} PRs to filter")

    kept = []
    skipped = {"bot": 0, "no_diff": 0, "trivial_config": 0, "too_large": 0, "config_only_changelog": 0}

    for i, pr in enumerate(prs):
        if i > 0 and i % 50 == 0:
            print(f"  Progress: {i}/{len(prs)} ({len(kept)} kept so far)")

        # Skip bots
        if is_bot_pr(pr):
            skipped["bot"] += 1
            continue

        # Skip overly large PRs
        total = pr.get("additions", 0) + pr.get("deletions", 0)
        if total > 600:
            skipped["too_large"] += 1
            continue

        config_files = pr.get("config_files", [])

        # Skip if only changelog/CHANGES type files
        if all("change" in cf.lower() or "history" in cf.lower() for cf in config_files):
            skipped["config_only_changelog"] += 1
            continue

        if not args.skip_diff:
            # Fetch and analyze diff
            diff = gh_diff(pr["repo"], pr["pr_number"])
            if not diff:
                skipped["no_diff"] += 1
                time.sleep(0.5)
                continue

            analysis = classify_config_diff(diff, config_files)
            pr["config_analysis"] = analysis

            if not analysis["meaningful"]:
                skipped["trivial_config"] += 1
                time.sleep(0.5)
                continue

            pr["config_edit_type"] = analysis["edit_type"]
            time.sleep(0.5)  # Rate limit
        else:
            pr["config_edit_type"] = "unknown"

        kept.append(pr)

    # Write output
    with open(output_path, "w") as f:
        for pr in kept:
            f.write(json.dumps(pr) + "\n")

    print(f"\n{'='*60}")
    print(f"  Kept: {len(kept)} / {len(prs)}")
    for reason, count in sorted(skipped.items()):
        if count > 0:
            print(f"  Skipped ({reason}): {count}")

    if kept:
        # Edit type breakdown
        types: dict[str, int] = {}
        for pr in kept:
            t = pr.get("config_edit_type", "unknown")
            types[t] = types.get(t, 0) + 1
        print(f"\n  Config edit types:")
        for t, c in sorted(types.items(), key=lambda x: -x[1]):
            print(f"    {t}: {c}")

    print(f"\n  Output: {output_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
