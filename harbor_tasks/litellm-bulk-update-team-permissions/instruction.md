# Bulk-update team member permissions

LiteLLM's proxy server has a per-team `team_member_permissions` field
listing which key-management routes a team's members may invoke. Today
operators can only edit those permissions one team at a time. We need a
single admin endpoint that **appends** a set of permissions across many
teams in one call, without overwriting what each team already has.

## Endpoint to add

`POST /team/permissions_bulk_update`

The handler lives in
`litellm/proxy/management_endpoints/team_endpoints.py` (alongside the
existing team handlers) and the Pydantic models in
`litellm/types/proxy/management_endpoints/team_endpoints.py`. Wire it up
through the same `router`, `Depends(user_api_key_auth)`, and
`@management_endpoint_wrapper` machinery the other team endpoints use.

### Request body — `BulkUpdateTeamMemberPermissionsRequest`

| field                | type                       | required | meaning |
|----------------------|----------------------------|----------|---------|
| `permissions`        | `List[KeyManagementRoutes]`| yes      | permissions to append to the target teams (duplicates are skipped) |
| `team_ids`           | `Optional[List[str]]`      | no       | specific teams to update (default `None`) |
| `apply_to_all_teams` | `bool`                     | no, default `False` | update every team in the database |

Use the existing `KeyManagementRoutes` enum from
`litellm.proxy._types` as the element type of `permissions` so unknown
permission strings are rejected at the type layer with a Pydantic
`ValidationError`.

### Response body — `BulkUpdateTeamMemberPermissionsResponse`

| field                  | type                | meaning |
|------------------------|---------------------|---------|
| `message`              | `str`               | human-readable status |
| `teams_updated`        | `int`               | count of teams whose row was actually written |
| `permissions_appended` | `Optional[List[str]]` | echo of the permissions argument |

## Required behavior

1. **Auth**: only callers whose `user_role ==
   LitellmUserRoles.PROXY_ADMIN.value` may use the endpoint. All others
   get HTTP **403**.
2. **Empty input**: if `permissions` is empty, return immediately with
   `teams_updated == 0` and **do not** read from the database.
3. **Mode selection**:
   - if neither `team_ids` nor `apply_to_all_teams=True` is supplied,
     return HTTP **400**;
   - if both are supplied, also return HTTP **400**.
4. **Targeted mode (`team_ids`)**: fetch all requested teams in a
   single query (no per-team round trip). If any of the given ids does
   not exist, return HTTP **404**.
5. **Global mode (`apply_to_all_teams=True`)**: walk the entire teams
   table. The table can have tens of thousands of rows, so the read
   must be **paginated**. Use cursor-based pagination ordered by
   `team_id`, with a page size around 500.
6. **Merge semantics**: for each fetched team, compute the union of
   `team.team_member_permissions` and the requested permissions. If the
   team already contains every requested permission, **skip** the
   write. Otherwise persist the merged list.
7. **Writes are batched**: when there are multiple rows to update,
   issue them through a single `prisma_client.db.batch_()` transaction
   per page. Do **not** call `.update()` on the team table directly in
   a Python loop. `teams_updated` is the count of rows actually
   written (not the count of rows fetched).
8. The handler returns a dict shaped like
   `BulkUpdateTeamMemberPermissionsResponse`.

### Example

If team A has `["/key/generate"]` and team B has `["/key/delete"]`,
calling with `{"permissions": ["/team/daily/activity"], "apply_to_all_teams": true}`
yields:

- team A → `["/key/generate", "/team/daily/activity"]`
- team B → `["/key/delete", "/team/daily/activity"]`

A team already containing `/team/daily/activity` is left untouched.

## Database access conventions (project-wide)

The repo has explicit rules about proxy DB access — your implementation
must follow them:

- **Use the Prisma generated client** (`prisma_client.db.<model>` with
  `find_many`, `update`, `batch_`, etc.). Do **not** write
  `execute_raw` or `query_raw`.
- **No N+1**: when fetching multiple specific rows, use `where={"team_id": {"in": [...]}}`,
  not a per-id loop.
- **Batch writes**: when several rows of the same table are updated,
  put the calls in a `prisma_client.db.batch_()` so the round-trips
  collapse into one transaction.
- **Bound large reads**: paginate the all-teams scan with
  `take`/`cursor`/`order` so the result set never materialises in full.

## Code Style Requirements

The repo lints with `ruff` (config in `pyproject.toml` / `litellm/`).
Your patch must not increase the number of ruff errors reported on the
two files you modify; the existing two F401 unused-import warnings on
the type module's pre-existing imports may stay.
