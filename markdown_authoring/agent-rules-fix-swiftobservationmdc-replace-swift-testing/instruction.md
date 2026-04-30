# Fix swift-observation.mdc: Replace Swift Testing content with Swift Observation content

Source: [steipete/agent-rules#12](https://github.com/steipete/agent-rules/pull/12)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `docs/swift-observation.mdc`

## What to add / change

## Summary

Fixes #2 - The `swift-observation.mdc` file incorrectly contained Swift Testing framework documentation instead of Swift Observation framework content.

## Changes

Completely rewrote the file with comprehensive Swift Observation framework documentation covering:

### Core Concepts
- `@Observable` macro usage and automatic property tracking
- Fine-grained observation vs object-level observation
- Protocol conformance and macro implementation details

### SwiftUI Integration
- Using `@State` instead of `@StateObject`
- `@Bindable` for two-way binding in child views
- `@Environment` for dependency injection
- Property-level update optimization

### Property Control
- `@ObservationTracked` for explicit tracking
- `@ObservationIgnored` for internal state and performance optimization

### Migration Guide
- Step-by-step checklist from ObservableObject to @Observable
- Side-by-side code comparisons
- Key differences table (imports, wrappers, update granularity)

### Advanced Patterns
- Computed properties and observation
- Nested observable objects
- Async operations with Swift concurrency
- Thread safety considerations

### Best Practices
- Model design patterns
- Performance optimization techniques
- Testing strategies
- Common architectural patterns (Repository, State Machine, Coordinator)

### Reference Information
- Platform availability (iOS 17+, macOS 14+, etc.)
- Links to WWDC sessions and Apple documentation
- Swift Evolution proposal reference

## Testing

Veri

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
