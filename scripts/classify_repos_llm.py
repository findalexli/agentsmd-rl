#!/usr/bin/env python3
"""LLM-based repo classifier — distinguishes real-software repos from skill-only collections.

Replaces (or complements) `scripts/classify_repos_by_code_density.py` by using
Gemini 3.1 Pro with structured output to read each repo's *intent* signals
— description, README excerpt, recent commits, top-level file tree — and
classify accordingly. The regex-based classifier is kept as a free first pass.

Output is JSONL with one row per repo, suitable as a sidecar to scout JSONL or
as metadata appended to `eval_manifest.yaml`'s `task.repo_class` field.

Schema:
    {
      "repo": "owner/name",
      "class": "production_software" | "working_tool" | "skill_collection"
             | "fork_or_template" | "abandoned_or_demo",
      "purpose_one_line": "...",
      "skills_relationship": "primary_artifact" | "supporting_documentation" | "absent",
      "repo_created_at": "2024-09-13T...",
      "stars": int,
      "primary_language": str,
      "is_useful_for_benchmark": bool,   # class in {production_software, working_tool}
                                          #   AND skills_relationship == supporting_documentation
      "reason": "..."
    }

Usage:
    .venv/bin/python scripts/classify_repos_llm.py \\
        --repos-file <one-repo-per-line> \\
        --output /tmp/repo_class_llm.jsonl \\
        --concurrency 8
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_KEY:
    sys.exit("GEMINI_API_KEY required")

# Reuse the project's call_gemini helper (Standard/Flex with thinking budget,
# fallback retry, structured output).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from taskforge.gemini_rubric_constructor import call_gemini


CLASSIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "class": {
            "type": "string",
            "enum": [
                "production_software",
                "working_tool",
                "skill_collection",
                "fork_or_template",
                "abandoned_or_demo",
            ],
        },
        "purpose_one_line": {
            "type": "string",
            "description": "One sentence describing what this repository is for.",
        },
        "skills_relationship": {
            "type": "string",
            "enum": ["primary_artifact", "supporting_documentation", "absent"],
            "description": (
                "primary_artifact = the SKILL.md/AGENTS.md files ARE what this "
                "repo distributes. supporting_documentation = the rule files "
                "are documentation for actual software the repo ships. absent "
                "= no rule files."
            ),
        },
        "reason": {
            "type": "string",
            "description": "<= 30 words explaining the classification.",
        },
    },
    "required": ["class", "purpose_one_line", "skills_relationship", "reason"],
    "propertyOrdering": ["class", "purpose_one_line", "skills_relationship", "reason"],
}


def gh_json(cmd: list[str], timeout: int = 30):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            return None
        return json.loads(r.stdout) if r.stdout else None
    except Exception:
        return None


def fetch_meta(repo: str) -> dict:
    """One gh-api call returning everything the LLM will need."""
    raw = gh_json([
        "gh", "api", f"repos/{repo}",
        "--jq", "{name, description, stars: .stargazers_count, "
                "fork: .fork, archived: .archived, "
                "language, created_at, pushed_at, "
                "open_issues: .open_issues_count, "
                "homepage}"]) or {}
    return raw


def fetch_tree(repo: str, max_paths: int = 60) -> list[str]:
    """Top-level file tree (one network call)."""
    raw = gh_json([
        "gh", "api", f"repos/{repo}/git/trees/HEAD?recursive=1",
        "--jq", ".tree[]?.path"], timeout=30)
    if not raw:
        return []
    if isinstance(raw, list):
        paths = [str(x) for x in raw]
    elif isinstance(raw, str):
        paths = raw.splitlines()
    else:
        return []
    return paths[:max_paths]


def fetch_recent_commits(repo: str, limit: int = 8) -> list[str]:
    raw = gh_json([
        "gh", "api", f"repos/{repo}/commits",
        "-F", f"per_page={limit}",
        "--jq", ".[] | .commit.message | split(\"\\n\")[0]"])
    if not raw:
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw][:limit]
    if isinstance(raw, str):
        return raw.splitlines()[:limit]
    return []


def fetch_readme(repo: str, max_chars: int = 1500) -> str:
    raw = subprocess.run(
        ["gh", "api", f"repos/{repo}/readme",
         "--jq", ".content"],
        capture_output=True, text=True, timeout=20)
    if raw.returncode != 0 or not raw.stdout:
        return ""
    import base64
    try:
        text = base64.b64decode(raw.stdout.strip().strip('"')).decode(
            "utf-8", errors="replace")
        return text[:max_chars]
    except Exception:
        return ""


def build_prompt(repo: str, meta: dict, tree: list[str],
                 commits: list[str], readme: str) -> str:
    paths = "\n".join(f"  - {p}" for p in tree[:60]) or "  (empty)"
    commits_block = "\n".join(f"  - {c}" for c in commits) or "  (none)"
    return f"""You are classifying a GitHub repository into one of five categories. Use the metadata below — name, description, README excerpt, recent commit messages, top-level paths.

## Categories

