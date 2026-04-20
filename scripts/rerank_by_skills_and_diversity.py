#!/usr/bin/env python3
"""
Re-rank prefiltered accepts with:
  1. License filter — keep only permissive OSS (MIT, Apache-2.0, BSD, ISC, etc.)
  2. Skill-count boost — more .claude/skills/*/SKILL.md = stronger research signal
  3. Per-repo cap — no repo contributes more than --cap PRs (prevents over-concentration)

Reads prefiltered_accepted.jsonl, writes prefiltered_accepted_reranked.jsonl.

Fetches repo-level metadata (license, skill files) once per unique repo via gh
CLI. Caches to repo_metadata_cache.jsonl so re-runs are free.

Usage:
  .venv/bin/python scripts/rerank_by_skills_and_diversity.py \
      --input prefiltered_accepted.jsonl \
      --output prefiltered_accepted_reranked.jsonl \
      --cap 8 --concurrency 10
"""
from __future__ import annotations
import argparse, asyncio, concurrent.futures, json, re, subprocess, sys, time
from collections import Counter, defaultdict
from pathlib import Path

# SPDX identifiers for permissive open-source licenses we accept.
PERMISSIVE_LICENSES = {
    "MIT", "MIT-0",
    "Apache-2.0",
    "BSD-2-Clause", "BSD-3-Clause", "BSD-3-Clause-Clear", "0BSD",
    "ISC",
    "Unlicense",
    "CC0-1.0",
    "Zlib",
    "BlueOak-1.0.0",
    # Dual-licensed MIT+Apache is common in Rust, counted as permissive
    "Apache-2.0 OR MIT",
}

# Repos the user flagged NOT to over-index on. Keep, but cap hard.
DOMINANT_REPOS_CAP = {
    "openclaw/openclaw": 3,
    "anomalyco/opencode": 3,
    # Add others we want to specifically limit
}


def fetch_repo_meta(repo: str) -> dict:
    """Fetch license + SKILL.md count for a repo. Returns dict with keys:
    license_spdx, skill_count, skill_paths, repo_err."""
    out = {"repo": repo, "license_spdx": None, "skill_count": 0, "skill_paths": [], "repo_err": None}
    # 1. License
    try:
        r = subprocess.run(
            ["gh", "api", f"repos/{repo}", "--jq", ".license.spdx_id // \"NONE\""],
            capture_output=True, text=True, timeout=30, check=True,
        )
        out["license_spdx"] = r.stdout.strip()
    except Exception as e:
        out["repo_err"] = f"license: {str(e)[:100]}"
        return out
    # 2. Default branch tree → count SKILL.md files
    try:
        r = subprocess.run(
            ["gh", "api", f"repos/{repo}",
             "--jq", ".default_branch"],
            capture_output=True, text=True, timeout=30, check=True,
        )
        default_branch = r.stdout.strip()
        r = subprocess.run(
            ["gh", "api", f"repos/{repo}/git/trees/{default_branch}?recursive=1",
             "--jq", "[.tree[] | select(.path | test(\"\\\\.claude/skills/.*/SKILL\\\\.md$\")) | .path]"],
            capture_output=True, text=True, timeout=60, check=True,
        )
        paths = json.loads(r.stdout.strip())
        out["skill_count"] = len(paths)
        out["skill_paths"] = paths[:20]
    except Exception as e:
        # Non-fatal — repo just has 0 skills
        out["skill_count"] = 0
    return out


def load_cache(path: Path) -> dict[str, dict]:
    cache = {}
    if path.exists():
        with path.open() as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    cache[obj["repo"]] = obj
                except Exception:
                    continue
    return cache


