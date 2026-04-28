"""Behavioral checks for medusa-chore-add-claude-skills-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/medusa")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/api-ref-doc/SKILL.md')
    assert 'Write or update API reference markdown pages in the `www/apps/api-reference/markdown/` directory. These pages document authentication methods, query parameters, pagination patterns, and other common A' in text, "expected to find: " + 'Write or update API reference markdown pages in the `www/apps/api-reference/markdown/` directory. These pages document authentication methods, query parameters, pagination patterns, and other common A'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/api-ref-doc/SKILL.md')
    assert '- [www/apps/api-reference/markdown/client-libraries.mdx](www/apps/api-reference/markdown/client-libraries.mdx)' in text, "expected to find: " + '- [www/apps/api-reference/markdown/client-libraries.mdx](www/apps/api-reference/markdown/client-libraries.mdx)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/api-ref-doc/SKILL.md')
    assert '- **Hand-written MDX** for common patterns and authentication (admin.mdx, store.mdx, client-libraries.mdx)' in text, "expected to find: " + '- **Hand-written MDX** for common patterns and authentication (admin.mdx, store.mdx, client-libraries.mdx)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/book-doc/SKILL.md')
    assert 'Write conceptual, tutorial, or configuration pages for the main Medusa documentation in `www/apps/book/app/learn/`. These pages form the core learning path for developers, covering fundamentals, custo' in text, "expected to find: " + 'Write conceptual, tutorial, or configuration pages for the main Medusa documentation in `www/apps/book/app/learn/`. These pages form the core learning path for developers, covering fundamentals, custo'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/book-doc/SKILL.md')
    assert '- Tutorial: [www/apps/book/app/learn/fundamentals/events-and-subscribers/page.mdx](www/apps/book/app/learn/fundamentals/events-and-subscribers/page.mdx)' in text, "expected to find: " + '- Tutorial: [www/apps/book/app/learn/fundamentals/events-and-subscribers/page.mdx](www/apps/book/app/learn/fundamentals/events-and-subscribers/page.mdx)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/book-doc/SKILL.md')
    assert '- Reference: [www/apps/book/app/learn/configurations/medusa-config/page.mdx](www/apps/book/app/learn/configurations/medusa-config/page.mdx)' in text, "expected to find: " + '- Reference: [www/apps/book/app/learn/configurations/medusa-config/page.mdx](www/apps/book/app/learn/configurations/medusa-config/page.mdx)'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/how-to/SKILL.md')
    assert 'Write concise 4-6 step how-to guides in `www/apps/resources/app/` that show developers how to accomplish specific tasks. These guides are more focused than tutorials, targeting developers who need to ' in text, "expected to find: " + 'Write concise 4-6 step how-to guides in `www/apps/resources/app/` that show developers how to accomplish specific tasks. These guides are more focused than tutorials, targeting developers who need to '[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/how-to/SKILL.md')
    assert 'You are an expert technical writer specializing in focused, task-oriented how-to guides for the Medusa ecommerce platform.' in text, "expected to find: " + 'You are an expert technical writer specializing in focused, task-oriented how-to guides for the Medusa ecommerce platform.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/how-to/SKILL.md')
    assert '- Where to place it? (suggest `/app/recipes/{domain}/page.mdx` or `/app/how-to-tutorials/{name}/page.mdx`)' in text, "expected to find: " + '- Where to place it? (suggest `/app/recipes/{domain}/page.mdx` or `/app/how-to-tutorials/{name}/page.mdx`)'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/recipe/SKILL.md')
    assert 'Write conceptual "recipe" guides in `www/apps/resources/app/recipes/` that explain architectural patterns and link to detailed implementation guides. Recipes answer "how should I architect this?" rath' in text, "expected to find: " + 'Write conceptual "recipe" guides in `www/apps/resources/app/recipes/` that explain architectural patterns and link to detailed implementation guides. Recipes answer "how should I architect this?" rath'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/recipe/SKILL.md')
    assert 'You are an expert technical writer specializing in architectural pattern documentation for the Medusa ecommerce platform.' in text, "expected to find: " + 'You are an expert technical writer specializing in architectural pattern documentation for the Medusa ecommerce platform.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/recipe/SKILL.md')
    assert '- [www/apps/resources/app/recipes/digital-products/page.mdx](www/apps/resources/app/recipes/digital-products/page.mdx)' in text, "expected to find: " + '- [www/apps/resources/app/recipes/digital-products/page.mdx](www/apps/resources/app/recipes/digital-products/page.mdx)'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/resources-doc/SKILL.md')
    assert 'Medusa has {feature} related features available out-of-the-box through the {Module Name} Module. A [module](!docs!/learn/fundamentals/modules) is a standalone package that provides features for a sing' in text, "expected to find: " + 'Medusa has {feature} related features available out-of-the-box through the {Module Name} Module. A [module](!docs!/learn/fundamentals/modules) is a standalone package that provides features for a sing'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/resources-doc/SKILL.md')
    assert 'Write general reference documentation in `www/apps/resources/app/` for commerce modules, infrastructure modules, integrations, and other technical references. This is the main skill for Resources docu' in text, "expected to find: " + 'Write general reference documentation in `www/apps/resources/app/` for commerce modules, infrastructure modules, integrations, and other technical references. This is the main skill for Resources docu'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/resources-doc/SKILL.md')
    assert 'In your Medusa application, you build flows around Commerce Modules. A flow is built as a [Workflow](!docs!/learn/fundamentals/workflows), which is a special function composed of a series of steps tha' in text, "expected to find: " + 'In your Medusa application, you build flows around Commerce Modules. A flow is built as a [Workflow](!docs!/learn/fundamentals/workflows), which is a special function composed of a series of steps tha'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tutorial/SKILL.md')
    assert 'Write detailed 10+ step tutorials in `www/apps/resources/app/` that guide developers through complete feature implementations. These tutorials combine conceptual understanding with hands-on coding acr' in text, "expected to find: " + 'Write detailed 10+ step tutorials in `www/apps/resources/app/` that guide developers through complete feature implementations. These tutorials combine conceptual understanding with hands-on coding acr'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tutorial/SKILL.md')
    assert '- [www/apps/resources/app/examples/guides/custom-item-price/page.mdx](www/apps/resources/app/examples/guides/custom-item-price/page.mdx)' in text, "expected to find: " + '- [www/apps/resources/app/examples/guides/custom-item-price/page.mdx](www/apps/resources/app/examples/guides/custom-item-price/page.mdx)'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tutorial/SKILL.md')
    assert '- [www/apps/resources/app/examples/guides/quote-management/page.mdx](www/apps/resources/app/examples/guides/quote-management/page.mdx)' in text, "expected to find: " + '- [www/apps/resources/app/examples/guides/quote-management/page.mdx](www/apps/resources/app/examples/guides/quote-management/page.mdx)'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ui-component-doc/SKILL.md')
    assert 'Write documentation for Medusa UI components in `www/apps/ui/`, including both the MDX documentation pages and live TSX example files. This involves a two-file system: documentation with embedded exam' in text, "expected to find: " + 'Write documentation for Medusa UI components in `www/apps/ui/`, including both the MDX documentation pages and live TSX example files. This involves a two-file system: documentation with embedded exam'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ui-component-doc/SKILL.md')
    assert '- **Component specs**: `specs/components/{Component}/{Component}.json` with TypeScript prop documentation (auto-generated)' in text, "expected to find: " + '- **Component specs**: `specs/components/{Component}/{Component}.json` with TypeScript prop documentation (auto-generated)'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ui-component-doc/SKILL.md')
    assert 'You are an expert technical writer specializing in UI component library documentation for the Medusa UI design system.' in text, "expected to find: " + 'You are an expert technical writer specializing in UI component library documentation for the Medusa UI design system.'[:80]

