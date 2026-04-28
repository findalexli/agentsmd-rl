#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sgr-agent-core

# Idempotency guard
if grep -qF "The project uses **modular architecture with clear separation of concerns**. The" ".cursor/rules/architecture.mdc" && grep -qF "def create_agent(self, agent_def: AgentDefinition, task_messages: list[dict]) ->" ".cursor/rules/code-style.mdc" && grep -qF "- Contains: reasoning_steps, current_situation, plan_status, enough_data, remain" ".cursor/rules/core-modules.mdc" && grep -qF "When adding new functionality, follow **\"one class at a time\"** principle, start" ".cursor/rules/implementation-order.mdc" && grep -qF "- Minimize `@app.on_event(\"startup\")` and `@app.on_event(\"shutdown\")` - prefer l" ".cursor/rules/python-fastapi.mdc" && grep -qF "agent = await AgentFactory.create(agent_def, task_messages=[{\"role\": \"user\", \"co" ".cursor/rules/testing.mdc" && grep -qF "**CRITICALLY IMPORTANT**: When user asks to implement a new feature (using words" ".cursor/rules/workflow.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/architecture.mdc b/.cursor/rules/architecture.mdc
@@ -0,0 +1,118 @@
+---
+description: Architectural rules and boundaries for SGR Agent Core
+globs: sgr_agent_core/**/*.py
+alwaysApply: true
+---
+
+# Architectural Rules for SGR Agent Core
+
+## General Architecture
+
+The project uses **modular architecture with clear separation of concerns**. The framework implements Schema-Guided Reasoning (SGR) for building intelligent research agents.
+
+## Core Architecture Layers
+
+### Layer 1: Base Classes (No Dependencies)
+- `BaseAgent` - Base class for all agents
+- `BaseTool` - Base class for all tools (Pydantic models)
+- `MCPBaseTool` - Base class for MCP-integrated tools
+- `models.py` - Core data models (AgentContext, AgentStatesEnum, etc.)
+
+### Layer 2: Configuration and Registry
+- `agent_config.py` - GlobalConfig singleton
+- `agent_definition.py` - AgentDefinition, AgentConfig, LLMConfig, etc.
+- `services/registry.py` - AgentRegistry, ToolRegistry
+- `services/prompt_loader.py` - PromptLoader service
+
+### Layer 3: Factory and Services
+- `agent_factory.py` - AgentFactory for creating agents
+- `services/mcp_service.py` - MCP2ToolConverter
+- `services/tavily_search.py` - Tavily search service
+- `next_step_tool.py` - NextStepToolsBuilder, NextStepToolStub
+
+### Layer 4: Agent Implementations
+- `agents/sgr_agent.py` - SGRAgent (Structured Output)
+- `agents/tool_calling_agent.py` - ToolCallingAgent (Function Calling)
+- `agents/sgr_tool_calling_agent.py` - SGRToolCallingAgent (Hybrid)
+
+### Layer 5: Tools
+- `tools/reasoning_tool.py` - ReasoningTool
+- `tools/clarification_tool.py` - ClarificationTool
+- `tools/web_search_tool.py` - WebSearchTool
+- `tools/extract_page_content_tool.py` - ExtractPageContentTool
+- `tools/generate_plan_tool.py` - GeneratePlanTool
+- `tools/adapt_plan_tool.py` - AdaptPlanTool
+- `tools/create_report_tool.py` - CreateReportTool
+- `tools/final_answer_tool.py` - FinalAnswerTool
+
+### Layer 6: Server and API
+- `server/app.py` - FastAPI application
+- `server/endpoints.py` - API endpoints
+- `server/models.py` - API request/response models
+- `server/settings.py` - Server settings
+- `stream.py` - OpenAIStreamingGenerator
+
+## Agent Execution Cycle
+
+All agents follow a two-phase cycle:
+
+```python
+while agent.state not in FINISH_STATES:
+    reasoning = await agent._reasoning_phase()
+    action_tool = await agent._select_action_phase(reasoning)
+    await agent._action_phase(action_tool)
+```
+
+### Phase 1: Reasoning Phase
+- Agent analyzes current context
+- Decides on next action
+- Implementation varies by agent type (SO, FC, or Hybrid)
+
+### Phase 2: Select Action Phase
+- Selects appropriate tool based on reasoning
+- Returns tool instance ready for execution
+
+### Phase 3: Action Phase
+- Executes selected tool
+- Updates conversation history
+- Updates agent context
+
+## Module Rules
+
+### Agents (`sgr_agent_core/agents/`)
+- Must inherit from `BaseAgent`
+- Must implement `_reasoning_phase()`, `_select_action_phase()`, `_action_phase()`
+- Automatically registered in `AgentRegistry` via `AgentRegistryMixin`
+- Can override `_prepare_context()` and `_prepare_tools()` for customization
+
+### Tools (`sgr_agent_core/tools/`)
+- Must inherit from `BaseTool` or `MCPBaseTool`
+- Must be Pydantic models
+- Must implement `__call__()` method
+- Automatically registered in `ToolRegistry` via `ToolRegistryMixin`
+- Return string or JSON string from `__call__()`
+
+### Services (`sgr_agent_core/services/`)
+- Stateless utility classes
+- Provide shared functionality (prompts, MCP, search)
+- No direct dependencies on agents or tools
+
+### Configuration (`agent_config.py`, `agent_definition.py`)
+- Hierarchical configuration: GlobalConfig → AgentDefinition → AgentConfig
+- Supports YAML loading
+- Automatic inheritance and override of settings
+
+## Design Principles
+
+1. **One class at a time**: When implementing new functionality, create one class at a time, starting from lower layers
+2. **Minimal dependencies**: Each module should depend only on lower layer modules
+3. **Type hints**: Use type hints for all functions and methods
+4. **Async-first**: All I/O operations must be async
+5. **Registry pattern**: Use registries for automatic discovery of agents and tools
+6. **Configuration over code**: Prefer YAML configuration over hardcoded values
+
+## References
+
+@docs/en/framework/main-concepts.md
+@docs/en/framework/agents.md
+@README.md
diff --git a/.cursor/rules/code-style.mdc b/.cursor/rules/code-style.mdc
@@ -0,0 +1,99 @@
+---
+description: Code style and formatting rules for SGR Agent Core
+globs: **/*.py
+alwaysApply: true
+---
+
+# Code Style Rules
+
+## General Rules
+
+1. **Comments**: Write all code comments **ONLY in English**
+2. **User responses**: Respond in Russian unless user requests otherwise
+3. **Empty line at end of file**: Always add an empty line at the end of new files
+4. **Virtual environment**: Virtual environment is located in `.venv` directory
+
+## Code Formatting
+
+### Ruff and Black
+- Use `ruff` for linting and formatting
+- Line length: **120 characters** (configured in `pyproject.toml`)
+- Follow rules from `pyproject.toml` and `.ruff.toml` if present
+
+### Imports
+- Use `isort` for import sorting
+- Group imports: standard library → third-party → local
+- One import per line for long lists
+
+### Type Hints
+- **Mandatory**: Use type hints for all functions and methods
+- Prefer `T | None` over `Optional[T]` (Python 3.10+)
+- Use `Union[A, B]` for complex types when needed
+- Use `dict[str, Any]` instead of `Dict[str, Any]` (Python 3.9+)
+
+### Docstrings
+- Use docstrings in Google style format
+- All docstrings in **English**
+- Must document:
+  - Public classes and methods
+  - Complex business logic
+  - Parameters and return values
+
+Example:
+```python
+def create_agent(self, agent_def: AgentDefinition, task_messages: list[dict]) -> BaseAgent:
+    """
+    Create an agent instance from a definition.
+
+    Args:
+        agent_def: Agent definition with configuration
+        task_messages: Task messages in OpenAI format
+
+    Returns:
+        Created agent instance
+    """
+```
+
+## File Structure
+
+### Element Order in File
+1. Module docstring
+2. Imports (standard library → third-party → local)
+3. Constants
+4. Types and exceptions
+5. Classes and functions
+
+### Naming
+- **Classes**: PascalCase (`SGRAgent`, `BaseTool`)
+- **Functions and methods**: snake_case (`create_agent`, `_prepare_context`)
+- **Constants**: UPPER_SNAKE_CASE (`MAX_ITERATIONS`)
+- **Private methods**: start with `_` (`_reasoning_phase`, `_log_reasoning`)
+- **Types**: PascalCase (`AgentContext`, `AgentDefinition`)
+
+## Error Handling
+
+- Use specific exceptions, not generic `Exception`
+- Create custom exceptions for business logic when needed
+- Always include informative error messages
+- Use `Optional` or `| None` for values that may be missing
+
+## Async/Await
+
+- Use `async def` for all asynchronous operations
+- Use `await` for all async calls
+- Don't use blocking I/O in async code
+- Use `httpx` instead of `requests` for async HTTP calls
+
+## FastAPI-Specific Guidelines
+
+- Avoid global scope variables, use application state
+- Use functional components and Pydantic models for validation
+- Use declarative route definitions with clear return type annotations
+- Use `async def` for asynchronous endpoints
+- Use Pydantic's `BaseModel` for input/output validation
+- Use `HTTPException` for expected errors
+
+## References
+
+@pyproject.toml
+@pytest.ini
diff --git a/.cursor/rules/core-modules.mdc b/.cursor/rules/core-modules.mdc
@@ -0,0 +1,169 @@
+---
+description: Rules for core modules of SGR Agent Core
+globs: sgr_agent_core/**/*.py
+alwaysApply: true
+---
+
+# Rules for Core Modules
+
+## Base Classes
+
+### BaseAgent (`sgr_agent_core/base_agent.py`)
+- Parent class for all agents
+- Implements two-phase execution cycle: Reasoning → Action
+- Manages agent context, conversation history, and streaming
+- Must be subclassed to implement `_reasoning_phase()`, `_select_action_phase()`, `_action_phase()`
+- Automatically registered in `AgentRegistry` via `AgentRegistryMixin`
+
+### BaseTool (`sgr_agent_core/base_tool.py`)
+- Parent class for all tools
+- Must be a Pydantic model
+- Must implement `__call__(context, config)` method
+- Returns string or JSON string
+- Automatically registered in `ToolRegistry` via `ToolRegistryMixin`
+
+### MCPBaseTool (`sgr_agent_core/base_tool.py`)
+- Base class for MCP-integrated tools
+- Handles MCP client calls
+- Converts MCP responses to tool format
+
+## Configuration Modules
+
+### GlobalConfig (`sgr_agent_core/agent_config.py`)
+- Singleton pattern for global configuration
+- Loads from YAML files (`config.yaml`, `agents.yaml`)
+- Provides default values for all agent settings
+
+### AgentDefinition (`sgr_agent_core/agent_definition.py`)
+- Definition template for creating agents
+- Contains: name, base_class, tools, llm, prompts, execution, search, mcp configs
+- Supports YAML loading
+- Validates required fields
+
+### AgentConfig (`sgr_agent_core/agent_definition.py`)
+- Runtime configuration for agent instance
+- Combines: LLMConfig, SearchConfig, ExecutionConfig, PromptsConfig, MCPConfig
+- Supports hierarchical inheritance from GlobalConfig
+
+## Factory and Services
+
+### AgentFactory (`sgr_agent_core/agent_factory.py`)
+- Creates agent instances from AgentDefinition
+- Resolves agent classes from AgentRegistry
+- Resolves tools from ToolRegistry
+- Builds MCP tools via MCP2ToolConverter
+- Creates OpenAI client with proxy support
+
+### AgentRegistry (`sgr_agent_core/services/registry.py`)
+- Centralized registry for agent classes
+- Automatic registration via `AgentRegistryMixin`
+- Supports lookup by name (case-insensitive)
+
+### ToolRegistry (`sgr_agent_core/services/registry.py`)
+- Centralized registry for tool classes
+- Automatic registration via `ToolRegistryMixin`
+- Supports lookup by name (case-insensitive)
+
+### PromptLoader (`sgr_agent_core/services/prompt_loader.py`)
+- Loads and formats prompts from files or strings
+- Generates system prompts with tool descriptions
+- Formats initial user requests and clarification responses
+
+### MCP2ToolConverter (`sgr_agent_core/services/mcp_service.py`)
+- Converts MCP server tools to BaseTool instances
+- Handles MCP client initialization
+- Builds tools from MCP configuration
+
+## Agent Implementations
+
+### SGRAgent (`sgr_agent_core/agents/sgr_agent.py`)
+- Uses Structured Output approach
+- Creates dynamic JSON schema for tools
+- LLM returns reasoning + tool schema in one call
+- Extracts tool directly from reasoning result
+
+### ToolCallingAgent (`sgr_agent_core/agents/tool_calling_agent.py`)
+- Uses native Function Calling
+- No explicit reasoning phase
+- Uses `tool_choice="required"` for tool selection
+- Best for advanced LLM models
+
+### SGRToolCallingAgent (`sgr_agent_core/agents/sgr_tool_calling_agent.py`)
+- Hybrid approach: SGR + Function Calling
+- Uses ReasoningTool for explicit reasoning
+- Uses Function Calling for tool selection
+- Best balance for most tasks
+
+## Tools
+
+### ReasoningTool (`sgr_agent_core/tools/reasoning_tool.py`)
+- Provides structured reasoning output
+- Contains: reasoning_steps, current_situation, plan_status, enough_data, remaining_steps, task_completed
+
+### ClarificationTool (`sgr_agent_core/tools/clarification_tool.py`)
+- Requests clarification from user
+- Pauses agent execution
+- Waits for user input via `provide_clarification()`
+
+### WebSearchTool (`sgr_agent_core/tools/web_search_tool.py`)
+- Performs web search via Tavily API
+- Returns search results with sources
+- Respects max_searches limit
+
+### ExtractPageContentTool (`sgr_agent_core/tools/extract_page_content_tool.py`)
+- Extracts content from web pages
+- Uses Tavily API for content extraction
+- Respects content_limit
+
+### GeneratePlanTool (`sgr_agent_core/tools/generate_plan_tool.py`)
+- Generates research plan
+- Defines research goal and steps
+- Provides search strategies
+
+### AdaptPlanTool (`sgr_agent_core/tools/adapt_plan_tool.py`)
+- Adapts existing plan based on new information
+- Updates research goal and steps
+- Modifies search strategies
+
+### CreateReportTool (`sgr_agent_core/tools/create_report_tool.py`)
+- Creates final research report
+- Saves report to file
+- Formats report with sources
+
+### FinalAnswerTool (`sgr_agent_core/tools/final_answer_tool.py`)
+- Provides final answer to user
+- Completes agent execution
+- Sets agent state to COMPLETED
+
+## Server and API
+
+### FastAPI Application (`sgr_agent_core/server/app.py`)
+- Main FastAPI application
+- Configures CORS, middleware
+- Registers endpoints
+
+### API Endpoints (`sgr_agent_core/server/endpoints.py`)
+- `/v1/chat/completions` - OpenAI-compatible chat endpoint
+- `/v1/agents/{agent_id}/state` - Get agent state
+- `/v1/agents/{agent_id}/clarification` - Provide clarification
+- `/v1/agents` - List available agents
+
+### Streaming (`sgr_agent_core/stream.py`)
+- OpenAIStreamingGenerator for streaming responses
+- Formats events in OpenAI-compatible format
+- Handles tool calls and content chunks
+
+## General Rules for All Modules
+
+1. **Type hints**: Use type hints everywhere
+2. **Async**: All I/O operations must be async
+3. **Documentation**: Document public methods in English
+4. **Error handling**: Use specific exceptions
+5. **Registry**: Use registry pattern for discovery
+6. **Configuration**: Prefer YAML over hardcoded values
+
+## References
+
+@architecture.mdc
+@code-style.mdc
+@docs/en/framework/main-concepts.md
diff --git a/.cursor/rules/implementation-order.mdc b/.cursor/rules/implementation-order.mdc
@@ -0,0 +1,222 @@
+---
+description: Implementation order for new features - one class at a time
+globs: sgr_agent_core/**/*.py
+alwaysApply: false
+---
+
+# Implementation Order: One Class at a Time
+
+## "One Class at a Time" Principle
+
+When adding new functionality, follow **"one class at a time"** principle, starting from lower architecture layers.
+
+## Architecture Layers (Bottom to Top)
+
+1. **Layer 1**: Base classes (BaseAgent, BaseTool, Models)
+2. **Layer 2**: Configuration and Registry
+3. **Layer 3**: Factory and Services
+4. **Layer 4**: Agent Implementations
+5. **Layer 5**: Tools
+6. **Layer 6**: Server and API
+
+## Implementation Steps
+
+### 1. Determine Layer
+Determine which layer the new functionality belongs to (see @architecture.mdc)
+
+### 2. Write Test First
+- Create test file `tests/test_<module_name>.py`
+- Write minimal unit tests for class
+- Test must **fail** (red) because class doesn't exist
+- Run test:
+  - **Linux/macOS**: `source .venv/bin/activate && pytest tests/test_<module_name>.py::test_name -v`
+  - **Windows**: `.venv\Scripts\activate && pytest tests/test_<module_name>.py::test_name -v`
+- Verify test fails for correct reason
+
+### 3. Implement Class
+- Create class with minimal implementation
+- Use type hints
+- Add docstrings in English
+- Follow rules from @code-style.mdc
+- Place in appropriate layer directory
+
+### 4. Verify Test Passes
+- Run test:
+  - **Linux/macOS**: `source .venv/bin/activate && pytest tests/test_<module_name>.py::test_name -v`
+  - **Windows**: `.venv\Scripts\activate && pytest tests/test_<module_name>.py::test_name -v`
+- Test must **pass** (green)
+- Make sure implementation is correct
+
+### 5. Run All Tests
+- Execute:
+  - **Linux/macOS**: `source .venv/bin/activate && pytest tests/ -v`
+  - **Windows**: `.venv\Scripts\activate && pytest tests/ -v`
+- All tests must pass
+- Fix any regressions
+
+### 6. Run Linter
+- Execute:
+  - **Linux/macOS**: `source .venv/bin/activate && pre-commit run -a`
+  - **Windows**: `.venv\Scripts\activate && pre-commit run -a`
+- Fix all linting errors
+- Repeat until all checks pass
+
+### 7. Move to Next Layer
+Only after lower layer class is ready and tested, move to upper layer classes.
+
+## Example: Adding New Tool
+
+### Step 1: Write Test
+```python
+# tests/test_custom_tool.py
+@pytest.mark.asyncio
+async def test_custom_tool_execution():
+    """Test CustomTool execution."""
+    tool = CustomTool(param="value")
+    result = await tool(context, config)
+    assert result == "expected_result"
+```
+
+### Step 2: Run Test (Should Fail)
+
+**Linux/macOS:**
+```bash
+source .venv/bin/activate
+pytest tests/test_custom_tool.py::test_custom_tool_execution -v
+# Expected: FAILED - CustomTool doesn't exist
+```
+
+**Windows:**
+```powershell
+.venv\Scripts\Activate.ps1
+pytest tests/test_custom_tool.py::test_custom_tool_execution -v
+# Expected: FAILED - CustomTool doesn't exist
+```
+
+### Step 3: Implement Tool (Layer 5)
+```python
+# sgr_agent_core/tools/custom_tool.py
+class CustomTool(BaseTool):
+    """Custom tool for specific functionality."""
+    tool_name: str = "custom_tool"
+    description: str = "Does custom thing"
+
+    param: str
+
+    async def __call__(self, context: AgentContext, config: AgentConfig) -> str:
+        """Execute custom tool."""
+        return "expected_result"
+```
+
+### Step 4: Verify Test Passes
+
+**Linux/macOS:**
+```bash
+source .venv/bin/activate
+pytest tests/test_custom_tool.py::test_custom_tool_execution -v
+# Expected: PASSED
+```
+
+**Windows:**
+```powershell
+.venv\Scripts\Activate.ps1
+pytest tests/test_custom_tool.py::test_custom_tool_execution -v
+# Expected: PASSED
+```
+
+### Step 5: Run All Tests
+
+**Linux/macOS:**
+```bash
+source .venv/bin/activate
+pytest tests/ -v
+# Expected: All tests pass
+```
+
+**Windows:**
+```powershell
+.venv\Scripts\Activate.ps1
+pytest tests/ -v
+# Expected: All tests pass
+```
+
+### Step 6: Run Linter
+
+**Linux/macOS:**
+```bash
+source .venv/bin/activate
+pre-commit run -a
+# Expected: All checks pass
+```
+
+**Windows:**
+```powershell
+.venv\Scripts\Activate.ps1
+pre-commit run -a
+# Expected: All checks pass
+```
+
+## Example: Adding New Agent
+
+### Step 1: Write Test
+```python
+# tests/test_custom_agent.py
+@pytest.mark.asyncio
+async def test_custom_agent_creation():
+    """Test CustomAgent creation."""
+    agent_def = AgentDefinition(
+        name="custom_agent",
+        base_class=CustomAgent,
+        tools=[ReasoningTool],
+        ...
+    )
+    agent = await AgentFactory.create(agent_def, task_messages=[...])
+    assert isinstance(agent, CustomAgent)
+```
+
+### Step 2: Implement Agent (Layer 4)
+```python
+# sgr_agent_core/agents/custom_agent.py
+class CustomAgent(BaseAgent):
+    """Custom agent implementation."""
+    name: str = "custom_agent"
+
+    async def _reasoning_phase(self) -> ReasoningTool:
+        """Reasoning phase implementation."""
+        ...
+
+    async def _select_action_phase(self, reasoning: ReasoningTool) -> BaseTool:
+        """Select action phase implementation."""
+        ...
+
+    async def _action_phase(self, tool: BaseTool) -> str:
+        """Action phase implementation."""
+        ...
+```
+
+## Forbidden
+
+❌ Implement multiple classes simultaneously
+❌ Move to upper layers before lower ones are ready
+❌ Skip writing tests
+❌ Skip running tests
+❌ Skip running linter
+❌ Implement functionality without understanding architecture
+
+## Allowed
+
+✅ Implement one class at a time
+✅ Write tests first (TDD)
+✅ Verify test fails before implementation
+✅ Verify test passes after implementation
+✅ Run all tests after each change
+✅ Run linter after each change
+✅ Use stubs for dependencies
+✅ Refactor after basic functionality works
+
+## References
+
+@architecture.mdc
+@code-style.mdc
+@testing.mdc
+@workflow.mdc
diff --git a/.cursor/rules/python-fastapi.mdc b/.cursor/rules/python-fastapi.mdc
@@ -1,48 +1,55 @@
 ---
