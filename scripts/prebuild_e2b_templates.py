"""Pre-build all E2B templates from Harbor task Dockerfiles.

Throttles to 10 concurrent builds to stay under E2B's 20-build limit.
Once built, templates are cached by alias and reused by the training script.

Usage:
    set -a && source .env && set +a && python scripts/prebuild_e2b_templates.py
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from hashlib import sha256
from pathlib import Path

from e2b import AsyncTemplate, Template

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

HARBOR_TASKS_DIR = Path(__file__).resolve().parent.parent / "harbor_tasks"
MAX_CONCURRENT_BUILDS = 5


def _dir_hash(directory: Path, length: int = 12) -> str:
    dockerfile = directory / "Dockerfile"
    if dockerfile.exists():
        return sha256(dockerfile.read_bytes()).hexdigest()[:length]
    return sha256(str(directory).encode()).hexdigest()[:length]


async def build_one(env_dir: Path, semaphore: asyncio.Semaphore) -> tuple[str, bool, str]:
    """Build a single E2B template. Returns (name, success, message)."""
    dir_hash = _dir_hash(env_dir)
    template_name = f"tinker-{env_dir.parent.name}-{dir_hash}".replace(".", "-")

    # Check if already built
    if await AsyncTemplate.alias_exists(template_name):
        return template_name, True, "cached"

    async with semaphore:
        try:
            logger.info("Building %s ...", template_name)
            dockerfile_path = env_dir / "Dockerfile"
            template = Template().from_dockerfile(
                dockerfile_content_or_path=str(dockerfile_path),
            )
            await AsyncTemplate.build(
                template=template,
                alias=template_name,
                cpu_count=2,
                memory_mb=1024,
            )
            logger.info("Built %s", template_name)
            return template_name, True, "built"
        except Exception as e:
            logger.error("Failed %s: %s", template_name, e)
            return template_name, False, str(e)


async def main() -> None:
    if not os.environ.get("E2B_API_KEY"):
        print("E2B_API_KEY not set")
        sys.exit(1)

    # Collect all task environment dirs
    env_dirs: list[Path] = []
    for task_dir in sorted(HARBOR_TASKS_DIR.iterdir()):
        if not task_dir.is_dir():
            continue
        env_dir = task_dir / "environment"
        if (env_dir / "Dockerfile").exists():
            env_dirs.append(env_dir)

    print(f"Found {len(env_dirs)} tasks with Dockerfiles")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_BUILDS)
    results = await asyncio.gather(*[build_one(d, semaphore) for d in env_dirs])

    cached = sum(1 for _, ok, msg in results if ok and msg == "cached")
    built = sum(1 for _, ok, msg in results if ok and msg == "built")
    failed = sum(1 for _, ok, _ in results if not ok)

    print(f"\nDone: {cached} cached, {built} newly built, {failed} failed")
    if failed:
        for name, ok, msg in results:
            if not ok:
                print(f"  FAILED: {name}: {msg}")


if __name__ == "__main__":
    asyncio.run(main())
