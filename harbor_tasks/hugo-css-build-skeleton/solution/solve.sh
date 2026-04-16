#!/bin/bash
set -e

cd /workspace/hugo

# Apply the gold patch from gohugoio/hugo#14631
# This patch updates the theme skeleton to use css.Build for CSS processing

# Create components directory
mkdir -p create/skeletons/theme/assets/css/components

# Create header.css
cat > create/skeletons/theme/assets/css/components/header.css << 'EOF'
header {
  border-bottom: 1px solid #222;
  margin-bottom: 1rem;
}
EOF

# Create footer.css
cat > create/skeletons/theme/assets/css/components/footer.css << 'EOF'
footer {
  border-top: 1px solid #222;
  margin-top: 1rem;
}
EOF

# Update main.css to use @import
cat > create/skeletons/theme/assets/css/main.css << 'EOF'
@import "components/header.css";
@import "components/footer.css";

body {
  color: #222;
  font-family: sans-serif;
  line-height: 1.5;
  margin: 1rem;
  max-width: 768px;
}

a {
  color: #00e;
  text-decoration: none;
}
EOF

# Update css.html to use css.Build
cat > create/skeletons/theme/layouts/_partials/head/css.html << 'EOF'
{{- with resources.Get "css/main.css" }}
  {{- $opts := dict
    "minify" (cond hugo.IsDevelopment false true)
    "sourceMap" (cond hugo.IsDevelopment "linked" "none")
  }}
  {{- with . | css.Build $opts }}
    {{- if hugo.IsDevelopment }}
      <link rel="stylesheet" href="{{ .RelPermalink }}">
    {{- else }}
      {{- with . | fingerprint }}
        <link rel="stylesheet" href="{{ .RelPermalink }}" integrity="{{ .Data.Integrity }}" crossorigin="anonymous">
      {{- end }}
    {{- end }}
  {{- end }}
{{- end }}
EOF

# Update js.html with new options
cat > create/skeletons/theme/layouts/_partials/head/js.html << 'EOF'
{{- with resources.Get "js/main.js" }}
  {{- $opts := dict
    "minify" (cond hugo.IsDevelopment false true)
    "sourceMap" (cond hugo.IsDevelopment "linked" "none")
  }}
  {{- with . | js.Build $opts }}
    {{- if hugo.IsDevelopment }}
      <script src="{{ .RelPermalink }}"></script>
    {{- else }}
      {{- with . | fingerprint }}
        <script src="{{ .RelPermalink }}" integrity="{{ .Data.Integrity }}" crossorigin="anonymous"></script>
      {{- end }}
    {{- end }}
  {{- end }}
{{- end }}
EOF

echo "Gold patch applied successfully"
