#!/usr/bin/env bash
set -euo pipefail

cd /workspace/biome

# Idempotency guard
if grep -qF "- Calling `.to_string()` or `.to_string_trimmed()` (allocates a string) on a `Sy" ".claude/skills/biome-developer/SKILL.md" && grep -qF "- Building strings or other data structures only used in the code action in `run" ".claude/skills/lint-rule-development/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/biome-developer/SKILL.md b/.claude/skills/biome-developer/SKILL.md
@@ -358,6 +358,11 @@ if let Some(directive) = VueDirective::cast_ref(&element) {
 
 The CI uses `markdownlint-cli2` which enforces the "compact" style requiring spaces.
 
+## Common Mistakes to Avoid
+
+- Calling `format!()` (allocates a string) when formatting strings in a `markup!` block. `markup!` supports interpolation, E.g. `markup! { "Hello, "{name}"!" }`.
+- Calling `.to_string()` or `.to_string_trimmed()` (allocates a string) on a `SyntaxToken` or `SyntaxNode`. It's highly unlikely that you actually need to call these methods on a syntax node. As for syntax tokens, you can easily borrow a `&str` from the token's text without allocating a new string, using `token.text()`.
+
 ## When to Use This Skill
 
 Load this skill when:
diff --git a/.claude/skills/lint-rule-development/SKILL.md b/.claude/skills/lint-rule-development/SKILL.md
@@ -302,6 +302,13 @@ impl Rule for UseMyRuleName {
 - **Error recovery**: When navigating CST, use `.ok()?` pattern to handle missing nodes gracefully
 - **Testing arrays**: Use `.jsonc` files with arrays of code snippets for multiple test cases
 
+## Common Mistakes to Avoid
+
+Generally, mistakes revolve around allocating unnecessary data during rule execution, which can lead to performance issues. Common examples include:
+
+- Placing `String` or `Box<str>` in a Rule's `State` type. It's a strong indicator that you are allocating a string unnecessarily. If the string comes from a CST token, this usually can be avoided by using `TokenText` instead.
+- Building strings or other data structures only used in the code action in `run()` instead of `action()`. `run()` should only decide whether to emit a diagnostic; `action()` should build the fix. This matters for performance because building the action can be expensive, and we should avoid doing it when no diagnostic is emitted.
+
 ## Common Query Types
 
 ```rust
PATCH

echo "Gold patch applied."
