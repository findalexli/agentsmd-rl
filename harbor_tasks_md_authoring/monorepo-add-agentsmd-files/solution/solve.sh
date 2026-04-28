#!/usr/bin/env bash
set -euo pipefail

cd /workspace/monorepo

# Idempotency guard
if grep -qF "This is the InversifyJS monorepo - a TypeScript dependency injection library eco" "AGENTS.md" && grep -qF "This directory contains example packages that demonstrate how to use the Inversi" "packages/container/examples/AGENTS.md" && grep -qF "The `@inversifyjs/binding-decorators` package provides decorator-based binding c" "packages/container/libraries/binding-decorators/AGENTS.md" && grep -qF "The `@inversifyjs/common` package provides shared utilities, types, and constant" "packages/container/libraries/common/AGENTS.md" && grep -qF "The `@inversifyjs/container` package provides the high-level container API and u" "packages/container/libraries/container/AGENTS.md" && grep -qF "The `@inversifyjs/core` package is the foundational layer of the InversifyJS dep" "packages/container/libraries/core/AGENTS.md" && grep -qF "The `@inversifyjs/plugin-dispose` package provides automatic resource disposal a" "packages/container/libraries/plugin-dispose/AGENTS.md" && grep -qF "The `@inversifyjs/plugin` package provides the plugin system interface and base " "packages/container/libraries/plugin/AGENTS.md" && grep -qF "The `@inversifyjs/strongly-typed` package provides enhanced type safety and comp" "packages/container/libraries/strongly-typed/AGENTS.md" && grep -qF "This directory contains code examples and tools for generating documentation exa" "packages/docs/tools/AGENTS.md" && grep -qF "This directory contains shared foundation tooling packages that provide common c" "packages/foundation/tools/AGENTS.md" && grep -qF "This is the InversifyJS framework core package that provides foundational framew" "packages/framework/core/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,196 @@
+# AGENTS.md
+
+## Project Overview
+
+This is the InversifyJS monorepo - a TypeScript dependency injection library ecosystem. The repository contains multiple packages organized into categories:
+
+- **Framework packages**: Core framework and HTTP functionality
+- **Container packages**: DI container implementation, plugins, and examples
+- **Foundation packages**: Shared tooling (ESLint, Prettier, TypeScript configs)
+- **Documentation packages**: Code examples and website services
+- **Logger package**: Logging utilities
+- **JSON Schema packages**: Schema validation utilities
+- **Open API packages**: OpenAPI integration
+
+## Build and Test Commands
+
+### Setup
+```bash
+# Install dependencies
+pnpm install
+
+# Build all packages
+pnpm run build
+
+# Run all tests
+pnpm test
+```
+
+### Development Workflow
+```bash
+# Format code
+pnpm run format
+
+# Lint code
+pnpm run lint
+
+# Run tests for a specific package
+pnpm run --filter "@inversifyjs/package-name" test
+
+# Run only unit tests
+pnpm run test:unit
+
+# Run only integration tests  
+pnpm run test:integration
+
+# Run tests with coverage
+pnpm run test:coverage
+
+```
+
+### Working with Specific Packages
+```bash
+# Build a specific package
+pnpm run --filter "@inversifyjs/package-name" build
+
+# Test a specific package
+pnpm run --filter "@inversifyjs/package-name" test
+
+# Format a specific package
+pnpm run --filter "@inversifyjs/package-name" format
+```
+
+## Code Style Guidelines
+
+- **TypeScript**: Strict mode enabled across all packages
+- **Testing**: Use Vitest with extensive unit and integration test coverage
+- **Mocking**: External modules are mocked using `vitest.fn()`
+- **Formatting**: Prettier configuration shared via `@inversifyjs/foundation-prettier-config`
+- **Linting**: ESLint configuration shared via `@inversifyjs/foundation-eslint-config`
+
+## Testing Instructions
+
+The project follows a comprehensive testing strategy with multiple test types:
+
+### Test Types
+- **Unit Tests** (`*.spec.ts`): Test individual functions/classes in isolation
+- **Integration Tests** (`*.int.spec.ts`): Test component interactions
+- **End-to-End Tests**: Full system tests (some packages)
+- **Type Tests** (`*.spec-d.ts`): TypeScript type checking tests
+
+### Test Structure
+Follow the structured testing patterns documented in:
+- [Unit Testing Guidelines](./docs/testing/unit-testing.md)
+- [Test Fixtures Guidelines](./docs/testing/fixtures.md)
+
+### Key Testing Principles
+1. **Four-layer describe structure**: Class → Method → Input → Flow scopes
+2. **Vitest mocking**: Use `vitest.fn()` and `vitest.mock()` for external dependencies
+3. **Fixture classes**: Create reusable test fixtures with static methods
+4. **Clear naming**: Use descriptive test names with "when called, and [condition]" pattern
+
+### Running Tests
+```bash
+# Run all tests
+pnpm test
+
+# Run only unit tests
+pnpm run test:unit
+
+# Run only integration tests
+pnpm run test:integration
+
+# Run tests for uncommitted changes
+pnpm run test:uncommitted
+
+# Run with coverage
+pnpm run test:coverage
+```
+
+## Package Types and Structure
+
+### Core Library Packages
+Main implementation packages with dual CJS/ESM builds:
+- `/packages/framework/core/` - Framework core
+- `/packages/container/libraries/` - Container implementations
+- `/packages/logger/` - Logging utilities
+
+**Standard structure:**
+- `src/` - TypeScript source code
+- `lib/cjs/` - CommonJS build output
+- `lib/esm/` - ES Module build output
+- `vitest.config.mjs` - Test configuration
+- Standard scripts: `build`, `test`, `lint`, `format`
+
+### Example Packages
+Demonstration packages (usually no tests):
+- `/packages/container/examples/` - Usage examples
+- `/packages/docs/tools/` - Code examples for documentation
+
+### Foundation Packages
+Shared tooling and configuration:
+- `/packages/foundation/tools/` - Shared configs (ESLint, Prettier, TypeScript, etc.)
+
+### Documentation Services
+Docusaurus-based documentation sites:
+- `/packages/docs/services/` - Documentation websites
+
+## Monorepo Architecture
+
+### Workspace Configuration
+- **Package Manager**: pnpm with workspaces
+- **Build Tool**: Turbo for task orchestration
+- **Dependency Management**: Workspace protocol for internal dependencies
+
+### Build System
+- **TypeScript**: Multiple tsconfig files for different output formats
+- **Rollup**: ES module builds
+- **SWC**: Fast TypeScript compilation for tests
+- **Turbo**: Cached, parallelized builds
+
+### Quality Assurance
+- **Pre-commit Hooks**: Husky with lint-staged
+- **Commitlint**: Conventional commit messages
+- **Changesets**: Version management and changelogs
+
+## Security Considerations
+
+- All packages use workspace protocol for internal dependencies
+- Development dependencies are pinned to specific versions
+- No known security vulnerabilities in production dependencies
+- Type-safe dependency injection prevents runtime injection attacks
+
+## Pull Request Guidelines
+
+1. **Branch Naming**: Use descriptive feature branch names
+2. **Commit Messages**: Follow conventional commit format
+3. **Testing**: All changes must include appropriate tests
+4. **Build**: Ensure `pnpm run build` passes
+5. **Linting**: Ensure `pnpm run lint` passes
+6. **Coverage**: Maintain or improve test coverage
+7. **Documentation**: Update relevant docs for public API changes
+
+## Performance Considerations
+
+- Turbo caching significantly speeds up repeated builds
+
+## Common Tasks
+
+### Adding a New Package
+1. Create package directory following existing structure
+2. Add to `pnpm-workspace.yaml`
+3. Configure `package.json` with standard scripts
+4. Add appropriate tsconfig files
+5. Configure Vitest, ESLint, and Prettier
+6. Add to Turbo build pipeline if needed
+
+### Debugging Build Issues
+- Check Turbo cache: builds are cached by input file hashes
+- Verify TypeScript configurations for target output format
+- Ensure all workspace dependencies are properly declared
+- Use `--filter` flag to isolate specific package issues
+
+### Working with Dependencies
+- Use `workspace:*` protocol for internal dependencies
+- Run `pnpm install` after adding new dependencies
+- Check `knip` output for unused dependencies: `pnpm run unused`
diff --git a/packages/container/examples/AGENTS.md b/packages/container/examples/AGENTS.md
@@ -0,0 +1,95 @@
+# AGENTS.md - Container Examples
+
+## Package Overview
+
+This directory contains example packages that demonstrate how to use the InversifyJS container libraries. These are **demonstration packages**, not libraries for consumption.
+
+## Working with Example Packages
+
+### Key Characteristics
+- **No tests required** - examples are meant to be read and understood
+- **Demonstration code** - shows usage patterns, not library implementation
+- **Buildable packages** - examples should compile successfully
+- **Dependencies on workspace packages** - examples use local workspace dependencies
+
+### Development Guidelines
+
+#### Purpose of Examples
+1. **Educational** - teach developers how to use InversifyJS features
+2. **Reference implementations** - show best practices
+3. **Validation** - ensure workspace packages work together correctly
+
+#### Code Quality
+- Examples should compile without errors
+- Follow TypeScript best practices
+- Use clear, descriptive variable names
+- Include meaningful comments explaining concepts
+
+### Build Process
+
+```bash
+# Build example to verify it compiles
+pnpm run build
+
+# Format code for readability
+pnpm run format
+
+# Lint for code quality
+pnpm run lint
+```
+
+### Dependencies
+
+#### Workspace Dependencies
+- Use `workspace:*` for local packages being demonstrated
+- Examples should use published APIs, not internal implementation
+
+#### Peer Dependencies
+- InversifyJS core library is typically a peer dependency
+- Allows examples to work with different InversifyJS versions
+
+### Testing Strategy
+
+#### No Unit Tests Needed
+- Examples demonstrate usage, not library functionality
+- The "test" is whether the example compiles and makes sense
+- Integration with the broader ecosystem is tested elsewhere
+
+#### Validation Through Build
+```bash
+# Verify examples are valid TypeScript
+pnpm run build
+
+# Ensure code follows standards
+pnpm run lint
+pnpm run format
+```
+
+### Common Tasks
+
+#### Creating a New Example
+1. **Identify the concept** to demonstrate
+2. **Create minimal, focused example**
+4. **Verify it builds** successfully
+5. **Test with actual InversifyJS** usage
+
+#### Updating Examples
+1. **Keep examples current** with latest API changes
+2. **Verify compatibility** when workspace packages change
+3. **Update documentation** if usage patterns change
+
+### Important Notes
+
+#### Focus on Clarity
+- Examples should be **easy to understand**
+- Avoid complex scenarios that obscure the main concept
+- Use realistic but simple use cases
+
+#### Maintain Compatibility
+- Examples should work with published InversifyJS versions
+- Test examples when making breaking changes to workspace packages
+- Update examples before releasing new package versions
+
+#### Documentation Value
+- Examples serve as **living documentation**
+- Show both basic and advanced usage patterns where relevant
diff --git a/packages/container/libraries/binding-decorators/AGENTS.md b/packages/container/libraries/binding-decorators/AGENTS.md
@@ -0,0 +1,140 @@
+# AGENTS.md - @inversifyjs/binding-decorators
+
+## Package Overview
+
+The `@inversifyjs/binding-decorators` package provides decorator-based binding configuration for InversifyJS. It enables developers to configure dependency injection through TypeScript decorators, offering a declarative alternative to programmatic container configuration.
+
+## Key Responsibilities
+
+- **Decorator Implementation**: Provides decorators for various binding scenarios
+- **Metadata Management**: Stores and retrieves binding metadata from decorated classes
+- **Reflection Integration**: Works with reflect-metadata for design-time type information
+- **Binding Translation**: Converts decorator metadata into container bindings
+- **Type Safety**: Maintains strong TypeScript support for decorated classes
+
+## Working with Binding Decorators
+
+### Key Characteristics
+- **Decorator-Heavy**: Extensive use of TypeScript decorators
+- **Reflection Dependent**: Requires reflect-metadata polyfill
+- **Type Information**: Relies on TypeScript's emitted metadata
+- **Peer Dependency**: Works with inversify container as peer dependency
+- **Compile-Time Configuration**: Decorators are processed at compilation
+
+### Testing Strategy
+
+#### Unit Testing Requirements
+Follow the [structured testing approach](../../../../docs/testing/unit-testing.md):
+
+1. **Class Scope**: Test each decorator function and metadata processor
+2. **Method Scope**: Test decorator application and metadata extraction
+3. **Input Scope**: Test various decorator parameter combinations
+4. **Flow Scope**: Test different decoration scenarios and edge cases
+
+#### Critical Test Areas
+- **Decorator Application**: Test that decorators properly set metadata
+- **Metadata Extraction**: Test that metadata can be correctly retrieved
+- **Type Reflection**: Test integration with TypeScript's type emission
+- **Container Integration**: Test that decorated classes work with container
+- **Error Scenarios**: Test invalid decorator usage and helpful error messages
+- **Compilation**: Test TypeScript compilation with various decorator configurations
+
+### Development Guidelines
+
+#### Decorator Design Principles
+- **Intuitive Naming**: Decorator names should clearly indicate their purpose
+- **Composable**: Decorators should work well together
+- **Type Safe**: Decorators should preserve and enhance type information
+- **Runtime Safe**: Graceful handling when reflection metadata is missing
+- **Consistent API**: Similar decorators should have similar signatures
+
+#### Metadata Management
+- **Metadata Keys**: Use consistent, namespaced metadata keys
+- **Data Structures**: Design efficient metadata storage formats
+- **Inheritance**: Handle decorator inheritance correctly
+- **Performance**: Minimize metadata lookup overhead
+
+#### TypeScript Integration
+- **experimentalDecorators**: Requires experimental decorator support
+- **emitDecoratorMetadata**: Needs decorator metadata emission
+- **Type Preservation**: Maintain type information through decoration
+- **Generic Support**: Handle generic classes and methods correctly
+
+### Build and Test Commands
+
+```bash
+# Build the package
+pnpm run build
+
+# Run all tests
+pnpm run test
+
+# Run only unit tests
+pnpm run test:unit
+
+# Run only integration tests
+pnpm run test:integration
+
+# Generate coverage report
+pnpm run test:coverage
+```
+
+### Common Development Tasks
+
+#### Adding New Decorators
+1. **Design the API**: Consider use cases and parameter requirements
+2. **Implement Decorator**: Create decorator function with proper typing
+3. **Add Metadata Logic**: Define how decorator information is stored
+4. **Create Type Definitions**: Ensure proper TypeScript support
+5. **Write Comprehensive Tests**: Cover all scenarios and integrations
+6. **Update Documentation**: Add usage examples and best practices
+
+#### Enhancing Metadata Processing
+1. **Analyze Requirements**: Understand what metadata is needed
+2. **Design Storage Format**: Create efficient metadata structures
+3. **Implement Processors**: Add logic to extract and transform metadata
+4. **Test Extraction Logic**: Verify metadata is correctly processed
+5. **Benchmark Performance**: Ensure acceptable metadata lookup speed
+
+#### Improving Type Safety
+1. **Identify Type Issues**: Find areas where type information is lost
+2. **Enhance Type Definitions**: Improve decorator type signatures
+3. **Add Generic Constraints**: Use constraints for better type checking
+4. **Test TypeScript Compilation**: Verify types work correctly
+5. **Update Examples**: Show best practices for type safety
+
+### Important Notes
+
+#### TypeScript Configuration
+Requires specific TypeScript compiler options:
+```json
+{
+  "compilerOptions": {
+    "experimentalDecorators": true,
+    "emitDecoratorMetadata": true
+  }
+}
+```
+
+#### Runtime Requirements
+- **reflect-metadata**: Must be imported before using decorators
+- **Container Configuration**: Decorated classes must still be bound to container
+- **Metadata Availability**: Graceful degradation when metadata is missing
+
+#### Performance Considerations
+- **Metadata Lookup**: Cache metadata where possible
+- **Decorator Overhead**: Minimize runtime overhead of decorators
+- **Bundle Size**: Consider impact on application bundle size
+- **Tree Shaking**: Ensure unused decorators can be tree-shaken
+
+#### Common Pitfalls
+- **Missing reflect-metadata**: Ensure polyfill is properly loaded
+- **Circular Dependencies**: Decorators don't prevent circular dependency issues
+- **Generic Type Erasure**: TypeScript generic information is not available at runtime
+- **Inheritance**: Decorator inheritance can be complex with class hierarchies
+
+#### Migration and Compatibility
+- **Inversify Version**: Maintain compatibility with target inversify versions
+- **Decorator Standard**: Consider future TypeScript decorator changes
+- **Breaking Changes**: Coordinate with container package for major changes
+- **Legacy Support**: Provide migration paths for older decorator patterns
diff --git a/packages/container/libraries/common/AGENTS.md b/packages/container/libraries/common/AGENTS.md
@@ -0,0 +1,171 @@
+# AGENTS.md - @inversifyjs/common
+
+## Package Overview
+
+The `@inversifyjs/common` package provides shared utilities, types, and constants used across the entire InversifyJS container ecosystem. It serves as the foundation layer that other packages build upon, ensuring consistency and avoiding code duplication.
+
+## Key Responsibilities
+
+- **Shared Types**: Common interfaces and type definitions
+- **Utility Functions**: Helper functions used across multiple packages
+- **Constants**: Shared constants and enumerations
+- **Base Interfaces**: Core abstractions that other packages implement
+- **Error Types**: Common error classes and error handling utilities
+
+## Working with Common
+
+### Key Characteristics
+- **Foundation Package**: Other packages depend on this one
+- **Stable API**: Breaking changes affect the entire ecosystem
+- **Utility Focus**: Provides tools, not business logic
+- **Type-Heavy**: Extensive use of TypeScript features
+- **Well-Tested**: Changes require comprehensive testing
+
+### Testing Strategy
+
+#### Unit Testing Requirements
+Follow the [structured testing approach](../../../../docs/testing/unit-testing.md):
+
+1. **Class Scope**: Test each utility class and error type
+2. **Method Scope**: Test each utility function thoroughly  
+3. **Input Scope**: Test various input scenarios and edge cases
+4. **Flow Scope**: Test different execution paths and error conditions
+
+#### Critical Test Areas
+- **Utility Functions**: Test all helper functions with various inputs
+- **Type Definitions**: Test TypeScript compilation and type inference
+- **Error Classes**: Test error creation and message formatting
+- **Constants**: Verify constant values and types
+- **Edge Cases**: Test boundary conditions and error scenarios
+
+### Development Guidelines
+
+#### Stability Requirements
+- **Backward Compatibility**: Maintain API compatibility across versions
+- **Deprecation Process**: Follow proper deprecation for removed features
+- **Impact Analysis**: Consider effects on all consuming packages
+- **Migration Support**: Provide clear migration paths for changes
+
+#### Code Quality Standards
+- **Pure Functions**: Utilities should be pure functions where possible
+- **Immutability**: Prefer immutable patterns and data structures
+- **Performance**: Optimize for common use cases
+- **Documentation**: Comprehensive JSDoc for all public APIs
+
+#### Type Safety Practices
+- **Strict Types**: Use strict TypeScript settings
+- **Generic Constraints**: Proper generic type constraints
+- **Type Guards**: Provide type guard functions where useful
+- **Branded Types**: Use branded types for domain-specific values
+
+### Build and Test Commands
+
+```bash
+# Build the package
+pnpm run build
+
+# Run all tests
+pnpm run test
+
+# Run only unit tests
+pnpm run test:unit
+
+# Run only integration tests
+pnpm run test:integration
+
+# Generate coverage report
+pnpm run test:coverage
+```
+
+### Common Development Tasks
+
+#### Adding New Utility Functions
+1. **Identify Need**: Ensure utility is needed by multiple packages
+2. **Design Interface**: Create clean, reusable API
+3. **Implement Function**: Write pure, well-documented function
+4. **Add Comprehensive Tests**: Cover all scenarios and edge cases
+5. **Update Type Definitions**: Ensure proper TypeScript support
+
+#### Adding New Types
+1. **Analyze Requirements**: Understand what types are needed
+2. **Design Type Hierarchy**: Create logical, extensible type structure
+3. **Define Interfaces**: Write clear, well-documented interfaces
+4. **Add Type Tests**: Test TypeScript compilation and inference
+5. **Update Documentation**: Document usage patterns and examples
+
+#### Refactoring Shared Code
+1. **Identify Duplicated Code**: Find code repeated across packages
+2. **Extract Common Logic**: Move shared logic to common package
+3. **Design Generic Interface**: Create reusable abstraction
+4. **Update All Consumers**: Migrate packages to use common code
+5. **Test Integration**: Verify all packages work correctly
+
+### Important Patterns
+
+#### Error Handling
+```typescript
+// Base error class for consistent error handling
+export abstract class InversifyError extends Error {
+  constructor(message: string) {
+    super(message);
+    this.name = this.constructor.name;
+  }
+}
+
+// Specific error types
+export class CircularDependencyError extends InversifyError {
+  constructor(serviceIdentifier: string) {
+    super(`Circular dependency detected for service: ${serviceIdentifier}`);
+  }
+}
+```
+
+#### Utility Functions
+```typescript
+// Type-safe utility functions
+export function isFunction(value: unknown): value is Function {
+  return typeof value === 'function';
+}
+
+export function isString(value: unknown): value is string {
+  return typeof value === 'string';
+}
+```
+
+#### Type Definitions
+```typescript
+// Shared interfaces
+export interface ServiceIdentifier<T = any> {
+  readonly name?: string;
+  readonly value: string | symbol | Function;
+}
+
+// Generic type constraints
+export type Constructor<T = {}> = new (...args: any[]) => T;
+```
+
+### Important Notes
+
+#### Breaking Changes
+- **Ecosystem Impact**: Changes affect all packages in the monorepo
+- **Version Coordination**: Coordinate major version bumps across packages
+- **Migration Planning**: Provide comprehensive migration guides
+- **Testing**: Test changes against all consuming packages
+
+#### Performance Considerations
+- **Hot Path Functions**: Utilities may be called frequently
+- **Memory Usage**: Minimize memory allocations in utilities
+- **Bundle Size**: Consider impact on final bundle size
+- **Tree Shaking**: Ensure utilities are tree-shakable
+
+#### Maintenance Guidelines
+- **Regular Reviews**: Periodically review for outdated utilities
+- **Deprecation**: Properly deprecate unused functions
+- **Documentation**: Keep documentation up to date
+- **Dependencies**: Avoid adding new dependencies unless absolutely necessary
+
+#### Quality Assurance
+- **High Test Coverage**: Aim for near 100% coverage
+- **Type Safety**: Test TypeScript compilation thoroughly
+- **Cross-Package Testing**: Test integration with consuming packages
+- **Performance Testing**: Benchmark critical utility functions
diff --git a/packages/container/libraries/container/AGENTS.md b/packages/container/libraries/container/AGENTS.md
@@ -0,0 +1,133 @@
+# AGENTS.md - @inversifyjs/container
+
+## Package Overview
+
+The `@inversifyjs/container` package provides the high-level container API and user-facing interfaces for the InversifyJS dependency injection system. It builds on `@inversifyjs/core` to provide a complete, easy-to-use container implementation.
+
+## Key Responsibilities
+
+- **Container API**: Main `Container` class and user-facing methods
+- **Binding DSL**: Fluent API for configuring service bindings
+- **Plugin Integration**: Supports the plugin system for extending functionality
+- **User Experience**: Provides intuitive APIs for common DI scenarios
+- **Snapshot Management**: Container state snapshots for testing and rollback
+
+## Working with Container
+
+### Key Characteristics
+- **User-Facing API**: Focus on developer experience and ease of use
+- **Type Safety**: Extensive TypeScript generics for compile-time safety
+- **Plugin Support**: Integrates with the plugin system seamlessly
+- **Performance**: Built on optimized core algorithms
+- **Testing Support**: Snapshot functionality for test isolation
+
+### Testing Strategy
+
+#### Unit Testing Requirements
+Follow the [structured testing approach](../../../../docs/testing/unit-testing.md):
+
+1. **Class Scope**: Test Container class and binding builders
+2. **Method Scope**: Test each public API method
+3. **Input Scope**: Test various binding configurations and scenarios  
+4. **Flow Scope**: Test different resolution paths and plugin interactions
+
+#### Critical Test Areas
+- **Binding API**: Test all binding methods and configurations
+- **Resolution**: Test get(), resolve(), and related methods
+- **Plugin Integration**: Test plugin lifecycle and interactions
+- **Snapshot Functionality**: Test save/restore operations
+- **Error Scenarios**: Test meaningful error messages
+- **Type Safety**: Test TypeScript compilation and type inference
+
+### Development Guidelines
+
+#### API Design Principles
+- **Intuitive Naming**: Method names should be self-explanatory
+- **Consistent Patterns**: Similar operations should use similar APIs
+- **Type Inference**: Minimize explicit type annotations where possible
+- **Error Prevention**: Design APIs to prevent common mistakes
+- **Backward Compatibility**: Maintain compatibility across versions
+
+#### User Experience Focus
+- **Clear Error Messages**: Provide actionable error information
+- **Good Defaults**: Choose sensible defaults for common scenarios
+- **Examples**: Provide clear usage examples in documentation
+
+#### Plugin Integration
+- **Plugin Lifecycle**: Properly integrate plugin hooks and events
+- **Composability**: Ensure plugins work well together
+- **Performance**: Minimize plugin overhead for core operations
+- **Testing**: Test plugin interactions thoroughly
+
+### Build and Test Commands
+
+```bash
+# Build the package
+pnpm run build
+
+# Run all tests
+pnpm run test
+
+# Run only unit tests
+pnpm run test:unit
+
+# Run only integration tests  
+pnpm run test:integration
+
+# Generate coverage report
+pnpm run test:coverage
+```
+
+#### Consumers
+- **Applications**: End-user applications using InversifyJS
+- **@inversifyjs/plugin-dispose**: Disposal plugin
+- **Framework Integrations**: Various framework-specific packages
+
+### Common Development Tasks
+
+#### Adding New Binding Methods
+1. **Design the API**: Consider type safety and user experience
+2. **Implement the Method**: Add to the binding interface
+3. **Add Type Definitions**: Ensure proper TypeScript support
+4. **Write Comprehensive Tests**: Cover all scenarios and edge cases
+5. **Update Documentation**: Add JSDoc and usage examples
+
+#### Enhancing Container Features
+1. **Analyze User Needs**: Understand the use case and requirements
+2. **Design the Interface**: Create intuitive and type-safe APIs
+3. **Implement Core Logic**: Build on existing core functionality
+4. **Add Plugin Support**: Consider plugin extension points
+5. **Test Thoroughly**: Unit tests, integration tests, real-world scenarios
+
+#### Improving Error Messages
+1. **Identify Pain Points**: Common user errors and confusion
+2. **Enhance Error Context**: Add more helpful information
+3. **Provide Solutions**: Suggest how to fix the issue
+4. **Test Error Scenarios**: Ensure messages are actually helpful
+5. **Update Documentation**: Include troubleshooting guides
+
+### Important Notes
+
+#### Type Safety Best Practices
+- Use service identifiers with strong typing
+- Leverage generic constraints for better compile-time checks
+- Provide clear type definitions for complex binding scenarios
+- Test TypeScript compilation in CI/CD pipeline
+
+#### Performance Considerations
+- Container operations should be fast for user-facing scenarios
+- Binding configuration is typically done at startup, so optimization focus is on resolution
+- Use core caching mechanisms effectively
+- Monitor memory usage for long-running applications
+
+#### Plugin Compatibility
+- Ensure new features work with existing plugins
+- Test plugin combinations thoroughly
+- Provide migration guides for breaking changes
+- Document plugin interaction patterns
+
+#### User Migration
+- Maintain backward compatibility where possible
+- Provide clear migration guides for breaking changes
+- Support gradual migration patterns
+- Test with real-world applications before releases
diff --git a/packages/container/libraries/core/AGENTS.md b/packages/container/libraries/core/AGENTS.md
@@ -0,0 +1,140 @@
+# AGENTS.md - @inversifyjs/core
+
+## Package Overview
+
+The `@inversifyjs/core` package is the foundational layer of the InversifyJS dependency injection system. It contains the core planning algorithms, resolution logic, and fundamental architecture patterns that power the entire container ecosystem.
+
+## Key Responsibilities
+
+- **Planning Phase**: Builds execution plans for dependency resolution
+- **Resolution Logic**: Core algorithms for creating and injecting dependencies  
+- **Metadata Management**: Handles reflection metadata and binding information
+- **Error Handling**: Provides detailed error reporting with context
+- **Symbol Management**: Manages service identifiers and injection tokens
+
+## Architecture Patterns
+
+### Planning Phase
+The core implements a two-phase resolution strategy:
+
+1. **Plan Creation**: Analyzes dependency graph and creates execution plan
+2. **Plan Execution**: Executes the plan to create actual instances
+
+This separation enables:
+- **Caching**: Plans can be cached for performance
+- **Validation**: Dependencies can be validated before execution
+- **Debugging**: Clear separation of concerns for troubleshooting
+
+### Resolution Phase  
+The resolution system follows these patterns:
+
+- **Request/Context Pattern**: Each resolution maintains context state
+- **Factory Pattern**: Different activation strategies for different binding types
+- **Chain of Responsibility**: Multiple resolvers handle different scenarios
+
+### Error Reporting
+Core provides comprehensive error reporting:
+- **Service Identifier Context**: Errors include which service failed
+- **Binding Information**: Details about how services are bound
+- **Resolution Stack**: Shows the dependency chain that led to errors
+
+## Working with Core
+
+### Key Characteristics
+- **Performance Critical**: Operations happen frequently at runtime
+- **Type Safety**: Heavy use of TypeScript generics and constraints  
+- **Immutable Patterns**: Core data structures are immutable where possible
+- **Comprehensive Testing**: Requires extensive unit and integration tests
+
+### Testing Strategy
+
+#### Unit Testing Requirements
+Follow the [four-layer testing structure](../../../../docs/testing/unit-testing.md):
+
+1. **Class Scope**: Test each planner, resolver, and metadata handler
+2. **Method Scope**: Test each public method thoroughly
+3. **Input Scope**: Test various dependency configurations
+4. **Flow Scope**: Test different resolution paths and error conditions
+
+#### Critical Test Areas
+- **Planning Algorithm**: Test plan generation for complex dependency graphs
+- **Resolution Logic**: Test actual object creation and injection
+- **Error Scenarios**: Test circular dependencies, missing bindings, etc.
+- **Performance**: Test plan caching and resolution performance
+- **Metadata Handling**: Test reflection metadata processing
+
+### Development Guidelines
+
+#### Performance Considerations
+- **Hot Path Optimization**: Resolution happens frequently - optimize for speed
+- **Memory Management**: Minimize allocations in planning and resolution
+- **Plan Caching**: Ensure plans are properly cached and invalidated
+- **Object Pooling**: Consider pooling for frequently created objects
+
+#### Type Safety Patterns
+- **Generic Constraints**: Use TypeScript constraints to enforce correct usage
+- **Branded Types**: Use branded types for service identifiers
+- **Mapped Types**: Leverage mapped types for complex binding scenarios
+- **Conditional Types**: Use conditional types for resolution logic
+
+#### Error Handling Best Practices
+- **Contextual Errors**: Include service identifiers and binding info
+- **User-Friendly Messages**: Provide clear guidance on how to fix issues
+- **Error Recovery**: Where possible, provide suggestions for resolution
+- **Stack Preservation**: Maintain error stacks for debugging
+
+### Build and Test Commands
+
+```bash
+# Build the package
+pnpm run build
+
+# Run all tests
+pnpm run test
+
+# Run only unit tests
+pnpm run test:unit
+
+# Run only integration tests
+pnpm run test:integration
+
+# Generate coverage report
+pnpm run test:coverage
+```
+
+### Common Development Tasks
+
+#### Adding New Planning Logic
+1. **Design the Algorithm**: Consider performance and correctness
+2. **Implement the Planner**: Add to the planning module
+3. **Add Comprehensive Tests**: Test all edge cases and performance
+4. **Update Integration Tests**: Ensure it works with the full container
+5. **Benchmark Performance**: Verify no performance regressions
+
+#### Extending Resolution Strategies
+1. **Define the Strategy Interface**: Add to resolution types
+2. **Implement the Resolver**: Add resolution logic
+3. **Update the Factory**: Integrate with the resolution factory
+4. **Test Thoroughly**: Unit tests, integration tests, error scenarios
+5. **Document Usage**: Update documentation and examples
+
+#### Optimizing Performance
+1. **Profile Current Performance**: Use container benchmarks
+2. **Identify Bottlenecks**: Focus on hot paths in planning/resolution
+3. **Implement Optimizations**: Make targeted improvements
+4. **Verify Improvements**: Re-run benchmarks to confirm gains
+5. **Test Correctness**: Ensure optimizations don't break functionality
+
+### Important Notes
+
+#### Breaking Changes
+- Core changes affect the entire container ecosystem
+- Coordinate with all consuming packages before making changes
+- Provide migration guides for major API changes
+- Test with real-world applications
+
+#### Debugging Guidelines
+- Use the planning system to understand resolution flow
+- Check binding metadata and constraints
+- Verify service identifier resolution
+- Use comprehensive error messages for troubleshooting
diff --git a/packages/container/libraries/plugin-dispose/AGENTS.md b/packages/container/libraries/plugin-dispose/AGENTS.md
@@ -0,0 +1,136 @@
+# AGENTS.md - @inversifyjs/plugin-dispose
+
+## Package Overview
+
+The `@inversifyjs/plugin-dispose` package provides automatic resource disposal and cleanup functionality for InversifyJS containers. It implements the plugin interface to add lifecycle management capabilities, ensuring that resources are properly disposed of when containers are torn down or services are no longer needed.
+
+## Key Responsibilities
+
+- **Resource Disposal**: Automatic cleanup of disposable resources
+- **Lifecycle Management**: Tracks service lifecycle for proper disposal timing
+- **Plugin Implementation**: Implements the plugin interface for container integration
+- **Disposal Patterns**: Supports various disposal patterns (IDisposable, async disposal, etc.)
+- **Memory Management**: Prevents memory leaks through proper resource cleanup
+
+## Working with Plugin Dispose
+
+### Key Characteristics
+- **Plugin Implementation**: Implements `@inversifyjs/plugin` interface
+- **Resource Management**: Focus on memory and resource cleanup
+- **Lifecycle Aware**: Understands container and service lifecycles
+- **Error Resilient**: Handles disposal errors gracefully
+- **Comprehensive Testing**: Requires thorough testing of disposal scenarios
+
+### Testing Strategy
+
+#### Unit Testing Requirements
+Follow the [structured testing approach](../../../../docs/testing/unit-testing.md):
+
+1. **Class Scope**: Test disposal plugin and disposal tracking classes
+2. **Method Scope**: Test disposal methods and lifecycle hooks
+3. **Input Scope**: Test various disposable resource types and scenarios
+4. **Flow Scope**: Test different disposal timing and error conditions
+
+#### Critical Test Areas
+- **Disposal Execution**: Test that disposable resources are actually disposed
+- **Lifecycle Integration**: Test proper integration with container lifecycle
+- **Error Handling**: Test disposal error scenarios and recovery
+- **Memory Leaks**: Test that disposal prevents memory leaks
+- **Plugin Composition**: Test interaction with other plugins
+- **Async Disposal**: Test asynchronous disposal patterns
+
+### Development Guidelines
+
+#### Disposal Patterns
+- **IDisposable Interface**: Support standard disposable patterns
+- **Async Disposal**: Handle asynchronous cleanup operations
+- **Disposal Ordering**: Ensure proper disposal order for dependent resources
+- **Error Isolation**: Prevent one disposal failure from affecting others
+- **Resource Tracking**: Track disposable resources throughout their lifecycle
+
+#### Error Handling Strategies
+- **Graceful Degradation**: Continue operation even if some disposals fail
+- **Error Logging**: Log disposal errors for debugging
+- **Timeout Handling**: Handle slow or hanging disposal operations
+- **Recovery Mechanisms**: Provide fallback disposal strategies
+
+#### Performance Considerations
+- **Minimal Overhead**: Don't slow down non-disposable service resolution
+- **Efficient Tracking**: Use efficient data structures for tracking disposables
+- **Batch Disposal**: Optimize disposal of multiple resources
+- **Memory Usage**: Minimize memory overhead of disposal tracking
+
+### Build and Test Commands
+
+```bash
+# Build the package
+pnpm run build
+
+# Run all tests
+pnpm run test
+
+# Run only unit tests
+pnpm run test:unit
+
+# Run only integration tests
+pnpm run test:integration
+
+# Generate coverage report
+pnpm run test:coverage
+```
+
+### Common Development Tasks
+
+#### Adding New Disposal Patterns
+1. **Identify Pattern**: Understand the new disposal pattern requirements
+2. **Design Strategy**: Create disposal strategy for the pattern
+3. **Implement Handler**: Add disposal logic for the pattern
+4. **Add Type Support**: Ensure TypeScript support for the pattern
+5. **Write Tests**: Comprehensive tests for the new pattern
+6. **Update Documentation**: Document usage and best practices
+
+#### Improving Error Handling
+1. **Analyze Failure Modes**: Understand how disposals can fail
+2. **Design Recovery**: Create strategies for handling failures
+3. **Implement Fallbacks**: Add fallback disposal mechanisms
+4. **Add Logging**: Improve error reporting and debugging
+5. **Test Scenarios**: Test various error conditions thoroughly
+
+#### Optimizing Performance
+1. **Profile Disposal**: Identify performance bottlenecks in disposal
+2. **Optimize Tracking**: Improve efficiency of disposable tracking
+3. **Batch Operations**: Optimize disposal of multiple resources
+4. **Reduce Overhead**: Minimize impact on non-disposable services
+5. **Benchmark Results**: Verify performance improvements
+
+### Important Notes
+
+#### Memory Management
+- **Weak References**: Use WeakMap for tracking to avoid memory leaks
+- **Cleanup Timing**: Dispose resources at appropriate lifecycle points
+- **Circular References**: Handle circular references in disposable objects
+- **Resource Monitoring**: Monitor for resource leaks in testing
+
+#### Plugin Integration
+- **Hook Priority**: Ensure disposal hooks run at the right time
+- **Plugin Ordering**: Consider order dependencies with other plugins
+- **State Management**: Maintain plugin state correctly across lifecycle
+- **Configuration**: Provide configurable disposal behaviors
+
+#### Error Handling
+- **Disposal Failures**: Handle individual disposal failures gracefully
+- **Timeout Management**: Prevent hanging on slow disposal operations
+- **Error Reporting**: Provide useful error information for debugging
+- **Recovery Strategies**: Implement fallback disposal mechanisms
+
+#### Testing Considerations
+- **Memory Leak Testing**: Verify that disposal prevents memory leaks
+- **Async Testing**: Test asynchronous disposal patterns thoroughly
+- **Error Scenarios**: Test various disposal failure conditions
+- **Integration Testing**: Test with real resources and containers
+
+#### Performance Impact
+- **Tracking Overhead**: Minimize overhead of tracking disposables
+- **Disposal Speed**: Optimize disposal operations for performance
+- **Memory Usage**: Keep disposal tracking memory usage minimal
+- **Batch Efficiency**: Optimize batch disposal operations
diff --git a/packages/container/libraries/plugin/AGENTS.md b/packages/container/libraries/plugin/AGENTS.md
@@ -0,0 +1,196 @@
+# AGENTS.md - @inversifyjs/plugin
+
+## Package Overview
+
+The `@inversifyjs/plugin` package provides the plugin system interface and base functionality for extending InversifyJS containers. It defines the plugin architecture that allows developers to add custom functionality to the container lifecycle without modifying core container code.
+
+## Key Responsibilities
+
+- **Plugin Interface**: Defines the contract that all plugins must implement
+- **Plugin Lifecycle**: Manages plugin activation, execution, and deactivation
+- **Hook System**: Provides extension points throughout container operations
+- **Plugin Composition**: Enables multiple plugins to work together seamlessly
+- **Base Implementations**: Common plugin patterns and utilities
+
+## Working with Plugin System
+
+### Key Characteristics
+- **Interface-Only Package**: Primarily provides interfaces and type definitions
+- **No Tests**: This package typically has no test files since it's interface-only
+- **Minimal Dependencies**: Only depends on core for basic types
+- **Extension Point**: Other packages implement the actual plugin functionality
+- **Type-Heavy**: Extensive use of TypeScript for plugin contracts
+
+### Plugin Architecture
+
+#### Plugin Interface
+```typescript
+interface Plugin {
+  name: string;
+  version: string;
+  activate(context: PluginContext): void | Promise<void>;
+  deactivate?(context: PluginContext): void | Promise<void>;
+}
+```
+
+#### Hook System
+Plugins can hook into various container lifecycle events:
+- **beforeBinding**: Before a service is bound to the container
+- **afterBinding**: After a service is bound to the container
+- **beforeResolution**: Before a service is resolved
+- **afterResolution**: After a service is resolved
+- **onError**: When an error occurs during container operations
+
+#### Plugin Context
+Provides plugins with access to:
+- Container instance
+- Current operation context
+- Plugin configuration
+- Inter-plugin communication
+
+### Development Guidelines
+
+#### Plugin Interface Design
+- **Clear Contracts**: Plugin interfaces should be well-defined and documented
+- **Async Support**: Support both synchronous and asynchronous plugin operations
+- **Error Handling**: Define how plugin errors should be handled
+- **Lifecycle Management**: Clear activation and deactivation patterns
+- **Version Compatibility**: Support for plugin version checking
+
+#### Type Safety Patterns
+- **Generic Plugin Types**: Use generics for type-safe plugin configuration
+- **Hook Type Safety**: Ensure hook parameters are properly typed
+- **Plugin Metadata**: Type-safe plugin metadata and configuration
+- **Context Types**: Strong typing for plugin execution context
+
+#### Performance Considerations
+- **Lazy Loading**: Plugins should only be loaded when needed
+- **Hook Overhead**: Minimize performance impact of hook system
+- **Plugin Isolation**: Prevent one plugin from affecting others' performance
+- **Caching**: Support caching of plugin results where appropriate
+
+### Build Commands
+
+```bash
+# Build the package (interfaces only)
+pnpm run build
+
+# Format code
+pnpm run format
+
+# Lint code
+pnpm run lint
+```
+
+Note: This package typically does not have tests since it primarily provides interfaces.
+
+### Plugin Development Examples
+
+#### Basic Plugin Implementation
+```typescript
+import { Plugin, PluginContext } from '@inversifyjs/plugin';
+
+export class LoggingPlugin implements Plugin {
+  public readonly name = 'LoggingPlugin';
+  public readonly version = '1.0.0';
+
+  public activate(context: PluginContext): void {
+    context.container.onResolution((binding, resolved) => {
+      console.log(`Resolved ${binding.serviceIdentifier} -> ${resolved}`);
+    });
+  }
+
+  public deactivate?(context: PluginContext): void {
+    // Cleanup logging hooks
+  }
+}
+```
+
+#### Advanced Plugin with Hooks
+```typescript
+export class MetricsPlugin implements Plugin {
+  public readonly name = 'MetricsPlugin';
+  public readonly version = '2.1.0';
+
+  private metrics: MetricsCollector;
+
+  public activate(context: PluginContext): void {
+    this.metrics = new MetricsCollector();
+
+    context.hooks.beforeResolution.tap('MetricsPlugin', (request) => {
+      this.metrics.startTimer(request.serviceIdentifier);
+    });
+
+    context.hooks.afterResolution.tap('MetricsPlugin', (request, result) => {
+      this.metrics.endTimer(request.serviceIdentifier);
+      this.metrics.recordResolution(request.serviceIdentifier, result);
+    });
+
+    context.hooks.onError.tap('MetricsPlugin', (error) => {
+      this.metrics.recordError(error);
+    });
+  }
+}
+```
+
+### Common Development Tasks
+
+#### Defining New Plugin Interfaces
+1. **Analyze Requirements**: Understand what functionality needs to be pluggable
+2. **Design Interface**: Create clear, focused plugin interfaces
+3. **Define Hooks**: Identify extension points where plugins can inject behavior
+4. **Add Type Definitions**: Ensure proper TypeScript support
+5. **Document Usage**: Provide clear examples and best practices
+
+#### Adding New Hook Points
+1. **Identify Extension Need**: Determine where new extension points are needed
+2. **Design Hook Interface**: Create consistent hook signatures
+3. **Update Plugin Context**: Add new hooks to plugin context
+4. **Version Compatibility**: Ensure backward compatibility
+5. **Update Documentation**: Document new extension capabilities
+
+#### Evolving Plugin Architecture
+1. **Gather Feedback**: Understand pain points in current plugin system
+2. **Design Improvements**: Create better abstractions and patterns
+3. **Maintain Compatibility**: Ensure existing plugins continue to work
+4. **Migration Support**: Provide clear migration paths
+5. **Performance Testing**: Verify improvements don't degrade performance
+
+### Important Notes
+
+#### Interface-Only Nature
+- This package primarily provides TypeScript interfaces and type definitions
+- Actual plugin functionality is implemented in consuming packages
+- No runtime logic or business functionality should be in this package
+- Focus on clear, well-documented contracts
+
+#### Version Compatibility
+- Plugin interface changes can break existing plugins
+- Use semantic versioning carefully for interface changes
+- Provide deprecation warnings for interface changes
+- Support multiple interface versions when possible
+
+#### Performance Impact
+- Plugin system should have minimal overhead when no plugins are loaded
+- Hook execution should be optimized for common cases
+- Plugin registration and management should be efficient
+- Consider lazy loading and caching strategies
+
+#### Plugin Ecosystem
+- Design interfaces to encourage a healthy plugin ecosystem
+- Provide examples and templates for common plugin patterns
+- Document best practices for plugin development
+- Consider plugin discovery and registry mechanisms
+
+#### Testing Strategy
+Since this is an interface-only package:
+- Focus on TypeScript compilation tests
+- Test interface compatibility across versions
+- Provide reference implementations for testing
+- Document testing patterns for plugin implementers
+
+#### Future Evolution
+- Consider standardization with other DI frameworks
+- Plan for potential decorator-based plugin registration
+- Think about plugin composition and dependency management
+- Consider runtime plugin loading and hot reloading capabilities
diff --git a/packages/container/libraries/strongly-typed/AGENTS.md b/packages/container/libraries/strongly-typed/AGENTS.md
@@ -0,0 +1,241 @@
+# AGENTS.md - @inversifyjs/strongly-typed
+
+## Package Overview
+
+The `@inversifyjs/strongly-typed` package provides enhanced type safety and compile-time guarantees for InversifyJS containers. It leverages advanced TypeScript features to ensure that dependency injection is type-safe, reducing runtime errors and improving the developer experience.
+
+## Key Responsibilities
+
+- **Type Safety**: Compile-time type checking for container operations
+- **Strong Typing Utilities**: Advanced TypeScript patterns for DI
+- **Type-Safe Service Identifiers**: Branded types and symbols for services
+- **Container Type Extensions**: Enhanced typing for container methods
+- **Inference Helpers**: Utilities to improve TypeScript type inference
+
+## Working with Strong Typing
+
+### Key Characteristics
+- **Type-Only Package**: Primarily provides type definitions and utilities
+- **Peer Dependency**: Works with inversify as a peer dependency
+- **Advanced TypeScript**: Uses cutting-edge TypeScript features
+- **Zero Runtime**: No runtime dependencies or code
+- **Compilation-Heavy**: Focuses on TypeScript compilation and type checking
+
+### Testing Strategy
+
+#### Type Testing Requirements
+Since this is a type-focused package, testing emphasizes TypeScript compilation:
+
+1. **Type Tests** (`*.spec-d.ts`): Test TypeScript type checking with `tsd` or similar
+2. **Compilation Tests**: Verify that expected patterns compile correctly
+3. **Error Tests**: Verify that incorrect usage produces compilation errors
+4. **Inference Tests**: Test that TypeScript correctly infers types
+
+#### Critical Test Areas
+- **Service Identifier Types**: Test that service identifiers are properly typed
+- **Container Method Types**: Test type safety of get(), bind(), etc.
+- **Generic Constraints**: Test that generic constraints work correctly
+- **Type Inference**: Test that TypeScript can infer types properly
+- **Error Scenarios**: Test that type errors are caught at compile time
+
+### Development Guidelines
+
+#### TypeScript Best Practices
+- **Latest Features**: Use cutting-edge TypeScript features for better types
+- **Generic Constraints**: Proper use of generic constraints for type safety
+- **Mapped Types**: Leverage mapped types for complex transformations
+- **Conditional Types**: Use conditional types for type-level logic
+- **Template Literal Types**: Use for string manipulation at type level
+
+#### Type Safety Patterns
+- **Branded Types**: Use branded types to prevent type confusion
+- **Phantom Types**: Use phantom types for additional type information
+- **Type Guards**: Provide type guard functions where useful
+- **Assertion Functions**: Use assertion functions for runtime type checking
+- **Const Assertions**: Leverage const assertions for literal types
+
+#### API Design
+- **Intuitive Types**: Types should feel natural to TypeScript developers
+- **Error Messages**: Provide helpful error messages for type mismatches
+- **IntelliSense**: Optimize for excellent IDE support and autocomplete
+- **Backwards Compatibility**: Maintain type compatibility across versions
+
+### Build and Test Commands
+
+```bash
+# Build the package
+pnpm run build
+
+# Run type tests
+pnpm run test
+
+# Run only unit tests (if any)
+pnpm run test:unit
+
+# Run only integration tests
+pnpm run test:integration
+
+# Generate coverage report
+pnpm run test:coverage
+
+# Format code
+pnpm run format
+
+# Lint code  
+pnpm run lint
+```
+
+### Strong Typing Examples
+
+#### Type-Safe Service Identifiers
+```typescript
+import { ServiceIdentifier, Container } from '@inversifyjs/strongly-typed';
+
+// Branded service identifier
+const USER_SERVICE = Symbol('UserService') as ServiceIdentifier<UserService>;
+const LOGGER = Symbol('Logger') as ServiceIdentifier<Logger>;
+
+const container = new Container();
+
+// Type-safe binding
+container.bind(USER_SERVICE).to(UserServiceImpl);
+container.bind(LOGGER).toConstant(new ConsoleLogger());
+
+// Type-safe resolution - TypeScript knows the return type
+const userService: UserService = container.get(USER_SERVICE);
+const logger: Logger = container.get(LOGGER);
+```
+
+#### Advanced Type Constraints
+```typescript
+// Generic constraints for type safety
+interface Repository<T> {
+  save(entity: T): Promise<void>;
+  findById(id: string): Promise<T | null>;
+}
+
+// Type-safe repository binding
+function bindRepository<T>(
+  container: Container,
+  identifier: ServiceIdentifier<Repository<T>>,
+  implementation: Constructor<Repository<T>>
+): void {
+  container.bind(identifier).to(implementation);
+}
+
+// Usage with compile-time type checking
+bindRepository(container, USER_REPOSITORY, UserRepository);
+bindRepository(container, PRODUCT_REPOSITORY, ProductRepository);
+```
+
+#### Type-Safe Factory Patterns
+```typescript
+// Strongly typed factory
+type Factory<T, TArgs extends readonly unknown[] = []> = (...args: TArgs) => T;
+
+// Type-safe factory binding
+container.bind<Factory<Database, [string]>>('DatabaseFactory')
+  .toFactory<Database, [string]>((context) => {
+    return (connectionString: string) => {
+      return new Database(connectionString);
+    };
+  });
+
+// Type-safe factory usage
+const dbFactory = container.get<Factory<Database, [string]>>('DatabaseFactory');
+const db: Database = dbFactory('connection-string'); // TypeScript knows the type
+```
+
+### Common Development Tasks
+
+#### Adding New Type Utilities
+1. **Identify Type Needs**: Understand what type utilities are needed
+2. **Design Type Logic**: Create TypeScript type-level logic
+3. **Implement Types**: Write advanced TypeScript type definitions
+4. **Add Type Tests**: Test compilation and type inference
+5. **Document Usage**: Provide clear examples and documentation
+
+#### Enhancing Type Safety
+1. **Analyze Weak Points**: Find areas where type safety could improve
+2. **Design Better Types**: Create more restrictive and helpful types
+3. **Implement Constraints**: Add generic constraints and type guards
+4. **Test Type Checking**: Verify that errors are caught at compile time
+5. **Benchmark Compilation**: Ensure types don't slow compilation too much
+
+#### Improving Developer Experience
+1. **Analyze IDE Support**: Test IntelliSense and autocomplete behavior
+2. **Optimize Type Definitions**: Improve type inference and suggestions
+3. **Add Helper Types**: Create utilities that make common patterns easier
+4. **Enhance Error Messages**: Improve TypeScript error messages
+5. **Create Examples**: Provide comprehensive usage examples
+
+### Important Patterns
+
+#### Branded Service Identifiers
+```typescript
+// Branded type for service identifiers
+export type ServiceIdentifier<T> = symbol & { readonly __serviceType: T };
+
+// Helper to create branded identifiers
+export function createServiceIdentifier<T>(description?: string): ServiceIdentifier<T> {
+  return Symbol(description) as ServiceIdentifier<T>;
+}
+
+// Usage
+const USER_SERVICE = createServiceIdentifier<UserService>('UserService');
+```
+
+#### Type-Safe Container Extensions
+```typescript
+// Enhanced container with better typing
+export interface StronglyTypedContainer {
+  bind<T>(serviceIdentifier: ServiceIdentifier<T>): BindingToSyntax<T>;
+  get<T>(serviceIdentifier: ServiceIdentifier<T>): T;
+  getAll<T>(serviceIdentifier: ServiceIdentifier<T>): T[];
+  resolve<T>(constructorFunction: Constructor<T>): T;
+}
+```
+
+#### Advanced Generic Constraints
+```typescript
+// Type constraints for dependency injection
+export type Injectable<T = {}> = Constructor<T> | Factory<T>;
+export type Constructor<T = {}> = new (...args: any[]) => T;
+export type Factory<T = {}> = (...args: any[]) => T;
+
+// Constraint for bindable types
+export type Bindable<T> = Injectable<T> | T | Promise<T>;
+```
+
+### Important Notes
+
+#### TypeScript Version Requirements
+- **Minimum Version**: Requires recent TypeScript version for advanced features
+- **Feature Dependencies**: Uses conditional types, mapped types, template literals
+- **Compilation Target**: May require specific TypeScript compilation settings
+- **IDE Support**: Best experience with VS Code and TypeScript extensions
+
+#### Performance Considerations
+- **Compilation Speed**: Complex types can slow TypeScript compilation
+- **Type Checking**: Extensive type checking may increase build times
+- **Memory Usage**: Complex type operations can use significant memory
+- **Bundle Size**: Should have zero impact on runtime bundle size
+
+#### Compatibility
+- **InversifyJS Versions**: Maintain compatibility with target inversify versions
+- **TypeScript Evolution**: Adapt to new TypeScript features and changes
+- **Breaking Changes**: Type changes can break consuming code
+- **Migration Support**: Provide type migration guides for major changes
+
+#### Common Pitfalls
+- **Over-Engineering**: Avoid overly complex types that hurt usability
+- **Type Performance**: Monitor TypeScript compilation performance
+- **Error Messages**: Ensure type errors are understandable
+- **Learning Curve**: Advanced types can be intimidating for new users
+
+#### Testing Strategy
+- **Type-Only Tests**: Use tools like `tsd` for type testing
+- **Compilation Tests**: Verify expected code compiles correctly
+- **Error Tests**: Verify incorrect code produces compilation errors
+- **Integration Tests**: Test with real-world usage patterns
+- **Performance Tests**: Monitor TypeScript compilation performance
diff --git a/packages/docs/tools/AGENTS.md b/packages/docs/tools/AGENTS.md
@@ -0,0 +1,83 @@
+# AGENTS.md - Documentation Code Examples
+
+## Package Overview
+
+This directory contains code examples and tools for generating documentation examples. These packages demonstrate usage patterns for the InversifyJS ecosystem but **do not export library code**.
+
+## Working with Code Example Packages
+
+### Key Characteristics
+- **Integration tests only** - examples are tested to ensure they work
+- **No unit tests** - the code demonstrates usage, not library implementation
+- **Generated output** - many examples generate documentation files
+- **Multiple InversifyJS versions** - some packages test against v6 and v7
+
+### Test Strategy
+```bash
+# Run integration tests to verify examples work
+pnpm run test:integration
+
+# Examples should demonstrate real-world usage
+pnpm run test  # Runs integration tests by default
+```
+
+### Development Guidelines
+
+#### Creating New Examples
+1. **Focus on real-world scenarios** - examples should solve actual problems
+2. **Keep examples simple** - one concept per example
+3. **Add integration tests** - ensure examples actually work
+4. **Document clearly** - examples serve as documentation
+
+#### Testing Examples
+- Use `.int.spec.ts` suffix for integration tests
+- Test the **outcome** of the example, not implementation details
+- Examples should be **executable and demonstrable**
+
+### Build Process
+
+#### Code Generation
+Many packages generate documentation files:
+```bash
+# Build and generate examples
+pnpm run build
+
+# Just generate examples (after build)
+pnpm run generate:examples
+```
+
+#### Dependencies
+- **Multiple InversifyJS versions**: Some packages depend on both `inversify@6.x` and `inversify7@7.x`
+- **Example-specific deps**: Dependencies needed for demonstration purposes
+- **Generation tools**: Build tools for creating documentation
+
+### Common Tasks
+
+#### Adding a New Example
+1. Create example file in appropriate version directory
+2. Add corresponding `.int.spec.ts` test file
+3. Verify example works: `pnpm run test:integration`
+4. Update generation scripts if needed
+
+#### Updating for New InversifyJS Version
+1. Add new version directory (e.g., `v8/`)
+2. Port relevant examples from previous version
+3. Update dependencies in `package.json`
+4. Verify all examples work with new version
+
+### Important Notes
+
+#### No Unit Tests
+- These packages **do not need unit tests**
+- Integration tests verify examples work correctly
+- Focus on demonstrating proper usage patterns
+
+#### Multiple Dependency Versions
+- Some packages test against multiple InversifyJS versions
+- Use package aliases (e.g., `"inversify7": "npm:inversify@7.9.1"`)
+- Organize examples by version in separate directories
+
+#### Generated Content
+- Many packages generate files in `generated/` directory
+- These files are typically committed to show output
+- Build process should be reproducible and deterministic
diff --git a/packages/foundation/tools/AGENTS.md b/packages/foundation/tools/AGENTS.md
@@ -0,0 +1,78 @@
+# AGENTS.md - Foundation Tools
+
+## Package Overview
+
+This directory contains shared foundation tooling packages that provide common configurations for ESLint, Prettier, TypeScript, Rollup, Vitest, and Stryker across the entire monorepo.
+
+## Package Types
+
+### Configuration Packages
+- **eslint-config**: Shared ESLint configuration
+- **prettier-config**: Shared Prettier configuration  
+- **typescript-config**: Shared TypeScript configurations
+- **rollup-config**: Shared Rollup build configuration
+- **vitest-config**: Shared Vitest test configuration
+- **stryker-config**: Shared Stryker mutation testing configuration
+
+### Utility Packages
+- **scripts**: Common build and utility scripts
+
+## Working with Foundation Packages
+
+### Key Characteristics
+- These packages provide **configuration only** - no runtime code
+- No unit tests required (configuration packages)
+- Changes affect the entire monorepo
+- Use `exports` field to expose configuration files
+
+### Development Guidelines
+
+#### Making Configuration Changes
+```bash
+# Test configuration changes across multiple packages
+pnpm run --filter="@inversifyjs/framework-*" lint
+pnpm run --filter="@inversifyjs/container-*" test
+
+# Verify builds work with new configs
+pnpm run build
+```
+
+#### Testing Configuration Impact
+1. **ESLint changes**: Run `pnpm run lint` across affected packages
+2. **TypeScript changes**: Run `pnpm run build` to verify compilation
+3. **Vitest changes**: Run `pnpm run test` to verify test execution
+4. **Prettier changes**: Run `pnpm run format` to verify formatting
+
+### Common Tasks
+
+#### Adding New ESLint Rules
+1. Update `packages/foundation/tools/eslint-config/index.js`
+2. Test with: `pnpm run --filter="*" lint`
+3. Fix any violations before committing
+
+#### Updating TypeScript Configuration
+1. Modify base configs in `typescript-config/`
+2. Test compilation: `pnpm run build`
+3. Verify both CJS and ESM builds work
+
+#### Modifying Test Configuration
+1. Update `vitest-config/lib/index.js`
+2. Test across package types: `pnpm run test`
+3. Verify unit, integration, and type tests still work
+
+## Important Notes
+
+### Breaking Changes
+- Configuration changes can break builds across the entire monorepo
+- Always test thoroughly before committing
+- Consider backward compatibility when possible
+
+### Dependencies
+- Keep peer dependencies minimal and well-documented
+- Foundation packages should have minimal runtime dependencies
+- Use exact versions for critical build tools
+
+### No Testing Required
+- Configuration packages typically don't need unit tests
+- The "test" is whether they work correctly when consumed
+- Integration testing happens at the consuming package level
diff --git a/packages/framework/core/AGENTS.md b/packages/framework/core/AGENTS.md
@@ -0,0 +1,109 @@
+# AGENTS.md - Framework Core
+
+## Package Overview
+
+This is the InversifyJS framework core package that provides foundational framework functionality and utilities for building applications with dependency injection.
+
+## Testing Requirements
+
+This package requires **comprehensive unit testing** following the [testing guidelines](../../docs/testing/unit-testing.md).
+
+### Test Structure
+Follow the four-layer describe structure:
+1. **Class scope** - `describe(ClassName, () => ...)`
+2. **Method scope** - `describe('.methodName', () => ...)`  
+3. **Input scope** - `describe('having specific input', () => ...)`
+4. **Flow scope** - `describe('when called, and [condition]', () => ...)`
+
+### Testing Commands
+```bash
+# Run all tests
+pnpm run test
+
+# Run only unit tests
+pnpm run test:unit
+
+# Run only integration tests
+pnpm run test:integration
+
+# Run with coverage
+pnpm run test:coverage
+
+# Test uncommitted changes only
+pnpm run test:uncommitted
+```
+
+## Development Guidelines
+
+### Code Quality
+- **TypeScript strict mode** - all code must compile without errors
+- **ESLint compliance** - follow the shared ESLint configuration
+- **Prettier formatting** - code must be properly formatted
+- **Type safety** - avoid `any` type, use proper generics
+
+### Testing Requirements
+- **Unit tests required** for all public methods and classes
+- **Mock external dependencies** using `vitest.fn()` and `vitest.mock()`
+- **Create fixtures** for complex test data using fixture classes
+- **Test error conditions** and edge cases thoroughly
+
+### Build Process
+```bash
+
+# Build both CommonJS and ES modules
+pnpm run build
+
+# Format source code
+pnpm run format
+
+# Lint source code
+pnpm run lint
+```
+
+## Framework Architecture
+
+### Core Concepts
+- **Metadata handling** - framework uses reflection metadata
+- **Lifecycle management** - supports component initialization and cleanup
+- **Type safety** - provides type-safe APIs for dependency injection
+- **Framework utilities** - common patterns for framework development
+
+### Integration with Container
+- Framework core works with the InversifyJS container system
+- Provides higher-level abstractions over core container functionality
+- Enables framework-specific features like lifecycle management
+
+## Common Tasks
+
+### Adding New Framework Features
+1. **Design type-safe APIs** using TypeScript generics
+2. **Implement core functionality** with proper error handling
+3. **Write comprehensive unit tests** following testing guidelines
+4. **Add integration tests** for component interactions
+5. **Update documentation** and add usage examples
+
+### Performance Considerations
+- Framework core operations should be efficient
+- Minimize metadata reflection overhead
+- Cache computed values where appropriate
+- Profile performance-critical paths
+
+## Important Notes
+
+### Breaking Changes
+- Framework core changes affect all framework packages
+- Coordinate with HTTP framework and other dependent packages
+- Test thoroughly with real applications
+- Provide migration guides for major changes
+
+### Type Safety
+- Framework APIs should be strongly typed
+- Use generic constraints to enforce correct usage
+- Provide clear compilation errors for misuse
+- Avoid runtime type checking where compile-time checking suffices
+
+### Testing Excellence
+- Framework core requires **excellent test coverage**
+- Test both happy path and error conditions
+- Use fixture classes for reusable test data
+- Follow the documented testing patterns consistently
PATCH

echo "Gold patch applied."
