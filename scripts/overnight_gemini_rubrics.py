#!/usr/bin/env python3
"""Overnight Gemini rubric extraction — multi-call with pre-numbered lines.

For each task:
1. Clone repo at commit (shallow --depth=1)
2. Find all config files (CLAUDE.md, AGENTS.md, SKILL.md, etc.)
3. Pre-number every line of each config file
4. Gemini Call 1: CLASSIFY each config file as relevant/distracting/irrelevant
5. Gemini Call 2: EXTRACT rubric rules from relevant files (with numbered lines)
6. Gemini Call 3: EXTRACT distractor rules from distracting files
7. Merge into eval_manifest.yaml (dedup, validate)

Key improvements over previous approach:
- Pre-numbered lines → zero line drift (Gemini sees "L42: Use snake_case")
- Multiple focused calls → better accuracy per call
- File-level classification first → right context for extraction
- Gold patch as ground truth for all decisions

Usage:
    set -a && source .env && set +a
    .venv/bin/python scripts/overnight_gemini_rubrics.py --dry-run
    .venv/bin/python scripts/overnight_gemini_rubrics.py --concurrency 10 --limit 20
    nohup .venv/bin/python -u scripts/overnight_gemini_rubrics.py --concurrency 10 > /tmp/overnight_rubrics.log 2>&1 &
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml
from taskforge.gemini_rubric_constructor import call_gemini

ROOT = Path(__file__).resolve().parent.parent

# ── Config file discovery ────────────────────────────────────────────────────

CONFIG_GLOBS = [
    "**/CLAUDE.md", "**/AGENTS.md", "**/SKILL.md", "**/CONVENTIONS.md",
    ".claude/rules/*.md", ".claude/skills/*/*.md",
    ".cursor/rules/*.md", "**/.agents/**/*.md",
    "**/skill/SKILL.md",
]

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".next", "dist", "build", "target"}


def find_config_files(repo_dir: Path) -> list[str]:
    """Find all agent config files in repo."""
    found = set()
    for g in CONFIG_GLOBS:
        for p in repo_dir.glob(g):
            rel = str(p.relative_to(repo_dir))
            if not any(d in rel.split("/") for d in SKIP_DIRS):
                found.add(rel)
    return sorted(found)


def number_lines(text: str) -> str:
    """Add line numbers to every line: 'L1: content', 'L2: content', ..."""
    lines = text.splitlines()
    return "\n".join(f"L{i+1}: {line}" for i, line in enumerate(lines))


# ── Gemini schemas ───────────────────────────────────────────────────────────

CLASSIFY_SCHEMA = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {
            "path": {"type": "STRING"},
            "classification": {"type": "STRING", "enum": ["relevant", "distracting", "irrelevant", "workflow_only"]},
            "reason": {"type": "STRING"},
            "key_rules_preview": {"type": "STRING"},
        },
        "required": ["path", "classification", "reason"],
    },
}

EXTRACT_RUBRIC_SCHEMA = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {
            "rule": {"type": "STRING"},
            "source_path": {"type": "STRING"},
            "start_line": {"type": "INTEGER"},
            "end_line": {"type": "INTEGER"},
            "source_text": {"type": "STRING"},
            "evidence_in_gold": {"type": "STRING"},
            "category": {"type": "STRING"},
        },
        "required": ["rule", "source_path", "start_line", "end_line", "source_text", "evidence_in_gold", "category"],
    },
}

EXTRACT_DISTRACTOR_SCHEMA = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {
            "rule": {"type": "STRING"},
            "source_path": {"type": "STRING"},
            "start_line": {"type": "INTEGER"},
            "end_line": {"type": "INTEGER"},
            "source_text": {"type": "STRING"},
            "collision_type": {"type": "STRING", "enum": [
                "rule_conflict", "scope_ambiguity", "meta_confusion",
                "architecture_boundary", "would_cause_bug",
            ]},
            "why_distracting": {"type": "STRING"},
            "severity": {"type": "STRING", "enum": ["high", "medium", "low"]},
        },
        "required": ["rule", "source_path", "start_line", "end_line", "source_text",
                      "collision_type", "why_distracting", "severity"],
    },
}

# ── Gemini calls ─────────────────────────────────────────────────────────────

def classify_config_files(
    config_files: dict[str, str],  # path -> numbered content
    gold_diff: str,
    gemini_key: str,
) -> list[dict]:
    """Call 1: Classify each config file as relevant/distracting/irrelevant."""
    file_summaries = []
    for path, content in config_files.items():
        # Send first 80 lines of each file for classification
        preview = "\n".join(content.splitlines()[:80])
        file_summaries.append(f"### {path} (first 80 lines)\n{preview}")

    prompt = f"""Classify each agent config file's relevance to this specific code change.

