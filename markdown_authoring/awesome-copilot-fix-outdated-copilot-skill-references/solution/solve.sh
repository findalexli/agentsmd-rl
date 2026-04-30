#!/usr/bin/env bash
set -euo pipefail

cd /workspace/awesome-copilot

# Idempotency guard
if grep -qF "- [ ] Skills and agents include relevant descriptions; include MCP/tool-related " "skills/github-copilot-starter/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/github-copilot-starter/SKILL.md b/skills/github-copilot-starter/SKILL.md
@@ -12,51 +12,82 @@ Ask the user for the following information if not provided:
 1. **Primary Language/Framework**: (e.g., JavaScript/React, Python/Django, Java/Spring Boot, etc.)
 2. **Project Type**: (e.g., web app, API, mobile app, desktop app, library, etc.)
 3. **Additional Technologies**: (e.g., database, cloud provider, testing frameworks, etc.)
-4. **Team Size**: (solo, small team, enterprise)
-5. **Development Style**: (strict standards, flexible, specific patterns)
+4. **Development Style**: (strict standards, flexible, specific patterns)
+5. **GitHub Actions / Coding Agent**: Does the project use GitHub Actions? (yes/no — determines whether to generate `copilot-setup-steps.yml`)
 
 ## Configuration Files to Create
 
 Based on the provided stack, create the following files in the appropriate directories:
 
 ### 1. `.github/copilot-instructions.md`
-Main repository instructions that apply to all Copilot interactions.
+Main repository instructions that apply to all Copilot interactions. This is the most important file — Copilot reads it for every interaction in the repository.
+
+Use this structure:
+```md
+# {Project Name} — Copilot Instructions
+
+## Project Overview
+Brief description of what this project does and its primary purpose.
+
+## Tech Stack
+List the primary language, frameworks, and key dependencies.
+
+## Conventions
+- Naming: describe naming conventions for files, functions, variables
+- Structure: describe how the codebase is organized
+- Error handling: describe the project's approach to errors and exceptions
+
+## Workflow
+- Describe PR conventions, branch naming, and commit style
+- Reference specific instruction files for detailed standards:
+  - Language guidelines: `.github/instructions/{language}.instructions.md`
+  - Testing: `.github/instructions/testing.instructions.md`
+  - Security: `.github/instructions/security.instructions.md`
+  - Documentation: `.github/instructions/documentation.instructions.md`
+  - Performance: `.github/instructions/performance.instructions.md`
+  - Code review: `.github/instructions/code-review.instructions.md`
+```
 
 ### 2. `.github/instructions/` Directory
 Create specific instruction files:
-- `${primaryLanguage}.instructions.md` - Language-specific guidelines
+- `{primaryLanguage}.instructions.md` - Language-specific guidelines
 - `testing.instructions.md` - Testing standards and practices
 - `documentation.instructions.md` - Documentation requirements
 - `security.instructions.md` - Security best practices
 - `performance.instructions.md` - Performance optimization guidelines
 - `code-review.instructions.md` - Code review standards and GitHub review guidelines
 
-### 3. `.github/prompts/` Directory
-Create reusable prompt files:
-- `setup-component.prompt.md` - Component/module creation
-- `write-tests.prompt.md` - Test generation
-- `code-review.prompt.md` - Code review assistance
-- `refactor-code.prompt.md` - Code refactoring
-- `generate-docs.prompt.md` - Documentation generation
-- `debug-issue.prompt.md` - Debugging assistance
+### 3. `.github/skills/` Directory
+Create reusable skills as self-contained folders:
+- `setup-component/SKILL.md` - Component/module creation
+- `write-tests/SKILL.md` - Test generation
+- `code-review/SKILL.md` - Code review assistance
+- `refactor-code/SKILL.md` - Code refactoring
+- `generate-docs/SKILL.md` - Documentation generation
+- `debug-issue/SKILL.md` - Debugging assistance
 
 ### 4. `.github/agents/` Directory
-Create specialized chat modes:
-- `architect.agent.md` - Architecture planning mode
-- `reviewer.agent.md` - Code review mode
-- `debugger.agent.md` - Debugging mode
+Always create these 4 agents:
+- `software-engineer.agent.md`
+- `architect.agent.md`
+- `reviewer.agent.md`
+- `debugger.agent.md`
+
+For each, fetch the most specific match from awesome-copilot agents. If none exists, use the generic template.
 