- **production_software**: A real software product / library / framework with users beyond the author. Ships releases, has issues being filed by users, primary artifact is runnable code. Rule files (CLAUDE.md / AGENTS.md / SKILL.md) here are documentation for the team's coding work, not the product itself.
- **working_tool**: Smaller but functional code project — a CLI, plugin, integration, or library. Real code that runs, used by someone. Same rule-file role as above.
- **skill_collection**: The repo's *primary purpose* is to curate, distribute, or showcase Claude Code skills, agent prompts, or rule files. The "code" (if any) is helper scripts attached to skills. Rule files ARE the artifact.
- **fork_or_template**: A fork of an upstream project or a starter template; original work isn't really here.
- **abandoned_or_demo**: Started, didn't go anywhere, or is a personal demo / sandbox / weekend project with no real users.

## skills_relationship
- **primary_artifact** — rule files are what the repo distributes
- **supporting_documentation** — rule files document software the repo ships
- **absent** — no rule files

## The repo

Repo: {repo}
Stars: {meta.get('stars', 0)}
Description: {meta.get('description') or '(none)'}
Primary language: {meta.get('language') or '(none)'}
Homepage: {meta.get('homepage') or '(none)'}
Created: {meta.get('created_at', 'unknown')}
Last push: {meta.get('pushed_at', 'unknown')}
Open issues: {meta.get('open_issues', 0)}
Fork: {meta.get('fork', False)}
Archived: {meta.get('archived', False)}

### Top-level file tree (first 60 paths)
{paths}

### Recent commit messages
{commits_block}

### README excerpt (first 1500 chars)
```
{readme[:1500] or '(empty)'}
```

Output JSON only.
"""


def classify_one(repo: str, bundle: dict | None = None) -> dict:
    """Classify a repo. If `bundle` is provided (from batch_repo_bundle), use
    its meta/tree/commits/readme directly (skips per-repo REST). Otherwise
    falls back to the legacy 4-REST-call path."""
    if bundle:
        meta = bundle.get("meta") or {}
        tree = bundle.get("tree") or []
        commits = bundle.get("commits") or []
        readme = bundle.get("readme") or ""
        # Normalize key names: GraphQL gives stars/primaryLanguage/createdAt,
        # legacy build_prompt expects stars/language/created_at.
        meta = {**meta,
                "language": meta.get("primaryLanguage"),
                "created_at": meta.get("createdAt", ""),
                "archived": meta.get("isArchived", False),
                "fork": meta.get("isFork", False)}
    else:
        meta = fetch_meta(repo)
        tree = fetch_tree(repo)
        commits = fetch_recent_commits(repo)
        readme = fetch_readme(repo)
    prompt = build_prompt(repo, meta, tree, commits, readme)
    res = call_gemini(prompt, GEMINI_KEY,
                      schema=CLASSIFY_SCHEMA, temperature=0.1,
                      max_tokens=1024, service_tier="standard",
                      thinking_budget=512)
    if "error" in res:
        return {"repo": repo, "class": None, "reason": f"gemini_err:{res.get('error','')[:30]}"}
    is_useful = (
        res.get("class") in ("production_software", "working_tool")
        and res.get("skills_relationship") == "supporting_documentation"
    )
    return {
        "repo": repo,
        "class": res.get("class"),
        "purpose_one_line": res.get("purpose_one_line", ""),
        "skills_relationship": res.get("skills_relationship", ""),
        "repo_created_at": meta.get("created_at", ""),
        "stars": meta.get("stars", 0),
        "primary_language": meta.get("language", ""),
        "archived": meta.get("archived", False),
        "is_useful_for_benchmark": is_useful,
        "reason": res.get("reason", ""),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos-file", type=Path, required=True,
                    help="One repo per line (owner/name)")
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--concurrency", type=int, default=8)
    args = ap.parse_args()

    repos = sorted({r.strip() for r in open(args.repos_file)
                    if r.strip() and "/" in r})
    print(f"Classifying {len(repos)} repos via Gemini Standard…", flush=True)

    # Single batched GraphQL fetch for all repo bundles (meta+tree+commits+
    # readme) — replaces 4×N REST calls with N/25 GraphQL calls.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from taskforge.gh_graphql import batch_repo_bundle
    print(f"Batched GraphQL bundle fetch for {len(repos)} repos…", flush=True)
    bundles = batch_repo_bundle(repos)
    n_with_data = sum(1 for r in repos if bundles.get(r))
    print(f"  bundle data resolved for {n_with_data}/{len(repos)} repos",
          flush=True)

    out: list[dict] = []
    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = {ex.submit(classify_one, r, bundles.get(r)): r for r in repos}
        for i, fut in enumerate(as_completed(futs)):
            r = fut.result()
            out.append(r)
            if (i + 1) % 25 == 0:
                rate = (i + 1) / (time.monotonic() - started)
                print(f"  [{i+1}/{len(repos)}] {rate:.1f}/s", flush=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")

    # Summary
    counts: dict[str, int] = {}
    useful = 0
    for r in out:
        c = r.get("class") or "ERROR"
        counts[c] = counts.get(c, 0) + 1
        if r.get("is_useful_for_benchmark"):
            useful += 1
    print(f"\n=== Classification summary ===")
    for c, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {c:25} {n}")
    print(f"  is_useful_for_benchmark = true: {useful}")


if __name__ == "__main__":
    main()