-alwaysApply: false
+description: Python and FastAPI specific guidelines
+globs: sgr_agent_core/server/**/*.py, **/*.py
+alwaysApply: true
 ---
-Python/FastAPI
-
-- use MinGW terminal for work
-- Don't use the requests library in asynchronous code.
-- Don't use print in the main logic of system services. Initialize logging.Logger
-- Use def for pure functions and async def for asynchronous operations.
-- Use type hints for all function signatures. Prefer Pydantic models over raw dictionaries for input validation.
-- Avoid unnecessary curly braces in conditional statements.
-- For single-line statements in conditionals, omit curly braces.
-- Use concise, one-line syntax for simple conditional statements (e.g., if condition: do_something()).
-- Write comments only in entities docs and complex logic. No need to comment every line of code
+
+# Python/FastAPI Guidelines
+
+## General Python Rules
+
+- Don't use the `requests` library in asynchronous code - use `httpx` instead
+- Don't use `print` in the main logic of system services - initialize `logging.Logger`
+- Use `def` for pure functions and `async def` for asynchronous operations
+- Use type hints for all function signatures
+- Prefer Pydantic models over raw dictionaries for input validation
+- Write comments only in entity docs and complex logic - no need to comment every line of code
 - Write comments only in English
-- Do not use Optional import from typing in cases you can use |
+- Do not use `Optional` import from `typing` in cases you can use `|` (Python 3.10+)
 
-Error Handling and Validation
+## Error Handling and Validation
 
 - Prioritize error handling and edge cases:
-  - Handle errors and edge cases at the beginning of functions.
-  - Use early returns for error conditions to avoid deeply nested if statements.
-  - Place the happy path last in the function for improved readability.
-  - Avoid unnecessary else statements; use the if-return pattern instead.
-  - Use guard clauses to handle preconditions and invalid states early.
-  - Implement proper error logging and user-friendly error messages.
-  - Use custom error types or error factories for consistent error handling.
-
-FastAPI-Specific Guidelines
-
-- Avoid global scope variables, implement/use global application state, set its initialization logic in one place
-- Use functional components (plain functions) and Pydantic models for input validation and response schemas.
-- Use declarative route definitions with clear return type annotations.
-- Use  async def for asynchronous ones.
-- Minimize @app.on_event("startup") and @app.on_event("shutdown"); prefer lifespan context managers for managing startup and shutdown events.
-- Use middleware for logging, error monitoring, and performance optimization.
-- Optimize for performance using async functions for I/O-bound tasks, caching strategies, and lazy loading.
-- Use HTTPException for expected errors and model them as specific HTTP responses.
-- Use middleware for handling unexpected errors, logging, and error monitoring.
-- Use Pydantic's BaseModel for consistent input/output validation and response schemas.
-
-
-Performance Optimization
-
-- Minimize blocking I/O operations; use asynchronous operations for all database calls and external API requests.
-- Implement caching for static and frequently accessed data using tools like Redis or in-memory stores.
-- Optimize data serialization and deserialization with Pydantic.
-- Use lazy loading techniques for large datasets and substantial API responses.
+  - Handle errors and edge cases at the beginning of functions
+  - Use early returns for error conditions to avoid deeply nested if statements
+  - Place the happy path last in the function for improved readability
+  - Avoid unnecessary else statements; use the if-return pattern instead
+  - Use guard clauses to handle preconditions and invalid states early
+  - Implement proper error logging and user-friendly error messages
+  - Use custom error types or error factories for consistent error handling
+
+## FastAPI-Specific Guidelines
+
+- Avoid global scope variables - implement/use global application state, set its initialization logic in one place
+- Use functional components (plain functions) and Pydantic models for input validation and response schemas
+- Use declarative route definitions with clear return type annotations
+- Use `async def` for asynchronous endpoints
+- Minimize `@app.on_event("startup")` and `@app.on_event("shutdown")` - prefer lifespan context managers for managing startup and shutdown events
+- Use middleware for logging, error monitoring, and performance optimization
+- Optimize for performance using async functions for I/O-bound tasks, caching strategies, and lazy loading
+- Use `HTTPException` for expected errors and model them as specific HTTP responses
+- Use middleware for handling unexpected errors, logging, and error monitoring
+- Use Pydantic's `BaseModel` for consistent input/output validation and response schemas
+
+## Performance Optimization
+
+- Minimize blocking I/O operations - use asynchronous operations for all database calls and external API requests
+- Implement caching for static and frequently accessed data using tools like Redis or in-memory stores
+- Optimize data serialization and deserialization with Pydantic
+- Use lazy loading techniques for large datasets and substantial API responses
+
+## References
+
+@code-style.mdc
+@architecture.mdc
+@core-modules.mdc
diff --git a/.cursor/rules/testing.mdc b/.cursor/rules/testing.mdc
@@ -0,0 +1,198 @@
+---
+description: Test writing rules for SGR Agent Core
+globs: tests/**/*.py
+alwaysApply: true
+---
+
+# Test Writing Rules
+
+## General Principles
+
+1. **Coverage**: Aim for code coverage >90%
+2. **One class at a time**: When creating new class, write tests for it immediately
+3. **Isolation**: Each test must be independent
+4. **Readability**: Test names should describe what is being tested
+5. **Virtual environment**: Use `.venv` for running tests
+
+## Test Structure
+
+### Naming
+- Test file: `test_<module_name>.py`
+- Test class: `Test<ClassName>`
+- Test method: `test_<what_is_tested>`
+
+### Test Class Structure
+```python
+class TestAgentFactory:
+    """Test suite for AgentFactory."""
+
+    @pytest.mark.asyncio
+    async def test_create_agent_from_definition(self):
+        """Test creating agent from AgentDefinition."""
+        # Arrange
+        # Act
+        # Assert
+```
+
+## Test Types
+
+### Unit Tests
+- Test individual modules in isolation
+- Use mocks for dependencies (OpenAI client, external APIs)
+- Fast and deterministic
+- Use `@pytest.mark.asyncio` for async tests
+
+### Integration Tests
+- Test interaction between modules
+- Test agent creation and execution flow
+- Use real configuration but mocked LLM clients
+
+### E2E Tests
+- Test full agent execution cycle
+- Use mocked LLM responses
+- Verify agent state transitions
+
+### Edge-case Tests
+- Test edge cases (empty inputs, max iterations, etc.)
+- Test error handling
+- Test input validation
+
+## Fixtures
+
+### Using Fixtures
+- Create fixtures in `tests/conftest.py` for reusable data
+- Use `@pytest.fixture` for reusable data
+- Use `scope="function"` for test isolation
+
+### Common Fixtures
+- `mock_openai_client` - Mocked AsyncOpenAI client
+- `test_llm_config` - Test LLM configuration
+- `test_prompts_config` - Test prompts configuration
+- `test_execution_config` - Test execution configuration
+- `create_test_agent()` - Helper function to create test agents
+
+## Test Examples
+
+### Unit Test for Agent Factory
+```python
+@pytest.mark.asyncio
+async def test_create_agent_from_definition(self):
+    """Test creating agent from AgentDefinition."""
+    with (
+        patch("sgr_agent_core.agent_factory.MCP2ToolConverter.build_tools_from_mcp", return_value=[]),
+        mock_global_config(),
+    ):
+        agent_def = AgentDefinition(
+            name="sgr_agent",
+            base_class=SGRAgent,
+            tools=[ReasoningTool],
+            llm={"api_key": "test-key", "base_url": "https://api.openai.com/v1"},
+            prompts={...},
+            execution={},
+        )
+        agent = await AgentFactory.create(agent_def, task_messages=[{"role": "user", "content": "Test"}])
+
+        assert isinstance(agent, SGRAgent)
+        assert len(agent.task_messages) == 1
+```
+
+### Integration Test for Agent Execution
+```python
+@pytest.mark.asyncio
+async def test_sgr_agent_full_execution_cycle(self):
+    """Test full execution cycle of SGRAgent."""
+    # Test agent creation and basic execution flow
+```
+
+## Assertions
+
+### What to Check
+- Return value types
+- Agent state transitions
+- Tool execution results
+- Error messages
+- HTTP status codes (for API tests)
+
+### Using assert
+- Use clear assert messages
+- Check multiple aspects of result
+- Use `isinstance()` for type checking
+
+## Running Tests
+
+### All Tests
+
+**Linux/macOS:**
+```bash
+source .venv/bin/activate
+pytest tests/ -v
+```
+
+**Windows (PowerShell):**
+```powershell
+.venv\Scripts\Activate.ps1
+pytest tests/ -v
+```
+
+**Windows (CMD):**
+```cmd
+.venv\Scripts\activate.bat
+pytest tests/ -v
+```
+
+**Windows (Git Bash/WSL):**
+```bash
+source .venv/Scripts/activate
+pytest tests/ -v
+```
+
+### With Coverage
+
+**Linux/macOS:**
+```bash
+source .venv/bin/activate
+pytest tests/ --cov=sgr_agent_core --cov-report=term-missing
+```
+
+**Windows:**
+```powershell
+.venv\Scripts\Activate.ps1
+pytest tests/ --cov=sgr_agent_core --cov-report=term-missing
+```
+
+### Specific Test
+
+**Linux/macOS:**
+```bash
+source .venv/bin/activate
+pytest tests/test_agent_factory.py::TestAgentFactory::test_create_agent_from_definition -v
+```
+
+**Windows:**
+```powershell
+.venv\Scripts\Activate.ps1
+pytest tests/test_agent_factory.py::TestAgentFactory::test_create_agent_from_definition -v
+```
+
+### Async Tests
+- Use `pytest-asyncio` plugin (configured in `pytest.ini`)
+- Mark async tests with `@pytest.mark.asyncio`
+- Use `asyncio_mode = "auto"` in pytest.ini
+
+## Mocking
+
+### OpenAI Client Mocking
+- Mock `AsyncOpenAI` client for all LLM calls
+- Use `AsyncMock` for async methods
+- Mock stream responses for streaming tests
+
+### External Services
+- Mock Tavily API calls
+- Mock MCP server calls
+- Mock file system operations when needed
+
+## References
+
+@pytest.ini
+@tests/conftest.py
+@code-style.mdc
diff --git a/.cursor/rules/workflow.mdc b/.cursor/rules/workflow.mdc
@@ -0,0 +1,280 @@
+---
+description: Workflow rules for bug fixes, new features, and testing
+globs: **/*.py, tests/**/*.py
+alwaysApply: true
+---
+
+# Workflow Rules for Bug Fixes and New Features
+
+## Virtual Environment
+
+**IMPORTANT**: Virtual environment is located in `.venv` directory. Always activate it before running tests or commands:
+
+**Linux/macOS:**
+```bash
+source .venv/bin/activate
+```
+
+**Windows (PowerShell):**
+```powershell
+.venv\Scripts\Activate.ps1
+```
+
+**Windows (CMD):**
+```cmd
+.venv\Scripts\activate.bat
+```
+
+**Windows (Git Bash/WSL):**
+```bash
+source .venv/Scripts/activate
+```
+
+## New Features (TDD Approach)
+
+### Mandatory Workflow for New Features
+
+**CRITICALLY IMPORTANT**: When user asks to implement a new feature (using words "фича", "feature", "новая функция", "добавить", "implement", "add"), **always** apply TDD approach and follow this strict workflow:
+
+**Do not skip any step!** Always follow order: write test (red) → verify test fails → implement feature → test (green) → run all tests → run linter → report.
+
+### Step-by-step Process for New Features
+
+1. **Write test first**
+   - Create test in corresponding file `tests/test_*.py`
+   - Test must **fail** (red) because feature doesn't exist yet
+   - Test must clearly describe expected behavior
+   - Make sure test actually fails for the right reason
+   - Run test:
+     - **Linux/macOS**: `source .venv/bin/activate && pytest tests/test_*.py::test_name -v`
+     - **Windows**: `.venv\Scripts\activate && pytest tests/test_*.py::test_name -v`
+
+2. **Verify test fails**
+   - Run new test:
+     - **Linux/macOS**: `source .venv/bin/activate && pytest tests/test_*.py::test_name -v`
+     - **Windows**: `.venv\Scripts\activate && pytest tests/test_*.py::test_name -v`
+   - Test must **fail** (red) - this confirms test is correct
+   - If test passes unexpectedly, review test logic
+
+3. **Implement feature**
+   - Write code that implements new feature
+   - Follow rules from @code-style.mdc and @architecture.mdc
+   - Use @implementation-order.mdc if adding new classes
+   - Implement one class/module at a time
+
+4. **Verify feature works**
+   - Run new test:
+     - **Linux/macOS**: `source .venv/bin/activate && pytest tests/test_*.py::test_name -v`
+     - **Windows**: `.venv\Scripts\activate && pytest tests/test_*.py::test_name -v`
+   - Test must **pass** (green)
+   - Make sure feature works as expected
+
+5. **Run all tests**
+   - Execute full test suite:
+     - **Linux/macOS**: `source .venv/bin/activate && pytest tests/ -v`
+     - **Windows**: `.venv\Scripts\activate && pytest tests/ -v`
+   - Make sure **all tests are green**
+   - If there are failing tests - fix them before proceeding
+
+6. **Run linter**
+   - Execute linter:
+     - **Linux/macOS**: `source .venv/bin/activate && pre-commit run -a`
+     - **Windows**: `.venv\Scripts\activate && pre-commit run -a`
+   - Fix all linting errors
+   - Make sure linter passes completely
+   - If there are errors, fix them and repeat step 6
+
+7. **Write report**
+   - Brief report of work done
+   - What feature was implemented
+   - Which tests were added/changed
+   - Test run results
+   - Linter results
+
+### Report Structure Example for New Features
+
+```markdown
+## Feature: [brief description]
+
+### Implementation
+1. Added test `test_new_feature` in `tests/test_module.py` (initially red)
+2. Implemented `new_method` in `sgr_agent_core/module.py`
+3. Ran new test - passed (green)
+4. Ran all tests - all green (239 passed)
+5. Ran linter - all checks passed
+
+### Changed Files
+- `sgr_agent_core/module.py` - added new_method implementation
+- `tests/test_module.py` - added test_new_feature test
+```
+
+## Bug Fixes (TDD Approach)
+
+### Mandatory Workflow for Bug Fixes
+
+**CRITICALLY IMPORTANT**: When user asks to fix a bug (using words "баг", "bug", "ошибка", "error", "исправить", "fix"), **always** apply TDD approach and follow this strict workflow:
+
+**Do not skip any step!** Always follow order: test (red) → fix → test (green) → all tests → run linter → report.
+
+### Step-by-step Process for Bug Fixes
+
+1. **Write test reproducing bug**
+   - Create test in corresponding file `tests/test_*.py`
+   - Test must **fail** (red) and reproduce bug
+   - Make sure error actually exists
+   - Run test:
+     - **Linux/macOS**: `source .venv/bin/activate && pytest tests/test_*.py::test_name -v`
+     - **Windows**: `.venv\Scripts\activate && pytest tests/test_*.py::test_name -v`
+
+2. **Fix code**
+   - Write code that fixes bug
+   - Follow rules from @code-style.mdc and @architecture.mdc
+   - Make minimal changes needed to fix the bug
+
+3. **Verify fix**
+   - Run new test:
+     - **Linux/macOS**: `source .venv/bin/activate && pytest tests/test_*.py::test_name -v`
+     - **Windows**: `.venv\Scripts\activate && pytest tests/test_*.py::test_name -v`
+   - Test must **pass** (green)
+   - Make sure bug is fixed
+
+4. **Run all tests**
+   - Execute full run:
+     - **Linux/macOS**: `source .venv/bin/activate && pytest tests/ -v`
+     - **Windows**: `.venv\Scripts\activate && pytest tests/ -v`
+   - Make sure **all tests are green**
+   - If there are failing tests - fix them
+
+5. **Run linter**
+   - Execute linter:
+     - **Linux/macOS**: `source .venv/bin/activate && pre-commit run -a`
+     - **Windows**: `.venv\Scripts\activate && pre-commit run -a`
+   - Fix all linting errors
+   - Make sure linter passes completely
+   - If there are errors, fix them and repeat step 5
+
+6. **Write report**
+   - Brief report of work done
+   - What was fixed
+   - Which tests were added/changed
+   - Test run results
+   - Linter results
+
+### Report Structure Example for Bug Fixes
+
+```markdown
+## Bug Fix: [brief description]
+
+### Problem
+[Bug description]
+
+### Solution
+1. Added test `test_bug_reproduction` in `tests/test_module.py` (initially red)
+2. Fixed method `method_name` in `sgr_agent_core/module.py`
+3. Ran new test - passed (green)
+4. Ran all tests - all green (239 passed)
+5. Ran linter - all checks passed
+
+### Changed Files
+- `sgr_agent_core/module.py` - fixed processing logic
+- `tests/test_module.py` - added test for bug
+```
+
+## Final Verification Before Reporting
+
+**MANDATORY**: Before writing final report for any work (bug fix or new feature), **always** complete these steps:
+
+1. **Run all tests**:
+   - **Linux/macOS**: `source .venv/bin/activate && pytest tests/ -v`
+   - **Windows**: `.venv\Scripts\activate && pytest tests/ -v`
+   - All tests must pass (green)
+   - No test failures allowed
+
+2. **Run linter**:
+   - **Linux/macOS**: `source .venv/bin/activate && pre-commit run -a`
+   - **Windows**: `.venv\Scripts\activate && pre-commit run -a`
+   - All linting checks must pass
+   - Fix all errors and warnings
+   - Repeat until all checks pass
+
+3. **Only then write report**
+   - Report must include test results
+   - Report must include linter results
+   - Report must confirm all checks passed
+
+## Testing Commands Reference
+
+### Linux/macOS
+```bash
+# Activate virtual environment
+source .venv/bin/activate
+
+# Run all tests
+pytest tests/ -v
+
+# Run specific test
+pytest tests/test_module.py::TestClass::test_method -v
+
+# Run with coverage
+pytest tests/ --cov=sgr_agent_core --cov-report=term-missing
+
+# Run linter
+pre-commit run -a
+
+# Run both tests and linter
+pytest tests/ -v && pre-commit run -a
+```
+
+### Windows (PowerShell/CMD)
+```powershell
+# Activate virtual environment (PowerShell)
+.venv\Scripts\Activate.ps1
+
+# Activate virtual environment (CMD)
+.venv\Scripts\activate.bat
+
+# Run all tests
+pytest tests/ -v
+
+# Run specific test
+pytest tests/test_module.py::TestClass::test_method -v
+
+# Run with coverage
+pytest tests/ --cov=sgr_agent_core --cov-report=term-missing
+
+# Run linter
+pre-commit run -a
+
+# Run both tests and linter (PowerShell)
+pytest tests/ -v; if ($?) { pre-commit run -a }
+
+# Run both tests and linter (CMD)
+pytest tests/ -v && pre-commit run -a
+```
+
+### Windows (Git Bash/WSL)
+```bash
+# Activate virtual environment
+source .venv/Scripts/activate
+
+# Run all tests
+pytest tests/ -v
+
+# Run specific test
+pytest tests/test_module.py::TestClass::test_method -v
+
+# Run with coverage
+pytest tests/ --cov=sgr_agent_core --cov-report=term-missing
+
+# Run linter
+pre-commit run -a
+
+# Run both tests and linter
+pytest tests/ -v && pre-commit run -a
+```
+
+## References
+
+@testing.mdc
+@code-style.mdc
+@architecture.mdc
PATCH

echo "Gold patch applied."
