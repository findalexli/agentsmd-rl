# feat(skills): add computer-vision-expert (SOTA 2026: YOLO26, SAM 3)

Source: [sickn33/antigravity-awesome-skills#58](https://github.com/sickn33/antigravity-awesome-skills/pull/58)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/computer-vision-expert/SKILL.md`

## What to add / change

# Pull Request Description

Summary: Added a new foundational skill for Computer Vision updated to SOTA 2026 standards. 
Skill Added: computer-vision-expert

This skill bridges classical computer vision (calibration, geometry) with the latest foundational models released recently. Key inclusions:
- **YOLO26**: Integration of the newest real-time NMS-free detection architecture.
- **SAM 3**: Support for text-guided promptable segmentation and 3D reconstruction.
- **VLMs**: Patterns for Visual Grounding and VQA using models like Florence-2 and Qwen2-VL.
- **Standards**: Complies with the universal skill format, including mandatory sections.

## Quality Bar Checklist

**All items must be checked before merging.**

- [x] **Standards**: I have read the quality bar and security guardrails documentation.
- [x] **Metadata**: The file frontmatter is valid (checked with local validation script).
- [x] **Risk Label**: Assigned as safe.
- [x] **Triggers**: The "When to use" section is clear and specific.
- [x] **Security**: This is a general-purpose vision skill.
- [x] **Local Test**: I have verified the skill works locally.
- [x] **Credits**: N/A (Original contribution based on 2026 SOTA research).

## Type of Change

- [x] New Skill (Feature)
- [ ] Documentation Update
- [ ] Infrastructure

## Screenshots (if applicable)
N/A

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
