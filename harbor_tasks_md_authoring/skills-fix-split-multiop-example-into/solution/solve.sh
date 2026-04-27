#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "Each file must contain exactly one operation. Each named operation becomes an MC" "skills/apollo-mcp-server/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/apollo-mcp-server/SKILL.md b/skills/apollo-mcp-server/SKILL.md
@@ -10,7 +10,7 @@ license: MIT
 compatibility: Works with Claude Code, Claude Desktop, Cursor.
 metadata:
   author: apollographql
-  version: "1.1.0"
+  version: "1.1.1"
 allowed-tools: Bash(rover:*) Bash(npx:*) Read Write Edit Glob Grep
 ---
 
@@ -124,16 +124,21 @@ operations:
     - ./operations/
 ```
 
+Each file must contain exactly one operation. Each named operation becomes an MCP tool.
+
 ```graphql
-# operations/users.graphql
+# operations/GetUser.graphql
 query GetUser($id: ID!) {
   user(id: $id) {
     id
     name
     email
   }
 }
+```
 
+```graphql
+# operations/CreateUser.graphql
 mutation CreateUser($input: CreateUserInput!) {
   createUser(input: $input) {
     id
@@ -142,8 +147,6 @@ mutation CreateUser($input: CreateUserInput!) {
 }
 ```
 
-Each named operation becomes an MCP tool.
-
 ### 2. Operation Collections
 
 ```yaml
PATCH

echo "Gold patch applied."
