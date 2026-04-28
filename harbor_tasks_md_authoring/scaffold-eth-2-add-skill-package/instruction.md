# add skill package

Source: [scaffold-eth/scaffold-eth-2#1235](https://github.com/scaffold-eth/scaffold-eth-2/pull/1235)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/eip-5792/SKILL.md`
- `.agents/skills/erc-20/SKILL.md`
- `.agents/skills/erc-721/SKILL.md`
- `.agents/skills/ponder/SKILL.md`
- `AGENTS.md`

## What to add / change

## Context: 

So, me and @carletex have been tinkering with how to share extension skills (migrated extension to skill) with world. 

We already merge https://docs.scaffoldeth.io/SKILL.md into SE-2-docs so now you can just give agent a prompt and ask it to create a dapp for you and it will use create-eth to scaffold it. But also it will look for possible extension which could be integrated. 

The earlier plan was to share skills via a single repo like https://github.com/technophile-04/ethereum-app-skill/ so that people can install it globally on their system, and the skill can be picked by a local agent.  But then Carlos suggested it's better to keep everthing dynamic instead of people needing to clone the skills manually, for example, they just copy the prompt from the https://github.com/BuidlGuidl/SpeedRunEthereum-v2/pull/356 and agent just fetches the require skills etc. In that prompt we just suggest it to use the orchestrator which is https://docs.scaffoldeth.io/SKILL.md and other things / skills it will fetch stuff dynamcially. 

## Description: 

So after tinkering more, we kind of have a certain flow in our mind, this is kind of v0.5 / 1 of it. The flow will be: 

1. User copies the prompt from SRE build-idea or just write a promp about his dapp idea and mention https://docs.scaffoldeth.io/SKILL.md
2. It will be picked by an agent and it will scaffold a create-eth repo with base SE-2 
3. Agent will go inside current scaffolded project  and first thing it

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
