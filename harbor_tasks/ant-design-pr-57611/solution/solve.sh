#!/bin/bash
set -e

cd /workspace/antd

# Idempotency check - skip if already applied
if grep -q "mergedMaskClosable" components/image/hooks/useMergedPreviewConfig.ts 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# ============================================
# Fix 1: components/image/hooks/useMergedPreviewConfig.ts
# ============================================

HOOK_FILE="components/image/hooks/useMergedPreviewConfig.ts"

# 1a. Update return type to include maskClosable
sed -i 's/): T & { blurClassName?: string } =>/): T \& { blurClassName?: string; maskClosable?: boolean } =>/' "$HOOK_FILE"

# 1b. Destructure mergedMaskClosable from useMergedMask
sed -i 's/const \[mergedPreviewMask, blurClassName\] = useMergedMask(/const [mergedPreviewMask, blurClassName, mergedMaskClosable] = useMergedMask(/' "$HOOK_FILE"

# 1c. Add maskClosable to the returned object (after mask: mergedPreviewMask)
sed -i 's/mask: mergedPreviewMask,$/mask: mergedPreviewMask,\n      maskClosable: mergedMaskClosable,/' "$HOOK_FILE"

# 1d. Add mergedMaskClosable to the dependency array (after mergedPreviewMask,)
# Match only the dependency array line (starts with exactly 4 spaces)
sed -i 's/^    mergedPreviewMask,$/    mergedPreviewMask,\n    mergedMaskClosable,/' "$HOOK_FILE"

# ============================================
# Fix 2: components/image/index.tsx
# ============================================

INDEX_FILE="components/image/index.tsx"

# Update OriginPreviewConfig type to use Omit
sed -i "s/type OriginPreviewConfig = NonNullable<Exclude<RcImageProps\['preview'\], boolean>>;/type OriginPreviewConfig = Omit<\n  NonNullable<Exclude<RcImageProps['preview'], boolean>>,\n  'maskClosable'\n>;/" "$INDEX_FILE"

# ============================================
# Fix 3: components/image/PreviewGroup.tsx
# ============================================

GROUP_FILE="components/image/PreviewGroup.tsx"

# Update OriginPreviewConfig type to use Omit
sed -i "s/type OriginPreviewConfig = NonNullable<Exclude<RcPreviewGroupProps\['preview'\], boolean>>;/type OriginPreviewConfig = Omit<\n  NonNullable<Exclude<RcPreviewGroupProps['preview'], boolean>>,\n  'maskClosable'\n>;/" "$GROUP_FILE"

echo "Patch applied successfully."
