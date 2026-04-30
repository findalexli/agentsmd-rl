# feat(agents): add 8 WFGY semantic reasoning sub-agents

Source: [qdhenry/Claude-Command-Suite#34](https://github.com/qdhenry/Claude-Command-Suite/pull/34)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/wfgy/README.md`
- `.claude/agents/wfgy/boundary-guardian.md`
- `.claude/agents/wfgy/cognitive-debugger.md`
- `.claude/agents/wfgy/decision-navigator.md`
- `.claude/agents/wfgy/knowledge-mapper.md`
- `.claude/agents/wfgy/logic-synthesizer.md`
- `.claude/agents/wfgy/memory-curator.md`
- `.claude/agents/wfgy/reasoning-validator.md`
- `.claude/agents/wfgy/semantic-architect.md`

## What to add / change

## Summary

- Adds 8 new strongly-typed YAML-based agents implementing the WFGY (WanFaGuiYi) semantic reasoning system
- Each agent specializes in a specific aspect of semantic reasoning, memory management, and validation
- Designed to work together as a comprehensive ecosystem for enhanced AI reasoning

## New Agents

1. **semantic-architect** (Atlas) - Builds and manages persistent semantic memory trees
2. **reasoning-validator** (Euclid) - Validates logic chains through mathematical formulas  
3. **boundary-guardian** (Sentinel) - Prevents hallucination by monitoring knowledge boundaries
4. **memory-curator** (Mnemonic) - Optimizes and maintains semantic memory structures
5. **logic-synthesizer** (Synthesis) - Explores parallel solution paths and synthesizes outcomes
6. **decision-navigator** (Navigator) - Guides strategic decision-making with semantic validation
7. **knowledge-mapper** (Cartographer) - Creates knowledge graphs and maps concept relationships
8. **cognitive-debugger** (Debugger) - Diagnoses and repairs reasoning failures

## Key Features

- **Strongly Typed Format**: Each agent uses YAML configuration with explicit types and validation
- **Proper Headers**: All agents include front-matter with name, description, tools, and model specifications
- **Unique Personas**: Each agent has a distinct personality and interaction style for better user experience
- **Command Structure**: Consistent `*` prefix commands across all agents
- **Integration Ready**: Designed

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
