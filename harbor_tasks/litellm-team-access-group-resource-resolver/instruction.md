# Surface access-group inherited resources on team endpoints

You are working in the LiteLLM proxy server (a FastAPI application backed by
Prisma). Teams in LiteLLM can be associated with **access groups** — named
bundles that grant the team access to a set of models, MCP server IDs, and
agent IDs. The link between a team and its access groups is stored in the
team row's `access_group_ids` list; the actual resources are stored in the
`litellm_accessgrouptable` table, with each row exposing
`access_model_names`, `access_mcp_server_ids`, and `access_agent_ids`.

Today, the `GET /team/info` and `POST /team/list` (`list_team_v2`)
endpoints return the `access_group_ids` but **do not** tell callers what
those access groups actually grant. The dashboard UI cannot distinguish
between models a team has direct access to and models the team inherits
through an access group, so the team detail / teams-table views can't
render the two sources separately.

## What to change

Make the response objects expose the *resolved* access-group resources, in
addition to the raw `access_group_ids` that are already there.

### 1. Response model fields

On the response model used by `GET /team/info`
(`TeamInfoResponseObjectTeamTable` in `litellm/proxy/_types.py`) **and** on
the response model used by `POST /team/list`
(`TeamListItem` in `litellm/types/proxy/management_endpoints/team_endpoints.py`),
add three new optional fields, each defaulting to `None`:

- `access_group_models: Optional[List[str]] = None`
- `access_group_mcp_server_ids: Optional[List[str]] = None`
- `access_group_agent_ids: Optional[List[str]] = None`

Existing callers that don't populate them must be unaffected (these are
strictly additive, optional fields).

### 2. A batched resolver helper

Add an `async` helper function exposed at module scope of
`litellm.proxy.management_endpoints.team_endpoints` named exactly
**`_batch_resolve_access_group_resources`**. It must have this contract:

- Signature: takes a single positional argument
  `all_access_group_ids: List[str]` and returns
  `Dict[str, Dict[str, List[str]]]`.
- The returned outer dict is keyed by `access_group_id`. Each inner dict
  has exactly these three string keys: `"models"`, `"mcp_server_ids"`,
  `"agent_ids"`. The values are the resource lists pulled from the matching
  row's `access_model_names`, `access_mcp_server_ids`, and
  `access_agent_ids` columns respectively. If any of those columns is
  `None` on a row, the corresponding output list must be `[]` (empty
  list), not `None`.
- If the input list is empty **or** the global `prisma_client`
  (`litellm.proxy.proxy_server.prisma_client`) is `None`, return `{}`
  immediately without touching the DB.
- Otherwise, fetch all matching rows in a **single** Prisma `find_many`
  call against `prisma_client.db.litellm_accessgrouptable`, using a
  `where={"access_group_id": {"in": <unique ids>}}` clause. The list
  passed to `"in"` must be deduplicated — calling the helper with
  `["ag-1", "ag-1", "ag-1"]` must result in exactly one DB call whose
  `"in"` value contains a single `"ag-1"`. (No N+1 queries; no per-id
  lookups in a loop.)
- If a requested ID does not exist in the table, it is silently absent
  from the returned dict — no exception, no `None` placeholder.

### 3. Wire the helper into both endpoints

- In `team_info`, after the existing team-info response object is
  populated, if the team has any `access_group_ids`, resolve them via the
  helper and populate the three new fields on the response object. Each
  field should be the **deduplicated union** across the team's access
  groups (so if two access groups both grant `gpt-4`, the resulting
  `access_group_models` list contains it once).
- In `list_team_v2`, do the same for every `TeamListItem` in the response
  that has `access_group_ids`. Use a **single** batch resolver call across
  all teams in the page (collect every access-group ID across every team,
  call the resolver once, then distribute the results back to each team).
  Skip this work entirely when the request is for the deleted-teams view
  (`use_deleted_table=True`).

## Code Style Requirements

The repo's CI runs Ruff, Black, and MyPy via `make lint`. Python code you
add must be type-annotated (use `Optional`, `List`, `Dict` from `typing`)
and follow the existing style of `litellm/proxy/management_endpoints/team_endpoints.py`.
The repository's CLAUDE.md adds these specific rules that apply to this
change:

- **Do not write raw SQL** for proxy DB operations — use Prisma model
  methods (`find_many`, etc.) on `prisma_client.db.<model>`.
- **No N+1 queries.** Batch-fetch with `{"in": ids}` and distribute
  in-memory.

## Files to look at

- `litellm/proxy/_types.py` — `TeamInfoResponseObjectTeamTable`
- `litellm/types/proxy/management_endpoints/team_endpoints.py` — `TeamListItem`
- `litellm/proxy/management_endpoints/team_endpoints.py` — `team_info`,
  `list_team_v2`, and where the new helper lives
