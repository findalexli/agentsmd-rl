#!/usr/bin/env python3
"""Causal markdown-relevance judge.

For each task, ask Gemini: would the agent's solution differ if the
markdown files (CLAUDE.md / AGENTS.md / .claude/rules/* / .cursorrules / etc.)
were removed from the repo BEFORE the agent saw the task?

If NO  → markdown is decorative; task does not test markdown-following.
If YES → markdown is load-bearing; task is a real markdown task.

Inputs assembled per task (Gemini handles long context):
- instruction.md (what the agent reads)
- solve.sh      (the gold solution)
- The actual markdown files referenced in eval_manifest.yaml `rubric:` source paths
- The agent_config check descriptions

Output JSON:
{
  "verdict": "load_bearing" | "decorative",
  "reason": "one short sentence",
  "evidence": ["...", "..."],
  "confidence": 0.0-1.0
}

Usage:
    .venv/bin/python scripts/markdown_causality_judge.py \\
        --corpus harbor_tasks/ \\
        --concurrency 8 \\
        --out /tmp/markdown_causality.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import httpx
import yaml
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
              "gemini-2.5-flash:generateContent")


JUDGE_PROMPT = """\
You judge whether a software-engineering task's gold solution is causally
dependent on the REPO'S agent-instruction markdown files. These are markdown
files committed in the repo BEFORE the task starts, e.g.:
- `CLAUDE.md`, `AGENTS.md`, `CONVENTIONS.md` (any directory)
- `.claude/rules/*.md`, `.claude/skills/*/SKILL.md`, `.claude/agents/*.md`
- `.cursorrules`, `.cursor/rules/`
- `.github/copilot-instructions.md`

DO NOT count the task's own `instruction.md` as a markdown — that is the
prompt given to the agent regardless. The question is about REPO files.

