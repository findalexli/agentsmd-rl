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

with open('/workspace/hugo/resources/transform.go', 'r') as f:
    content = f.read()

# Old function pattern - match the exact code at base commit
old_func = """func (r *resourceAdapter) getImageOps() images.ImageResourceOps {
	img, ok := r.target.(images.ImageResourceOps)
	if !ok {
		if r.MediaType().SubType == "svg" {
			panic("this method is only available for raster images. To determine if an image is SVG, you can do {{ if eq .MediaType.SubType \\"svg\\" }}{{ end }}")
		}
		panic("this method is only available for image resources")
	}
	r.init(false, false)
	return img
}"""

new_func = """func (r *resourceAdapter) getImageOps() images.ImageResourceOps {
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
}"""

if old_func in content:
    content = content.replace(old_func, new_func)
    with open('/workspace/hugo/resources/transform.go', 'w') as f:
        f.write(content)
    print("Fix applied successfully")
else:
    # Check if already fixed
    if "resource %q of media type %q" in content:
        print("Fix already applied")
    else:
        print("Old function not found")
        exit(1)
EOF

echo "Fix complete"
