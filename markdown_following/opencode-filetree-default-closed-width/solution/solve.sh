#!/bin/bash
# Gold patch solution for the demonstration task
# This is a minimal demonstration - creates CLAUDE.md with task guidance

set -e

cd "$REPO" 2>/dev/null || cd /workspace/matplotlib

# Create CLAUDE.md with task-specific guidance
cat > CLAUDE.md << 'EOF'
# Task-specific guidance

When working on matplotlib fixes, prefer using Agg backend for tests.
EOF

# Configure git and commit the change so judge can detect it
git config user.email "agent@example.com" || true
git config user.name "Agent" || true
git add CLAUDE.md
git commit -m "Add CLAUDE.md with task-specific guidance" || true

echo "Applied gold patch: created CLAUDE.md with task guidance"
