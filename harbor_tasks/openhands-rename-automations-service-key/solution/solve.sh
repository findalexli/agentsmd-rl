#!/bin/bash
set -e

# Fix service.py
cd /workspace/openhands/enterprise/server/routes

# Fix 1: Update the module docstring (line 8)
sed -i 's/through the AUTOMATIONS_SERVICE_API_KEY environment variable/through the AUTOMATIONS_SERVICE_KEY environment variable/' service.py

# Fix 2: Update the module-level constant assignment (lines 22-23)
sed -i "s/AUTOMATIONS_SERVICE_API_KEY = os.getenv('AUTOMATIONS_SERVICE_API_KEY', '').strip()/AUTOMATIONS_SERVICE_KEY = os.getenv('AUTOMATIONS_SERVICE_KEY', '').strip()/" service.py

# Fix 3: Update the validate_service_api_key function - check condition
sed -i 's/if not AUTOMATIONS_SERVICE_API_KEY:/if not AUTOMATIONS_SERVICE_KEY:/' service.py

# Fix 4: Update the log message
sed -i "s/Service authentication not configured (AUTOMATIONS_SERVICE_API_KEY not set)/Service authentication not configured (AUTOMATIONS_SERVICE_KEY not set)/" service.py

# Fix 5: Update the key comparison
sed -i 's/if x_service_api_key != AUTOMATIONS_SERVICE_API_KEY:/if x_service_api_key != AUTOMATIONS_SERVICE_KEY:/' service.py

# Fix 6: Update the health endpoint
sed -i "s/'service_auth_configured': bool(AUTOMATIONS_SERVICE_API_KEY)/'service_auth_configured': bool(AUTOMATIONS_SERVICE_KEY)/" service.py

echo "service.py fix applied successfully"

# Fix test_service.py - update all references from AUTOMATIONS_SERVICE_API_KEY to AUTOMATIONS_SERVICE_KEY
cd /workspace/openhands/enterprise/tests/unit/routes
sed -i "s/server\.routes\.service\.AUTOMATIONS_SERVICE_API_KEY/server.routes.service.AUTOMATIONS_SERVICE_KEY/g" test_service.py

echo "test_service.py fix applied successfully"

# Verify the changes
echo "Verifying changes..."
grep -q "AUTOMATIONS_SERVICE_KEY" /workspace/openhands/enterprise/server/routes/service.py && echo "✓ service.py: New env var name found"
grep -q "AUTOMATIONS_SERVICE_API_KEY" /workspace/openhands/enterprise/server/routes/service.py && echo "✗ service.py: Old env var name still present" || echo "✓ service.py: Old env var name removed"
grep -q "AUTOMATIONS_SERVICE_KEY" /workspace/openhands/enterprise/tests/unit/routes/test_service.py && echo "✓ test_service.py: New env var name found"
grep -q "AUTOMATIONS_SERVICE_API_KEY" /workspace/openhands/enterprise/tests/unit/routes/test_service.py && echo "✗ test_service.py: Old env var name still present" || echo "✓ test_service.py: Old env var name removed"
