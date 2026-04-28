# Improve/skill review optimization

Source: [zjunlp/SkillNet#9](https://github.com/zjunlp/SkillNet/pull/9)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `experiments/src/skills/alfworld/alfworld-appliance-navigator/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-appliance-preparer/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-clean-object/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-device-operator/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-environment-scanner/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-heat-object-with-appliance/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-inventory-management/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-locate-target-object/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-object-cooler/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-object-heater/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-object-locator/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-object-state-inspector/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-object-state-modifier/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-object-storer/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-object-transporter/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-receptacle-closer/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-receptacle-finder/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-receptacle-navigator/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-search-pattern-executor/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-search-verifier/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-storage-explorer/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-task-verifier/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-temperature-regulator/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-tool-locator/SKILL.md`
- `experiments/src/skills/alfworld/alfworld-tool-user/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-ambiguous-action-resolution/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-animal-identifier/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-circuit-builder/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-circuit-connector/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-conditional-focus-executor/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-conditional-placer/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-container-inspector/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-container-item-retriever/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-container-relocator/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-container-transfer/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-controlled-waiting/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-device-activator/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-environment-isolation/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-growth-focuser/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-instruction-reader/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-inventory-focus/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-inventory-manager/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-item-fetcher/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-liquid-pourer/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-living-entity-identifier/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-material-classifier/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-measurement-taker/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-mixture-creator/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-object-classifier/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-object-focuser/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-object-locator/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-object-placer/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-object-retriever/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-object-selector/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-process-monitor/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-process-pauser/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-recipe-retriever/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-room-explorer/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-room-navigator/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-room-scanner/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-substance-cooler/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-substance-fetcher/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-substance-preparator/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-target-locator/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-task-focuser/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-task-parser/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-threshold-evaluator/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-tool-user/SKILL.md`
- `experiments/src/skills/scienceworld/scienceworld-tool-validator/SKILL.md`
- `experiments/src/skills/scienceworld/task-completion-focus/SKILL.md`
- `experiments/src/skills/webshop/webshop-attribute-verifier/SKILL.md`
- `experiments/src/skills/webshop/webshop-initial-search/SKILL.md`
- `experiments/src/skills/webshop/webshop-product-detail-check/SKILL.md`
- `experiments/src/skills/webshop/webshop-product-evaluator/SKILL.md`
- `experiments/src/skills/webshop/webshop-product-search/SKILL.md`
- `experiments/src/skills/webshop/webshop-product-selector/SKILL.md`
- `experiments/src/skills/webshop/webshop-purchase-executor/SKILL.md`
- `experiments/src/skills/webshop/webshop-purchase-initiator/SKILL.md`
- `experiments/src/skills/webshop/webshop-query-interpreter/SKILL.md`
- `experiments/src/skills/webshop/webshop-result-filter/SKILL.md`
- `experiments/src/skills/webshop/webshop-search-executor/SKILL.md`

## What to add / change

Hullo @zjunlp 👋

I ran your skills through `tessl skill review` at work and found some targeted improvements. Here are the ten most improved:

<img width="1312" height="1290" alt="score_card" src="https://github.com/user-attachments/assets/70c5d40b-a87a-4673-9833-7971ef78ef9c" />

Here's the full before/after:

| Skill | Before | After | Change |
|-------|--------|-------|--------|
| alfworld-tool-user | 17% | 85% | +68% |
| scienceworld-inventory-focus | 25% | 85% | +60% |
| scienceworld-task-focuser | 17% | 75% | +58% |
| alfworld-inventory-management | 35% | 85% | +50% |
| alfworld-object-storer | 35% | 85% | +50% |
| alfworld-task-verifier | 35% | 85% | +50% |
| scienceworld-measurement-taker | 35% | 85% | +50% |
| scienceworld-threshold-evaluator | 35% | 85% | +50% |
| webshop-attribute-verifier | 50% | 100% | +50% |
| scienceworld-object-selector | 45% | 85% | +40% |
| scienceworld-tool-validator | 35% | 75% | +40% |
| alfworld-object-locator | 52% | 85% | +33% |
| alfworld-clean-object | 67% | 100% | +33% |
| alfworld-device-operator | 67% | 100% | +33% |
| alfworld-object-state-inspector | 67% | 100% | +33% |
| scienceworld-ambiguous-action-resolution | 52% | 85% | +33% |
| scienceworld-instruction-reader | 67% | 100% | +33% |
| scienceworld-living-entity-identifier | 68% | 100% | +32% |
| scienceworld-animal-identifier | 57% | 85% | +28% |
| alfworld-heat-object-with-appliance | 75% | 100% | +25% |
| alfworld-appliance-preparer | 75% | 1

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
