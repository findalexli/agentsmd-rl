# Task: Add Pluggable Command Interception to Selenium Grid Node

## Problem

The Selenium Grid Node currently executes WebDriver HTTP commands directly without any extension points for observing or wrapping command execution. This makes it difficult for third-party tools to implement features like:

- Trace recording for debugging
- Custom logging of command patterns
- Request/response transformation
- Performance monitoring

Users want to extend Grid behavior without forking the codebase or modifying the server itself. The `--ext` classpath mechanism exists for loading extensions, but there is no SPI (Service Provider Interface) for intercepting commands at the Node level.

## Requirements

### 1. Define a new SPI interface

Create an interface in the `org.openqa.selenium.grid.node` package that:

- Can be discovered via `ServiceLoader` (put the fully-qualified class name in `META-INF/services/`)
- Has a method to check if the interceptor is enabled based on configuration
- Has a lifecycle initialization method that receives the config and event bus
- Has an intercept method that receives the session ID, HTTP request, and a callable for the next handler
- Returns an `HttpResponse`
- Implements `java.io.Closeable` for resource cleanup on shutdown

### 2. Integrate with LocalNode

Modify the Node implementation so that:

- The Builder accepts interceptors through an `addInterceptor` method
- Interceptors are stored in a list field
- A method wraps command execution by calling each interceptor in order
- Interceptors are closed when the node shuts down
- The first interceptor added via the Builder becomes the outermost wrapper in the chain

### 3. Wire up ServiceLoader discovery

In the factory that creates Nodes:

- Use `ServiceLoader.load(...)` to discover interceptor implementations on the classpath
- Call `isEnabled(config)` on each discovered interceptor; only add enabled ones
- Call `initialize(config, eventBus)` on enabled interceptors during node startup

### 4. Update BUILD files

Ensure Bazel dependencies and service exports are configured so that:

- The interceptor interface is exported as a service implementation
- The node package depends on the events package

## Verification

The feature is complete when:

- The interceptor interface compiles and its methods can be called
- A single interceptor receives every WebDriver command executed through the node
- Multiple interceptors are invoked in the correct order (first added = outermost)
- The node compiles successfully with interceptors registered
- Existing node unit tests continue to pass