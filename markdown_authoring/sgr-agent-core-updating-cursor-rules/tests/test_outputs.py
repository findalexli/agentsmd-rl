"""Behavioral checks for sgr-agent-core-updating-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sgr-agent-core")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/architecture.mdc')
    assert 'The project uses **modular architecture with clear separation of concerns**. The framework implements Schema-Guided Reasoning (SGR) for building intelligent research agents.' in text, "expected to find: " + 'The project uses **modular architecture with clear separation of concerns**. The framework implements Schema-Guided Reasoning (SGR) for building intelligent research agents.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/architecture.mdc')
    assert '1. **One class at a time**: When implementing new functionality, create one class at a time, starting from lower layers' in text, "expected to find: " + '1. **One class at a time**: When implementing new functionality, create one class at a time, starting from lower layers'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/architecture.mdc')
    assert '5. **Registry pattern**: Use registries for automatic discovery of agents and tools' in text, "expected to find: " + '5. **Registry pattern**: Use registries for automatic discovery of agents and tools'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/code-style.mdc')
    assert 'def create_agent(self, agent_def: AgentDefinition, task_messages: list[dict]) -> BaseAgent:' in text, "expected to find: " + 'def create_agent(self, agent_def: AgentDefinition, task_messages: list[dict]) -> BaseAgent:'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/code-style.mdc')
    assert '3. **Empty line at end of file**: Always add an empty line at the end of new files' in text, "expected to find: " + '3. **Empty line at end of file**: Always add an empty line at the end of new files'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/code-style.mdc')
    assert '4. **Virtual environment**: Virtual environment is located in `.venv` directory' in text, "expected to find: " + '4. **Virtual environment**: Virtual environment is located in `.venv` directory'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/core-modules.mdc')
    assert '- Contains: reasoning_steps, current_situation, plan_status, enough_data, remaining_steps, task_completed' in text, "expected to find: " + '- Contains: reasoning_steps, current_situation, plan_status, enough_data, remaining_steps, task_completed'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/core-modules.mdc')
    assert '- Must be subclassed to implement `_reasoning_phase()`, `_select_action_phase()`, `_action_phase()`' in text, "expected to find: " + '- Must be subclassed to implement `_reasoning_phase()`, `_select_action_phase()`, `_action_phase()`'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/core-modules.mdc')
    assert '- Contains: name, base_class, tools, llm, prompts, execution, search, mcp configs' in text, "expected to find: " + '- Contains: name, base_class, tools, llm, prompts, execution, search, mcp configs'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/implementation-order.mdc')
    assert 'When adding new functionality, follow **"one class at a time"** principle, starting from lower architecture layers.' in text, "expected to find: " + 'When adding new functionality, follow **"one class at a time"** principle, starting from lower architecture layers.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/implementation-order.mdc')
    assert '- **Linux/macOS**: `source .venv/bin/activate && pytest tests/test_<module_name>.py::test_name -v`' in text, "expected to find: " + '- **Linux/macOS**: `source .venv/bin/activate && pytest tests/test_<module_name>.py::test_name -v`'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/implementation-order.mdc')
    assert '- **Windows**: `.venv\\Scripts\\activate && pytest tests/test_<module_name>.py::test_name -v`' in text, "expected to find: " + '- **Windows**: `.venv\\Scripts\\activate && pytest tests/test_<module_name>.py::test_name -v`'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/python-fastapi.mdc')
    assert '- Minimize `@app.on_event("startup")` and `@app.on_event("shutdown")` - prefer lifespan context managers for managing startup and shutdown events' in text, "expected to find: " + '- Minimize `@app.on_event("startup")` and `@app.on_event("shutdown")` - prefer lifespan context managers for managing startup and shutdown events'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/python-fastapi.mdc')
    assert '- Avoid global scope variables - implement/use global application state, set its initialization logic in one place' in text, "expected to find: " + '- Avoid global scope variables - implement/use global application state, set its initialization logic in one place'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/python-fastapi.mdc')
    assert '- Minimize blocking I/O operations - use asynchronous operations for all database calls and external API requests' in text, "expected to find: " + '- Minimize blocking I/O operations - use asynchronous operations for all database calls and external API requests'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing.mdc')
    assert 'agent = await AgentFactory.create(agent_def, task_messages=[{"role": "user", "content": "Test"}])' in text, "expected to find: " + 'agent = await AgentFactory.create(agent_def, task_messages=[{"role": "user", "content": "Test"}])'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing.mdc')
    assert 'patch("sgr_agent_core.agent_factory.MCP2ToolConverter.build_tools_from_mcp", return_value=[]),' in text, "expected to find: " + 'patch("sgr_agent_core.agent_factory.MCP2ToolConverter.build_tools_from_mcp", return_value=[]),'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing.mdc')
    assert 'pytest tests/test_agent_factory.py::TestAgentFactory::test_create_agent_from_definition -v' in text, "expected to find: " + 'pytest tests/test_agent_factory.py::TestAgentFactory::test_create_agent_from_definition -v'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/workflow.mdc')
    assert '**CRITICALLY IMPORTANT**: When user asks to implement a new feature (using words "фича", "feature", "новая функция", "добавить", "implement", "add"), **always** apply TDD approach and follow this stri' in text, "expected to find: " + '**CRITICALLY IMPORTANT**: When user asks to implement a new feature (using words "фича", "feature", "новая функция", "добавить", "implement", "add"), **always** apply TDD approach and follow this stri'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/workflow.mdc')
    assert '**CRITICALLY IMPORTANT**: When user asks to fix a bug (using words "баг", "bug", "ошибка", "error", "исправить", "fix"), **always** apply TDD approach and follow this strict workflow:' in text, "expected to find: " + '**CRITICALLY IMPORTANT**: When user asks to fix a bug (using words "баг", "bug", "ошибка", "error", "исправить", "fix"), **always** apply TDD approach and follow this strict workflow:'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/workflow.mdc')
    assert '**Do not skip any step!** Always follow order: write test (red) → verify test fails → implement feature → test (green) → run all tests → run linter → report.' in text, "expected to find: " + '**Do not skip any step!** Always follow order: write test (red) → verify test fails → implement feature → test (green) → run all tests → run linter → report.'[:80]

