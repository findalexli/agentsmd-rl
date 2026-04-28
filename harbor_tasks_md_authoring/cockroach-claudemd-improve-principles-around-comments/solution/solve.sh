#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cockroach

# Idempotency guard
if grep -qF "Explain concepts/abstractions, show how pieces fit together, connect to use case" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -514,6 +514,39 @@ s := fmt.Sprint(rand.Int())   // slower
 func (n NodeID) SafeValue() {}  // always safe to log
 ```
 
+#### Comment Placement Principles
+
+Comments should be placed where they provide the most value and avoid duplication:
+
+**Data Structure Comments:**
+- Belong at the **data structure declaration**
+- Explain the purpose, lifecycle, and invariants of the struct/type
+- Document which code initializes fields, which code accesses them, and when they become obsolete
+- Do not repeat this information in function comments that use these structures
+
+**Algorithmic Comments:**
+- Belong **inside function bodies**
+- Explain the logic, phases, and non-obvious implementation details
+- Separate different processing phases with summary comments
+- Focus on "why" rather than "what" the code does
+
+**Function Declaration Comments:**
+- Focus on **inputs and outputs** - what the function does, not how
+- Describe the contract, preconditions, postconditions, and behavior
+- Do NOT explain the intricacies of input/output types if those are data structures already documented at their declaration
+- Readers should refer to the data structure definition for detailed field explanations
+
+**Overview and Design Comments:**
+- Must be **completely understandable with zero knowledge of the code**
+- If a reader cannot understand the overview without reading code, either improve the comment or remove it
+- Reading an incomprehensible comment followed by code is double work
+- To make overview comments understandable:
+  - **Minimize new terminology** - use plain language where possible
+  - **Define new terms immediately** when you must introduce them
+  - **Illustrate with examples** to clarify abstract concepts
+  - **Limit term introduction** - avoid introducing many new terms at once; consider using variants of existing terms instead
+- If you introduce terms like "satisfiable", "strict", "coverage" in quick succession, step back and see if fewer, clearer terms would suffice
+
 #### Engineering Standards (Enforced in Reviews)
 
 CockroachDB is a complex system and you should write code under the assumption
@@ -537,7 +570,7 @@ compatibility issues.  See `pkg/clusterversion` for more on this.
 #### Comment Types and Examples
 
 **Top-Level Design Comments:**
-Explain concepts/abstractions, show how pieces fit together, connect to use cases.
+Explain concepts/abstractions, show how pieces fit together, connect to use cases. These must be understandable without reading any code - define terms clearly and use examples to illustrate abstract concepts.
 
 Example from `concurrency/concurrency_control.go`:
 ```go
@@ -568,6 +601,8 @@ type AuthConn interface {
 ```
 
 **Function Comments:**
+Focus on inputs, outputs, and behavior. Avoid re-documenting data structure details that are explained at their declaration.
+
 ```go
 // Append appends the provided string and any number of query parameters.
 // Instead of using normal placeholders (e.g. $1, $2), use meta-placeholder $.
@@ -589,6 +624,8 @@ func (q *sqlQuery) Append(s string, params ...interface{}) { /* ... */ }
 ```
 
 **Struct Field Comments:**
+Document the purpose, lifecycle, and usage of each field. This is where data structure details belong - function comments should not repeat this information.
+
 ```go
 // cliState defines the current state of the CLI during command-line processing.
 //
@@ -610,6 +647,8 @@ type cliState struct {
 ```
 
 **Phase Comments in Function Bodies:**
+Algorithmic comments that separate different processing phases and explain non-obvious logic. These belong inside functions, not at function declarations.
+
 ```go
 func (r *Replica) executeAdminCommandWithDescriptor(
     ctx context.Context, updateDesc func(*roachpb.RangeDescriptor) error,
PATCH

echo "Gold patch applied."
