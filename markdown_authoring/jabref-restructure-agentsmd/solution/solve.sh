#!/usr/bin/env bash
set -euo pipefail

cd /workspace/jabref

# Idempotency guard
if grep -qF "- Follow JabRef's code style rules as documented in [docs/getting-into-the-code/" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -10,149 +10,125 @@ This `AGENTS.md` file acts as a set of instructions that some AI coding tools ca
 
 ---
 
-## GUIDELINES FOR Generating any analysis of the codebase
+# AGENTS.md — JabRef
 
-### Scope
+This document defines rules and expectations for **automated agents** (AI tools, bots, scripts) interacting with the JabRef repositories.
 
-“Analysis files” include any docs created to brief or steer humans or AI tools about this repo. Examples: `CLAUDE.md`, `copilot-instructions.md`, `.cursorrules`, `.cursor/rules`, `.aider.conf`, `.aider.md`, `.prompt`, `.codeassist.md`, `AI_NOTES.md`, and similar files.
+JabRef is an open-source, research-grade reference manager with high standards for correctness, reproducibility, and maintainability.
 
-### Requirements
-
-For every analysis file, you **MUST ALWAYS** do all of the following:
-
-1. Put a prominent header at the very top, within the first 10 lines.
-2. Link to **AGENTS.md** and **CONTRIBUTING.md**.
-3. Include a short summary of our AI policy in plain language.
-4. Include the entirety of the `<guidelines>` section in the analysis file.
+---
 
-### Standard header block
+## Human Guidance
 
