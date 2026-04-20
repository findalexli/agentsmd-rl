# Builder-Vite Hash Collision Bug

## Symptom

When building Storybook with pnpm package manager, the build fails with:

```
[vite:build-html] The symbol "preview_XXXX" has already been declared
```

where `XXXX` is a numeric identifier. This happens because the preview annotation
generator uses a hash function to create variable names, and that hash produces
collisions when paths contain different character sequences that sum to the same
value.

## Root Cause

The hash function in `codegen-project-annotations.ts` uses a simple
character-code summation approach:

```typescript
value.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
```

This is **not position-sensitive**: different strings containing the same characters
(anagrams) produce identical hash values. With npm/yarn, preview paths are short
and collisions don't occur. However, with pnpm, peer dependency hash suffixes
(hex strings) are included in paths, causing different packages to produce the
same hash value.

## Expected Behavior

The hash function must:
1. Produce **different hash values** for anagramatic strings (e.g., "abc" vs "cba")
2. Be **position-sensitive** — character position must affect the hash
3. Produce **no collisions** for the pnpm-style paths that trigger the bug

## Validation Reference

The reference hash values for specific inputs are:
- Empty string (`""`): 5381
- `"a"`: 177670
- `"abc"`: 193485963

A known hash algorithm documented at `http://www.cse.yorku.ca/~oz/hash.html` produces
these values using a seed of 5381 and an iterative update formula.

## Task

Fix the hash function in `codegen-project-annotations.ts` to eliminate the variable
name collision bug when building with pnpm.

The function should produce position-sensitive hashes with no anagram collisions,
matching the reference values shown above.