# Add skills directory and document the skills system

## Task

Create a `skills/` directory to host agent "skills" — progressively-disclosed instructions that teach AI coding agents how to handle specific workflows in the codebase. Skills use YAML frontmatter for metadata and markdown body for detailed instructions.

## Required Changes

### 1. Create the skills directory structure

Create two initial skills:

**`skills/inference-server/SKILL.md`** — Document how to start and test the vLLM-based inference server:
- Use the `inference` entry point (not `vllm serve` directly)
- Show config file usage with `@` syntax
- Document custom endpoints (`/v1/chat/completions/tokens`, `/update_weights`, `/load_lora_adapter`, `/init_broadcaster`)
- Include a curl example for testing
- List key source files

**`skills/toml-config/SKILL.md`** — Document how to write and use TOML configs:
- Explain the `@` syntax for loading configs
- Document CLI override syntax
- Explain boolean flag handling (no value needed for true, `--no-` prefix for false)
- Document TOML structure (top-level fields before sections)
- Document config inheritance with `toml_files`
- List available commands with their config classes
- List key source files

Both SKILL.md files must have YAML frontmatter with `name:` and `description:` fields.

### 2. Create the symlink

Create a symlink from `.claude/skills` pointing to `../skills` so Claude Code picks up the skills automatically.

### 3. Update AGENTS.md

Add a new "Skills" section to AGENTS.md that:
- Explains that skills live in `skills/` and are symlinked to `.claude/skills/`
- Documents that skills teach agents specific workflows
- States that agents are responsible for maintaining skills when workflows change
- References the `toml-config` skill from the CLI Usage section (replace the detailed bullet points with a reference to the skill)

## Files to Modify

- Create `skills/inference-server/SKILL.md`
- Create `skills/toml-config/SKILL.md`
- Create `.claude/skills` (symlink to `../skills`)
- Update `AGENTS.md`

## Notes

- The skills system is new — there are no existing skills to reference as examples
- Use the existing CLI documentation in AGENTS.md as source material for the toml-config skill
- The inference-server skill documents knowledge not currently captured in AGENTS.md
