# Add a `make-pr` Skill to the Remix Repository

The Remix monorepo at `/workspace/remix` has an agent instruction system based on reusable skills. Each skill lives in a `skills/<name>/SKILL.md` file and is referenced in `AGENTS.md`. There is already one skill called `supersede-pr` for replacing PRs.

## Task

Create a new reusable skill called **make-pr** that teaches agents how to create GitHub pull requests with clear, well-structured descriptions.

### Requirements

**1. Create the skill definition file**

Create `skills/make-pr/SKILL.md` with YAML frontmatter containing the fields `name` (set to `make-pr`) and a `description` field explaining the skill's purpose. The body should include:

- An **Overview** section explaining that the skill produces high-signal PR descriptions with sparse headings, focusing on problem/feature explanation, context links, and code examples.
- A numbered **Workflow** section with these steps:
  1. **Gather context**: capture what changed, why, and who it affects; find related issues/PRs.
  2. **Draft the PR body**: start with 1-2 intro paragraphs containing bullets for the feature/issue addressed, key behavior/API changes, and expected impact. For large changes, expand to 3-4 paragraphs with background context and related links.
  3. **Add usage examples**: for new features, include a comprehensive usage snippet; for improvements or replacements, include before/after examples.
  4. **Exclude redundant sections**: do not add `Validation`, `Testing`, or other process sections that are implicit in PR workflow; avoid boilerplate.
  5. **Create the PR**: save the body to a temp file and run `gh pr create --base main --head <branch> --title "<title>" --body-file <file>`.
- A **Body Template** section showing a markdown template with placeholders for intro paragraphs, bullet points, and code example slots (with `ts` language tags for TypeScript snippets).

**2. Register the skill in AGENTS.md**

Edit `AGENTS.md` to add the `make-pr` skill to the "Available skills" list, using the same format as the existing `supersede-pr` entry: a dash-bulleted line with the skill name in bold, a one-sentence description, and the file path in parentheses. The make-pr entry should appear after the supersede-pr entry.

**3. Create the OpenAI agent interface config**

Create `skills/make-pr/agents/openai.yaml` with an `interface` key containing:
- `display_name`: a human-readable name for the skill (derive this naturally from the skill name)
- `short_description`: a one-line summary of what the skill does
- `default_prompt`: an invocation prompt that references `$make-pr`

### Reference

Study the existing `skills/supersede-pr/SKILL.md` file for the expected structure, frontmatter format, and writing style. The make-pr skill should feel like a sibling to supersede-pr: same tone, same level of detail, same conventions for headings and formatting.

### Context

This task is purely about authoring markdown and YAML files — no code changes are needed. The skill provides instructions to AI agents, not executable code.
