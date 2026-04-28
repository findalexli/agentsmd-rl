#!/usr/bin/env bash
set -euo pipefail

cd /workspace/php-ai-client

# Idempotency guard
if grep -qF "The project uses PHPUnit for unit testing. Test files are located in the `tests/" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,87 +1,89 @@
-# PHP AI Client SDK
+# PHP AI Client - Coding Agent Guide
 
-## Project brief
+## Project Overview
 
-The project implements a provider agnostic PHP AI client SDK to communicate with any generative AI models of various capabilities using a uniform API.
+The PHP AI Client is a provider-agnostic PHP SDK designed to communicate with any generative AI model across various capabilities through a uniform API. It is a WordPress-agnostic PHP package that can be used in any PHP project, providing a flexible and extensible way to integrate AI features.
 
-The project is stewarded by [WordPress AI Team](https://make.wordpress.org/ai/) members and contributors. It is however WordPress agnostic, so that any PHP project can use it.
+## Commands & Scripts
 
-## High-level architecture
+The following commands are available for development and can be run using Composer:
 
-The project architecture has several key design principles:
+*   `composer lint`: Runs all linting checks.
+*   `composer phpcs`: Runs PHP_CodeSniffer to check for coding standards violations.
+*   `composer phpcbf`: Automatically fixes coding standards violations that can be fixed automatically.
+*   `composer phpstan`: Runs PHPStan for static analysis.
+*   `composer test`: Runs the PHPUnit test suite (this is an alias for `composer phpunit`).
+*   `composer phpunit`: Runs the PHPUnit test suite.
 
-### API layers
+## Coding Standards & Compatibility Constraints
 
-1. **Implementer API**: For developers using the SDK to add AI features to their applications
-    - Fluent API: Chain methods for readable, declarative code (e.g. `AiClient::prompt('...')->generateText()`)
-    - Traditional API: Method-based approach with arrays of arguments (e.g. `AiClient::generateText('...')`)
+All code in this project MUST adhere to the coding standards, naming conventions, and documentation standards outlined in the `CONTRIBUTING.md` file. Any agent working on this project MUST read and follow the guidelines in that file before starting any work.
 
-2. **Extender API**: For developers adding new providers, models, or extending functionality
-    - Provider Registry system for managing available AI providers
-    - Model discovery based on capabilities and requirements
+Key constraints include:
 
-### Core concepts
+*   PHP 7.4 as the minimum required version.
+*   PER Coding Style (extending PSR-12).
+*   Strict type hinting for all parameters, return values, and properties.
 
-- **Provider Agnostic**: Abstracts away provider-specific details, allowing code to work with any AI provider (Google, OpenAI, Anthropic, etc.)
-- **Capability-Based Model Selection**: Models can be discovered and selected based on their supported capabilities (text generation, image generation, etc.) and options (input modalities, output formats, etc.)
-- **Uniform Data Structures**: Consistent message formats, file representations, and results across all providers
-- **Modality Support**: Designed to support arbitrary combinations of input/output modalities (text, image, audio, video)
+## Core Principles
 
-### Key design patterns
+*   **Provider Agnostic:** The client is designed to work with any AI provider, avoiding vendor lock-in.
+*   **Extensibility:** The architecture allows for new providers, models, and capabilities to be added without modifying the core functionality.
+*   **Flexibility:** The client supports a wide range of AI capabilities, including text generation, image generation, and more, with arbitrary combinations of input and output modalities.
+*   **Developer Experience:** The client provides two distinct APIs: a simple, fluent API for implementers and a more technical, interface-based API for extenders.
 
-- **Interface Segregation**: Separate interfaces for different model capabilities (TextGenerationModelInterface, ImageGenerationModelInterface, etc.)
-- **Composition over Inheritance**: Models compose capabilities through interfaces rather than inheritance
-- **DTO Pattern**: Data Transfer Objects for messages, results, and configurations with JSON schema support
-- **Builder Pattern**: Fluent builders for constructing prompts and messages
+### Dependency Management
 
-### Directory structure
+The project aims to have minimal third-party dependencies. Any new dependency requires justification and should be discussed before implementation.
 
-- **Production Code**: All production code is found in the `src` directory, in subdirectories that match the namespace structure.
-- **Tests**: PHPUnit tests are found in the `tests/unit` directory, with each test file covering a specific class from `src`.
-    - Each test file is named after the tested class, suffixed with `Test`.
-    - Each test file is located in a subdirectory equivalent to the tested class's directory within `src`.
-    - Test specific mock classes and traits are located in `tests/mocks` and `tests/traits` respectively.
+### Error Handling
 
-### Namespace structure
+The project uses custom exceptions for error handling. When appropriate, throw a custom exception class. Custom exception classes should extend the base `Exception` class.
 
-The production code in `src` follows a structured namespace hierarchy under the root namespace `WordPress\AiClient`:
+### Testing
 
-- `Builders`: Fluent API builders (PromptBuilder, MessageBuilder)
-- `Embeddings`: Embedding-related data structures
-- `Files`: File handling contracts and implementations
-- `Messages`: Message DTOs and enums
-- `Operations`: Long-running operation support
-- `Providers`: Provider system with contracts, models, and registry
-- `Results`: Result data structures and transformations
-- `Tools`: Function calling and tool support
-- `Util`: Utility classes for common operations
+The project uses PHPUnit for unit testing. Test files are located in the `tests/` directory and mirror the structure of the `src/` directory. The test suite is executed by running `composer phpunit`. The `tests/mocks` directory contains mock implementations for testing purposes, and `tests/traits` contains reusable testing traits. All new code requires corresponding unit tests.
 
-## Development tooling and commands
+## Project Architecture Overview
 
-### Linting and code quality
+The project's architecture is heavily inspired by the Vercel AI SDK and is designed to be modular and extensible. Key components include:
 
-- **Run all linting checks**: `composer lint` (runs both PHPCS and PHPStan)
-- **Run PHP CodeSniffer**: `composer phpcs`
-- **Fix code style issues**: `composer phpcbf`
-- **Run PHPStan static analysis**: `composer phpstan`
+*   **`AiClient`:** The main entry point for interacting with the SDK, offering both a fluent API (via `AiClient::prompt()`) and a traditional method-based API.
+*   **Providers:** Implementations for specific AI providers (e.g., OpenAI, Google, Anthropic). Each provider has its own models and metadata.
+*   **`ProviderRegistry`:** Manages the available AI providers and models, allowing for discovery of models based on their capabilities.
+*   **Models:** Represent specific AI models and their capabilities. They are responsible for handling the logic for a specific AI task.
+*   **HTTP Communication:** A custom `HttpTransporter` layer abstracts HTTP communication, decoupling models from specific PSR-18 HTTP client implementations. Models create custom `Request` objects and receive custom `Response` objects, which the transporter translates to and from PSR-7 standards.
 
-### Testing
+For a more detailed overview, refer to the `docs/ARCHITECTURE.md` file.
 
-- **Run PHPUnit tests**: `composer phpunit`
+## Directory Structure
 
-### Dependencies
+*   `src/`: Contains the main source code for the client.
+    *   `src/Builders/`: Home to the fluent API builders (`PromptBuilder`, `MessageBuilder`).
+    *   `src/Providers/`: Contains the contracts and base classes for AI providers and models.
+    *   `src/ProviderImplementations/`: Contains the concrete implementations for specific AI providers like Google, OpenAI, and Anthropic.
+    *   `src/Providers/Http/`: Contains the HTTP communication layer, including the `HttpTransporter`.
+*   `tests/`: Contains the test suite for the project.
+*   `docs/`: Contains the project's documentation, including architecture, requirements, and a glossary.
 
-- **Install dependencies**: `composer install`
-- **Update dependencies**: `composer update`
+## Agent Guidelines
+
+### Naming conventions
 
-## Coding standards and best practices
+### DO:
 
-- **Code style**: All code must be compliant with the [PER Coding Style](https://www.php-fig.org/per/coding-style/), which extends [PSR-12](https://www.php-fig.org/psr/psr-12/).
-- **Minimum required PHP version**: All code must be backward compatible with PHP 7.4. For newer PHP functions, polyfills can be used.
+*   **Read the Docs:** Before making any changes, thoroughly read `CONTRIBUTING.md` and `docs/ARCHITECTURE.md`.
+*   **Follow Coding Standards:** Strictly adhere to the coding standards defined in `CONTRIBUTING.md` and enforced by PHP_CodeSniffer.
+*   **Write Tests:** All new features or bug fixes must be accompanied by corresponding unit tests.
+*   **Use the Fluent API:** When writing examples or tests for the implementer API, prefer the fluent API for readability.
+*   **Use `{@inheritDoc}`:** When implementing an interface method, use `{@inheritDoc}` in the PHPDoc block to avoid duplicating documentation, as specified in `CONTRIBUTING.md`.
 
-### Type hints
+### DON'T:
 
-All parameters, return values, and properties must use explicit type hints, except in cases where providing the correct type hint would be impossible given limitations of backward compatibility with PHP 7.4. In any case, concrete type annotations using PHPStan should be present.
+*   **Bypass the `HttpTransporter`:** Do not use a PSR-18 HTTP client directly within a model. All HTTP communication must go through the `HttpTransporter`.
+*   **Add Provider-Specific Logic to Core:** Keep the core client agnostic. Provider-specific logic should be encapsulated within the provider's implementation in `src/ProviderImplementations/`.
+*   **Introduce Out-of-Scope Features:** Do not add features that are out of scope for this project, such as agents or the Model Context Protocol (MCP), as noted in `docs/REQUIREMENTS.md`.
+*   **Duplicate Documentation:** Avoid duplicating PHPDoc descriptions for methods that implement an interface.
 
 ### Exception handling
 
@@ -92,16 +94,8 @@ All exceptions must use the project's custom exception classes rather than PHP b
 - All custom exceptions implement `WordPress\AiClient\Exceptions\AiClientExceptionInterface` for unified exception handling
 - Follow usage-driven design: only implement static factory methods that are actually used in the codebase
 
-### Naming conventions
-
-The following naming conventions must be followed for consistency and autoloading:
-
-- Interfaces are suffixed with `Interface`.
-- Traits are suffixed with `Trait`.
-- Enums are suffixed with `Enum`.
-- File names are the same as the class, trait, and interface name for PSR-4 autoloading.
-- Classes, interfaces, and traits, and namespaces are not prefixed with `Ai`, excluding the root namespace.
-
-## Further reading
+## Common Pitfalls
 
-The `docs` folder in this repository provides additional in-depth information about various aspects of the project, such as its requirements or architecture.
+*   **Direct HTTP Client Usage:** A common mistake is to instantiate a PSR-18 client directly in a model. This is incorrect. Instead, the model should receive an `HttpTransporter` instance and use it to send requests.
+*   **Ignoring the Fluent API:** While the traditional API is available, the fluent API is the preferred way for implementers to use the client. Avoid writing complex, nested method calls when the fluent API provides a cleaner alternative.
+*   **Duplicating Interface Documentation:** Manually writing PHPDoc descriptions for methods that implement an interface is a common pitfall. The `{@inheritDoc}` tag should be used instead to inherit the documentation from the interface.
PATCH

echo "Gold patch applied."
