#!/bin/bash
set -e

cd /workspace/airflow

# Idempotency check - skip if fix is already applied
if grep -q "skip_locked=True" airflow-core/src/airflow/jobs/scheduler_job_runner.py 2>/dev/null && \
   grep -q "key_share=False" airflow-core/src/airflow/jobs/scheduler_job_runner.py 2>/dev/null && \
   grep -q "deadline_query = " airflow-core/src/airflow/jobs/scheduler_job_runner.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the fix using Python for reliable text manipulation
python3 << 'PYTHON_FIX'
import re

file_path = "airflow-core/src/airflow/jobs/scheduler_job_runner.py"

with open(file_path, 'r') as f:
    content = f.read()

# Step 1: Add with_row_locks to imports if not present
# Look for existing sqlalchemy imports from airflow.utils
if "from airflow.utils.sqlalchemy import" in content:
    if "with_row_locks" not in content:
        # Add to existing import
        content = re.sub(
            r'(from airflow\.utils\.sqlalchemy import )([^)\n]+)',
            r'\1with_row_locks, \2',
            content
        )
else:
    # Add new import line after other airflow.utils imports
    content = re.sub(
        r'(from airflow\.utils\.\w+ import [^\n]+\n)',
        r'\1from airflow.utils.sqlalchemy import with_row_locks\n',
        content,
        count=1
    )

# Step 2: Replace the deadline query pattern
# The original code is:
#     for deadline in session.scalars(
#         select(Deadline)
#         .where(Deadline.deadline_time < datetime.now(timezone.utc))
#         .where(~Deadline.missed)
#         .options(selectinload(Deadline.callback), selectinload(Deadline.dagrun))
#     ):
#         deadline.handle_miss(session)

# Pattern to match the original deadline loop
old_pattern = r'''(\s+)for deadline in session\.scalars\(\s*\n\s+select\(Deadline\)\s*\n\s+\.where\(Deadline\.deadline_time < datetime\.now\(timezone\.utc\)\)\s*\n\s+\.where\(~Deadline\.missed\)\s*\n\s+\.options\(selectinload\(Deadline\.callback\), selectinload\(Deadline\.dagrun\)\)\s*\n\s+\):'''

new_code = r'''\1# Lock expired, unhandled deadlines with FOR UPDATE SKIP LOCKED so
\1# concurrent HA scheduler replicas don't both process the same row
\1# and create duplicate callbacks.
\1deadline_query = (
\1    select(Deadline)
\1    .where(Deadline.deadline_time < datetime.now(timezone.utc))
\1    .where(~Deadline.missed)
\1    .options(selectinload(Deadline.callback), selectinload(Deadline.dagrun))
\1)
\1for deadline in session.scalars(
\1    with_row_locks(
\1        deadline_query,
\1        of=Deadline,
\1        session=session,
\1        skip_locked=True,
\1        key_share=False,
\1    )
\1):'''

content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

print("Fix applied successfully")
PYTHON_FIX

echo "Gold patch applied to scheduler_job_runner.py"
