# Add unified agent skill: add-content

Source: [debs-obrien/debbie.codes#539](https://github.com/debs-obrien/debbie.codes/pull/539)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/add-content/SKILL.md`
- `.agents/skills/add-content/references/blog.md`
- `.agents/skills/add-content/references/environment.md`
- `.agents/skills/add-content/references/podcast.md`
- `.agents/skills/add-content/references/video.md`

## What to add / change

## Unified Content Skill

Replaces the single-purpose `add-youtube-video` skill with a unified `add-content` skill in `.agents/skills/add-content/` that handles **videos, podcasts, and blog posts**.

### Architecture

Follows the [progressive disclosure pattern](https://skills.sh/anthropics/skills/skill-creator) from the Anthropic skill-creator guide:

```
.agents/skills/add-content/
├── SKILL.md                     # Core workflow + routing (75 lines)
└── references/
    ├── environment.md           # Shell env, git, dev server, PR creation
    ├── video.md                 # YouTube extraction + frontmatter schema
    ├── podcast.md               # Podcast extraction + Cloudinary upload + frontmatter
    └── blog.md                  # Blog content extraction + canonical URL + frontmatter
```

- **SKILL.md** (always loaded): Determines content type, routes to the right reference file, defines the core workflow
- **references/** (loaded on demand): Only the relevant content-type file + environment file are loaded per task

### What each content type does

| | Video | Podcast | Blog |
|---|---|---|---|
| **Source** | YouTube | Podcast platforms | Blog platforms |
| **Browser extraction** | ✅ playwright-cli | ✅ playwright-cli | ✅ playwright-cli |
| **Image handling** | YouTube thumbnail URL | Extract → Cloudinary MCP upload | No image |
| **Body content** | None | None | Full markdown extraction |
| **Canonical URL** | No | No | Yes (if hosted elsewhere) |
| **Dev server verify*

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
