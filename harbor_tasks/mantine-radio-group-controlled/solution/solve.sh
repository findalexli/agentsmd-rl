#!/bin/bash
set -e

cd /workspace/mantine

# Apply the gold patch to fix the controlled/uncontrolled Radio.Group warning
cat > /tmp/radio.patch << 'ENDPATCH'
diff --git a/packages/@mantine/core/src/components/Radio/Radio.tsx b/packages/@mantine/core/src/components/Radio/Radio.tsx
index e8c36d6..a1b2c3d 100644
--- a/packages/@mantine/core/src/components/Radio/Radio.tsx
+++ b/packages/@mantine/core/src/components/Radio/Radio.tsx
@@ -174,8 +174,10 @@ export const Radio = factory<RadioFactory>((_props, ref) => {
   const { styleProps, rest } = extractStyleProps(others);
   const uuid = useId(id);

+  const contextChecked = ctx ? ctx.value === rest.value : undefined;
+
   const withContextProps = {
-    checked: ctx?.value === rest.value || checked || undefined,
+    checked: contextChecked ?? checked,
     name: ctx?.name ?? rest.name,
     onChange: (event: React.ChangeEvent<HTMLInputElement>) => {
       ctx?.onChange(event);
@@ -199,7 +201,7 @@ export const Radio = factory<RadioFactory>((_props, ref) => {
       classNames={classNames}
       styles={styles}
       unstyled={unstyled}
-      data-checked={withContextProps.checked}
+      data-checked={(contextChecked ?? checked) || undefined}
       variant={variant}
       ref={rootRef}
       mod={mod}
ENDPATCH
patch -p1 < /tmp/radio.patch

# Apply the test file changes
cat > /tmp/radio_test.patch << 'ENDPATCH'
diff --git a/packages/@mantine/core/src/components/Radio/Radio.test.tsx b/packages/@mantine/core/src/components/Radio/Radio.test.tsx
index 58f36d4..5d7a23f 100644
--- a/packages/@mantine/core/src/components/Radio/Radio.test.tsx
+++ b/packages/@mantine/core/src/components/Radio/Radio.test.tsx
@@ -1,5 +1,5 @@
-import { createRef } from 'react';
-import { render, tests } from '@mantine-tests/core';
+import { createRef, useState } from 'react';
+import { render, screen, tests, userEvent } from '@mantine-tests/core';
 import { Radio, RadioProps, RadioStylesNames } from './Radio';
 import { RadioGroup } from './RadioGroup/RadioGroup';

@@ -46,4 +46,27 @@ describe('@mantine/core/Radio', () => {
     render(<Radio {...defaultProps} rootRef={ref} />);
     expect(ref.current).toBeInstanceOf(HTMLDivElement);
   });
+
+  it('does not log controlled/uncontrolled warning inside controlled Radio.Group', async () => {
+    const errorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
+
+    try {
+      const ControlledRadioGroup = () => {
+        const [value, setValue] = useState('first');
+        return (
+          <Radio.Group value={value} onChange={setValue}>
+            <Radio value="first" label="First" />
+            <Radio value="second" label="Second" />
+          </Radio.Group>
+        );
+      };
+
+      render(<ControlledRadioGroup />);
+      await userEvent.click(screen.getByLabelText('Second'));
+
+      expect(errorSpy).not.toHaveBeenCalled();
+    } finally {
+      errorSpy.mockRestore();
+    }
+  });
 });
ENDPATCH
patch -p1 < /tmp/radio_test.patch

# Verify patches were applied (idempotency check)
grep -q "contextChecked" packages/@mantine/core/src/components/Radio/Radio.tsx
grep -q "does not log controlled/uncontrolled warning" packages/@mantine/core/src/components/Radio/Radio.test.tsx