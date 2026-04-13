#!/bin/bash
set -euo pipefail

cd /workspace/react

TARGET="packages/shared/ReactPerformanceTrackProperties.js"
TESTFILE="packages/react-reconciler/src/__tests__/ReactPerformanceTrackProperties-test.js"

# Check if already applied
if grep -q "readReactElementTypeof" "$TARGET" 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

# Add the helper function after the addObjectToProperties function
sed -i '/^}$/{ N; /^}\n\nexport function addValueToProperties/s/^}/}\n\nfunction readReactElementTypeof(value: Object): mixed {\n  \/\/ Prevents dotting into $$typeof in opaque origin windows.\n  return '\''\$\$typeof'\'' in value \&\& hasOwnProperty.call(value, '\''\$\$typeof'\'' )\n    ? value.\$\$typeof\n    : undefined;\n}/; /^}$/d }' "$TARGET"

# Alternative approach: use a Python script for more reliable edits
python3 << 'PYEOF'
import re

# Read the file
with open('/workspace/react/packages/shared/ReactPerformanceTrackProperties.js', 'r') as f:
    content = f.read()

# Add the helper function after addObjectToProperties closing brace
helper_function = '''\nfunction readReactElementTypeof(value: Object): mixed {
  // Prevents dotting into $$typeof in opaque origin windows.
  return '$$typeof' in value && hasOwnProperty.call(value, '$$typeof')
    ? value.$$typeof
    : undefined;
}
'''

# Find the pattern: closing brace of addObjectToProperties followed by export function addValueToProperties
pattern = r'(\n\nexport function addValueToProperties)'
replacement = helper_function + r'\1'
content = re.sub(pattern, replacement, content)

# Replace the three $$typeof accesses
content = content.replace(
    'if (value.$$typeof === REACT_ELEMENT_TYPE) {',
    'if (readReactElementTypeof(value) === REACT_ELEMENT_TYPE) {'
)
content = content.replace(
    'prevValue.$$typeof === nextValue.$$typeof',
    'readReactElementTypeof(prevValue) ===\n            readReactElementTypeof(nextValue)'
)
content = content.replace(
    'if (nextValue.$$typeof === REACT_ELEMENT_TYPE) {',
    'if (readReactElementTypeof(nextValue) === REACT_ELEMENT_TYPE) {'
)

# Write back
with open('/workspace/react/packages/shared/ReactPerformanceTrackProperties.js', 'w') as f:
    f.write(content)

print("Source file modified successfully")
PYEOF

# Now add the test case - remove the old test if it exists and add new one
python3 << 'PYEOF'
import re

# Read the test file
with open('/workspace/react/packages/react-reconciler/src/__tests__/ReactPerformanceTrack-test.js', 'r') as f:
    content = f.read()

# Check if test already exists
if "diffs HTML-like objects" in content:
    print("Test already exists")
else:
    # Add the test before the final closing of the describe block
    new_test = '''

  // @gate __DEV__ && enableComponentPerformanceTrack
  it('diffs HTML-like objects', async () => {
    const App = function App({container}) {
      Scheduler.unstable_advanceTime(10);
      React.useEffect(() => {}, [container]);
    };

    class Window {}
    const createOpaqueOriginWindow = () => {
      return new Proxy(new Window(), {
        get(target, prop) {
          if (prop === Symbol.toStringTag) {
            return target[Symbol.toStringTag];
          }
          // Some properties are allowed if JS itself is accessign those e.g.
          // Symbol.toStringTag.
          // Just make sure React isn't accessing arbitrary properties.
          throw new Error(
            `Failed to read named property '${String(prop)}' from Window`,
          );
        },
      });
    };

    class OpaqueOriginHTMLIFrameElement {
      constructor(textContent) {
        this.textContent = textContent;
      }
      contentWindow = createOpaqueOriginWindow();
      nodeType = 1;
      [Symbol.toStringTag] = 'HTMLIFrameElement';
    }

    Scheduler.unstable_advanceTime(1);
    await act(() => {
      ReactNoop.render(
        <App
          container={new OpaqueOriginHTMLIFrameElement('foo')}
          contentWindow={createOpaqueOriginWindow()}
        />,
      );
    });

    expect(performanceMeasureCalls).toEqual([
      [
        'Mount',
        {
          detail: {
            devtools: {
              color: 'warning',
              properties: null,
              tooltipText: 'Mount',
              track: 'Components ⚛',
            },
          },
          end: 11,
          start: 1,
        },
      ],
    ]);
    performanceMeasureCalls.length = 0;

    Scheduler.unstable_advanceTime(10);

    await act(() => {
      ReactNoop.render(
        <App
          container={new OpaqueOriginHTMLIFrameElement('bar')}
          contentWindow={createOpaqueOriginWindow()}
        />,
      );
    });

    expect(performanceMeasureCalls).toEqual([
      [
        '\u200bApp',
        {
          detail: {
            devtools: {
              color: 'primary-dark',
              properties: [
                ['Changed Props', ''],
                ['-\u00a0container', 'HTMLIFrameElement'],
                ['-\u00a0\u00a0\u00a0contentWindow', 'Window'],
                ['-\u00a0\u00a0\u00a0nodeType', '1'],
                ['-\u00a0\u00a0\u00a0textContent', '"foo"'],
                ['+\u00a0container', 'HTMLIFrameElement'],
                ['+\u00a0\u00a0\u00a0contentWindow', 'Window'],
                ['+\u00a0\u00a0\u00a0nodeType', '1'],
                ['+\u00a0\u00a0\u00a0textContent', '"bar"'],
                [
                  '\u2007\u00a0contentWindow',
                  'Referentially unequal but deeply equal objects. Consider memoization.',
                ],
              ],
              tooltipText: 'App',
              track: 'Components ⚛',
            },
          },
          end: 31,
          start: 21,
        },
      ],
    ]);
  });
'''
    # Insert before the final }); that closes the describe block
    content = content.rstrip()
    if content.endswith('});'):
        content = content[:-3] + new_test + '});'

    with open('/workspace/react/packages/react-reconciler/src/__tests__/ReactPerformanceTrack-test.js', 'w') as f:
        f.write(content)
    print("Test file modified successfully")
PYEOF

echo "Patch applied successfully"
