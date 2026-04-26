#!/usr/bin/env python3
"""Flex-tier sync judge — drop-in replacement for the batch path.

Reads a Gemini batch JSONL (one `{key, request}` per line, the same shape
audit_stub_batch.py builds in Phase 2) and submits each request via the
synchronous endpoint with `service_tier=FLEX`. Same 50% discount as batch,
but typical ~2-5s per call lets us fan out and finish 9k prompts in ~12min
at concurrency=32.

Output: appends rows to a CSV in the same schema audit_stub_batch.py emits.

Usage:
    .venv/bin/python scripts/judge_flex.py \\
        --jsonl /tmp/deep-scout-2026-04-25-13046-v2.jsonl \\
        --out pipeline_logs/batch_judge_2026_04_25/deep_scout_judges.csv \\
        --concurrency 32 \\
        --keys-from-jsonl    # only submit keys not yet in --out
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_KEY:
    sys.exit("GEMINI_API_KEY not set")

# We use the REST endpoint directly — it's the simplest async path with httpx,
# avoids the SDK's blocking-thread-pool overhead at high concurrency.
MODEL = "gemini-3.1-pro-preview-customtools"
URL = (f"https://generativelanguage.googleapis.com/v1beta/models/"
       f"{MODEL}:generateContent?key={GEMINI_KEY}")


def parse_verdict(text: str) -> tuple[str, str, str]:
    """Map Gemini JSON to (class, reason, extra) — same logic as the batch path."""
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


# repo,pr metadata are not in the JSONL — scrape them from the prompt body
# (the prompt format uses "Repo: {repo}\nPR #{pr}\n").
_REPO_RE = re.compile(r"Repo:\s+([\w.-]+/[\w.-]+)")
_PR_RE = re.compile(r"PR\s*#?(\d+)")


async def judge_one(client, sem, key: str, request_body: dict,
                    out_q: asyncio.Queue, retry_budget: int = 4):
    """Submit one Flex request; on retryable error, back off and retry."""
    # The batch JSONL format embeds generationConfig; we add service_tier
    # at the top level (REST/v1beta).
    body = dict(request_body)
    body["service_tier"] = "flex"

    # Pull repo/pr from the prompt for CSV columns
    prompt = body["contents"][0]["parts"][0]["text"]
    repo = (_REPO_RE.search(prompt) or [None, ""])[1]
    pr = (_PR_RE.search(prompt) or [None, "0"])[1]

    async with sem:
        for attempt in range(retry_budget):
            try:
                r = await client.post(URL, json=body, timeout=120)
            except Exception as e:
                if attempt == retry_budget - 1:
                    await out_q.put({
                        "stub": key, "repo": repo, "pr": pr,
                        "class": "ERR", "reason": f"network: {type(e).__name__}",
                        "extra": "",
                    })
                    return
                await asyncio.sleep(2 ** attempt)
                continue

            if r.status_code == 200:
                try:
                    data = r.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError, json.JSONDecodeError) as e:
                    await out_q.put({
                        "stub": key, "repo": repo, "pr": pr,
                        "class": "ERR", "reason": f"parse: {type(e).__name__}",
                        "extra": "",
                    })
                    return
                cls, reason, extra = parse_verdict(text)
                await out_q.put({
                    "stub": key, "repo": repo, "pr": pr,
                    "class": cls, "reason": reason, "extra": extra,
                })
                return

            if r.status_code in (429, 503):
                # 429: TPM exceeded; 503: Flex shed. Back off + retry.
                await asyncio.sleep(min(30, 2 ** attempt + 1))
                continue
            if r.status_code in (502, 504):
                await asyncio.sleep(2 ** attempt)
                continue

            # Other errors — record and move on
            await out_q.put({
                "stub": key, "repo": repo, "pr": pr,
                "class": "ERR", "reason": f"http {r.status_code}: {r.text[:120]}",
                "extra": "",
            })
            return

        # Exhausted retries
        await out_q.put({
            "stub": key, "repo": repo, "pr": pr,
            "class": "ERR", "reason": "retries exhausted (likely 429/503)",
            "extra": "",
        })


async def csv_writer(out_path: Path, q: asyncio.Queue, total: int):
    """Drain the result queue and append rows incrementally."""
    new = not out_path.exists()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    f = out_path.open("a", newline="")
    w = csv.DictWriter(f, fieldnames=["stub", "repo", "pr", "class", "reason", "extra"])
    if new:
        w.writeheader()
        f.flush()
    n = 0
    by_class: dict[str, int] = {}
    t0 = time.time()
    while n < total:
        row = await q.get()
        w.writerow(row)
        f.flush()
        by_class[row["class"]] = by_class.get(row["class"], 0) + 1
        n += 1
        if n % 100 == 0 or n == total:
            elapsed = time.time() - t0
            rate = n / elapsed if elapsed > 0 else 0
            eta = (total - n) / rate / 60 if rate > 0 else 0
            print(f"  [{n}/{total}] {rate:.1f}/s ETA {eta:.0f}min  by_class={by_class}",
                  flush=True)
    f.close()


def load_done_keys(out_path: Path) -> set[str]:
    if not out_path.exists():
        return set()
    return {row["stub"] for row in csv.DictReader(out_path.open()) if row.get("stub")}


async def run(args):
    # Load JSONL
    items: list[tuple[str, dict]] = []
    with open(args.jsonl) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            items.append((d["key"], d["request"]))
    print(f"Loaded {len(items)} prompts from {args.jsonl}", flush=True)

    # Resume: skip keys already in CSV
    done = load_done_keys(args.out)
    if done:
        before = len(items)
        items = [(k, r) for k, r in items if k not in done]
        print(f"Resume: skipping {before-len(items)} already-done; {len(items)} to go",
              flush=True)
    if not items:
        print("Nothing to do.")
        return

    sem = asyncio.Semaphore(args.concurrency)
    q: asyncio.Queue = asyncio.Queue()

    import httpx
    async with httpx.AsyncClient(http2=False) as client:
        writer_task = asyncio.create_task(csv_writer(args.out, q, len(items)))
        await asyncio.gather(*[
            judge_one(client, sem, k, r, q) for k, r in items
        ])
        await writer_task


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", type=Path, required=True,
                    help="Gemini batch JSONL (built by audit_stub_batch.py Phase 2)")
    ap.add_argument("--out", type=Path, required=True,
                    help="Output CSV (resumed if exists)")
    ap.add_argument("--concurrency", type=int, default=32)
    args = ap.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
