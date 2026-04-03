#!/usr/bin/env bash
set -euo pipefail

cd /workspace/angular

# Idempotent: skip if already applied
if grep -q 'agent-skills' adev/src/app/routing/navigation-entries/index.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Create agent-skills.md documentation page
mkdir -p adev/src/content/ai
cat > adev/src/content/ai/agent-skills.md <<'AGENTSKILLS'
# Agent Skills

Agent Skills are specialized, domain-specific instructions and capabilities designed for AI agents like Gemini CLI. These skills provide architectural guidance, generate idiomatic Angular code, and help scaffold new projects using modern best practices.

By using Agent Skills, you can ensure that the AI agent you are working with has the most up-to-date information about Angular's conventions, reactivity models (like Signals), and project structure.

## Available Skills

The Angular team maintains a collection of official skills that are regularly updated to stay in sync with the latest framework improvements.

| Skill                   | Description                                                                                                                                                                                                                                                                                       |
| :---------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **`angular-developer`** | Generates Angular code and provides architectural guidance. Useful for creating components, services, or obtaining best practices on reactivity (signals, linkedSignal, resource), forms, dependency injection, routing, SSR, accessibility (ARIA), animations, styling, testing, or CLI tooling. |
| **`angular-new-app`**   | Creates a new Angular app using the Angular CLI. Provides important guidelines for effectively setting up and structuring a modern Angular application.                                                                                                                                           |

## Using Agent Skills

Agent Skills are designed to be used with agentic coding tools like [Gemini CLI](https://geminicli.com/docs/cli/skills/), [Antigravity](https://antigravity.google/docs/skills) and more. Activating a skill loads the specific instructions and resources needed for that task.

To use these skills in your own environment you may follow the instructions for your specific tool or use a community tool like [skills.sh](https://skills.sh/).

```bash
npx skills add https://github.com/angular/skills
```
AGENTSKILLS

# Create skills/dev-skills/README.md
mkdir -p skills/dev-skills
cat > skills/dev-skills/README.md <<'SKILLSREADME'
# Angular Skills

The Angular skills are designed to help coding agents create applications aligned with the latest versions of Angular, best practices, new features and manage Angular applications effectively. These skills provide architectural guidance, generate idiomatic Angular code, and help scaffold new projects using modern best practices.

## Available Skills

- **`angular-developer`**: Generates Angular code and provides architectural guidance. Useful for creating components, services, or obtaining best practices on reactivity (signals, linkedSignal, resource), forms, dependency injection, routing, SSR, accessibility (ARIA), animations, styling, testing, or CLI tooling.
- **`angular-new-app`**: Creates a new Angular app using the Angular CLI. Provides important guidelines for effectively setting up and structuring a modern Angular application.

## Contributions

We welcome contributions to the Angular agent skills. If you would like to contribute to the skills, please make the updates directly in `angular/angular` repository, and to that repository will be output here as a part of our infrastructure setup.

### Feedback & Issues

If you encounter a bug, have feedback, or want to suggest an improvement to the skills, please file an issue in the [angular/angular](https://github.com/angular/angular/issues/new?template=3-docs-bug.yaml) issue tracker. Providing detailed context will help us address your feedback effectively.

### Features & Changes (Pull Requests)

We also accept pull requests for new features, updates, or bug fixes for the skills:

1. Make your changes within the `skills/dev-skills/` directory.
2. Follow the standard Angular [Commit Guidelines](https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md) and [Coding Standards](https://github.com/angular/angular/blob/main/contributing-docs/coding-standards.md).
3. Submit a Pull Request to the main `angular/angular` repository.
SKILLSREADME

# Update overview.md — add agent-skills pill
sed -i '/<docs-pill href="ai\/develop-with-ai" title="LLM prompts and IDE setup"\/>/a\  <docs-pill href="ai/agent-skills" title="Agent Skills"/>' adev/src/content/ai/overview.md

# Update navigation-entries/index.ts
# 1. Remove status: 'new' from "Build with AI" parent
# 2. Replace "Design Patterns" entry with "Agent Skills" entry (with status: 'new')
# 3. Add "Design Patterns" after "Angular AI Tutor"
python3 -c "
import re

path = 'adev/src/app/routing/navigation-entries/index.ts'
with open(path) as f:
    content = f.read()

# Remove status: 'new' from 'Build with AI' section
content = content.replace(
    \"\"\"label: 'Build with AI',
    status: 'new',\"\"\",
    \"\"\"label: 'Build with AI',\"\"\"
)

# Replace Design Patterns entry with Agent Skills entry
content = content.replace(
    \"\"\"      {
        label: 'Design Patterns',
        path: 'ai/design-patterns',
        contentPath: 'ai/design-patterns',
      },\"\"\",
    \"\"\"      {
        label: 'Agent Skills',
        path: 'ai/agent-skills',
        contentPath: 'ai/agent-skills',
        status: 'new',
      },\"\"\"
)

# Add Design Patterns entry after Angular AI Tutor
content = content.replace(
    \"\"\"      {
        label: 'Angular AI Tutor',
        path: 'ai/ai-tutor',
        contentPath: 'ai/ai-tutor',
      },\"\"\",
    \"\"\"      {
        label: 'Angular AI Tutor',
        path: 'ai/ai-tutor',
        contentPath: 'ai/ai-tutor',
      },
      {
        label: 'Design Patterns',
        path: 'ai/design-patterns',
        contentPath: 'ai/design-patterns',
      },\"\"\"
)

with open(path, 'w') as f:
    f.write(content)
"

echo "Patch applied successfully."
