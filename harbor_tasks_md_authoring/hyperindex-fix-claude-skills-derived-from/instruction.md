# fix: claude skills derived from confusion

Source: [enviodev/hyperindex#1023](https://github.com/enviodev/hyperindex/pull/1023)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `packages/cli/templates/static/shared/.claude/skills/indexing-handler-syntax/SKILL.md`
- `packages/cli/templates/static/shared/.claude/skills/indexing-schema/SKILL.md`
- `packages/cli/templates/static/shared/AGENTS.md`
- `packages/cli/templates/static/shared/CLAUDE.md`

## What to add / change

Noticed the skills kept converting schemas to have for example 

```graphql
type NftCollection {
  id: ID!
  contractAddress: Bytes!
  name: String!
  symbol: String!
  maxSupply: BigInt!
  currentSupply: Int!
  tokens: [Token!]! @derivedFrom(field: "collection")
}

type Token {
  id: ID!
  tokenId: BigInt!
  collection_id: NftCollection!
  owner: User!
}
```

When it should be without the `_id`

```graphql
  collection: NftCollection!
```



<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Clarified entity relationship field naming conventions in schema definitions
  * Added comprehensive mapping showing schema vs handler field correspondences
  * Expanded examples demonstrating correct entity reference patterns
  * Updated guidance on derivedFrom alignment with schema field names

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
