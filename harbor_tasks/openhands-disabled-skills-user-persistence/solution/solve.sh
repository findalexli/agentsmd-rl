#!/bin/bash
set -e

REPO_DIR=/workspace/OpenHands

# Idempotency check: if the fix is already applied, exit
if grep -q "disabled_skills = Column(JSON, nullable=True)" "$REPO_DIR/enterprise/storage/user.py" 2>/dev/null; then
    echo "Fix already applied, skipping."
    exit 0
fi

# Apply the patch using a heredoc
cat > /tmp/fix.patch << 'PATCH'
diff --git a/enterprise/migrations/versions/104_add_disabled_skills_to_user.py b/enterprise/migrations/versions/104_add_disabled_skills_to_user.py
new file mode 100644
index 000000000000..943870e59b7f
--- /dev/null
+++ b/enterprise/migrations/versions/104_add_disabled_skills_to_user.py
@@ -0,0 +1,29 @@
+"""Add disabled_skills column to user table.
+
+Migration 102 added disabled_skills to the legacy user_settings table,
+but the active SaaS flow (SaasSettingsStore) reads from/writes to the
+user table. This migration adds the column where it is actually needed.
+
+Revision ID: 104
+Revises: 103
+Create Date: 2026-03-31
+"""
+
+from typing import Sequence, Union
+
+import sqlalchemy as sa
+from alembic import op
+
+# revision identifiers, used by Alembic.
+revision: str = '104'
+down_revision: Union[str, None] = '103'
+branch_labels: Union[str, Sequence[str], None] = None
+depends_on: Union[str, Sequence[str], None] = None
+
+
+def upgrade() -> None:
+    op.add_column('user', sa.Column('disabled_skills', sa.JSON(), nullable=True))
+
+
+def downgrade() -> None:
+    op.drop_column('user', 'disabled_skills')
diff --git a/enterprise/storage/user.py b/enterprise/storage/user.py
index 2df86a703926..e60c3f1f6aa5 100644
--- a/enterprise/storage/user.py
+++ b/enterprise/storage/user.py
@@ -5,6 +5,7 @@
 from uuid import uuid4

 from sqlalchemy import (
+    JSON,
     UUID,
     Boolean,
     Column,
@@ -34,6 +35,7 @@ class User(Base):  # type: ignore
     git_user_name = Column(String, nullable=True)
     git_user_email = Column(String, nullable=True)
     sandbox_grouping_strategy = Column(String, nullable=True)
+    disabled_skills = Column(JSON, nullable=True)

     # Relationships
     role = relationship('Role', back_populates='users')
PATCH

cd "$REPO_DIR"
git apply /tmp/fix.patch

echo "Patch applied successfully."