-**Chat Mode Attribution**: When using content from awesome-copilot chatmodes, add attribution comments:
+**Agent Attribution**: When using content from awesome-copilot agents, add attribution comments:
 ```markdown
 <!-- Based on/Inspired by: https://github.com/github/awesome-copilot/blob/main/agents/[filename].agent.md -->
 ```
 
-### 5. `.github/workflows/` Directory
+### 5. `.github/workflows/` Directory (only if user uses GitHub Actions)
+Skip this section entirely if the user answered "no" to GitHub Actions.
+
 Create Coding Agent workflow file:
 - `copilot-setup-steps.yml` - GitHub Actions workflow for Coding Agent environment setup
 
 **CRITICAL**: The workflow MUST follow this exact structure:
-- Job name MUST be `copilot-setup-steps` 
+- Job name MUST be `copilot-setup-steps`
 - Include proper triggers (workflow_dispatch, push, pull_request on the workflow file)
 - Set appropriate permissions (minimum required)
 - Customize steps based on the technology stack provided
@@ -66,9 +97,10 @@ Create Coding Agent workflow file:
 For each file, follow these principles:
 
 **MANDATORY FIRST STEP**: Always use the fetch tool to research existing patterns before creating any content:
-1. **Fetch from awesome-copilot collections**: https://github.com/github/awesome-copilot/blob/main/docs/README.collections.md
-2. **Fetch specific instruction files**: https://raw.githubusercontent.com/github/awesome-copilot/main/instructions/[relevant-file].instructions.md
-3. **Check for existing patterns** that match the technology stack
+1. **Fetch specific instruction from awesome-copilot docs**: https://github.com/github/awesome-copilot/blob/main/docs/README.instructions.md
+2. **Fetch specific agents from awesome-copilot docs**: https://github.com/github/awesome-copilot/blob/main/docs/README.agents.md
+3. **Fetch specific skills from awesome-copilot docs**: https://github.com/github/awesome-copilot/blob/main/docs/README.skills.md
+4. **Check for existing patterns** that match the technology stack
 
 **Primary Approach**: Reference and adapt existing instructions from awesome-copilot repository:
 - **Use existing content** when available - don't reinvent the wheel
@@ -77,12 +109,12 @@ For each file, follow these principles:
 - **ALWAYS add attribution comments** when using awesome-copilot content
 
 **Attribution Format**: When using content from awesome-copilot, add this comment at the top of the file:
-```markdown
+```md
 <!-- Based on/Inspired by: https://github.com/github/awesome-copilot/blob/main/instructions/[filename].instructions.md -->
 ```
 
 **Examples:**
-```markdown
+```md
 <!-- Based on: https://github.com/github/awesome-copilot/blob/main/instructions/react.instructions.md -->
 ---
 applyTo: "**/*.jsx,**/*.tsx"
@@ -92,7 +124,7 @@ description: "React development best practices"
 ...
 ```
 
-```markdown
+```md
 <!-- Inspired by: https://github.com/github/awesome-copilot/blob/main/instructions/java.instructions.md -->
 <!-- and: https://github.com/github/awesome-copilot/blob/main/instructions/spring-boot.instructions.md -->
 ---
@@ -128,20 +160,19 @@ description: "Java Spring Boot development standards"
 **Research Strategy with fetch tool:**
 1. **Check awesome-copilot first** - Always start here for ALL file types
 2. **Look for exact tech stack matches** (e.g., React, Node.js, Spring Boot)
-3. **Look for general matches** (e.g., frontend chatmodes, testing prompts, review modes)
-4. **Check awesome-copilot collections** for curated sets of related files
-5. **Adapt community examples** to project needs
+3. **Look for general matches** (e.g., frontend agents, testing skills, review workflows)
+4. **Check the docs and relevant directories directly** for related files
+5. **Prefer repo-native examples** over inventing new formats
 6. **Only create custom content** if nothing relevant exists
 
 **Fetch these awesome-copilot directories:**
 - **Instructions**: https://github.com/github/awesome-copilot/tree/main/instructions
