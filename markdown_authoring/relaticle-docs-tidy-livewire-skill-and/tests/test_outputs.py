"""Behavioral checks for relaticle-docs-tidy-livewire-skill-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/relaticle")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/livewire-development/SKILL.md')
    assert 'Before creating a component, check `config/livewire.php` for directory overrides, which change where files are stored. Then, look at existing files in those directories (defaulting to `app/Livewire/` ' in text, "expected to find: " + 'Before creating a component, check `config/livewire.php` for directory overrides, which change where files are stored. Then, look at existing files in those directories (defaulting to `app/Livewire/` '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/livewire-development/SKILL.md')
    assert 'Namespaced components map to subdirectories: `make:livewire Posts/CreatePost` creates files at `app/Livewire/Posts/CreatePost.php` and `resources/views/livewire/posts/create-post.blade.php`.' in text, "expected to find: " + 'Namespaced components map to subdirectories: `make:livewire Posts/CreatePost` creates files at `app/Livewire/Posts/CreatePost.php` and `resources/views/livewire/posts/create-post.blade.php`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/livewire-development/SKILL.md')
    assert '| View-based | ⚡ prefix | — | `resources/views/livewire/create-post.blade.php` (Blade-only with functional state) |' in text, "expected to find: " + '| View-based | ⚡ prefix | — | `resources/views/livewire/create-post.blade.php` (Blade-only with functional state) |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Laravel can be deployed using [Laravel Cloud](https://cloud.laravel.com/), which is the fastest way to deploy and scale production Laravel applications.' in text, "expected to find: " + '- Laravel can be deployed using [Laravel Cloud](https://cloud.laravel.com/), which is the fastest way to deploy and scale production Laravel applications.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '## Deployment' in text, "expected to find: " + '## Deployment'[:80]

