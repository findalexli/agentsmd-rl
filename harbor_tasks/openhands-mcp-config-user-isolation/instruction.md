# Fix MCP Settings Isolation

## Problem

MCP (Model Context Protocol) settings are currently stored at the organization level, making them visible to **all users** in the organization. This is a security/privacy issue because MCP configs may contain sensitive information like API keys or private server URLs.

## Required Changes

Make MCP settings **user-specific** instead of organization-wide:

1. **Database Migration**: Create migration #103 to add `mcp_config` column to the `org_member` table (not the `org` table)
   - The migration should also migrate existing org-level MCP configs to all members in each org
   - Include a proper `downgrade()` function

2. **OrgMember Model**: Add `mcp_config` JSON column to the SQLAlchemy `OrgMember` model in `enterprise/storage/org_member.py`

3. **SaasSettingsStore.load()**: Update to read `mcp_config` from `org_member.mcp_config` instead of `org.mcp_config`
   - Only set the config if `org_member.mcp_config is not None`

4. **SaasSettingsStore.store()**: Update to skip saving `mcp_config` to the `org` model
   - Add a condition: `if key == 'mcp_config' and model is org: continue`
   - The config should only be saved to `org_member` (which happens automatically via the existing loop)

5. **OrgUpdate Model**: Remove `mcp_config` field from `OrgUpdate` Pydantic model in `enterprise/server/routes/org_models.py`
   - This is no longer an organization-level setting

## Key Files

- `enterprise/migrations/versions/103_add_mcp_config_to_org_member.py` (create new)
- `enterprise/storage/org_member.py`
- `enterprise/storage/saas_settings_store.py`
- `enterprise/server/routes/org_models.py`

## What Success Looks Like

- User A's MCP config is stored only on their org_member record
- User B cannot see User A's MCP config
- When User A saves settings, only their org_member.mcp_config is updated
- The org.mcp_config field is never read or written by the settings store
- Existing tests pass and new tests verify user-specific isolation