-- **Prompts**: https://github.com/github/awesome-copilot/tree/main/prompts  
-- **Chat Modes**: https://github.com/github/awesome-copilot/tree/main/chatmodes
-- **Collections**: https://github.com/github/awesome-copilot/blob/main/docs/README.collections.md
+- **Agents**: https://github.com/github/awesome-copilot/tree/main/agents
+- **Skills**: https://github.com/github/awesome-copilot/tree/main/skills
 
-**Awesome-Copilot Collections to Check:**
+**Awesome-Copilot Areas to Check:**
 - **Frontend Web Development**: React, Angular, Vue, TypeScript, CSS frameworks
-- **C# .NET Development**: Testing, documentation, and best practices  
+- **C# .NET Development**: Testing, documentation, and best practices
 - **Java Development**: Spring Boot, Quarkus, testing, documentation
 - **Database Development**: PostgreSQL, SQL Server, and general database best practices
 - **Azure Development**: Infrastructure as Code, serverless functions
@@ -162,77 +193,73 @@ project-root/
 │   │   ├── security.instructions.md
 │   │   ├── performance.instructions.md
 │   │   └── code-review.instructions.md
-│   ├── prompts/
-│   │   ├── setup-component.prompt.md
-│   │   ├── write-tests.prompt.md
-│   │   ├── code-review.prompt.md
-│   │   ├── refactor-code.prompt.md
-│   │   ├── generate-docs.prompt.md
-│   │   └── debug-issue.prompt.md
+│   ├── skills/
+│   │   ├── setup-component/
+│   │   │   └── SKILL.md
+│   │   ├── write-tests/
+│   │   │   └── SKILL.md
+│   │   ├── code-review/
+│   │   │   └── SKILL.md
+│   │   ├── refactor-code/
+│   │   │   └── SKILL.md
+│   │   ├── generate-docs/
+│   │   │   └── SKILL.md
+│   │   └── debug-issue/
+│   │       └── SKILL.md
 │   ├── agents/
+│   │   ├── software-engineer.agent.md
 │   │   ├── architect.agent.md
 │   │   ├── reviewer.agent.md
 │   │   └── debugger.agent.md
-│   └── workflows/
+│   └── workflows/                        # only if GitHub Actions is used
 │       └── copilot-setup-steps.yml
 ```
 
 ## YAML Frontmatter Template
 
-Use this frontmatter structure for all files:
+Use this structure for all files:
 
 **Instructions (.instructions.md):**
-```yaml
+```md
 ---
-applyTo: "**/*.ts,**/*.tsx"
+applyTo: "**/*.{lang-ext}"
+description: "Development standards for {Language}"
 ---
-# Project coding standards for TypeScript and React
+# {Language} coding standards
 
-Apply the [general coding guidelines](./general-coding.instructions.md) to all code.
+Apply the repository-wide guidance from `../copilot-instructions.md` to all code.
 
-## TypeScript Guidelines
-- Use TypeScript for all new code
-- Follow functional programming principles where possible
-- Use interfaces for data structures and type definitions
-- Prefer immutable data (const, readonly)
-- Use optional chaining (?.) and nullish coalescing (??) operators
-
-## React Guidelines
-- Use functional components with hooks
-- Follow the React hooks rules (no conditional hooks)
-- Use React.FC type for components with children
-- Keep components small and focused
-- Use CSS modules for component styling
+## General Guidelines
+- Follow the project's established conventions and patterns
+- Prefer clear, readable code over clever abstractions
+- Use the language's idiomatic style and recommended practices
+- Keep modules focused and appropriately sized
 
+<!-- Adapt the sections below to match the project's specific technology choices and preferences -->
 ```
 
-**Prompts (.prompt.md):**
-```yaml
+**Skills (SKILL.md):**
+```md
 ---
-agent: 'agent'
-model: Claude Sonnet 4
-tools: ['githubRepo', 'codebase']
-description: 'Generate a new React form component'
+name: {skill-name}
+description: {Brief description of what this skill does}
 ---
-Your goal is to generate a new React form component based on the templates in #githubRepo contoso/react-templates.
 
-Ask for the form name and fields if not provided.
+# {Skill Name}
 
