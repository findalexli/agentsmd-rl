# Cursor rules file for Audius style guide

Source: [AudiusProject/apps#12870](https://github.com/AudiusProject/apps/pull/12870)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/audius-style-guide.mdc`

## What to add / change

### Description
Try adding cursor rules for the audius style guide

---
description: TypeScript/React coding standards - prefer null coalescing, optional chaining, ternaries for rendering, optional types, and organized string constants
globs:
alwaysApply: true
---

# TypeScript Best Practices

## Null Coalescing & Optional Chaining

Use `??` and `?.` instead of `&&`/`||` for null checks.

```typescript
// ✅ Good
const value = user?.name ?? 'Anonymous'
const displayName = user?.profile?.displayName ?? 'Unknown'

// ❌ Bad
const value = (user && user.name) || 'Anonymous'
const displayName =
  (user && user.profile && user.profile.displayName) || 'Unknown'
```

## Conditional Rendering

Use ternaries instead of `&&` for JSX conditional rendering.

```tsx
// ✅ Good
return !user ? null : <UserProfile user={user} />
return list.length === 0 ? null : <List items={list} />

// ❌ Bad
return user && <UserProfile user={user} />
return list.length && <List items={list} />
```

## String Constants

Organize user-facing strings in a `messages` object at the top of components.

```tsx
// ✅ Good
const messages = {
  title: 'Welcome',
  error: 'Something went wrong'
}

return <h1>{messages.title}</h1>

// ❌ Bad
return <h1>Welcome</h1>
```

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
