#!/usr/bin/env bash
set -euo pipefail

cd /workspace/hex1b

# Idempotency guard
if grep -qF "This skill captures API design preferences for the Hex1b codebase. Use it when r" ".github/skills/api-reviewer/SKILL.md" && grep -qF "**Problem**: Rendering is inherently async. Finding \"Header\" doesn't guarantee \"" ".github/skills/writing-unit-tests/SKILL.md" && grep -qF "This repository includes specialized skills in `.github/skills/` that provide de" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/api-reviewer/SKILL.md b/.github/skills/api-reviewer/SKILL.md
@@ -0,0 +1,435 @@
+---
+name: api-reviewer
+description: Guidelines for reviewing API design in the Hex1b codebase. Use when evaluating public APIs, reviewing accessibility modifiers, or assessing whether new APIs follow project conventions.
+---
+
+# API Reviewer Skill
+
+This skill captures API design preferences for the Hex1b codebase. Use it when reviewing public APIs, evaluating whether code should be public or internal, or assessing API design decisions made by AI agents.
+
+## Codebase Architecture
+
+Hex1b is structured into distinct layers, each with different API design considerations:
+
+### Layer 1: Hex1bTerminal (Core)
+
+The foundational layer maintaining an in-memory representation of terminal state.
+
+| Component | Purpose | Accessibility |
+|-----------|---------|---------------|
+| `Hex1bTerminal` | Core terminal state management | Public |
+| `Hex1bTerminalBuilder` | Fluent terminal construction | Public |
+| Presentation adapters | Output to real terminals, tests, web | Public interfaces |
+| Workload adapters | Input/output abstraction | Public interfaces |
+| `Surface`, `SurfaceCell` | Low-level cell storage | Public (low-level API) |
+
+**Design note**: Hex1bTerminal emerged from the need to properly test TUI components. The adapter pattern enables use in real terminals, unit tests, or projecting state across networks.
+
+### Layer 2: Hex1bApp/TUI
+
+The widget/node tree layer, inspired by React/Ink but not beholden to it.
+
+| Component | Purpose | Accessibility |
+|-----------|---------|---------------|
+| `Hex1bApp` | Root of TUI applications | Public |
+| `*Widget` records | Declarative UI configuration | Public |
+| `*Node` classes | DOM-like render elements | Generally public (for extensibility) |
+| Reconciliation logic | Widget→Node synchronization | Internal |
+| Layout algorithms | Measure/arrange implementation | Internal |
+
+### Layer 3: Automation
+
+Testing and automation infrastructure.
+
+| Component | Purpose | Accessibility |
+|-----------|---------|---------------|
+| `Hex1bTerminalInputSequenceBuilder` | Fluent input automation | Public |
+| `CellPatternSearcher` | Visual assertion matching | Public |
+| `Hex1bTerminalSnapshot` | Captured terminal state | Public |
+
+**Design note**: Automation APIs are explicitly for external consumers, not just internal testing.
+
+---
+
+## Public vs Internal Decision Framework
+
+When reviewing accessibility modifiers, apply this framework:
+
+### Make it PUBLIC when:
+
+1. **External consumers need it** - Adapters, extension points, widget customization
+2. **It's part of the conceptual API** - Users think in terms of this abstraction
+3. **It enables extensibility** - Custom widgets, themes, adapters
+4. **It's stable** - You're confident the design won't need breaking changes
+
+### Make it INTERNAL when:
+
+1. **It's implementation detail** - Only Hex1b itself (or agents working on it) would invoke it
+2. **The abstraction isn't proven** - Uncertain if this is the right level of abstraction
+3. **It could change** - Design may evolve with more usage
+4. **It exposes internals** - Would leak implementation details to consumers
+
+### Make it PRIVATE when:
+
+1. **Single class usage** - Only used within one type
+2. **Helper methods** - Implementation helpers with no external meaning
+
+### Review Questions
+
+When reviewing agent-generated code, ask:
+
+- [ ] Is this API an internal implementation detail?
+- [ ] Does this method/property make sense on this type?
+- [ ] Is the abstraction level right?
+- [ ] Would making this public lock us into a design we're not confident about?
+- [ ] Can this be internal for now until we're confident in the design?
+
+---
+
+## API Design Patterns
+
+### Builders: Classic `With...()` Pattern
+
+For `Hex1bTerminalBuilder` and similar construction scenarios:
+
+```csharp
+// ✅ PREFERRED: Classic builder pattern
+var terminal = Hex1bTerminal.CreateBuilder()
+    .WithWorkload(workload)
+    .WithPresentation(presentation)
+    .WithDimensions(80, 24)
+    .WithHeadless()
+    .Build();
+```
+
+### Widgets: SwiftUI-Inspired Minimal Constructors
+
+For widget APIs, use minimal constructors with essential arguments only, then fluent extension methods:
+
+```csharp
+// ✅ PREFERRED: Minimal constructor + fluent methods
+ctx.Table(columns, rows)
+   .SelectedRow(selectedIndex)
+   .OnSelectionChanged(HandleSelection)
+
+// ✅ PREFERRED: Cross-cutting concerns as extension methods
+ctx.Progress(value, max).Fill()
+
+// ❌ AVOID: Overloaded constructors with many parameters
+new TableWidget(columns, rows, selectedIndex, onSelectionChanged, sortColumn, sortDirection, ...)
+```
+
+**Guideline**: Only include the most essential arguments in the constructor. Make usage "bleeding obvious." Use extension methods to splice in extra behavior.
+
+### Options Types for Complex Configuration
+
+When you start creating many overloads, use an options type:
+
+```csharp
+// ✅ PREFERRED: Options type for complex configuration
+public class Hex1bAppOptions
+{
+    public Hex1bTheme? Theme { get; init; }
+    public IHex1bTerminalWorkloadAdapter? WorkloadAdapter { get; init; }
+    // ... extensible without breaking changes
+}
+
+// ❌ AVOID: Many overloads
+public Hex1bApp(Func<...> builder) { }
+public Hex1bApp(Func<...> builder, Hex1bTheme theme) { }
+public Hex1bApp(Func<...> builder, Hex1bTheme theme, IWorkloadAdapter adapter) { }
+```
+
+**But**: Don't have options classes everywhere. Be conservative with what you require.
+
+---
+
+## Async Patterns
+
+### Prefer Task, Use ValueTask for Performance
+
+```csharp
+// ✅ PREFERRED: Task as default
+public Task<Hex1bWidget> BuildAsync(WidgetContext ctx);
+
+// ✅ Use ValueTask when there's a performance reason (hot paths, avoiding allocations)
+public ValueTask HandleInputAsync(Hex1bKeyEvent key);
+```
+
+### Sync + Async Overloads for Callbacks
+
+Provide both sync and async overloads for event handlers. Implement everything assuming async is possible, then wrap sync handlers:
+
+```csharp
+// ✅ PREFERRED: Both overloads, sync wraps to async
+public ButtonWidget OnClick(Action<ButtonClickedEventArgs> handler)
+    => this with { ClickHandler = args => { handler(args); return Task.CompletedTask; } };
+
+public ButtonWidget OnClick(Func<ButtonClickedEventArgs, Task> handler)
+    => this with { ClickHandler = handler };
+```
+
+**Note**: Samples often favor sync versions for simplicity.
+
+---
+
+## Naming and Nullability
+
+### Types Over Magic Strings
+
+```csharp
+// ✅ PREFERRED: Strongly typed
+public void SetColor(Hex1bColor color);
+
+// ❌ AVOID: Magic strings
+public void SetColor(string colorName);
+```
+
+### Avoid Forcing Null Arguments
+
+```csharp
+// ❌ AVOID: Forcing callers to pass null
+public void Configure(string? requiredArg, string? optionalArg);
+Configure("value", null);  // Awkward
+
+// ✅ PREFERRED: Overloads or optional parameters
+public void Configure(string requiredArg);
+public void Configure(string requiredArg, string optionalArg);
+```
+
+### Avoid Primitive Obsession
+
+Be wary of using too many primitive types, as it makes creating overloads harder in the future:
+
+```csharp
+// Consider whether a type is warranted
+public void SetPosition(int x, int y);        // OK for simple cases
+public void SetPosition(Point position);       // Better if Point is meaningful elsewhere
+```
+
+---
+
+## Extension Methods
+
+Use extension methods when:
+
+1. **They don't need internal access** - Can work with public API surface
+2. **They represent cross-cutting concerns** - e.g., `.Fill()`, `.FixedWidth()`
+3. **They add optional behavior** - Not core to the type's identity
+
+Use instance methods when:
+
+1. **They need internal state** - Avoiding would leak implementation details
+2. **They're core to the type** - Essential behavior, not optional configuration
+
+---
+
+## Namespace Design
+
+### Discoverability First
+
+Minimize the namespaces developers need to know:
+
+```csharp
+// ✅ PREFERRED: Most types in root namespace
+using Hex1b;
+
+// Specialized namespaces for specific concerns
+using Hex1b.Theming;
+using Hex1b.Input;
+```
+
+**Guideline**: Ideally, most developers just need `using Hex1b;` and discover other types through methods on types in that namespace.
+
+---
+
+## Documentation Standards
+
+> **📘 See the `doc-writer` skill** for comprehensive documentation guidelines including XML API docs and end-user guides.
+
+### XML Documentation Requirements
+
+All public APIs must have XML documentation:
+
+```csharp
+/// <summary>
+/// Creates a button widget with the specified label.
+/// </summary>
+/// <remarks>
+/// Buttons are focusable widgets that respond to Enter key or click events.
+/// Use <see cref="OnClick"/> to register a handler for button activation.
+/// 
+/// Buttons automatically display a focus indicator when focused and can be
+/// styled using <see cref="ButtonTheme"/> elements.
+/// </remarks>
+/// <param name="label">The text displayed on the button.</param>
+/// <example>
+/// <description>A simple quit button that stops the application:</description>
+/// <code>
+/// using Hex1b;
+/// 
+/// await using var terminal = Hex1bTerminal.CreateBuilder()
+///     .WithHex1bApp((app, options) => ctx => 
+///         ctx.Button("Quit").OnClick(e => e.Context.RequestStop()))
+///     .Build();
+/// 
+/// await terminal.RunAsync();
+/// </code>
+/// </example>
+public sealed record ButtonWidget(string Label) : Hex1bWidget
+```
+
+### Documentation Guidelines
+
+| Element | Guideline |
+|---------|-----------|
+| `<summary>` | Concise and accurate - what it does, not how |
+| `<remarks>` | Detailed, useful from end-user perspective, no irrelevant internals |
+| `<param>` | Required for all parameters |
+| `<returns>` | Required for non-void methods |
+| `<example>` | Complete, runnable mini-apps when possible |
+| `<code>` | Cut-and-paste ready, not just method invocation |
+
+**Anti-pattern**: Examples that just show invoking the method without context. Always provide complete, runnable examples.
+
+---
+
+## Error Handling
+
+### Exceptions for Irrecoverable Errors
+
+Throw exceptions when something is truly irrecoverable:
+
+```csharp
+// ✅ Use existing exception types when they fit
+throw new ArgumentNullException(nameof(widget));
+throw new InvalidOperationException("Cannot render before Measure()");
+
+// ✅ Custom exceptions when debugging info is needed
+throw new Hex1bRenderException(widget, node, phase, "Render failed", innerException);
+```
+
+**Guideline**: Think about what information developers need to debug. Attach widget/node/phase information when it helps.
+
+**Note**: The `RescueWidget` exists to handle and display errors gracefully in the UI.
+
+---
+
+## Code Organization
+
+### One Type Per File
+
+Each type should be in its own file. This makes it easier to:
+- Review changes
+- Track modifications
+- Support concurrent agent work
+
+### Avoid Statics
+
+```csharp
+// ❌ AVOID: Static state (causes testability bugs)
+private static readonly Dictionary<string, Widget> _cache = new();
+
+// ✅ PREFERRED: Instance state
+private readonly Dictionary<string, Widget> _cache = new();
+```
+
+**Rationale**: AI agents tend to use statics, which introduce subtle testability bugs.
+
+### Constants Are Fine
+
+```csharp
+// ✅ OK: Constants
+public const int DefaultWidth = 80;
+public const int DefaultHeight = 24;
+```
+
+---
+
+## Review Checklist
+
+When reviewing APIs, check:
+
+### Accessibility
+- [ ] Is this the right accessibility level (public/internal/private)?
+- [ ] Are we exposing implementation details unnecessarily?
+- [ ] Is the API stable enough to be public?
+
+### Design
+- [ ] Does the method/property make sense on this type?
+- [ ] Is the abstraction level right?
+- [ ] Are we using options types where there are many parameters?
+- [ ] Are we avoiding primitive obsession?
+- [ ] Types over magic strings?
+
+### Patterns
+- [ ] Builders use `With...()` pattern?
+- [ ] Widgets use minimal constructors + fluent extensions?
+- [ ] Callbacks have sync + async overloads?
+- [ ] ValueTask preferred over Task?
+
+### Documentation
+- [ ] Summary is concise and accurate?
+- [ ] Remarks provide useful detail (not internal implementation)?
+- [ ] Examples are complete, runnable mini-apps?
+
+### Organization
+- [ ] One type per file?
+- [ ] Avoiding unnecessary statics?
+- [ ] Namespaces minimized for discoverability?
+
+---
+
+## Anti-Patterns to Flag
+
+### Overly Public Agent-Generated Code
+
+AI agents often make things public by default. Flag for review:
+
+```csharp
+// ❌ REVIEW: Should this be internal?
+public void ReconcileChildNodes(List<Hex1bNode> children) { }
+
+// ❌ REVIEW: Implementation detail exposed
+public int CalculateInternalLayoutOffset() { }
+```
+
+### Too Many Overloads
+
+When you see many overloads, suggest an options type:
+
+```csharp
+// ❌ REVIEW: Consider options type
+public Table(columns);
+public Table(columns, selectedRow);
+public Table(columns, selectedRow, sortColumn);
+public Table(columns, selectedRow, sortColumn, sortDirection);
+```
+
+### Magic Strings
+
+Flag string parameters that should be types:
+
+```csharp
+// ❌ REVIEW: Should be enum or type
+public void SetAlignment(string alignment);  // "left", "center", "right"
+
+// ✅ Better
+public void SetAlignment(Alignment alignment);
+```
+
+### Incomplete Documentation
+
+Flag public APIs without proper documentation:
+
+```csharp
+// ❌ REVIEW: Missing documentation
+public Hex1bWidget CreateWidget(WidgetContext ctx);
+
+// ❌ REVIEW: Example not runnable
+/// <example>
+/// <code>
+/// widget.OnClick(handler);
+/// </code>
+/// </example>
+```
diff --git a/.github/skills/writing-unit-tests/SKILL.md b/.github/skills/writing-unit-tests/SKILL.md
@@ -0,0 +1,553 @@
+---
+name: writing-unit-tests
+description: Guidelines for writing unit tests in the Hex1b TUI library. Use when creating new tests for widgets, nodes, or terminal functionality.
+---
+
+# Writing Unit Tests Skill
+
+This skill provides guidelines for AI agents writing unit tests for the Hex1b TUI library. It outlines the preferred testing approach, patterns, and anti-patterns to avoid.
+
+## Core Philosophy
+
+1. **Prefer full terminal stack testing** - Use `Hex1bTerminal.CreateBuilder()` to create complete terminal environments
+2. **Use `.WithHex1bApp()`** for TUI functionality tests - This wires up the full app lifecycle
+3. **Keep tests simple and linear** - Avoid excessive abstractions; repeating patterns are beneficial for AI agents
+4. **Assert on visual behavior** - Use `CellPatternSearcher` and color assertions for render verification
+5. **Update this skill** when discovering new patterns - Build the body of knowledge as part of PRs
+
+## When to Use Full Stack vs Isolation
+
+| Test Type | Approach |
+|-----------|----------|
+| Widget behavior, layout, rendering | Full stack with `Hex1bTerminal.CreateBuilder()` |
+| Input handling, focus navigation | Full stack with `WithHex1bApp()` |
+| Low-level APIs (Surface, SurfaceCell) | Test in isolation (dependencies of Hex1bApp) |
+| Color/theme verification | Full stack with snapshot color assertions |
+
+---
+
+## Standard Test Structure
+
+### Full Stack Integration Test
+
+This is the **preferred pattern** for most tests:
+
+```csharp
+[Fact]
+public async Task WidgetName_Scenario_ExpectedBehavior()
+{
+    // Arrange - Build the terminal with the app
+    await using var terminal = Hex1bTerminal.CreateBuilder()
+        .WithHex1bApp((app, options) => ctx => new VStackWidget([
+            new TextBlockWidget("Hello"),
+            new ButtonWidget("Click Me")
+        ]))
+        .WithHeadless()
+        .WithDimensions(80, 24)
+        .Build();
+
+    // Act & Assert - Use input sequencer with WaitUntil
+    var snapshot = await new Hex1bTerminalInputSequenceBuilder()
+        .WaitUntil(s => s.ContainsText("Hello"), TimeSpan.FromSeconds(2), "initial render")
+        .Down()  // Navigate to button
+        .WaitUntil(s => s.ContainsText("> Click Me"), TimeSpan.FromSeconds(2), "button focused")
+        .Capture("focused-button")
+        .Ctrl().Key(Hex1bKey.C)
+        .Build()
+        .ApplyWithCaptureAsync(terminal, TestContext.Current.CancellationToken);
+
+    // Assert (often redundant if WaitUntil already verified)
+    Assert.True(snapshot.ContainsText("> Click Me"));
+}
+```
+
+### Key Elements
+
+1. **`await using var terminal`** - Ensures proper disposal
+2. **`.WithHeadless()`** - No actual terminal output (CI-safe)
+3. **`.WithDimensions(80, 24)`** - Explicit terminal size
+4. **`WaitUntil` before assertions** - Prevents timing issues
+5. **`.Capture("name")`** - Saves SVG/HTML for debugging
+6. **`Ctrl().Key(Hex1bKey.C)`** - Clean exit
+
+---
+
+## Input Sequencing Patterns
+
+### Basic Navigation
+
+```csharp
+await new Hex1bTerminalInputSequenceBuilder()
+    .WaitUntil(s => s.ContainsText("Item 1"), TimeSpan.FromSeconds(2), "list rendered")
+    .Down()
+    .WaitUntil(s => s.ContainsText("> Item 2"), TimeSpan.FromSeconds(2), "moved to item 2")
+    .Down()
+    .WaitUntil(s => s.ContainsText("> Item 3"), TimeSpan.FromSeconds(2), "moved to item 3")
+    .Capture("navigation-result")
+    .Ctrl().Key(Hex1bKey.C)
+    .Build()
+    .ApplyWithCaptureAsync(terminal, TestContext.Current.CancellationToken);
+```
+
+### Text Input
+
+```csharp
+await new Hex1bTerminalInputSequenceBuilder()
+    .WaitUntil(s => s.ContainsText("Name:"), TimeSpan.FromSeconds(2), "form rendered")
+    .Type("John Doe")
+    .WaitUntil(s => s.ContainsText("John Doe"), TimeSpan.FromSeconds(2), "text entered")
+    .Capture("text-input")
+    .Ctrl().Key(Hex1bKey.C)
+    .Build()
+    .ApplyWithCaptureAsync(terminal, TestContext.Current.CancellationToken);
+```
+
+### Keyboard Shortcuts
+
+```csharp
+await new Hex1bTerminalInputSequenceBuilder()
+    .WaitUntil(s => s.ContainsText("Ready"), TimeSpan.FromSeconds(2), "app ready")
+    .Ctrl().Key(Hex1bKey.S)  // Ctrl+S
+    .WaitUntil(s => s.ContainsText("Saved"), TimeSpan.FromSeconds(2), "save completed")
+    .Capture("after-save")
+    .Ctrl().Key(Hex1bKey.C)
+    .Build()
+    .ApplyWithCaptureAsync(terminal, TestContext.Current.CancellationToken);
+```
+
+---
+
+## Visual Assertion Patterns
+
+### Using CellPatternSearcher
+
+For precise cell-level assertions:
+
+```csharp
+// Find a specific character
+var pattern = new CellPatternSearcher().Find('█');
+var result = pattern.Search(snapshot);
+Assert.True(result.HasMatches);
+Assert.Equal(expectedX, result.First!.Start.X);
+
+// Find with regex pattern
+var pattern = new CellPatternSearcher().FindPattern(@"Count:\s*\d+");
+var result = pattern.Search(snapshot);
+Assert.True(result.HasMatches);
+
+// Find with predicate
+var pattern = new CellPatternSearcher()
+    .Find(ctx => char.IsDigit(ctx.Cell.Character[0]));
+var result = pattern.Search(snapshot);
+Assert.Equal(3, result.Count);
+```
+
+### Color Assertions
+
+For verifying themed/styled output:
+
+```csharp
+// Check if any cell has a specific background color
+Assert.True(snapshot.HasBackgroundColor(Hex1bColor.FromRgb(0, 100, 200)),
+    "Button should have blue background");
+
+// Check if any cell has a specific foreground color
+Assert.True(snapshot.HasForegroundColor(Hex1bColor.FromRgb(255, 255, 255)),
+    "Text should be white");
+
+// Get color at specific position
+var bgColor = snapshot.GetBackgroundColor(10, 5);
+Assert.Equal(Hex1bColor.FromRgb(255, 0, 0), bgColor);
+
+// Check uniform row background
+Assert.True(snapshot.HasUniformBackgroundColor(0, Hex1bColor.FromRgb(50, 50, 50)),
+    "Header row should have dark background");
+```
+
+### Available Color Extension Methods
+
+| Method | Purpose |
+|--------|---------|
+| `HasBackgroundColor()` | Any cell has a background color |
+| `HasBackgroundColor(Hex1bColor)` | Any cell has specific background |
+| `HasForegroundColor()` | Any cell has a foreground color |
+| `HasForegroundColor(Hex1bColor)` | Any cell has specific foreground |
+| `GetBackgroundColor(x, y)` | Get background at position |
+| `GetForegroundColor(x, y)` | Get foreground at position |
+| `HasUniformBackgroundColor(y, color)` | All cells in row have same background |
+| `VisualizeBackgroundColors()` | Debug helper with visual representation |
+
+---
+
+## Anti-Patterns to Avoid
+
+> **📘 See the `test-fixer` skill** for detailed diagnosis and fixes when tests become flaky.
+
+### ❌ Insufficient WaitUntil Conditions (Partial Render)
+
+```csharp
+// BROKEN: Waits for partial content, but rest of screen may not be rendered
+await new Hex1bTerminalInputSequenceBuilder()
+    .WaitUntil(s => s.ContainsText("Header"), TimeSpan.FromSeconds(2))  // ❌ Only checks header
+    .Capture("screen")
+    .Build()
+    .ApplyAsync(terminal, ct);
+
+// Assertion on footer may fail - it wasn't part of the WaitUntil!
+Assert.True(snapshot.ContainsText("Footer"));
+```
+
+**Problem**: Rendering is inherently async. Finding "Header" doesn't guarantee "Footer" has rendered yet. This is especially problematic when testing other terminal frameworks (like Spectre Console) which may drop input if they're not ready to receive it.
+
+**Fix**: Over-specify the `WaitUntil` condition to ensure everything you need is present:
+
+```csharp
+// ✅ Wait for ALL content you'll assert on
+await new Hex1bTerminalInputSequenceBuilder()
+    .WaitUntil(s => s.ContainsText("Header") && s.ContainsText("Footer"), 
+               TimeSpan.FromSeconds(2), "full screen rendered")
+    .Capture("screen")
+    .Build()
+    .ApplyAsync(terminal, ct);
+```
+
+**Guideline**: If you're going to assert on specific screen content, include it in the `WaitUntil` condition. Don't assume the rest of the screen is ready just because one part appeared.
+
+### ❌ Snapshot After Exit
+
+```csharp
+// BROKEN: Snapshot taken AFTER Ctrl+C clears the buffer
+var snapshot = await new Hex1bTerminalInputSequenceBuilder()
+    .WaitUntil(s => s.ContainsText("Hello"), TimeSpan.FromSeconds(2))
+    .Capture("final")
+    .Ctrl().Key(Hex1bKey.C)  // Buffer may be cleared before snapshot!
+    .Build()
+    .ApplyWithCaptureAsync(terminal, ct);
+
+Assert.True(snapshot.ContainsText("Hello"));  // ❌ May fail on Linux CI
+```
+
+**Fix**: The `WaitUntil` already verified the content. If you need to assert, the `WaitUntil` serves as the assertion.
+
+### ❌ Missing WaitUntil After Action
+
+```csharp
+// BROKEN: No wait for render after Down()
+await new Hex1bTerminalInputSequenceBuilder()
+    .WaitUntil(s => s.ContainsText("Item 1"), TimeSpan.FromSeconds(2))
+    .Down()
+    .Capture("after-down")  // ❌ Render may not be complete!
+    .Ctrl().Key(Hex1bKey.C)
+    .Build()
+    .ApplyAsync(terminal, ct);
+```
+
+**Fix**: Always add `WaitUntil` after any action that changes state:
+
+```csharp
+.Down()
+.WaitUntil(s => s.ContainsText("> Item 2"), TimeSpan.FromSeconds(2), "moved down")
+.Capture("after-down")
+```
+
+### ❌ Task.Delay for Async Events
+
+```csharp
+// BROKEN: Fixed delay may not be long enough on slow CI
+await terminal.SendKeyAsync(Hex1bKey.Enter);
+await Task.Delay(100);  // ❌ Arbitrary delay
+Assert.True(eventFired);
+```
+
+**Fix**: Use `TaskCompletionSource` to signal completion:
+
+```csharp
+var eventSignal = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
+
+// In event handler:
+eventSignal.TrySetResult();
+
+// In test:
+await eventSignal.Task.WaitAsync(TimeSpan.FromSeconds(2), ct);
+```
+
+### ❌ Over-Abstracted Test Helpers
+
+```csharp
+// AVOID: Too many layers of abstraction
+var result = await TestHelpers.CreateTerminalAndRunScenario(
+    widgets: WidgetFactory.CreateStandardList(),
+    actions: ActionBuilder.NavigateAndSelect(3),
+    assertions: AssertionBuilder.SelectedItem("Item 3")
+);
+```
+
+**Prefer**: Simple, linear, self-contained tests. Repetition is acceptable and helps AI agents understand patterns.
+
+---
+
+## Widget Test Dimensions
+
+When writing tests for widgets, consider all the **dimensions** that affect behavior. Each widget should have tests covering these scenarios:
+
+### 1. Terminal Size Variations
+
+Widgets must work across different terminal sizes. Test the realistic range:
+
+```csharp
+[Theory]
+[InlineData(40, 10)]   // Minimum realistic size
+[InlineData(80, 24)]   // Standard terminal
+[InlineData(120, 40)]  // Large terminal
+[InlineData(200, 60)]  // Very large terminal
+public async Task ListWidget_VariousTerminalSizes_RendersCorrectly(int width, int height)
+{
+    await using var terminal = Hex1bTerminal.CreateBuilder()
+        .WithHex1bApp((app, options) => ctx => new ListWidget(["Item 1", "Item 2", "Item 3"]))
+        .WithHeadless()
+        .WithDimensions(width, height)
+        .Build();
+
+    await new Hex1bTerminalInputSequenceBuilder()
+        .WaitUntil(s => s.ContainsText("Item 1"), TimeSpan.FromSeconds(2), "list rendered")
+        .Capture($"list-{width}x{height}")
+        .Ctrl().Key(Hex1bKey.C)
+        .Build()
+        .ApplyAsync(terminal, TestContext.Current.CancellationToken);
+}
+```
+
+**Key questions to answer:**
+- What is the realistic minimum terminal size for this widget?
+- Does the widget truncate, scroll, or wrap when space is limited?
+- Does the widget expand appropriately in large terminals?
+- Are there edge cases at specific sizes?
+
+### 2. Container Widget Context
+
+Widgets behave differently depending on their parent container. Test inside various layouts:
+
+```csharp
+[Fact]
+public async Task ProgressWidget_InsideBorder_RendersWithCorrectWidth()
+{
+    await using var terminal = Hex1bTerminal.CreateBuilder()
+        .WithHex1bApp((app, options) => ctx => new BorderWidget(
+            new ProgressWidget { Value = 50, Maximum = 100 },
+            title: "Loading"
+        ))
+        .WithHeadless()
+        .WithDimensions(60, 10)
+        .Build();
+
+    await new Hex1bTerminalInputSequenceBuilder()
+        .WaitUntil(s => s.ContainsText("Loading"), TimeSpan.FromSeconds(2), "border rendered")
+        .Capture("progress-in-border")
+        .Ctrl().Key(Hex1bKey.C)
+        .Build()
+        .ApplyAsync(terminal, TestContext.Current.CancellationToken);
+}
+
+[Fact]
+public async Task Button_InsideHStack_SharesSpaceCorrectly()
+{
+    await using var terminal = Hex1bTerminal.CreateBuilder()
+        .WithHex1bApp((app, options) => ctx => new HStackWidget([
+            new ButtonWidget("Cancel"),
+            new ButtonWidget("OK")
+        ]))
+        .WithHeadless()
+        .WithDimensions(40, 5)
+        .Build();
+
+    await new Hex1bTerminalInputSequenceBuilder()
+        .WaitUntil(s => s.ContainsText("Cancel") && s.ContainsText("OK"), TimeSpan.FromSeconds(2))
+        .Capture("buttons-in-hstack")
+        .Ctrl().Key(Hex1bKey.C)
+        .Build()
+        .ApplyAsync(terminal, TestContext.Current.CancellationToken);
+}
+```
+
+**Common container scenarios to test:**
+- Inside `VStackWidget` (vertical stacking)
+- Inside `HStackWidget` (horizontal stacking)
+- Inside `BorderWidget` (reduced available space)
+- Inside `ScrollWidget` (scrollable content)
+- Inside `SplitterWidget` (resizable panes)
+- Nested containers (e.g., Border inside VStack inside Splitter)
+
+### 3. Theming Behavior
+
+Verify that widgets respect theme colors and can be customized:
+
+```csharp
+[Fact]
+public async Task Button_WithCustomTheme_UsesThemeColors()
+{
+    var customTheme = new Hex1bTheme("TestTheme")
+        .Set(ButtonTheme.BackgroundColor, Hex1bColor.FromRgb(255, 0, 0))
+        .Set(ButtonTheme.ForegroundColor, Hex1bColor.FromRgb(255, 255, 255));
+
+    await using var terminal = Hex1bTerminal.CreateBuilder()
+        .WithHex1bApp((app, options) =>
+        {
+            options.Theme = customTheme;
+            return ctx => new ButtonWidget("Test Button");
+        })
+        .WithHeadless()
+        .WithDimensions(40, 5)
+        .Build();
+
+    var snapshot = await new Hex1bTerminalInputSequenceBuilder()
+        .WaitUntil(s => s.ContainsText("Test Button"), TimeSpan.FromSeconds(2))
+        .Capture("themed-button")
+        .Ctrl().Key(Hex1bKey.C)
+        .Build()
+        .ApplyWithCaptureAsync(terminal, TestContext.Current.CancellationToken);
+
+    Assert.True(snapshot.HasBackgroundColor(Hex1bColor.FromRgb(255, 0, 0)),
+        "Button should have red background from theme");
+    Assert.True(snapshot.HasForegroundColor(Hex1bColor.FromRgb(255, 255, 255)),
+        "Button should have white text from theme");
+}
+
+[Fact]
+public async Task Button_FocusedState_UsesFocusedThemeColors()
+{
+    await using var terminal = Hex1bTerminal.CreateBuilder()
+        .WithHex1bApp((app, options) => ctx => new VStackWidget([
+            new TextBlockWidget("Header"),
+            new ButtonWidget("Focusable Button")
+        ]))
+        .WithHeadless()
+        .WithDimensions(40, 5)
+        .Build();
+
+    var snapshot = await new Hex1bTerminalInputSequenceBuilder()
+        .WaitUntil(s => s.ContainsText("Focusable Button"), TimeSpan.FromSeconds(2))
+        .Tab()  // Focus the button
+        .WaitUntil(s => s.ContainsText(">"), TimeSpan.FromSeconds(2), "button focused")
+        .Capture("focused-button-theme")
+        .Ctrl().Key(Hex1bKey.C)
+        .Build()
+        .ApplyWithCaptureAsync(terminal, TestContext.Current.CancellationToken);
+
+    // Verify focused state uses different colors than unfocused
+    Assert.True(snapshot.HasBackgroundColor(), "Focused button should have background color");
+}
+```
+
+**Theming scenarios to test:**
+- Default theme renders correctly
+- Custom theme colors are applied
+- Focused vs unfocused states use appropriate theme values
+- Disabled state styling (if applicable)
+- Theme inheritance from parent widgets
+
+### 4. Widget Test Matrix
+
+For comprehensive widget coverage, consider this matrix:
+
+| Dimension | Variations to Test |
+|-----------|-------------------|
+| **Terminal Size** | Minimum (40×10), Standard (80×24), Large (120×40), Very Large (200×60) |
+| **Container** | Root, VStack, HStack, Border, Scroll, Splitter, Nested |
+| **Theme** | Default, Custom colors, Focused state, Disabled state |
+| **Content** | Empty, Minimal, Typical, Maximum/overflow |
+| **State** | Initial, After interaction, Edge cases |
+
+Not every widget needs every combination, but consider which dimensions are relevant for the widget's behavior.
+
+---
+
+## Low-Level API Testing (Isolation)
+
+For APIs that are dependencies of `Hex1bApp` (like `Surface`), test in isolation:
+
+```csharp
+[Fact]
+public void Surface_WriteText_SetsCorrectCells()
+{
+    // Arrange
+    var surface = new Surface(80, 24);
+    
+    // Act
+    surface.WriteText(0, 0, "Hello");
+    
+    // Assert
+    Assert.Equal('H', surface[0, 0].Character[0]);
+    Assert.Equal('e', surface[1, 0].Character[0]);
+    Assert.Equal('l', surface[2, 0].Character[0]);
+    Assert.Equal('l', surface[3, 0].Character[0]);
+    Assert.Equal('o', surface[4, 0].Character[0]);
+}
+
+[Fact]
+public void SurfaceCell_WithColor_PreservesColor()
+{
+    // Arrange
+    var cell = new SurfaceCell('X', Hex1bColor.Red, Hex1bColor.Blue);
+    
+    // Assert
+    Assert.Equal('X', cell.Character[0]);
+    Assert.Equal(Hex1bColor.Red, cell.Foreground);
+    Assert.Equal(Hex1bColor.Blue, cell.Background);
+}
+```
+
+---
+
+## Test Naming Convention
+
+Follow `MethodName_Scenario_ExpectedBehavior`:
+
+```csharp
+[Fact]
+public async Task ListWidget_DownArrow_SelectsNextItem() { }
+
+[Fact]
+public async Task TextBox_TypeText_DisplaysInput() { }
+
+[Fact]
+public async Task Button_EnterKey_TriggersClickHandler() { }
+
+[Fact]
+public void Surface_Fill_SetsAllCellsInRegion() { }
+```
+
+---
+
+## Updating This Skill
+
+When you discover a new testing pattern while writing tests:
+
+1. **Add the pattern to this skill** as part of the same PR
+2. **Include a concrete example** with comments
+3. **Explain when to use it** (what problem does it solve?)
+4. **If it's an anti-pattern**, add it to the anti-patterns section with the fix
+
+This builds the body of knowledge available to AI agents working on the codebase.
+
+### Examples of Patterns to Document
+
+- New assertion helpers or extension methods
+- Patterns for testing specific widget types
+- Workarounds for platform-specific behavior
+- Performance testing patterns
+- Patterns for testing async behavior
+
+---
+
+## Checklist for New Tests
+
+- [ ] Uses `Hex1bTerminal.CreateBuilder()` with `.WithHeadless()`
+- [ ] Uses `.WithHex1bApp()` for TUI functionality (unless testing low-level APIs)
+- [ ] Has `WaitUntil` after every action that changes state
+- [ ] Has `WaitUntil` immediately before `.Capture()`
+- [ ] Uses descriptive wait messages (third parameter to `WaitUntil`)
+- [ ] Exits cleanly with `Ctrl().Key(Hex1bKey.C)`
+- [ ] Follows `MethodName_Scenario_ExpectedBehavior` naming
+- [ ] Is simple and linear (no unnecessary abstractions)
+- [ ] Asserts on colors when testing themed/styled widgets
+- [ ] Uses `CellPatternSearcher` for precise cell assertions when needed
diff --git a/AGENTS.md b/AGENTS.md
@@ -2,6 +2,23 @@
 
 This document provides context and conventions for AI coding agents (GitHub Copilot, Claude, Cursor, etc.) working with the Hex1b codebase.
 
