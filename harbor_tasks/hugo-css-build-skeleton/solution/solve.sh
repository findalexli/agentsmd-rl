#!/bin/bash
set -e

cd /workspace/hugo

# Create the components directory if it doesn't exist
mkdir -p create/skeletons/theme/assets/css/components

# Create header.css component file
cat > create/skeletons/theme/assets/css/components/header.css << 'EOF'
header {
  border-bottom: 1px solid #222;
  margin-bottom: 1rem;
}
EOF

# Create footer.css component file
cat > create/skeletons/theme/assets/css/components/footer.css << 'EOF'
footer {
  border-top: 1px solid #222;
  margin-top: 1rem;
}
EOF

# Rewrite main.css to use @import instead of inline header/footer rules
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

# Rewrite css.html template to use css.Build
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

# Rewrite js.html template to use cond for options
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

# Rebuild Hugo to embed the new skeleton files
# GOTOOLCHAIN=auto will download the required Go version
echo "Rebuilding Hugo to embed new skeleton files..."
export GOTOOLCHAIN=auto
go build -o /tmp/hugo_new .

# Replace the installed Hugo with our newly built one
mv /tmp/hugo_new /go/bin/hugo

echo "Gold fix applied successfully and Hugo rebuilt"
