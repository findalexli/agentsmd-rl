#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'POSSIBLY_MISSING_SUBMODULE' crates/ty_python_semantic/src/types/diagnostic.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch from PR #23918
git cherry-pick --no-commit a9a544c30dea4ec4ceed2f0feb0c3726b6df2b48 || \
    git checkout a9a544c30dea4ec4ceed2f0feb0c3726b6df2b48 -- \
        .github/mypy-primer-ty.toml \
        crates/ty/docs/rules.md \
        crates/ty_python_semantic/resources/mdtest/attributes.md \
        crates/ty_python_semantic/resources/mdtest/import/nonstandard_conventions.md \
        crates/ty_python_semantic/resources/mdtest/import/relative.md \
        "crates/ty_python_semantic/resources/mdtest/snapshots/attribute_assignment…_-_Attribute_assignment_-_Possibly-missing_att…_(e603e3da35f55c73).snap" \
        "crates/ty_python_semantic/resources/mdtest/snapshots/attributes.md_-_Attributes_-_Unimported_submodule…_(2b6da09ed380b2).snap" \
        crates/ty_python_semantic/resources/mdtest/type_properties/is_equivalent_to.md \
        crates/ty_python_semantic/src/types/diagnostic.rs \
        crates/ty_python_semantic/src/types/infer/builder.rs \
        crates/ty_server/tests/e2e/snapshots/e2e__code_actions__code_action_possible_missing_submodule_attribute.snap \
        ty.schema.json

echo "Patch applied successfully."
