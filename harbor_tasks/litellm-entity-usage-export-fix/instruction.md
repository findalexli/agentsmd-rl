# Entity Usage Export Bug

## Symptom

When exporting entity usage data for non-team entity types (tags, organizations, customers, agents, users) from the LiteLLM dashboard, the exported CSV/JSON files show incorrect values in the entity ID and entity alias columns.

The file `src/components/EntityUsageExport/utils.ts` contains a helper function `extractTeamIdFromApiKeyBreakdown` that extracts `team_id` from `api_key_breakdown` metadata. This logic is only appropriate for team exports, but it is being used for all entity types. As a result:

- A tag export with entity key `my-tag` shows a team name like `admins` in the entity ID column instead of `my-tag`
- The entity alias column similarly shows incorrect values
- For entity types with no team context, the ID falls back to `-` instead of using the entity key

## Expected Behavior

The `utils.ts` file should contain a new helper function named `resolveEntityDisplay` that determines entity ID and alias values by using the entity key directly, rather than extracting team_id from api_key_breakdown metadata.

For a **tag export** with entity key `my-tag` and no alias mapping:
- Entity ID column: must show `my-tag`
- Entity alias column: must show `my-tag`

For a **team export** with entity key `team-1` and alias map entry `"team-1": "Team One"`:
- Entity ID column: must show `team-1`
- Entity Alias column: must show `Team One`

For a **team export** with no alias map entry:
- Entity ID column: must show `team-1`
- Entity Alias column: must show `team-1`

## Implementation Requirements

1. Remove the function `extractTeamIdFromApiKeyBreakdown` from `src/components/EntityUsageExport/utils.ts`
2. Add a new function `resolveEntityDisplay` to `src/components/EntityUsageExport/utils.ts` that uses entity keys directly for ID/alias resolution
3. Update `src/components/EntityUsageExport/utils.test.ts`:
   - Replace test name `"should use dash when team id is not available"` with `"should fall back to the entity key when there is no team alias mapping"`
   - Replace test name `"should use key alias when available"` with `"should use entity key as alias when no team alias map is provided"`
   - Update mock spend data to use entity keys `"team-1"` and `"team-2"` instead of `entity1`/`entity2`

## Verification

The fix must satisfy all of the following conditions:

1. The vitest suite for EntityUsageExport (`pnpm vitest run src/components/EntityUsageExport/`) must pass with 83 tests across 6 files
2. Running vitest with the test-name pattern `should fall back to the entity key when there is no team alias mapping` must find and pass tests
3. Running vitest with the test-name pattern `should use entity key as alias when no team alias map is provided` must find and pass tests
4. The mock spend data in `utils.test.ts` uses entity keys `"team-1"` and `"team-2"` (not `entity1`/`entity2`)
5. The test named `should fall back to the entity key when there is no team alias mapping` must be present in `utils.test.ts`
6. The 63 tests in `utils.test.ts` must pass
