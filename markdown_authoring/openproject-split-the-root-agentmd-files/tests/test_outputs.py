"""Behavioral checks for openproject-split-the-root-agentmd-files (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openproject")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'See [`docker/dev/AGENTS.md`](docker/dev/AGENTS.md) for full Docker setup and commands.' in text, "expected to find: " + 'See [`docker/dev/AGENTS.md`](docker/dev/AGENTS.md) for full Docker setup and commands.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `.github/copilot-instructions.md` — Extended agent instructions with troubleshooting' in text, "expected to find: " + '- `.github/copilot-instructions.md` — Extended agent instructions with troubleshooting'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `lookbook/` — ViewComponent previews (<https://qa.openproject-edge.com/lookbook/>)' in text, "expected to find: " + '- `lookbook/` — ViewComponent previews (<https://qa.openproject-edge.com/lookbook/>)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('app/AGENTS.md')
    assert '- Follow [Ruby community style guide](https://github.com/bbatsov/ruby-style-guide)' in text, "expected to find: " + '- Follow [Ruby community style guide](https://github.com/bbatsov/ruby-style-guide)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('app/AGENTS.md')
    assert '- Use service objects for complex business logic (return `ServiceResult`)' in text, "expected to find: " + '- Use service objects for complex business logic (return `ServiceResult`)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('app/AGENTS.md')
    assert '- `app/components/` - ViewComponent-based UI components (Ruby + ERB)' in text, "expected to find: " + '- `app/components/` - ViewComponent-based UI components (Ruby + ERB)'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('app/CLAUDE.md')
    assert 'app/CLAUDE.md' in text, "expected to find: " + 'app/CLAUDE.md'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('config/AGENTS.md')
    assert 'bundle exec i18n-tasks check-consistent-interpolations  # Check interpolation consistency' in text, "expected to find: " + 'bundle exec i18n-tasks check-consistent-interpolations  # Check interpolation consistency'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('config/AGENTS.md')
    assert 'bundle exec i18n-tasks normalize                      # Fix/normalize translation files' in text, "expected to find: " + 'bundle exec i18n-tasks normalize                      # Fix/normalize translation files'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('config/AGENTS.md')
    assert 'bundle exec i18n-tasks missing                        # Show missing translation keys' in text, "expected to find: " + 'bundle exec i18n-tasks missing                        # Show missing translation keys'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('config/CLAUDE.md')
    assert 'config/CLAUDE.md' in text, "expected to find: " + 'config/CLAUDE.md'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('db/AGENTS.md')
    assert '**CRITICAL**: `config/database.yml` must NOT exist when using Docker (rename or delete it)' in text, "expected to find: " + '**CRITICAL**: `config/database.yml` must NOT exist when using Docker (rename or delete it)'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('db/AGENTS.md')
    assert '- Migrations are "squashed" between major releases (see `docs/development/migrations/`)' in text, "expected to find: " + '- Migrations are "squashed" between major releases (see `docs/development/migrations/`)'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('db/AGENTS.md')
    assert 'bin/compose exec backend bundle exec rails db:migrate      # Run migrations' in text, "expected to find: " + 'bin/compose exec backend bundle exec rails db:migrate      # Run migrations'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('db/CLAUDE.md')
    assert 'db/CLAUDE.md' in text, "expected to find: " + 'db/CLAUDE.md'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('docker/dev/AGENTS.md')
    assert 'bin/compose run                           # Start frontend in background, backend in foreground (for debugging with pry)' in text, "expected to find: " + 'bin/compose run                           # Start frontend in background, backend in foreground (for debugging with pry)'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('docker/dev/AGENTS.md')
    assert 'The Docker development environment uses configurations in `docker/dev/` and the `bin/compose` wrapper script.' in text, "expected to find: " + 'The Docker development environment uses configurations in `docker/dev/` and the `bin/compose` wrapper script.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('docker/dev/AGENTS.md')
    assert '- Most developers use a local `docker-compose.override.yml` for custom port mappings and configurations' in text, "expected to find: " + '- Most developers use a local `docker-compose.override.yml` for custom port mappings and configurations'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('docker/dev/CLAUDE.md')
    assert 'docker/dev/CLAUDE.md' in text, "expected to find: " + 'docker/dev/CLAUDE.md'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('frontend/AGENTS.md')
    assert '- **New development**: Use Hotwire (Turbo + Stimulus) with server-rendered HTML' in text, "expected to find: " + '- **New development**: Use Hotwire (Turbo + Stimulus) with server-rendered HTML'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('frontend/AGENTS.md')
    assert '- Use [Primer Design System](https://primer.style/product/) via ViewComponent' in text, "expected to find: " + '- Use [Primer Design System](https://primer.style/product/) via ViewComponent'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('frontend/AGENTS.md')
    assert '- `../package.json` / `./frontend/package.json` - Node.js dependencies' in text, "expected to find: " + '- `../package.json` / `./frontend/package.json` - Node.js dependencies'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('frontend/CLAUDE.md')
    assert 'frontend/CLAUDE.md' in text, "expected to find: " + 'frontend/CLAUDE.md'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('spec/AGENTS.md')
    assert 'bin/compose rspec spec/models/user_spec.rb   # Run specific tests in backend-test container' in text, "expected to find: " + 'bin/compose rspec spec/models/user_spec.rb   # Run specific tests in backend-test container'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('spec/AGENTS.md')
    assert 'bin/compose exec backend bundle exec rspec    # Run tests directly in backend container' in text, "expected to find: " + 'bin/compose exec backend bundle exec rspec    # Run tests directly in backend container'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('spec/AGENTS.md')
    assert './script/github_pr_errors | xargs bundle exec rspec    # Run failed tests from CI' in text, "expected to find: " + './script/github_pr_errors | xargs bundle exec rspec    # Run failed tests from CI'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('spec/CLAUDE.md')
    assert 'spec/CLAUDE.md' in text, "expected to find: " + 'spec/CLAUDE.md'[:80]