-Requirements for the form:
-* Use form design system components: [design-system/Form.md](../docs/design-system/Form.md)
-* Use `react-hook-form` for form state management:
-* Always define TypeScript types for your form data
-* Prefer *uncontrolled* components using register
-* Use `defaultValues` to prevent unnecessary rerenders
-* Use `yup` for validation:
-* Create reusable validation schemas in separate files
-* Use TypeScript types to ensure type safety
-* Customize UX-friendly validation rules
+{One sentence describing what this skill does. Always follow the repository's established patterns.}
 
+Ask for {required inputs} if not provided.
+
+## Requirements
+- Use the existing design system and repository conventions
+- Follow the project's established patterns and style
+- Adapt to the specific technology choices of this stack
+- Reuse existing validation and documentation patterns
 ```
 
-**Chat Modes (.agent.md):**
-```yaml
+**Agents (.agent.md):**
+```md
 ---
 description: Generate an implementation plan for new features or refactoring existing code.
 tools: ['codebase', 'web/fetch', 'findTestFiles', 'githubRepo', 'search', 'usages']
@@ -248,43 +275,48 @@ The plan consists of a Markdown document that describes the implementation plan,
 * Requirements: A list of requirements for the feature or refactoring task.
 * Implementation Steps: A detailed list of steps to implement the feature or refactoring task.
 * Testing: A list of tests that need to be implemented to verify the feature or refactoring task.
-
 ```
 
 ## Execution Steps
 
-1. **Analyze the provided technology stack**
-2. **Create the directory structure**
-3. **Generate main copilot-instructions.md with project-wide standards**
-4. **Create language-specific instruction files using awesome-copilot references**
-5. **Generate reusable prompts for common development tasks**
-6. **Set up specialized chat modes for different development scenarios**
-7. **Create the GitHub Actions workflow for Coding Agent** (`copilot-setup-steps.yml`)
-8. **Validate all files follow proper formatting and include necessary frontmatter**
+1. **Gather project information** - Ask the user for technology stack, project type, and development style if not provided
+2. **Research awesome-copilot patterns**:
+   - Use the fetch tool to explore awesome-copilot directories
+   - Check instructions: https://github.com/github/awesome-copilot/tree/main/instructions
+   - Check agents: https://github.com/github/awesome-copilot/tree/main/agents (especially for matching expert agents)
+   - Check skills: https://github.com/github/awesome-copilot/tree/main/skills
+   - Document all sources for attribution comments
+3. **Create the directory structure**
+4. **Generate main copilot-instructions.md** with project-wide standards
+5. **Create language-specific instruction files** using awesome-copilot references with attribution
+6. **Generate reusable skills** tailored to project needs
+7. **Set up specialized agents**, fetching from awesome-copilot where applicable (especially for expert engineer agents matching the tech stack)
+8. **Create the GitHub Actions workflow for Coding Agent** (`copilot-setup-steps.yml`) — skip if user does not use GitHub Actions
+9. **Validate** all files follow proper formatting and include necessary frontmatter
 
 ## Post-Setup Instructions
 
 After creating all files, provide the user with:
 
 1. **VS Code setup instructions** - How to enable and configure the files
-2. **Usage examples** - How to use each prompt and chat mode
+2. **Usage examples** - How to use each skill and agent
 3. **Customization tips** - How to modify files for their specific needs
 4. **Testing recommendations** - How to verify the setup works correctly
 
 ## Quality Checklist
 
 Before completing, verify:
-- [ ] All files have proper YAML frontmatter
+- [ ] All authored Copilot markdown files have proper YAML frontmatter where required
 - [ ] Language-specific best practices are included
 - [ ] Files reference each other appropriately using Markdown links
-- [ ] Prompts include relevant tools and variables
+- [ ] Skills and agents include relevant descriptions; include MCP/tool-related metadata only when the target Copilot environment actually supports or requires it
 - [ ] Instructions are comprehensive but not overwhelming
 - [ ] Security and performance considerations are addressed
 - [ ] Testing guidelines are included
 - [ ] Documentation standards are clear
 - [ ] Code review standards are defined
 
-## Workflow Template Structure
+## Workflow Template Structure (only if GitHub Actions is used)
 
 The `copilot-setup-steps.yml` workflow MUST follow this exact format and KEEP IT SIMPLE:
 
PATCH

echo "Gold patch applied."