+## 🛠️ Available Skills
+
+This repository includes specialized skills in `.github/skills/` that provide detailed guidance for specific tasks. **Invoke these skills when working on related tasks** - they contain step-by-step procedures, templates, and best practices.
+
+| Skill | When to Use |
+|-------|-------------|
+| **widget-creator** | Creating new widgets (widget records, nodes, theming, tests) |
+| **writing-unit-tests** | Writing unit tests for widgets, nodes, or terminal functionality |
+| **test-fixer** | Diagnosing flaky tests, especially timing-related failures in CI |
+| **api-reviewer** | Reviewing API design, accessibility modifiers, and naming conventions |
+| **doc-writer** | Writing XML API documentation or end-user guides |
+| **doc-tester** | Validating documentation accuracy against library behavior |
+| **surface-benchmarker** | Running performance benchmarks after modifying `src/Hex1b/Surfaces/` |
+| **aspire** | Working with .NET Aspire (running samples, debugging, MCP tools) |
+
+Skills are invoked automatically by AI agents based on the task context. They contain comprehensive procedures that complement the high-level guidance in this file.
+
 ## 📋 Project Overview
 
 **Hex1b** is a .NET library for building terminal user interfaces (TUI) with a React-inspired declarative API. The library ships to NuGet as `Hex1b`.
