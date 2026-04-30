# Update the Effect skill (`.opencode/skills/effect/SKILL.md`)

You are working in the `opencode` repository. The agent skill at
`.opencode/skills/effect/SKILL.md` is the file every agent reads when it
needs to write or modify Effect-framework TypeScript code in this repo.

The current skill is too vague. Its `description` is a placeholder, and its
body only tells the reader to "use the explore agent" and "do not answer
from memory" without naming any of the concrete API patterns this codebase
actually uses. As a result, agents fall back on Effect v2/v3 examples from
training data and write code that does not match this project's house style.

Your job is to **rewrite `.opencode/skills/effect/SKILL.md` so it captures
the rules and conventions an Effect-aware agent must follow when working
in this repo.** Keep the YAML frontmatter (`name: effect`, plus a
`description:`) and the `# Effect` heading. Replace the rest with content
that meets the requirements below.

## What the skill must convey

### Frontmatter

The `description:` field must be replaced with a short line that describes
what the skill is *for in this repo* — i.e. working with this repo's
Effect TypeScript code — rather than the generic "Answer questions about
the Effect framework" placeholder.

### Source of truth

The repo targets the in-progress beta line of Effect referred to as
**Effect v4**, also known by its source repository name **effect-smol**
(`https://github.com/Effect-TS/effect-smol`). Older Effect v2/v3 examples
from blog posts, package memory, or training data must not be used.

The skill must:

- Name **Effect v4** explicitly so readers do not fall back to v2/v3 patterns.
- Refer to the local clone path **`.opencode/references/effect-smol`** as
  the place to look up exact APIs, examples, tests, and naming patterns.
  Mention that if it is missing, the agent should clone effect-smol there
  (in the project, not inside the skill folder).
- Tell readers to also look at neighboring repo code for local house style
  before introducing new patterns.

### Concrete API rules

The skill must spell out the concrete Effect API patterns this codebase
expects. At a minimum:

- Use **`Effect.gen(function* () { ... })`** for composing multi-step
  workflows.
- Use **`Effect.fn("Name")`** (the traced/named-effect helper) — and its
  untraced sibling `Effect.fnUntraced(...)` — for reusable service
  methods and important workflows that should appear in traces.
- Prefer Effect **`Schema`** for API and domain data shapes. Use branded
  schemas for ID types, and **`Schema.TaggedErrorClass`** for typed
  domain errors when adding new error surfaces.
- Keep HTTP handlers thin: decode input, read request context, call
  services, map transport errors. Business rules belong in services, not
  in handlers.
- Prefer Effect-aware platform abstractions and dependencies inside Effect
  service code, instead of dropping down to ad hoc promises when the
  surrounding code does not.
- Keep layer composition explicit; avoid broad hidden provisioning that
  hides missing dependencies.
- In tests, prefer the repo's existing Effect test helpers and live tests
  for filesystem, git, child-process, lock, or timing behavior.

### Bans

The skill must explicitly forbid introducing **`any`**, **non-null
assertions**, unchecked casts, or older Effect APIs purely to satisfy the
type checker.

It must also restate the existing rule: **do not answer from memory** —
verify against `.opencode/references/effect-smol` or nearby repo code first.

## What you must NOT do

- Do not rename or move the file. It must remain at
  `.opencode/skills/effect/SKILL.md`.
- Do not change the `name: effect` line in the frontmatter.
- Do not delete the YAML frontmatter or the top-level `# Effect` heading.

## Notes

- This is a documentation/skill-authoring task. There are no Effect-code
  changes required in this task.
- You can reference the repo's existing `AGENTS.md` files for the house
  style on Effect (`packages/opencode/AGENTS.md` already documents many of
  the same patterns); the goal of this skill is to surface those rules in
  the place agents actually look when the topic is Effect.
