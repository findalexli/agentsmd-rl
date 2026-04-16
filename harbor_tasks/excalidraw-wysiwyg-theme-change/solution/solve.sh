#!/bin/bash
set -e

cd /workspace/excalidraw

FILE="packages/excalidraw/wysiwyg/textWysiwyg.tsx"

# Check if already patched (idempotency check)
if grep -q "let LAST_THEME = app.state.theme" "$FILE"; then
    echo "Already patched, exiting"
    exit 0
fi

# Apply the gold patch for theme change detection in WYSIWYG editor
python3 << 'PYTHON_SCRIPT'
file_path = "packages/excalidraw/wysiwyg/textWysiwyg.tsx"

with open(file_path, 'r') as f:
    content = f.read()
    lines = content.split('\n')

new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)

    # 1. After textPropertiesUpdated function ends
    # Looking for the line with "  };" that ends the function (indented, not at column 0)
    # This comes after "    return false;" in textPropertiesUpdated
    if i > 0:
        prev_line = lines[i-1]
        # Check if this is the end of textPropertiesUpdated function
        if line == '  };' and 'return false;' in prev_line and i < len(lines) - 1:
            # Check context - look back for function signature
            context_start = max(0, i-20)
            context = '\n'.join(lines[context_start:i+1])
            if 'textPropertiesUpdated' in context and 'updatedTextElement' in context:
                # Add the LAST_THEME declaration after this
                new_lines.append('')
                new_lines.append('  let LAST_THEME = app.state.theme;')

    # 2. Inside updateWysiwygStyle at the beginning
    if line == '  const updateWysiwygStyle = () => {':
        new_lines.append('    LAST_THEME = app.state.theme;')
        new_lines.append('')

# Join and split again for the next modification
content = '\n'.join(new_lines)
lines = content.split('\n')

# 3. In cleanup function, add unsubOnChange() before unbindOnScroll()
new_lines = []
for i, line in enumerate(lines):
    # Check if next line is unbindOnScroll and current is unbindUpdate
    if i < len(lines) - 1 and 'unbindUpdate();' in line and 'unbindOnScroll();' in lines[i+1]:
        new_lines.append('    unbindUpdate();')
        new_lines.append('    unsubOnChange();')
    else:
        new_lines.append(line)

# Join and split again for the next modification
content = '\n'.join(new_lines)
lines = content.split('\n')

# 4. Add the onChangeEmitter subscription before "// handle updates of textElement properties"
new_lines = []
for i, line in enumerate(lines):
    if '// handle updates of textElement properties of editing element' in line:
        # Add the subscription block before this comment
        new_lines.append('  // FIXME after we start emitting updates from Store for appState.theme')
        new_lines.append('  const unsubOnChange = app.onChangeEmitter.on((elements) => {')
        new_lines.append('    if (app.state.theme !== LAST_THEME) {')
        new_lines.append('      updateWysiwygStyle();')
        new_lines.append('    }')
        new_lines.append('  });')
        new_lines.append('')
    new_lines.append(line)

with open(file_path, 'w') as f:
    f.write('\n'.join(new_lines))

print("Patch applied successfully")
PYTHON_SCRIPT

echo "Gold patch applied"