@@ -95,27 +112,25 @@ public class ButtonNode : Hex1bNode
 
 ### Adding New Widgets
 
-When adding a new widget type, you must:
+> **📘 Use the `widget-creator` skill** for comprehensive step-by-step guidance including templates, theming, and test patterns.
 
+Quick checklist:
 1. Create `XxxWidget` record in `src/Hex1b/Widgets/`
 2. Create `XxxNode` class in `src/Hex1b/Nodes/`
-3. Add reconciliation case in `Hex1bApp.Reconcile()` switch expression
-4. Add `ReconcileXxx()` method in `Hex1bApp.cs`
+3. Add extension methods in `src/Hex1b/XxxExtensions.cs`
+4. Add theme elements in `src/Hex1b/Theming/XxxTheme.cs`
 5. Write tests in `tests/Hex1b.Tests/XxxNodeTests.cs`
 
 ### Test Conventions
+
+> **📘 Use the `test-fixer` skill** when tests pass locally but fail in CI, or exhibit timing-sensitive behavior.
+
+Follow the `MethodName_Scenario_ExpectedBehavior` naming pattern:
 ```csharp
 [Fact]
-public void MethodName_Scenario_ExpectedBehavior()
+public void Measure_WithConstraints_ReturnsExpectedSize()
 {
-    // Arrange
-    var node = new ButtonNode { Label = "Test" };
-    
-    // Act
-    var result = node.HandleInput(new Hex1bKeyEvent(Hex1bKey.Enter, '\r', Hex1bModifiers.None));
-    
-    // Assert
-    Assert.Equal(InputResult.Handled, result);
+    // Arrange, Act, Assert
 }
 ```
 
