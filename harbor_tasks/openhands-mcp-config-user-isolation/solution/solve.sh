#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the gold patch for MCP config isolation
cat <<'PATCH' | git apply -
diff --git a/enterprise/migrations/versions/103_add_mcp_config_to_org_member.py b/enterprise/migrations/versions/103_add_mcp_config_to_org_member.py
new file mode 100644
index 000000000000..47f40e351ec2
--- /dev/null
+++ b/enterprise/migrations/versions/103_add_mcp_config_to_org_member.py
@@ -0,0 +1,41 @@
+"""Add mcp_config to org_member for user-specific MCP settings.
+
+Revision ID: 103
+Revises: 102
+Create Date: 2026-03-26
+
+"""
+
+from typing import Sequence, Union
+
+import sqlalchemy as sa
+from alembic import op
+
+# revision identifiers, used by Alembic.
+revision: str = '103'
+down_revision: Union[str, None] = '102'
+branch_labels: Union[str, Sequence[str], None] = None
+depends_on: Union[str, Sequence[str], None] = None
+
+
+def upgrade() -> None:
+    op.add_column('org_member', sa.Column('mcp_config', sa.JSON(), nullable=True))
+
+    # Migrate existing org-level MCP configs to all members in each org.
+    # This preserves existing configurations while transitioning to user-specific settings.
+    conn = op.get_bind()
+    orgs_with_config = conn.execute(
+        sa.text('SELECT id, mcp_config FROM org WHERE mcp_config IS NOT NULL')
+    ).fetchall()
+
+    for org_id, mcp_config in orgs_with_config:
+        conn.execute(
+            sa.text(
+                'UPDATE org_member SET mcp_config = :config WHERE org_id = :org_id'
+            ),
+            {'config': mcp_config, 'org_id': str(org_id)},
+        )
+
+
+def downgrade() -> None:
+    op.drop_column('org_member', 'mcp_config')
diff --git a/enterprise/server/routes/org_models.py b/enterprise/server/routes/org_models.py
index a3be71d856e1..257c43473afa 100644
--- a/enterprise/server/routes/org_models.py
+++ b/enterprise/server/routes/org_models.py
@@ -241,7 +241,6 @@ class OrgUpdate(BaseModel):
     enable_proactive_conversation_starters: bool | None = None
     sandbox_base_container_image: str | None = None
     sandbox_runtime_container_image: str | None = None
-    mcp_config: dict | None = None
     sandbox_api_key: str | None = None
     max_budget_per_task: float | None = Field(default=None, gt=0)
     enable_solvability_analysis: bool | None = None
