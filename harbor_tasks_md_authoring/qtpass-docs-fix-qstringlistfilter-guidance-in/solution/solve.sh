#!/usr/bin/env bash
set -euo pipefail

cd /workspace/qtpass

# Idempotency guard
if grep -qF "When the goal is to drop env vars by name prefix, use `std::remove_if` with `sta" ".opencode/skills/qtpass-fixing/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.opencode/skills/qtpass-fixing/SKILL.md b/.opencode/skills/qtpass-fixing/SKILL.md
@@ -210,7 +210,6 @@ for (int i = 0; i < m_userList.size(); ++i) {
     item->setData(Qt::UserRole, QVariant::fromValue(i));
 }
 
-
 // Later, lookup by index
 bool success = false;
 const int index = item->data(Qt::UserRole).toInt(&success);
@@ -288,13 +287,15 @@ env.erase(std::remove_if(env.begin(), env.end(),
           env.end());
 ```
 
-When filtering with a substring match (e.g., environment variable removal), use `startsWith` rather than `contains` or `filter()` to avoid removing unrelated entries with similar prefixes:
+When the goal is to drop env vars by name prefix, use `std::remove_if` with `startsWith`. Don't reach for `QStringList::filter()` — it does the opposite (keeps matching entries) and matches substrings anywhere in the string, so even as a selection it would over-match:
 
 ```cpp
-// Bad — filter("FOO") also removes "FOOBAR=value"
+// Bad — filter() returns entries containing key, also matching "FOOBAR=value"
+// when key is "FOO". And it selects, not removes; the assignment then drops
+// every entry that didn't match — opposite of the intent.
 env = env.filter(key);
 
-// Good — explicit prefix check
+// Good — explicit prefix-based removal
 env.erase(std::remove_if(env.begin(), env.end(),
                           [&key](const QString &e) { return e.startsWith(key); }),
           env.end());
PATCH

echo "Gold patch applied."
