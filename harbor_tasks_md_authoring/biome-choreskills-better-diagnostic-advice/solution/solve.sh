#!/usr/bin/env bash
set -euo pipefail

cd /workspace/biome

# Idempotency guard
if grep -qF "\"Variables declared with \"<Emphasis>\"var\"</Emphasis>\" are function-scoped, not b" ".claude/skills/diagnostics-development/SKILL.md" && grep -qF "If the rule has an `action()` to fix the issue, the 3rd message should go in the" ".claude/skills/lint-rule-development/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/diagnostics-development/SKILL.md b/.claude/skills/diagnostics-development/SKILL.md
@@ -142,14 +142,14 @@ impl Rule for NoVar {
                 rule_category!(),
                 node.range(),
                 markup! {
-                    "Use "<Emphasis>"let"</Emphasis>" or "<Emphasis>"const"</Emphasis>" instead of "<Emphasis>"var"</Emphasis>"."
+                    "Using "<Emphasis>"var"</Emphasis>" is not recommended."
                 },
             )
             .note(markup! {
-                "Variables declared with "<Emphasis>"var"</Emphasis>" are function-scoped, not block-scoped."
+                "Variables declared with "<Emphasis>"var"</Emphasis>" are function-scoped, not block-scoped, which means they can leak outside of loops and conditionals and cause unexpected behavior."
             })
             .note(markup! {
-                "See the "<Hyperlink href="https://developer.mozilla.org/docs/Web/JavaScript/Reference/Statements/var">"MDN documentation"</Hyperlink>" for more details."
+                "Consider using "<Emphasis>"let"</Emphasis>" or "<Emphasis>"const"</Emphasis>" instead."
             })
         )
     }
diff --git a/.claude/skills/lint-rule-development/SKILL.md b/.claude/skills/lint-rule-development/SKILL.md
@@ -211,7 +211,8 @@ just test-lintrule useMyRuleName
 
 Review snapshots:
 ```shell
-cargo insta review
+cargo insta accept # accept all snapshots
+cargo insta reject # reject all snapshots
 ```
 
 ### Generate Analyzer Code
@@ -317,6 +318,42 @@ declare_node_union! {
 type Query = Semantic<AnyFunctionLike>;
 ```
 
+## High Quality Diagnostics
+
+Diagnostics must convey these messages, in this order:
+
+1. What the problem is
+2. Why it's a problem (motivation to fix the issue)
+3. How to fix it (actionable advice)
+
+If the rule has an `action()` to fix the issue, the 3rd message should go in the action's message. If not, it should go in the diagnostic's advice.
+
+Good:
+```
+1. "Foo is not allowed here."
+2. "Foo harms readability because of X, Y, Z."
+3. "Consider using Bar instead, which is more concise and easier to read."
+```
+
+```
+1. "Unexpected for-in loop."
+2. "For-in loops are confusing and easy to misuse."
+3. "You likely want to use a regular loop, for-of loop or forEach instead."
+```
+
+Bad:
+
+```
+1. "Prefer let or const over var." // conflates the what and the how in one message,
+2. "var is bad." // not meaningful motivation to fix, doesn't explain the consequences
+// third message missing is bad, because it doesn't give users a clear path to fix the issue
+```
+
+## Tips
+
+- New rules are always in the `nursery` group. No need to move them to another category.
+- Changesets are always required for new rules. New rules are `patch` level changes. There's a skill to help write good changesets.
+
 ## References
 
 - Full guide: `crates/biome_analyze/CONTRIBUTING.md`
PATCH

echo "Gold patch applied."
