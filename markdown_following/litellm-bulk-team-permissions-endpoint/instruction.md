# Add a bulk-update endpoint for team-member permissions

LiteLLM-proxy administrators need a way to append a set of permissions to many
teams at once — either to a specific list of teams, or across the entire
`LiteLLM_TeamTable`. There is no programmatic way to do this today (only a
single-team `update_team_member_permissions` exists), so administrators have
been editing the database by hand. Add a single new admin endpoint to
`litellm/proxy/management_endpoints/team_endpoints.py` and the matching
request/response models to
`litellm/types/proxy/management_endpoints/team_endpoints.py`.

The repo is at `/workspace/litellm`. You should not need to install anything;
the proxy environment is already set up.

## Public surface

### Route

```
POST /team/permissions_bulk_update
```

Register it on the existing `router` in the team-endpoints module. Authorize
through the existing `user_api_key_auth` dependency, decorate with the
existing `@management_endpoint_wrapper`, and use a Pydantic `response_model`.
The handler function (the one you `import` from the module) must be named
**`bulk_update_team_member_permissions`** — that exact name is part of the
public API.

### Request body — `BulkUpdateTeamMemberPermissionsRequest`

A Pydantic v2 `BaseModel` with these fields:

| field                | type                          | default | meaning                                                                 |
| -------------------- | ----------------------------- | ------- | ----------------------------------------------------------------------- |
| `permissions`        | `List[KeyManagementRoutes]`   | —       | Permissions to **append** to each target team (duplicates are skipped). |
| `team_ids`           | `Optional[List[str]]`         | `None`  | Specific team IDs to update.                                            |
| `apply_to_all_teams` | `bool`                        | `False` | If `True`, every team in the table is targeted.                         |

`KeyManagementRoutes` is an existing enum already exported from
`litellm.proxy._types` — re-use it. Typing `permissions` as
`List[KeyManagementRoutes]` is what makes Pydantic reject permission values
that are not actual proxy routes (e.g. constructing
`BulkUpdateTeamMemberPermissionsRequest(permissions=["/not/a/real/permission"])`
must raise `pydantic.ValidationError`).

### Response body — `BulkUpdateTeamMemberPermissionsResponse`

A Pydantic v2 `BaseModel` with these fields, in this order:

| field                  | type                       |
| ---------------------- | -------------------------- |
| `message`              | `str`                      |
| `teams_updated`        | `int`                      |
| `permissions_appended` | `Optional[List[str]] = None` |

The handler may return a `dict` literal with these keys (FastAPI will coerce
through `response_model`).

## Behavior

### Authorization

- Only callers whose `user_api_key_dict.user_role` equals
  `LitellmUserRoles.PROXY_ADMIN.value` may call this endpoint.
- Any other role must produce `HTTPException(status_code=403, ...)`.

### Input validation (in this order; `HTTPException` codes shown)

1. **Empty `permissions` list** — return immediately with
   `{"message": "...", "teams_updated": 0}` and **do not** touch the
   database. (No `find_many`, no `batch_()`.)
2. **Neither `team_ids` nor `apply_to_all_teams=True`** — `400`.
3. **Both `team_ids` non-empty and `apply_to_all_teams=True`** — `400`
   (mutually exclusive).

The order matters: the empty-permissions case is a no-op and short-circuits
before the mutual-exclusion checks.

### `team_ids` branch

- Fetch all named teams in **a single Prisma call** using an `IN` filter:
  `prisma_client.db.litellm_teamtable.find_many(where={"team_id": {"in": team_ids}})`.
  Do **not** issue one query per id (no N+1).
- If any requested `team_id` is not present in the result, raise
  `HTTPException(status_code=404, ...)`. The exception's `detail` must
  include the missing id(s) so a caller can read which one was wrong (e.g.
  the string representation of `detail` must contain the offending team id).

### `apply_to_all_teams` branch

The teams table can be very large (live deployments routinely have thousands
of teams), so you must **not** load it all into memory. Page through it
using Prisma cursor-based pagination:

- **Batch size: 500.** Each page calls `find_many` with `take=500` and an
  explicit `order` on `team_id`.
- After the first page, subsequent pages pass
  `cursor={"team_id": <last team_id of previous page>}` and `skip=1` to
  step past the cursor row itself.
- Stop when the page returns fewer than 500 rows (or zero rows).
- Each page is processed independently — accumulate the count of updated
  teams across pages.

### Computing each team's new permissions

For every team in a page (whether from the `team_ids` or
`apply_to_all_teams` branch):

1. Read its existing `team_member_permissions` (treat `None`/missing as
   empty).
2. If the existing set already contains every requested permission, **skip
   the team** (no DB write, do not count it in `teams_updated`).
3. Otherwise, the team's new value is the union of existing and requested
   permissions. Sort the merged list (alphabetically) before writing it,
   so the stored value is order-stable.

### Writing updates

All update writes for a given page must go through a single Prisma
`batch_()` transaction:

```
batcher = prisma_client.db.batch_()
# for each team that needs updating:
batcher.litellm_teamtable.update(
    where={"team_id": team_id},
    data={"team_member_permissions": merged_perms},
)
# ...
await batcher.commit()
```

Don't await individual `.update()` calls in a loop — that defeats the point
of batching and can deadlock under contention. (`CLAUDE.md` requires Prisma
`batch_()` for this kind of multi-row write.)

### Return value

On success, return:

```python
{
    "message": "Team permissions updated successfully",
    "teams_updated": <int>,
    "permissions_appended": data.permissions,
}
```

`teams_updated` is the **count of teams whose permissions actually changed**
— not the number of teams scanned. (Teams that already had every requested
permission are excluded.)

## Database access rules (from `CLAUDE.md`)

- Use Prisma model methods (`prisma_client.db.litellm_teamtable.find_many`,
  `.update`, `.batch_()`). **Never** use `execute_raw` / `query_raw`.
- For multi-row reads, use `{"in": [...]}` filters, not loops.
- For multi-row writes, use `batch_()` (or `update_many` where appropriate).
- For unbounded scans, paginate with `cursor` + `take` + an explicit `order`.

## Code Style Requirements

Follow the project's existing style for endpoint handlers in
`team_endpoints.py`:

- Async/await throughout.
- Type hints on all signatures (request data, helpers, return types).
- Pydantic v2 models for request/response.
- Module-level imports — keep imports at the top of the file. The only
  acceptable inline import is to break a circular import (importing
  `prisma_client` from `litellm.proxy.proxy_server` is the existing
  convention in this file and is acceptable).
- Black-format any code you add (line length 88, the project default).

## Out of scope

- You do not need to add a new permission constant to `KeyManagementRoutes`,
  modify the Prisma schema, or write CLI / SDK wrappers.
- You do not need to wire the new route into any frontend.
- You do not need to write tests; an external test suite will exercise the
  endpoint via mocked Prisma.
