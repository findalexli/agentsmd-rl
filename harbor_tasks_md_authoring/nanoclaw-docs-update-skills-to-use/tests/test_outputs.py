"""Behavioral checks for nanoclaw-docs-update-skills-to-use (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanoclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-discord/modify/src/index.ts.intent.md')
    assert '- Container runtime check is unchanged (ensureContainerSystemRunning)' in text, "expected to find: " + '- Container runtime check is unchanged (ensureContainerSystemRunning)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-parallel/SKILL.md')
    assert 'echo \'{}\' | docker run -i --entrypoint /bin/echo nanoclaw-agent:latest "Container OK"' in text, "expected to find: " + 'echo \'{}\' | docker run -i --entrypoint /bin/echo nanoclaw-agent:latest "Container OK"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-parallel/SKILL.md')
    assert '3. Docker installed and running' in text, "expected to find: " + '3. Docker installed and running'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-telegram/modify/src/index.ts.intent.md')
    assert '- Container runtime check is unchanged (ensureContainerSystemRunning)' in text, "expected to find: " + '- Container runtime check is unchanged (ensureContainerSystemRunning)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-voice-transcription/SKILL.md')
    assert '### Step 7: Test Voice Transcription' in text, "expected to find: " + '### Step 7: Test Voice Transcription'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-voice-transcription/SKILL.md')
    assert '### Step 6: Build and Restart' in text, "expected to find: " + '### Step 6: Build and Restart'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-voice-transcription/SKILL.md')
    assert 'Verify it started:' in text, "expected to find: " + 'Verify it started:'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/debug/SKILL.md')
    assert 'echo \'{}\' | docker run -i --entrypoint /bin/echo nanoclaw-agent:latest "OK" 2>/dev/null || echo "MISSING - run ./container/build.sh"' in text, "expected to find: " + 'echo \'{}\' | docker run -i --entrypoint /bin/echo nanoclaw-agent:latest "OK" 2>/dev/null || echo "MISSING - run ./container/build.sh"'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/debug/SKILL.md')
    assert 'docker info &>/dev/null && echo "OK" || echo "NOT RUNNING - start Docker Desktop (macOS) or sudo systemctl start docker (Linux)"' in text, "expected to find: " + 'docker info &>/dev/null && echo "OK" || echo "NOT RUNNING - start Docker Desktop (macOS) or sudo systemctl start docker (Linux)"'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/debug/SKILL.md')
    assert "docker run --rm --entrypoint /bin/bash nanoclaw-agent:latest -c 'ls -la /workspace/'" in text, "expected to find: " + "docker run --rm --entrypoint /bin/bash nanoclaw-agent:latest -c 'ls -la /workspace/'"[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup/SKILL.md')
    assert "**If APPLE_CONTAINER=installed** (macOS only): Ask the user which runtime they'd like to use — Docker (default, cross-platform) or Apple Container (native macOS). If they choose Apple Container, run `" in text, "expected to find: " + "**If APPLE_CONTAINER=installed** (macOS only): Ask the user which runtime they'd like to use — Docker (default, cross-platform) or Apple Container (native macOS). If they choose Apple Container, run `"[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup/SKILL.md')
    assert '- DOCKER=installed_not_running → start Docker: `open -a Docker` (macOS) or `sudo systemctl start docker` (Linux). Wait 15s, re-check with `docker info`. If still not running, tell the user Docker is s' in text, "expected to find: " + '- DOCKER=installed_not_running → start Docker: `open -a Docker` (macOS) or `sudo systemctl start docker` (Linux). Wait 15s, re-check with `docker info`. If still not running, tell the user Docker is s'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup/SKILL.md')
    assert '- macOS: install via `brew install --cask docker`, then `open -a Docker` and wait for it to start. If brew not available, direct to Docker Desktop download at https://docker.com/products/docker-deskto' in text, "expected to find: " + '- macOS: install via `brew install --cask docker`, then `open -a Docker` and wait for it to start. If brew not available, direct to Docker Desktop download at https://docker.com/products/docker-deskto'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/x-integration/SKILL.md')
    assert 'docker build -t "${IMAGE_NAME}:${TAG}" -f container/Dockerfile .' in text, "expected to find: " + 'docker build -t "${IMAGE_NAME}:${TAG}" -f container/Dockerfile .'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/x-integration/SKILL.md')
    assert 'docker run nanoclaw-agent ls -la /app/src/skills/' in text, "expected to find: " + 'docker run nanoclaw-agent ls -la /app/src/skills/'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/x-integration/SKILL.md')
    assert 'docker build -t "${IMAGE_NAME}:${TAG}" .' in text, "expected to find: " + 'docker build -t "${IMAGE_NAME}:${TAG}" .'[:80]

