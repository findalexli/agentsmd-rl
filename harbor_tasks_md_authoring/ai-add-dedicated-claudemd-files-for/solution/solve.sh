#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai

# Idempotency guard
if grep -qF "- Use project specific exceptions instead of global exception classes like \\Runt" "CLAUDE.md" && grep -qF "This is a Symfony 7.3 demo application showcasing AI integration capabilities us" "demo/CLAUDE.md" && grep -qF "This is the examples directory of the Symfony AI monorepo, containing standalone" "examples/CLAUDE.md" && grep -qF "The Agent component provides a framework for building AI agents that interact wi" "src/agent/CLAUDE.md" && grep -qF "The Symfony AI Bundle is an integration bundle that provides Symfony dependency " "src/ai-bundle/CLAUDE.md" && grep -qF "This is the Platform component of the Symfony AI monorepo - a unified abstractio" "src/platform/CLAUDE.md" && grep -qF "This is the Store component of the Symfony AI ecosystem, providing a low-level a" "src/store/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -117,4 +117,5 @@ Each component uses:
 - Add @author tags to newly introduced classes by the user
 - Prefer classic if statements over short-circuit evaluation when possible
 - Define array shapes for parameters and return types
-- Use project specific exceptions instead of global exception classes like \RuntimeException, \InvalidArgumentException etc.
\ No newline at end of file
+- Use project specific exceptions instead of global exception classes like \RuntimeException, \InvalidArgumentException etc.
+- NEVER mention Claude as co-author in commits
\ No newline at end of file
diff --git a/demo/CLAUDE.md b/demo/CLAUDE.md
@@ -0,0 +1,103 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+
+## Project Overview
+
+This is a Symfony 7.3 demo application showcasing AI integration capabilities using Symfony AI components. The application demonstrates various AI use cases including RAG (Retrieval Augmented Generation), streaming chat, multimodal interactions, and MCP (Model Context Protocol) server functionality.
+
+## Architecture
+
+### Core Components
+- **Chat Systems**: Multiple specialized chat implementations in `src/` (Blog, YouTube, Wikipedia, Audio, Stream)
+- **Twig LiveComponents**: Interactive UI components using Symfony UX for real-time chat interfaces  
+- **AI Agents**: Configured agents with different models, tools, and system prompts
+- **Vector Store**: ChromaDB integration for embedding storage and similarity search
+- **MCP Tools**: Model Context Protocol tools for extending agent capabilities
+
+### Key Technologies
+- Symfony 7.3 with UX components (LiveComponent, Turbo, Typed)
+- OpenAI GPT-4o-mini models and embeddings
+- ChromaDB vector database
+- FrankenPHP runtime
+- Docker Compose for ChromaDB service
+
+## Development Commands
+
+### Environment Setup
+```bash
+# Start ChromaDB service
+docker compose up -d
+
+# Install dependencies
+composer install
+
+# Set OpenAI API key
+echo "OPENAI_API_KEY='sk-...'" > .env.local
+
+# Initialize vector store
+symfony console app:blog:embed -vv
+
+# Test vector store
+symfony console app:blog:query
+
+# Start development server
+symfony serve -d
+```
+
+### Testing
+```bash
+# Run all tests
+vendor/bin/phpunit
+
+# Run specific test
+vendor/bin/phpunit tests/SmokeTest.php
+
+# Run with coverage
+vendor/bin/phpunit --coverage-text
+```
+
+### Code Quality
+```bash
+# Fix code style (uses PHP CS Fixer via Shim)
+vendor/bin/php-cs-fixer fix
+
+# Static analysis
+vendor/bin/phpstan analyse
+```
+
+### MCP Server
+```bash
+# Start MCP server
+symfony console mcp:server
+
+# Test MCP server (paste in terminal)
+{"method":"tools/list","jsonrpc":"2.0","id":1}
+```
+
+## Configuration Structure
+
+### AI Configuration (`config/packages/ai.yaml`)
+- **Agents**: Multiple pre-configured agents (blog, stream, youtube, wikipedia, audio)
+- **Platform**: OpenAI integration with API key from environment
+- **Store**: ChromaDB vector store for similarity search
+- **Indexer**: Text embedding model configuration
+
+### Chat Implementations
+Each chat type follows the pattern:
+- `Chat` class: Handles message flow and session management
+- `TwigComponent` class: LiveComponent for UI interaction
+- Agent configuration in `ai.yaml`
+
+### Session Management
+Chat history stored in Symfony sessions with component-specific keys (e.g., 'blog-chat', 'stream-chat').
+
+## Development Notes
+
+- Uses PHP 8.4+ with strict typing and modern PHP features
+- All AI agents use OpenAI GPT-4o-mini by default
+- Vector embeddings use OpenAI's text-ada-002 model
+- ChromaDB runs on port 8080 (mapped from container port 8000)
+- Application follows Symfony best practices with dependency injection
+- LiveComponents provide real-time UI updates without custom JavaScript
+- MCP server enables tool integration for AI agents
\ No newline at end of file
diff --git a/examples/CLAUDE.md b/examples/CLAUDE.md
@@ -0,0 +1,71 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+
+## Project Overview
+
+This is the examples directory of the Symfony AI monorepo, containing standalone examples demonstrating component usage across different AI platforms. The examples serve as both reference implementations and integration tests.
+
+## Development Commands
+
+### Setup
+```bash
+# Install dependencies
+composer install
+
+# Link local AI components for development
+../link
+
+# Start Docker services for store examples
+docker compose up -d
+```
+
+### Running Examples
+
+#### Standalone Examples
+```bash
+# Run a specific example
+php openai/chat.php
+
+# Run with verbose output to see HTTP and tool calls
+php openai/toolcall-stream.php -vvv
+```
+
+#### Example Runner
+```bash
+# Run all examples in parallel
+./runner
+
+# Run examples from specific subdirectories
+./runner openai mistral
+
+# Filter examples by name pattern
+./runner --filter=toolcall
+```
+
+### Environment Configuration
+Examples require API keys configured in `.env.local`. Copy from `.env` template and add your keys for the platforms you want to test.
+
+## Architecture
+
+### Directory Structure
+- Each subdirectory represents a different AI platform (openai/, anthropic/, gemini/, etc.)
+- `misc/` contains cross-platform examples
+- `rag/` contains RAG (Retrieval Augmented Generation) examples
+- `toolbox/` contains utility tools and integrations
+- `bootstrap.php` provides common setup and utilities for all examples
+
+### Common Patterns
+- All examples use the shared `bootstrap.php` for setup
+- Examples follow a consistent structure with platform-specific clients
+- Verbose output (`-vv`, `-vvv`) shows detailed HTTP requests and responses
+- Examples demonstrate both synchronous and streaming capabilities
+
+### Dependencies
+Examples use `@dev` versions of Symfony AI components:
+- `symfony/ai-platform`
+- `symfony/ai-agent` 
+- `symfony/ai-store`
+
+## Testing
+Examples serve as integration tests. The runner executes them in parallel to verify all components work correctly across different platforms.
\ No newline at end of file
diff --git a/src/agent/CLAUDE.md b/src/agent/CLAUDE.md
@@ -0,0 +1,94 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/code) when working with code in the Agent component.
+
+## Component Overview
+
+The Agent component provides a framework for building AI agents that interact with users and perform tasks. It sits on top of the Platform component and optionally integrates with the Store component for memory capabilities.
+
+## Architecture
+
+The Agent component follows a processor-based architecture:
+
+### Core Classes
+- **Agent** (`src/Agent.php`): Main agent class that orchestrates input/output processing
+- **AgentInterface** (`src/AgentInterface.php`): Contract for agent implementations
+- **Chat** (`src/Chat.php`): High-level chat interface with conversation management
+- **Input/Output** (`src/Input.php`, `src/Output.php`): Data containers for processing pipeline
+
+### Processing Pipeline
+- **InputProcessorInterface** (`src/InputProcessorInterface.php`): Contract for input processors
+- **OutputProcessorInterface** (`src/OutputProcessorInterface.php`): Contract for output processors
+
+### Key Features
+- **Memory System** (`src/Memory/`): Conversation memory with embedding support
+- **Toolbox** (`src/Toolbox/`): Tool integration for function calling capabilities
+- **Structured Output** (`src/StructuredOutput/`): Support for typed responses
+- **Message Stores** (`src/Chat/MessageStore/`): Persistence for chat conversations
+
+## Development Commands
+
+### Testing
+```bash
+# Run all tests
+vendor/bin/phpunit
+
+# Run specific test
+vendor/bin/phpunit tests/AgentTest.php
+
+# Run tests with coverage
+vendor/bin/phpunit --coverage-html coverage/
+```
+
+### Code Quality
+```bash
+# Static analysis (from component directory)
+vendor/bin/phpstan analyse
+
+# Code style fixing (from monorepo root)
+cd ../../.. && vendor/bin/php-cs-fixer fix src/agent/
+```
+
+## Component-Specific Architecture
+
+### Input/Output Processing Chain
+The agent uses a middleware-like pattern:
+1. Input processors modify requests before sending to the platform
+2. Platform processes the request  
+3. Output processors modify responses before returning
+
+### Built-in Processors
+- **SystemPromptInputProcessor**: Adds system prompts to conversations
+- **ModelOverrideInputProcessor**: Allows runtime model switching
+- **MemoryInputProcessor**: Adds conversation context from memory providers
+
+### Memory Providers
+- **StaticMemoryProvider**: Simple in-memory storage
+- **EmbeddingProvider**: Vector-based semantic memory using Store component
+
+### Tool Integration
+The Toolbox system enables function calling:
+- Tools are auto-discovered via attributes
+- Fault-tolerant execution with error handling
+- Event system for tool lifecycle management
+
+## Dependencies
+
+The Agent component depends on:
+- **Platform component**: Required for AI model communication
+- **Store component**: Optional, for embedding-based memory
+- **Symfony components**: HttpClient, Serializer, PropertyAccess, Clock
+
+## Testing Patterns
+
+- Use `MockHttpClient` for HTTP mocking instead of response mocking
+- Test processors independently from the main Agent class
+- Use fixtures from `/fixtures` for multimodal content testing
+- Prefer `self::assert*` over `$this->assert*` in tests
+
+## Development Notes
+
+- All new classes should have `@author` tags
+- Use component-specific exceptions from `src/Exception/`
+- Follow Symfony coding standards with `@Symfony` PHP CS Fixer rules
+- The component is marked as experimental and subject to BC breaks
\ No newline at end of file
diff --git a/src/ai-bundle/CLAUDE.md b/src/ai-bundle/CLAUDE.md
@@ -0,0 +1,117 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+
+## Project Overview
+
+The Symfony AI Bundle is an integration bundle that provides Symfony dependency injection configuration for the Symfony AI components (Platform, Agent, Store). It enables declarative configuration of AI agents, platforms, vector stores, and indexers through semantic YAML configuration and PHP attributes.
+
+## Architecture
+
+### Core Integration Points
+- **Platform Integration**: Configures AI platforms (OpenAI, Anthropic, Azure, Gemini, etc.) as services
+- **Agent Configuration**: Sets up AI agents with tools, processors, and system prompts
+- **Store Configuration**: Configures vector stores for document retrieval (ChromaDB, Pinecone, etc.)
+- **Security Integration**: Provides `#[IsGrantedTool]` attribute for tool-level authorization
+- **Profiler Integration**: Adds debug toolbar integration for monitoring AI interactions
+
+### Key Components
+- `AiBundle.php`: Main bundle class handling service configuration and compiler passes
+- `ProcessorCompilerPass.php`: Compiler pass for registering input/output processors
+- Security system with `IsGrantedToolAttributeListener` for runtime permission checks
+- Profiler data collector and traceable decorators for debugging
+
+## Development Commands
+
+### Testing
+Run the test suite using PHPUnit 11:
+```bash
+vendor/bin/phpunit
+```
+
+Run specific test file:
+```bash
+vendor/bin/phpunit tests/DependencyInjection/AiBundleTest.php
+```
+
+Run tests with coverage:
+```bash
+vendor/bin/phpunit --coverage-html coverage/
+```
+
+### Static Analysis
+Run PHPStan analysis:
+```bash
+vendor/bin/phpstan analyse
+```
+
+The bundle uses PHPStan level 6 and includes custom extension rules for Symfony AI components.
+
+### Code Quality
+This bundle follows the parent monorepo's PHP CS Fixer configuration. Code style fixes should be run from the monorepo root.
+
+## Configuration Architecture
+
+The bundle processes configuration through several main sections:
+
+### Platform Configuration
+Supports multiple AI platforms through factory classes:
+- Anthropic, OpenAI, Azure OpenAI, Gemini, Vertex AI
+- Each platform creates a `Platform` service with HTTP client integration
+- Automatic service aliasing when only one platform is configured
+
+### Agent Configuration
+Creates `Agent` services with:
+- Model configuration (class, name, options)
+- Tool integration via `#[AsTool]` attribute or explicit service references
+- Input/Output processor chains for request/response handling
+- System prompt configuration with optional tool inclusion
+- Token usage tracking for supported platforms
+
+### Store Configuration
+Supports vector stores for document retrieval:
+- Local stores (memory, cache)
+- Cloud stores (Azure Search, Pinecone, Qdrant)
+- Database stores (MongoDB, ClickHouse, Neo4j)
+
+### Security Integration
+- `#[IsGrantedTool]` attribute for method-level authorization
+- Integration with Symfony Security component
+- Runtime permission checking through event listeners
+
+## Service Registration Patterns
+
+### Attribute-Based Registration
+The bundle automatically registers services tagged with:
+- `#[AsTool]` - Tool registration with name and description
+- `#[AsInputProcessor]` - Input processor for specific agents
+- `#[AsOutputProcessor]` - Output processor for specific agents
+
+### Interface-Based Autoconfiguration
+Automatic tagging for:
+- `InputProcessorInterface` → `ai.agent.input_processor`
+- `OutputProcessorInterface` → `ai.agent.output_processor`
+- `ModelClientInterface` → `ai.platform.model_client`
+
+## Debug and Development Features
+
+### Profiler Integration
+In debug mode, the bundle provides:
+- Traceable decorators for platforms and toolboxes
+- Data collector for Symfony Profiler toolbar
+- Monitoring of AI interactions and token usage
+
+### Error Handling
+- Fault-tolerant toolbox wrapper for graceful tool failures
+- Comprehensive exception hierarchy with bundle-specific exceptions
+- Clear error messages for missing dependencies
+
+## Testing Patterns
+
+The test suite demonstrates:
+- Bundle configuration testing with `AiBundleTest`
+- Compiler pass testing for processor registration
+- Security integration testing with mock authorization checker
+- Profiler data collection and tracing functionality
+
+Tests use PHPUnit 11 with strict configuration and coverage requirements.
\ No newline at end of file
diff --git a/src/platform/CLAUDE.md b/src/platform/CLAUDE.md
@@ -0,0 +1,74 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+
+## Platform Component Overview
+
+This is the Platform component of the Symfony AI monorepo - a unified abstraction for interacting with AI platforms like OpenAI, Anthropic, Azure, Gemini, VertexAI, Ollama, and others. The component provides consistent interfaces regardless of the underlying AI provider.
+
+## Development Commands
+
+### Testing
+```bash
+# Run all tests
+vendor/bin/phpunit
+
+# Run specific test
+vendor/bin/phpunit tests/ModelTest.php
+
+# Run tests with coverage
+vendor/bin/phpunit --coverage-html coverage
+```
+
+### Code Quality
+```bash
+# Run PHPStan static analysis
+vendor/bin/phpstan analyse
+
+# Fix code style (run from project root)
+cd ../../.. && vendor/bin/php-cs-fixer fix src/platform/
+```
+
+### Installing Dependencies
+```bash
+composer install
+
+# Update dependencies
+composer update
+```
+
+## Architecture
+
+### Core Classes
+- **Platform**: Main entry point implementing `PlatformInterface`
+- **Model**: Represents AI models with provider-specific configurations
+- **Contract**: Abstract contracts for different AI capabilities (chat, embedding, speech, etc.)
+- **Message**: Message system for AI interactions
+- **Tool**: Function calling capabilities
+- **Bridge**: Provider-specific implementations (OpenAI, Anthropic, etc.)
+
+### Key Directories
+- `src/Bridge/`: Provider-specific implementations
+- `src/Contract/`: Abstract contracts and interfaces  
+- `src/Message/`: Message handling system
+- `src/Tool/`: Function calling and tool definitions
+- `src/Result/`: Result types and converters
+- `src/Exception/`: Platform-specific exceptions
+
+### Provider Support
+The component supports multiple AI providers through Bridge implementations:
+- OpenAI (GPT models, DALL-E, Whisper)
+- Anthropic (Claude models)
+- Azure OpenAI
+- Google Gemini
+- VertexAI
+- AWS Bedrock
+- Ollama
+- And many others (see composer.json keywords)
+
+## Testing Architecture
+
+- Uses PHPUnit 11+ with strict configuration
+- Test fixtures located in `../../fixtures` for multi-modal content
+- Mock HTTP client pattern preferred over response mocking
+- Component follows Symfony coding standards
\ No newline at end of file
diff --git a/src/store/CLAUDE.md b/src/store/CLAUDE.md
@@ -0,0 +1,67 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+
+## Project Overview
+
+This is the Store component of the Symfony AI ecosystem, providing a low-level abstraction for storing and retrieving documents in vector stores. The component enables Retrieval Augmented Generation (RAG) applications by offering unified interfaces for various vector database implementations.
+
+## Development Commands
+
+### Testing
+Run the full test suite:
+```bash
+vendor/bin/phpunit
+```
+
+Run tests for a specific bridge (e.g., InMemory):
+```bash
+vendor/bin/phpunit tests/Bridge/Local/InMemoryStoreTest.php
+```
+
+Run a single test method:
+```bash
+vendor/bin/phpunit --filter testMethodName
+```
+
+### Code Quality
+Run PHPStan static analysis:
+```bash
+vendor/bin/phpstan analyse
+```
+
+### Installation
+Install dependencies:
+```bash
+composer install
+```
+
+## Architecture
+
+### Core Interfaces
+- **StoreInterface**: Main interface defining `add()` and `query()` methods for vector document storage and retrieval
+- **ManagedStoreInterface**: Extension interface providing `setup()` and `drop()` methods for store lifecycle management
+- **Indexer**: High-level service that converts TextDocuments to VectorDocuments and stores them in batches
+
+### Bridge Pattern Architecture
+The component follows a bridge pattern with implementations for multiple vector stores:
+
+**Database Bridges**: Postgres, MariaDB, ClickHouse, MongoDB, Neo4j, SurrealDB
+**Cloud Service Bridges**: Azure AI Search, Pinecone
+**Search Engine Bridges**: Meilisearch, Typesense, Weaviate, Qdrant, Milvus
+**Local Bridges**: InMemoryStore, CacheStore (PSR-6)
+**External Service Bridges**: ChromaDb (requires codewithkyrian/chromadb-php)
+
+### Document System
+- **TextDocument**: Input documents containing text and metadata
+- **VectorDocument**: Documents with embedded vectors for storage
+- **Vectorizer**: Converts TextDocuments to VectorDocuments using AI Platform
+- **Transformers**: ChainTransformer, TextSplitTransformer, ChunkDelayTransformer for document preprocessing
+
+### Key Dependencies
+- **symfony/ai-platform**: For AI model integration and vectorization
+- **psr/log**: For logging throughout the indexing process
+- **symfony/http-client**: For HTTP-based vector store communication
+
+### Test Architecture
+Tests follow the same bridge structure as source code, with each store implementation having corresponding test classes. Tests use PHPUnit 11+ with strict configuration for coverage and error handling.
\ No newline at end of file
PATCH

echo "Gold patch applied."
