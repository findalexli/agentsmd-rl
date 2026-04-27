#!/usr/bin/env bash
set -euo pipefail

cd /workspace/awesome-llm-apps

# Idempotency guard
if grep -qF "awesome_agent_skills/python-expert/AGENTS.md" "awesome_agent_skills/python-expert/AGENTS.md" && grep -qF "Detailed rules with examples are documented in [AGENTS.md](AGENTS.md), organized" "awesome_agent_skills/python-expert/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/awesome_agent_skills/python-expert/AGENTS.md b/awesome_agent_skills/python-expert/AGENTS.md
@@ -66,8 +66,6 @@ def add_item(item: str, items: list[str] | None = None) -> list[str]:
     return items
 ```
 
-[➡️ Full details: correctness-mutable-defaults.md](rules/correctness-mutable-defaults.md)
-
 ---
 
 ### Proper Error Handling
@@ -98,8 +96,6 @@ except FileNotFoundError:
     config = get_default_config()
 ```
 
-[➡️ Full details: correctness-error-handling.md](rules/correctness-error-handling.md)
-
 ---
 
 ## Type Safety
@@ -138,8 +134,6 @@ def get_user(user_id: int) -> Optional[Dict[str, Any]]:
     return users.get(user_id)
 ```
 
-[➡️ Full details: type-hints.md](rules/type-hints.md)
-
 ---
 
 ### Use Dataclasses
@@ -186,8 +180,6 @@ class Config:
     timeout: int = 30
 ```
 
-[➡️ Full details: type-dataclasses.md](rules/type-dataclasses.md)
-
 ---
 
 ## Performance
@@ -229,8 +221,6 @@ evens = [x for x in range(20) if x % 2 == 0]
 matrix = [[i * j for j in range(3)] for i in range(3)]
 ```
 
-[➡️ Full details: performance-comprehensions.md](rules/performance-comprehensions.md)
-
 ---
 
 ### Use Context Managers
@@ -263,8 +253,6 @@ with open('input.txt') as infile, open('output.txt', 'w') as outfile:
     outfile.write(infile.read().upper())
 ```
 
-[➡️ Full details: performance-context-managers.md](rules/performance-context-managers.md)
-
 ---
 
 ## Style
@@ -307,8 +295,6 @@ class UserAccount:
 x = 1 + 2
 ```
 
-[➡️ Full details: style-pep8.md](rules/style-pep8.md)
-
 ---
 
 ### Write Docstrings
@@ -364,8 +350,6 @@ def process_user_data(
     ...
 ```
 
-[➡️ Full details: style-docstrings.md](rules/style-docstrings.md)
-
 ---
 
 ## Quick Reference
@@ -453,7 +437,6 @@ When reviewing Python code, structure your output as:
 
 ## References
 
-- Individual rule files in `rules/` directory
 - [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/)
 - [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
 - [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
diff --git a/awesome_agent_skills/python-expert/SKILL.md b/awesome_agent_skills/python-expert/SKILL.md
@@ -28,31 +28,30 @@ Use this skill when:
 
 ## How to Use This Skill
 
-This skill contains **detailed rules** in the `rules/` directory, organized by category and priority.
+Detailed rules with examples are documented in [AGENTS.md](AGENTS.md), organized by category and priority.
 
 ### Quick Start
 
 1. **Review [AGENTS.md](AGENTS.md)** for a complete compilation of all rules with examples
-2. **Reference specific rules** from `rules/` directory for deep dives
-3. **Follow priority order**: Correctness → Type Safety → Performance → Style
+2. **Follow priority order**: Correctness → Type Safety → Performance → Style
 
 ### Available Rules
 
 **Correctness (CRITICAL)**
-- [Avoid Mutable Default Arguments](rules/correctness-mutable-defaults.md)
-- [Proper Error Handling](rules/correctness-error-handling.md)
+- [Avoid Mutable Default Arguments](AGENTS.md#avoid-mutable-default-arguments)
+- [Proper Error Handling](AGENTS.md#proper-error-handling)
 
 **Type Safety (HIGH)**
-- [Use Type Hints](rules/type-hints.md)
-- [Use Dataclasses](rules/type-dataclasses.md)
+- [Use Type Hints](AGENTS.md#use-type-hints)
+- [Use Dataclasses](AGENTS.md#use-dataclasses)
 
 **Performance (HIGH)**
-- [Use List Comprehensions](rules/performance-comprehensions.md)
-- [Use Context Managers](rules/performance-context-managers.md)
+- [Use List Comprehensions](AGENTS.md#use-list-comprehensions)
+- [Use Context Managers](AGENTS.md#use-context-managers)
 
 **Style (MEDIUM)**
-- [Follow PEP 8 Style Guide](rules/style-pep8.md)
-- [Write Docstrings](rules/style-docstrings.md)
+- [Follow PEP 8 Style Guide](AGENTS.md#follow-pep-8-style-guide)
+- [Write Docstrings](AGENTS.md#write-docstrings)
 
 ## Development Process
 
PATCH

echo "Gold patch applied."