@@ -138,70 +153,22 @@ dotnet run --project samples/Cancellation
 
 ## 🚀 .NET Aspire
 
-Aspire is the orchestrator for the entire application, handling dependency configuration, building, and running. Resources are defined in `apphost.cs`.
-
-### Running with Aspire
-```bash
-aspire run
-```
-
-If there is already an instance running, it will prompt to stop the existing instance. You only need to restart if `apphost.cs` changes, but restarting can reset everything to a known state.
+> **📘 Use the `aspire` skill** for detailed Aspire workflows, MCP tools, debugging, and integration guidance.
 
-### General Aspire Workflow
-1. **Before making changes**: Run `aspire run` and inspect resource state to build from a known state
-2. **Make changes incrementally**: Validate with `aspire run` after each change
-3. **Use MCP tools**: Check resource status and debug issues using Aspire MCP tools
+Aspire orchestrates sample applications. Resources are defined in `apphost.cs`.
 
-### Aspire MCP Tools
-
-| Tool | Purpose |
-|------|---------|
-| `list_resources` | Check status of resources in the app model |
-| `execute_resource_command` | Restart resources or perform other actions |
-| `list_integrations` | Get available integrations with versions |
-| `get_integration_docs` | Fetch documentation for specific integrations |
-| `list_structured_logs` | Get structured log details for debugging |
-| `list_console_logs` | Get console log output for debugging |
-| `list_traces` | Get distributed trace information |
-| `list_trace_structured_logs` | Get logs related to a specific trace |
-| `select_apphost` | Switch between multiple app hosts |
-| `list_apphosts` | View active app hosts |
-
-### Adding Integrations
-**IMPORTANT**: When adding a resource to the app model:
-1. Use `list_integrations` to get current versions of available integrations
-2. Match the integration version to the Aspire.AppHost.Sdk version (some may have preview suffix)
-3. Use `get_integration_docs` to fetch the latest documentation
-4. Follow documentation links for additional guidance
-
-### Debugging with Aspire
-Aspire captures rich logs and telemetry. Use diagnostic tools **before** making changes:
-1. `list_structured_logs` - Detailed structured logs
-2. `list_console_logs` - Console output
-3. `list_traces` - Distributed traces
-4. `list_trace_structured_logs` - Logs related to a specific trace
-
-### Updating Aspire
-```bash
-aspire update
-```
-This updates the apphost and some Aspire packages. You may need to manually update other packages. Consider using `dotnet-outdated` with user consent:
+### Quick Commands
 ```bash
-dotnet tool install --global dotnet-outdated-tool
+aspire run              # Run the app host
+aspire run --detach     # Run in background (for agent environments)
+aspire stop             # Stop running instances
+aspire update           # Update Aspire packages
 ```
 
