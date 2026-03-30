"""E2B sandbox implementing tinker_cookbook's SandboxInterface.

Builds E2B templates from Dockerfiles with retry on rate limits,
and handles stale template aliases gracefully.
"""

from __future__ import annotations

import asyncio
import logging
import os
import shlex
from hashlib import sha256
from pathlib import Path

from e2b import AsyncSandbox, AsyncTemplate, Template
from e2b.sandbox.commands.command_handle import CommandExitException
from tinker_cookbook.sandbox.sandbox_interface import SandboxResult, SandboxTerminatedError

logger = logging.getLogger(__name__)


def _dir_hash(directory: str | Path, length: int = 12) -> str:
    """Stable hash of a directory's Dockerfile content for template caching."""
    dockerfile = Path(directory) / "Dockerfile"
    if dockerfile.exists():
        return sha256(dockerfile.read_bytes()).hexdigest()[:length]
    return sha256(str(directory).encode()).hexdigest()[:length]


class E2BSandbox:
    """SandboxInterface implementation backed by E2B."""

    def __init__(
        self,
        sandbox: AsyncSandbox,
        template_name: str,
        max_output_bytes: int = 128 * 1024,
    ) -> None:
        self._sandbox = sandbox
        self._template_name = template_name
        self._max_output_bytes = max_output_bytes

    @classmethod
    async def create(
        cls,
        env_dir: Path,
        timeout: int = 3600,
        cpu_count: int = 2,
        memory_mb: int = 1024,
        max_output_bytes: int = 128 * 1024,
    ) -> E2BSandbox:
        if not os.environ.get("E2B_API_KEY"):
            raise SystemExit("E2B_API_KEY not set")

        dockerfile_path = env_dir / "Dockerfile"
        if not dockerfile_path.exists():
            raise FileNotFoundError(f"Dockerfile not found at {dockerfile_path}")

        dir_hash = _dir_hash(env_dir)
        template_name = f"tinker-{env_dir.parent.name}-{dir_hash}".replace(".", "-")

        async def _build_template() -> None:
            logger.info("Building E2B template %s", template_name)
            tpl = Template().from_dockerfile(dockerfile_content_or_path=str(dockerfile_path))
            for attempt in range(5):
                try:
                    await AsyncTemplate.build(
                        template=tpl, alias=template_name,
                        cpu_count=cpu_count, memory_mb=memory_mb,
                    )
                    logger.info("Template %s built", template_name)
                    return
                except Exception as e:
                    if "429" in str(e) or "rate limit" in str(e).lower():
                        wait = 30 * (attempt + 1)
                        logger.warning("Rate limited on %s, retry in %ds", template_name, wait)
                        await asyncio.sleep(wait)
                    else:
                        raise
            raise RuntimeError(f"Failed to build {template_name} after 5 attempts")

        if not await AsyncTemplate.alias_exists(template_name):
            await _build_template()

        for attempt in range(3):
            try:
                sandbox = await AsyncSandbox.create(template=template_name, timeout=timeout)
                # Ensure /logs/verifier is writable by non-root user
                handle = await sandbox.commands.run(
                    "mkdir -p /logs/verifier && chmod 777 /logs/verifier",
                    background=True, user="root",
                )
                await handle.wait()
                return cls(sandbox=sandbox, template_name=template_name, max_output_bytes=max_output_bytes)
            except Exception as e:
                if "not found" in str(e).lower():
                    logger.warning("Template %s stale, rebuilding", template_name)
                    await _build_template()
                elif "429" in str(e) or "rate limit" in str(e).lower():
                    await asyncio.sleep(30 * (attempt + 1))
                else:
                    raise

        raise RuntimeError(f"Failed to create sandbox for {template_name}")

    @property
    def sandbox_id(self) -> str:
        return self._sandbox.sandbox_id

    async def send_heartbeat(self) -> None:
        pass

    async def run_command(
        self, command: str, workdir: str | None = None,
        timeout: int = 60, max_output_bytes: int | None = None,
    ) -> SandboxResult:
        cap = max_output_bytes if max_output_bytes is not None else self._max_output_bytes
        try:
            # Run as root to match Harbor's E2B environment behavior
            handle = await self._sandbox.commands.run(
                cmd=command, background=True, cwd=workdir or "/", timeout=timeout,
                user="root",
            )
            try:
                result = await handle.wait()
            except CommandExitException as e:
                result = e
            return SandboxResult(
                stdout=(result.stdout or "")[:cap],
                stderr=(result.stderr or "")[:cap],
                exit_code=result.exit_code,
            )
        except Exception as e:
            if any(kw in str(e).lower() for kw in ("terminated", "not found", "killed")):
                raise SandboxTerminatedError(str(e)) from e
            return SandboxResult(stdout="", stderr=str(e), exit_code=-1)

    async def read_file(self, path: str, max_bytes: int | None = None, timeout: int = 60) -> SandboxResult:
        try:
            data = await self._sandbox.files.read(path, format="bytes")
            text = data.decode("utf-8", errors="replace")
            if max_bytes is not None:
                text = text[:max_bytes]
            return SandboxResult(stdout=text, stderr="", exit_code=0)
        except Exception as e:
            return SandboxResult(stdout="", stderr=str(e), exit_code=1)

    async def write_file(self, path: str, content: str | bytes = "", executable: bool = False, timeout: int = 60) -> SandboxResult:
        try:
            if isinstance(content, str):
                content = content.encode()
            dir_path = os.path.dirname(path)
            if dir_path and dir_path != "/":
                await self._sandbox.files.make_dir(dir_path)
            await self._sandbox.files.write(path, content)
            if executable:
                await self.run_command(f"chmod +x {shlex.quote(path)}", timeout=timeout)
            return SandboxResult(stdout="", stderr="", exit_code=0)
        except Exception as e:
            return SandboxResult(stdout="", stderr=str(e), exit_code=-1)

    async def cleanup(self) -> None:
        try:
            await self._sandbox.kill()
        except Exception as e:
            logger.warning("E2B sandbox kill failed: %s", e)