diff --git a/enterprise/storage/org_member.py b/enterprise/storage/org_member.py
index 7abc5c0a38cf..3842b765205e 100644
--- a/enterprise/storage/org_member.py
+++ b/enterprise/storage/org_member.py
@@ -3,7 +3,7 @@
 """

 from pydantic import SecretStr
-from sqlalchemy import UUID, Column, ForeignKey, Integer, String
+from sqlalchemy import JSON, UUID, Column, ForeignKey, Integer, String
 from sqlalchemy.orm import relationship
 from storage.base import Base
 from storage.encrypt_utils import decrypt_value, encrypt_value
@@ -23,6 +23,7 @@ class OrgMember(Base):  # type: ignore
     _llm_api_key_for_byor = Column(String, nullable=True)
     llm_base_url = Column(String, nullable=True)
     status = Column(String, nullable=True)
+    mcp_config = Column(JSON, nullable=True)

     # Relationships
     org = relationship('Org', back_populates='org_members')
diff --git a/enterprise/storage/saas_settings_store.py b/enterprise/storage/saas_settings_store.py
index 0c0540564e12..1cdf33037964 100644
--- a/enterprise/storage/saas_settings_store.py
+++ b/enterprise/storage/saas_settings_store.py
@@ -115,6 +115,9 @@ async def load(self) -> Settings | None:
             kwargs['llm_api_key_for_byor'] = org_member.llm_api_key_for_byor
         if org_member.llm_base_url:
             kwargs['llm_base_url'] = org_member.llm_base_url
+        # MCP config is user-specific (stored on org_member, not org)
+        if org_member.mcp_config is not None:
+            kwargs['mcp_config'] = org_member.mcp_config
         if org.v1_enabled is None:
             kwargs['v1_enabled'] = True
         # Apply default if sandbox_grouping_strategy is None in the database
@@ -187,6 +190,9 @@ async def store(self, item: Settings):
             kwargs = item.model_dump(context={'expose_secrets': True})
             for model in (user, org, org_member):
                 for key, value in kwargs.items():
+                    # Skip mcp_config for org - it should only be stored on org_member (user-specific)
+                    if key == 'mcp_config' and model is org:
+                        continue
                     if hasattr(model, key):
                         setattr(model, key, value)

PATCH

echo "Gold patch applied successfully"

# Also append the new unit tests for MCP config isolation
cat <<'TESTS' >> /workspace/OpenHands/enterprise/tests/unit/test_saas_settings_store.py


@pytest.mark.asyncio
async def test_store_saves_mcp_config_to_user_org_member_only(
    session_maker, async_session_maker, mock_config, org_with_multiple_members_fixture
):
    """When user saves MCP config, it should be stored ONLY on their org_member, not propagated to others.

    This test verifies that MCP settings are user-specific:
    1. The saving user's org_member.mcp_config is set
    2. Other members' org_member.mcp_config remains unchanged (NULL)
    """
    from sqlalchemy import select
    from storage.org_member import OrgMember

    # Arrange
    fixture = org_with_multiple_members_fixture
    org_id = fixture['org_id']
    admin_user_id = str(fixture['admin_user_id'])
    member1_user_id = fixture['member1_user_id']
    member2_user_id = fixture['member2_user_id']

    store = SaasSettingsStore(admin_user_id, mock_config)

    user_mcp_config = {
        'sse_servers': [{'url': 'https://user1-mcp-server.com', 'api_key': None}],
        'stdio_servers': [],
        'shttp_servers': [],
    }

    new_settings = DataSettings(
        llm_model='test-model',
        llm_base_url='http://non-litellm-url.com',  # Non-LiteLLM URL to skip API key verification
        llm_api_key=SecretStr('test-api-key'),
        mcp_config=user_mcp_config,
    )

    # Act
    with patch('storage.saas_settings_store.a_session_maker', async_session_maker):
        await store.store(new_settings)

    # Assert
    with session_maker() as session:
        result = session.execute(select(OrgMember).where(OrgMember.org_id == org_id))
        members = {str(m.user_id): m for m in result.scalars().all()}

        # Admin's mcp_config should be set
        assert members[admin_user_id].mcp_config == user_mcp_config

        # Other members' mcp_config should remain NULL (not propagated)
        assert members[str(member1_user_id)].mcp_config is None
        assert members[str(member2_user_id)].mcp_config is None


@pytest.mark.asyncio
async def test_store_does_not_update_org_mcp_config(
    session_maker, async_session_maker, mock_config, org_with_multiple_members_fixture
):
    """When user saves MCP config, org.mcp_config should NOT be updated.

    MCP settings are user-specific and should be stored on org_member, not org.
    """
    from sqlalchemy import select
    from storage.org import Org

    # Arrange
    fixture = org_with_multiple_members_fixture
    org_id = fixture['org_id']
    admin_user_id = str(fixture['admin_user_id'])

    store = SaasSettingsStore(admin_user_id, mock_config)

    user_mcp_config = {
        'sse_servers': [{'url': 'https://private-mcp-server.com', 'api_key': None}],
        'stdio_servers': [],
        'shttp_servers': [],
    }

    new_settings = DataSettings(
        llm_model='test-model',
        llm_base_url='http://non-litellm-url.com',  # Non-LiteLLM URL to skip API key verification
        llm_api_key=SecretStr('test-api-key'),
        mcp_config=user_mcp_config,
    )

    # Act
    with patch('storage.saas_settings_store.a_session_maker', async_session_maker):
        await store.store(new_settings)

    # Assert - org.mcp_config should remain NULL
    with session_maker() as session:
        result = session.execute(select(Org).where(Org.id == org_id))
        org = result.scalars().first()

        assert org is not None
        assert org.mcp_config is None


@pytest.mark.asyncio
async def test_load_returns_user_specific_mcp_config(
    session_maker, async_session_maker, mock_config, org_with_multiple_members_fixture
):
    """When loading settings, mcp_config should come from the user's org_member, not from org or other members.

    This test verifies user isolation:
    1. User1 stores their MCP config
    2. User2 stores a different MCP config
    3. Loading as User1 returns User1's config (not User2's)
    """

    # Arrange
    fixture = org_with_multiple_members_fixture
    admin_user_id = str(fixture['admin_user_id'])
    member1_user_id = str(fixture['member1_user_id'])

    user1_mcp_config = {
        'sse_servers': [{'url': 'https://user1-private-server.com', 'api_key': None}],
        'stdio_servers': [],
        'shttp_servers': [],
    }
    user2_mcp_config = {
        'sse_servers': [{'url': 'https://user2-private-server.com', 'api_key': None}],
        'stdio_servers': [],
        'shttp_servers': [],
    }

    # Store MCP config for user1 (admin)
    store1 = SaasSettingsStore(admin_user_id, mock_config)
    settings1 = DataSettings(
        llm_model='test-model',
        llm_base_url='http://non-litellm-url.com',  # Non-LiteLLM URL to skip API key verification
        llm_api_key=SecretStr('test-api-key'),
        mcp_config=user1_mcp_config,
    )
    with patch('storage.saas_settings_store.a_session_maker', async_session_maker):
        await store1.store(settings1)

    # Store different MCP config for user2 (member1)
    store2 = SaasSettingsStore(member1_user_id, mock_config)
    settings2 = DataSettings(
        llm_model='test-model',
        llm_base_url='http://non-litellm-url.com',  # Non-LiteLLM URL to skip API key verification
        llm_api_key=SecretStr('test-api-key'),
        mcp_config=user2_mcp_config,
    )
    with patch('storage.saas_settings_store.a_session_maker', async_session_maker):
        await store2.store(settings2)

    # Act - load settings as user1
    # Need to patch all store modules since load() calls UserStore, OrgStore, etc.
    with patch(
        'storage.saas_settings_store.a_session_maker', async_session_maker
    ), patch('storage.user_store.a_session_maker', async_session_maker), patch(
        'storage.org_store.a_session_maker', async_session_maker
    ):
        loaded_settings = await store1.load()

    # Assert - user1 should see their own MCP config, not user2's
    assert loaded_settings is not None
    assert loaded_settings.mcp_config is not None
    assert (
        loaded_settings.mcp_config.sse_servers[0].url
        == 'https://user1-private-server.com'
    )
TESTS

echo "Unit tests appended successfully"
