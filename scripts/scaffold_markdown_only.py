#!/usr/bin/env python3
"""Deterministic scaffolder for markdown_authoring tasks (no LLM).

For PRs whose `changed_files` are *all* tier-1 instruction-file paths
(CLAUDE.md / AGENTS.md / SKILL.md / .cursor/rules / etc.), the entire
scaffold is mechanical: clone Dockerfile, solve.sh that applies the gold
patch, test.sh that greps for distinctive lines from the patch, and a v2.0
eval_manifest with `task.kind = markdown_authoring`. No Opus call.

Input: scaffold queue JSONL with `{repo, pr}` rows (e.g. the same format
audit_stub_batch.py + scaffold v3/v4 use).

Output:
  - Tasks scaffolded under `harbor_tasks_md_authoring/<slug>/`
  - PRs that aren't pure-markdown are written to <queue_basename>_codebearing.jsonl
    (so they can be routed through the Opus pipeline separately)

Usage:
    .venv/bin/python scripts/scaffold_markdown_only.py \\
        --queue /tmp/scaffold_queue_v4_remaining.jsonl \\
        --out-dir harbor_tasks_md_authoring \\
        --concurrency 16

Behavior is idempotent: re-running on the same queue with existing task dirs
is a no-op for those tasks.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import httpx

# ---------------------------------------------------------------------------
# Tier-1 path detection — keep in sync with taskforge.config.AGENT_INSTRUCTION_RE
# ---------------------------------------------------------------------------

TIER1_RE = re.compile(
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

ROOT = Path(__file__).resolve().parents[1]
GH_TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
if not GH_TOKEN:
    try:
        GH_TOKEN = subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    except Exception:
        sys.exit("No GH_TOKEN available")


# ---------------------------------------------------------------------------
# GH helpers
# ---------------------------------------------------------------------------


def gh_headers() -> dict:
    return {"Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {GH_TOKEN}"}


# Process-wide rate-limit guard: when GH says we're out, all coroutines block
# until reset.
_RATE_RESET_AT: float = 0.0
_RATE_LOCK = asyncio.Lock()
_LAST_RATE_LOG: float = 0.0


async def _rate_wait():
    global _RATE_RESET_AT, _LAST_RATE_LOG
    if _RATE_RESET_AT <= 0:
        return
    delay = _RATE_RESET_AT - time.time()
    if delay <= 0:
        _RATE_RESET_AT = 0.0
        return
    delay = min(delay + 5, 3600)
    if time.time() - _LAST_RATE_LOG > 60:
        _LAST_RATE_LOG = time.time()
        print(f"  [rate-limit] sleeping {delay:.0f}s until reset",
              file=sys.stderr, flush=True)
    await asyncio.sleep(delay)
    _RATE_RESET_AT = 0.0


async def _gh_get(client, url, params=None, timeout=30):
    """GET with rate-limit awareness."""
    global _RATE_RESET_AT
    for attempt in range(5):
        await _rate_wait()
        try:
            r = await client.get(url, headers=gh_headers(),
                                  params=params, timeout=timeout)
        except (httpx.ReadError, httpx.ConnectError, httpx.TimeoutException,
                httpx.RemoteProtocolError, httpx.WriteError):
            await asyncio.sleep(2 + attempt * 2)
            continue
        remaining = r.headers.get("x-ratelimit-remaining")
        reset = r.headers.get("x-ratelimit-reset")
        if remaining and reset and int(remaining) <= 1:
            async with _RATE_LOCK:
                if _RATE_RESET_AT < int(reset):
                    _RATE_RESET_AT = float(reset)
        if r.status_code == 200:
            return r
        if r.status_code in (403, 429):
            if reset:
                async with _RATE_LOCK:
                    _RATE_RESET_AT = max(_RATE_RESET_AT, float(reset))
                await _rate_wait()
            else:
                await asyncio.sleep(30 * (attempt + 1))
            continue
        if r.status_code in (502, 503, 504):
            await asyncio.sleep(2 ** attempt)
            continue
        return r
    return None


async def fetch_pr(client: httpx.AsyncClient, repo: str, pr: int) -> dict | None:
    r = await _gh_get(client, f"https://api.github.com/repos/{repo}/pulls/{pr}")
    if r is None or r.status_code != 200:
        return None
    return r.json()


async def fetch_files(client: httpx.AsyncClient, repo: str, pr: int) -> list[dict] | None:
    out = []
    page = 1
    while True:
        r = await _gh_get(
            client, f"https://api.github.com/repos/{repo}/pulls/{pr}/files",
            params={"per_page": 100, "page": page})
        if r is None or r.status_code != 200:
            return None
        chunk = r.json()
        if not chunk:
            break
        out.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    return out


# ---------------------------------------------------------------------------
# Patch parsing
# ---------------------------------------------------------------------------


def slugify(repo: str, title: str) -> str:
    repo_short = repo.split("/")[-1].lower()
    clean = re.sub(r"[^a-z0-9\s]", "", title.lower())
    words = clean.split()[:5]
    return f"{repo_short}-{('-'.join(words) or 'unnamed')}"[:60]


def added_lines_from_patch(patch: str) -> list[str]:
    """Return only the `+` lines from a unified diff (not `+++` headers)."""
    out = []
    for line in patch.split("\n"):
        if line.startswith("+") and not line.startswith("+++"):
            out.append(line[1:])
    return out


def pick_signal_lines(added: list[str], n: int = 3) -> list[str]:
    """Pick up to N distinctive signal lines from the added content.

    Heuristic: prefer longer lines that aren't pure punctuation, are not
    blank, and aren't generic (e.g., just `---` or `## `). Sort by length
    descending and take the top N.
    """
    candidates = []
    for ln in added:
        s = ln.strip()
        if len(s) < 12:
            continue
        if not re.search(r"[A-Za-z0-9一-鿿]", s):
            continue
        if s in ("---", "```", "```python", "```bash"):
            continue
        candidates.append(s)
    candidates.sort(key=lambda x: -len(x))
    # De-duplicate while preserving order
    seen = set()
    picked = []
    for c in candidates:
        if c in seen:
            continue
        seen.add(c)
        picked.append(c)
        if len(picked) >= n:
            break
    return picked


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------


DOCKERFILE_TPL = """\
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \\
    git ca-certificates curl \\
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/{repo_short} && \\
    cd /workspace/{repo_short} && \\
    git remote add origin https://github.com/{repo}.git && \\
    git fetch --depth=1 origin {base_commit} && \\
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/{repo_short}
"""

SOLVE_SH_TPL = """\
#!/usr/bin/env bash
set -euo pipefail

