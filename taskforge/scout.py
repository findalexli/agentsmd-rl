"""PR scouting: discover, filter, and classify candidate PRs for task generation.

Consolidates all scouting logic:
  - Code-only PR scouting (harbor_tasks)
  - AgentMD PR scouting (harbor_tasks_agentmd_edits) — PRs touching code + config
  - Pre-filtering with heuristics
  - Quality filtering with diff analysis and config classification

Adapted from:
- SWE-bench (princeton-nlp/SWE-bench) — patch splitting, License: MIT
- R2E-Gym — size thresholds

Usage:
    python -m taskforge.scout --output scouted_prs.jsonl
    python -m taskforge.scout --agentmd --output scouted_agentmd_prs.jsonl
    python -m taskforge.scout filter --input scouted_prs.jsonl --output filtered.jsonl
    python -m taskforge.scout filter --agentmd --input scouted_agentmd.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Sequence

from unidiff import PatchSet

from taskforge.config import gh_json, is_agent_instruction_file, is_code_file, is_config_file, is_doc_file
from taskforge.models import PRCandidate

ROOT = Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# Default repo lists
# ---------------------------------------------------------------------------

DEFAULT_REPOS = [
    ("sgl-project/sglang", 30, None),
    ("vllm-project/vllm", 30, None),
    ("gradio-app/gradio", 40, None),
    ("huggingface/transformers", 40, None),
    ("pytorch/pytorch", 20, "large repo, be selective"),
    ("astral-sh/ruff", 35, None),
    ("vercel/next.js", 30, None),
    ("inclusionAI/AReaL", 25, None),
    ("openclaw/openclaw", 15, "vibecoded, extra careful"),
    ("elev8tion/zeroclaw", 10, "vibecoded, extra careful"),
    ("THUDM/slime", 20, None),
    ("anomalyco/opencode", 40, None),
    ("PrimeIntellect-ai/prime-rl", 20, None),
    ("thinking-machines-lab/tinker", 15, None),
    ("oven-sh/bun", 40, None),
    ("astral-sh/uv", 35, None),
]

SKIP_LABELS = {
    "dependencies", "documentation", "docs", "release", "ci", "chore",
    "bot", "automated", "renovate", "dependabot", "skip-ci",
}

# ---------------------------------------------------------------------------
# Patch splitting
# ---------------------------------------------------------------------------

TEST_PATH_KEYWORDS: Sequence[str] = ("test", "tests", "e2e", "testing", "spec", "__tests__")


def split_patch(diff_text: str) -> tuple[str, str]:
    """Split a unified diff into (code_patch, test_patch)."""
    if not diff_text or not diff_text.strip():
        return "", ""
    try:
        patch_set = PatchSet(diff_text)
    except Exception:
        return diff_text, ""

    code_hunks: list[str] = []
    test_hunks: list[str] = []
    for patched_file in patch_set:
        path_lower = patched_file.path.lower()
        if any(kw in path_lower for kw in TEST_PATH_KEYWORDS):
            test_hunks.append(str(patched_file))
        else:
            code_hunks.append(str(patched_file))
    return "\n".join(code_hunks), "\n".join(test_hunks)


def extract_new_identifiers(diff_text: str) -> set[str]:
    """Extract identifiers that appear only in added lines (leakage detection)."""
    if not diff_text:
        return set()
    added: set[str] = set()
    removed: set[str] = set()
    ident_re = re.compile(r"\b([a-zA-Z_]\w{2,})\b")
    for line in diff_text.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            added.update(ident_re.findall(line))
        elif line.startswith("-") and not line.startswith("---"):
            removed.update(ident_re.findall(line))
    return added - removed


# ---------------------------------------------------------------------------
# PR filtering (heuristic)
# ---------------------------------------------------------------------------

MAX_FILES = 100
MAX_LINES_CHANGED = 5000
MIN_LINES_CHANGED = 5

_DOC_EXTENSIONS = frozenset({".md", ".rst", ".adoc"})
_DOC_PREFIXES = ("docs/", "doc/", ".github/", "website/")
_LOCKFILE_KEYWORDS = frozenset({
    "lock", "requirements", "package.json", "Cargo.toml",
    "pyproject.toml", "go.sum", "yarn.lock", "pnpm-lock",
})
_SHA1_RE = re.compile(r"(?<!/)\b[0-9a-f]{40}\b")


def is_good_candidate(pr: PRCandidate, diff: str = "") -> tuple[bool, str]:
    """Run all heuristic filters. Returns (passed, reason)."""
    if pr.changed_files < 1 or pr.changed_files > MAX_FILES:
        return False, f"file count {pr.changed_files} outside [1, {MAX_FILES}]"
    if pr.total_changes > MAX_LINES_CHANGED:
        return False, f"too large ({pr.total_changes} lines > {MAX_LINES_CHANGED})"
    if pr.total_changes < MIN_LINES_CHANGED:
        return False, f"too small ({pr.total_changes} < {MIN_LINES_CHANGED} lines)"
    if _is_docs_only(pr.file_paths):
        return False, "docs-only PR"
    if _is_deps_only(pr.file_paths):
        return False, "deps-only PR"
    if diff:
        code_patch, _ = split_patch(diff)
        if not code_patch.strip():
            return False, "test-only PR (no code changes)"
    if _SHA1_RE.search(pr.title or ""):
        return False, "title contains commit hash"
    return True, "passed"


def _is_docs_only(paths: Sequence[str]) -> bool:
    if not paths:
        return False
    for p in paths:
        ext = "." + p.rsplit(".", 1)[-1] if "." in p else ""
        if ext not in _DOC_EXTENSIONS and ext not in {".toml", ".cfg", ".ini", ".yml", ".yaml", ".json"}:
            if not any(p.startswith(pfx) for pfx in _DOC_PREFIXES):
                return False
    return True


def _is_deps_only(paths: Sequence[str]) -> bool:
    if not paths:
        return False
    return all(any(kw in p for kw in _LOCKFILE_KEYWORDS) for p in paths)


# ---------------------------------------------------------------------------
# Existing task dedup
# ---------------------------------------------------------------------------

def get_existing_prs(*task_dirs: Path) -> set[tuple[str, int]]:
    """Get (repo, pr_number) pairs for already-scaffolded tasks."""
    existing = set()
    for task_dir in task_dirs:
        if not task_dir.exists():
            continue
        for td in task_dir.iterdir():
            toml = td / "task.toml"
            if not toml.exists():
                continue
            text = toml.read_text()
            repo = pr = None
            for line in text.splitlines():
                if line.startswith("source_repo"):
                    repo = line.split("=")[1].strip().strip('"')
                if line.startswith("source_pr"):
                    try:
                        pr = int(line.split("=")[1].strip())
                    except ValueError:
                        pass
            if repo and pr:
                existing.add((repo, pr))
    return existing


# ---------------------------------------------------------------------------
# Code-only scouting
# ---------------------------------------------------------------------------

def scout_repo(
    repo: str,
    target: int,
    existing: set[tuple[str, int]],
    caution: str | None = None,
) -> list[dict]:
    """Scout a single repo for candidate code-only PRs."""
    print(f"\n{'='*60}")
    print(f"  Scouting {repo} (target: {target})")
    if caution:
        print(f"  ! {caution}")
    print(f"{'='*60}")

    fetch_limit = target * 4

    prs = gh_json([
        "pr", "list",
        "--repo", repo,
        "--state", "merged",
        "--limit", str(fetch_limit),
        "--json", "number,title,files,changedFiles,additions,deletions,mergedAt,labels,mergeCommit",
    ])

    if not prs:
        print(f"  No PRs found or error")
        return []

    print(f"  Fetched {len(prs)} merged PRs")

    candidates = []
    skipped: dict[str, int] = {
        "existing": 0, "too_many_files": 0, "too_few_changes": 0,
        "too_many_changes": 0, "docs_only": 0, "deps_only": 0, "label_skip": 0,
    }

    for pr in prs:
        pr_num = pr.get("number", 0)

        if (repo, pr_num) in existing:
            skipped["existing"] += 1
            continue

        pr_labels = {la.get("name", "").lower() for la in pr.get("labels", [])}
        if pr_labels & SKIP_LABELS:
            skipped["label_skip"] += 1
            continue

        changed_files = pr.get("changedFiles", 0)
        additions = pr.get("additions", 0)
        deletions = pr.get("deletions", 0)
        total_changes = additions + deletions

        if changed_files < 1 or changed_files > 8:
            skipped["too_many_files"] += 1
            continue
        if total_changes < 5:
            skipped["too_few_changes"] += 1
            continue
        if total_changes > 500:
            skipped["too_many_changes"] += 1
            continue

        files = pr.get("files", [])
        file_paths = [f.get("path", "") for f in files] if files else []

        if file_paths:
            code_files = [f for f in file_paths if not any(
                f.endswith(ext) for ext in (".md", ".rst", ".txt", ".toml", ".cfg", ".ini", ".yml", ".yaml", ".json")
            ) and not f.startswith(("docs/", "doc/", ".github/"))]
            if not code_files:
                skipped["docs_only"] += 1
                continue
            if all(any(p in f for p in ("lock", "requirements", "package.json", "Cargo.toml", "pyproject.toml"))
                   for f in file_paths):
                skipped["deps_only"] += 1
                continue

        title = pr.get("title", "")
        merge_commit = pr.get("mergeCommit", {})
        merge_sha = merge_commit.get("oid", "") if isinstance(merge_commit, dict) else ""

        candidates.append({
            "repo": repo,
            "pr_number": pr_num,
            "title": title,
            "changed_files": changed_files,
            "additions": additions,
            "deletions": deletions,
            "merged_at": pr.get("mergedAt", ""),
            "merge_sha": merge_sha,
            "file_paths": file_paths[:10],
        })

        if len(candidates) >= target:
            break

    print(f"  Candidates: {len(candidates)}")
    for reason, count in sorted(skipped.items()):
        if count > 0:
            print(f"    Skipped ({reason}): {count}")

    return candidates


# ---------------------------------------------------------------------------
# AgentMD scouting — PRs that touch code + config files
# ---------------------------------------------------------------------------

def _get_config_file_changes(repo: str, pr_number: int) -> list[dict]:
    """Get detailed file-level changes for config files in a PR."""
    files = gh_json([
        "api", f"repos/{repo}/pulls/{pr_number}/files",
        "--paginate",
        "--jq", '[.[] | {path: .filename, additions: .additions, deletions: .deletions, status: .status}]',
    ])
    if not files:
        return []
    if isinstance(files, list) and files and isinstance(files[0], list):
        files = [f for page in files for f in page]
    return [f for f in files if is_config_file(f.get("path", ""))]


def scout_repo_agentmd(
    repo: str,
    target: int,
    existing: set[tuple[str, int]],
    cutoff_date: str,
    caution: str | None = None,
    check_config_diff: bool = True,
) -> list[dict]:
    """Scout a single repo for PRs that touch both code and config files."""
    print(f"\n{'='*60}")
    print(f"  Scouting {repo} (target: {target})")
    if caution:
        print(f"  ! {caution}")
    print(f"{'='*60}")

    fetch_limit = min(max(target * 15, 1000), 2000)  # cap at 2000 to avoid gh timeouts

    prs = gh_json([
        "pr", "list",
        "--repo", repo,
        "--state", "merged",
        "--limit", str(fetch_limit),
        "--json", "number,title,files,changedFiles,additions,deletions,mergedAt,labels,mergeCommit",
    ], retries=3)

    if not prs:
        print(f"  No PRs found or error")
        return []

    print(f"  Fetched {len(prs)} merged PRs")

    candidates = []
    skipped: dict[str, int] = {
        "existing": 0, "too_old": 0, "label_skip": 0,
        "too_many_files": 0, "too_few_files": 0,
        "too_few_changes": 0, "too_many_changes": 0,
        "no_config_file": 0, "no_code_file": 0,
        "trivial_config_edit": 0, "doc_only_trivial": 0,
    }

    for pr in prs:
        pr_num = pr.get("number", 0)

        if (repo, pr_num) in existing:
            skipped["existing"] += 1
            continue

        merged_at = pr.get("mergedAt", "")
        if merged_at and merged_at < cutoff_date:
            skipped["too_old"] += 1
            continue

        pr_labels = {la.get("name", "").lower() for la in pr.get("labels", [])}
        if pr_labels & SKIP_LABELS:
            skipped["label_skip"] += 1
            continue

        changed_files = pr.get("changedFiles", 0)
        additions = pr.get("additions", 0)
        deletions = pr.get("deletions", 0)
        total_changes = additions + deletions

        if changed_files < 2:
            skipped["too_few_files"] += 1
            continue
        if changed_files > 15:
            skipped["too_many_files"] += 1
            continue
        if total_changes < 10:
            skipped["too_few_changes"] += 1
            continue
        if total_changes > 800:
            skipped["too_many_changes"] += 1
            continue

        files = pr.get("files", [])
        file_paths = [f.get("path", "") for f in files] if files else []

        # Tier 1: agent instruction files (CLAUDE.md, AGENTS.md, .cursorrules, etc.)
        # Tier 2: documentation (README.md, CONTRIBUTING.md, CHANGELOG.md)
        instruction_files = [f for f in file_paths if is_agent_instruction_file(f)]
        doc_files = [f for f in file_paths if is_doc_file(f)]
        config_files = instruction_files + doc_files
        code_files = [f for f in file_paths if is_code_file(f)]

        if not config_files:
            skipped["no_config_file"] += 1
            continue
        if not code_files:
            skipped["no_code_file"] += 1
            continue

        # PRs that ONLY touch Tier 2 docs (no CLAUDE.md/AGENTS.md) are low-value.
        # Skip unless the doc change is substantial (>10 lines).
        if not instruction_files:
            doc_changes = sum(
                f.get("additions", 0) + f.get("deletions", 0)
                for f in files
                if is_doc_file(f.get("path", ""))
            )
            if doc_changes < 10:
                skipped["doc_only_trivial"] += 1
                continue

        # Check that config changes are meaningful (not just version bumps)
        config_changes_meaningful = False
        for f in files:
            fpath = f.get("path", "")
            if is_config_file(fpath):
                f_adds = f.get("additions", 0)
                f_dels = f.get("deletions", 0)
                # Tier 1 files: even small changes are interesting
                # Tier 2 files: need >5 lines to be meaningful
                threshold = 2 if is_agent_instruction_file(fpath) else 5
                if f_adds + f_dels > threshold:
                    config_changes_meaningful = True
                    break

        if not config_changes_meaningful and check_config_diff:
            config_detail = _get_config_file_changes(repo, pr_num)
            config_changes_meaningful = any(
                (f.get("additions", 0) + f.get("deletions", 0)) > 2
                for f in config_detail
                if is_agent_instruction_file(f.get("path", ""))
            )
            if not config_changes_meaningful:
                skipped["trivial_config_edit"] += 1
                continue

        title = pr.get("title", "")
        merge_commit = pr.get("mergeCommit", {})
        merge_sha = merge_commit.get("oid", "") if isinstance(merge_commit, dict) else ""

        candidates.append({
            "repo": repo,
            "pr_number": pr_num,
            "title": title,
            "changed_files": changed_files,
            "additions": additions,
            "deletions": deletions,
            "merged_at": merged_at,
            "merge_sha": merge_sha,
            "file_paths": file_paths[:15],
            "config_files": config_files,
            "instruction_files": instruction_files,
            "doc_files": doc_files,
            "code_files": code_files[:10],
            "has_tier1": bool(instruction_files),
        })

        if len(candidates) >= target:
            break

    print(f"  Candidates: {len(candidates)}")
    for reason, count in sorted(skipped.items()):
        if count > 0:
            print(f"    Skipped ({reason}): {count}")

    if candidates:
        all_configs = set()
        for c in candidates:
            all_configs.update(c["config_files"])
        print(f"  Config files touched: {sorted(all_configs)[:10]}")

    return candidates


# ---------------------------------------------------------------------------
# AgentMD quality filter — diff-based analysis
# ---------------------------------------------------------------------------

TRIVIAL_PATTERNS = [
    r"^[-+]\s*$",
    r"^[-+]\s*#+\s*v?\d+\.\d+",
    r"^[-+]\s*- \d{4}-\d{2}-\d{2}",
    r"^[-+]\s*<!--",
    r"^[-+]\s*\*\*Full Changelog\*\*",
]
TRIVIAL_RE = [re.compile(p) for p in TRIVIAL_PATTERNS]
BOT_PATTERNS = ["[bot]", "dependabot", "renovate", "github-actions"]


def classify_config_diff(diff_text: str, config_files: list[str]) -> dict:
    """Analyze the config file portions of a diff.

    Returns: {meaningful, config_lines_changed, edit_type, reason}
    """
    if not diff_text:
        return {"meaningful": False, "config_lines_changed": 0, "edit_type": "unknown", "reason": "no diff"}

    config_hunks: list[str] = []
    in_config_file = False
    current_lines: list[str] = []

    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            if in_config_file and current_lines:
                config_hunks.extend(current_lines)
            in_config_file = False
            current_lines = []
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

    added_lines = []
    removed_lines = []
    for line in config_hunks:
        if line.startswith("+") and not line.startswith("+++"):
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


def _gh_diff(repo: str, pr_number: int) -> str:
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


def filter_prs(
    prs: list[dict],
    *,
    agentmd: bool = False,
    fetch_diffs: bool = True,
) -> tuple[list[dict], dict[str, int]]:
    """Filter a list of scouted PRs for quality.

    For agentmd mode: fetches diffs and classifies config changes.
    For standard mode: applies heuristic filters via is_good_candidate.

    Returns (kept, skipped_counts).
    """
    kept = []
    skipped: dict[str, int] = {}

    for i, raw in enumerate(prs):
        if i > 0 and i % 50 == 0:
            print(f"  Progress: {i}/{len(prs)} ({len(kept)} kept so far)")

        if agentmd:
            # AgentMD quality filter — prioritize PRs with meaningful instruction file changes
            title = raw.get("title", "").lower()
            if any(bot in title for bot in BOT_PATTERNS):
                skipped["bot"] = skipped.get("bot", 0) + 1
                continue

            total = raw.get("additions", 0) + raw.get("deletions", 0)
            if total > 600:
                skipped["too_large"] = skipped.get("too_large", 0) + 1
                continue

            config_files = raw.get("config_files", [])
            instruction_files = raw.get("instruction_files", [])

            # Skip PRs that only touch changelogs/history
            if all("change" in cf.lower() or "history" in cf.lower() for cf in config_files):
                skipped["config_only_changelog"] = skipped.get("config_only_changelog", 0) + 1
                continue

            # Skip PRs that only touch Tier 2 docs (README/CONTRIBUTING) with no
            # Tier 1 instruction files — unless the doc change is substantial
            if not instruction_files:
                doc_only_title_signals = ["readme", "changelog", "contributing", "docs:", "doc:", "documentation"]
                if any(sig in title for sig in doc_only_title_signals):
                    skipped["doc_only_pr"] = skipped.get("doc_only_pr", 0) + 1
                    continue

            if fetch_diffs:
                diff = _gh_diff(raw["repo"], raw["pr_number"])
                if not diff:
                    skipped["no_diff"] = skipped.get("no_diff", 0) + 1
                    time.sleep(0.5)
                    continue

                analysis = classify_config_diff(diff, config_files)
                raw["config_analysis"] = analysis

                if not analysis["meaningful"]:
                    skipped["trivial_config"] = skipped.get("trivial_config", 0) + 1
                    time.sleep(0.5)
                    continue

                raw["config_edit_type"] = analysis["edit_type"]
                time.sleep(0.5)
            else:
                raw["config_edit_type"] = "unknown"

            raw["config_tier"] = "tier1" if instruction_files else "tier2"
            kept.append(raw)
        else:
            # Standard heuristic filter
            pr = PRCandidate(**raw)
            diff = ""
            if fetch_diffs:
                try:
                    result = subprocess.run(
                        ["gh", "pr", "diff", str(pr.pr_number), "--repo", pr.repo],
                        capture_output=True, text=True, timeout=30,
                    )
                    if result.returncode == 0:
                        diff = result.stdout
                except Exception:
                    pass

            ok, reason = is_good_candidate(pr, diff=diff)
            if ok:
                kept.append(raw)
            else:
                skipped[reason] = skipped.get(reason, 0) + 1

    return kept, skipped


# ---------------------------------------------------------------------------
# Repo loading
# ---------------------------------------------------------------------------

def load_repos(
    repos_file: str | None = None,
    repos_csv: str | None = None,
    default_limit: int | None = None,
) -> list[tuple[str, int, str | None]]:
    """Load repo list from file, CSV arg, or default list.

    Returns list of (repo, target_count, caution_note).
    """
    if repos_file:
        repos_path = ROOT / repos_file
        repos = []
        with open(repos_path) as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                repo = r["repo"]
                target = default_limit or min(r.get("configs", 10) * 2, 50)
                repos.append((repo, target, None))
        print(f"Loaded {len(repos)} repos from {repos_path}")
        return repos

    repos = DEFAULT_REPOS
    if repos_csv:
        filter_repos = set(repos_csv.split(","))
        repos = [(r, t, c) for r, t, c in repos if r in filter_repos]

    if default_limit:
        repos = [(r, default_limit, c) for r, _, c in repos]

    return repos


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _write_jsonl(path: Path, items: list[dict]) -> None:
    with open(path, "w") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")


def _print_summary(candidates: list[dict], label: str = "Total") -> None:
    by_repo: dict[str, int] = {}
    for c in candidates:
        by_repo[c["repo"]] = by_repo.get(c["repo"], 0) + 1
    print(f"\n{'='*60}")
    print(f"  {label}: {len(candidates)}")
    for repo, count in sorted(by_repo.items()):
        print(f"    {repo}: {count}")
    print(f"{'='*60}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scout and filter GitHub PRs for task generation",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # --- scout command (default when no subcommand) ---
    scout_parser = subparsers.add_parser("scout", help="Scout repos for candidate PRs")
    scout_parser.add_argument("--agentmd", action="store_true", help="Scout for code + config PRs")
    scout_parser.add_argument("--output", help="Output JSONL file")
    scout_parser.add_argument("--repos", help="Comma-separated repo filter")
    scout_parser.add_argument("--repos-file", help="JSONL file with repos")
    scout_parser.add_argument("--limit", type=int, help="Per-repo target count")
    scout_parser.add_argument("--months", type=int, default=4, help="Months back for agentmd (default: 4)")
    scout_parser.add_argument("--skip-config-diff-check", action="store_true")
    scout_parser.add_argument("--dry-run", action="store_true")

    # --- filter command ---
    filter_parser = subparsers.add_parser("filter", help="Filter scouted PRs for quality")
    filter_parser.add_argument("--agentmd", action="store_true", help="Use agentmd filter (diff analysis)")
    filter_parser.add_argument("--input", required=True, help="Input JSONL file")
    filter_parser.add_argument("--output", help="Output JSONL file")
    filter_parser.add_argument("--skip-diffs", action="store_true", help="Skip fetching diffs")
    filter_parser.add_argument("--limit", type=int, help="Process only first N PRs")

    args = parser.parse_args()

    # Default to "scout" if no subcommand
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "scout":
        _cmd_scout(args)
    elif args.command == "filter":
        _cmd_filter(args)


def _cmd_scout(args: argparse.Namespace) -> None:
    harbor_tasks = ROOT / "harbor_tasks"
    harbor_agentmd = ROOT / "harbor_tasks_agentmd_edits"
    existing = get_existing_prs(harbor_tasks, harbor_agentmd)
    print(f"Existing tasks: {len(existing)} PRs across repos")

    if args.agentmd:
        default_output = "scouted_agentmd_prs.jsonl"
        repos_file = args.repos_file or "scouted_repos.jsonl"
        repos = load_repos(repos_file=repos_file, repos_csv=args.repos, default_limit=args.limit or 15)

        cutoff = datetime.now(timezone.utc) - timedelta(days=args.months * 30)
        cutoff_date = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"Cutoff date: {cutoff_date} ({args.months} months ago)")

        if args.dry_run:
            for repo, target, _ in repos:
                existing_count = sum(1 for r, _ in existing if r == repo)
                print(f"  {repo}: target {target}, existing {existing_count}")
            return

        all_candidates = []
        for repo, target, caution in repos:
            candidates = scout_repo_agentmd(
                repo, target, existing, cutoff_date, caution,
                check_config_diff=not args.skip_config_diff_check,
            )
            all_candidates.extend(candidates)
            time.sleep(1)

        # Config type summary
        config_types: dict[str, int] = {}
        for c in all_candidates:
            for cf in c.get("config_files", []):
                basename = cf.rsplit("/", 1)[-1] if "/" in cf else cf
                config_types[basename] = config_types.get(basename, 0) + 1
        if config_types:
            print(f"\n  Config file types:")
            for name, count in sorted(config_types.items(), key=lambda x: -x[1])[:15]:
                print(f"    {name}: {count}")
    else:
        default_output = "scouted_prs.jsonl"
        repos = load_repos(repos_file=args.repos_file, repos_csv=args.repos, default_limit=args.limit)

        if args.dry_run:
            for repo, target, _ in repos:
                existing_count = sum(1 for r, _ in existing if r == repo)
                print(f"  {repo}: target {target}, existing {existing_count}")
            return

        all_candidates = []
        for repo, target, caution in repos:
            candidates = scout_repo(repo, target, existing, caution)
            all_candidates.extend(candidates)
            time.sleep(1)

    output_path = ROOT / (args.output or default_output)
    _write_jsonl(output_path, all_candidates)
    _print_summary(all_candidates)
    print(f"  Output: {output_path}")


def _cmd_filter(args: argparse.Namespace) -> None:
    input_path = ROOT / args.input
    with open(input_path) as f:
        prs = [json.loads(line) for line in f if line.strip()]

    if args.limit:
        prs = prs[:args.limit]

    print(f"Loaded {len(prs)} PRs to filter")

    kept, skipped = filter_prs(
        prs,
        agentmd=args.agentmd,
        fetch_diffs=not args.skip_diffs,
    )

    # Default output name
    if args.output:
        output_path = ROOT / args.output
    else:
        stem = Path(args.input).stem
        output_path = ROOT / f"{stem}_filtered.jsonl"

    _write_jsonl(output_path, kept)

    print(f"\n{'='*60}")
    print(f"  Kept: {len(kept)} / {len(prs)}")
    for reason, count in sorted(skipped.items(), key=lambda x: -x[1]):
        if count > 0:
            print(f"  Skipped ({reason}): {count}")

    if args.agentmd and kept:
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