async def fetch_all_repo_meta(repos: list[str], cache_path: Path, concurrency: int) -> dict[str, dict]:
    cache = load_cache(cache_path)
    todo = [r for r in repos if r not in cache or cache[r].get("repo_err")]
    print(f"Repos total: {len(repos)} | cached: {len(repos)-len(todo)} | fetching: {len(todo)}")

    if not todo:
        return cache

    loop = asyncio.get_event_loop()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=concurrency * 2)
    loop.set_default_executor(executor)
    sem = asyncio.Semaphore(concurrency)
    cache_f = cache_path.open("a")
    done = 0
    t0 = time.monotonic()

    async def worker(repo: str):
        nonlocal done
        async with sem:
            meta = await loop.run_in_executor(None, fetch_repo_meta, repo)
        cache_f.write(json.dumps(meta) + "\n")
        cache_f.flush()
        cache[repo] = meta
        done += 1
        if done % 20 == 0:
            elapsed = time.monotonic() - t0
            print(f"  fetched {done}/{len(todo)} ({done/max(1,elapsed)*60:.0f}/min)")

    try:
        await asyncio.gather(*(worker(r) for r in todo))
    finally:
        cache_f.close()
    return cache


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="prefiltered_accepted.jsonl")
    p.add_argument("--output", default="prefiltered_accepted_reranked.jsonl")
    p.add_argument("--cache", default="repo_metadata_cache.jsonl")
    p.add_argument("--cap", type=int, default=8, help="Max PRs per repo (default 8)")
    p.add_argument("--concurrency", type=int, default=10)
    p.add_argument("--allow-non-permissive", action="store_true",
                   help="Keep non-permissive licenses (default drops them)")
    args = p.parse_args()

    # Load accepts
    accepts = []
    with open(args.input) as f:
        for line in f:
            try:
                obj = json.loads(line)
                if obj.get("pr_ref") and "#" in obj["pr_ref"]:
                    accepts.append(obj)
            except Exception:
                continue
    print(f"Loaded {len(accepts)} accepts from {args.input}")

    # Unique repos
    repos = sorted({a["pr_ref"].split("#")[0] for a in accepts})
    print(f"Unique repos: {len(repos)}")

    # Fetch metadata
    cache_path = Path(args.cache)
    meta = asyncio.run(fetch_all_repo_meta(repos, cache_path, args.concurrency))

    # Enrich accepts with repo metadata
    for a in accepts:
        repo = a["pr_ref"].split("#")[0]
        m = meta.get(repo, {})
        a["license_spdx"] = m.get("license_spdx", "NONE")
        a["skill_count"] = m.get("skill_count", 0)
        a["skill_paths"] = m.get("skill_paths", [])

    # License filter
    before = len(accepts)
    if not args.allow_non_permissive:
        accepts = [a for a in accepts if a["license_spdx"] in PERMISSIVE_LICENSES]
    print(f"After license filter (permissive only): {len(accepts)}/{before}")
    drops_by_license = Counter(a["license_spdx"] or "NONE" for a in [
        x for x in accepts if x["license_spdx"] not in PERMISSIVE_LICENSES])

    # Compute new priority:
    # base + skill boost + hierarchy boost
    for a in accepts:
        base = float(a.get("priority_score") or 0.5)
        skill_boost = min(a["skill_count"], 10) * 0.05   # cap at 0.5
        # Bonus if PR is code_plus_config (track 2)
        config_boost = 0.2 if a.get("task_class") == "code_plus_config" else 0
        a["final_priority"] = round(base + skill_boost + config_boost, 3)

    # Sort by final priority desc
    accepts.sort(key=lambda a: -a["final_priority"])

    # Per-repo cap (prevents over-indexing)
    per_repo_count: dict[str, int] = defaultdict(int)
    kept = []
    dropped_by_cap = Counter()
    for a in accepts:
        repo = a["pr_ref"].split("#")[0]
        cap = DOMINANT_REPOS_CAP.get(repo, args.cap)
        if per_repo_count[repo] >= cap:
            dropped_by_cap[repo] += 1
            continue
        per_repo_count[repo] += 1
        kept.append(a)

    # Write output
    with open(args.output, "w") as f:
        for a in kept:
            f.write(json.dumps({
                "pr_ref": a["pr_ref"],
                "priority_score": a["final_priority"],
                "license": a["license_spdx"],
                "skill_count": a["skill_count"],
                "task_class": a.get("task_class"),
            }) + "\n")

    # Report
    print(f"\n=== Output: {args.output} ===")
    print(f"  kept: {len(kept)} PRs from {len(set(per_repo_count))} repos")
    print(f"  cap drops: {sum(dropped_by_cap.values())}")
    if dropped_by_cap:
        print(f"  over-cap repos (top 5): {dropped_by_cap.most_common(5)}")

    print(f"\n=== License distribution ===")
    for lic, n in Counter(a["license_spdx"] for a in kept).most_common(10):
        print(f"  {lic}: {n}")

    print(f"\n=== Skill-rich repos in output (top 10 by count) ===")
    repo_skill = {(a["pr_ref"].split("#")[0]): a["skill_count"] for a in kept}
    for r, s in sorted(repo_skill.items(), key=lambda x: -x[1])[:10]:
        n = per_repo_count[r]
        print(f"  {r}: skill_count={s}, n_prs={n}")

    print(f"\n=== Per-repo PR count (top 10) ===")
    for r, n in sorted(per_repo_count.items(), key=lambda x: -x[1])[:10]:
        print(f"  {r}: {n} PRs")


if __name__ == "__main__":
    main()