cd /workspace/{repo_short}

# Idempotency guard
if {idempotency_check}; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
{patch}
PATCH

echo "Gold patch applied."
"""

TEST_SH_TPL = """\
#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

cd /workspace/{repo_short}

pytest -v --tb=short /tests/test_outputs.py
status=$?

if [ "$status" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
exit 0
"""

TEST_OUTPUTS_TPL = '''\
"""Behavioral checks for {task_name} (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/{repo_short}")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{{p}} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


{test_funcs}
'''

TEST_FUNC_TPL = '''\
def test_signal_{i:02d}():
    """Distinctive line from gold patch must be present."""
    text = _read({path!r})
    assert {needle!r} in text, "expected to find: " + {needle!r}[:80]
'''

INSTRUCTION_TPL = """\
# {title}

Source: [{repo}#{pr}]({pr_url})

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

{file_list}

## What to add / change

{description}

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
"""

EVAL_MANIFEST_TPL = """\
version: "2.0"

task:
  name: {task_name}
  kind: markdown_authoring
  difficulty: easy

source:
  repo: {repo}
  pr: {pr}
  base_commit: "{base_commit}"
  merge_commit: "{merge_commit}"

checks:
{checks_yaml}

config_edits:
{config_edits_yaml}
"""

TASK_TOML_TPL = """\
name = "{task_name}"
difficulty = "easy"
kind = "markdown_authoring"

[source]
type = "github_pr"
repo = "{repo}"
pr = {pr}
base_commit = "{base_commit}"
merge_commit = "{merge_commit}"
url = "{pr_url}"
"""


# ---------------------------------------------------------------------------
# Scaffold one
# ---------------------------------------------------------------------------


def is_pure_markdown(files: list[dict]) -> bool:
    if not files:
        return False
    return all(TIER1_RE.search(f["filename"]) for f in files)


def yaml_quote(s: str) -> str:
    """Block-scalar-quote a string for YAML."""
    if not s:
        return '""'
    # Use double quotes with escaping
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def scaffold_one(pr_record: dict, files: list[dict], pr_data: dict,
                 out_dir: Path) -> Path | None:
    repo = pr_record["repo"]
    pr = pr_record["pr"]
    title = pr_data.get("title", "")
    body = pr_data.get("body") or ""
    base_commit = pr_data.get("base", {}).get("sha")
    merge_commit = pr_data.get("merge_commit_sha")
    pr_url = pr_data.get("html_url", f"https://github.com/{repo}/pull/{pr}")
    repo_short = repo.split("/")[-1].lower().replace("_", "-")

    if not base_commit or not merge_commit:
        return None

    task_name = slugify(repo, title)
    task_dir = out_dir / task_name
    if task_dir.exists():
        return task_dir  # idempotent

    # Build per-file artifacts
    test_funcs = []
    config_edits = []
    idempotency_checks = []
    full_patch_chunks = []

    for f in files:
        filename = f["filename"]
        patch = f.get("patch") or ""
        added = added_lines_from_patch(patch)
        signals = pick_signal_lines(added, n=3)
        if not signals:
            # Fall back to a marker that the file was modified
            signals = [f.get("filename", "")]

        # Build test functions for this file
        for i, s in enumerate(signals):
            fn = TEST_FUNC_TPL.format(
                i=len(test_funcs),
                path=filename,
                needle=s[:200],  # cap length
            )
            test_funcs.append(fn)

        # Idempotency: any signal already present
        if signals:
            idempotency_checks.append(
                f'grep -qF {json.dumps(signals[0][:80])} {json.dumps(filename)}'
            )

        # config_edits entry
        added_text = "\n".join(added)
        config_edits.append({
            "path": filename,
            "tier": 1,
            "gold_added": added_text,
            "gold_removed": "",
        })

        # Full patch
        full_patch_chunks.append(f"diff --git a/{filename} b/{filename}\n{patch}")

    # Render files
    task_dir.mkdir(parents=True)
    (task_dir / "environment").mkdir()
    (task_dir / "solution").mkdir()
    (task_dir / "tests").mkdir()

    # Dockerfile
    (task_dir / "environment" / "Dockerfile").write_text(
        DOCKERFILE_TPL.format(
            repo=repo, repo_short=repo_short, base_commit=base_commit,
        )
    )

    # solve.sh — embed each file's patch
    full_patch = "\n".join(full_patch_chunks)
    idempotency = " && ".join(idempotency_checks) or "false"
    (task_dir / "solution" / "solve.sh").write_text(
        SOLVE_SH_TPL.format(
            repo_short=repo_short,
            idempotency_check=idempotency,
            patch=full_patch,
        )
    )
    (task_dir / "solution" / "solve.sh").chmod(0o755)

    # test.sh + test_outputs.py
    (task_dir / "tests" / "test.sh").write_text(
        TEST_SH_TPL.format(repo_short=repo_short)
    )
    (task_dir / "tests" / "test.sh").chmod(0o755)
    (task_dir / "tests" / "test_outputs.py").write_text(
        TEST_OUTPUTS_TPL.format(
            task_name=task_name,
            repo_short=repo_short,
            test_funcs="\n\n".join(test_funcs) or "def test_placeholder(): assert True\n",
        )
    )

    # instruction.md
    file_list = "\n".join(f"- `{f['filename']}`" for f in files)
    description = body.strip()[:1500] if body else (
        f"See the PR for the intended changes to the listed file(s).")
    (task_dir / "instruction.md").write_text(
        INSTRUCTION_TPL.format(
            title=title, repo=repo, pr=pr, pr_url=pr_url,
            file_list=file_list, description=description,
        )
    )

    # eval_manifest.yaml
    checks_yaml_lines = []
    idx = 0
    for f in files:
        signals = pick_signal_lines(added_lines_from_patch(f.get("patch") or ""), n=3)
        if not signals:
            continue
        for s in signals:
            checks_yaml_lines.append(
                f"  - id: signal_{idx:02d}\n"
                f"    type: fail_to_pass\n"
                f"    origin: pr_diff\n"
                f"    description: \"Distinctive line from gold patch must appear in {f['filename']}.\""
            )
            idx += 1
    checks_yaml = "\n".join(checks_yaml_lines) or "  []"

    config_edits_yaml_lines = []
    for ce in config_edits:
        # Use YAML block literals for multi-line content
        added_indented = "\n".join(f"      {ln}" for ln in ce["gold_added"].split("\n"))
        config_edits_yaml_lines.append(
            f"  - path: {yaml_quote(ce['path'])}\n"
            f"    tier: 1\n"
            f"    gold_added: |-\n{added_indented}\n"
            f"    gold_removed: \"\""
        )
    config_edits_yaml = "\n".join(config_edits_yaml_lines)

    (task_dir / "eval_manifest.yaml").write_text(
        EVAL_MANIFEST_TPL.format(
            task_name=task_name,
            repo=repo, pr=pr,
            base_commit=base_commit, merge_commit=merge_commit,
            checks_yaml=checks_yaml,
            config_edits_yaml=config_edits_yaml,
        )
    )

    # task.toml
    (task_dir / "task.toml").write_text(
        TASK_TOML_TPL.format(
            task_name=task_name, repo=repo, pr=pr,
            base_commit=base_commit, merge_commit=merge_commit,
            pr_url=pr_url,
        )
    )

    # scaffold_status.json — same shape oneshot_scaffold writes
    (task_dir / "scaffold_status.json").write_text(
        json.dumps({
            "scaffolded": True, "kind": "markdown_authoring",
            "deterministic": True, "nop_reward": 0, "gold_reward": 1,
        })
    )

    return task_dir


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def process_one(client, sem, pr_record, out_dir, codebearing_path):
    async with sem:
        repo = pr_record["repo"]
        pr = pr_record["pr"]
        try:
            files = await fetch_files(client, repo, pr)
            if files is None:
                return ("err", repo, pr, "files fetch failed")
            if not is_pure_markdown(files):
                # Code-bearing — write to codebearing queue
                with open(codebearing_path, "a") as f:
                    f.write(json.dumps(pr_record) + "\n")
                return ("codebearing", repo, pr, f"{len(files)} files, mixed")
            pr_data = await fetch_pr(client, repo, pr)
            if pr_data is None:
                return ("err", repo, pr, "pr metadata fetch failed")
            task_dir = scaffold_one(pr_record, files, pr_data, out_dir)
            if task_dir is None:
                return ("err", repo, pr, "scaffold returned None")
            return ("ok", repo, pr, task_dir.name)
        except Exception as e:
            return ("err", repo, pr, f"{type(e).__name__}: {str(e)[:200]}")


async def amain(args):
    queue = []
    with open(args.queue) as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                queue.append(json.loads(ln))
    print(f"Queue: {len(queue)}", flush=True)

    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    codebearing_path = Path(args.queue).parent / (
        Path(args.queue).stem + "_codebearing.jsonl")
    # Truncate codebearing file to start fresh
    open(codebearing_path, "w").close()

    sem = asyncio.Semaphore(args.concurrency)
    counts = {"ok": 0, "codebearing": 0, "err": 0}
    t0 = time.time()
    n = 0
    async with httpx.AsyncClient(follow_redirects=True) as client:
        coros = [process_one(client, sem, r, out_dir, codebearing_path) for r in queue]
        for fut in asyncio.as_completed(coros):
            status, repo, pr, msg = await fut
            counts[status] += 1
            n += 1
            if n % 50 == 0 or status == "err":
                rate = n / (time.time() - t0 + 1e-6)
                print(f"  [{n}/{len(queue)}] {rate:.1f}/s  "
                      f"ok={counts['ok']} codebearing={counts['codebearing']} err={counts['err']}",
                      flush=True)

    print(f"\n=== Final ===", flush=True)
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print(f"Tasks scaffolded → {out_dir}")
    print(f"Code-bearing queue → {codebearing_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", required=True, help="Input JSONL of {repo, pr}")
    ap.add_argument("--out-dir", default="harbor_tasks_md_authoring",
                    help="Output dir for scaffolded tasks (under repo root)")
    ap.add_argument("--concurrency", type=int, default=16)
    args = ap.parse_args()
    asyncio.run(amain(args))


if __name__ == "__main__":
    main()
