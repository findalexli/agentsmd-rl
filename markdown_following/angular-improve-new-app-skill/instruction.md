# Improve the `angular-new-app` SKILL.md

The repository ships an authored skill that teaches an AI agent how to scaffold a new Angular application:

```
skills/dev-skills/angular-new-app/SKILL.md
```

Maintainers have filed a documentation-quality issue against this file. Several improvements are needed. Edit **only** that file, in place. Do not modify any other file in the repository.

## Issues to address

### 1. Typo in the frontmatter description

The YAML frontmatter at the top of the file currently says the skill should be used **`whenver`** a user wants to create a new application. Correct the misspelling so the description reads `… should be used whenever a user wants to create a new Angular application …`.

### 2. Redundant duplicate persona intro

Just below the `# Angular New App` heading there are **two separate "You are an expert…" sentences** that say overlapping things:

> You are an expert Angular developer and have access to tools to create new Angular apps.
>
> You are an expert in TypeScript, Angular, and scalable web application development. You write functional, maintainable, performant, and accessible code following Angular and TypeScript best practices.

Consolidate these into a single persona paragraph. The first short line — *"You are an expert Angular developer and have access to tools to create new Angular apps."* — must no longer appear as a standalone sentence; the "have access to tools to create new Angular apps" idea should be folded into the longer paragraph so the persona is described once, not twice.

### 3. Step 2 is missing commonly useful `ng new` flags

Step 2 (the `npx ng new …` step) currently does not document any of the flags users typically want. Add a section in step 2 that lists these commonly useful flags, with a one-line description of each, in code font:

- `--style=scss|css|less` — stylesheet format
- `--routing` — add routing module
- `--ssr` — enable server-side rendering
- `--prefix=<prefix>` — component selector prefix
- `--skip-tests` — only if the user explicitly requests it

### 4. Step 4 is missing several common generators

Step 4 lists the Angular CLI commands for generating components, services, pipes, directives, and interfaces, but is missing five other generators that agents routinely need. Add bullets for each of the following, matching the existing wording pattern (`To generate <plurals>, use the Angular CLI \`npx ng generate <kind> <kind-name>\``):

- `npx ng generate guard <guard-name>`
- `npx ng generate interceptor <interceptor-name>`
- `npx ng generate resolver <resolver-name>`
- `npx ng generate enum <enum-name>`
- `npx ng generate class <class-name>`

### 5. Capitalize "AI configuration"

In step 2 the sentence currently begins **`Load the contents of that ai configuration …`**. The acronym should be capitalized: change it to **`AI configuration`**. While you are there, the sentence reads slightly more naturally as "This will help you generate code …" rather than "This will help you to generate code …" — feel free to tighten that wording too.

## Constraints

- Edit only `skills/dev-skills/angular-new-app/SKILL.md`. Do not touch any other file.
- Preserve the existing structure: the YAML frontmatter (including the `name: angular-new-app` field), the `# Angular New App` heading, the numbered steps, and every existing bullet point already in the file. Your edits should *add to* and *rephrase* — never delete the existing component / service / pipe / directive / interface generator bullets, the existing `ng new` command, or the tailwind step.
- Follow the documentation conventions used elsewhere in this repository (`.agent/skills/adev-writing-guide/SKILL.md`):
  - **Conciseness** — one idea per sentence; no redundant restatements.
  - **Code font** — wrap CLI flags, command names, and option values in backticks.
  - **Consistent terminology** — match the wording and casing of the already-listed entries when adding new ones.
  - **Second person** — keep the existing "you" voice.
