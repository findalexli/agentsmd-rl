# feat: Add comprehensive `mermaid-diagram` skill and references

Source: [wanshuiyin/Auto-claude-code-research-in-sleep#43](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/pull/43)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/mermaid-diagram/SKILL.md`

## What to add / change

This feature can serve as an _alternative_ to `paper-illustration` without `GEMINI_API_KEY`, which runs much faster.

- A new skill for generating **Mermaid diagrams** based on user requirements, supporting 20+ diagram types with syntax verification, file output, and strict visual review guidance.
- Enables advanced diagram workflows, academic math support, and integration details for robust and accurate diagram generation in various contexts.

Reference: [thdk/mermaid-skill](https://github.com/thdk/mermaid-skill)

---

Example use:
```
/mermaid-diagram 'Create a diagram of ViT-B-16'
```

Output files:
```
figures
├── vit-b-16.md
├── vit-b-16.mmd
└── vit-b-16.png
```

Output diagram:
```mermaid
flowchart TD
    inputImg["Input Image<br/>224 x 224 x 3"]

    patchSplit["Split into Patches<br/>14 x 14 grid of 16 x 16 patches"]
    inputImg --> patchSplit

    flatten["Flatten Patches<br/>196 patches, each 768-dim"]
    patchSplit --> flatten

    linearEmbed["Linear Embedding"]
    flatten --> linearEmbed

    patchTokens["Patch Tokens<br/>196 x 768"]
    linearEmbed --> patchTokens

    clsToken["Prepend CLS Token"]
    patchTokens --> clsToken

    tokens["Token Sequence<br/>197 x 768"]
    clsToken --> tokens

    posEmbed["Add Position Embeddings"]
    tokens --> posEmbed

    encodedTokens["Encoded Tokens<br/>197 x 768"]
    posEmbed --> encodedTokens

    %% Transformer Encoder (x12)
    subgraph encoderBlock ["Transform

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
