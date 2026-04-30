#!/usr/bin/env bash
set -euo pipefail

cd /workspace/copilot-collections

# Idempotency guard
if grep -qF "Your goal is to design a solution that is not overengineered and easy to compreh" ".github/skills/architecture-design/SKILL.md" && grep -qF "- [ ] Step 7: Run static code analysis tools and formatting tools" ".github/skills/code-review/SKILL.md" && grep -qF "Generate a report following the `./research.example.md` structure. Make sure to " ".github/skills/task-analysis/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/architecture-design/SKILL.md b/.github/skills/architecture-design/SKILL.md
@@ -15,9 +15,9 @@ Use the checklist below and track your progress:
 Analysis progress:
 - [ ] Step 1: Understand the goal of the task
 - [ ] Step 2: Analyse the current codebase
-- [ ] Step 3: Ask questions about ambigious parts
+- [ ] Step 3: Ask questions about ambiguous parts
 - [ ] Step 4: Design a solution
-- [ ] Step 5: Create a implementation plan document
+- [ ] Step 5: Create an implementation plan document
 ```
 
 **Step 1: Understand the goal of the task**
@@ -27,16 +27,16 @@ Thorougly process the conversation history and task `research.md` file to fully
 Perform a current codebase analysis to get a full picture of a current system in a context of the task.
 Make sure to understand the project and domain best practices.
 
-**Step 3: Ask questions about ambigious parts**
+**Step 3: Ask questions about ambiguous parts**
 After getting a full picture of the codebase and the task, ask any remaining questions.
-Don't continue untill you get all of the answers.
+Don't continue until you get all of the answers.
 
 **Step 4: Design a solution**
 Based on your findings design a solution architecture.
 
 Follow the best security and software design patterns. 
 
-Your goal is to design a solution that is not overengineered and easy to comprehend by developers, that is at the same time scallable, secure and easy to maintain.
+Your goal is to design a solution that is not overengineered and easy to comprehend by developers, that is at the same time scalable, secure and easy to maintain.
 
 The example patterns you should check (but you are not limited to only use those):
 - Dont repeat yourself
diff --git a/.github/skills/code-review/SKILL.md b/.github/skills/code-review/SKILL.md
@@ -19,9 +19,9 @@ Analysis progress:
 - [ ] Step 4: Verify that solution has implemented all necessary tests
 - [ ] Step 5: Run the available tests
 - [ ] Step 6: Verify that solution follows the best practices
-- [ ] Step 7: Run static code analysis tools and formating tools
+- [ ] Step 7: Run static code analysis tools and formatting tools
 - [ ] Step 8: Validate the solution is secure
-- [ ] Step 9: Validate the solution is scallable
+- [ ] Step 9: Validate the solution is scalable
 ```
 
 **Step 1: Understand the task description**
@@ -59,15 +59,15 @@ Take into account project standards and a practices like SOLID, SRP, DDD, DRY, K
 
 Make sure that solution is not over engineered. Keep the cognitive complexity on a lower side.
 
-**Step 7: Run static code analysis tools and formating tools**
+**Step 7: Run static code analysis tools and formatting tools**
 
 Make sure to run linters, static code analysis tools and formatting tools.
 
 **Step 8: Validate the solution is secure**
 
 Focus on security. Check for potential OWASP TOP10 issues. Check for potential critical security issues that allows other users to take control over the system.
 
-**Step 9: Validate the solution is scallable**
+**Step 9: Validate the solution is scalable**
 
 Analyse if the implemented solution is scalable. Focus on areas like being able to scale it horizontaly, not having a stateful components, not having code with high computational complexity.
 
diff --git a/.github/skills/task-analysis/SKILL.md b/.github/skills/task-analysis/SKILL.md
@@ -16,7 +16,7 @@ Analysis progress:
 - [ ] Step 1: Look for available external sources of information
 - [ ] Step 2: Gather information from all sources
 - [ ] Step 3: Identify gaps and ask clarification questions
-- [ ] Step 4: Based on the answers and gathered information finalize the reasearch report
+- [ ] Step 4: Based on the answers and gathered information finalize the research report
 ```
 
 **Step 1: Look for available external sources of information**
@@ -44,8 +44,8 @@ Find relevant information on knowledge base tools.
 
 Based on the gathered information and task description, look for ambiguities or missing information. Create questions and ask them to the user. Don't proceed until all questions are answered or you are directly told to continue.
 
-**Step 4: Based on the answers and gathered information finalize the reasearch report**
+**Step 4: Based on the answers and gathered information finalize the research report**
 
-Generate a report following the `./research.example.md` structure. Make sure to provide all necessary informations that you gathered, all findings and all answered questions.
+Generate a report following the `./research.example.md` structure. Make sure to provide all necessary information that you gathered, all findings and all answered questions.
 
 Don't add or remove any sections from the template. Follow the structure and naming conventions strictly to ensure clarity and consistency.
\ No newline at end of file
PATCH

echo "Gold patch applied."
