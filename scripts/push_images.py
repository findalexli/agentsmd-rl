#!/usr/bin/env python3
"""Build and push harbor task Docker images to ghcr.io.

Designed to run inside GitHub Actions (free, no local builds needed).
Can also run locally if Docker is available.

The script:
1. Discovers tasks with Dockerfiles
2. Builds each image (one at a time to save disk — prunes between builds)
3. Pushes to ghcr.io/<owner>/agentsmd-rl/<task-name>:<tag>
4. Optionally updates task.toml with docker_image field

Usage (GitHub Actions — preferred):
    # Trigger via workflow_dispatch in the GitHub UI, or:
    gh workflow run push-images.yml -f task_dir=harbor_tasks -f tier_a_only=true

Usage (local — if you really need to):
    echo $(gh auth token) | docker login ghcr.io -u findalexli --password-stdin
    .venv/bin/python scripts/push_images.py --task-dir harbor_tasks --tier-a --batch-size 50

Usage (generate task list for GHA matrix):
    .venv/bin/python scripts/push_images.py --list-tasks --tier-a --task-dir harbor_tasks
"""

import argparse
import hashlib
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

REGISTRY = "ghcr.io"
REPO_NAME = "agentsmd-rl"
ROOT = Path(__file__).resolve().parent.parent


def dockerfile_hash(dockerfile_path: Path) -> str:
    """Short hash of Dockerfile contents for cache-busting tags."""
    return hashlib.sha256(dockerfile_path.read_bytes()).hexdigest()[:12]


def image_ref(owner: str, task_name: str, tag: str) -> str:
    """Full ghcr.io image reference."""
    return f"{REGISTRY}/{owner.lower()}/{REPO_NAME}/{task_name.lower()}:{tag}"


def find_tasks(task_dir: Path, tier_a_only: bool = False) -> list[Path]:
    """Find task directories with Dockerfiles, optionally filtering to tier-A."""
    tasks = []
    for d in sorted(task_dir.iterdir()):
        if not d.is_dir():
            continue
        dockerfile = d / "environment" / "Dockerfile"
        if not dockerfile.exists():
            continue

        if tier_a_only:
            status = d / "status.json"
            if not status.exists():
                continue
            try:
                data = json.loads(status.read_text())
                if data.get("verdict") != "pass":
                    continue
            except (json.JSONDecodeError, KeyError):
                continue
            quality = d / "quality.json"
            if quality.exists():
                try:
                    qdata = json.loads(quality.read_text())
                    tier_ab_fails = [
                        f for f in qdata.get("fails", [])
                        if f.get("tier") in ("A", "B")
                    ]
                    if tier_ab_fails:
                        continue
                except (json.JSONDecodeError, KeyError):
                    pass

        tasks.append(d)
    return tasks


def check_image_exists(ref: str) -> bool:
    """Check if image already exists in registry (skip re-push)."""
    result = subprocess.run(
        ["docker", "manifest", "inspect", ref],
        capture_output=True,
    )
    return result.returncode == 0


def build_and_push_one(
    task_path: Path,
    owner: str,
    tag: str,
    skip_existing: bool = True,
    update_toml: bool = False,
) -> dict:
    """Build and push a single task image. Returns result dict."""
    task_name = task_path.name
    dockerfile = task_path / "environment" / "Dockerfile"

    actual_tag = dockerfile_hash(dockerfile) if tag == "auto" else tag
    ref = image_ref(owner, task_name, actual_tag)
    # Also tag as :latest for convenience
    ref_latest = image_ref(owner, task_name, "latest")

    result = {"task": task_name, "image": ref, "status": "pending", "duration_s": 0}
    t0 = time.monotonic()

    # Skip if already pushed
    if skip_existing and check_image_exists(ref):
        result["status"] = "exists"
        log.info(f"[skip] {task_name} already at {ref}")
        return result

    # Build
    log.info(f"[build] {task_name}...")
    build = subprocess.run(
        [
            "docker", "build",
            "--platform", "linux/amd64",
            "-t", ref,
            "-t", ref_latest,
            "-f", str(dockerfile),
            str(dockerfile.parent),
        ],
        capture_output=True,
        timeout=900,  # 15 min max per build
    )
    if build.returncode != 0:
        result["status"] = "build_failed"
        result["error"] = build.stderr.decode()[-500:]
        log.error(f"[FAIL] {task_name} build: {result['error'][-200:]}")
        return result

    # Push both tags
    for r in [ref, ref_latest]:
        push = subprocess.run(
            ["docker", "push", r],
            capture_output=True,
            timeout=600,
        )
        if push.returncode != 0:
            result["status"] = "push_failed"
            result["error"] = push.stderr.decode()[-500:]
            log.error(f"[FAIL] {task_name} push: {result['error'][-200:]}")
            return result

    result["status"] = "pushed"
    result["duration_s"] = round(time.monotonic() - t0, 1)
    log.info(f"[done] {task_name} → {ref} ({result['duration_s']}s)")

    # Update task.toml
    if update_toml:
        update_task_toml(task_path, ref)

    return result