## Gold Diff (the correct solution)
{gold_diff[:4000]}

## Config Files
{chr(10).join(file_summaries)[:12000]}

## Classification Rules
For each file, decide:
- **relevant**: Contains coding conventions that the gold diff demonstrably FOLLOWS.
  The file has rules about patterns, naming, architecture, or style that the changed code adheres to.
- **distracting**: Contains conventions that SEEM relevant but the gold diff correctly IGNORES.
  The file covers a different scope, domain, or package than the changed files. Following these
  rules would be wrong for THIS specific change.
- **irrelevant**: Completely unrelated to the changed files (different language, different subsystem,
  no overlap in concerns).
- **workflow_only**: File only contains workflow instructions (git, CI, PR, build commands) with
  no code conventions.

Be generous with "relevant" and "distracting" — we want to extract rules, not skip them:
- A file is "relevant" if ANY rule in it could apply to the changed code's patterns, style, or architecture
- A file is "distracting" if it covers the same language/framework but different scope or subsystem
- Only mark "irrelevant" if the file is about a completely different language, platform, or domain
- Root-level CLAUDE.md and AGENTS.md are almost always "relevant" or "distracting", never "irrelevant"
- SKILL.md files in the same language as the diff are at minimum "distracting"
- Prefer "distracting" over "irrelevant" when uncertain — distractors are valuable for training"""

    resp = call_gemini(prompt, gemini_key, schema=CLASSIFY_SCHEMA,
                       temperature=0.1, max_tokens=4096)
    if isinstance(resp, str):
        return json.loads(resp)
    if isinstance(resp, list):
        return resp
    return []


def extract_rubric_rules(
    config_files: dict[str, str],  # path -> numbered content
    relevant_paths: list[str],
    gold_diff: str,
    gemini_key: str,
) -> list[dict]:
    """Call 2: Extract rubric rules from relevant config files."""
    if not relevant_paths:
        return []

    file_contents = []
    for path in relevant_paths:
        if path in config_files:
            file_contents.append(f"### {path}\n{config_files[path][:3000]}")

    prompt = f"""Extract coding convention rules from these config files that the gold diff FOLLOWS.

## Gold Diff
{gold_diff[:5000]}

## Relevant Config Files (with line numbers)
{chr(10).join(file_contents)[:10000]}

## Extraction Rules
For each rule you find:
1. The rule must be an imperative coding convention (naming, architecture, imports, style, patterns)
2. The gold diff must DEMONSTRABLY follow this rule — provide specific evidence from the diff
3. Use the EXACT line numbers shown (L42 means start_line=42)
4. Quote the source text verbatim from the numbered lines
5. SKIP workflow instructions: "run tests", "git commit", "create PR", "pre-commit", "push"
6. SKIP rules that are too generic: "write clean code", "follow best practices"
7. Each rule must cite a specific, verifiable convention — not a vague principle

