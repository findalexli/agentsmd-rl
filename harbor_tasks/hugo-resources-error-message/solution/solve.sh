#!/bin/bash
set -e

cd /workspace/hugo

# Read the transform.go file
FILE="resources/transform.go"

# Create the new getImageOps function content
NEW_FUNC='func (r *resourceAdapter) getImageOps() images.ImageResourceOps {
	img, ok := r.target.(images.ImageResourceOps)
	if !ok {
		instructions := "use reflect.IsImageResource, " +
			"reflect.IsImageResourceProcessable, or " +
			"reflect.IsImageResourceWithMeta to check if the resource " +
			"supports this method before calling it"
		msg := fmt.Sprintf(
			"resource %q of media type %q does not support this method: %s",
			r.Name(),
			r.MediaType(),
			instructions,
		)
		panic(msg)
	}
	r.init(false, false)

	return img
}'

# Extract the old function and replace it
# Use Python for reliable multi-line replacement
python3 << 'EOF'
import re

with open('resources/transform.go', 'r') as f:
    content = f.read()

# Pattern to match the old getImageOps function
old_pattern = r'func \(r \*resourceAdapter\) getImageOps\(\) images\.ImageResourceOps \{[^}]+if r\.MediaType\(\)\.SubType == "svg" \{[^}]+\}[^}]+panic\("this method is only available for image resources"\)[^}]+\}[^}]+r\.init\(false, false\)[^}]+return img[^}]+\}'

new_func = '''func (r *resourceAdapter) getImageOps() images.ImageResourceOps {
	img, ok := r.target.(images.ImageResourceOps)
	if !ok {
		instructions := "use reflect.IsImageResource, " +
			"reflect.IsImageResourceProcessable, or " +
			"reflect.IsImageResourceWithMeta to check if the resource " +
			"supports this method before calling it"
		msg := fmt.Sprintf(
			"resource %q of media type %q does not support this method: %s",
			r.Name(),
			r.MediaType(),
			instructions,
		)
		panic(msg)
	}
	r.init(false, false)

	return img
}'''

# Try to match and replace
if re.search(old_pattern, content, re.DOTALL):
    content = re.sub(old_pattern, new_func, content, flags=re.DOTALL)
    with open('resources/transform.go', 'w') as f:
        f.write(content)
    print("Fix applied successfully")
else:
    # Try a simpler approach - just replace the specific lines
    print("Pattern not found, trying simpler approach")
    # Check if already fixed
    if 'resource %q of media type %q' in content:
        print("Fix already applied")
    else:
        # Manual line replacement
        lines = content.split('\n')
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if 'func (r *resourceAdapter) getImageOps()' in line:
                # Found the function, now replace until we find the closing brace
                new_lines.append('func (r *resourceAdapter) getImageOps() images.ImageResourceOps {')
                i += 1
                # Skip until we find r.init
                while i < len(lines) and 'r.init(false, false)' not in lines[i]:
                    i += 1
                # Now we're at r.init, keep it and the return
                new_lines.append('\timg, ok := r.target.(images.ImageResourceOps)')
                new_lines.append('\tif !ok {')
                new_lines.append('\t\tinstructions := "use reflect.IsImageResource, " +')
                new_lines.append('\t\t\t"reflect.IsImageResourceProcessable, or " +')
                new_lines.append('\t\t\t"reflect.IsImageResourceWithMeta to check if the resource " +')
                new_lines.append('\t\t\t"supports this method before calling it"')
                new_lines.append('\t\tmsg := fmt.Sprintf(')
                new_lines.append('\t\t\t"resource %q of media type %q does not support this method: %s",')
                new_lines.append('\t\t\tr.Name(),')
                new_lines.append('\t\t\tr.MediaType(),')
                new_lines.append('\t\t\tinstructions,')
                new_lines.append('\t\t)')
                new_lines.append('\t\tpanic(msg)')
                new_lines.append('\t}')
                # Add r.init line
                new_lines.append('\t' + lines[i].strip())
                i += 1
                # Add blank line and return
                new_lines.append('')
                new_lines.append('\t' + lines[i].strip())
                i += 1
                # Add closing brace
                new_lines.append('}')
                i += 1
            else:
                new_lines.append(line)
                i += 1
        content = '\n'.join(new_lines)
        with open('resources/transform.go', 'w') as f:
            f.write(content)
        print("Fix applied via line replacement")
EOF

echo "Fix complete"
