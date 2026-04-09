# Task: Add Global NUnit AssemblyFixture for Test Setup

## Problem

The Selenium .NET Support test project has duplicated setup and teardown code across multiple test classes. Currently, both `PopupWindowFinderTests` and `SelectBrowserTests` contain identical `[OneTimeSetUp]` and `[OneTimeTearDown]` methods that start and stop the test web server.

This duplication:
- Violates DRY principles
- Makes maintenance harder (changes needed in multiple places)
- Is inefficient (the TODO comment in PopupWindowFinderTests acknowledges this should be fixed)

## Goal

Refactor the test infrastructure to use NUnit's `[SetUpFixture]` mechanism for assembly-level setup/teardown, removing the duplicated code from individual test classes.

## What You Need to Do

### 1. Create AssemblyFixture.cs

Create a new file at `dotnet/test/support/AssemblyFixture.cs` with:
- `[SetUpFixture]` attribute on the class
- A public constructor
- `RunBeforeAnyTestAsync()` method with `[OneTimeSetUp]` that:
  - Sets the internal log level to Trace (`Internal.Logging.Log.SetLevel(Internal.Logging.LogEventLevel.Trace)`)
  - Starts the web server (`EnvironmentManager.Instance.WebServer.StartAsync()`)
  - Conditionally starts the remote server if using Browser.Remote
- `RunAfterAnyTestsAsync()` method with `[OneTimeTearDown]` that:
  - Closes the current driver (`EnvironmentManager.Instance.CloseCurrentDriver()`)
  - Stops the web server (`EnvironmentManager.Instance.WebServer.StopAsync()`)
  - Conditionally stops the remote server if using Browser.Remote

Use the `OpenQA.Selenium.Support` namespace and import:
- `System.Threading.Tasks`
- `NUnit.Framework`
- `OpenQA.Selenium.Environment`

### 2. Clean Up PopupWindowFinderTests

Edit `dotnet/test/support/UI/PopupWindowFinderTests.cs`:
- Remove the `[OneTimeSetUp]` and `[OneTimeTearDown]` methods
- Remove the `RunBeforeAnyTestAsync()` and `RunAfterAnyTestsAsync()` methods
- Remove unused `using System.Threading.Tasks;`
- Remove unused `using OpenQA.Selenium.Environment;`
- Remove the TODO comment about moving setup to a standalone class

### 3. Clean Up SelectBrowserTests

Edit `dotnet/test/support/UI/SelectBrowserTests.cs`:
- Remove the `[OneTimeSetUp]` and `[OneTimeTearDown]` methods
- Remove the `RunBeforeAnyTestAsync()` and `RunAfterAnyTestsAsync()` methods
- Remove unused `using System.Threading.Tasks;`
- Remove unused `using OpenQA.Selenium.Environment;`

## Files to Modify

1. **Create**: `dotnet/test/support/AssemblyFixture.cs` (new file)
2. **Edit**: `dotnet/test/support/UI/PopupWindowFinderTests.cs`
3. **Edit**: `dotnet/test/support/UI/SelectBrowserTests.cs`

## Notes

- This is a standard NUnit pattern for assembly-level test fixtures
- The `[SetUpFixture]` runs once before any tests in the assembly and once after all tests complete
- The change should be purely refactoring—no test behavior changes
- Follow the existing code style in the dotnet directory (XML documentation comments, proper async/await patterns)
