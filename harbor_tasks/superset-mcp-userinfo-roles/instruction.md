# Fix UserInfo role serialization in MCP service

The Superset MCP (Model Context Protocol) service exposes Charts, Dashboards, and Datasets through tools like `list_charts`, `get_dashboard_info`, etc. Each response embeds an `owners` list of `UserInfo` objects, defined in `superset/mcp_service/system/schemas.py`. The relevant field is:

```python
roles: List[str] = Field(
    default_factory=list,
    description=(
        "Role names assigned to the user (e.g., Admin, Alpha, Gamma, Viewer). "
        "Use this to determine what actions the user can perform."
    ),
)
```

When any of these MCP tools is invoked against a real Superset instance whose objects have owners, serialization fails with a Pydantic validation error similar to:

```
1 validation error for UserInfo
roles.0
  Input should be a valid string [type=string_type, input_value=Admin, input_type=Role]
```

## Why it fails

The owners returned from SQLAlchemy are user ORM objects whose `.roles` attribute is a list of `Role` ORM instances (each instance has a `.name` string attribute), not a list of strings. The chart, dashboard, and dataset serializers feed the raw user object straight into `UserInfo` (e.g., via `UserInfo.model_validate(owner, from_attributes=True)`), so Pydantic sees `Role` objects where it expects strings.

## Required behavior after the fix

For every call site that builds a `UserInfo` from a user-like ORM object — that is, the owner-serialization paths inside the chart, dashboard, and dataset response builders — the resulting `UserInfo.roles` must be a `list[str]` of role names extracted from each role object's `.name` attribute. Concretely:

1. Given a user whose `roles` is `[Role("Admin"), Role("Alpha")]` (where `Role` is any object with a `.name` string attribute), the produced `UserInfo.roles` must equal `["Admin", "Alpha"]`. Every element must be a `str`, never a `Role`-typed object.
2. Order must match the input order.
3. The other `UserInfo` fields (`id`, `username`, `first_name`, `last_name`, `email`, `active`) must continue to be populated as before.
4. The fix applies in **all three** owner-serialization sites: the Chart response builder (`superset/mcp_service/chart/schemas.py`), the Dashboard response builder (`superset/mcp_service/dashboard/schemas.py`), and the Dataset response builder (`superset/mcp_service/dataset/schemas.py`).

## Required edge-case handling

The serialization must not raise on any of the following:

- Owner has no `roles` attribute at all → `UserInfo.roles == []`.
- Owner has `roles = None` → `UserInfo.roles == []`.
- Owner has `roles` set to a non-iterable scalar (e.g., a stray int) → `UserInfo.roles == []`.

Pydantic alone will reject `roles=None` against a `List[str]` field, so the fix must guard against these cases before validation.

## Out of scope

You do not need to add new tools, change the `UserInfo` schema's field set, or alter the chart/dashboard/dataset response shapes beyond what is required to make role serialization correct.

## Code Style Requirements

This codebase enforces several agent-instruction rules from `AGENTS.md` and `superset/mcp_service/CLAUDE.md`. The most relevant ones for this task:

- Modern Python 3.10+ type-hint syntax in any new code: prefer `T | None` over `Optional[T]`. Do not import `Optional`, `List`, or `Dict` from `typing` in new helper code — use the built-in `list[...]`, `dict[...]`, etc. (Existing imports of `List`/`Dict` in already-modified files do not need to be removed.)
- Every Python file in `superset/mcp_service/` must carry the standard Apache Software Foundation license header at the top. If you create any new `.py` file, include the header verbatim. Never remove an existing header during an edit.
- Type hints on new functions/parameters/returns are required.
- Avoid time-specific words like "now", "currently", "today" in code comments — they go stale.

## Where the agent-config rules live

- `AGENTS.md` (repo root): general Python/TS conventions, license-header expectations.
- `superset/mcp_service/CLAUDE.md`: MCP-specific conventions, including the strict license-header requirement and the Python 3.10+ type-hint style guide.
