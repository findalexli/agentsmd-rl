#!/usr/bin/env python3
"""Batch-mode causality judge for stub PRs.

Same 3-way verdict (load_bearing / decorative / unscaffoldable) as
audit_stub_full.py, but submitted as a single Gemini batch job:
50% cost discount, no rate-limit babysitting, up to 24h SLA but
typically completes within minutes.

Input modes (mutually exclusive):
  --from-jsonl <path>         New PRs from a scout output JSONL
                              (fields: repo, pr_number/pr/number, title)
  --recheck-class <CLASS>     Re-judge rows in /tmp/stub_pr_audit_full.csv
                              with class==CLASS (e.g., "ERR" or "C-unfetchable")

Output: appends to --out CSV (same schema as audit_stub_full.py:
        stub,repo,pr,class,reason,extra)
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import csv
import json
import os
import re
import sys
import time
from pathlib import Path

import httpx
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_KEY:
    sys.exit("GEMINI_API_KEY not set")

GH_TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
if not GH_TOKEN:
    import subprocess
    try:
        GH_TOKEN = subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    except Exception:
        pass

MODEL = "gemini-3.1-pro-preview-customtools"

TIER1_PATH_RE = re.compile(
    r"^(CLAUDE\.md|AGENTS\.md|CONVENTIONS\.md|\.cursorrules)$|"
    r"^\.cursor/rules/|^\.github/copilot-instructions\.md$|"
    r"^\.claude/(rules|skills|agents)/|"
    r"(^|/)SKILL\.md$|"
    r"^\.agents?/skills/|^\.opencode/skills/|^\.codex/skills/|"
    r"^\.github/skills/|^\.github/prompts/.*\.prompt\.md$"
)

JUDGE_PROMPT = """You judge whether a merged GitHub PR is suitable for an
agent-instruction-following benchmark task that runs on Linux Docker.

Three verdicts (output exactly one):

1. **load_bearing** — The PR's gold diff either edits an
   agent-instruction markdown file directly (CLAUDE.md / AGENTS.md /
   SKILL.md / .cursor/rules / etc.) OR specifically follows a rule from
   one. Removing the markdown would change the agent's solution.

2. **decorative** — The fix is determined by the bug itself; removing
   the markdown wouldn't change it. The repo has markdowns but they're
   either generic ("follow existing style") or unrelated to this PR.

3. **unscaffoldable** — Cannot become a valid Linux-Docker benchmark
   regardless of markdown causality. Common patterns:
   - **Platform-specific runtime**: paths matching `Android/`, `iOS/`,
     `macOS/`, `Windows/`, `WinUI`, `Cocoa`, `XCUI`, `UIKit`, or imports
     of `import AppleArchive` / `import androidx` / `using Microsoft.UI`
   - **GPU/special hardware**: `cuda/`, `gpu/`, `kernels/`, `triton/`,
     `.cu` files, `model_weights/`
   - **Massive cross-cutting refactor**: > 500 lines OR > 10 files
     spanning unrelated subsystems
   - **No testable behavior**: docs-only, CI-only, pure UI/CSS
   - **Needs secrets / cloud accounts / OAuth / paid services**

Be strict for "load_bearing": cite the SPECIFIC rule from the markdown
content provided. Generic rules ("follow existing style", "run linting")
do NOT qualify. Be aggressive for "unscaffoldable" only when concrete
evidence is in the diff. When in doubt between "decorative" and
"unscaffoldable", prefer "decorative".

Repo: {repo}
PR #{pr}

Repo's agent-instruction markdown files (sample):
---
{tier1_content}
---

Merged PR diff (truncated):
---
{diff_excerpt}
---

