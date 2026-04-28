"""Behavioral checks for tambo-chore-add-agentsmd-claudemd-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tambo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Make non-breaking changes to the code. Only make breaking changes if the user specifically asks for it. Ensure you warn them about the breaking changes.' in text, "expected to find: " + '- Make non-breaking changes to the code. Only make breaking changes if the user specifically asks for it. Ensure you warn them about the breaking changes.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is a Turborepo monorepo for the Tambo AI framework. The repository contains multiple packages:' in text, "expected to find: " + 'This is a Turborepo monorepo for the Tambo AI framework. The repository contains multiple packages:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- If tests fail, do not just change the code to make the tests pass. Take one of 2 approaches:' in text, "expected to find: " + '- If tests fail, do not just change the code to make the tests pass. Take one of 2 approaches:'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and development workflows.**' in text, "expected to find: " + '**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and development workflows.**'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'For detailed information on architecture, development patterns, and cross-package workflows, see [AGENTS.md](./AGENTS.md).' in text, "expected to find: " + 'For detailed information on architecture, development patterns, and cross-package workflows, see [AGENTS.md](./AGENTS.md).'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('cli/AGENTS.md')
    assert 'The Tambo CLI (`tambo`) is a command-line tool for scaffolding, managing, and extending Tambo AI applications. It provides component generation, project initialization, dependency management, and deve' in text, "expected to find: " + 'The Tambo CLI (`tambo`) is a command-line tool for scaffolding, managing, and extending Tambo AI applications. It provides component generation, project initialization, dependency management, and deve'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('cli/AGENTS.md')
    assert 'We have a doc-first approach to developing new features in our CLI. This means we write the documentation first, then write the code to implement the feature. Our docs are in the docs site (read Docs/' in text, "expected to find: " + 'We have a doc-first approach to developing new features in our CLI. This means we write the documentation first, then write the code to implement the feature. Our docs are in the docs site (read Docs/'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('cli/AGENTS.md')
    assert '3. Before writing any code, write a detailed description of the feature in the docs site' in text, "expected to find: " + '3. Before writing any code, write a detailed description of the feature in the docs site'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('cli/CLAUDE.md')
    assert '**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and command workflows.**' in text, "expected to find: " + '**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and command workflows.**'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('cli/CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('cli/CLAUDE.md')
    assert 'The Tambo CLI (`tambo`) - command-line tool for scaffolding and managing Tambo AI applications.' in text, "expected to find: " + 'The Tambo CLI (`tambo`) - command-line tool for scaffolding and managing Tambo AI applications.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('create-tambo-app/AGENTS.md')
    assert "The `create-tambo-app` package is a lightweight bootstrapper that creates new Tambo AI applications. It acts as a proxy to the latest version of the `tambo` CLI's `create-app` command." in text, "expected to find: " + "The `create-tambo-app` package is a lightweight bootstrapper that creates new Tambo AI applications. It acts as a proxy to the latest version of the `tambo` CLI's `create-app` command."[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('create-tambo-app/AGENTS.md')
    assert "Since this is a simple proxy, most functionality changes should be made in the main `tambo` CLI's `create-app` command rather than here." in text, "expected to find: " + "Since this is a simple proxy, most functionality changes should be made in the main `tambo` CLI's `create-app` command rather than here."[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('create-tambo-app/AGENTS.md')
    assert 'Detailed guidance for Claude Code agents working with the create-tambo-app package.' in text, "expected to find: " + 'Detailed guidance for Claude Code agents working with the create-tambo-app package.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('create-tambo-app/CLAUDE.md')
    assert '**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and proxy patterns.**' in text, "expected to find: " + '**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and proxy patterns.**'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('create-tambo-app/CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('create-tambo-app/CLAUDE.md')
    assert 'The `create-tambo-app` package - lightweight bootstrapper for creating new Tambo AI applications.' in text, "expected to find: " + 'The `create-tambo-app` package - lightweight bootstrapper for creating new Tambo AI applications.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert "The documentation follows a **progressive disclosure** pattern - starting with quick wins (quickstart), moving through core concepts, then diving into specifics. This structure mirrors the user's lear" in text, "expected to find: " + "The documentation follows a **progressive disclosure** pattern - starting with quick wins (quickstart), moving through core concepts, then diving into specifics. This structure mirrors the user's lear"[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert 'The Docs package (`@tambo-ai/docs`) is a Next.js application serving as the official Tambo AI documentation site. Built with Fumadocs, it provides comprehensive guides, API reference, and interactive ' in text, "expected to find: " + 'The Docs package (`@tambo-ai/docs`) is a Next.js application serving as the official Tambo AI documentation site. Built with Fumadocs, it provides comprehensive guides, API reference, and interactive '[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert 'Please update the `Information Architecture` section in the AGENTS.md file to reflect changes when you make them. Keeping this up to date is VERY IMPORTANT.' in text, "expected to find: " + 'Please update the `Information Architecture` section in the AGENTS.md file to reflect changes when you make them. Keeping this up to date is VERY IMPORTANT.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/CLAUDE.md')
    assert '**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and content workflows.**' in text, "expected to find: " + '**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and content workflows.**'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/CLAUDE.md')
    assert 'The Docs package (`@tambo-ai/docs`) - Next.js documentation site built with Fumadocs.' in text, "expected to find: " + 'The Docs package (`@tambo-ai/docs`) - Next.js documentation site built with Fumadocs.'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('react-sdk/AGENTS.md')
    assert 'This is the **@tambo-ai/react** package - the core React SDK for building AI-powered generative UI applications. It provides hooks, providers, and utilities that enable AI to dynamically generate and ' in text, "expected to find: " + 'This is the **@tambo-ai/react** package - the core React SDK for building AI-powered generative UI applications. It provides hooks, providers, and utilities that enable AI to dynamically generate and '[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('react-sdk/AGENTS.md')
    assert 'We have a doc-first approach to developing new features in our React SDK. This means we write the documentation first, then write the code to implement the feature. Our docs are in the docs site (read' in text, "expected to find: " + 'We have a doc-first approach to developing new features in our React SDK. This means we write the documentation first, then write the code to implement the feature. Our docs are in the docs site (read'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('react-sdk/AGENTS.md')
    assert '3. Before writing any code, write a detailed description of the feature in the docs site' in text, "expected to find: " + '3. Before writing any code, write a detailed description of the feature in the docs site'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('react-sdk/CLAUDE.md')
    assert '**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and development patterns.**' in text, "expected to find: " + '**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and development patterns.**'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('react-sdk/CLAUDE.md')
    assert 'The **@tambo-ai/react** package - the core React SDK for AI-powered generative UI applications.' in text, "expected to find: " + 'The **@tambo-ai/react** package - the core React SDK for AI-powered generative UI applications.'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('react-sdk/CLAUDE.md')
    assert '## Quick Reference' in text, "expected to find: " + '## Quick Reference'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('showcase/AGENTS.md')
    assert 'The Showcase (`@tambo-ai/showcase`) is a Next.js application that demonstrates all Tambo AI components and patterns. It serves as both a component library browser and an interactive testing ground for' in text, "expected to find: " + 'The Showcase (`@tambo-ai/showcase`) is a Next.js application that demonstrates all Tambo AI components and patterns. It serves as both a component library browser and an interactive testing ground for'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('showcase/AGENTS.md')
    assert '- **Generative Interfaces**: `src/components/generative/` - AI-powered chat demos' in text, "expected to find: " + '- **Generative Interfaces**: `src/components/generative/` - AI-powered chat demos'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('showcase/AGENTS.md')
    assert 'Detailed guidance for Claude Code agents working with the Showcase package.' in text, "expected to find: " + 'Detailed guidance for Claude Code agents working with the Showcase package.'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('showcase/CLAUDE.md')
    assert '**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and component patterns.**' in text, "expected to find: " + '**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and component patterns.**'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('showcase/CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('showcase/CLAUDE.md')
    assert 'The Showcase (`@tambo-ai/showcase`) - Next.js demo application showcasing all Tambo AI components.' in text, "expected to find: " + 'The Showcase (`@tambo-ai/showcase`) - Next.js demo application showcasing all Tambo AI components.'[:80]

