"""Multi-backend pool with automatic fallback for LLM API calls.

Supports Anthropic-format (GLM, Anthropic API key) and OpenAI-format
(OpenRouter/Fireworks for Kimi K2.5) backends. Routes requests cheapest-first;
on 429 rate limits, transparently retries on the next available backend.

Two execution modes share the same pool:
  - Direct API (httpx)  — ~5 MB/request, for single-shot tasks
  - Subprocess (claude -p) — ~300 MB/process, for multi-turn agent tasks
    Note: OpenAI-format backends need a litellm proxy for subprocess mode.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import AsyncIterator, Literal

import httpx

# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Backend:
    """Immutable config for one LLM backend."""

    name: str
    base_url: str                          # "" → https://api.anthropic.com
    api_key: str
    auth_type: Literal["x-api-key", "bearer"] = "x-api-key"
    api_format: Literal["anthropic", "openai"] = "anthropic"
    model_map: dict[str, str] = field(default_factory=dict)
    max_concurrent: int = 4
    cost_tier: int = 0                     # 0 free → 1 sub → 2 paid → 3 cheap-paid
    supports_direct: bool = True           # False for OAuth
    supports_subprocess: bool = True       # False for OpenAI-format without proxy

    def resolve_model(self, logical: str) -> str:
        return self.model_map.get(logical, logical)

    def api_headers(self) -> dict[str, str]:
        h: dict[str, str] = {"content-type": "application/json"}
        if self.api_format == "anthropic":
            h["anthropic-version"] = "2023-06-01"
        if self.auth_type == "bearer":
            h["authorization"] = f"Bearer {self.api_key}"
        else:
            h["x-api-key"] = self.api_key
        return h

    def messages_url(self) -> str:
        base = self.base_url or "https://api.anthropic.com"
        if self.api_format == "openai":
            return f"{base}/chat/completions"
        return f"{base}/v1/messages"

    def subprocess_env(self) -> dict[str, str]:
        """Env vars for a claude -p subprocess."""
        env: dict[str, str] = {}
        if self.base_url:
            env["ANTHROPIC_BASE_URL"] = self.base_url
        if self.auth_type == "bearer":
            env["CLAUDE_ACCESS_TOKEN"] = self.api_key
        else:
            env["ANTHROPIC_API_KEY"] = self.api_key
            env["ANTHROPIC_AUTH_TOKEN"] = self.api_key
        for logical, actual in self.model_map.items():
            env[f"ANTHROPIC_DEFAULT_{logical.upper()}_MODEL"] = actual
        return env


# ---------------------------------------------------------------------------
# Pool state
# ---------------------------------------------------------------------------

@dataclass
class _Slot:
    backend: Backend
    sem: asyncio.Semaphore = field(init=False)
    cooldown_until: float = 0.0
    consecutive_429s: int = 0
    total_ok: int = 0
    total_429: int = 0
    available: bool = True

    def __post_init__(self) -> None:
        self.sem = asyncio.Semaphore(self.backend.max_concurrent)

    @property
    def in_cooldown(self) -> bool:
        return time.monotonic() < self.cooldown_until


class BackendPool:
    """Routes requests across backends, cheapest-first, with 429 fallback."""

    def __init__(self, backends: list[Backend], acquire_timeout: float = 600):
        self._slots = sorted(
            [_Slot(b) for b in backends],
            key=lambda s: s.backend.cost_tier,
        )
        self._timeout = acquire_timeout

    @property
    def names(self) -> list[str]:
        return [s.backend.name for s in self._slots]

    # -- acquire / release --------------------------------------------------

    @asynccontextmanager
    async def acquire(self, *, direct_only: bool = False) -> AsyncIterator[Backend]:
        """Acquire the cheapest available backend. Releases on context exit."""
        slot = await self._wait(direct_only)
        try:
            yield slot.backend
        finally:
            slot.sem.release()

    async def _wait(self, direct_only: bool) -> _Slot:
        deadline = time.monotonic() + self._timeout
        while True:
            now = time.monotonic()
            for s in self._slots:
                if not s.available:
                    continue
                if direct_only and not s.backend.supports_direct:
                    continue
                if now < s.cooldown_until:
                    continue
                if s.sem._value > 0:
                    await s.sem.acquire()
                    return s

            # Sleep until earliest cooldown or 1s.
            waits = [
                s.cooldown_until - now
                for s in self._slots
                if s.available and now < s.cooldown_until
                and (not direct_only or s.backend.supports_direct)
            ]
            delay = max(0.1, min(min(waits, default=1.0), 2.0))
            if time.monotonic() + delay > deadline:
                raise TimeoutError(
                    f"No backend available within {self._timeout}s. "
                    f"Pool: {self.stats()}"
                )
            await asyncio.sleep(delay)

    # -- feedback -----------------------------------------------------------

    def report_success(self, backend: Backend) -> None:
        s = self._find(backend)
        s.consecutive_429s = 0
        s.total_ok += 1

    def report_429(self, backend: Backend) -> None:
        s = self._find(backend)
        s.consecutive_429s += 1
        s.total_429 += 1
        delay = min(10 * (2 ** (s.consecutive_429s - 1)), 300)
        s.cooldown_until = time.monotonic() + delay
        print(f"  [{_ts()}] 429 on {backend.name}, cooldown {delay}s")

    def report_dead(self, backend: Backend) -> None:
        self._find(backend).available = False
        print(f"  [{_ts()}] {backend.name} marked dead")

    def _find(self, backend: Backend) -> _Slot:
        for s in self._slots:
            if s.backend is backend:
                return s
        raise ValueError(f"Unknown backend: {backend.name}")

    # -- stats --------------------------------------------------------------

    def stats(self) -> str:
        parts = []
        for s in self._slots:
            state = "dead" if not s.available else "ok"
            parts.append(f"{s.backend.name}({s.total_ok}ok/{s.total_429}×429/{state})")
        return " | ".join(parts)


def _ts() -> str:
    return time.strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# Direct API client
# ---------------------------------------------------------------------------

class RateLimitError(Exception):
    pass


class APIError(Exception):
    def __init__(self, status: int, body: str):
        self.status = status
        super().__init__(f"HTTP {status}: {body[:300]}")


async def call_api(
    pool: BackendPool,
    *,
    messages: list[dict],
    model: str = "opus",
    max_tokens: int = 16384,
    system: str | None = None,
    http: httpx.AsyncClient | None = None,
) -> tuple[str, dict | None, str]:
    """Single-shot LLM call with automatic backend fallback.

    Returns ``(response_text, usage_or_None, backend_name)``.
    Retries across backends on 429; raises on persistent failure.
    """
    own_client = http is None
    if own_client:
        http = httpx.AsyncClient(timeout=httpx.Timeout(300, connect=15))

    last_err: Exception | None = None
    max_attempts = len(pool._slots) * 3
    try:
        for _ in range(max_attempts):
            async with pool.acquire(direct_only=True) as backend:
                try:
                    resp = await http.post(
                        backend.messages_url(),
                        json=_build_request(backend, messages, model, max_tokens, system),
                        headers=backend.api_headers(),
                    )
                except (httpx.ConnectError, httpx.ReadTimeout) as e:
                    pool.report_429(backend)
                    last_err = e
                    continue

                if resp.status_code == 200:
                    text, usage = _parse_response(backend, resp.json())
                    pool.report_success(backend)
                    return text, usage, backend.name

                if resp.status_code == 429:
                    pool.report_429(backend)
                    last_err = RateLimitError(resp.text[:200])
                    continue

                if resp.status_code == 401:
                    pool.report_dead(backend)
                    last_err = APIError(401, resp.text)
                    continue

                if resp.status_code >= 500:
                    last_err = APIError(resp.status_code, resp.text)
                    continue

                raise APIError(resp.status_code, resp.text)

        raise last_err or RuntimeError("All backends exhausted")
    finally:
        if own_client:
            await http.aclose()


def _build_request(
    backend: Backend,
    messages: list[dict],
    model: str,
    max_tokens: int,
    system: str | None,
) -> dict:
    resolved = backend.resolve_model(model)
    if backend.api_format == "openai":
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.extend(messages)
        return {"model": resolved, "max_tokens": max_tokens, "messages": msgs}
    else:
        body: dict = {"model": resolved, "max_tokens": max_tokens, "messages": messages}
        if system:
            body["system"] = system
        return body


def _parse_response(backend: Backend, data: dict) -> tuple[str, dict | None]:
    """Extract (text, usage) from either Anthropic or OpenAI response format."""
    if backend.api_format == "openai":
        choices = data.get("choices", [])
        if choices:
            msg = choices[0].get("message", {})
            text = msg.get("content") or ""
        else:
            text = ""
        usage = data.get("usage")
        return text, usage
    else:
        blocks = data.get("content", [])
        text = "".join(b["text"] for b in blocks if b.get("type") == "text")
        return text, data.get("usage")


# ---------------------------------------------------------------------------
# Output parsing — extract file contents from LLM response
# ---------------------------------------------------------------------------

_FILE_BLOCK = re.compile(
    r"<file\s+path=[\"']([^\"']+)[\"']\s*>\n(.*?)</file>",
    re.DOTALL,
)
_NAMED_FENCE = re.compile(
    r"```(?:python|yaml|toml)?\s+([\w./]+)\n(.*?)```",
    re.DOTALL,
)
_PLAIN_FENCE = re.compile(
    r"```(python|yaml|toml)\n(.*?)```",
    re.DOTALL,
)


def parse_file_blocks(text: str) -> dict[str, str]:
    """Extract named file contents from LLM response.

    Tries, in order:
      1. ``<file path="...">`` XML tags (most explicit)
      2. Fenced blocks with filename: ````` ```python test_outputs.py``
      3. Heuristic: largest ``python`` block → test_outputs.py,
         ``yaml`` block containing ``checks:`` → eval_manifest.yaml
    """
    blocks: dict[str, str] = {}

    # 1. XML-style tags
    for m in _FILE_BLOCK.finditer(text):
        blocks[m.group(1)] = m.group(2).strip()
    if blocks:
        return blocks

    # 2. Named fenced blocks
    for m in _NAMED_FENCE.finditer(text):
        blocks[m.group(1)] = m.group(2).strip()
    if blocks:
        return blocks

    # 3. Heuristic: match by content
    py_blocks = []
    yaml_blocks = []
    for m in _PLAIN_FENCE.finditer(text):
        lang, content = m.group(1), m.group(2).strip()
        if lang == "python":
            py_blocks.append(content)
        elif lang == "yaml":
            yaml_blocks.append(content)

    # Largest python block with test functions → test_outputs.py
    test_blocks = [b for b in py_blocks if "def test_" in b]
    if test_blocks:
        blocks["tests/test_outputs.py"] = max(test_blocks, key=len)

    # YAML block with checks → eval_manifest.yaml
    manifest_blocks = [b for b in yaml_blocks if "checks:" in b or "version:" in b]
    if manifest_blocks:
        blocks["eval_manifest.yaml"] = max(manifest_blocks, key=len)

    return blocks


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def backends_from_env(env_file: Path | None = None) -> list[Backend]:
    """Discover available backends from .env and os.environ."""
    dotenv: dict[str, str] = {}
    ef = env_file or Path(__file__).parent.parent / ".env"
    if ef.exists():
        for line in ef.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            dotenv[k.strip()] = v.strip().strip('"').strip("'")

    def _get(key: str) -> str:
        return os.environ.get(key) or dotenv.get(key, "")

    backends: list[Backend] = []

    # GLM-5.1 — free via Z.AI Anthropic proxy
    if _get("GLM_API_KEY"):
        backends.append(Backend(
            name="glm",
            base_url="https://api.z.ai/api/anthropic",
            api_key=_get("GLM_API_KEY"),
            model_map={"opus": "glm-5.1", "sonnet": "glm-5.1", "haiku": "glm-4.5-air"},
            max_concurrent=4,
            cost_tier=0,
        ))

    # OAuth — subscription, subprocess-only (direct API returns 401)
    oauth_token = os.environ.get("CLAUDE_ACCESS_TOKEN", "")
    if not oauth_token:
        creds = Path.home() / ".claude" / ".credentials_backup.json"
        if creds.exists():
            try:
                oauth_token = json.loads(creds.read_text()).get(
                    "claudeAiOauth", {}
                ).get("accessToken", "")
            except (json.JSONDecodeError, KeyError):
                pass
    if oauth_token:
        backends.append(Backend(
            name="oauth",
            base_url="",
            api_key=oauth_token,
            auth_type="bearer",
            max_concurrent=8,
            cost_tier=1,
            supports_direct=False,
        ))

    # Kimi K2.5 via OpenRouter — cheap, fast, OpenAI format
    if _get("OPENROUTER_API_KEY"):
        backends.append(Backend(
            name="kimi",
            base_url="https://openrouter.ai/api/v1",
            api_key=_get("OPENROUTER_API_KEY"),
            auth_type="bearer",
            api_format="openai",
            model_map={
                "opus": "moonshotai/kimi-k2.5",
                "sonnet": "moonshotai/kimi-k2.5",
                "haiku": "moonshotai/kimi-k2.5",
            },
            max_concurrent=10,
            cost_tier=1,
            supports_subprocess=False,  # needs litellm proxy
        ))

    # Fireworks — if key available, alternative to OpenRouter for Kimi
    if _get("FIREWORKS_API_KEY"):
        backends.append(Backend(
            name="fireworks",
            base_url="https://api.fireworks.ai/inference/v1",
            api_key=_get("FIREWORKS_API_KEY"),
            auth_type="bearer",
            api_format="openai",
            model_map={
                "opus": "accounts/fireworks/models/kimi-k2-5-instruct",
                "sonnet": "accounts/fireworks/models/kimi-k2-5-instruct",
            },
            max_concurrent=10,
            cost_tier=1,
            supports_subprocess=False,
        ))

    # Anthropic API key — pay-per-token, high limits
    if _get("ANTHROPIC_API_KEY"):
        backends.append(Backend(
            name="apikey",
            base_url="",
            api_key=_get("ANTHROPIC_API_KEY"),
            max_concurrent=20,
            cost_tier=2,
        ))

    return backends