The line numbers are pre-computed and exact. Use them as-is."""

    resp = call_gemini(prompt, gemini_key, schema=EXTRACT_RUBRIC_SCHEMA,
                       temperature=0.1, max_tokens=8192)
    if isinstance(resp, str):
        return json.loads(resp)
    if isinstance(resp, list):
        return resp
    return []


def extract_distractor_rules(
    config_files: dict[str, str],
    distracting_paths: list[str],
    gold_diff: str,
    gemini_key: str,
) -> list[dict]:
    """Call 3: Extract distractor rules from distracting config files."""
    if not distracting_paths:
        return []

    file_contents = []
    for path in distracting_paths:
        if path in config_files:
            file_contents.append(f"### {path}\n{config_files[path][:2000]}")

    prompt = f"""Extract distractor rules from these config files — conventions that SEEM relevant
to this code change but the gold diff correctly IGNORES.

## Gold Diff
{gold_diff[:4000]}

## Distracting Config Files (with line numbers)
{chr(10).join(file_contents)[:8000]}

## What Makes a Good Distractor
A distractor is a rule from a config file that an AI agent might mistakenly follow when working
on this specific change, but doing so would be WRONG because:
- The rule applies to a DIFFERENT scope/package/language than the changed files
- Following it would BREAK the code or architecture
- It mentions similar concepts (same technology, similar names) but for a different purpose
- It conflicts with the specific requirements of this change

