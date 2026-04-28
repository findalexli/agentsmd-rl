"""Behavioral checks for ai-add-dedicated-claudemd-files-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Use project specific exceptions instead of global exception classes like \\RuntimeException, \\InvalidArgumentException etc.' in text, "expected to find: " + '- Use project specific exceptions instead of global exception classes like \\RuntimeException, \\InvalidArgumentException etc.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- NEVER mention Claude as co-author in commits' in text, "expected to find: " + '- NEVER mention Claude as co-author in commits'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('demo/CLAUDE.md')
    assert 'This is a Symfony 7.3 demo application showcasing AI integration capabilities using Symfony AI components. The application demonstrates various AI use cases including RAG (Retrieval Augmented Generati' in text, "expected to find: " + 'This is a Symfony 7.3 demo application showcasing AI integration capabilities using Symfony AI components. The application demonstrates various AI use cases including RAG (Retrieval Augmented Generati'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('demo/CLAUDE.md')
    assert '- **Chat Systems**: Multiple specialized chat implementations in `src/` (Blog, YouTube, Wikipedia, Audio, Stream)' in text, "expected to find: " + '- **Chat Systems**: Multiple specialized chat implementations in `src/` (Blog, YouTube, Wikipedia, Audio, Stream)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('demo/CLAUDE.md')
    assert "Chat history stored in Symfony sessions with component-specific keys (e.g., 'blog-chat', 'stream-chat')." in text, "expected to find: " + "Chat history stored in Symfony sessions with component-specific keys (e.g., 'blog-chat', 'stream-chat')."[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('examples/CLAUDE.md')
    assert 'This is the examples directory of the Symfony AI monorepo, containing standalone examples demonstrating component usage across different AI platforms. The examples serve as both reference implementati' in text, "expected to find: " + 'This is the examples directory of the Symfony AI monorepo, containing standalone examples demonstrating component usage across different AI platforms. The examples serve as both reference implementati'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('examples/CLAUDE.md')
    assert 'Examples serve as integration tests. The runner executes them in parallel to verify all components work correctly across different platforms.' in text, "expected to find: " + 'Examples serve as integration tests. The runner executes them in parallel to verify all components work correctly across different platforms.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('examples/CLAUDE.md')
    assert 'Examples require API keys configured in `.env.local`. Copy from `.env` template and add your keys for the platforms you want to test.' in text, "expected to find: " + 'Examples require API keys configured in `.env.local`. Copy from `.env` template and add your keys for the platforms you want to test.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('src/agent/CLAUDE.md')
    assert 'The Agent component provides a framework for building AI agents that interact with users and perform tasks. It sits on top of the Platform component and optionally integrates with the Store component ' in text, "expected to find: " + 'The Agent component provides a framework for building AI agents that interact with users and perform tasks. It sits on top of the Platform component and optionally integrates with the Store component '[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('src/agent/CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with code in the Agent component.' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with code in the Agent component.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('src/agent/CLAUDE.md')
    assert '- **OutputProcessorInterface** (`src/OutputProcessorInterface.php`): Contract for output processors' in text, "expected to find: " + '- **OutputProcessorInterface** (`src/OutputProcessorInterface.php`): Contract for output processors'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('src/ai-bundle/CLAUDE.md')
    assert 'The Symfony AI Bundle is an integration bundle that provides Symfony dependency injection configuration for the Symfony AI components (Platform, Agent, Store). It enables declarative configuration of ' in text, "expected to find: " + 'The Symfony AI Bundle is an integration bundle that provides Symfony dependency injection configuration for the Symfony AI components (Platform, Agent, Store). It enables declarative configuration of '[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('src/ai-bundle/CLAUDE.md')
    assert "This bundle follows the parent monorepo's PHP CS Fixer configuration. Code style fixes should be run from the monorepo root." in text, "expected to find: " + "This bundle follows the parent monorepo's PHP CS Fixer configuration. Code style fixes should be run from the monorepo root."[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('src/ai-bundle/CLAUDE.md')
    assert '- **Platform Integration**: Configures AI platforms (OpenAI, Anthropic, Azure, Gemini, etc.) as services' in text, "expected to find: " + '- **Platform Integration**: Configures AI platforms (OpenAI, Anthropic, Azure, Gemini, etc.) as services'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('src/platform/CLAUDE.md')
    assert 'This is the Platform component of the Symfony AI monorepo - a unified abstraction for interacting with AI platforms like OpenAI, Anthropic, Azure, Gemini, VertexAI, Ollama, and others. The component p' in text, "expected to find: " + 'This is the Platform component of the Symfony AI monorepo - a unified abstraction for interacting with AI platforms like OpenAI, Anthropic, Azure, Gemini, VertexAI, Ollama, and others. The component p'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('src/platform/CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('src/platform/CLAUDE.md')
    assert '- **Contract**: Abstract contracts for different AI capabilities (chat, embedding, speech, etc.)' in text, "expected to find: " + '- **Contract**: Abstract contracts for different AI capabilities (chat, embedding, speech, etc.)'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('src/store/CLAUDE.md')
    assert 'This is the Store component of the Symfony AI ecosystem, providing a low-level abstraction for storing and retrieving documents in vector stores. The component enables Retrieval Augmented Generation (' in text, "expected to find: " + 'This is the Store component of the Symfony AI ecosystem, providing a low-level abstraction for storing and retrieving documents in vector stores. The component enables Retrieval Augmented Generation ('[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('src/store/CLAUDE.md')
    assert 'Tests follow the same bridge structure as source code, with each store implementation having corresponding test classes. Tests use PHPUnit 11+ with strict configuration for coverage and error handling' in text, "expected to find: " + 'Tests follow the same bridge structure as source code, with each store implementation having corresponding test classes. Tests use PHPUnit 11+ with strict configuration for coverage and error handling'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('src/store/CLAUDE.md')
    assert '- **ManagedStoreInterface**: Extension interface providing `setup()` and `drop()` methods for store lifecycle management' in text, "expected to find: " + '- **ManagedStoreInterface**: Extension interface providing `setup()` and `drop()` methods for store lifecycle management'[:80]

