#!/bin/bash
set -e

cd /workspace/OpenHands

# Idempotency check: if the fix is already applied, skip
if grep -q "disabled_skills = Column(JSON, nullable=True)" enterprise/storage/user.py 2>/dev/null; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Create the migration file
mkdir -p enterprise/migrations/versions
cat > enterprise/migrations/versions/104_add_disabled_skills_to_user.py << 'EOF'
"""Add disabled_skills column to user table.

Migration 102 added disabled_skills to the legacy user_settings table,
but the active SaaS flow (SaasSettingsStore) reads from/writes to the
user table. This migration adds the column where it is actually needed.

Revision ID: 104
Revises: 103
Create Date: 2026-03-31
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '104'
down_revision: Union[str, None] = '103'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('disabled_skills', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('user', 'disabled_skills')
EOF

# Modify user.py to add the disabled_skills column
# First, add JSON to the imports
sed -i 's/from sqlalchemy import (/from sqlalchemy import (\n    JSON,/' enterprise/storage/user.py

# Then add the disabled_skills column after sandbox_grouping_strategy
sed -i 's/sandbox_grouping_strategy = Column(String, nullable=True)/sandbox_grouping_strategy = Column(String, nullable=True)\n    disabled_skills = Column(JSON, nullable=True)/' enterprise/storage/user.py

echo "Fix applied successfully"

# Verify the changes
if grep -q "disabled_skills = Column(JSON, nullable=True)" enterprise/storage/user.py; then
    echo "Verification: disabled_skills column added to User model"
else
    echo "ERROR: Failed to add disabled_skills column"
    exit 1
fi

if [ -f "enterprise/migrations/versions/104_add_disabled_skills_to_user.py" ]; then
    echo "Verification: Migration file created"
else
    echo "ERROR: Failed to create migration file"
    exit 1
fi
