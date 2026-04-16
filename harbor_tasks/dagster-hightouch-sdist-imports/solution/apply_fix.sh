#!/bin/bash
set -e

cd /workspace/dagster/python_modules/libraries/dagster-hightouch

# Fix __init__.py
cat > dagster_hightouch/__init__.py << 'EOF'
from dagster_shared.libraries import DagsterLibraryRegistry

from dagster_hightouch.component import HightouchSyncComponent
from dagster_hightouch.ops import hightouch_sync_op
from dagster_hightouch.resources import ConfigurableHightouchResource, HightouchResource
from dagster_hightouch.version import __version__ as __version__

DagsterLibraryRegistry.register("dagster-hightouch", __version__, is_dagster_package=True)

__all__ = [
    "ConfigurableHightouchResource",
    "HightouchResource",
    "HightouchSyncComponent",
    "hightouch_sync_op",
]
EOF

# Fix resources.py - change relative imports to absolute
sed -i 's/from \. import utils/from dagster_hightouch import utils/' dagster_hightouch/resources.py
sed -i 's/from \.types import HightouchOutput/from dagster_hightouch.types import HightouchOutput/' dagster_hightouch/resources.py

# Fix ops.py - change relative imports to absolute
sed -i 's/from \.resources import DEFAULT_POLL_INTERVAL, HightouchOutput/from dagster_hightouch.resources import DEFAULT_POLL_INTERVAL, HightouchOutput/' dagster_hightouch/ops.py

# Fix utils.py - change relative imports to absolute
sed -i 's/from \.types import SyncRunParsedOutput/from dagster_hightouch.types import SyncRunParsedOutput/' dagster_hightouch/utils.py

# Fix component.py - change relative imports to absolute
sed -i 's/from \.resources import ConfigurableHightouchResource/from dagster_hightouch.resources import ConfigurableHightouchResource/' dagster_hightouch/component.py

# Fix test file
sed -i 's/from typing import cast, Sequence/from typing import TYPE_CHECKING, cast/' dagster_hightouch_tests/test_component.py
sed -i 's/assets=cast(Sequence\[dg.AssetsDefinition\], list(defs.assets or \[\]))/assets=cast("Sequence[dg.AssetsDefinition]", list(defs.assets or []))/' dagster_hightouch_tests/test_component.py

# Remove pyproject.toml
rm -f pyproject.toml

echo "Fix applied successfully"