Output JSON only:
{{"verdict": "load_bearing"|"decorative"|"unscaffoldable", "reason": "<one short sentence>", "rule_cited": "<verbatim rule from markdown if load_bearing, else empty>"}}
"""


# ---------------------------------------------------------------------------
# GH helpers (concurrent prompt build phase)
# ---------------------------------------------------------------------------

def _gh_headers(diff: bool = False) -> dict:
    h = {"Accept": "application/vnd.github.v3.diff" if diff
         else "application/vnd.github.v3+json"}
    if GH_TOKEN:
        h["Authorization"] = f"token {GH_TOKEN}"
    return h


# Process-wide rate-limit guard. When a 403 / X-RateLimit-Remaining=0 is seen,
# all coroutines block on this event until the reset time passes.
_RATE_RESET_AT: float = 0.0
_RATE_LOCK = asyncio.Lock()


_LAST_RATE_LOG_AT: float = 0.0

async def _rate_limit_wait():
    """If we're in a rate-limit window, sleep until reset (cap 1h).

    Logs once per window even though many coroutines may hit it.
    """
    global _RATE_RESET_AT, _LAST_RATE_LOG_AT
    if _RATE_RESET_AT <= 0:
        return
    delay = _RATE_RESET_AT - time.time()
    if delay <= 0:
        _RATE_RESET_AT = 0.0
        return
    delay = min(delay + 5, 3600)
    if time.time() - _LAST_RATE_LOG_AT > 60:
        _LAST_RATE_LOG_AT = time.time()
        print(f"  [rate-limit] sleeping {delay:.0f}s until reset "
              f"(workers paused)", file=sys.stderr, flush=True)
    await asyncio.sleep(delay)
    _RATE_RESET_AT = 0.0


async def _gh_get(client: httpx.AsyncClient, url: str, *, diff: bool = False,
                  timeout: int = 30) -> httpx.Response | None:
    """GET with rate-limit awareness. Returns None on persistent failure."""
    global _RATE_RESET_AT
    for attempt in range(5):
        await _rate_limit_wait()
        try:
            r = await client.get(url, headers=_gh_headers(diff=diff),
                                  timeout=timeout)
        except (httpx.ReadError, httpx.ConnectError, httpx.TimeoutException,
                httpx.RemoteProtocolError, httpx.WriteError):
            await asyncio.sleep(2 + attempt * 2)
            continue
        # Track rate-limit headers from successful responses too
        remaining = r.headers.get("x-ratelimit-remaining")
        reset = r.headers.get("x-ratelimit-reset")
        if remaining and reset and int(remaining) <= 1:
            async with _RATE_LOCK:
                if _RATE_RESET_AT < int(reset):
                    _RATE_RESET_AT = float(reset)
        if r.status_code == 200:
            return r
        if r.status_code in (403, 429):
            # Primary or secondary rate limit
            if reset:
                async with _RATE_LOCK:
                    _RATE_RESET_AT = max(_RATE_RESET_AT, float(reset))
                await _rate_limit_wait()
            else:
                await asyncio.sleep(30 * (attempt + 1))
            continue
        if r.status_code in (502, 503, 504):
            await asyncio.sleep(2 ** attempt)
            continue
        # 404, 410, 422 etc. — not retryable
        return r
    return None


async def gh_pr_files(client: httpx.AsyncClient, repo: str, pr: int):
    r = await _gh_get(client, f"https://api.github.com/repos/{repo}/pulls/{pr}")
    if r is None or r.status_code != 200:
        return None, None
    base = r.json().get("base", {}).get("sha", "HEAD")
    r2 = await _gh_get(client,
        f"https://api.github.com/repos/{repo}/pulls/{pr}/files")
    if r2 is None or r2.status_code != 200:
        return base, []
    return base, [f["filename"] for f in r2.json()]


async def gh_content(client: httpx.AsyncClient, repo: str, path: str, ref: str) -> str:
    r = await _gh_get(client,
        f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}")
    if r is None or r.status_code != 200:
        return ""
    try:
        return base64.b64decode(r.json()["content"]).decode("utf-8", errors="replace")
    except Exception:
        return ""


async def gh_pr_diff(client: httpx.AsyncClient, repo: str, pr: int) -> str:
    r = await _gh_get(client,
        f"https://api.github.com/repos/{repo}/pulls/{pr}",
        diff=True, timeout=60)
    return r.text if (r is not None and r.status_code == 200) else ""


# ---------------------------------------------------------------------------
# Prompt build
# ---------------------------------------------------------------------------

def slugify(repo: str, title: str) -> str:
    repo_short = repo.split("/")[-1].lower()
    clean = re.sub(r"[^a-z0-9\s]", "", title.lower())
    words = clean.split()[:5]
    return f"{repo_short}-{('-'.join(words) or 'unnamed')}"[:60]


async def build_one(client: httpx.AsyncClient, sem: asyncio.Semaphore,
                    stub: str, repo: str, pr: int,
                    tier1_paths: list[str]) -> dict | None:
    """Returns row dict for class-A short-circuit, or {'prompt': ...} for batch.
    """
    async with sem:
        base, files = await gh_pr_files(client, repo, pr)
        if files is None:
            return {"stub": stub, "repo": repo, "pr": pr, "class": "ERR",
                    "reason": "pr fetch failed", "extra": ""}
        if not files:
            return {"stub": stub, "repo": repo, "pr": pr, "class": "ERR",
                    "reason": "empty files list", "extra": ""}

        # Class A: PR directly modifies a tier-1 markdown
        hit_paths = [p for p in files if TIER1_PATH_RE.search(p)]
        if hit_paths:
            return {"stub": stub, "repo": repo, "pr": pr, "class": "A",
                    "reason": "PR modifies tier-1 markdown directly",
                    "extra": ",".join(hit_paths)[:200]}

        # Fetch up to 2 tier-1 contents
        contents = []
        for p in tier1_paths[:2]:
            c = await gh_content(client, repo, p, base)
            if c:
                contents.append(f"=== {p} ===\n{c[:6000]}")
        if not contents:
            return {"stub": stub, "repo": repo, "pr": pr, "class": "C",
                    "reason": "tier-1 unfetchable; default decorative",
                    "extra": ""}

        diff = await gh_pr_diff(client, repo, pr)
        if not diff:
            return {"stub": stub, "repo": repo, "pr": pr, "class": "ERR",
                    "reason": "diff fetch failed", "extra": ""}

        prompt = JUDGE_PROMPT.format(
            repo=repo, pr=pr,
            tier1_content="\n\n".join(contents)[:10000],
            diff_excerpt=diff[:8000],
        )
        return {"stub": stub, "repo": repo, "pr": pr,
                "_prompt": prompt}  # marker → goes to batch


# ---------------------------------------------------------------------------
# Batch submit / poll
# ---------------------------------------------------------------------------

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "verdict":     {"type": "STRING",
                        "enum": ["load_bearing", "decorative", "unscaffoldable"]},
        "reason":      {"type": "STRING"},
        "rule_cited":  {"type": "STRING"},
    },
    "required": ["verdict", "reason"],
}


def write_batch_jsonl(path: Path, items: list[dict]):
    """Batch JSONL uses raw REST/camelCase format (not the SDK's snake_case)."""
    with path.open("w") as f:
        for item in items:
            req = {
                "key": item["stub"],
                "request": {
                    "contents": [{"parts": [{"text": item["_prompt"]}]}],
                    "generationConfig": {
                        "temperature": 0.0,
                        "maxOutputTokens": 1024,
                        "responseMimeType": "application/json",
                        "responseSchema": RESPONSE_SCHEMA,
                        "thinkingConfig": {"thinkingBudget": 512},
                    },
                },
            }
            f.write(json.dumps(req) + "\n")


def submit_batch(client, jsonl_path: Path, display_name: str):
    print(f"  uploading {jsonl_path} ({jsonl_path.stat().st_size:,} bytes)...",
          flush=True)
    f = client.files.upload(file=str(jsonl_path), config=dict(
        display_name=display_name, mime_type="jsonl"))
    print(f"  uploaded: {f.name}", flush=True)
    job = client.batches.create(
        model=MODEL, src=f.name, config={"display_name": display_name})
    print(f"  batch job: {job.name} (state={job.state.name})", flush=True)
    return job


def poll_until_done(client, job_name: str, poll_secs: int = 60):
    done_states = {"JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED",
                   "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"}
    t0 = time.time()
    while True:
        job = client.batches.get(name=job_name)
        if job.state.name in done_states:
            print(f"  done in {time.time()-t0:.0f}s, state={job.state.name}",
                  flush=True)
            return job
        print(f"  [{time.time()-t0:.0f}s] state={job.state.name}", flush=True)
        time.sleep(poll_secs)


def download_results(client, job) -> list[dict]:
    if job.state.name != "JOB_STATE_SUCCEEDED":
        print(f"  batch did not succeed: {job.state.name}", file=sys.stderr)
        if hasattr(job, "error") and job.error:
            print(f"  error: {job.error}", file=sys.stderr)
        return []
    file_name = job.dest.file_name
    raw = client.files.download(file=file_name)
    text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def parse_verdict(rec: dict) -> tuple[str, str, str]:
    """Return (class, reason, extra) from one batch result row."""
    resp = rec.get("response") or {}
    candidates = resp.get("candidates") or []
    if not candidates:
        err = (rec.get("error") or {}).get("message", "no candidates")
        return "ERR", str(err)[:200], ""
    parts = (candidates[0].get("content") or {}).get("parts") or []
    text = parts[0].get("text", "") if parts else ""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n", "", text)
        text = re.sub(r"\n```\s*$", "", text)
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        s, e = text.find("{"), text.rfind("}")
        if s == -1 or e == -1:
            return "ERR", "unparseable verdict", text[:200]
        try:
            obj = json.loads(text[s:e+1])
        except Exception:
            return "ERR", "unparseable verdict", text[:200]
    v = obj.get("verdict", "decorative")
    cls = {"load_bearing": "B", "unscaffoldable": "D"}.get(v, "C")
    return cls, (obj.get("reason") or "")[:200], (obj.get("rule_cited") or "")[:200]


# ---------------------------------------------------------------------------
# Eligibility — same loading logic as audit_stub_full.py
# ---------------------------------------------------------------------------

def load_eligibles_from_existing(audit_csv: Path,
                                 want_classes: set[str]) -> list[tuple]:
    """Re-load eligibles for stubs already in audit CSV with given classes.

    Returns [(stub, repo, pr, tier1_paths)]. tier1_paths re-fetched from
    /tmp/repo_tier1.json.
    """
    repo_tier1 = json.load(open("/tmp/repo_tier1.json"))
    tier1_repos = {r: paths for r, paths in repo_tier1.items()
                   if paths and not any(
                       p.startswith(("ERR:", "TIMEOUT")) for p in paths)}
    elig = []
    for row in csv.DictReader(open(audit_csv)):
        if row["class"] not in want_classes:
            continue
        # C-unfetchable special case
        if "C-unfetchable" in want_classes and row["class"] == "C" \
                and "tier-1 unfetchable" not in row.get("reason", ""):
            continue
        repo = row["repo"]
        if repo not in tier1_repos:
            continue
        try:
            pr = int(row["pr"])
        except ValueError:
            continue
        elig.append((row["stub"], repo, pr, tier1_repos[repo]))
    return elig


def load_eligibles_from_jsonl(jsonl: Path) -> list[tuple]:
    """For new scout PRs."""
    repo_tier1 = json.load(open("/tmp/repo_tier1.json"))
    tier1_repos = {r: paths for r, paths in repo_tier1.items()
                   if paths and not any(
                       p.startswith(("ERR:", "TIMEOUT")) for p in paths)}
    elig = []
    for line in open(jsonl):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        repo = d.get("repo", "")
        title = d.get("title", "")
        pr = d.get("pr_number") or d.get("pr") or d.get("number")
        if not (repo and title and pr):
            continue
        if repo not in tier1_repos:
            continue
        elig.append((slugify(repo, title), repo, int(pr), tier1_repos[repo]))
    return elig


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def build_all_prompts(eligibles: list[tuple], gh_concurrency: int):
    sem = asyncio.Semaphore(gh_concurrency)
    total = len(eligibles)
    done = {"n": 0, "t0": time.time()}
    results: list = [None] * total

    async def _wrap(i, e, client):
        r = await build_one(client, sem, *e)
        results[i] = r
        done["n"] += 1
        n = done["n"]
        if n % 200 == 0 or n == total:
            elapsed = time.time() - done["t0"]
            rate = n / elapsed if elapsed > 0 else 0
            eta = (total - n) / rate / 60 if rate > 0 else 0
            short = sum(1 for x in results if x and "_prompt" not in x)
            print(f"  [{n}/{total}] {rate:.1f} stub/s  ETA {eta:.0f}min  "
                  f"(short-circuit: {short})", flush=True)

    async with httpx.AsyncClient(follow_redirects=True) as client:
        await asyncio.gather(*[
            _wrap(i, e, client) for i, e in enumerate(eligibles)
        ])
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-jsonl", type=Path,
                    help="Scout JSONL with new PRs to judge")
    ap.add_argument("--recheck-class",
                    choices=["ERR", "C-unfetchable"],
                    help="Re-judge specific class from existing audit CSV")
    ap.add_argument("--audit-csv", type=Path,
                    default=Path("/tmp/stub_pr_audit_full.csv"))
    ap.add_argument("--out", type=Path, required=True,
                    help="Output CSV (will append, same schema as audit)")
    ap.add_argument("--limit", type=int, default=0,
                    help="Cap eligibles (for testing)")
    ap.add_argument("--gh-concurrency", type=int, default=20)
    ap.add_argument("--display-name", default=None)
    ap.add_argument("--dry-run", action="store_true",
                    help="Build prompts and write JSONL but don't submit")
    args = ap.parse_args()

    if not args.from_jsonl and not args.recheck_class:
        sys.exit("Must specify --from-jsonl or --recheck-class")

    if args.recheck_class:
        want = {"ERR"} if args.recheck_class == "ERR" else {"C", "C-unfetchable"}
        elig = load_eligibles_from_existing(args.audit_csv, want)
        label = f"recheck-{args.recheck_class}"
    else:
        elig = load_eligibles_from_jsonl(args.from_jsonl)
        label = f"scout-{args.from_jsonl.stem}"

    if args.limit:
        elig = elig[:args.limit]
    print(f"Eligibles: {len(elig)}", flush=True)
    if not elig:
        sys.exit("No eligibles — exiting")

    # Phase 1: build prompts (parallel gh fetches)
    print(f"Phase 1: building prompts (gh concurrency={args.gh_concurrency})…",
          flush=True)
    t0 = time.time()
    rows = asyncio.run(build_all_prompts(elig, args.gh_concurrency))
    print(f"  built {len(rows)} rows in {time.time()-t0:.0f}s", flush=True)

    # Split: short-circuited (no LLM) vs needs-batch
    short_circuit = [r for r in rows if "_prompt" not in r]
    needs_batch = [r for r in rows if "_prompt" in r]
    print(f"  short-circuit (no LLM): {len(short_circuit)}", flush=True)
    print(f"  needs Gemini judge:      {len(needs_batch)}", flush=True)

    # Write short-circuit rows immediately
    new_csv = not args.out.exists()
    with args.out.open("a", newline="") as f:
        w = csv.DictWriter(f,
            fieldnames=["stub", "repo", "pr", "class", "reason", "extra"])
        if new_csv:
            w.writeheader()
        for r in short_circuit:
            w.writerow({k: r.get(k, "") for k in
                        ["stub", "repo", "pr", "class", "reason", "extra"]})

    if not needs_batch:
        print("Nothing to send to Gemini batch. Done.", flush=True)
        return

    # Phase 2: write JSONL + submit batch
    display = args.display_name or f"audit-{label}-{int(time.time())}"
    jsonl_path = Path(f"/tmp/{display}.jsonl")
    write_batch_jsonl(jsonl_path, needs_batch)
    print(f"Phase 2: wrote {jsonl_path} ({len(needs_batch)} requests)",
          flush=True)

    if args.dry_run:
        print("--dry-run: not submitting", flush=True)
        return

    client = genai.Client(api_key=GEMINI_KEY)
    job = submit_batch(client, jsonl_path, display)

    # Phase 3: poll
    print("Phase 3: polling…", flush=True)
    job = poll_until_done(client, job.name)

    # Phase 4: download + parse
    print("Phase 4: parsing results…", flush=True)
    records = download_results(client, job)
    by_key = {r["key"]: r for r in records if "key" in r}
    print(f"  got {len(records)} results, {len(by_key)} keyed", flush=True)

    with args.out.open("a", newline="") as f:
        w = csv.DictWriter(f,
            fieldnames=["stub", "repo", "pr", "class", "reason", "extra"])
        n_by_class = {"A": 0, "B": 0, "C": 0, "D": 0, "ERR": 0}
        n_by_class["A"] += sum(1 for r in short_circuit if r.get("class") == "A")
        n_by_class["C"] += sum(1 for r in short_circuit if r.get("class") == "C")
        n_by_class["ERR"] += sum(1 for r in short_circuit if r.get("class") == "ERR")
        for nb in needs_batch:
            rec = by_key.get(nb["stub"])
            if rec is None:
                cls, reason, extra = "ERR", "no result returned", ""
            else:
                cls, reason, extra = parse_verdict(rec)
            n_by_class[cls] = n_by_class.get(cls, 0) + 1
            w.writerow({"stub": nb["stub"], "repo": nb["repo"], "pr": nb["pr"],
                        "class": cls, "reason": reason, "extra": extra})

    print(f"\n=== Final ({len(rows)} stubs) ===", flush=True)
    for k, v in n_by_class.items():
        if v:
            print(f"  {k}: {v}")
    print(f"\nResults appended → {args.out}", flush=True)


if __name__ == "__main__":
    main()
