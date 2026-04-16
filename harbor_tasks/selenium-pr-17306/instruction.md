# Task: Enable External BiDi Module Extensibility

## Problem

The Selenium .NET WebDriver library's BiDi (WebDriver BiDi protocol) module system cannot be extended by external consumers. Users who want to create custom BiDi modules encounter compilation errors because key types in the BiDi command infrastructure and logging subsystem are inaccessible from outside the WebDriver assembly.

Related issue: SeleniumHQ/selenium#17306.

## Symptom Details

External developers attempting to build custom BiDi modules observe:

1. The `Command<TParameters, TResult>` class in `dotnet/src/webdriver/BiDi/Command.cs` cannot be inherited from by external code
2. The `Parameters` record in the same file cannot be referenced from external assemblies
3. The `ILogger` interface in `dotnet/src/webdriver/Internal/Logging/ILogger.cs` is not visible to external code
4. In `dotnet/src/webdriver/Internal/Logging/Log.cs`, the `CurrentContext` property and both `GetLogger` overloads (`GetLogger<T>()` and `GetLogger(Type type)`) are inaccessible from outside the assembly
5. In `dotnet/src/webdriver/Internal/Logging/ILogContext.cs`, the `GetLogger` methods on the `ILogContext` interface cannot be called from external code
6. The WebDriver project uses assembly-level attributes to grant its internal test project access to types that external consumers cannot access, which masks the accessibility issues during internal testing but does not help third-party developers

## Expected Outcome

After your fix:

1. External code can inherit from `Command<TParameters, TResult>` and reference `Parameters` to create custom BiDi commands
2. The `ILogger` interface, `ILogContext` interface, and the `Log` class members listed above are all usable from external assemblies
3. The WebDriver test project compiles and works without requiring any special assembly-level access permissions
4. All existing public APIs remain unchanged and backwards compatible
5. Modified files pass `dotnet format` whitespace and style checks in the `src/webdriver/BiDi/` and `src/webdriver/Internal/Logging/` directories

## Constraints

- Maintain backwards compatibility with existing public APIs
- Follow the existing code style and conventions
- Changes should be minimal and focused on enabling extensibility
