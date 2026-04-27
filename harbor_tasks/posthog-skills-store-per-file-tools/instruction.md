# Teach the `skills-store` skill the per-file edit primitives

## Background

The PostHog skills MCP API recently grew several primitives that let callers
edit a stored skill *surgically* instead of round-tripping the whole skill on
every update:

| Tool | What it does |
|---|---|
| `posthog:skill-file-create` | Add one bundled file to a skill (publishes a new immutable version). |
| `posthog:skill-file-delete` | Remove one bundled file from a skill. |
| `posthog:skill-file-rename` | Rename one bundled file (move without rewriting content). |
| `posthog:skill-update` (with `edits`) | Body-level incremental find/replace — `edits: [{ "old": "...", "new": "..." }]`. |
| `posthog:skill-update` (with `file_edits`) | Per-file find/replace inside one bundled file — `file_edits: [{ "path": "...", "edits": [{ "old": "...", "new": "..." }] }]`. |

The local-allowed-tools form of those names — used in agent skill frontmatter
under `allowed-tools:` — is `mcp__posthog__skill-file-create`,
`mcp__posthog__skill-file-delete`, and `mcp__posthog__skill-file-rename`.

## The problem

The agent-facing skill **`products/llm_analytics/skills/skills-store/SKILL.md`**
is what other coding agents read when we point them at "the PostHog skills
store". It is the canonical entry point for teaching agents how to use the
skills MCP API.

Today that file only documents the bulk-replace shape of `posthog:skill-update`
(full `body` + replace-all `files`). It does not mention:

- the new per-file CRUD tools (`skill-file-create` / `-delete` / `-rename`)
- the body `edits` payload (incremental find/replace on the body)
- the per-file `file_edits` payload (incremental find/replace inside one
  bundled file)

An agent reading the skill today still reaches for the dangerous bulk-replace
primitive even though safer ones exist. We need the documentation to point
agents at the surgical primitives.

The skill also documents a small **local /phs bridge skill** at the bottom of
the file — that local skill's `allowed-tools` frontmatter line is the
allowlist of MCP tools the bridge can route to. Today it only lists the
old set, so even an agent that *wants* to use a per-file tool through the
bridge cannot.

## What you need to do

Update **only** `products/llm_analytics/skills/skills-store/SKILL.md` so that:

1. **The "Available tools" table** at the top of the skill body lists the
   three new tools (`posthog:skill-file-create`, `posthog:skill-file-delete`,
   `posthog:skill-file-rename`) alongside the existing entries, with a short
   purpose blurb for each. The existing `posthog:skill-update` row's purpose
   blurb is also stale — its description should reflect that updates now
   accept `body`, `edits`, or `file_edits`.

2. **The "Updating a skill" section** is rewritten so that the recommended
   path is the most-surgical primitive available, not bulk replace. Cover
   the three editing primitives with concrete worked JSON examples, in this
   order of preference:
   - body `edits` (incremental find/replace on the body)
   - per-file `file_edits` (incremental find/replace inside one bundled file,
     with no round-trip of the other files)
   - the per-file CRUD tools (`skill-file-create` / `-delete` / `-rename`)
     for atomic add/remove/rename

   Bulk-replace via `files` should be reframed as an opt-in for intentional
   bundle wipes — explicitly *not* the default update shape. Specifically,
   the original phrasing
   > "If you pass `files`, they replace the previous version's file set;
   > if you omit `files`, they're carried forward"
   should not survive — it implies the bulk-replace path is the normal one.

3. **The local /phs bridge skill** (the markdown block near the bottom of
   the file showing the bridge's frontmatter and body) needs the new tools
   added to its `allowed-tools:` line. The bridge's `allowed-tools` value
   is one comma-separated line and must include
   `mcp__posthog__skill-file-create`, `mcp__posthog__skill-file-delete`,
   and `mcp__posthog__skill-file-rename` alongside the tools it already
   lists. Also add a short section to the bridge body that points the
   bridge at the surgical primitives.

## Constraints

- This is a documentation-only change. Do not modify any other file. Do not
  change the skill's top-level frontmatter `name:` (it must remain
  `skills-store`) or `description:`.
- The whole `SKILL.md` must stay under 500 lines — the
  `.agents/skills/writing-skills/` convention requires bodies that size,
  with detailed material moved into bundled `references/` or `scripts/`
  if needed. (You shouldn't need bundled files here.)
- The repo's markdown style is "semantic line breaks, no hard wrapping" —
  match the existing surrounding paragraphs.
- Use American English spelling throughout (per the repo's AGENTS.md).
- Match the existing skill's tone: describe the workflow and reasoning,
  not a rigid script. Trust the agent to adapt.

## Where to find what you need

- The skill you are editing: `products/llm_analytics/skills/skills-store/SKILL.md`
- Repo-wide markdown conventions: `AGENTS.md` (root)
- Skill-authoring conventions: `.agents/skills/writing-skills/SKILL.md`
- The pre-existing `posthog:skill-update` example in the same file is a
  good shape to mimic for the new JSON examples.