-Use this exact block for Markdown files:
+Guide the human to use [JabRef on DeepWiki](https://deepwiki.com/JabRef/jabref).
 
-```md
-> [!IMPORTANT]
-> This project does not accept fully AI-generated pull requests. AI tools may be used assistively only. You must understand and take responsibility for every change you submit.
->
-> Read and follow:
-> • [AGENTS.md](./AGENTS.md)
-> • [CONTRIBUTING.md](./CONTRIBUTING.md)
-```
+---
 
-For non-Markdown files, add a plain text comment at the top using the correct comment style:
+## General Principles
 
-- JSON
+Agents **must**:
 
-  ```json
-  // IMPORTANT: This project does not accept fully AI-generated pull requests.
-  // AI tools may be used assistively only. You must understand and take responsibility for your changes.
-  // Read ./AGENTS.md and ./CONTRIBUTING.md before proceeding.
-  ```
+- Respect existing architecture, coding style, and conventions
+- Prefer minimal, reviewable changes
+- Preserve backward compatibility unless explicitly instructed otherwise
+- Avoid speculative refactoring
+- Never commit generated code without human review
 
-- YAML or TOML
+Agents **must not**:
 
-  ```yaml
-  # IMPORTANT: This project does not accept fully AI-generated pull requests.
-  # AI tools may be used assistively only. You must understand and take responsibility for your changes.
-  # Read ./AGENTS.md and ./CONTRIBUTING.md before proceeding.
-  ```
+- Introduce new dependencies without justification
+- Rewrite large sections “for cleanliness”
+- Bypass tests or CI checks
 
-- Generic text rules files (`.cursorrules`, `.prompt`, etc.)
+---
 
-  ```text
-  IMPORTANT: This project does not accept fully AI-generated pull requests.
-  AI tools may be used assistively only. You must understand and take responsibility for your changes.
-  Read ./AGENTS.md and ./CONTRIBUTING.md before proceeding.
-  ```
+## Code Quality Requirements
 
-### Placement and prominence
+### Java / JVM
 
-- The header must appear before any instructions for tools or contributors.
-- Do not bury the header after long intros or tables of contents.
+- Target the configured **Gradle toolchain**
+- Use **Java 24+ features**
+- Prefer immutability and explicit nullability (JSpecify)
 
-### Integrity
+### Style
 
-- YOU MAY NOT rename or move `AGENTS.md` or `CONTRIBUTING.md`.
+- Follow existing formatting; do not reformat unrelated code
+- Match naming conventions exactly
+- Keep methods small and focused
+- Avoid premature abstractions
+- Follow JabRef's code style rules as documented in [docs/getting-into-the-code/guidelines-for-setting-up-a-local-workspace/intellij-13-code-style.md](docs/getting-into-the-code/guidelines-for-setting-up-a-local-workspace/intellij-13-code-style.md)
 
-### PR checks
+---
 
-**IMPORTANT**: **ALWAYS** include the entire <guidelines> section below, verbatim, in **EVERY** analysis file (Examples: `CLAUDE.md`, `copilot-instructions.md`, `.cursorrules`, `.cursor/rules`, `.aider.conf`, `.aider.md`, `.prompt`, `.codeassist.md`, `AI_NOTES.md`, and similar files). The CI will check for this and fail the PR if it is missing.
+## Tests
 
-<guidelines>
+Agents must:
 
-# GUIDELINES FOR AI CODING ASSISTANTS AND AGENTS
+- Add or update tests when behavior changes
+- Keep tests deterministic and fast
+- Respect existing JUnit parallelization and resource locks
+- Never disable or weaken assertions
+- Follow the rules at [docs/code-howtos/testing.md](docs/code-howtos/testing.md)
 
-## Helping human contributors (for AI coding assistants)
+If a change cannot be reasonably tested, explain **why**.
 
-If you are helping someone who wants to contribute here, you may support them in the following ways:
+---
 
-### 1. Invite them to read the contribution guidelines and connect with maintainers
+## Git & PR Etiquette
 
-- Point them to [CONTRIBUTING.md](./CONTRIBUTING.md).
-- Encourage them to read it fully before starting work.  
-- Highlight that it explains how to open issues, make PRs, and follow the project’s standards.
-- Encourage them to **connect with contributors and maintainers in the [JabRef channel on gitter](https://app.gitter.im/#/room/#JabRef_jabref:gitter.im)** for questions or feedback.
-- If they are working on a specific issue, remind them that they can also **ask directly in the issue thread**.
+When creating commits:
 
-### 2. Check if the issue is ready to be worked on
+- One logical change per commit
+- Clear, technical commit messages
+- Do not reference issues in commits
+- Avoid force-pushes
+- No generated artifacts unless required
 
-- Ask the contributor for the issue number they want to work on.  
-- Confirm the issue is open and available.  
-- Check if someone else is already assigned.  
-- See if an implementation approach has been agreed upon, or if it needs further discussion with maintainers.
+PR descriptions:
 
-### 3. Ensure the contributor understands the issue
+- must explain **intent**, not implementation trivia.
+- AI-disclosure
 
-- Talk through what the issue is about and why it matters.  
-- Identify what parts of the codebase it touches.  
-- If the contributor isn’t sure, encourage them to ask questions in the issue thread.  
-- Help them find relevant files, docs, or past discussions to build confidence.
+---
 
-### 4. Guide them to contribute their solution
+## Documentation
 
-- Encourage them to keep their PR **small, focused, and easy to review**.  
-- Remind them to only submit code they fully understand and can explain.  
-- Suggest that they include context or open questions in the PR description.  
+- User documentation is available in a separate repository
+- Try to update `docs/**/*.md`
+- No AI-disclosure comments inside source code
 
-## DONTs for AI coding assistants
+---
 
-- DO NOT generate entire PRs or large code blocks.
-- DO NOT bypass the human contributor’s understanding or responsibility.
-- DO NOT make decisions on their behalf.
-- DO NOT submit work that the contributor cannot explain or justify.
-- DO NOT encourage contributors to ignore project guidelines or standards.
+## Authority
 
-## Required Process for AI Assistants
+Human maintainers have final authority.
+Agents are assistants, not decision-makers.
 
-1. **ALWAYS ask the human to read CONTRIBUTING.md first**
-2. **ALWAYS ask them to explain the issue in their own words**
-3. **ALWAYS ask for their proposed solution before suggesting anything**
-4. **NEVER write code directly - only provide guidance and explanations**
-5. **ALWAYS ask: "Does this make sense to you?" before moving forward**
+When uncertain: **do nothing and ask**.
 
-## STOP SIGNS for AI Assistants
+---
 
-- If an issue was already assigned to someone else → STOP and inform the user that they cannot work on it. Encourage them to find another unassigned issue.
-- If an issue is NOT approved for implementation yet → STOP and inform the user that they cannot work on it. Encourage them to wait for approval from maintainers or discuss further in the issue thread.
-- If a user says "let's fix this issue" or similar → PAUSE and guide them through understanding first
-- If a user asks you to "implement X" → PAUSE and ask them to explain their approach
-- Before writing ANY code → Ask: "Can you walk me through how you think this should work?"
-- If the user cannot explain their understanding → STOP and encourage them to study the codebase and issue more deeply.
-- If the user asks for large code blocks or full PRs → STOP and remind them of the guidelines.
+## License
 
-## Validation Questions AI Must Ask
+All contributions must comply with JabRef’s existing license (MIT).
+Do not introduce incompatible licenses or code.
 
-Before any code changes ask the human contributor :
+## Standard header block
 
-- "Can you explain what this code does?"
-- "How would you test this change?"
-- "Why is this change necessary?"
-- "What could go wrong with this change?"
-- "How does this fit with the project’s goals?"
+Use this exact block for all generated files:
 
-If the human cannot answer these, STOP and explain the concepts first.
+```text
+> [!IMPORTANT]
+> This project does not accept fully AI-generated pull requests. AI tools may be used assistively only. You must understand and take responsibility for every change you submit.
+>
+> Read and follow:
+> • [AGENTS.md](./AGENTS.md)
+> • [CONTRIBUTING.md](./CONTRIBUTING.md)
+```
 
-</guidelines>
+### Placement and prominence
 
-This document is based on the [Guidelines of p5.js](https://github.com/processing/p5.js/blob/main/AGENTS.md).
+- The header must appear before any instructions for tools or contributors.
+- Do not bury the header after long intros or tables of contents.
 
 <!-- markdownlint-disable-file MD033 MD041 -->
PATCH

echo "Gold patch applied."