The test:
> Imagine we DELETED the listed REPO MARKDOWN FILES below before the agent
> looked at the repo. Would the gold solution still be the SAME correct fix?
>   - If YES (gold doesn't depend on those files) → verdict "decorative"
>   - If NO (gold needs those files to choose this specific fix) → verdict
>     "load_bearing"

LOAD_BEARING examples:
- Gold patch updates AGENTS.md/CLAUDE.md to document a new feature/rule
- Gold patch follows a naming/style/pattern rule that exists ONLY in repo's
  CLAUDE.md (e.g., "use single-word variable names", "no wildcard imports")
- Gold patch creates files at paths mandated by `.claude/rules/`
- Without the markdown, an equally-correct alternative fix would be plausible

DECORATIVE examples:
- Gold patch fixes a bug whose correct fix is fully determined by code/tests
- Repo markdowns contain only generic advice with no rule that constrains the gold
- Gold patch never touches markdown AND no rule from markdown predicts the choice

Be strict: if you cannot point to a SPECIFIC sentence in a REPO MARKDOWN
file (CLAUDE.md / AGENTS.md / .claude/* / etc., NOT instruction.md) that
predicts a SPECIFIC choice in the gold patch, the verdict is "decorative".

=== TASK INSTRUCTION (the agent's prompt — DOES NOT count as a markdown) ===
{instruction}

=== GOLD SOLUTION (solve.sh) ===
{solve_sh}

=== REPO MARKDOWN FILES (the only files that count for this judgment) ===
{markdowns}

=== agent_config CHECKS (link from a check to a markdown rule) ===
{checks}

=== RUBRIC RULES (rules supposedly mined from repo markdowns) ===
{rubric}

Output JSON. Keep `reason` ≤ 25 words. Each `evidence` item must cite a
specific repo markdown file (not instruction.md), ≤ 20 words.
"""


# ---------------------------------------------------------------------------
# Per-task prompt assembly
# ---------------------------------------------------------------------------


_MD_PATTERN = re.compile(
    r"(CLAUDE\.md|AGENTS\.md|CONVENTIONS\.md|SKILL\.md|"
    r"\.claude/.+\.md|\.cursor/.+\.md|\.cursorrules|"
    r"\.github/copilot-instructions\.md)",
    re.IGNORECASE,
)


def _find_repo_dir(task_dir: Path) -> Path | None:
    """Find the cloned repo dir for the task. Common locations:
    - <task>/repo/
    - <task>/<repo-name>/
    - <task>/environment/<repo-name>/
    Otherwise None — caller should fall back to fetching via gh.
    """
    # Try direct ./repo
    p = task_dir / "repo"
    if p.is_dir():
        return p
    # Look for any subdir containing a .git/
    for child in task_dir.iterdir():
        if child.is_dir() and (child / ".git").exists():
            return child
    # Look in environment/
    env = task_dir / "environment"
    if env.is_dir():
        for child in env.iterdir():
            if child.is_dir() and (child / ".git").exists():
                return child
    return None


# Persistent on-disk cache for fetched markdown content
_FETCH_CACHE_DIR = Path("/tmp/markdown_fetch_cache")
_FETCH_CACHE_DIR.mkdir(exist_ok=True, parents=True)


def _fetch_markdown_via_gh(repo: str, path: str, ref: str) -> str | None:
    """Fetch a single file from GitHub at a given commit ref.

    Caches by (repo, path, ref). Falls back to HEAD if ref is unreachable.
    """
    import hashlib, subprocess, base64
    key = hashlib.sha1(f"{repo}|{path}|{ref}".encode()).hexdigest()[:24]
    cache_file = _FETCH_CACHE_DIR / f"{key}.txt"
    if cache_file.exists():
        return cache_file.read_text(errors="ignore") or None

    def _try(commit_ref: str) -> str | None:
        try:
            url = f"repos/{repo}/contents/{path}"
            if commit_ref:
                url = f"{url}?ref={commit_ref}"
            r = subprocess.run(
                ["gh", "api", "-X", "GET", url, "--jq", ".content"],
                capture_output=True, text=True, timeout=15,
            )
            if r.returncode != 0 or not r.stdout.strip():
                return None
            content = base64.b64decode(
                r.stdout.strip().replace("\n", "")
            ).decode("utf-8", errors="ignore")
            return content
        except Exception:
            return None

    text = _try(ref) if ref else None
    if text is None:
        text = _try("HEAD")
    cache_file.write_text(text or "")
    return text


_DOCKERFILE_REPO_RE = re.compile(
    r"git\s+clone[^\n]*?(?:https://github\.com/|git@github\.com:)([\w.-]+/[\w.-]+?)(?:\.git)?\s",
    re.IGNORECASE,
)
_DOCKERFILE_CHECKOUT_RE = re.compile(r"git\s+checkout\s+([0-9a-f]{7,40})", re.IGNORECASE)


def _manifest_source(task_dir: Path) -> tuple[str | None, str | None]:
    """Return (owner/repo, base_commit) for fetching markdown from GitHub.

    Tries (in order):
    - eval_manifest.yaml: source.repo / source_pr.owner+repo / pr.owner+repo
    - environment/Dockerfile: parse `git clone https://github.com/o/r ... git checkout <sha>`
    """
    mp = task_dir / "eval_manifest.yaml"
    repo, base = None, None

    if mp.exists():
        try:
            m = yaml.safe_load(mp.read_text(errors="ignore")) or {}
            src = m.get("source")
            if isinstance(src, dict) and isinstance(src.get("repo"), str):
                repo = src.get("repo")
                base = src.get("base_commit") or src.get("commit")
            else:
                for key in ("source_pr", "pr", "source_repo"):
                    s = m.get(key)
                    if isinstance(s, dict):
                        owner = s.get("owner")
                        rname = s.get("repo") or s.get("name")
                        if owner and rname:
                            repo = f"{owner}/{rname}"
                            base = s.get("base_commit") or s.get("commit")
                            break
        except Exception:
            pass

    # Fall back to Dockerfile
    if repo is None:
        dockerfile = task_dir / "environment" / "Dockerfile"
        if dockerfile.exists():
            text = dockerfile.read_text(errors="ignore")
            m = _DOCKERFILE_REPO_RE.search(text)
            if m:
                repo = m.group(1)
            if base is None:
                m2 = _DOCKERFILE_CHECKOUT_RE.search(text)
                if m2:
                    base = m2.group(1)

    # Strip trailing .git
    if repo and repo.endswith(".git"):
        repo = repo[:-4]
    return repo, base


# Pattern matching repo-level instruction markdowns. Any tree path that matches
# one of these is fetched and shown to the judge.
_INSTRUCTION_PATH_RE = re.compile(
    r"(?:^|/)("
    r"CLAUDE\.md|AGENTS\.md|CONVENTIONS\.md|"
    r"\.cursorrules|"
    r"\.github/copilot-instructions\.md"
    r")$|"
    r"^\.claude/(?:rules|skills|agents)/.+\.md$|"
    r"^\.cursor/rules/.+",
    re.IGNORECASE,
)


def _list_instruction_markdowns(repo: str, ref: str) -> list[str]:
    """List instruction-style markdown paths in the repo.

    Strategy (cheapest first):
    1. Try recursive tree at base_commit, then at HEAD.
    2. If both fail (e.g., huge repo or unreachable commit), use code search:
       `repo:owner/repo filename:CLAUDE.md OR filename:AGENTS.md OR ...`

    Cached by repo (not commit) — markdowns rarely move.
    """
    import hashlib, subprocess
    key = hashlib.sha1(f"md_paths|{repo}".encode()).hexdigest()[:24]
    cache_file = _FETCH_CACHE_DIR / f"paths_{key}.json"
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text())
        except Exception:
            pass

    # Path 1: tree API
    def _try_tree(commit_ref: str) -> list[str] | None:
        r = subprocess.run(
            ["gh", "api", f"repos/{repo}/commits/{commit_ref}",
             "--jq", ".commit.tree.sha"],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode != 0 or not r.stdout.strip():
            return None
        tree_sha = r.stdout.strip()
        r2 = subprocess.run(
            ["gh", "api", f"repos/{repo}/git/trees/{tree_sha}",
             "-f", "recursive=1",
             "--jq", '[.tree[] | select(.type == "blob") | .path]'],
            capture_output=True, text=True, timeout=30,
        )
        if r2.returncode != 0:
            return None
        try:
            return json.loads(r2.stdout)
        except Exception:
            return None

    paths = (_try_tree(ref) if ref else None) or _try_tree("HEAD")

    if paths is not None:
        matched = [p for p in paths if _INSTRUCTION_PATH_RE.search(p)]
    else:
        # Path 2: code search
        # Build a single OR query covering common filenames
        query = (
            f"repo:{repo} "
            f"filename:CLAUDE.md OR filename:AGENTS.md OR "
            f"filename:CONVENTIONS.md OR filename:SKILL.md OR "
            f"filename:copilot-instructions.md OR filename:.cursorrules"
        )
        try:
            r = subprocess.run(
                ["gh", "api", f"search/code?q={query.replace(' ', '+')}",
                 "--jq", "[.items[].path]"],
                capture_output=True, text=True, timeout=30,
            )
            if r.returncode == 0:
                matched = json.loads(r.stdout) or []
            else:
                matched = []
        except Exception:
            matched = []

    cache_file.write_text(json.dumps(matched))
    return matched


def collect_markdown_text(task_dir: Path) -> tuple[str, list[str]]:
    """Collect the contents of all markdown files referenced by this task.

    Strategy: parse eval_manifest.yaml for source.path entries, fetch via
    gh api at the recorded base_commit (cached). Returns (combined_text,
    list_of_paths_used).
    """
    manifest_path = task_dir / "eval_manifest.yaml"
    if not manifest_path.exists():
        return "(no eval_manifest.yaml)", []
    try:
        manifest = yaml.safe_load(manifest_path.read_text(errors="ignore")) or {}
    except Exception:
        return "(unparseable eval_manifest.yaml)", []

    def _src_path(item):
        if not isinstance(item, dict):
            return None
        src = item.get("source")
        if isinstance(src, dict):
            return src.get("path")
        # Old format: free-text "source" — scan for embedded path
        if isinstance(src, str):
            m = _MD_PATTERN.search(src)
            if m:
                return m.group(1)
        return None

    paths: set[str] = set()
    for r in (manifest.get("rubric") or []):
        p = _src_path(r)
        if p:
            paths.add(p)
    for r in (manifest.get("distractors") or []):
        p = _src_path(r)
        if p:
            paths.add(p)
    for c in (manifest.get("checks") or []):
        if isinstance(c, dict) and c.get("origin") == "agent_config":
            p = _src_path(c)
            if p:
                paths.add(p)

    # Enumerate ALL instruction-style markdowns in the repo via tree API.
    # This catches cases where manifests don't cite paths and CLAUDE.md is
    # nested (e.g., .claude/CLAUDE.md, packages/foo/AGENTS.md).
    repo_slug, base = _manifest_source(task_dir)
    if repo_slug and base:
        for p in _list_instruction_markdowns(repo_slug, base):
            paths.add(p)

    # 1. Try local checked-out repo
    local_repo = _find_repo_dir(task_dir)
    chunks: list[str] = []
    used: list[str] = []
    seen: set[str] = set()

    for path in sorted(paths):
        # Local first
        text = None
        if local_repo:
            f = local_repo / path
            if f.exists() and f.is_file():
                text = f.read_text(errors="ignore")
        # Fall back to gh api
        if text is None:
            repo_slug, base = _manifest_source(task_dir)
            if repo_slug and base:
                text = _fetch_markdown_via_gh(repo_slug, path, base)
        if text is not None:
            chunks.append(f"## {path}\n```markdown\n{text[:8000]}\n```")
            used.append(path)
            seen.add(path)
        else:
            chunks.append(f"## {path}\n(NOT FOUND — could not fetch)")
            seen.add(path)

    if not chunks:
        return "(no markdown files referenced or available)", []
    return "\n\n".join(chunks), used


def collect_checks(task_dir: Path) -> str:
    manifest_path = task_dir / "eval_manifest.yaml"
    if not manifest_path.exists():
        return "(none)"
    try:
        manifest = yaml.safe_load(manifest_path.read_text(errors="ignore")) or {}
    except Exception:
        return "(unparseable)"
    out = []
    for c in (manifest.get("checks") or []):
        if isinstance(c, dict) and c.get("origin") == "agent_config":
            src = c.get("source") if isinstance(c.get("source"), dict) else {}
            out.append(f"- [{c.get('id')}] {c.get('description', '')} "
                       f"(source: {src.get('path','?')}:{src.get('lines','?')})")
    return "\n".join(out) if out else "(no agent_config checks)"


def collect_rubric(task_dir: Path) -> str:
    manifest_path = task_dir / "eval_manifest.yaml"
    if not manifest_path.exists():
        return "(none)"
    try:
        manifest = yaml.safe_load(manifest_path.read_text(errors="ignore")) or {}
    except Exception:
        return "(unparseable)"
    out = []
    for r in (manifest.get("rubric") or []):
        if isinstance(r, dict):
            src = r.get("source") if isinstance(r.get("source"), dict) else {}
            out.append(f"- {str(r.get('rule', ''))[:200]} "
                       f"(source: {src.get('path','?')}:{src.get('lines','?')})")
        elif isinstance(r, str):
            out.append(f"- {r[:200]}")
    return "\n".join(out) if out else "(no rubric rules)"


def build_prompt(task_dir: Path) -> tuple[str, list[str]] | None:
    instr = task_dir / "instruction.md"
    sv    = task_dir / "solution" / "solve.sh"
    if not instr.exists() or not sv.exists():
        return None
    instruction = instr.read_text(errors="ignore")[:6000]
    solve_sh    = sv.read_text(errors="ignore")[:12000]
    markdowns, used_paths = collect_markdown_text(task_dir)
    checks  = collect_checks(task_dir)
    rubric  = collect_rubric(task_dir)
    prompt = (JUDGE_PROMPT
              .replace("{instruction}", instruction)
              .replace("{solve_sh}", solve_sh)
              .replace("{markdowns}", markdowns)
              .replace("{checks}", checks)
              .replace("{rubric}", rubric))
    return prompt, used_paths


# ---------------------------------------------------------------------------
# Gemini call
# ---------------------------------------------------------------------------


_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "verdict":    {"type": "STRING", "enum": ["load_bearing", "decorative"]},
        "reason":     {"type": "STRING"},
        "evidence":   {"type": "ARRAY", "items": {"type": "STRING"}},
        "confidence": {"type": "NUMBER"},
    },
    "required": ["verdict", "reason"],
}


async def call_gemini(prompt: str, client: httpx.AsyncClient) -> dict | None:
    r = await client.post(
        f"{GEMINI_URL}?key={GEMINI_KEY}",
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 1024,
                "responseMimeType": "application/json",
                "responseSchema": _RESPONSE_SCHEMA,
                "thinkingConfig": {"thinkingBudget": 0},
            },
        },
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    parts = ((data.get("candidates") or [{}])[0]
             .get("content", {}).get("parts") or [{}])
    txt = parts[0].get("text", "")
    # Strip fences if any
    t = txt.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*\n", "", t)
        t = re.sub(r"\n```\s*$", "", t)
    try:
        return json.loads(t)
    except Exception:
        # Greedy fallback
        s, e = t.find("{"), t.rfind("}")
        if s == -1 or e == -1:
            return None
        try:
            return json.loads(t[s:e+1])
        except Exception:
            return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def judge_task(name: str, prompt: str, used_paths: list[str],
                     client: httpx.AsyncClient, sem: asyncio.Semaphore) -> dict:
    async with sem:
        out: dict[str, Any] = {"name": name, "used_paths": used_paths,
                               "verdict": None, "reason": "", "confidence": None,
                               "evidence": []}
        try:
            v = await call_gemini(prompt, client)
            if v and v.get("verdict") in ("load_bearing", "decorative"):
                out.update(v)
        except Exception as e:
            out["error"] = str(e)[:300]
        return out


async def main_async(args: argparse.Namespace) -> None:
    if args.tasks_file:
        names = [n.strip() for n in args.tasks_file.read_text().splitlines() if n.strip()]
    else:
        names = sorted(d.name for d in args.corpus.iterdir() if d.is_dir())

    print(f"Judging {len(names)} tasks with Gemini (concurrency={args.concurrency})…")
    sem = asyncio.Semaphore(args.concurrency)

    # Build all prompts up-front so we can fail fast on missing files
    prompts: list[tuple[str, str, list[str]]] = []
    skipped: list[dict] = []
    for n in names:
        tdir = args.corpus / n
        built = build_prompt(tdir)
        if built is None:
            skipped.append({"name": n, "verdict": "skip",
                            "reason": "missing instruction.md or solve.sh"})
            continue
        prompt, used = built
        prompts.append((n, prompt, used))

    print(f"  built prompts: {len(prompts)}, skipped: {len(skipped)}")

    results: list[dict] = list(skipped)
    completed = 0
    async with httpx.AsyncClient() as client:
        async def runner(n: str, p: str, used: list[str]) -> None:
            nonlocal completed
            r = await judge_task(n, p, used, client, sem)
            results.append(r)
            completed += 1
            verdict = r.get("verdict") or "ERR"
            mds = len(used)
            if completed % 25 == 0 or verdict == "ERR":
                print(f"  [{completed}/{len(prompts)}] {verdict:>13s} "
                      f"({mds} md) {n}")
            # Persist incrementally
            if completed % 50 == 0:
                args.out.write_text(json.dumps(results, indent=2))

        await asyncio.gather(*[runner(n, p, u) for n, p, u in prompts])

    args.out.write_text(json.dumps(results, indent=2))

    counts: dict[str, int] = {}
    for r in results:
        counts[r.get("verdict") or "error"] = counts.get(r.get("verdict") or "error", 0) + 1
    print("\n=== Summary ===")
    for k, v in sorted(counts.items()):
        print(f"  {k:>14s}: {v}")
    print(f"\nResults → {args.out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path("harbor_tasks"))
    ap.add_argument("--tasks-file", type=Path,
                    help="File with one task name per line (default: all in corpus)")
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--out", type=Path, default=Path("/tmp/markdown_causality.json"))
    args = ap.parse_args()

    if not GEMINI_KEY:
        sys.exit("GEMINI_API_KEY not set")

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
