"""Behavioral checks for dotnet-skills-add-rememberentities-guidance-test-config (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dotnet-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/akka/hosting-actor-patterns/SKILL.md')
    assert 'When using `WithShardRegion<T>`, the generic parameter `T` serves as a marker type for the `ActorRegistry`. Use a dedicated marker type (not the actor class itself) for consistent registry access:' in text, "expected to find: " + 'When using `WithShardRegion<T>`, the generic parameter `T` serves as a marker type for the `ActorRegistry`. Use a dedicated marker type (not the actor class itself) for consistent registry access:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/akka/hosting-actor-patterns/SKILL.md')
    assert '`RememberEntities` controls whether the shard region remembers and automatically restarts all entities that were ever created. **This should almost always be `false`.**' in text, "expected to find: " + '`RememberEntities` controls whether the shard region remembers and automatically restarts all entities that were ever created. **This should almost always be `false`.**'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/akka/hosting-actor-patterns/SKILL.md')
    assert "`WithShardRegion<T>` automatically registers the shard region in the `ActorRegistry`. Don't call `registry.Register<T>()` again:" in text, "expected to find: " + "`WithShardRegion<T>` automatically registers the shard region in the `ActorRegistry`. Don't call `registry.Register<T>()` again:"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/akka/testing-patterns/SKILL.md')
    assert 'When your production code uses custom `AkkaConfigurationBuilder` extension methods (for serializers, actors, persistence), your tests should use those same extension methods rather than duplicating HO' in text, "expected to find: " + 'When your production code uses custom `AkkaConfigurationBuilder` extension methods (for serializers, actors, persistence), your tests should use those same extension methods rather than duplicating HO'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/akka/testing-patterns/SKILL.md')
    assert 'protected override void ConfigureAkka(AkkaConfigurationBuilder builder, IServiceProvider provider)' in text, "expected to find: " + 'protected override void ConfigureAkka(AkkaConfigurationBuilder builder, IServiceProvider provider)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/akka/testing-patterns/SKILL.md')
    assert '| **Easier Maintenance** | Add a new binding in one place, tests automatically pick it up |' in text, "expected to find: " + '| **Easier Maintenance** | Add a new binding in one place, tests automatically pick it up |'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/aspire/integration-testing/SKILL.md')
    assert 'Design your AppHost to support different configurations for interactive development (F5/CLI) vs automated test fixtures. The pattern goes beyond just volumes - it covers execution modes, authenticatio' in text, "expected to find: " + 'Design your AppHost to support different configurations for interactive development (F5/CLI) vs automated test fixtures. The pattern goes beyond just volumes - it covers execution modes, authenticatio'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/aspire/integration-testing/SKILL.md')
    assert '> **Default to production-like behavior in AppHost.** Tests explicitly override what they need to be different. This catches configuration gaps early (e.g., missing DI registrations that only surface ' in text, "expected to find: " + '> **Default to production-like behavior in AppHost.** Tests explicitly override what they need to be different. This catches configuration gaps early (e.g., missing DI registrations that only surface '[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/aspire/integration-testing/SKILL.md')
    assert 'Tests explicitly opt-out of specific production behaviors rather than opting-in to a test mode that might miss real issues.' in text, "expected to find: " + 'Tests explicitly opt-out of specific production behaviors rather than opting-in to a test mode that might miss real issues.'[:80]

