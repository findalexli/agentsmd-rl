#!/usr/bin/env python3
"""Classify a repository as 'real-code' vs 'skill-collection'.

Heuristic: fetch the full file tree at HEAD, count files in the rule-file-only
namespace (`.claude/skills/*`, `**/SKILL.md`, etc.) vs. everything else, and
compare against a few name/description signals.

A repo is **real-code** if:
  - rule-files / total < 30 %, AND
  - it has at least 30 source-language files (.py, .ts, .js, .rs, .go, .java,
    .c, .cpp, .rb, .php, etc.), AND
  - its name does NOT match common collection patterns
    (`*-skills`, `*-templates`, `awesome-*`, `*-prompts`, `*-rules`)

Output is JSONL of `{repo, is_code_repo, rule_ratio, src_file_count, reason}`.

Usage:
    .venv/bin/python scripts/classify_repos_by_code_density.py \\
        --repos-file <one repo per line> \\
        --output /tmp/repo_classifications.jsonl
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

RULE_RE = re.compile(
    r"(?:^|/)("
    r"CLAUDE\.md|CLAUDE\.local\.md|AGENTS\.md|CONVENTIONS\.md|SKILL\.md|"
    r"\.cursorrules|\.windsurfrules|\.clinerules|\.continuerules"
    r")$|"
    r"^\.claude/(rules|skills|agents)/.+\.md$|"
    r"^\.cursor/rules/.+|"
    r"^\.github/(copilot-instructions\.md|skills/.+SKILL\.md|prompts/.+\.prompt\.md)$|"
    r"^\.agents?/skills/.+SKILL\.md$|"
    r"^\.opencode/skills/.+SKILL\.md$|"
    r"^\.codex/skills/.+SKILL\.md$|"
    r"\.mdc$",
    re.IGNORECASE,
)

SOURCE_EXTS = {
    ".py", ".pyx", ".pyi",
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".rs", ".go",
    ".java", ".kt", ".scala",
    ".c", ".cc", ".cpp", ".cxx", ".h", ".hpp",
    ".rb", ".php", ".cs", ".swift", ".m", ".mm",
    ".sh", ".bash", ".zsh",
    ".sql",
    ".vue", ".svelte",
}

COLLECTION_NAME_RE = re.compile(
    r"(?:^|[-_/])(awesome|skills?|agents|claude-code|claude-rules|"
    r"templates?|prompts?|cursor-rules|rules|workflows?)(?:[-_]|$)",
    re.IGNORECASE,
)


def fetch_tree(repo: str) -> list[str] | None:
    try:
        r = subprocess.run(
            ["gh", "api", f"repos/{repo}/git/trees/HEAD?recursive=1",
             "--jq", ".tree[]?.path"],
            capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            return None
        return r.stdout.splitlines()
    except Exception:
        return None


def fetch_meta(repo: str) -> dict | None:
    try:
        r = subprocess.run(
            ["gh", "api", f"repos/{repo}",
             "--jq", "{stars: .stargazers_count, desc: .description, "
                     "name: .name, archived: .archived, "
                     "primary_lang: .language, pushed_at: .pushed_at}"],
            capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            return None
        return json.loads(r.stdout)
    except Exception:
        return None


def classify(repo: str) -> dict:
    paths = fetch_tree(repo)
    meta = fetch_meta(repo) or {}
    if paths is None:
        return {"repo": repo, "is_code_repo": None,
                "reason": "tree_fetch_failed", **meta}
    total = len(paths)
    if total == 0:
        return {"repo": repo, "is_code_repo": False,
                "reason": "empty_tree", **meta}
    n_rule = sum(1 for p in paths if RULE_RE.search(p))
    n_src = sum(1 for p in paths if any(p.endswith(e) for e in SOURCE_EXTS))
    rule_ratio = n_rule / total
    name_signal = "name_looks_like_collection" if COLLECTION_NAME_RE.search(repo) else None

    is_code = (
        rule_ratio < 0.30
        and n_src >= 30
        and not name_signal
    )
    if is_code:
        reason = f"{rule_ratio:.0%} rules, {n_src} src files"
    else:
        bits = []
        if rule_ratio >= 0.30:
            bits.append(f"rules={rule_ratio:.0%}≥30%")
        if n_src < 30:
            bits.append(f"src={n_src}<30")
        if name_signal:
            bits.append(name_signal)
        reason = "; ".join(bits)
    return {
        "repo": repo,
        "is_code_repo": is_code,
        "rule_ratio": round(rule_ratio, 3),
        "src_file_count": n_src,
        "total_files": total,
        "reason": reason,
        **meta,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos-file", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--concurrency", type=int, default=20)
    args = ap.parse_args()

    repos = sorted({r.strip() for r in open(args.repos_file) if r.strip()
                    and "/" in r})
    print(f"Classifying {len(repos)} repos…", flush=True)
    out = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = {ex.submit(classify, r): r for r in repos}
        for i, fut in enumerate(as_completed(futs)):
            r = fut.result()
            out.append(r)
            if (i + 1) % 50 == 0:
                code = sum(1 for x in out if x.get("is_code_repo"))
                print(f"  [{i+1}/{len(repos)}] code-repos so far: {code}",
                      flush=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")

    by_class = {True: 0, False: 0, None: 0}
    for r in out:
        by_class[r.get("is_code_repo")] += 1
    print(f"\nClassification:")
    print(f"  code-repos:        {by_class[True]}")
    print(f"  skill-collections: {by_class[False]}")
    print(f"  unknown:           {by_class[None]}")


if __name__ == "__main__":
    main()