-### Aspire Constraints
-- ⚠️ **Persistent containers**: Avoid early in development to prevent state management issues
-- ⚠️ **Aspire workload is OBSOLETE**: Never install or use the Aspire workload
-- ✅ Changes to `apphost.cs` require application restart
-
-### Playwright Integration
-The Playwright MCP server is configured for functional testing. Use `list_resources` to get endpoints for navigation with Playwright.
-
-### Official Aspire Documentation
-1. https://aspire.dev
-2. https://learn.microsoft.com/dotnet/aspire
-3. https://nuget.org (for integration package details)
+### Key Points
+- Changes to `apphost.cs` require restart
+- Use Aspire MCP tools (`list_resources`, `list_structured_logs`, etc.) for debugging
+- Avoid persistent containers early in development
 
 ## ⚠️ Important Constraints
 
@@ -246,18 +213,22 @@ The Playwright MCP server is configured for functional testing. Use `list_resour
 | `src/Hex1b/Widgets/Hex1bWidget.cs` | Base class for all widgets |
 | `src/Hex1b/Layout/Constraints.cs` | Layout constraint system |
 
-## 🧪 Testing Strategies
+## 🧪 Testing
+
+### Running Tests
+```bash
+dotnet test
+```
 
 ### Unit Testing Nodes
 - Create node directly, set properties, verify behavior
 - Use `Hex1bKeyEvent` to simulate input
 - Check measured size after `Measure()`
-- Verify rendering output if needed
 
 ### Integration Testing
-- Use `Hex1bApp` with mock `IHex1bTerminal`
+- Use `Hex1bApp` with `Hex1bAppWorkloadAdapter`
 - Test full widget → node → render cycle
-- See `Hex1bAppIntegrationTests.cs` for examples
+- See `tests/Hex1b.Tests/` for examples
 
 ## 💬 Asking for Help
 
PATCH

echo "Gold patch applied."
