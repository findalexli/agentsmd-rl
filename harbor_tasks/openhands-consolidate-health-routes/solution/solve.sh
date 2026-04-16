#!/bin/bash
set -e

cd /workspace/OpenHands

# Check if already applied (idempotency)
if grep -q "openhands.app_server.status.status_router" openhands/server/app.py 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Create the new status directory structure
mkdir -p openhands/app_server/status

# Create the status_router.py with consolidated health endpoints
cat > openhands/app_server/status/status_router.py << 'ROUTER_EOF'
from fastapi import APIRouter

from openhands.app_server.status.system_stats import get_system_info

router = APIRouter(tags=['Status'])


@router.get('/alive')
async def alive():
    """Endpoint for liveness probes.

    If this responds then the server is considered alive.
    """
    return {'status': 'ok'}


@router.get('/health')
async def health() -> str:
    """Health check endpoint.

    Returns 'OK' if the service is healthy and ready to accept requests.
    This is typically used by load balancers and orchestrators (e.g., Kubernetes)
    to determine if the service should receive traffic.
    """
    return 'OK'


@router.get('/server_info')
async def get_server_info():
    """Server information endpoint.

    Returns system information including CPU count, memory usage, and
    other runtime details about the server. Useful for monitoring and
    debugging purposes.
    """
    return get_system_info()


@router.get('/ready')
async def ready() -> str:
    """Endpoint for readiness probes.

    For now this is functionally the same as the liveness probe, but should
    we need to establish further invariants in the future, having a separate
    endpoint will mean we don't need to change client code.
    """
    return 'OK'
ROUTER_EOF

# Move system_stats.py to the new location (copy from old location, it will be kept for compatibility)
cp openhands/runtime/utils/system_stats.py openhands/app_server/status/system_stats.py

# Update imports in action_execution_server.py
sed -i 's/from openhands.runtime.utils.system_stats import (/from openhands.app_server.status.system_stats import (/' openhands/runtime/action_execution_server.py

# Update imports in action_execution_client.py
sed -i 's/from openhands.runtime.utils.system_stats import update_last_execution_time/from openhands.app_server.status.system_stats import update_last_execution_time/' openhands/runtime/impl/action_execution/action_execution_client.py

# Update app.py - replace add_health_endpoints import with health_router import
# Remove old import line first
sed -i '/from openhands.server.routes.health import add_health_endpoints/d' openhands/server/app.py
# Insert new import after openhands.app_server.config line
sed -i '/from openhands.app_server.config import get_app_lifespan_service/a\from openhands.app_server.status.status_router import router as health_router' openhands/server/app.py

# Update app.py - replace add_health_endpoints(app) with app.include_router(health_router)
sed -i 's/add_health_endpoints(app)/app.include_router(health_router)/' openhands/server/app.py

# Remove the old health.py file
rm -f openhands/server/routes/health.py

echo "Patch applied successfully!"