def update_task_toml(task_path: Path, image_ref: str) -> None:
    """Add docker_image to task.toml under [environment]."""
    toml_path = task_path / "task.toml"
    if not toml_path.exists():
        return
    content = toml_path.read_text()
    lines = [l for l in content.splitlines() if not l.strip().startswith("docker_image")]
    content = "\n".join(lines)
    if "[environment]" in content:
        content = content.replace(
            "[environment]",
            f'[environment]\ndocker_image = "{image_ref}"',
        )
    toml_path.write_text(content)
    log.info(f"  Updated task.toml: {task_path.name}")


def main():
    parser = argparse.ArgumentParser(description="Build and push task images to ghcr.io")
    parser.add_argument("--task-dir", type=Path, default=ROOT / "harbor_tasks")
    parser.add_argument("--tier-a", action="store_true", help="Only tier-A tasks")
    parser.add_argument("--owner", default=os.environ.get("GH_OWNER", "findalexli"))
    parser.add_argument("--tag", default="auto", help="Image tag (default: Dockerfile hash)")
    parser.add_argument("--skip-existing", action="store_true", default=True)
    parser.add_argument("--no-skip-existing", dest="skip_existing", action="store_false")
    parser.add_argument("--update-toml", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--list-tasks", action="store_true", help="Print task names as JSON (for GHA matrix)")
    parser.add_argument("--batch-start", type=int, default=0, help="Start index (for batching)")
    parser.add_argument("--batch-size", type=int, default=0, help="Batch size (0 = all)")
    parser.add_argument("--out", type=Path, help="Output JSONL results")
    args = parser.parse_args()

    tasks = find_tasks(args.task_dir, tier_a_only=args.tier_a)
    log.info(f"Found {len(tasks)} tasks in {args.task_dir.name}")

    # Slice for batching (GHA matrix splits work across jobs)
    if args.batch_size > 0:
        tasks = tasks[args.batch_start:args.batch_start + args.batch_size]
        log.info(f"Batch [{args.batch_start}:{args.batch_start + args.batch_size}] → {len(tasks)} tasks")

    # List mode: output JSON for GHA matrix
    if args.list_tasks:
        names = [t.name for t in tasks]
        # Output as batches of 50 for GHA matrix
        batch_size = 50
        batches = []
        for i in range(0, len(names), batch_size):
            batches.append({"start": i, "size": batch_size, "count": min(batch_size, len(names) - i)})
        print(json.dumps({"total": len(names), "batches": batches, "tasks": names}))
        return

    if args.dry_run:
        for t in tasks:
            df = t / "environment" / "Dockerfile"
            tag = dockerfile_hash(df) if args.tag == "auto" else args.tag
            ref = image_ref(args.owner, t.name, tag)
            print(f"  {t.name} → {ref}")
        print(f"\n{len(tasks)} images would be built+pushed")
        return

    if not tasks:
        log.error("No tasks found")
        sys.exit(1)

    # Build and push sequentially (one at a time to save disk)
    results = []
    pushed, failed, skipped = 0, 0, 0
    for i, task in enumerate(tasks):
        log.info(f"[{i+1}/{len(tasks)}] {task.name}")
        r = build_and_push_one(task, args.owner, args.tag, args.skip_existing, args.update_toml)
        results.append(r)

        if r["status"] == "pushed":
            pushed += 1
        elif r["status"] == "exists":
            skipped += 1
        else:
            failed += 1

        # Prune after each build to save disk (GHA runners have ~14GB)
        if r["status"] == "pushed":
            subprocess.run(
                ["docker", "image", "rm", "-f", r["image"]],
                capture_output=True,
            )
            # Also remove dangling images from multi-stage builds
            subprocess.run(
                ["docker", "image", "prune", "-f"],
                capture_output=True,
            )

    log.info(f"Done: {pushed} pushed, {skipped} skipped, {failed} failed")

    if args.out:
        with open(args.out, "w") as f:
            for r in results:
                f.write(json.dumps(r) + "\n")
        log.info(f"Results → {args.out}")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