For each distractor:
1. Use EXACT line numbers from the numbered content
2. Quote the source text verbatim
3. Explain WHY an agent might follow this (the trap)
4. Rate severity: high (would cause bug), medium (wasted effort), low (minor confusion)"""

    resp = call_gemini(prompt, gemini_key, schema=EXTRACT_DISTRACTOR_SCHEMA,
                       temperature=0.1, max_tokens=8192)
    if isinstance(resp, str):
        return json.loads(resp)
    if isinstance(resp, list):
        return resp
    return []


# ── Task processing ──────────────────────────────────────────────────────────

def get_task_info(task_path: Path) -> tuple[str, str, str]:
    """Extract repo, commit, and gold diff from task."""
    df = task_path / "environment" / "Dockerfile"
    if not df.exists():
        return "", "", ""
    df_text = df.read_text()

    repo = ""
    match = re.search(r"github\.com/([^/]+/[^\s.]+?)(?:\.git|[\s]|$)", df_text)
    if match:
        repo = match.group(1)

    commit = ""
    for pat in [r"git checkout\s+([a-f0-9]{7,40})", r"ARG\s+BASE_COMMIT=([a-f0-9]{7,40})"]:
        m = re.search(pat, df_text)
        if m:
            commit = m.group(1)
            break

    gold_diff = ""
    solve = task_path / "solution" / "solve.sh"
    if solve.exists():
        text = solve.read_text()
        match = re.search(r"(diff --git.*?)(?:\nPATCH|\nEOF|\Z)", text, re.DOTALL)
        if match:
            gold_diff = match.group(1)

    return repo, commit, gold_diff


def clone_shallow(repo: str, commit: str, cache_dir: Path) -> Path | None:
    """Shallow clone at specific commit."""
    repo_dir = cache_dir / repo.replace("/", "_")
    if repo_dir.exists() and (repo_dir / ".git").exists():
        try:
            r = subprocess.run(["git", "cat-file", "-t", commit],
                               capture_output=True, text=True, cwd=repo_dir, timeout=5)
            if r.returncode == 0:
                subprocess.run(["git", "checkout", commit],
                               capture_output=True, text=True, cwd=repo_dir, timeout=30)
                return repo_dir
        except Exception:
            pass
        # Fetch this commit
        try:
            subprocess.run(["git", "fetch", "--depth=1", "origin", commit],
                           capture_output=True, text=True, cwd=repo_dir, timeout=120)
            subprocess.run(["git", "checkout", commit],
                           capture_output=True, text=True, cwd=repo_dir, timeout=30)
            return repo_dir
        except Exception:
            pass

    repo_dir.mkdir(parents=True, exist_ok=True)
    try:
        if not (repo_dir / ".git").exists():
            subprocess.run(["git", "init", str(repo_dir)],
                           capture_output=True, text=True, timeout=10, check=True)
            subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{repo}.git"],
                           capture_output=True, text=True, cwd=repo_dir, timeout=10, check=True)
        subprocess.run(["git", "fetch", "--depth=1", "origin", commit],
                       capture_output=True, text=True, cwd=repo_dir, timeout=300, check=True)
        subprocess.run(["git", "checkout", commit],
                       capture_output=True, text=True, cwd=repo_dir, timeout=60, check=True)
        return repo_dir
    except Exception as e:
        print(f"  Clone failed: {repo}@{commit[:10]}: {e}")
        return None


def process_task(
    task_path: Path,
    gemini_key: str,
    repo_cache: dict[str, Path],
    cache_dir: Path,
    replace: bool = False,
) -> dict:
    """Process one task through the 3-call Gemini pipeline."""
    task_name = task_path.name
    result = {
        "task": task_name,
        "status": "error",
        "config_files": 0,
        "relevant": 0,
        "distracting": 0,
        "rubrics_added": 0,
        "distractors_added": 0,
        "error": "",
        "time": 0,
    }
    t0 = time.monotonic()

    repo, commit, gold_diff = get_task_info(task_path)
    if not repo or not commit:
        result["error"] = "no repo/commit"
        result["time"] = time.monotonic() - t0
        return result
    if not gold_diff:
        result["error"] = "no gold diff"
        result["time"] = time.monotonic() - t0
        return result

    # Clone repo
    repo_dir = repo_cache.get(repo)
    if not repo_dir:
        repo_dir = clone_shallow(repo, commit, cache_dir)
        if not repo_dir:
            result["error"] = "clone failed"
            result["time"] = time.monotonic() - t0
            return result
        repo_cache[repo] = repo_dir
    else:
        try:
            subprocess.run(["git", "checkout", commit],
                           capture_output=True, text=True, cwd=repo_dir, timeout=30)
        except Exception:
            pass

    # Find and number config files
    config_paths = find_config_files(repo_dir)
    if not config_paths:
        result["error"] = "no config files"
        result["time"] = time.monotonic() - t0
        return result
    result["config_files"] = len(config_paths)

    config_files = {}
    for cp in config_paths:
        try:
            content = (repo_dir / cp).read_text()
            config_files[cp] = number_lines(content)
        except Exception:
            pass

    if not config_files:
        result["error"] = "no readable config files"
        result["time"] = time.monotonic() - t0
        return result

    # Call 1: Classify
    try:
        classifications = classify_config_files(config_files, gold_diff, gemini_key)
    except Exception as e:
        result["error"] = f"classify: {str(e)[:100]}"
        result["time"] = time.monotonic() - t0
        return result

    classified_paths = {c["path"] for c in classifications}
    relevant_paths = [c["path"] for c in classifications if c.get("classification") == "relevant"]
    distracting_paths = [c["path"] for c in classifications if c.get("classification") == "distracting"]

    # Force root CLAUDE.md/AGENTS.md as relevant if Gemini dropped or misclassified them
    for cp in config_files:
        basename = cp.split("/")[-1]
        if basename in ("CLAUDE.md", "AGENTS.md") and "/" not in cp:
            if cp not in classified_paths or cp not in relevant_paths + distracting_paths:
                relevant_paths.append(cp)
    result["relevant"] = len(relevant_paths)
    result["distracting"] = len(distracting_paths)

    # Call 2: Extract rubric rules
    rubric_rules = []
    if relevant_paths:
        try:
            rubric_rules = extract_rubric_rules(config_files, relevant_paths, gold_diff, gemini_key)
        except Exception as e:
            result["error"] = f"extract_rubric: {str(e)[:100]}"

    # Call 3: Extract distractors
    distractor_rules = []
    if distracting_paths:
        try:
            distractor_rules = extract_distractor_rules(config_files, distracting_paths, gold_diff, gemini_key)
        except Exception as e:
            result["error"] = f"extract_distractor: {str(e)[:100]}"

    # Merge into manifest
    manifest_path = task_path / "eval_manifest.yaml"
    if not manifest_path.exists():
        result["error"] = "no manifest"
        result["time"] = time.monotonic() - t0
        return result

    m = yaml.safe_load(manifest_path.read_text())
    if not m:
        result["error"] = "bad manifest"
        result["time"] = time.monotonic() - t0
        return result

    existing_rubric = m.get("rubric", []) or []
    existing_distractors = m.get("distractors", []) or []

    existing_rule_keys = {
        r.get("rule", "")[:50].lower().strip()
        for r in existing_rubric if isinstance(r, dict)
    }
    existing_dist_keys = {
        d.get("rule", "")[:50].lower().strip()
        for d in existing_distractors if isinstance(d, dict)
    }

    # Convert and dedup rubric rules
    new_rubrics = []
    for r in rubric_rules:
        rule_text = r.get("rule", "")
        if not rule_text or len(rule_text) < 15:
            continue
        if rule_text[:50].lower().strip() in existing_rule_keys:
            continue
        existing_rule_keys.add(rule_text[:50].lower().strip())

        # Verify file exists
        src_path = r.get("source_path", "")
        if src_path and not (repo_dir / src_path).exists():
            continue

        new_rubrics.append({
            "rule": rule_text,
            "source": {
                "path": src_path,
                "lines": f"{r.get('start_line', '')}-{r.get('end_line', '')}",
            },
            "source_text": r.get("source_text", ""),
            "evidence": r.get("evidence_in_gold", ""),
            "category": r.get("category", ""),
            "verification": "llm_judge",
        })

    # Convert and dedup distractor rules
    new_distractors = []
    for d in distractor_rules:
        rule_text = d.get("rule", "")
        if not rule_text or len(rule_text) < 15:
            continue
        if rule_text[:50].lower().strip() in existing_dist_keys:
            continue
        existing_dist_keys.add(rule_text[:50].lower().strip())

        src_path = d.get("source_path", "")
        if src_path and not (repo_dir / src_path).exists():
            continue

        new_distractors.append({
            "rule": rule_text,
            "source": {
                "path": src_path,
                "lines": f"{d.get('start_line', '')}-{d.get('end_line', '')}",
            },
            "source_text": d.get("source_text", ""),
            "collision_type": d.get("collision_type", "scope_ambiguity"),
            "why_distracting": d.get("why_distracting", ""),
            "severity": d.get("severity", "medium"),
        })

    if new_rubrics or new_distractors:
        if replace:
            # Keep non-source_text rules (existing Gemini/manual), replace source_text ones
            m["rubric"] = [r for r in existing_rubric if not r.get("source_text")] + new_rubrics
            m["distractors"] = [d for d in existing_distractors if not d.get("source_text")] + new_distractors
        else:
            m["rubric"] = existing_rubric + new_rubrics
            m["distractors"] = existing_distractors + new_distractors

        manifest_path.write_text(
            yaml.dump(m, default_flow_style=False, sort_keys=False, allow_unicode=True)
        )

    result["rubrics_added"] = len(new_rubrics)
    result["distractors_added"] = len(new_distractors)
    result["status"] = "ok" if (new_rubrics or new_distractors) else "no_new_rules"
    result["time"] = time.monotonic() - t0
    return result


# ── Scanning ─────────────────────────────────────────────────────────────────

def scan_all_tasks() -> list[Path]:
    """Find all tasks with valid structure."""
    tasks = []
    for base in ["harbor_tasks", "harbor_tasks_agentmd_edits"]:
        base_path = ROOT / base
        if not base_path.exists():
            continue
        for task in sorted(base_path.iterdir()):
            if not task.is_dir():
                continue
            if all((task / p).exists() for p in [
                "eval_manifest.yaml", "environment/Dockerfile", "solution/solve.sh"
            ]):
                tasks.append(task)
    return tasks


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Overnight Gemini rubric extraction")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--replace", action="store_true",
                        help="Replace existing Codex/Gemini rules (vs merge)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--cache-dir", type=str, default="/tmp/repo_cache")
    parser.add_argument("--repo", type=str, default=None, help="Filter to specific repo")
    args = parser.parse_args()

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key and not args.dry_run:
        print("GEMINI_API_KEY not set. Run: set -a && source .env && set +a")
        sys.exit(1)

    tasks = scan_all_tasks()
    if args.repo:
        tasks = [t for t in tasks if args.repo in str(t)]
    tasks = tasks[args.offset:]
    if args.limit:
        tasks = tasks[:args.limit]

    # Filter to tasks with extractable diffs and repo/commit
    eligible = []
    for t in tasks:
        repo, commit, diff = get_task_info(t)
        if repo and commit and diff:
            eligible.append(t)

    print(f"Total tasks: {len(tasks)}, Eligible (have diff+repo): {len(eligible)}")

    if args.dry_run:
        for t in eligible[:30]:
            repo, commit, diff = get_task_info(t)
            print(f"  {t.parent.name}/{t.name} repo={repo} diff={len(diff)}chars")
        if len(eligible) > 30:
            print(f"  ... and {len(eligible) - 30} more")
        return

    cache_dir = Path(args.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    repo_cache: dict[str, Path] = {}

    results = []
    t_start = time.monotonic()
    processed = 0

    # Process sequentially (Gemini rate limits are the bottleneck, not I/O)
    for task in eligible:
        processed += 1
        task_name = task.name
        print(f"[{processed}/{len(eligible)}] {task_name}")

        result = process_task(task, gemini_key, repo_cache, cache_dir, replace=args.replace)
        results.append(result)

        if result["status"] == "ok":
            print(f"  OK: +{result['rubrics_added']}R +{result['distractors_added']}D "
                  f"(files={result['config_files']}, rel={result['relevant']}, "
                  f"dist={result['distracting']}) [{result['time']:.1f}s]")
        elif result["status"] == "no_new_rules":
            print(f"  SKIP: no new rules [{result['time']:.1f}s]")
        else:
            print(f"  ERROR: {result['error'][:80]}")

        time.sleep(0.5)  # Rate limit

    elapsed = time.monotonic() - t_start

    # Summary
    ok = sum(1 for r in results if r["status"] == "ok")
    no_new = sum(1 for r in results if r["status"] == "no_new_rules")
    errors = sum(1 for r in results if r["status"] == "error")
    total_r = sum(r["rubrics_added"] for r in results)
    total_d = sum(r["distractors_added"] for r in results)

    print()
    print("=" * 70)
    print(f"  OVERNIGHT GEMINI RUBRIC EXTRACTION")
    print(f"  Processed:     {len(results)}")
    print(f"  Updated:       {ok}")
    print(f"  No new rules:  {no_new}")
    print(f"  Errors:        {errors}")
    print(f"  +Rubrics:      {total_r}")
    print(f"  +Distractors:  {total_d}")
    print(f"  Time:          {elapsed:.1f}s ({elapsed / 60:.1f}m)")
    print("=" * 70)

    # Save log
    ts = time.strftime("%Y%m%d_%H%M%S")
    log_file = ROOT / "pipeline_logs" / f"overnight_gemini_{ts}.json"
    log_file.parent.mkdir(exist_ok=True)
    log_file.write_text(json.dumps(results, indent=2))
    print(f"\nResults: {log_file}")


if __name__ == "__main__":
    main()
