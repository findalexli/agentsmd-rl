#!/usr/bin/env python3
"""V3 markdown-authoring scaleup: deep-rescout + new-discovery in one batch.

Waits for both scouts to finish, merges their outputs, then runs:
  pre-judge (Gemini Standard) -> scaffold (deterministic) -> post-judge -> quarantine

After post-judge, commits the new tasks + audit trail and triggers the
GHCR push workflow.
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path("/home/alex/agentsmd-rl")
MD_DIR = ROOT / "markdown_authoring"


def log(msg: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def pid_alive(pid: int) -> bool:
    return Path(f"/proc/{pid}").exists()


def wait_for_pid(pid: int, name: str, max_h: float = 4.0):
    t0 = time.time()
    while pid_alive(pid):
        if time.time() - t0 > max_h * 3600:
            log(f"[{name}] timeout — proceeding")
            return
        time.sleep(60)
    log(f"[{name}] PID {pid} done (waited {(time.time()-t0)/60:.1f}m)")


def count_corpus():
    return sum(1 for d in MD_DIR.iterdir() if d.is_dir())


def merge_jsonls(out_path: Path, *inputs: Path) -> int:
    seen = set()
    n = 0
    with open(out_path, "w") as fout:
        for src in inputs:
            if not src.exists():
                log(f"  (missing input {src} — skipping)")
                continue
            for line in open(src):
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                key = (d.get("repo"), d.get("pr_number") or d.get("pr"))
                if key in seen:
                    continue
                seen.add(key)
                fout.write(line + "\n")
                n += 1
    return n


def run(cmd, log_path: Path) -> int:
    log(f"running: {' '.join(str(c) for c in cmd)} > {log_path.name}")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w") as f:
        rc = subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT).returncode
    log(f"  rc={rc}")
    return rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deep-pid", type=int, required=True)
    ap.add_argument("--new-pid", type=int, required=True)
    ap.add_argument("--deep-output", type=Path,
                    default=ROOT / "scouted_deep30_2026_04_27.jsonl")
    ap.add_argument("--new-output", type=Path,
                    default=ROOT / "scouted_v3_new_2026_04_27.jsonl")
    ap.add_argument("--label", default="v3")
    args = ap.parse_args()

    log(f"V3 orchestrator start. Initial corpus: {count_corpus()}")

    log(f"Phase 1: waiting for scouts (deep PID {args.deep_pid}, new PID {args.new_pid})")
    wait_for_pid(args.deep_pid, "deep_scout", max_h=2)
    wait_for_pid(args.new_pid, "new_scout", max_h=2)

    log("Phase 2: merge scout outputs")
    merged = ROOT / f"scouted_{args.label}_merged.jsonl"
    n = merge_jsonls(merged, args.deep_output, args.new_output)
    log(f"  merged {n} unique candidate PRs -> {merged}")

    log("Phase 3: pre-judge (Standard tier, regex pre-filter inside)")
    prejudged = ROOT / f"scouted_{args.label}_prejudged.jsonl"
    pj_log = ROOT / "pipeline_logs" / "scaffold_v4_2026_04_26" / f"prejudge_{args.label}.log"
    run([".venv/bin/python", "scripts/quality_judge.py",
         "--mode", "markdown_authoring",
         "--scout-jsonl", str(merged),
         "--filtered-output", str(prejudged),
         "--service-tier", "standard",
         "--concurrency", "16"], pj_log)

    if not prejudged.exists() or prejudged.stat().st_size == 0:
        log("  (pre-judge produced no output — nothing to scaffold)")
        return

    log("Phase 4: deterministic scaffold")
    queue = Path(f"/tmp/scaffold_queue_{args.label}.jsonl")
    n_scaff = 0
    with open(prejudged) as fin, open(queue, "w") as fout:
        for line in fin:
            d = json.loads(line)
            row = {"repo": d["repo"], "pr": d.get("pr_number") or d.get("pr")}
            if d.get("file_paths"):
                row["file_paths"] = d["file_paths"]
            fout.write(json.dumps(row) + "\n")
            n_scaff += 1
    log(f"  queue size: {n_scaff}")

    pre = count_corpus()
    sc_log = ROOT / "pipeline_logs" / "scaffold_v4_2026_04_26" / f"md_only_{args.label}.log"
    run([".venv/bin/python", "scripts/scaffold_markdown_only.py",
         "--queue", str(queue),
         "--out-dir", "markdown_authoring",
         "--concurrency", "16"], sc_log)
    post_scaff = count_corpus()
    log(f"  scaffolded {post_scaff - pre} new tasks ({pre} -> {post_scaff})")

    log("Phase 5: post-judge with --quarantine (Standard tier)")
    pj2_log = ROOT / "pipeline_logs" / "scaffold_v4_2026_04_26" / f"md_quality_{args.label}.log"
    out_json = ROOT / "pipeline_logs" / "scaffold_v4_2026_04_26" / f"md_quality_{args.label}.json"
    run([".venv/bin/python", "scripts/quality_judge.py",
         "--mode", "markdown_authoring",
         "--task-dir", "markdown_authoring",
         "--concurrency", "32",
         "--service-tier", "standard",
         "--quarantine",
         "--output", str(out_json)], pj2_log)
    final = count_corpus()
    log(f"After quarantine: {final} active (was {post_scaff} pre-quarantine)")

    log("Phase 6: refresh research/md_authoring_quality_judgments.json")
    target = ROOT / "research" / "md_authoring_quality_judgments.json"
    if out_json.exists():
        # Merge new judge output into the canonical audit trail
        prior = []
        if target.exists():
            prior = json.load(open(target))
        new = json.load(open(out_json))
        # Keyed by task name; new wins on overlap
        prior_by = {r.get("task"): r for r in prior}
        new_by = {r.get("task"): r for r in new}
        merged_aud = list({**prior_by, **new_by}.values())
        json.dump(merged_aud, open(target, "w"), indent=2)
        log(f"  audit trail: {len(prior)} -> {len(merged_aud)} entries")

    log("Phase 7: commit + push")
    subprocess.run(["git", "add",
                    "markdown_authoring/",
                    "research/md_authoring_quality_judgments.json",
                    "scouted_v3_new_2026_04_27.jsonl",
                    "scouted_deep30_2026_04_27.jsonl"],
                   cwd=ROOT, check=False)
    msg = (f"Add v3 markdown_authoring scaleup ({final - pre} more active)\n\n"
           f"Deep re-scout of top-30 yielding repos with extended 36-month "
           f"recency window + new-discovery scout of 22 repos with confirmed "
           f"tier-1 files. Pipeline B unchanged: pre-judge (Gemini Standard, "
           f"title-only) -> deterministic scaffold -> post-judge with "
           f"--quarantine (Gemini Standard, full gold-patch context).\n\n"
           f"Active markdown_authoring corpus: {final} (was {pre}).\n\n"
           f"Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>")
    r = subprocess.run(["git", "commit", "-m", msg],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        log(f"git commit: {r.stderr[-300:]}")
        return
    log(f"committed: {r.stdout.strip().splitlines()[0] if r.stdout else ''}")
    r = subprocess.run(["git", "push", "origin", "master"], cwd=ROOT,
                       capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        log(f"push failed: {r.stderr[-300:]}")
        return
    log("pushed")

    log("Phase 8: trigger GHCR workflow")
    r = subprocess.run(["gh", "workflow", "run", "push-images.yml",
                        "-f", "task_dir=markdown_authoring",
                        "-f", "tier_a_only=false",
                        "-f", "update_toml=false"],
                       cwd=ROOT, capture_output=True, text=True)
    log(f"workflow: {r.stdout.strip() or r.stderr[-200:]}")
    log("V3 orchestrator done.")


if __name__ == "__main__":
    main()
